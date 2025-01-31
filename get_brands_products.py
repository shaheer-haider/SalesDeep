import os
import csv
import json
import requests

from login import login_and_extract_data
from get_brands import get_brands

# API URLs
LIST_BRAND_PRODUCTS_URL = "https://sg-leixiao.salesdeep.com/api/discover/listCategorySalesPrice"
PRODUCT_DETAIL_URL = "https://sg-leixiao.salesdeep.com/api/discover/skuDetail"

#From Brands.csv get category_id
def get_brands_ids(file_path):
    category_ids = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            category_ids.append(row["id"])  # Category ID brand file se
    return category_ids 


# Fetch brand products
def get_brand_products(brand_id=9508, page_no=1, page_size=100):
    payload = {"category_id": brand_id, "pageNo": page_no, "pageSize": page_size, }
    response = requests.post(LIST_BRAND_PRODUCTS_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("Status") == 0:
            return data  # Returning product list
    return []


# Main function
def main():

    # Login and get auth_data:
    auth_data = login_and_extract_data()

    # Get Brands Data:
    brands_data = get_brands(auth_data)

    for brand in brands_data:
        print(brand)
        catagory_id = brand.get('id')

        # Get Brand product data:
        brand_products_data = get_brand_products(catagory_id, 1, 100)
        if brand_products_data is not []:
            print("This is brand_products_data: ", brand_products_data)
        # total= brand_products_data['data'].get("total")
        # per_page= brand_products_data['data'].get("per_page")
        # current_page= brand_products_data['data'].get("current_page")
        # last_page= brand_products_data['data'].get("last_page")
        # print("Total: ", total, " pages:", last_page)


        # for page_no in range(1, last_page+1):
        #     brand_products_data = get_brand_products(catagory_id, page_no, per_page)
        #     print("This is brand_products_data: ", brand_products_data)
        #     break
    

    # Get Brands IDs:
    base_dir = "./DATA/"
    brands_ids = get_brands_ids(os.path.join(base_dir+'brands.csv'))
    print(len(brands_ids))

    brands_products = get_brand_products()
    print(brands_products)

if __name__ == "__main__":
    main()
