import os
import csv
import json
import requests
import rds
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def login_and_extract_data():
    """
    Logs in to the API, extracts relevant user data, saves it as a CSV, and returns the data as a dictionary.
    
    Returns:
        dict: Extracted user information.
    """
    # Fetch credentials from environment variables
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    # API endpoint
    url = 'https://sg-d.salesdeep.com/v2/login/login'

    # Headers for the request
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://login.salesdeep.com',
        'referer': 'https://login.salesdeep.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
    }

    # Payload (login credentials)
    payload = {'username': username, 'pwd': password}

    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP failures (4xx, 5xx)

        # Parse JSON response
        response_json = response.json()

        # Extract relevant data
        if response_json.get("Status") == 0:  # Check if login was successful
            user_data = response_json.get("data", {})
            extracted_info = [{
                "user_uid": user_data.get("user_uid"),
                "nickname": user_data.get("nickname"),
                "user_mail": user_data.get("user_mail"),
                "token": user_data.get("token"),
                "expires_in": user_data.get("expires_in"),
                "user_type": user_data.get("user_type"),
                "isSuperAdmin": user_data.get("isSuperAdmin"),
                "company_id": user_data.get("company_info", {}).get("company_id"),
                "company_name": user_data.get("company_info", {}).get("company_name"),
                "user_group_id": user_data.get("user_group", {}).get("user_group_id"),
                "UserGroupName": user_data.get("user_group", {}).get("UserGroupName"),
                "country_name": user_data.get("countryInfo", {}).get("name"),
                "department_name": user_data.get("department_info", {}).get("department_name"),
            }]
            return extracted_info
        else:
            print("Error: Login failed or no data extracted.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_brands(auth_data):
    token = auth_data[0].get("token")
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": token,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
    }
    url = "https://sg-leixiao.salesdeep.com/api/discover/brands"
    payload = {"type": "brand"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        brand_data = response.json().get("data", {}).get("data", [])
        
        # Process data for CSV
        data = []
        for category in brand_data:
            for brand in category.get("children", []):
                data.append({
                    "id": brand.get("id"),
                    "parent_id": brand.get("parent_id"),
                    "label": brand.get("label"),
                    "stage": brand.get("stage"),
                    "sku_num": brand.get("sku_num"),
                    "image": brand.get("image"),
                    "all_sku_num": brand.get("all_sku_num")
                })        
        return data
    else:
        print("Failed to fetch brands:", response.text)
        return None


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

    # Database connection:
    db_connection = rds.get_db_connection()

    # Login and get auth_data:
    auth_data = login_and_extract_data()
    # Insert auth_data into database on users table:
    rds.insert_data_into_db(db_connection=db_connection, table_name='users', data=auth_data)

    db_connection = rds.get_db_connection()

    # Get Brands Data:
    brands_data = get_brands(auth_data)
    # Insert brands_data into database on brands table:
    rds.insert_data_into_db(db_connection=db_connection, table_name='brands', data=brands_data)


    for brand in brands_data:
        # print(brand)
        catagory_id = brand.get('id')

        # call brand products API function:
        brand_products_data = get_brand_products(auth_data=auth_data, brand_id=catagory_id)
        if brand_products_data:
            last_page = brand_products_data.get('data', {}).get('last_page', None)
            
            all_products = []
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
                        imgs = str(product_details.get('imgs'))
                        image_url = str(product_details.get("image"))

                        # Extract pricing
                        prices = product_details.get("leadings", [])[0].get("priceList", [])
                        price_texts = []
                        for price in prices:
                            price_texts.append(f"{price['currency_symbol']}{price['unit_price']} {price['qty_txt2']}")
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
                            '`leading`': Leading, 
                            '`condition`': condition, 
                            'imgs': imgs, 
                            'image_url': image_url, 
                            'price_str': price_str, 
                            'description_name': description_name, 
                            'description_content': description_content 
                        }
                        all_products.append(product_info)
                print(page_no)
                db_connection = rds.get_db_connection()
                rds.insert_data_into_db(db_connection=db_connection, table_name='products', data=all_products)
            print(f"Brand: {brand_name} has {len(all_products)} products")


if __name__ == "__main__":
    main()
