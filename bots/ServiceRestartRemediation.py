from servicenow import update_incident
from mongo_config import MONGO_CONFIG
workflow_name = 'ServiceRestartRemediation'


def resolve_ticket_ServiceRestartRemediation(device_config,service_state):
    """
    Resolves the incident ticket by updating its state and incident payload,it checks the 
    provided service state and updates the ticket with appropriate work and close notes.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sysId', 'deviceName', and 'serviceName'.
    - service_state (str, optional): The state of the service is either Restart or Running. It is used to customize the incident payload and close notes. Defaults to None.
    Returns-None
    """
    try:
        if device_config is not None and service_state is not None:
            sys_id = device_config['sysId']
            device_name = device_config['deviceName']
            service_name = device_config['serviceName']
            service_config = MONGO_CONFIG[workflow_name]
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


def escalate_ticket_ServiceRestartRemediation(device_config,service_state):

    """
    Escalates the incident ticket if the device is not in the expected state or in case of any failure.If the service state indicates a problem
    ('Restart' or 'Failed'), it updates the incident with relevant work notes to escalate the issue for further attention.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sysId', 'deviceName', and 'serviceName'.
    - service_state (str): The state of the service is 'Restart' if failed while restarting or 'Failed' if failed while updating.It determines the type of escalation.
    Returns:None
    """
    try:
        if device_config is not None and service_state is not None:
            sys_id = device_config['sysId']
            device_name = device_config['deviceName']
            service_name = device_config['serviceName']
            if service_state == 'Restart':
                service_config = MONGO_CONFIG[workflow_name]
                incident_payload = service_config['RESOLVED_STARTED']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                update_incident(sys_id,incident_payload)
            else:
                print("Invalid service")
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)
