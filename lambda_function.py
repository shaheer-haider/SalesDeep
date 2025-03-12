import os
import sys
from main import get_brands_totals, scrap_single_brand
import boto3
from utils.salesdeep.brands import BRAND_NAMES
import json
import dotenv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

dotenv.load_dotenv()

aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

def distribute_scraping(brands):
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    brands = list(filter(lambda brand: brand.get("label") in BRAND_NAMES, brands))
    print(f"Scraping {len(brands)} brands")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(
            lambda brand: # brand name
                scrap_single_brand(
                    list(filter(lambda b: b.get("label") == brand, brands))[0],
                    dt,
                    len(BRAND_NAMES)
                ), BRAND_NAMES
            )

    # for brand in BRAND_NAMES:
    #     scrap_single_brand(
    #         list(filter(lambda b: b.get("label") == brand, brands))[0],
    #         dt,
    #         len(BRAND_NAMES)
    #     )

    return {
        'statusCode': 200,
        'body': f'Started scraping {len(BRAND_NAMES)} brands'
    }

if __name__ == "__main__":
    brands = get_brands_totals()
    distribute_scraping(brands)

print(__name__)
