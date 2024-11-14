import requests
import json
import os
import sys
from zif_workflow_helper import get_workflow_config_value 

headers = {"Content-Type": "application/json"}

def search_incidents(filter_pattern):
	"""
	This function searches for incidents in ServiceNow using a specified filter pattern.
	Args:filter_pattern (str): The pattern to filter incidents in ServiceNow.
	Returns:dict or None: The result of the search operation in JSON format if successful, otherwise None.
	"""
	result = None
	try:
		base_resource = os.environ["UNICONN_API_URL"]
		endpoint = get_workflow_config_value("UNICONN_IMPORT_ENDPOINT")
		path = "{}{}".format(base_resource, endpoint)
		request_payload = {
			"operation": "REMEDIATE_ITSM",
			"exportedTool": "ServiceNow",
			"payload": {
				"apiFilter": filter_pattern
			}
		}
		response = requests.request("POST", path, headers = headers, data = json.dumps(request_payload))
		if response is not None and response.status_code == 200:
			result = response.json()
	except Exception as exception:
		print(exception)
	return result

def update_incident(sys_id, payload):
	"""	
	This function updates an incident in ServiceNow using the provided system ID and payload.
	Args:
		sys_id (str): The system ID of the incident to be updated.
		payload (dict): A dictionary containing the data to update the incident with.
	Returns:str: "SUCCESS" if the update is successful, "ERROR" if an error occurs, or "NO RESULT" if no response is received.
	"""
	result = "NO RESULT"
	try:
		base_resource = os.environ["UNICONN_API_URL"]
		endpoint = get_workflow_config_value("UNICONN_EXPORT_ENDPOINT")
		path = "{}{}".format(base_resource, endpoint)
		request_payload = {
			"operation": "REMEDIATE_ITSM",
			"exportedTool": "ServiceNow",
			"payload": {
				"refId": sys_id,
				"request": str(json.dumps(payload))
			}
		}
		response = requests.request("POST",path, headers=headers, data=json.dumps(request_payload))
		if response is not None and response.status_code == 200:
			result = "SUCCESS"
	except Exception as exception:
		print(exception)
		result = "ERROR"
	return result