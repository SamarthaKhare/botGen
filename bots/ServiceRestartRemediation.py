from zif_workflow_helper import get_workflow_config_value
from remote_connection_helper import is_ping_success, get_winrm_reachable_status
from Service_Restart import get_state, update_state
from zif_service_bot import get_automation_status_payloads, insert_automation_status
from uniconn.servicenow import update_incident
from GetServiceNowIncidents import get_workflow_payload

workflow_name = 'ServiceRestartRemediation'

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

def device_unreachable_status(device_config,failureStatus):
    """
    Handles the escalation process when a device becomes unreachable. It checks the device status 
    and, if it meets the criteria, it updates the incident with relevant work notes and escalates 
    the issue based on the failure type (e.g., Ping Failure or Winrm Failure).
    Arguments:
    - device_config (dict): A dictionary containing the device details, such as 'sysId' and 'deviceName'.
    - failureStatus (str): A string representing the failure type (e.g., "Ping_Failure" or "Winrm_Failure").
    Returns- None
    """
    try:
        service_config = get_workflow_config_value('SERVICE_RESTART_REMEDIATE_CONFIG')
        if all([device_config,failureStatus,service_config]) and 'ESCALATE_DEVICE_UNREACHABLE' in service_config:
            sys_id = device_config['sysId']
            device_name = device_config['deviceName']
            incident_payload = service_config['ESCALATE_DEVICE_UNREACHABLE']['INCIDENT_PAYLOAD']
            incident_payload['work_notes'] = incident_payload['work_notes'].format(DEVICE_NAME=
                                                    device_name,FAILURE_TYPE=failureStatus)
            response = update_incident(sys_id,incident_payload)
            print('response is',response)
    except Exception as exception:
        print(exception)

def is_device_reachable(device_config):
    """
    Checks if the device is reachable by pinging it and verifying its WinRM status. It retries 
    the connection based on a configured retry count. If the device is reachable, it returns "Success", 
    otherwise it calls the `device_unreachable_status` function to handle the failure.
    Arguments- device_config (dict): A dictionary containing the device details, such as 'deviceName'.
    Returns- str: "Success" if the device is reachable, otherwise it returns the failure status.
    """
    status = None
    try:
        retry_count = get_workflow_config_value("REMEDIATION_RETRY_COUNT")
        if retry_count is None:
            retry_count=3
        device_name=device_config["deviceName"]
        ping_status = is_ping_success(device_name, retry_count)
        if ping_status == True:
            if get_winrm_reachable_status(device_name) == "Success":
                status = "Success"
            else:
                status="Winrm_Failure"
            print(status)  
        else:
            status="Ping_Failure"
            print("Ping Failure")
        if status=="Success":
            return "Success"
        else:
            device_unreachable_status(device_config,status)
    except Exception as exception:
        print(exception)

    
def service_remediation(incident):
    """
    Remediates an issue with a service on a device. It first checks if the device is reachable. 
    If the device is reachable, it checks the state of the service and takes action to restart 
    it if necessary. It then resolves or escalates the incident based on the outcome of the remediation.
    Arguments- incident (dict): A dictionary containing the incident details, including device name and service name.
    Returns- None
    """
    try:
        state = None
        payload = get_workflow_payload(workflow_name,incident)
        if payload is not None:
            # set the ticket to in-progress state
            resolve_ticket(payload,True,None)
            device_name = payload['deviceName']
            # device_name
            if is_device_reachable(payload)=="Success":
                service_name = payload['serviceName']
                service_status = get_state(device_name,service_name)
                print("service status is")
                print(service_status)
                if service_status == 'Stopped':
                    restart_status = update_state(device_name,service_name)
                    if restart_status == 'SUCCESS':
                        state = ['Success','Restart']
                    else:
                        state = ['Failure','Restart']
                elif service_status == 'Running':
                    state = ['Success','Running']
                else:
                    state = ['Failure','Failed']
                if state is not None:
                    if state[0]=="Success":
                        resolve_ticket(payload,state[1])
                    else:
                        escalate_ticket(payload,state[1])
                else:
                    escalate_ticket(payload,"Failed")
            else:
                print("Device is not reachable")
        else:
            print("Required Config is None")
    except Exception as exception:
        print(exception)

def resolve_ticket(device_config,wip=False,service_state=None):
    """
    Resolves the incident ticket by updating its state and incident payload. 
    If the 'wip' flag is set to True, it updates the ticket status to "Work In Progress" 
    using the provided workflow configuration. If 'wip' is False, the function checks the 
    provided service state and updates the ticket with appropriate work and close notes.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sysId', 'deviceName', and 'serviceName'.
    - wip (bool, optional): If True, the ticket is set to "Work In Progress". Defaults to False.
    - service_state (str, optional): The state of the service (e.g., 'Restart'). It is used to customize the incident payload and close notes. Defaults to None.
    Returns-None
    """
    if (wip):
        service_config = get_workflow_config_value('SERVICE_RESTART_REMEDIATE_CONFIG')
        if service_config is not None and 'WIP' in service_config:
            incident_payload = service_config['WIP']['INCIDENT_PAYLOAD']
            response = update_incident(device_config['sysId'],incident_payload)
            print(response)
    else:
        try:
            if device_config is not None and service_state is not None:
                sys_id = device_config['sysId']
                device_name = device_config['deviceName']
                service_name = device_config['serviceName']
                service_config = get_workflow_config_value('SERVICE_RESTART_REMEDIATE_CONFIG')
                incident_payload = service_config['RESOLVED_STARTED']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name)
                incident_payload['close_notes'] = incident_payload['close_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                # check the service state and update acc
                response = update_incident(sys_id,incident_payload)
                print('response is',response)
            else:
                print("device_config or service_state is none")
        except Exception as exception:
            print(exception)   


def escalate_ticket(device_config,service_state):

    """
    Escalates the incident ticket if the device is not in the expected state. 
    If the service state indicates a problem (e.g., 'Restart'), it updates the incident 
    with relevant work notes to escalate the issue for further attention.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sysId', 'deviceName', and 'serviceName'.
    - service_state (str): The state of the service (e.g., 'Restart'). It determines the type of escalation.
    Returns:None
    """
    try:
        if device_config is not None and service_state is not None:
            sys_id = device_config['sysId']
            device_name = device_config['deviceName']
            service_name = device_config['serviceName']
            if service_state == 'Restart':
                service_config = get_workflow_config_value('SERVICE_RESTART_REMEDIATE_CONFIG')
                incident_payload = service_config['RESOLVED_STARTED']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                update_incident(sys_id,incident_payload)
            else:
                print("Invalid service")
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)
