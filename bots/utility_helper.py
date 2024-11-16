import re
import logging
import requests
import os
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
authentication = HTTPBasicAuth(os.getenv('SN_USERNAME'), os.getenv('SN_PASSWORD'))

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

def get_workflow_payload(incident):
    """
    Extracts device configuration/remediation inputs from the description field of an incident .
    The function uses a regular expression pattern to search for matches in the format "Key: Value" 
    within the incident description, and then it creates a dictionary with the extracted data.
    Arguments:Incident (dict): A dictionary containing the incident details, where 'description' is a key that 
    holds a string with key-value pairs in the format "Key: Value".
    Returns:dict: A dictionary containing the extracted key-value pairs from the incident description.
    """
    #search pattern
    pattern = r"(\w+(?: \w+)*):\s*([^\n:]+)"
    # Find all matches
    print(incident)
    matches = re.findall(pattern, incident['description'])
    #Convert matches to a dictionary
    device_config = {key.strip(): value.strip() for key, value in matches}
    return device_config

def search_incidents(filter_query):
	"""
	This function searches for incidents in Service Now using a specified filter pattern.
	Args:filter_pattern (str): The pattern to filter incidents of Service Now.
	Returns:The list of all the incident that matches with the filter patter, otherwise None.
	"""
	result = None
	try:
		base = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
		path =base+ f"/api/now/v2/table/incident?sysparm_query=state=1^ORstate=2^{filter_query}"
		
		response = requests.request("get", path, headers = headers,auth=authentication)
		if response is not None and response.status_code == 200:
			result = response.json()
			return result['result']
	except Exception as exception:
		print(exception)
	return result
