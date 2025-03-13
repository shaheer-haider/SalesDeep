from itertools import chain
from utils.salesdeep.api_client import ApiClient
from utils.salesdeep.login import login_and_extract_data
from utils.salesdeep.products import get_brand_products, get_product_details
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.storage.s3 import upload_file
import os
import time

login_details = None

def process_brand(brand, total_products):
    token = login_details[0]['token']
    page = 1
    page_size = 1000
    brand_name, brand_id = brand["label"], brand["id"]
    brand_products = []
    print(f"Scraping {total_products} products of {brand_name} with ID {brand_id}...")
    while True:
        products = get_brand_products(token, brand_id, page, page_size)
        brand_products.extend(products["data"]["data"])
        page += 1
        if page * page_size > total_products:
            break

    brand_details = []
    for product_from_list in brand_products:
        if not product_from_list["sku"]:
            continue

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                product_details = get_product_details(token, product_from_list["sku"])
                if not product_details.get("data"):
                    print(f"No data for SKU {product['sku']}, retrying...")
                    time.sleep(5)
                    retry_count += 1
                    continue

                if not product_details["data"]["product_name"]:
                    break

                product = product_details["data"]
                description_html = product["descriptions"][0]["description"] if len(product["descriptions"]) > 0 else ""
                brand_details.append({
                    "product_id": product_from_list["product_id"],
                    "sku": product_from_list["sku"],
                    "name": product_from_list["product_name"],
                    "model": product_from_list["model"],
                    "brand": product_from_list["brand_name"],
                    "price": product_from_list["unit_price"],
                    "currency": product_from_list["currency"],
                    "type": product["category_txt"],
                    "weight": f'{product["weight"]} {product["weight_unit"]}',
                    "leading": product["leadings"][0]["leading"] if len(product["leadings"]) > 0 else None,
                    "image": product["image"],
                    "description": BeautifulSoup(description_html, "html.parser").get_text(),
                    "description_html": description_html,
                })
                break
            except Exception as e:
                print(f"Error processing SKU {product['sku']}: {str(e)}")
                if retry_count < max_retries - 1:
                    print(f"Retrying in 5 seconds... (Attempt {retry_count + 1}/{max_retries})")
                    time.sleep(5)
                    retry_count += 1
                else:
                    print(f"Skipping SKU {product['sku']} after {max_retries} failed attempts")
                    break

        print(f"Processed SKU {product_from_list['sku']}...")

    return brand_name, brand_details

def scrap_single_brand(brand, datetime_folder, number_of_brands):
    brand_name, total = brand["label"], brand["all_sku_num"]
    start_time = datetime.now()
    print(f"Started scraping {brand_name} at:", start_time)

    os.makedirs(datetime_folder, exist_ok=True)
    brand_name, brand_products = process_brand(brand, total)

    brand_filename = f"{datetime_folder}/{brand_name}.xlsx"
    pd.DataFrame(brand_products).to_excel(brand_filename, index=False)
    upload_file(brand_filename, f"{datetime_folder}/{brand_name}.xlsx")

    end_time = datetime.now()
    print(f"Finished scraping {brand_name} at:", end_time)
    print("Total execution time:", end_time - start_time)


    # file_link = f"https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/{brand_name}.xlsx"

    # email_body = f"SalesDeep Products for {brand_name} have been scrapped:\n\n{file_link}"
    # send_email(email_body)

    return {
        'statusCode': 200,
        'body': f'Successfully scraped {brand_name}'
    }

def get_brands_totals():
    global login_details
    if not login_details:
        login_details = login_and_extract_data()
        if not login_details:
            raise Exception("Login failed")

    # Fetch products details:
    token = login_details[0]['token']
    client = ApiClient(token)
    data = client.post("discover/brands", {'type': "brand"})
    if data["Message"] != 'success':
        raise Exception("Failed to fetch brands")
    brands = list(chain.from_iterable(x["children"] for x in data["data"]["data"]))
    return brands

