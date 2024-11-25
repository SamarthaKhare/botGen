from Service_Restart import get_service_state_, update_service_state
from servicenow import update_incident
from mongo_config import MONGO_CONFIG
workflow_name = 'PingResponseRemediation'

def update_incident_status(status,incident,payload,ping_result=None):
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


