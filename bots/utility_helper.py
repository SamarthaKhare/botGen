import re
import logging
import requests
import os
from requests.auth import HTTPBasicAuth
import json
from remote_connection_helper import is_ping_success,get_winrm_connection_status,get_ssh_reachable_status
from servicenow import update_incident
from dotenv import load_dotenv
from remediation_connection_helper import get_ping_output
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
from mongo_config import MONGO_CONFIG 

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
        if isinstance(value, str) and value.lower() in ['true','false']:
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

def work_in_progress(device_config,workflow_name):
    """
    """
    try:
        config = MONGO_CONFIG[workflow_name]
        if config is not None and 'WIP' in config:
            incident_payload = config['WIP']['INCIDENT_PAYLOAD']
            if update_incident(device_config['sys_id'],incident_payload) is not None:
                return True
            return False
    except Exception as exception:
        return False
        print(exception)

def is_device_reachable(device_config,workflow_name):
    """
    """
    status = None
    try: 
        if device_config is not None: 
            retry_count = 3
            if retry_count is None:
                retry_count = 3
            if is_ping_success(device_config['device_name'],retry_count):
                if device_config['is_linux']:
                    if get_ssh_reachable_status(device_config['device_name'])=="Success":
                        status = "Success"
                        print("SSH Success")
                    else:
                        status = "SSH Failure"
                        print("SSH Failure")
                else:
                    if get_winrm_connection_status(device_config['device_name']) == 'Success':
                        status = "Success"
                        print(status)
                    else:
                        status = "Winrm Failure"
                        print(status)
            else:
                status="Ping Failure"
                print("Ping Failure")
        else:
            print("Device Config is empty.")
        if status == "Success":
            return "Success"
        else:
            device_unreachable_status(device_config,status,workflow_name)
            return status
    except Exception as exception:
        print(exception)

def device_unreachable_status(device_config,failureStatus,workflow_name):
    """
    """
    try:
        config = MONGO_CONFIG[workflow_name]        
        if all([device_config,failureStatus,config]) and 'ESCALATE_DEVICE_UNREACHABLE' in config:
            sys_id = device_config['sys_id']
            device_name = device_config['device_name']
            incident_payload = config['ESCALATE_DEVICE_UNREACHABLE']['INCIDENT_PAYLOAD']
            if workflow_name=="PingResponseRemediation":
                ping_result=get_ping_output(device_name)
                incident_payload["work_notes"] = incident_payload["work_notes"].format(
                                        DEVICE_NAME=device_name,
                                        SERVICE_NAME=device_config.get('service_name',None),
                                        PING_RESULT=ping_result,
                                        FAILURE_TYPE=failureStatus)
            else:
                incident_payload['work_notes'] = incident_payload['work_notes'].format(DEVICE_NAME=device_name,FAILURE_TYPE=failureStatus)
            response = update_incident(sys_id,incident_payload)
            print('response is',response)
    except Exception as exception:
        print(exception)
