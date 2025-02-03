from utils.salesdeep.login import login_and_extract_data
from utils.salesdeep.products import get_brand_products, get_product_details
from utils.salesdeep.brands import BRAND_IDS
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import concurrent.futures
from utils.mail import send_email
from utils.storage.s3 import upload_file
from utils.storage.rds import store_products
import dotenv
import os

dotenv.load_dotenv()

start_time = datetime.now()
print("Script started at:", start_time)

# login_details = login_and_extract_data()
login_details = [{'user_uid': '1737368395896625168', 'nickname': 'Dzevad', 'user_mail': '6lRMv7eVFRKjsB3olCz75FqFVAr2ibSHKcAK4IdI3jI=', 'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIiLCJhdWQiOiIiLCJpYXQiOjE3Mzg1Nzk4NDEsIm5iZiI6MTczODU3OTk0MSwiZXhwIjoxNzM5MTg0NjQxLCJpZCI6IjE3MzczNjgzOTU4OTY2MjUxNjgiLCJhbm9ueW1vdXMiOiJubyIsInVzZXJfdHlwZSI6IjAiLCJ1c2VyX2lkIjoiMTczNzM1NTQ2NzczNjA3OTE4MSIsImNvbXBhbnlfaWQiOiIxNzM3MzY4MjExMTAwMDAxOTA2In0.nonQlDpK59VgLhByqfh79K3KrGcP7xmruk5OR5Zwol4', 'expires_in': 604800, 'user_type': 0, 'isSuperAdmin': 1, 'company_id': '1737368211100001906', 'company_name': None, 'user_group_id': '1737368211110005774', 'UserGroupName': '超级管理员', 'country_name': 'Unknown nationality', 'department_name': ''}]

if not login_details:
    print("Login failed")
    exit()

def process_brand(brand):
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

all_brands_products = []
datetime_folder = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
os.makedirs(datetime_folder, exist_ok=True)
file_links = []

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_brand, brand) for brand in BRAND_IDS.items()]
    for future in concurrent.futures.as_completed(futures):
        brand_name, brand_products = future.result()
        all_brands_products.extend(brand_products)
        brand_filename = f"{datetime_folder}/{brand_name}.xlsx"
        pd.DataFrame(brand_products).to_excel(brand_filename, index=False)
        upload_file(brand_filename, f"{datetime_folder}/{brand_name}.xlsx")
        file_links.append(f"https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/{brand_name}.xlsx")

complete_filename = f"{datetime_folder}/complete.xlsx"
pd.DataFrame(all_brands_products).to_excel(complete_filename, index=False)
upload_file(complete_filename, f"{datetime_folder}/complete.xlsx")
file_links.insert(0, f"https://salesdeep-scrapped-data.s3.us-east-2.amazonaws.com/{datetime_folder}/complete.xlsx")

email_body = "SalesDeep Products have been scrapped:\n\n"
email_body += "\n".join(file_links)

send_email(email_body)

end_time = datetime.now()
print("Script ended at:", end_time)
print("Total execution time:", end_time - start_time)
