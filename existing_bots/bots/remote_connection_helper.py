import winrm
import subprocess
from ast import literal_eval
import logging
import os
import sys
import paramiko
import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)


def is_ping_success(host, count):
    """
    """
    import subprocess
    import platform
    ping_command = ['ping', '-c', str(count), host]  # Default ping command for Unix-like systems
    if platform.system() == 'Windows':
        ping_command = ['ping', '-n', str(count), host]  # Use Windows-specific ping flag

    try:
        response = subprocess.run(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.returncode == 0  # Check the response code to determine success
    except Exception as exception:
        print(f"Error during ping: {exception}")
        return False



def get_winrm_connection(host_name, is_ntlm=True):
    """
    """
    connection = None
    try:
        username = os.environ['USER_NAME_WINDOWS']
        password = os.environ['PASSWORD_WINDOWS']
        if username is not None and password is not None:
            account_name =username
            account_key = password
            if is_ntlm == True:
                connection = winrm.Session(
                    host_name, auth=(account_name, account_key), transport='ntlm')
            else:
                connection = winrm.Session(
                    host_name, auth=(account_name, account_key))
    except Exception as exception:
        print(exception)
    return connection


def get_winrm_script_result(host_name, command_text, is_ntlm=True):
    """
    Executes a PowerShell command on a remote Windows machine via WinRM and returns the output.
    This function sends a command to a remote Windows host over a WinRM session and captures its output. It uses
    PowerShell to execute the command and handles command parsing to ensure proper execution.
    Args:
        host (str): The IP address or host name of the remote Windows machine.
        command (str): The command to execute on the remote machine.
        is_ntlm (bool): If True, NTLM authentication is used for the WinRM session.
    Returns:
        str: The command's output if successfull, else None if an error occurs.
    """
    result = None
    connection = None

    try:
        if is_ntlm == True:
            connection = get_winrm_connection(host_name, True)
        else:
            connection = get_winrm_connection(host_name)
        if connection is not None:
            response = connection.run_ps(command_text)
            if response is not None:
                result = response.std_out.decode()
    except Exception as exception:
        print(exception)
    return result


def get_winrm_connection_status(host_name, is_ntlm=True):
    """
    Checks if a Windows host is reachable via WinRM by running the 'Test-WSMan' command.
    This function tests whether the remote machine can be accessed via WinRM by executing the 'Test-WSMan' PowerShell 
    command. If successful, the machine is considered reachable.
    Args:
        host_name (str): The IP address or host name of the remote Windows machine.
        is_ntlm (bool): If True, NTLM authentication is used for the WinRM session.
    Returns:
        str: "Success" if the host is reachable via WinRM, otherwise "Failure".
    """
    status = "Failure"
    try:
        command = 'Test-WSMan'
        if is_ntlm == True:
            result = get_winrm_script_result(host_name, command, True)
        else:
            result = get_winrm_script_result(host_name, command)
        if result is not None:
            status = "Success"
    except Exception as exception:
        print(exception)
    return status




def get_ssh_client(host_name, db_connection=None):
    """
    Establishes an SSH connection to a remote Linux host using Paramiko.
    This function initiates an SSH connection to a remote Linux machine. It can authenticate using environment 
    variables or provided credentials. It ensures that the connection is securely established with the server.
    Args:
        host_name (str): The IP address or host name of the remote Linux machine.
        db_connection (dict): Optional dictionary containing 'username' and 'password' for authentication.
    Returns:
        paramiko.SSHClient: A Paramiko SSH client object if the connection is successfully established, otherwise None.
    """
    import paramiko
    import os
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    username = os.environ['USER_NAME_LINUX']
    password = os.environ['PASSWORD_LINUX']
    try:
        if username and password:
            connection_params = {'username': username, 'password': password}
        elif db_connection:
            connection_params = db_connection
        else:
            connection_params = {'username': 'SSHSERVICEACCOUNT', 'password': 'your_password'}
        client.connect(hostname=host_name, username=connection_params['username'], password=connection_params['password'])
        if client.get_transport() and client.get_transport().is_active():
            return client
    except (paramiko.AuthenticationException, paramiko.SSHException) as e:
        print(f"Error establishing SSH connection: {e}")
    except KeyError as e:
        print(f"Missing required key in connection parameters: {e}")
    return None

def get_ssh_script_result(host_name, command_text, sudo_access=True, db_connection=None):
    """
    Executes a script or command on a remote Linux host via SSH and returns the result.
    This function runs a command or script on the remote Linux machine through an SSH session, with optional 
    sudo privileges. It captures and returns the output of the script.
    Args:
        host_name (str): The IP address or host name of the remote Linux machine.
        command_text (str): The command or script to execute.
        sudo_access (bool): Whether to execute the command with sudo privileges (default: True).
        db_connection (dict): Optional dictionary for authentication credentials.
    Returns:
        str: The output of the executed script or command, or None if an error occurs.
    """
    password = os.environ['PASSWORD_LINUX']
    try:
        ssh_result = []
        script_result = None
        result = ''
        client = get_ssh_client(host_name, db_connection)
        if client is not None:
            if sudo_access:
                command_text = "sudo %s" % command_text
            stdin, stdout, stderr = client.exec_command(command_text, get_pty=True)
            if sudo_access:
                stdin.write(password + "\n")
                stdin.flush()
            for std_index in stdout:
                output = std_index.strip().replace('\r', '').replace('\n', '')
                if output != password and not output.startswith('***'):
                    ssh_result.append(output)
                result = "Success"
            client.close()
            if result != "Success" and stderr is not None:
                print("ERROR: ", str(stderr))
            if len(ssh_result) >= 1:
                ssh_result[-1].strip().replace('\r', '').replace('\n', '')
                return ssh_result
        return script_result
    except Exception as exception:
        print(f"Error executing SSH command: {exception}")
        return None
        
def get_ssh_reachable_status(host_name, db_connection=None):
    """
    Checks if a Linux host is reachable via SSH by attempting to execute a simple 'pwd' command on the remote machine.
    Args:
        host_name (str): The host name or IP address of the remote Linux machine.
        db_connection (dict, optional): A dictionary containing 'username' and 'password' for SSH authentication.If not provided, the function attempts to use default credentials stored in environment variables.
    Returns:
        str: 
            - "Success" if the SSH connection is established and the 'pwd' command is executed successfully.
            - "Failure" if the SSH connection could not be established or the command execution fails.
    """
    status = "Failure"
    try:
        # Establish SSH connection
        client = get_ssh_client(host_name, db_connection)
        if client is not None:
            # Execute a simple command (e.g., 'pwd') to verify connectivity
            stdin, stdout, stderr = client.exec_command("pwd")
            # If stdout has output, the connection was successful
            for line in stdout:
                status = "Success"
    except Exception as exception:
        # Print any errors encountered during the process
        print(exception)
    return status
