import os
import sys
from main import scrap_single_brand
import boto3
from utils.salesdeep.brands import BRAND_IDS
import json
import dotenv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

dotenv.load_dotenv()

aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

def trigger_brand_scraping(brand_name, brand_id, dt):
    if __name__ == "__main__":
        print(f"Starting scraping process for brand: {brand_name}")
        with ThreadPoolExecutor() as executor:
            executor.submit(scrap_single_brand, brand_name, brand_id, dt, len(BRAND_IDS.keys()))
    else:
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName='salesdeep-scrapping',
            InvocationType='Event',
            Payload=json.dumps({
                "action": "scrap_brand",
                "brand_name": brand_name,
                "brand_id": brand_id,
                "dt": dt,
                "number_of_brands": len(BRAND_IDS.keys())
            })
        )

def distribute_scraping(event, context):
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    for brand_name, brand_id in BRAND_IDS.items():
        trigger_brand_scraping(brand_name, brand_id, dt)
    return {
        'statusCode': 200,
        'body': f'Started scraping {len(BRAND_IDS)} brands'
    }

def lambda_handler(event, context):
    actions = {
        "default": distribute_scraping,
        "scrap_brand": lambda e, c: scrap_single_brand(
            e.get('brand_name'),
            e.get('brand_id'),
            e.get('dt'),
            e.get('number_of_brands')
        )
    }

    action = event.get("action", "default")
    return actions[action](event, context)

if __name__ == "__main__":
    lambda_handler({}, None)
print(__name__)
