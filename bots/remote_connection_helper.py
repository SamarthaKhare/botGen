import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../.env"
load_dotenv(dotenv_path=dotenv_path)

def parse_command(command):
    """
    Parses a command string to be compatible with PowerShell execution.

    Args:
        command: The command string to parse.

    Returns:
        The parsed command string.
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
  Checks if a host is reachable via ping.

  Args:
    host: The host name or IP address to ping.
    count: The number of ping packets to send.

  Returns:
    True if the ping is successful, False otherwise.
  """
  # Determine the ping command based on the operating system
  

  import subprocess
  import platform
  ping_command = ['ping', '-c', str(count), host]
  if platform.system() == 'Windows':
    ping_command = ['ping', '-n', str(count), host]

  try:
    # Execute the ping command
    response = subprocess.run(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the ping was successful (return code 0)
    if response.returncode == 0:
      return True
    else:
      return False

  except Exception as exception:
    print(f"Error during ping: {exception}")
    return False

def get_winrm_session(host_name,is_ntlm=True):
    """
    Establishes a WinRM session to a remote host.

    Args:
        host_name: The host name or IP address of the remote machine.
        is_ntlm: Whether to use NTLM authentication (default: False).

    Returns:
        A winrm.Session object if the session is successfully established, None otherwise.
    """
    import winrm
    username=os.environ['USER_NAME_WINDOWS']
    password=os.environ['PASSWORD_WINDOWS']
    session = None
    try:
        if is_ntlm:
            session = winrm.Session(host_name, auth=(username, password), transport='ntlm')
        else:
            session = winrm.Session(host_name, auth=(username, password))
    except Exception as exception:
        print(exception)
    return session


def get_winrm_result(host, command,is_ntlm=True):
    """
    Executes a command on a remote host via WinRM and returns the output.

    Args:
        host: The host name or IP address of the remote machine.
        command: The command to execute.
        is_ntlm: Whether to use NTLM authentication.

    Returns:
        The output of the command as a string or None if an error occurs .
    """
    result = None
    try:
        # Assuming connection_id is a dictionary with 'username' and 'password'
        session=get_winrm_session(host,is_ntlm)
        if session is not None:
                # Use the parse_command function to prepare the command
            command = parse_command(command)
            if command is not None:
                output = session.run_cmd(command)
                print("err", output.std_err.decode())
                print("out", output)
                print('od', output.std_out.decode())
                if output.status_code == 0:
                    result = output.std_out.decode().strip()
                    if result=="":
                       result+="Success"
                       print(f"{result} but no std output")
                else:
                    print("output is none")
            else:
                print("Command parsing failed.")
        else:
            print("session is none")


    except Exception as exception:
        print(exception)

    return result


def get_winrm_reachable_status(host_name,is_ntlm=True):
    """
    Checks if a host is reachable via WinRM.

    Args:
        host_name: The host name or IP address of the remote machine.
        is_ntlm: Whether to use NTLM authentication.

    Returns:
        "Success" if the host is reachable, "Failure" otherwise.
    """
    status="Failure"
    try:
        command_text = "powershell -command 'Test-WSMan'"
        session = get_winrm_session(host_name,is_ntlm=is_ntlm)
        if session is not None:
            result = session.run_cmd(command_text)
            if result is not None and result.status_code == 0:
                status = "Success"
    except Exception as exception:
        print(exception)
    return status

def get_ssh_client(host_name,db_connection=None):
  """
  Establishes an SSH connection to a remote host.

  Args:
    host_name: The host name or IP address of the remote machine.
    db_connection: A dictionary containing 'username' and 'password' for authentication (optional). 
  Returns:
    A paramiko.SSHClient object if the connection is successfully established, None otherwise.
  """
  print("in")
  import paramiko
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  username=os.environ['USER_NAME_LINUX']
  password=os.environ['PASSWORD_LINUX']
  try:
    # Prioritize username and password if provided
    if username and password:
      connection_params = {'username': username, 'password': password}
    elif db_connection:
      connection_params = db_connection
    else:
      # Default credentials (consider a more secure approach)
      connection_params = {'username': 'SSHSERVICEACCOUNT', 'password': 'your_password'}
    print(connection_params)
    client.connect(
      hostname=host_name,
      username=connection_params['username'],
      password=connection_params['password']
    )

    # Check if the transport is active
    if client.get_transport() and client.get_transport().is_active():
      return client

  except (paramiko.AuthenticationException, paramiko.SSHException) as e:
    print(f"Error establishing SSH connection: {e}")

  except KeyError as e:
    print(f"Missing required key in connection parameters: {e}")
    
  return None


def get_ssh_script_result(host_name, command_text,sudo_access=True,db_connection=None):
    """
    Executes a script on a remote host via SSH and returns the output.

    Args:
        host_name: The host name or IP address of the remote machine.
        command_text: The command or script to execute.
        sudo_access: Whether to execute the command with sudo privileges.
        db_connection: username,password for connection (optional)

    Returns:
        The output of the script as a string, or None if an error occurs.
    """
    password=""
    try:
        ssh_result = []
        script_result = None
        result = ''
        client = get_ssh_client(host_name,db_connection)
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
            print("ssh_result : ", ssh_result)
            client.close()
            if result != "Success" and stderr is not None:
                print("ERROR : ", str(stderr))
            if len(ssh_result) >= 1:
                script_result = ssh_result[-1].strip().replace('\r', '').replace('\n', '')
    except Exception as exception:
        print(exception)
    return script_result

def get_ssh_reachable_status(host_name,db_connection=None):
    """
    Checks if a host is reachable via SSH.

    Args:
        host_name: The host name or IP address of the remote machine.
        db_connection: The name of the database connection to use for authentication (optional).

    Returns:
        "SUCCESS" if the host is reachable, "Failure" otherwise.
    """
    status = "Failure"
    try:
        client = get_ssh_client(host_name,db_connection)
        if client is not None:
            stdin, stdout, stderr = client.exec_command("pwd")	
            for line in stdout:
                status = "SUCCESS"
    except Exception as exception:
        print(exception)
    return status