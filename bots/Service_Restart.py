
from remote_connection_helper import get_winrm_script_result
from servicenow import update_incident
from mongo_config import MONGO_CONFIG
workflow_name='ServiceRestartRemediation'
def get_state_ServiceRestartRemediation(device_config):
    """
    Checks the current status of a specified Windows service on a remote host using WinRM for service restart remediation.
    It runs a PowerShell command to determine if the service is valid and, if so, retrieves its status.
    Arguments- device_config (dict): A dictionary containing the device details like 'sys_id', 'device_name', and 'service_name'.
    Returns:- str or None: The status of the service (e.g., "Running", "Stopped), or 'Invalid' if the service is not found. Returns None in case of an exception.
    """
    result = None
    try:
        service_config = MONGO_CONFIG[workflow_name]
        if service_config is not None and 'WIP' in service_config:
            incident_payload = service_config['WIP']['INCIDENT_PAYLOAD']
            response = update_incident(device_config['sys_id'],incident_payload)
            print(response)
        host_name=device_config['device_name']
        service_name=device_config['service_name']
        if host_name is not None and service_name is not None:
            command = "if((Get-Service -Name '"+service_name+"' -ErrorAction SilentlyContinue) -eq $null){echo 'Invalid'} else {(Get-Service -Name '"+service_name+"').Status}"
            result = get_winrm_script_result(host_name, command,True).strip()
    except Exception as exception:
        print(exception)
    return result


def update_state_ServiceRestartRemediation(device_config):
    """
    Attempts to start a specified Windows service on a remote host using WinRM for service restart remediation.
    It uses a PowerShell command to try starting the service multiple times and checks if the service reaches the "Running" status. 
    Arguments- device_config (dict): A dictionary containing the device details like 'sys_id', 'device_name', and 'service_name'.
    Returns:- str or None: "SUCCESS" if the service starts successfully, "FAILURE" if it fails to start, or None in case of an exception.
    """
    result = None
    try:
        
        host_name=device_config['device_name']
        service_name=device_config['service_name']
        if host_name is not None and service_name is not None:
            success_message = "SUCCESS"
            error_message = "FAILURE"

            command = f"""
            try {{
                $MaxRepeat = 2
                Start-Service {service_name} -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
                do {{
                    $Count = (Get-Service {service_name} | Where-Object {{ $_.Status -eq 'Running' }}).Count
                    $MaxRepeat -= 1
                    Start-Sleep -Milliseconds 5000
                }} until ($Count -eq 1 -or $MaxRepeat -eq 0)
                
                $CurrentStatus = (Get-Service {service_name}).Status
                if ($CurrentStatus -eq 'Running' -or $CurrentStatus -eq 'StartPending') {{
                    Write-Output "{success_message}"
                }} else {{
                    Start-Service {service_name} -WarningAction SilentlyContinue
                    $CurrentStatus = (Get-Service {service_name}).Status
                    if ($CurrentStatus -eq 'Running' -or $CurrentStatus -eq 'StartPending') {{
                        Write-Output "{success_message}"
                    }} else {{
                        Write-Output "{error_message}"
                    }}
                }}
            }} catch {{
                Write-Output "{error_message}"
            }}
            """
            result = get_winrm_script_result(host_name, command,True).strip()
    except Exception as exception:
        print(exception)
    return result
