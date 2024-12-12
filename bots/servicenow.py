import requests
import json
import os
import sys
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
from zif_mongo_helper import get_single_document
query={"tenantId": "6735248edb0aefa5f65131b0", "key": "CPUMemoryResourceRemediation"}
host = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
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
def update_incident(incident,data):
    response = None
    payload={}
    sys_id=incident.get('sysId',None)
    if sys_id:
        for key in data:
            payload[key]=data[key]
        if 'state' in payload and payload['state']=='6':
            payload['close_code']='Solution Provided'
        try:
            url = f"/api/now/v2/table/incident/{sys_id}"
            attributes = {"type": "PATCH", "url": url, "payload": payload}
            result, response_code = get_api_response(attributes)
            if response_code == 200:
                response = "SUCCESS"
        except Exception as exception:
            error_message = f"Error updating status: {exception}"
            print(error_message)
    else:
        print("sys id missing")
    return response

def create_incident(fpayload):
    response = None
    try:
        url = "/api/now/table/incident"
        payload=fpayload.copy()
        del payload['alertDescription']
        del payload['_id']
        payload['alertDateTime']=payload['alertDateTime'].strftime('%Y-%m-%d %H:%M:%S')
        mongodoc=get_single_document(query)
        data={
            'description':mongodoc['description'],
            'short_description':mongodoc['shortDescription'],
            'impact':'1',
            'urgency':'1'
        }
        attributes = {"type": "POST", "url": url, "payload": data}
        result, response_code = get_api_response(attributes)
        if result is not None and response_code == 201:
            sys_id = result['result']['sys_id']
            print(f"Incident number : {result['result']['number']}")
            print(f"Sys_id is {sys_id}")
            response = sys_id
        else:
            response = result
    except Exception as exception:
        error_message = f"Error creating incident: {exception}"
        print(error_message)
        response = {"error": error_message}
    return response

def check_incident_status(sys_id):
    response = None
    try:
        url = f"/api/now/v2/table/incident/{sys_id}"
        attributes = {"type": "GET", "url": url,'payload':None}
        result, response_code = get_api_response(attributes)
        if response_code == 200:
            response = result['result']['state']
            if(response=='1'):
                response='open'
            print(response)
        else:
            response = 'Faliure'
    except Exception as exception:
        error_message = f"Error updating status: {exception}"
        print(error_message)
    return response
