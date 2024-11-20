import requests
import json
import os
import sys
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
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
def update_incident(sys_id,data):
    response = None
    try:
        payload=\
        {
            "close_code": data['close_code'],
            "incident_state": data['state'],
            "caller_id": "admin",
            "close_notes": data['close_notes'],
            'work_notes':data['work_notes']
		}
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
