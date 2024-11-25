from Service_Restart import get_service_state_, update_service_state
from servicenow import update_incident
from mongo_config import MONGO_CONFIG
workflow_name = 'PingResponseRemediation'

def update_incident_status(status,incident,payload,ping_result=None):
    """
    """
    try:
        print("updating status")
        if "close_notes" in payload:
            payload['close_notes'] = payload["close_notes"].format(
                                DEVICE_NAME=incident['device_name'],
                                SERVICE_NAME=incident.get('service_name',None))
        if "work_notes" in payload:
            payload["work_notes"] = payload["work_notes"].format(
                                DEVICE_NAME=incident['device_name'],
                                SERVICE_NAME=incident.get('service_name',None),
                                PING_RESULT=ping_result
                                )
                
        print(f"updating incident for {status}")
        print(update_incident(incident['sys_id'],payload))
    except Exception as exception:
        print(exception)

    
def update_status(status,incident,ping_result=None):
    """
    """
    try:
        ping_config = MONGO_CONFIG['PING_REMEDIATE_CONFIG']
        if status in ping_config:
            print("updating status")
            print(incident)
            incident_payload = ping_config[status]['INCIDENT_PAYLOAD']
            if ping_result is not None:
                print('nemp')
                update_incident_status(status,incident,incident_payload,ping_result) 
            else:
                print('emp')
                update_incident_status(status,incident,incident_payload)
            if incident.get('result_time',None) is not None:
                print('updating metrics')
                incident_payload['work_notes'])
        else:
            print(f"{status} is empty")
    except Exception as exception:
        print(exception)


def resolve_ticket_PingResponseRemediation(device_config,ping_result,service_state):
    """
    Resolves a ticket related to ping response remediation by updating the incident status 
    based on the device configuration, ping results, and the current service state.
    Args:
        device_config (dict): Configuration details of the device related to the incident.
        ping_result (str): Result of the ping operation for the device.
        service_state (str): state of the service,if service update was successfull service_state=Restart else service_state=Running.It is used to customize the incident payload and close notes.
    Returns:None
    """
    try:
        if all([device_config,service_state,ping_result]) :
            if ping_result is not None:
                if service_state == 'Restart':
                    update_status("SERVICE_STARTED",device_config,ping_result)
                elif service_state == 'Running':
                    update_status("SERVICE_RUNNING",device_config,ping_result)
            else:
                print("ping output is none")
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)


def escalate_ticket_PingResponseRemediation(device_config,service_state,ping_result=None):
    """
    Escalates the ticket for ping response remediation based on the service state and ping results.
    Args:
        device_config (dict): Configuration details of the device related to the incident.
        service_state (str):The state of the service is 'Restart' when the service is valid but failure occur in updating the service. Other wise invalid service
        ping_result (str, optional): Result of the ping operation for the device. Default is None.
    Returns:None
    """
    try:
        if all([device_config,service_state,ping_result]):
            if service_state == 'Restart':
                update_status("RESTART_FAILURE",device_config,ping_result)
            else:
                print("Invalid service")
        else:
            print("device_config or service_state is none")
    except Exception as exception:
        print(exception)
