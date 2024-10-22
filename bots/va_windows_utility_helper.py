import os
import winrm
import warnings
from datetime import datetime
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

def winrm_device_status_check(ip_address, document_id):
        """
        Checks the WinRM connection status for a given device by pinging the IP address and verifying WinRM reachability.
        Args:
            ip_address (str): The IP address of the device to check.
            document_id (str): The ID of the document associated with the current transaction.
        Returns:
            dict: A dictionary containing the device status and result:
                - "status" (str): A message indicating the status of the device (e.g., 'Ping Failed', 'WinRM Connection Issue').
                - "result" (bool): A boolean indicating whether the WinRM connection was successful (True/False).
        Raises:
            Exception: Catches and prints any exceptions that occur during the process.
        """
        from remote_connection_helper import is_ping_success, get_winrm_reachable_status
        from zif_workflow_helper import get_workflow_config_value, update_va_transaction_status
        device_details = {}
        device_details["status"] = None
        device_details["result"] = False
        try:
                retry_count = get_workflow_config_value("REMEDIATION_RETRY_COUNT")
                if retry_count is None:
                        retry_count = 3
                ping_status = is_ping_success(ip_address, retry_count)
                print("ping status :",ping_status)
                if ping_status:
                        winrm_status = get_winrm_reachable_status(ip_address, is_ntlm=True)
                        print("winrm status : ",winrm_status)
                        if winrm_status != "Success":
                                print(f"Winrm Failed for {ip_address}")
                                device_details["status"] = f"Winrm Connection/Access Issue for {ip_address}"
                                update_va_transaction_status(document_id, 'Failed', device_details["status"])
                        else:
                                device_details["result"] = True
                else:
                        print(f"Ping Failed for {ip_address}")
                        device_details["status"] = f"Ping Failed for {ip_address}"
                        update_va_transaction_status(document_id, 'Failed', device_details["status"])
        except Exception as exception:
                print(exception)
        return device_details

def va_backup(host_name, file_path, is_ntlm=True):
    """
    Creates a backup of a specified file on a remote machine using WinRM, copying the file with a new name based on the current timestamp.
    Args:
        host_name (str): The hostname or IP address of the remote machine.
        file_path (str): The file path to the file to be backed up.
        is_ntlm (bool): Specifies whether NTLM authentication is used.
    Returns:
        dict: A dictionary with the following keys:
            - "status" (bool): Indicates whether the backup was successful.
            - "note" (str): Additional information, e.g., success or failure message.
    Raises:
        Exception: Catches and prints any exceptions that occur during the process.
    """
    from remote_connection_helper import get_winrm_result
    result = None
    temp_dict = {}
    try:
        if file_path is not None:
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H%M")
            backup_filename = f"{file_name}_backup_{current_datetime}{file_extension}"
            command = f"""
            if(Test-Path -Path "{file_path}")
            {{
                Copy-Item -Path {file_path} -Destination {backup_filename} -Recurse
                if(Test-Path -Path "{backup_filename}"){{
                    echo $true
                }}
            }}
            else
            {{
                echo $false
            }}
            """
            result = get_winrm_result(host_name, command, is_ntlm)
            result = result.strip()
            if result.lower() == "true":
                temp_dict["status"] = True
                temp_dict["note"] = "Backup Completed"
            else:
                temp_dict["status"] = False
                temp_dict["note"] = f"Backup Failed due to invalid file path - {file_path}"
    except Exception as exception:
        print(exception)
    return temp_dict

def start_stop_service(host_name, service_name, action_type):
    """
    Starts or stops a Windows service on a remote machine via WinRM.
    Args:
        host_name (str): The hostname or IP address of the remote machine.
        service_name (str): The name of the service to be started or stopped.
        action_type (str): Specifies the action to perform ('start' or 'stop').
    Returns:
        dict: A dictionary with the following keys:
            - "status" (bool): Indicates whether the service action was successful.
            - "note" (str): Additional information, e.g., success or failure message.
    Raises:
        Exception: Catches and prints any exceptions that occur during the process.
    """
    from remote_connection_helper import get_winrm_result
    from zif_workflow_helper import get_workflow_config_value
    temp_dict = {}
    result = None
    try:
        config_result = get_workflow_config_value("VA_WINDOWS_SERVICES_NAMES")
        if config_result is not None and service_name.lower() in config_result:
            name = config_result[service_name.lower()]
            if action_type == 'start':
                command = f"Restart-Service -Name '*{name}*' -Force -Confirm:$false"
            elif action_type == 'stop':
                command = f"Stop-Service -Name '*{name}*' -Force -Confirm:$false"
            result = get_winrm_result(host_name, command, is_ntlm=True)
            result = result.strip()
            if result is not None :
                temp_dict["status"] = True
                temp_dict["note"] = f"{action_type} services Completed for {service_name}"
            else:
                temp_dict["status"] = False
                temp_dict["note"] = f"{action_type} services Failed for {service_name}"
        else:
            print("config value is None")
    except Exception as exception:
        print(exception)
        temp_dict["status"] = False
        temp_dict["note"] = str(exception)
    return temp_dict


