
from remote_connection_helper import get_winrm_script_result

def get_service_state(device_config):
    """
    For ServiceRestartRemediation and PingResponseRemediation it check the current state of a specified Windows service on a remote host using WinRM. 
    Arguments- device_config (dict): A dictionary containing the device details like 'sys_id', 'device_name', and 'service_name'.
    Returns:- str or None: The state of the service (e.g., "Running", "Stopped), or 'Invalid' if the service is not found. Returns None in case of an exception.
    """
    result = None
    try:
        host_name=device_config['device_name']
        service_name=device_config['service_name']
        if host_name is not None and service_name is not None:
            command = "if((Get-Service -Name '"+service_name+"' -ErrorAction SilentlyContinue) -eq $null){echo 'Invalid'} else {(Get-Service -Name '"+service_name+"').Status}"
            result = get_winrm_script_result(host_name, command,True).strip()
    except Exception as exception:
        print(exception)
    return result


def update_service_state(device_config):
    """
    For ServiceRestartRemediation and PingResponseRemediation it attempts update the service state by starting thw specified Windows service on a remote host using WinRM. 
    It try starting the service multiple times and checks if the service reaches the "Running" status. 
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
