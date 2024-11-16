import requests
import json
import os
import sys
from zif_workflow_helper import get_workflow_config_value 

headers = {"Content-Type": "application/json"}

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
		base_resource = base = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
		#endpoint = get_workflow_config_value("UNICONN_EXPORT_ENDPOINT")
		endpoint=f"/api/now/v2/table/incident/{sys_id}"
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
