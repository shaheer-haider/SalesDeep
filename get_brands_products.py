import os
import csv
import json
import requests

from get_users import login_and_extract_data
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
def get_brand_products(auth_data, brand_id, page_no=1, page_size=100): 
    token = auth_data[0].get("token")
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
    }
    url = "https://sg-leixiao.salesdeep.com/api/discover/listCategorySalesPrice"
    payload = {"category_id": brand_id, "pageNo": page_no, "pageSize": page_size}
    
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    return []

# Fetch products details:
def get_product_details(auth_data, sku): 
    token = auth_data[0].get("token")
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
    }
    url = "https://sg-leixiao.salesdeep.com/api/discover/skuDetail"
    payload = {'sku': sku, 'customer_info_id': "", 'currency': ""}
    
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    return []



# Main function
def main():

    # Login and get auth_data:
    auth_data = login_and_extract_data()

    # Get Brands Data:
    brands_data = get_brands(auth_data)

    for brand in brands_data:
        # print(brand)
        catagory_id = brand.get('id')

        # call brand products API function:
        brand_products_data = get_brand_products(auth_data=auth_data, brand_id=catagory_id)
        if brand_products_data:
            last_page = brand_products_data.get('data', {}).get('last_page', None)
            
            for page_no in range(1, int(last_page)+1):
                brand_products_data = get_brand_products(auth_data=auth_data, brand_id=catagory_id, page_no=page_no)
                if brand_products_data:
                    brand_products = brand_products_data.get('data', {}).get('data', None)
                    
                    for brand_product in brand_products:
                        sku = brand_product.get('sku')

                        # call product details API function
                        product_details = get_product_details(auth_data=auth_data, sku=sku)
                        product_details = product_details.get('data', {})
                        
                        product_id = product_details.get('product_id')
                        product_name = product_details.get('product_name')
                        model = product_details.get('model')
                        brand_name = product_details.get('brand_name')
                        type = product_details.get('category_txt', '-')
                        length = f"{product_details.get('length', '-')}{product_details.get('length_unit')}"
                        width = f"{product_details.get('width', '-')}{product_details.get('width_unit')}"
                        height = f"{product_details.get('height', '-')}{product_details.get('height_unit')}"
                        size = f"{length},{width},{height}"
                        weight = f"{product_details.get('weight')}{product_details.get('weight_unit')}"
                        Leading = product_details.get('leadings', [])[0].get('leading', "-")
                        condition = product_details.get("spec", {}).get("condition_name", "-")
                        imgs = product_details.get('imgs')
                        image_url = product_details.get("image")

                        # Extract pricing
                        prices = product_details.get("leadings", [])[0].get("priceList", [])
                        price_texts = []
                        for price in prices:
                            price_texts.append(f"${price['unit_price']} {price['qty_txt2']}")
                        price_str = " ".join(price_texts)
                        
                        # Extract description
                        descriptions = product_details.get("descriptions", [])
                        description_name = "-"
                        description_content = "-"
                        for desc in descriptions:
                            if desc["language_name"].lower() == "english":
                                description_name = desc["name"] if desc["name"] else model
                                description_content = desc["description"]
                                break

                        
                        product_info = {
                            'product_id': product_id, 
                            'product_name': product_name, 
                            'model': model, 
                            'brand_name': brand_name, 
                            'type': type, 
                            'length': length, 
                            'width': width, 
                            'height': height, 
                            'size': size, 
                            'weight': weight, 
                            'Leading': Leading, 
                            'condition': condition, 
                            'imgs': imgs, 
                            'image_url': image_url, 
                            'price_str': price_str, 
                            'description_name': description_name, 
                            'description_content': description_content 

                        }
                        print(product_info)

                        break
                    break
                break
            break
        break


if __name__ == "__main__":
    main()
