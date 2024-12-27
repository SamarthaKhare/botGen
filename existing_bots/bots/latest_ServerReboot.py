from utility_helper import search_incident, work_in_progress, get_workflow_payload
from servicenow import update_incident
def process_server_reboot_incidents():
    """
    This function polls ServiceNow for open incidents with a specific filter, checks device connectivity,
    and either updates the incident state or escalates it based on software requirements.
    """
    incident_filter = "check"
    workflow_name = "ServerReboot"
    incidents = search_incident(incident_filter)
    if incidents:
        for incident in incidents:
            if work_in_progress(incident, workflow_name):
                device_config = get_workflow_payload(incident)
                if device_config:
                    print(f"Processing incident {incident} with device config: {device_config}")
                else:
                    print(f"Skipping incident {incident} due to missing or invalid device configuration.")
            else:
                print(f"Failed to update the state of {incident} to Work in Progress")