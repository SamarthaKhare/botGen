import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
 
def get_windows_server_uptime(host_name):
    """
    Retrieves the uptime of a Windows server by calculating the time since its last boot.
    Parameters- host_name (str): The hostname or IP address of the Windows server.
    Returns:
    str: A string representing the uptime in the format "hours:minutes:seconds".
         If an error occurs, the error message is returned as a string.
    Raises:
    Exception: If an error occurs during the WinRM execution or result processing.
    """
    from remote_connection_helper import get_winrm_result
    result = None
    try:
        command_text = """try{{
                $OS = Get-WmiObject Win32_operatingsystem
                if($OS -ne $null -and $OS.LastBootUpTime -ne $null){{
                    $UpTime = (Get-Date) - ($OS.ConvertToDateTime($OS.LastBootUpTime))
                    $Result = $UpTime.Hours.ToString() + ':' + $UpTime.Minutes.ToString() + ':' + $UpTime.Seconds.ToString()
                    echo $Result
                }} else {{
                    echo {error_message}
                }}
            }} catch {{
                echo {error_message} }} """.format(error_message = "ERROR")
        status = get_winrm_result(host_name, command_text, is_ntlm=True)
        if status is not None:
            result = status.strip()    
    except Exception as exception:
        print(exception)
        result = str(exception)
    return result

def get_linux_server_uptime(host_name, db_connection=None):
    """
    Retrieves the uptime of a Linux server by executing the 'uptime' command.
    Parameters:
    - host_name (str): The hostname or IP address of the Linux server.
    - db_connection (optional): A database connection object, if required for SSH client (default is None).
    Returns:
    str: A string representing the uptime in the format of the number of days the server has been up.If an error occurs, None is returned.
    Raises:
    Exception: If an error occurs during the SSH command execution or client connection.
    """
    from remote_connection_helper import get_ssh_client
    result = None
    try:
        client = get_ssh_client(host_name)
        if client is not None:
            stdin, stdout, stderr = client.exec_command('uptime')
            if stdout is not None:
                uptime = stdout.read().decode().strip()
                uptime = uptime.split('up ')[-1].split(',')[0].strip()
                result = ''.join(filter(str.isdigit, uptime))
    except Exception as exception:
        print(exception)
    finally:
        if client is not None:
            client.close()
    return result

def windows_server_reboot(host_name, is_ntlm=True):
    """
    Reboots a Windows server using PowerShell command.
    Parameters:
    - host_name (str): The hostname or IP address of the Windows server.
    - is_ntlm (bool, optional): Determines whether NTLM authentication is used for the remote connection (default is True).
    Returns:
    bool: True if the reboot command was successfully executed, False otherwise.
    Raises:
    Exception: If an error occurs during the WinRM session or command execution.
    """
    from remote_connection_helper import get_winrm_session
    result = False
    try:
        command = 'powershell -command "Restart-Computer -Force"'
        session = get_winrm_session(host_name, is_ntlm=is_ntlm)
        response = session.run_cmd(command)
        if response is not None:
            response_code = response.status_code
            if response_code == 0:
                result = True
    except Exception as exception:
        print(exception)
    return result

def linux_server_reboot(host_name, os_name, db_connection=None):
    """
    Retrieves the uptime of a Linux server by executing the 'uptime' command.
    Parameters:
    - host_name (str): The hostname or IP address of the Linux server.
    - db_connection (optional): A database connection object, if required for SSH client (default is None).
    Returns:
    str: A string representing the uptime in the format of the number of days the server has been up.If an error occurs, None is returned.
    Raises:
    Exception: If an error occurs during the SSH command execution or client connection.
    """
    from remote_connection_helper import get_ssh_client
    from zif_workflow_helper import get_workflow_config_value
    command = None
    result = None
    status = False
    try:
        result = get_workflow_config_value("VA_REBOOT_CONFIG")
        if result is not None and os_name.lower() in result:
            command = result[os_name.lower()]
            client = get_ssh_client(host_name, db_connection=db_connection)
            if all([client, command]):
                #print("cmd  : ",command)
                stdin, stdout, stderr = client.exec_command(command, get_pty=True)
                status = True
                script_result = []
                password = os.environ['PASSWORD_LINUX']
                if password is not None:
                        stdin.write(password + "\n")
                        stdin.flush()
                for std_index in stdout:
                    script_result.append(std_index)
    except Exception as exception:
        print(exception)
    finally:
        if client is not None:
            client.close()
    return status