def extract_zip(host_name,source_path, destination_path, is_ntlm=True):
    """
    Extracts a zip file to a specified destination on a remote machine using WinRM.
    Args:
        host_name (str): The hostname or IP address of the remote machine.
        source_path (str): The path to the zip file on the remote machine.
        destination_path (str): The directory where the zip file should be extracted.
        is_ntlm (bool): Specifies whether NTLM authentication is used.Deafults to True
    Returns:
        dict: A dictionary with the following keys:
            - "status" (bool): Indicates whether the extraction was successful.
            - "note" (str): Additional information, e.g., success or failure message.
    Raises:
        Exception: Catches and prints any exceptions that occur during the process.
    """
    from remote_connection_helper import get_winrm_result
    result = None
    temp_dict = {}
    try:
        if all([host_name, source_path, destination_path]):
            command = f"""$zipFile = "{source_path}"
            $destinationDir = "{destination_path}"
            if (Test-Path -Path $zipFile){{
            Expand-Archive -Path $zipFile -DestinationPath $destinationDir -Force
            echo "True"
            }} else {{
            echo "False"
            }}
            """
            result = get_winrm_result(host_name, command, is_ntlm)
            result = result.strip()
            if result.lower() == "true":
                temp_dict["status"] = True
                temp_dict["note"] = "Extracted zip file successfully"
            elif result.lower() == "false":
                temp_dict["status"] = False
                temp_dict["note"] = "Zip file extraction failed"
    except Exception as exception:
        print(exception)
        temp_dict["status"] = False
        temp_dict["note"] = str(exception)
    return temp_dict

def stop_application_service(host_name, service_list):
    """
    Stops multiple Windows services on a remote machine using WinRM.
    Args:
        host_name (str): The hostname or IP address of the remote machine.
        service_list (list): A list of service names to be stopped.
    Returns:
        list: A list of dictionaries, each containing the following keys:
            - "id" (str): The task ID.
            - "name" (str): The name of the service.
            - "status" (str): The result of stopping the service ('SUCCESS' or 'FAILED').
            - "stopDateTime" (datetime): The time when the service was stopped.
    Raises:
        Exception: Catches and prints any exceptions that occur during the process.
    """
    from remote_connection_helper import parse_command
    task_result = {'id': None, 'name': None, 'status': None, 'stopDateTime': None}
    result_list = []
    counter = 1
    
    if all([host_name, service_list]):
        try:
            user_name=os.environ['USER_NAME_WINDOWS']
            password=os.environ['PASSWORD_WINDOWS']
            connection = winrm.Session(host_name, auth=(user_name, password), transport='ntlm')
            
            for service in service_list:
                service_result = None
                command_text = """$ServiceToStop = '{service_name}'
                    $Service = Get-Service -Name $ServiceToStop
                    $ServiceResult = $null
                    $CurrentStatus = '{error_message}'
                    if($Service.Status -eq 'stopped'){{
                        $CurrentStatus = '{success_message}'
                    }}
                    if(($Service.Status -eq 'running') -or ($Service.Status -eq 'paused')) {{
                    try{{
                    $CurrentStatus = Stop-Service $ServiceToStop -WarningAction SilentlyContinue -PassThru | Select-Object -ExpandProperty Status
                    if(![string]::IsNullOrEmpty($CurrentStatus)) {{
                    if(($CurrentStatus -eq 'stopped') -or ($CurrentStatus -eq 'stoppending')) {{
                    $CurrentStatus = '{success_message}'
                    }}  else{{
                    $CurrentStatus = '{error_message}'        
                    }}
                    }}
                    $ServiceResult = -join($ServiceToStop, '||', $CurrentStatus)    
                    }} catch {{
                    $CurrentStatus = '{error_message}'
                    $ServiceResult = -join($ServiceToStop, '||', $CurrentStatus)    
                    }}
                    }} else {{
                    $ServiceResult = -join($ServiceToStop, '||', $CurrentStatus)
                    }}
                    echo $ServiceResult
                """.format(service_name = service, success_message = 'SUCCESS', error_message = 'FAILED')
                print(command_text)
                command = parse_command(command_text)
                command_result = connection.run_cmd(command)
                print(command_result)
                if command_result is not None:
                    service_result = command_result.std_out.decode().strip()
                    
                if service_result is not None:
                    for temp_result in service_result.split('\r\n'):
                        task_result['id'] = str(counter)
                        task_result['name'] = str(temp_result).split('||')[0]
                        task_result['status'] = str(temp_result).split('||')[1]
                        task_result['stopDateTime'] = datetime.utcnow()
                        result_list.append(task_result)
                        counter = counter + 1
                        task_result = {}
        except Exception as exception:
            print(exception)
            
    return result_list

