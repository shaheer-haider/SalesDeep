from utils.salesdeep.login import login_and_extract_data
from utils.salesdeep.products import get_brand_products, get_product_details
from utils.salesdeep.brands import BRAND_IDS
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import concurrent.futures
from utils.mail import send_email
from utils.storage.s3 import upload_file, get_number_of_files
from utils.storage.rds import store_products
import os
from utils.salesdeep.brands import BRAND_IDS

def process_brand(brand, login_details):
    token = login_details[0]['token']
    page = 1
    page_size = 1000
    total = None
    brand_name = brand[0]
    brand_id = brand[1]
    brand_products = []
    while True:
        products = get_brand_products(token, brand_id, page, page_size)
        if not total:
            total = products["data"]["total"]
        brand_products.extend(products["data"]["data"])
        page += 1
        if page * page_size > total:
            break

    brand_details = []
    for product in brand_products:
        if not product["sku"]:
            continue
        product_details = get_product_details(token, product["sku"])
        if not product_details["data"]["product_name"]:
            continue

        product = product_details["data"]
        description_html = product["descriptions"][0]["description"] if len(product["descriptions"]) > 0 else ""

        brand_details.append({
            "product_id": product["product_id"],
            "sku": product["spec"]["sku"],
            "name": product["product_name"],
            "model": product["model"],
            "brand": product["brand_name"],
            "type": product["category_txt"],
            "price": product["leadings"][0]["price"] if len(product["leadings"]) > 0 else None,
            "currency": product["leadings"][0]["currency"] if len(product["leadings"]) > 0 else None,
            "weight": f'{product["weight"]} {product["weight_unit"]}',
            "length": f'{product["length"]} {product["length_unit"]}',
            "width": f'{product["width"]} {product["width_unit"]}',
            "height": f'{product["height"]} {product["height_unit"]}',
            "diameter": f'{product["diameter"]} {product["diameter_unit"]}',
            "leading": product["leadings"][0]["leading"] if len(product["leadings"]) > 0 else None,
            "image": product["image"],
            "description_html": description_html,
            "description": BeautifulSoup(description_html, "html.parser").get_text(),
        })
    return brand_name, brand_details

def scrap_single_brand(brand_name, brand_id, datetime_folder, number_of_brands):
    start_time = datetime.now()
    print(f"Started scraping {brand_name} at:", start_time)

    login_details = login_and_extract_data()
    if not login_details:
        raise Exception("Login failed")

    os.makedirs(datetime_folder, exist_ok=True)

    brand_name, brand_products = process_brand((brand_name, brand_id), login_details)

    brand_filename = f"{datetime_folder}/{brand_name}.xlsx"
    pd.DataFrame(brand_products).to_excel(brand_filename, index=False)
    upload_file(brand_filename, f"{datetime_folder}/{brand_name}.xlsx")


    # check if number_of_brands is same as number of files in s3 buckets's folder
    number_of_files = get_number_of_files(datetime_folder)
    if number_of_files == number_of_brands:
        # download all files and merge them
        complete_filename = f"{datetime_folder}/complete.xlsx"
        complete_df = pd.concat([pd.read_excel(f"https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/{brand}.xlsx") for brand in BRAND_IDS.keys()])
        complete_df.to_excel(complete_filename, index=False)
        upload_file(complete_filename, f"{datetime_folder}/complete.xlsx")
        email_body = f"""
<h2>SalesDeep Products for all brands have been scrapped</h2>

<p>Download links:</p>
{"".join([f"<a href='https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/{brand}.xlsx'>{brand}</a><br>" for brand in BRAND_IDS.keys()])}

<p>Complete File:</p>
<a href='https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/complete.xlsx'>Download</a>
"""
        send_email(email_body)

    # file_link = f"https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/{brand_name}.xlsx"

    # email_body = f"SalesDeep Products for {brand_name} have been scrapped:\n\n{file_link}"
    # send_email(email_body)

    end_time = datetime.now()
    print(f"Finished scraping {brand_name} at:", end_time)
    print("Total execution time:", end_time - start_time)

    return {
        'statusCode': 200,
        'body': f'Successfully scraped {brand_name}'
    }
