import os
import sys
import pandas as pd
from main import get_brands_totals, scrap_single_brand
import boto3
from utils.mail import send_email
from utils.salesdeep.brands import BRAND_NAMES
import json
import dotenv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from utils.storage.s3 import get_number_of_files, upload_file

dotenv.load_dotenv()

aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

def scrape_brand_safe(brand, dt, number_of_brands):
    """Wrapper function to catch exceptions for ThreadPoolExecutor"""
    try:
        return scrap_single_brand(brand, dt, number_of_brands)
    except Exception as e:
        error_message = f"Error scraping brand {brand}: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        # Log the error to a file for later inspection
        with open(f"error_{brand}_{dt}.log", "w") as f:
            f.write(error_message)
        # You could also upload error logs to S3
        upload_file(f"error_{brand}_{dt}.log", f"{dt}/error_{brand}.log")
        # Re-raise if you want the ThreadPoolExecutor to know about it
        raise

def distribute_scraping(brands):
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    selected_brands = []
    BRAND_NAMES_LOWER = [brand.lower() for brand in BRAND_NAMES]
    # brands = list(filter(lambda brand: brand.get("label").lower() in BRAND_NAMES_LOWER, brands))
    for brand in brands:
        brand_name = brand["label"]
        if brand_name.lower() in BRAND_NAMES_LOWER:
            selected_brands.append(brand)
    print(f"Scraping {len(selected_brands)} brands")

    results = []
    exceptions = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks and get futures
        futures = {
            executor.submit(scrape_brand_safe, brand, dt, len(selected_brands)): brand
            for brand in selected_brands
        }

        # Process futures as they complete
        for future in as_completed(futures):
            brand = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Successfully processed brand: {brand.get('label')}")
            except Exception as exc:
                exceptions.append((brand.get('label'), exc))
                print(f"Brand {brand.get('label')} generated an exception: {exc}")

    if exceptions:
        print(f"There were {len(exceptions)} errors during scraping:")

        # You could also send an email about the errors
        error_email_body = f"""
<h2>WARNING: Errors occurred during SalesDeep scraping</h2>

<p>The following brands had errors:</p>
<ul>
{"".join([f"<li>{brand}: {str(exc)}</li>" for brand, exc in exceptions])}
</ul>

<p>Check the logs for more details.</p>
"""
        send_email(error_email_body, subject="SalesDeep Scraping Errors")

    # Only proceed if we have some successful results
    if results:
        number_of_files_in_s3 = get_number_of_files(dt)
        print("Number of files in S3", number_of_files_in_s3, "of", dt)

        # Only create the complete file if all brands were successful
        successfully_scraped_brands = [brand for brand in BRAND_NAMES if brand not in [b for b, _ in exceptions]]
        print("successfully_scraped_brands", successfully_scraped_brands)
        if successfully_scraped_brands:
            try:
                # Create a local directory for the files if it doesn't exist
                os.makedirs(dt, exist_ok=True)

                # Get list of all Excel files in S3 bucket for this datetime folder
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_REGION', 'us-east-2')
                )

                # List objects in the bucket with the given prefix
                bucket_name = 'salesdeep-scrapped-data'
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=f"{dt}/"
                )

                excel_files = []

                # Download each Excel file (except any existing complete.xlsx)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        if obj['Key'].endswith('.xlsx') and not obj['Key'].endswith('complete.xlsx'):
                            file_key = obj['Key']
                            local_file_path = file_key  # Use S3 key as local path

                            # Create local directories if they don't exist
                            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                            # Download the file from S3
                            print(f"Downloading {file_key} to {local_file_path}")
                            s3_client.download_file(bucket_name, file_key, local_file_path)

                            excel_files.append(local_file_path)

                # Merge all downloaded Excel files
                complete_filename = f"{dt}/complete.xlsx"
                if excel_files:
                    print(f"Merging {len(excel_files)} Excel files: {excel_files}")
                    dfs = [pd.read_excel(file) for file in excel_files]
                    complete_df = pd.concat(dfs, ignore_index=True)

                    print(f"Creating complete file with {len(complete_df)} rows")
                    complete_df.to_excel(complete_filename, index=False)
                    upload_file(complete_filename, f"{dt}/complete.xlsx")

                    file_links = []
                    for file_path in excel_files:
                        brand_name = os.path.basename(file_path).replace('.xlsx', '')
                        file_links.append(f"<a href='https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{dt}/{brand_name}.xlsx'>{brand_name}</a><br>")

                    email_body = f"""
<h2>SalesDeep Products scraping completed</h2>

<p>Download links for successful brands:</p>
{"".join(file_links)}

<p>Complete File:</p>
<a href='https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{dt}/complete.xlsx'>Download</a>
"""
                    if exceptions:
                        email_body += f"""
<p>Note: The following brands failed: {', '.join([b for b, _ in exceptions])}</p>
"""
                    send_email(email_body)
                else:
                    print("No Excel files found to merge.")
                    error_email_body = "No Excel files found to merge for creating complete file."
                    send_email(error_email_body, subject="SalesDeep Complete File Creation Warning")
            except Exception as e:
                print(f"Error creating complete file: {str(e)}")
                traceback.print_exc()
                # Send email about this error too
                error_email_body = f"Error creating complete file: {str(e)}"
                send_email(error_email_body, subject="SalesDeep Complete File Creation Error")
    else:
        print("No brands were successfully scraped.")
        send_email("All brand scraping failed. Check the logs for details.", subject="SalesDeep Scraping Failed")

    return {
        'statusCode': 200,
        'body': f'Scraping completed. Successful: {len(results)}, Failed: {len(exceptions)}'
    }

if __name__ == "__main__":
    brands = get_brands_totals()
    distribute_scraping(brands)

print(__name__)
