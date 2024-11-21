import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

def parse_command(command):
    """
    Parses a given command string to make it compatible with PowerShell execution by handling common formatting issues.
    This function adjusts the command string to be safely executed in a PowerShell session. It removes extra spaces, 
    replaces line breaks and tabs with semicolons, and ensures proper handling of curly braces to avoid errors in 
    PowerShell's syntax.
    Args:
        command (str): The command string to be parsed. This is typically a Windows command to be executed remotely.   
    Returns:
        str: The parsed command string, formatted for PowerShell execution, enclosed in a PowerShell command wrapper.
             Returns None if the input command is None.
    """
    import re
    if command is not None:
        command = re.sub(' +', ' ', command)  # Remove extra spaces
        command = command.replace('\r', ';').replace('\n', ';').replace('\t', '')  # Replace line breaks and tabs with semicolons
        command = command.replace('{;', '{').replace(';}', '}')  # Fix potential issues with curly braces
        return f'powershell -command "{command}"'
    return None


def is_ping_success(host, count):
    """
    Sends ping requests to a specified host to check its network connectivity.
    The function sends a specified number of ping packets to the host and evaluates the response to determine if the 
    host is reachable. It adjusts the ping command for Windows and Unix-like systems and captures the success or 
    failure of the ping.
    Args:
        host (str): The host name or IP address to ping.
        count (int): The number of ping packets to send.
    Returns:
        bool: True if the ping was successful (the host is reachable), False if the ping failed or an error occurred.
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


def get_winrm_session(host_name, is_ntlm=True):
    """
    Establishes a WinRM (Windows Remote Management) session to a remote Windows host.
    This function initiates a session with the remote Windows host using the WinRM protocol, with the option to use 
    NTLM (Windows integrated) authentication or basic authentication.
    Args:
        host_name (str): The IP address or host name of the remote Windows machine.
        is_ntlm (bool): If True, NTLM authentication is used. If False, basic authentication is used.   
    Returns:
        winrm.Session: A WinRM session object if successfully connected to the host, otherwise None.
    """
    import winrm
    import os
    username = os.environ['USER_NAME_WINDOWS']
    password = os.environ['PASSWORD_WINDOWS']
    session = None
    try:
        if is_ntlm:
            session = winrm.Session(host_name, auth=(username, password), transport='ntlm')
        else:
            session = winrm.Session(host_name, auth=(username, password))
    except Exception as exception:
        print(f"Error establishing WinRM session: {exception}")
    return session


def get_winrm_script_result(host, command, is_ntlm=True):
    """
    Executes a PowerShell command on a remote Windows machine via WinRM and returns the output.
    This function sends a command to a remote Windows host over a WinRM session and captures its output. It uses
    PowerShell to execute the command and handles command parsing to ensure proper execution.
    Args:
        host (str): The IP address or host name of the remote Windows machine.
        command (str): The command to execute on the remote machine.
        is_ntlm (bool): If True, NTLM authentication is used for the WinRM session.
    Returns:
        str: The command's output if successful, "Success" if command is successful but has no output, else None if an error occurs.
    """
    result = None
    try:
        session = get_winrm_session(host, is_ntlm)
        if session is not None:
            command = parse_command(command)
            if command is not None:
                output = session.run_cmd(command)
                print("err", output.std_err.decode())
                if output.status_code == 0:
                    result = output.std_out.decode().strip()
                    if result == "":
                        result += "Success"
                        print(f"{result} but no std output")
                else:
                    print("output is none")
            else:
                print("Command parsing failed.")
        else:
            print("session is none")
    except Exception as exception:
        print(f"Error executing WinRM command: {exception}")
    return result


def get_winrm_reachable_status(host_name, is_ntlm=True):
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
        command_text = "powershell -command 'Test-WSMan'"
        session = get_winrm_session(host_name, is_ntlm=is_ntlm)
        if session is not None:
            result = session.run_cmd(command_text)
            if result is not None and result.status_code == 0:
                status = "Success"
    except Exception as exception:
        print(f"Error checking WinRM reachability: {exception}")
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
                script_result = ssh_result[-1].strip().replace('\r', '').replace('\n', '')
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

