import requests

class ApiClient:
    def __init__(self, token):
        self.base_url = "https://sg-leixiao.salesdeep.com/api/"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": token,
            "cache-control": "no-cache",
            "content-type": "application/json;charset=UTF-8",
        }

    def get(self, path):
        url = self.base_url + path
        response = requests.get(url, headers=self.headers)
        return response.json()

    def post(self, path, data):
        url = self.base_url + path
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