def start_application_service(host_name, service_list):
    """
    Starts multiple Windows services on a remote machine using WinRM.
    Args:
        host_name (str): The hostname or IP address of the remote machine.
        service_list (list): A list of service names to be started.
    Returns:
        list: A list of dictionaries, each containing the following keys:
            - "id" (str): The task ID.
            - "name" (str): The name of the service.
            - "status" (str): The result of starting the service ('SUCCESS' or 'FAILED').
            - "startDateTime" (datetime): The time when the service was started.
    Raises:
        Exception: Catches and prints any exceptions that occur during the process.
    """
    from remote_connection_helper import parse_command
    task_result = {'id': None, 'name': None, 'status': None, 'startDateTime': None}
    result_list = []
    counter = 1
    if all([host_name, service_list]):
        try:
            user_name=os.environ['USER_NAME_WINDOWS']
            password=os.environ['PASSWORD_WINDOWS']
            connection = winrm.Session(host_name, auth=(user_name, password), transport='ntlm')
            for service in service_list:
                service_result = None
                command_text = """$ServiceToStart = '{service_name}'
                    $Service = Get-Service -Name $ServiceToStart -ErrorAction SilentlyContinue -WarningAction SilentlyContinue
                    $ServiceResult = $null
                    $action = $null
                    $CurrentStatus = '{error_message}'
                    if($Service.Status -eq 'running') {{
                        $action = 'restart'
                    }} if(($Service.Status -eq 'stopped') -or ($Service.Status -eq 'paused')) {{
                        $action = 'start'
                    }} try {{ 
                    if($action -eq 'restart') {{
                    $CurrentStatus = Restart-Service $ServiceToStart -ErrorAction SilentlyContinue -WarningAction SilentlyContinue -PassThru | Select-Object -ExpandProperty Status
                    }} else {{
                    $CurrentStatus = Start-Service $ServiceToStart -ErrorAction SilentlyContinue -WarningAction SilentlyContinue -PassThru | Select-Object -ExpandProperty Status    
                    }} if(![string]::IsNullOrEmpty($CurrentStatus)) {{
                    if(($CurrentStatus -eq 'running') -or ($CurrentStatus -eq 'startpending')) {{
                    $CurrentStatus = '{success_message}'
                    }} else {{
                    $CurrentStatus = '{error_message}'
                    }}
                    }}
                    $ServiceResult = -join($ServiceToStart, '||', $CurrentStatus)    
                    }} catch {{
                    $CurrentStatus = '{error_message}'
                    $ServiceResult = -join($ServiceToStart, '||', $CurrentStatus)
                    }} 
                    echo $ServiceResult
                """.format(service_name = service, success_message = 'SUCCESS', error_message = 'FAILED')
                print(command_text)
                command = parse_command(command_text)
                command_result = connection.run_cmd(command)
                print(command_result)
                if command_result is not None:
                    service_result = command_result.std_out.decode().strip()
                if service_result is not None:
                    for temp_result in service_result.split('\r\n'):
                        task_result['id'] = str(counter)
                        task_result['name'] = str(temp_result).split('||')[0]
                        task_result['status'] = str(temp_result).split('||')[1]
                        task_result['startDateTime'] = datetime.utcnow()
                        result_list.append(task_result)
                        counter = counter + 1
                        task_result = {}
        except Exception as exception:
            print(exception)
    #check it properly how its done 
    return result_list

def check_service_status(services):
    """
    Checks the status of multiple services.
    Args:
        services (list): A list of dictionaries, where each dictionary contains a service's name and status. 
        Example: [{'name': 'service1', 'status': 'SUCCESS'}, ...]
    Returns:bool: Returns True if all services have a status of 'SUCCESS', otherwise returns False.
    """
    result = True
    for service in services:
        if service["status"]!="SUCCESS":
            return False
    return result


