from servicenow import update_incident
from mongo_config import MONGO_CONFIG
workflow_name = 'ServiceRestartRemediation'


def resolve_ticket_ServiceRestartRemediation(device_config,service_state):
    """
    For-ServiceRestartRemediation it resolves the incident ticket by updating its state and incident payload,it checks the 
    provided service state and updates the ticket accordingly with appropriate work and close notes.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sys_id', 'device_name', and 'service_name'.
    - service_state (str, optional): state of the service,if service update was successfull service_state=Restart else service_state=Running.It is used to customize the incident payload and close notes.
    Returns-None
    """
    try:
        if device_config is not None and service_state is not None:
            sys_id = device_config['sys_id']
            device_name = device_config['device_name']
            service_name = device_config['service_name']
            service_config = MONGO_CONFIG[workflow_name]

            if service_state=="Restart":
                incident_payload = service_config['RESOLVED']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                incident_payload['close_notes'] = incident_payload['close_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                # check the service state and update acc
                print(incident_payload)
                response = update_incident(sys_id,incident_payload)
                print('response is',response)
            elif service_state=='Running':
                #print("I am here")
                incident_payload = service_config['RUNNING']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                incident_payload['close_notes'] = incident_payload['close_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                # check the service state and update acc
                response = update_incident(sys_id,incident_payload)
                print('response is',response)
            else:
                print('Invalid Service State')
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)   


def escalate_ticket_ServiceRestartRemediation(device_config,service_state):

    """
    For- ServiceRestartRemediation it escalates the incident ticket if the device is not in the expected state or in case of any failure.If the service state indicates a problem
    ('Restart' or 'Failed'), it updates the incident with relevant work notes to escalate the issue for further attention.
    Arguments:
    - device_config (dict): A dictionary containing the device details like 'sys_id', 'device_name', and 'service_name'.
    - service_state (str): state of the service either Restart or Invalid.
    Returns:None
    """
    try:
        if device_config is not None and service_state is not None:
            sys_id = device_config['sys_id']
            device_name = device_config['device_name']
            service_name = device_config['service_name']
            if service_state != 'Invalid':
                service_config = MONGO_CONFIG[workflow_name]
                incident_payload = service_config['ESCALATE']['INCIDENT_PAYLOAD']
                incident_payload['work_notes'] = incident_payload['work_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                incident_payload['close_notes'] = incident_payload['close_notes'].format(SERVICE_NAME=service_name,DEVICE_NAME=device_name)
                update_incident(sys_id,incident_payload)
            else:
                print("Invalid service")
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)
