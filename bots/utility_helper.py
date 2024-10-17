import logging
import requests
import os
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

def remove_spaces(value):
    """
    Recursively removes leading and trailing spaces from a given value, which can be a string, list, or dictionary.
    Args:
        value: The value to remove spaces from. This can be:
               - str: A string where leading and trailing spaces will be removed.
               - list: A list where each element will have spaces removed recursively.
               - dict: A dictionary where keys and values will have spaces removed recursively.
    Returns:
        The value with spaces removed. If the value is a string, leading and trailing spaces are removed.
        If the value is a list or dictionary, spaces are removed recursively from each element.
        If the value is not a string, list, or dictionary, it is returned unchanged.
    """
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return [remove_spaces(item) for item in value]
    elif isinstance(value, dict):
        return {key: remove_spaces(val) for key, val in value.items()}
    else:
        return value

def create_ticket(message):
 
    instance = os.environ['SN_INSTANCE']
    username = os.environ['SN_USERNAME']
    password = os.environ['SN_PASSWORD']
    url = f'https://{instance}.service-now.com/api/now/table/incident'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'short_description': message,
        'description': message,
        'category':'inquiry'
    }
    
    logging.info(f"Sending request to ServiceNow with data: {data}")
    try:
        response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(data))
        response.raise_for_status()  
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response content: {response.content}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {'error': str(e)}