def copy_file_folder(host,source,destination,is_ntlm=True):
    """
    Copies a file or folder from a source to a destination on a remote Windows host.
    Args:
        host (str): The target host's address.
        source (str): The source file/folder path to copy.
        destination (str): The destination path where the file/folder will be copied.
        is_ntlm (bool, optional): Indicates if NTLM authentication is being used. Default is True.
    Returns:None: Outputs the result of the copy operation via print.
    """
    from remote_connection_helper import get_winrm_result
    try:
        if all([host,source,destination]):
            command = '''
            Copy-Item -Path "{sourcePath}" -Destination "{destinationPath}" -Recurse
            '''.format(sourcePath=source,destinationPath=destination)
            print('cmd',command)
            res = get_winrm_result(host,command,is_ntlm)
            print('r',res)
        else:
            print()
    except Exception as exception:
        print(exception)

def get_program_type(program_name):
    """
    Determines the type of a program by identifying if it is an SQL Server KB or other program.
    Args:program_name (str): The name of the program to check.
    Returns:str: Returns "SQL Server KB" if the program is identified as an SQL Server KB, otherwise returns the original program name.
    """
    import re
    result = None
    try:
        if program_name:
            sql_pattern =  r'\bSQL\s*Server\b.*\(kb\d+\)'
            if re.search(sql_pattern, program_name, re.IGNORECASE):
                print("SQL KB")
                result = "SQL Server KB"
            else:
                result = program_name
    except Exception as exception:
        print(exception)
    return result

def check_program_status(host_name, program_name, version_id=None,is_ntlm=True):
    """
    Checks whether a specific program (optionally a specific version) is installed on a remote Windows host.
    Args:
        host_name (str): The target host's address.
        program_name (str): The name of the program to check.
        version_id (str, optional): The version of the program to check. If not provided, checks for any version.
        is_ntlm (bool, optional): Indicates if NTLM authentication is being used. Default is True.
    Returns:dict: A dictionary with keys 'status' (True if installed, False otherwise) and 'note' (details about the installation).
    """
    from remote_connection_helper import get_winrm_result
    try:
        temp_dict = {'status':None, 'note':None}
        if all([host_name, program_name]):
            if version_id is None:
                version_id = 'null'
            command = f"""$desiredVersion = '{version_id}'
            $uninstalled = $false
            if ($desiredVersion -ne $null -and $desiredVersion -ne 'null') {{
            $msiPackages = Get-WmiObject -Class Win32_Product | Where-Object {{ $_.Name -like '{program_name}' -and $_.Version -like '{version_id}' }} -ErrorAction SilentlyContinue
            $exePackages = Get-Package 3>$null -Name '{program_name}' -RequiredVersion '{version_id}' -ErrorAction SilentlyContinue
            }} else {{
            $msiPackages = Get-WmiObject -Class Win32_Product | Where-Object {{ $_.Name -like '{program_name}' }} -ErrorAction SilentlyContinue
            $exePackages = Get-Package 3>$null -Name '{program_name}' -ErrorAction SilentlyContinue
            }}
            $installed = $false
            if ($msiPackages -ne $null -and $exePackages.Count -eq 1) {{
                $result = 'True||'+$msiPackages.Name+','+$msiPackages.Version
                $installed = $true
                $exePackages = $null
            }}
            if ($exePackages -ne $null -and $exePackages.Count -eq 1) {{
                $result = 'True||'+$exePackages.Name+','+$exePackages.Version
                $installed = $true
            }}
            if ($installed) {{
                echo $result
            }} else {{
                echo 'False||{program_name} is not installed.'
            }}"""
            print(command)
            result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
            result = result.strip()
            result = result.split("||")
            if result[0].lower() == "true":
                software_name, software_version = result[1].split(",")
                temp_dict['status'] = True
                if version_id is not None and version_id!='null':
                    if software_version == version_id: 
                        temp_dict['note'] = f'{software_name} with v{version_id} is already present'
                    else:
                        temp_dict['status'] = False
                        temp_dict['note'] = f'{software_name} with v{version_id} is not present'
                else:
                    temp_dict['note'] = f'{software_name} with v{software_version} is already present'
            elif result[0].lower() == "false":
                temp_dict["status"] = False
                temp_dict["note"] = result[1]
    except Exception as exception:
        print(exception)
        temp_dict['note'] = str(exception)
    return temp_dict


