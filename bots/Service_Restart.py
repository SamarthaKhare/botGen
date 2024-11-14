
from remote_connection_helper import get_winrm_script_result


def get_state(host_name, service_name):
    """
    Checks the current status of a specified Windows service on a remote host using WinRM. It runs a PowerShell 
    command to determine if the service is valid and, if so, retrieves its status.
    Arguments:
    - host_name (str): The name or IP address of the remote Windows host.
    - service_name (str): The name of the service whose status is to be checked.
    Returns:- str or None: The status of the service (e.g., "Running", "Stopped), or 'Invalid' if the service is not found. Returns None in case of an exception.
    """
    result = None
    try:
        if host_name is not None and service_name is not None:
            command = "if((Get-Service -Name '"+service_name+"' -ErrorAction SilentlyContinue) -eq $null){echo 'Invalid'} else {(Get-Service -Name '"+service_name+"').Status}"
            result = get_winrm_script_result(host_name, command,True).strip()
    except Exception as exception:
        print(exception)
    return result


def update_state(host_name, service_name):
    """
    Attempts to start a specified Windows service on a remote host using WinRM. It uses a PowerShell command 
    to try starting the service multiple times and checks if the service reaches the "Running" status. Returns 
    a success or failure message based on the outcome.
    Arguments:
    - host_name (str): The name or IP address of the remote Windows host.
    - service_name (str): The name of the service to be started.
    Returns:- str or None: "SUCCESS" if the service starts successfully, "FAILURE" if it fails to start, or None in case of an exception.
    """
    result = None
    try:
        if host_name is not None and service_name is not None:
            command = """
            try
                {{
                    $MaxRepeat = 2
                    Start-Service {service_name} -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
                    do
                    {{
                        $Count = (Get-Service {service_name} | ? {{$_.status -eq 'Running'}}).count
                        $MaxRepeat = $MaxRepeat - 1
                        Sleep -Milliseconds 5000
                    }} until ($Count -eq 1 -or $MaxRepeat -eq 0)
                    $CurrentStatus = (Get-Service {service_name}).Status
                    if($CurrentStatus -eq 'Running' -or $CurrentStatus -eq 'StartPending')
                    {{
                        echo {success_message}
                    }}
                    else
                    {{
                        Start-Service {service_name} -WarningAction SilentlyContinue
                        $CurrentStatus = (Get-Service {service_name}).Status
                        if($CurrentStatus -eq 'Running' -or $CurrentStatus -eq 'StartPending')
                        {{
                            echo {success_message}
                        }}
                        else
                        {{
                            echo {error_message}
                        }}
                    }}
                }}
                catch
                {{
                    echo {error_message}
                }}
                """.format(service_name = service_name, success_message = 'SUCCESS', error_message = 'FAILURE')
            result = get_winrm_script_result(host_name, command,True).strip()
    except Exception as exception:
        print(exception)
    return result

