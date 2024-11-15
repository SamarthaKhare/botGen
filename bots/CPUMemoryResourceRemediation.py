
from cpu_memory_process import get_total_cpu_usage, get_top_cpu_process, get_total_memory_usage, get_top_memory_process,get_top_cpu_consuming,get_top_memory_consuming,get_top_cpu_consuming_process,get_top_memory_consuming_process
from zif_workflow_helper import get_workflow_config_value
from zif_service_bot import get_automation_status_payloads, insert_automation_status
from remote_connection_helper import is_ping_success,get_winrm_reachable_status,get_ssh_reachable_status
from uniconn.servicenow import update_incident
from GetServiceNowIncidents import get_workflow_payload

workflow_name = 'CPUMemoryResourceRemediation'

def get_result_table(result,is_linux):
    """
    Generates an HTML table representation of the resource-consuming processes based on the provided 
    result data. If the device is Linux-based, it formats the data into rows with process information 
    in each cell. If the device is not Linux-based, it formats the data differently. The table is 
    formatted with specific styling for better readability.
    Arguments:
    - result (list): A list of process data to be displayed in the table. For Linux, this is a list 
    of dictionaries with process details; for non-Linux, it is a list of strings representing process information.
    - is_linux (bool): A flag indicating whether the device is Linux-based or not, which determines 
    the format of the table.
    Returns- str: A string containing the HTML table of the process data.
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

def update_metrics(result_time,remarks):
    try:
        effort_config = get_workflow_config_value("REMEDIATE_EFFORT_SAVINGS")
        if effort_config is not None and workflow_name.upper() in effort_config:
            effort_saving = effort_config[workflow_name.upper()]
            status_payload = get_automation_status_payloads(
                workflow_name, result_time, True,
                'Completed', remarks, effort_saving)
            if status_payload is not None:
                insert_automation_status(status_payload)
    except Exception as exception:
        print(exception)

def update_incident_status(status,incident,payload,process=None,process_result=None):
    """
    Updates the status of an incident in an ITSM tool. The function prepares and formats the payload 
    based on the incident details and updates the incident with the specified status. Additional 
    information such as work notes and close notes are formatted using incident attributes.
    Arguments:
    - status (str): The new status to be assigned to the incident ("WIP" or "RESOLVED").
    - incident (dict): A dictionary containing incident details such as sys_id, alert_type,resolver_id, etc.
    - payload (dict): The payload to be updated for the incident.
    - process (optional): The process details associated with the incident, if any.
    - process_result (optional, str): The result of the process, which will be included in 
    the work notes.
    Returns- None: The function performs updates and prints the outcome or error messages.
    """
    resolver = None
    try:
        print("updating status")
        print(incident)
        print(payload)

        if status not in ["WIP", "RESOLVED"]:
            payload["assignment_group"] = incident.get('resolver_id', None)
            resolver = incident.get('resolver', None)
            print(payload["assignment_group"])

        if "close_notes" in payload:
            payload['close_notes'] = payload["close_notes"].format(
                                ALERT_TYPE=incident['alert_type'])
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
    Updates the status of an incident based on a workflow configuration. The function retrieves 
    the appropriate configuration for the status, formats the incident payload, and updates the 
    incident status. If a result time is present, it updates the metrics accordingly.
    Arguments:
    - status (str): The status to update the incident with.
    - incident (dict): A dictionary containing incident details such as result_time and attributes 
    required for formatting the payload.
    - process (optional): The process details associated with the incident, if any.
    - process_result (optional, str): The result of the process, if available.
    Returns:None: The function updates the incident and prints logs or error messages.
    """
    try:
        cpu_config = get_workflow_config_value('CPUMEMORY_REMEDIATION_CONFIG')
        if status in cpu_config:
            incident_payload = cpu_config[status]['INCIDENT_PAYLOAD']
            if process_result is not None:
                update_incident_status(status,incident,incident_payload,process, process_result)  
            else:
                update_incident_status(status,incident,incident_payload)
            if incident.get('result_time',None) is not None:
                print('updating metrics')
                update_metrics(incident['result_time'],
                incident_payload['work_notes'])
        else:
            print(f"{status} is empty")
    except Exception as exception:
        print(exception)

def is_device_reachable(device_config):
    """
    Checks the reachability status of a device based on its configuration. It first checks if the 
    device is reachable via ping, then verifies its accessibility over SSH (for Linux devices) or 
    WinRM (for non-Linux devices). The function returns the status of the device based on the 
    reachability checks.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details such as device_name,and whether the device is Linux or not.
    Returns:str: A string indicating the reachability status ("Success", "Ping Failure", "SSH Failure", 
    "Winrm Failure").
    """
    status = None
    try: 
        if device_config is not None: 
            retry_count = get_workflow_config_value("REMEDIATION_RETRY_COUNT")
            if retry_count is None:
                retry_count = 3
            if is_ping_success(device_config['device_name'],retry_count):
                if device_config['is_linux']:
                    if get_ssh_reachable_status(device_config['device_name']):
                        status = "Success"
                        print("Success")
                    else:
                        status = "SSH Failure"
                        print("SSH Failure")
                else:
                    if get_winrm_reachable_status(device_config['device_name']) == 'Success':
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
            return device_unreachable_status(device_config,status)
    except Exception as exception:
        print(exception)
   