def backup_multiple_files(host_name : str, source_files : list, folder_prefix:str,is_ntlm =True, is_rollback = False):
    """
    Backs up multiple files from a source to a destination folder on a remote Windows host.
    Args:
        host_name (str): The target host's address.
        source_files (list): A list of file paths to be backed up.
        folder_prefix (str): Prefix to use when naming the backup folder.
        is_ntlm (bool, optional): Indicates if NTLM authentication is being used. Default is True.
        is_rollback (bool, optional): If True, backs up to a rollback path instead of the default backup path.
    Returns:bool: Returns True if the backup was successful, otherwise False.
    """
    from remote_connection_helper import get_winrm_result
    from zif_workflow_helper import get_workflow_config_value
    result = False
    try:
        destination_folder = get_workflow_config_value("VA_WINDOWS_BACKUP_PATH")
        rollback_path = get_workflow_config_value("VA_WINDOWS_ROLLBACK_PATH")
        if all([host_name, source_files,destination_folder, rollback_path]):
            print(source_files)
            files_string = '|'.join(source_files)
            datetime_str = datetime.now().strftime("%d%b%Y%H%M")
            backup_folder = folder_prefix + '_' + datetime_str
            if is_rollback:
                destination_folder = rollback_path
            print("DTS",datetime_str)
            script = '''$files_arr = '{files_string}'.Split('|')
            $file_result = $false
            $dir = '{destinationPath}\\{bck_folder}'
            if ( -not (Test-Path -Path $dir)) {{
                New-Item -Path '{destinationPath}' -Name '{bck_folder}' -ItemType 'directory' | Out-Null
            }}
            $previous_count = (Get-ChildItem -Path $dir -File | Measure-Object).Count
            Copy-Item -Path $files_arr -Destination $dir -Recurse
            $current_count = (Get-ChildItem -Path $dir -File | Measure-Object).Count
            $count = $current_count - $previous_count
            if ($count -eq {fileCount} ) {{
                $file_result = $true
            }}
            echo $file_result
            '''.format(files_string=files_string,destinationPath=destination_folder,
                       fileCount=len(source_files),bck_folder=backup_folder)
            result = get_winrm_result(host_name,script,is_ntlm)
            print('result',result)
            if result.strip().lower() == 'true':
                result = True
            else:
                result = False
        else:
            print('1 or more is none')
    except Exception as exception:
        print(exception)
    return result

def get_failed_services_list(service_status : list) -> list:
    """
    Retrieves a list of failed services from a given list of service statuses.
    Args:
        service_status (list): A list of dictionaries, where each dictionary contains a service's name and status. 
        Example: [{'name': 'service1', 'status': 'SUCCESS'}, ...]
    Returns:list: A list of service names that have a status other than 'SUCCESS'.
    """
    return [service['name'] for service in service_status if service['status'] != 'SUCCESS']

def check_patch_status(host_name, patch_name, is_ntlm=True):
    """
    Function to check if a specific patch is installed on a remote Windows device.
    Parameters:
    host_name (str): The hostname or IP address of the target device.
    patch_name (str): The name of the patch to check.
    is_ntlm (bool, optional): Flag indicating whether NTLM authentication should be used. Default is True.
    Returns:
    dict: A dictionary with two keys:
          'status' (bool): True if the patch is present, otherwise False.
          'note' (str): A message indicating whether the patch is present or if there was an error.
    """
    from remote_connection_helper import get_winrm_result
    result = {'status': False, 'note': 'Patch is not present'}
    try:
        patch_name_filter = f"*{patch_name}*"
        command = f'''$patchName = '{patch_name_filter}'
        $exePackages = Get-Package 3>$null | Where-Object {{ $_.Name -like $patchName }}
        if ($exePackages.Count -gt 0) {{
            'Package is present'
        }} else {{
            'Package is not present'
        }}
        '''
        print("command:",command)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            program_result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if "Package is present" in program_result:
            result['status'] = True
            result['note'] = f'SQL Patch {patch_name} is present'
        else:
            result['note'] = f'SQL Patch {patch_name} is not present'
    except Exception as exception:
        print(exception)
        result['note']= f"An error occurred: {str(exception)}"
    return result


