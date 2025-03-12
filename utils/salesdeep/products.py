from .api_client import ApiClient
import requests

# Fetch brand products
def get_brand_products(token, brand_id, page_no=1, page_size=100):
    client = ApiClient(token)
    data = client.post("discover/listCategorySalesPrice", {"category_id": brand_id, "pageNo": page_no, "pageSize": page_size})
    return data

# Fetch products details:
def get_product_details(token, sku):
    client = ApiClient(token)
    data = client.post("discover/skuDetail", {'sku': str(sku), 'customer_info_id': "", 'currency': ""})
    return data
