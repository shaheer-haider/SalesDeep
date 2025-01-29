import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./env")

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
            extracted_info = {
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
            }

            # Convert to DataFrame and save as CSV
            df = pd.DataFrame([extracted_info])
            csv_filename = "user_info.csv"
            df.to_csv(csv_filename, index=False)

            print(f"CSV file '{csv_filename}' saved successfully!")

            return extracted_info  # Return extracted data as dictionary

        else:
            print("Error: Login failed or no data extracted.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
user_data = login_and_extract_data()
if user_data:
    print("Extracted User Data:", user_data)