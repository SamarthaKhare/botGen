
from cpu_memory_process import get_total_cpu_usage, get_top_cpu_process, get_total_memory_usage, get_top_memory_process,get_top_cpu_consuming,get_top_memory_consuming,get_top_cpu_consuming_process,get_top_memory_consuming_process
from servicenow import update_incident
import sys
import os
# Add the parent directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from mongo_config import MONGO_CONFIG  # Import the MONGO_CONFIG
workflow_name = 'CPUMemoryResourceRemediation'

def get_result_table(result,is_linux):
    """
    """
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

def update_incident_status(status,incident,payload,process=None,process_result=None):
    """
    """
    resolver = None
    try:
        print("updating status")
        print(f"Current payload is : {payload}")

        if status not in ["WIP", "RESOLVED"]:
            payload["assignment_group"] = incident.get('resolver_id', None)
            resolver = incident.get('resolver', None)
            print(payload["assignment_group"])

        if "close_notes" in payload:
            payload['close_notes'] = payload["close_notes"].format(ALERT_TYPE=incident['alert_type'])
        if "work_notes" in payload:
            if  process_result is not None:
                process_result = process_result.replace("\r\n", "")
            else:
                process_result = ""
            payload["work_notes"] = payload["work_notes"].format(
                                DEVICE_NAME=incident.get("device_name", None),
                                ALERT_TYPE=incident.get("alert_type", None),
                                THRESHOLD_VALUE=incident.get("threshold_value", None),
                                TOTAL_USAGE=incident.get('total_usage',None),
                                FAILURE_TYPE= incident.get('failureType',None),
                                RESOLVER = resolver,
                                PROCESS_RESULT  = process_result
                                )      
        print(f"updating incident for {status}")
        print(update_incident(incident['sys_id'],payload))
    except Exception as exception:
        print(exception)

def update_status(status,incident,process=None,process_result=None):
    """
    """
    try:
        cpu_config = MONGO_CONFIG['CPUMemoryResourceRemediation']
        if status in cpu_config:
            incident_payload = cpu_config[status]['INCIDENT_PAYLOAD']
            if process_result is not None:
                update_incident_status(status,incident,incident_payload,process, process_result)  
            else:
                update_incident_status(status,incident,incident_payload)
        else:
            print(f"{status} is empty")
    except Exception as exception:
        print(exception)


   
def resolve_ticket(device_config,total_usage):
    """
    for-CPUMemoryResourceRemediation it updates the incident status to "RESOLVED" with the provided device configuration and total cpu resource usage 
    The device configuration is updated with the total usage before calling the update_status function to mark the incident as resolved.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details.
    - total_usage (float): The total usage value to be added to the device configuration.
    Returns:- None
    """
    try:
        if device_config['is_comment_code']=='True' or device_config['is_vault_agent']=='True':
            update_status('ESCALATE_CLUSTER_SERVERS',incident=device_config)
            return
        print(device_config)
        print(total_usage)
        if device_config is not None and total_usage is not None:
            device_config['total_usage'] = total_usage
            update_status('RESOLVED',incident=device_config)
        else:
            print("Device Config or actual value is empty.")
    except Exception as exception:
        print(exception)


def get_actual_threshold(device_config):
    """
    Determines and retrieves the total usage of cpu/memory  for a given device based on its configuration.
    The function takes in the `device_config` dictionary containing device settings such as alert type, 
    OS type, and device name.If the threshold is successfully retrieved, it is processed and returned 
    as a cleaned string else this function update incident with an escalation status.
    Args:device_config (dict): A dictionary containing the following keys:
            - "alert_type" (str): The type of alert, either 'CPU' or 'MEMORY'.
            - "is_linux" (bool): Specifies if the device is a Linux machine.
            - "device_name" (str): The name or identifier of the device.
    Returns:str or None: The actual threshold value as a string if successfully retrieved and processed, 
        or None if an error occurs or the threshold is unavailable.
    """
    try:
        actual_threshold = None
        if device_config:
            alert_type = device_config["alert_type"]
            is_linux = device_config['is_linux']
            device_name = device_config["device_name"]
            retry_count=3
            if alert_type == 'CPU':
                if is_linux:
                    actual_threshold = get_top_cpu_consuming(device_name,retry_count)
                else:
                    actual_threshold = get_total_cpu_usage(device_name,retry_count)
            elif alert_type == 'MEMORY':
                if is_linux:
                    actual_threshold = get_top_memory_consuming(device_name,retry_count)
                else:
                    actual_threshold = get_total_memory_usage(device_name,retry_count)
            if actual_threshold is not None:
                actual_threshold = actual_threshold.encode().decode().strip()
                print(f'actual thresold is {actual_threshold}')
            else:
                print("Threshold empty")
                device_config['failureType'] = "SSH Failure"
                device_config['result_time'] = 3
                update_status('ESCALATE_DEVICE_UNREACHABLE',incident=device_config)
        else:
            print("Device Config is None")
        return actual_threshold
    except Exception as exception:
        print(exception)


def escalate_ticket_CPUMemoryResourceRemediation(device_config,total_usage,retry_count):
    """
    for-CPUMemoryResourceRemediation it escalates the ticket if the resource usage (CPU or Memory) exceeds a specified threshold. The 
    function retrieves the top resource-consuming processes for the device (based on whether it's 
    Linux or not) and triggers an escalation if the process information is available. The status is 
    updated with the top processes and their results.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details, such as device name, 
    alert type, and whether the device is Linux-based.
    - total_usage (float): The total resource usage value.
    - retry_count (int): The number of retries for fetching resource data.
    Returns:None
    """
    try:
        if all([device_config,total_usage,retry_count]):
            device_config['total_usage'] = total_usage
            if device_config["alert_type"] == 'CPU':
                result = None
                if device_config['is_linux']:
                    print("linux case")
                    top_process = get_top_cpu_consuming_process(device_config['device_name'],5,retry_count)
                    print(top_process)
                    result = get_result_table(top_process,True)
                else:
                    top_process = get_top_cpu_process(
                        device_config["device_name"],5,retry_count)
                    print(top_process)
                    if top_process is not None:
                        top_process = top_process.split('~~~')[:-1]
                        result = get_result_table(top_process,False)
                if result is not None:
                    update_status('ESCALATE_RESOURCE_HIGH_USAGE',incident=device_config,process=top_process,process_result=result)
                else:
                    print("CPU Top Process Result is empty")

            elif device_config["alert_type"] == 'MEMORY':
                if device_config['is_linux']:
                    print('linux case')
                    top_process = get_top_memory_consuming_process(device_config['device_name'],5,retry_count)
                    result = get_result_table(top_process,True)
                else:
                    top_process = get_top_memory_process(device_config["device_name"],5,retry_count)
                    if top_process is not None:
                        top_process = top_process.split('~~~')[:-1]
                        result = get_result_table(top_process,False)
                if result is not None:
                    update_status('ESCALATE_RESOURCE_HIGH_USAGE',incident=device_config,process=top_process,process_result=result)
                else:
                    print("Memory Top Process Result is None.")
        else:
            print('Device config is none.')
    except Exception as exception:
        print(exception)
