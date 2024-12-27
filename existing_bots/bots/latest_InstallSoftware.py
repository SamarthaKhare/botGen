from utility_helper import search_incident, work_in_progress, get_workflow_payload, is_device_reachable, get_incident_payload
from servicenow import update_incident
from va_windows_software_helper import install_vmware_tools

def install_software_on_windows():
    """
    This function installs software on a Windows machine by leveraging ServiceNow incidents and workflows.
    It retrieves incidents, checks device reachability, installs VMware Tools, and updates the incident status accordingly.
    """
    incident_filter = 'check'
    workflow_name = 'InstallSoftware'
    incidents = search_incident(incident_filter)
    if incidents:
        for incident in incidents:
            if  work_in_progress(incident, workflow_name):
                device_config = get_workflow_payload(incident)
                if is_device_reachable(device_config, workflow_name) == 'Success':
                    try:
                        # Assuming installer_path and is_ntlm are provided in device_config
                        install_result = install_vmware_tools(device_config.get('device_name'), device_config.get('installer_path'), device_config.get('is_ntlm', True))
                        if install_result == "Success":
                            payload = get_incident_payload('RESOLVED', workflow_name, process_result=install_result)
                        else:
                            payload = get_incident_payload('ESCALATE', workflow_name, process_result=install_result)
                        update_incident(device_config, payload)
                    except Exception as e:
                        payload = get_incident_payload('ESCALATE', workflow_name, process_result=str(e))
                        update_incident(device_config, payload)
