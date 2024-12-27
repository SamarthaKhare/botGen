
import logging
import requests
import os
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/.env"
load_dotenv(dotenv_path=dotenv_path)

host = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
print(host)
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
authentication = HTTPBasicAuth(os.getenv('SN_USERNAME'), os.getenv('SN_PASSWORD'))

def get_api_response(attributes):
    response, response_code = None, None
    try:
        if attributes is not None:
            request_type = attributes["type"]
            request_url = attributes["url"]
            request_payload = attributes["payload"]

            if all([request_type, request_url]):
                request_url = "".join([host, request_url])
                if request_type == "GET" and request_payload is None:
                    response = requests.request(request_type, request_url, headers=headers, auth=authentication)
                else:
                    response = requests.request(request_type, request_url, headers=headers, data=json.dumps(request_payload), auth=authentication)
        else:
            print("One or more params are empty")
        
        if response is not None:
            response_code = response.status_code
            response = response.json()
    except Exception as exception:
        error_message = f"Error executing API request: {exception}"
        print(error_message)
    return response, response_code

# Function to update the status of an incident
def update_incident_status(sys_id,payload):
    response = None
    try:
        url = f"/api/now/v2/table/incident/{sys_id}"
        attributes = {"type": "PATCH", "url": url, "payload": payload}
        result, response_code = get_api_response(attributes)
        if response_code == 200:
            response = "SUCCESS"
        else:
            response = result
    except Exception as exception:
        error_message = f"Error updating status: {exception}"
        print(error_message)
    return response

def extract_incident_details(incident_id,sys_id=False):
    details = {}
    try:
        # Construct the API URL for the incident
        url = f"/api/now/v2/table/incident?sysparm_query=number={incident_id}&sysparm_display_value=all"
        attributes = {"type": "GET", "url": url, "payload": None}
        # Get the incident data
        result, response_code = get_api_response(attributes)
        if result is not None and response_code == 200 and "result" in result and len(result["result"]) > 0:
            incident = result["result"][0]
            # Extract relevant details from the incident
            details["short_description"] = incident.get("short_description", {}).get("value", None)
            details["description"] = incident.get("description", {}).get("value", None)
            details["sys_id"] = incident.get("sys_id", {}).get("value", None)
        else:
            print("No valid result found for the given incident_id")
    except Exception as exception:
        error_message = f"Error extracting incident details: {exception}"
        print(error_message)
    if sys_id:
        return details['sys_id']
    return details['description']

def search_incident(filter_query):
	"""
      	    filter out the service now incident and returns a list of incident which matches the provided filer  
 	"""
	result = None
	try:
		base = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
		path =base+ f"/api/now/v2/table/incident?sysparm_query={filter_query}"
		
		response = requests.request("get", path, headers = headers,auth=authentication)
		if response is not None and response.status_code == 200:
			result = response.json()
			return result['result']
	except Exception as exception:
		print(exception)
	return result

filter_query = "short_descriptionLIKEcpu has high resource usage^state=1"
res=search_incident(filter_query)
print(res)
print(len(res))
# 1- extract the inputs in description
# 2- perform the remediation
# 3- use ur update logic to update the tickets involved.