def restart_service(host_name, service_name, is_ntlm=True):
    """
    Function to restart a Windows service on a remote device.
    Parameters:
    host_name (str): The hostname or IP address of the target device.
    service_name (str): The name of the service to restart.
    is_ntlm (bool, optional): Flag indicating whether NTLM authentication should be used. Default is True.
    Returns:
    dict: A dictionary with two keys:
          'status' (bool): True if the service was successfully restarted, otherwise False.
          'note' (str): A message indicating whether the service was restarted or not.
    """
    from remote_connection_helper import get_winrm_result
    result = {'status': False, 'note': ''}
    exception_message = ''
    try:
        command = f"""
        if (Get-Service {service_name} -ErrorAction SilentlyContinue) {{
            Restart-Service {service_name} -Force
            echo $true
        }} else {{
            echo $false
        }}
        """
        command_result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if command_result.strip().lower() == "true":
            result['status'] = True
            result['note'] = f"Restarted {service_name} service"
        else:
            result['status'] = False
            result['note'] = f"{service_name} service not found"
    except Exception as exception:
        print(exception)
        exception_message = str(exception)
    if exception_message:
        result['exception'] = exception_message
    return result

def kill_process(host_name, process_name, is_ntlm=True):

    """
    Function to terminate a process by its name on a remote Windows device.
    Parameters:
    host_name (str): The hostname or IP address of the target device.
    process_name (str): The name of the process to terminate.
    is_ntlm (bool, optional): Flag indicating whether NTLM authentication should be used. Default is True.
    Returns:
    str: The result of the command execution on the remote device, indicating whether the process was successfully terminated.
    """
    from remote_connection_helper import get_winrm_result
    command = None
    result = None
    try:
        if process_name is not None :
            command = "Get-Process -Name {Program} -ErrorAction SilentlyContinue | Stop-Process -Force".format(Program = process_name)
            if command is not None:
                result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
    except Exception as exception:
        print(exception)
    return result


def stop_process_by_ids(host_name,process_details,is_ntlm=True):
    
    """
    Function to stop processes on a remote Windows device by their process IDs.
    Parameters:
    host_name (str): The hostname or IP address of the target device.
    process_details (list of dict): List of dictionaries containing process details such as process ID.
    is_ntlm (bool, optional): Flag indicating whether NTLM authentication should be used. Default is True.
    Returns: None
    """
    from remote_connection_helper import get_winrm_result
    result = None
    try:
        if all([host_name, process_details]):
            process_ids = '|'.join([str(process['Id']) for process in process_details])
            command_text = f"""$process_arr = '{process_ids}'.Split('|')
                            Stop-Process -Id $process_arr -Force -ErrorAction SilentlyContinue
                            """
            script_result = get_winrm_result(host_name,command_text,is_ntlm)
            if script_result:
                print("process stop triggered")
    except Exception as exception:
        print(exception)

def stop_process_services(host_name, process_ids ,is_ntlm=True):
    """
    Function to stop processes and their associated services on a remote Windows device.
    Parameters:host_name (str): The hostname or IP address of the target device.
    process_ids (list): List of process IDs to stop.
    is_ntlm (bool, optional): Flag indicating whether NTLM authentication should be used. Default is True.
    Returns:list: A list of unique service names associated with the stopped processes.
    """
    import json
    from remote_connection_helper import get_winrm_result
    result = None
    try:
        if all([host_name, process_ids]):
            print()
            process_string = '|'.join(process_ids)
            print('ps',process_string)
            command_text = f"""$process_arr = '{process_string}'.Split('|')
                $serviceNames =  @()
                foreach($id in $process_arr){{
                  $err = ''
                  try {{
                  $serviceNames += (Get-WmiObject Win32_Service | Where-Object {{ $_.ProcessId -eq $id }}).Name
                  $parentId = (Get-CimInstance Win32_Process  | Where-Object {{ $_.ProcessId -eq $id }}).ParentProcessId
                  if(-not [string]::IsNullOrEmpty($parentId)){{
                     $serviceNames += (Get-WmiObject Win32_Service | Where-Object {{ $_.ProcessId -eq $parentId }}).Name
                  }} 
                    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
                 }} catch {{
                    $err = ''
                 }}}}
                $serviceNames = $serviceNames | Select-Object -Unique
                $result = ($serviceNames -join '|')
                echo $result
                """
            print(command_text)
            script_result = get_winrm_result(host_name, command_text, is_ntlm)
            print(script_result)
            print(type(script_result))
            if script_result is not None:
                output_lines = script_result.strip()
                print("ol")
                print(output_lines)
                result = output_lines.strip().split('|')
                print('res',type(result))
                print(result)            
    except Exception as exception:
        print(exception)
    return result

