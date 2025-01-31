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

    for brands in brands_data:
        catagory_id = brands.get('id')

        # Get Brand product data:
        brand_products_data = get_brand_products(catagory_id, 1, 100)
        total= brand_products_data['data'].get("total")
        per_page= brand_products_data['data'].get("per_page")
        current_page= brand_products_data['data'].get("current_page")
        last_page= brand_products_data['data'].get("last_page")

        for page_no in range(1, last_page+1):
            brand_products_data = get_brand_products(catagory_id, page_no, per_page)
            for products_data in brand_products_data:
                
                product_id = bramds_product_data"product_id": "1727243580357663321",
                "sku": "1727243580357663322",
                "spec_name": "",
                "condition": 1,
                "image": "https:\/\/crmfiles-1306719578.cos.ap-guangzhou.myqcloud.com\/product\/638603264482198413?imageMogr2\/format\/jpg",
                "brand_id": 4,
                "size": "55cm,40cm,20cm",
                "brand_name": "ALLEN-BRADLEY",
                "model": "2090-CFBM7DD-CEAF90",
                "product_name": "2090-CFBM7DD-CEAF90",
                "stock_qty": 0,
                "is_favorite": 0,
                "condition_name": "New Sealed Under Guarantee",
                "qty": 1,
                "leading": "In Stock",
                "origin_price": 0,
                "price": "976.69",
                "unit_price": "976.69",
                "unit_origin": 0,
                "currency": "USD",
                "rid": "1731161464100000409",
                "symbol": "$"

    

    # Get Brands IDs:
    base_dir = "./DATA/"
    brands_ids = get_brands_ids(os.path.join(base_dir+'brands.csv'))
    print(len(brands_ids))

    brands_products = get_brand_products()
    print(brands_products)

if __name__ == "__main__":
    main()
