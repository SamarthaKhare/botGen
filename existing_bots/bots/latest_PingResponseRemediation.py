import time
from utility_helper import search_incident, work_in_progress, get_workflow_payload
from remediation_connection_helper import is_device_reachable
from Service_Restart import get_service_state, update_service_state
from remediation_connection_helper import get_ping_output
from utility_helper import get_incident_payload
from servicenow import update_incident
def servicenow_automation():
    """
    This function automates the remediation of ServiceNow incidents related to host unresponsiveness.
    It polls for open incidents, checks device reachability, ping status, and service status,
    and takes appropriate actions to resolve the incidents.
    """
    incident_filter = "short_descriptionLIKEhost not responding"
    workflow_name = "PingResponseRemediation"
    incidents = search_incident(incident_filter)
    if incidents:
        for incident in incidents:
            device_config = get_workflow_payload(incident)
            if work_in_progress(device_config, workflow_name):
                if is_device_reachable(device_config, workflow_name) == "Success":
                    ping_result = get_ping_output(device_config.get('device_name'))
                    service_state = get_service_state(device_config)
                    if service_state == "Running":
                        payload = get_incident_payload(status="RUNNING", workflow_name=workflow_name, process_result=ping_result)
                        update_incident(device_config, payload)
                    elif service_state == "Stopped":
                        service_restart_status = update_service_state(device_config)
                        if service_restart_status == "SUCCESS":
                            payload = get_incident_payload(status="RESTART", workflow_name=workflow_name, process_result=ping_result)
                            update_incident(device_config, payload)
                        else:
                            payload = get_incident_payload(status="RESTART_FAILURE", workflow_name=workflow_name, process_result=ping_result)
                            update_incident(device_config, payload)
                else:
                    print(f"Device {device_config.get('device_name')} is not reachable")
    else:
        print("No incidents found matching the filter.")