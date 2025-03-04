from .api_client import ApiClient
import requests

# Fetch brand products
def get_brand_products(token, brand_id, page_no=1, page_size=100):
    client = ApiClient(token)
    data = client.post("goods/productList", {"brand_id": brand_id, "pageNo": page_no, "pageSize": page_size})
    return data

def get_brand_product_count(token, brand_id):
    """Get total number of products for a brand"""
    data = get_brand_products(token, brand_id, page_no=1, page_size=1)
    return data.get('total', 0)

# Fetch products details:
def get_product_details(token, sku):
    client = ApiClient(token)
    data = client.post("discover/skuDetail", {'sku': str(sku[0]), 'customer_info_id': "", 'currency': ""})
    return data
