import requests
import os
import json
import dotenv

def login_and_extract_data():
    """
    Logs in to the API, extracts relevant user data, saves it as a CSV, and returns the data as a dictionary.

    Returns:
        dict: Extracted user information.
    """

    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Fetch credentials from environment variables
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    # API endpoint
    url = 'https://sg-d.salesdeep.com/v2/login/login'

    # Headers for the request
    headers =  {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-us",
        "cache-control": "no-cache",
        "codekey": "",
        "content-type": "application/json",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sokratiq-staging-key": "sampleAPIKey1234-5678-90abcdef-ghijklmnopqrstuv",
        "Referer": "https://login.salesdeep.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    # Payload (login credentials)
    payload = json.dumps({
        "username": username,
        "pwd": password
    })
    try:
        # Send POST request
        response = requests.post(url, data=payload, headers=headers)
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
            print("login successfull")
            return extracted_info
        else:
            print("Error: Login failed or no data extracted.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
