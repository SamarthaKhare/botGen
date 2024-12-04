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


def get_result_table(result,is_linux):
    table_result = None
    td_string ="<td style='font-family: calibri, tahoma, verdana; color: black; height: 10px;'>"
    count = 0
    try:
        if is_linux:
            processes = [[item for item in row.values()] for row in result]
            table_result = ""
            for process in processes:
                table_result += "<tr>" + td_string
                count += 1
                process.insert(0, str(count))
                table_result += ("</td>" + td_string).join(process)
                table_result += "</td></tr>"
        else:
            table_result = ""
            for process in result:
                table_result += "<tr>" + td_string
                count += 1
                process_format = str(count) + "|||"+process
                table_result += ("</td>" + td_string).join(process_format.split('|||'))
                table_result += "</td></tr>"
    except Exception as exception:
        print(exception)
    return table_result


def get_workflow_payload(incident):
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
    if 'is_linux' not in device_config:
        device_config['is_linux']=False
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
    try:
        config = MONGO_CONFIG[workflow_name]        
        if all([device_config,failureStatus,config]) and 'ESCALATE_DEVICE_UNREACHABLE' in config:
            sys_id = device_config.get('sys_id',None)
            if sys_id:
                device_name = device_config.get('device_name',None)
                if device_name:
                    incident_payload = config['ESCALATE_DEVICE_UNREACHABLE']['INCIDENT_PAYLOAD']
                    incident_payload["work_notes"] = incident_payload["work_notes"].format(
                                            DEVICE_NAME=device_config.get('_name',None),
                                            SERVICE_NAME=device_config.get('service_name',None),
                                            FAILURE_TYPE=failureStatus)
                    response = update_incident(sys_id,incident_payload)
                    print('response is',response)
                else:
                    print("Device name is missing")
            else:
                print("Sys id is missing")
            
    except Exception as exception:
        print(exception)


def get_incident_payload(status,incident,workflow_name,process_result=None):

    """
    This function prepares the payload to update the incident using status and further formats payload with process_result,device name and other relvant parameters.
    Arguments:
    status: the status for which we will update the incident it can be 'RESOLVED','RUNNING','RESTART','ESCALATE' or 'ESCALATE_DEVICE_UNREACHABLE'
    workflow_name: name of workflow it is used to get payload from config file
    process_result: result of process with which incident is updated, like it can contain list of top resource using process or ping result etc. Defaults to None 
    Return:(dict) the payload for the provided workflow and status
    """
    payload=None
    try:
        config = MONGO_CONFIG[workflow_name]
        if status in config:
            payload = config[status]['INCIDENT_PAYLOAD']
            if "close_notes" in payload:
                payload['close_notes'] = payload["close_notes"].format(ALERT_TYPE=incident.get("alert_type", None),DEVICE_NAME=incident.get("device_name", None),SERVICE_NAME=incident.get('service_name',None))
            if "work_notes" in payload:
                if  process_result is not None:
                    process_result=get_result_table(process_result,incident.get('is_linux'))
                else:
                    process_result = ""
                payload["work_notes"] = payload["work_notes"].format(
                                    DEVICE_NAME=incident.get("device_name", None),
                                    ALERT_TYPE=incident.get("alert_type", None),
                                    THRESHOLD_VALUE=incident.get("threshold_value", None),
                                    TOTAL_USAGE=incident.get('total_usage',None),
                                    FAILURE_TYPE= incident.get('failureType',None),
                                    RESOLVER = incident.get('resolver', None),
                                    SERVICE_NAME=incident.get('service_name',None),
                                    PROCESS_RESULT= process_result
                                    )           
        else:
            print(f"{status} is empty")
    except Exception as exception:
        print(exception)
    return payload