def resolve_ticket(device_config,total_usage):
    """
    Updates the incident status to "RESOLVED" with the provided device configuration and total cpu resource usage 
    The device configuration is updated with the total usage before calling the update_status function to mark the incident as resolved.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details.
    - total_usage (float): The total usage value to be added to the device configuration.
    Returns:- None
    """
    try:
        print(device_config)
        print(total_usage)
        if device_config is not None and total_usage is not None:
            device_config['total_usage'] = total_usage
            update_status('RESOLVED',incident=device_config)
        else:
            print("Device Config or actual value is empty.")
    except Exception as exception:
        print(exception)


def device_unreachable_status(device_config,failureStatus):
    """
    Handles the escalation process when a device is unreachable. It checks the CPU/Memory remediation 
    configuration to determine if the failure status should lead to an "ESCALATE_DEVICE_UNREACHABLE" 
    status. If the failure status and device configuration are provided, it updates the incident with 
    the failure type and triggers the status update.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details.
    - failureStatus (str): The failure status indicating the reason for the device's unreachability.
    Returns- None
    """
    try:
        cpu_memory_config = get_workflow_config_value('CPUMEMORY_REMEDIATION_CONFIG')
        if cpu_memory_config is not None and "ESCALATE_DEVICE_UNREACHABLE" in cpu_memory_config:
            print(failureStatus)
            if device_config is not None and failureStatus is not None:
                device_config['failureType'] = failureStatus
                device_config['result_time'] = 1
                update_status('ESCALATE_DEVICE_UNREACHABLE',incident=device_config)
        else:
            print("Device Config or ping output is empty.")
    except Exception as exception:
        print(exception)


def get_resource_usage(device_config):
    """
    Evaluates the resource usage of a device and performs actions based on predefined thresholds 
    for CPU or memory. Handles both Linux and non-Linux systems and supports escalation if needed.
    Steps:
    1. Retrieves the retry count from the workflow configuration and updates the incident status to "WIP".
    2. If conditions like 'is_comment_code' or 'is_vault_agent' are true, escalates to cluster servers.
    3. Extracts device details, including `device_name`, `threshold_value`, and `alert_type`.
    4. Fetches resource usage based on the device type and alert type (CPU or MEMORY).
    5. If usage data is available, compares it to the threshold:
       - Resolves the ticket if usage is within the threshold.
       - Escalates the ticket if usage exceeds the threshold.
    6. Escalates for SSH failure if usage data is not retrievable.
    7. Catches and logs any exceptions encountered.
    Args:
        device_config (dict): Device configuration, including device_name,threshold_value,alert_type etc
    """
    actual_threshold = None
    try:
        retry_count = get_workflow_config_value("REMEDIATION_RETRY_COUNT")
        if device_config is not None and retry_count is not None :
            update_status('WIP',incident=device_config)
            if device_config['is_comment_code'] or device_config['is_vault_agent']:
                update_status('ESCALATE_CLUSTER_SERVERS',incident=device_config)
            device_name = device_config["device_name"]
            threshold_value = device_config["threshold_value"]
            alert_type = device_config["alert_type"]
            is_linux = device_config['is_linux']
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
                print(actual_threshold)
                actual_threshold = actual_threshold.encode().decode().strip()
                print('actual thresold is')
                print(actual_threshold)
            else:
                print("Threshold empty")
                device_config['failureType'] = "SSH Failure"
                device_config['result_time'] = 3
                update_status('ESCALATE_DEVICE_UNREACHABLE',incident=device_config)
                
            if float(actual_threshold) <= float(threshold_value):
                return resolve_ticket(device_config,actual_threshold)
            else:
                return escalate_ticket(device_config,actual_threshold,retry_count)
        else:
            print("Device Config is None")
    except Exception as exception:
        print(exception)

def escalate_ticket(device_config,total_usage,retry_count):
    """
    Escalates the ticket if the resource usage (CPU or Memory) exceeds a specified threshold. The 
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
                    top_process = get_top_cpu_consuming_process(
                        device_config['device_name'],5,retry_count)
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
                    update_status('ESCALATE_RESOURCE_HIGH_USAGE',
                    incident=device_config,process=top_process,process_result=result)
                else:
                    print("CPU Top Process Result is empty")

            elif device_config["alert_type"] == 'MEMORY':
                if device_config['is_linux']:
                    print('linux case')
                    top_process = get_top_memory_consuming_process(
                        device_config['device_name'],5,retry_count)
                    result = get_result_table(top_process,True)
                else:
                    top_process = get_top_memory_process(
                        device_config["device_name"],5,retry_count)
                    if top_process is not None:
                        top_process = top_process.split('~~~')[:-1]
                        result = get_result_table(top_process,False)
                if result is not None:
                    update_status('ESCALATE_RESOURCE_HIGH_USAGE',
                    incident=device_config,process=top_process,process_result=result)
                else:
                    print("Memory Top Process Result is None.")
        else:
            print('Device config is none.')
    except Exception as exception:
        print(exception)

    
