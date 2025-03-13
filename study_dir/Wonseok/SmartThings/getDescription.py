from dotenv import load_dotenv
import os

import requests

load_dotenv()

deviceId = os.environ.get("switch")

access_token = os.environ.get("PAT")
headers = {'Authorization': 'Bearer ' + access_token}

URL = f"https://api.smartthings.com/v1/devices/{deviceId}"


def get_the_description_of_a_device():
    response = requests.get(URL, headers=headers)
    return response.json()
