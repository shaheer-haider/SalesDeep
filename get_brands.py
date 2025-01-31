import requests
import csv
from login import login_and_extract_data 

def get_brands(auth_data):
    token = auth_data.get("token")
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
        csv_data = []
        for category in brand_data:
            for brand in category.get("children", []):
                csv_data.append([
                    brand.get("id"),
                    brand.get("parent_id"),
                    brand.get("label"),
                    brand.get("stage"),
                    brand.get("sku_num"),
                    brand.get("image"),
                    brand.get("all_sku_num")
                ])
        
        # Save to CSV
        file_name = "brands.csv"
        with open(f"./DATA/{file_name}", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "parent_id", "label", "stage", "sku_num", "image", "all_sku_num"])
            writer.writerows(csv_data)
        
        return brand_data
    else:
        print("Failed to fetch brands:", response.text)
        return None

# # Example usage
# if __name__ == "__main__":
#     # Get authentication details from login function
#     auth_data = login_and_extract_data()
#     brands = get_brands(auth_data)
#     print(brands)
#     print("Brands fetched:", len(brands) if brands else 0)
