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
	This function extracts the relevant input parameters/device configuration such as device name, service name, alert type, 
 	and threshold values by parsing the incident description and applying search patterns.
	Arguments:- incident (dict): A dictionary containing incident details, which may include "subcategory", "description", 
	"sys_id", "number", "alertType", etc.
	Returns:
	dict or None: A dictionary containing the constructed payload with fields such as "sysId", "number", 
	"deviceName", "thresholdValue", "alertType", and "is_linux","serviceName". If essential data is missing, 
	it returns None.
    """
    #search pattern
    pattern = r"(\w+(?: \w+)*):\s*([^\n:]+)"
    # Find all matches
    matches = re.findall(pattern, incident['description'])
    #Convert matches to a dictionary
    device_config = {key.strip(): value.strip() for key, value in matches}
    description = incident.get("description")			
    sys_id=incident.get("sys_id")
    number= incident.get("number")
    device_config['sys_id']=sys_id
    device_config['number']=number
    device_config['description']=description
    for key, value in device_config.items():
        if isinstance(value, str) and value.lower() in ['true', 'false']:
            device_config[key] = value.lower() == 'true'
    print(device_config)
    return device_config

def search_incident(filter_query):
	"""
      	    filter out the service now incident and returns a list of incident which matches the provided filer  
 	"""
	result = None
	try:
		base = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
		path =base+ f"/api/now/v2/table/incident?sysparm_query={filter_query}^state=1^ORstate=2"
		
		response = requests.request("get", path, headers = headers,auth=authentication)
		if response is not None and response.status_code == 200:
			result = response.json()
			return result['result']
	except Exception as exception:
		print(exception)
	return result
