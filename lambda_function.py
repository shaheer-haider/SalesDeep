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

def distribute_scraping():
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda brand: scrap_single_brand(brand[0], brand[1], dt, len(BRAND_IDS.keys())), BRAND_IDS.items())

    return {
        'statusCode': 200,
        'body': f'Started scraping {len(BRAND_IDS)} brands'
    }

if __name__ == "__main__":
    distribute_scraping()

print(__name__)
