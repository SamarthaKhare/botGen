import os
import winrm
from datetime import datetime
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

def get_software_status(host_name : str, software_name : str, version_id = None , is_ntlm=True):
    """
    Checks the status of a specified software on a remote Windows host.

    Parameters:
    - host_name (str): The hostname or IP address of the remote Windows device. 
    - software_name (str): The name of the software to check.
    - version_id (str, optional): The specific version of the software to check for. If not provided, only the presence of the software is checked.
    - is_ntlm (bool, optional): Determines whether NTLM authentication is used for the remote connection (default is True).

    Returns:
    dict: A dictionary with the following keys:
        - 'status' (bool): True if the software is installed (and version meets the requirement), False otherwise.
        - 'note' (str): A message indicating the result of the check (software present, version match, etc.).

    Raises:
    Exception: If an error occurs during the WinRM execution or result processing.
    """
    from remote_connection_helper import get_winrm_result
    result = {'status': False, 'note':None}
    try:
        if all([host_name,software_name]):
            result['note'] = f'{software_name} is not present'
            if version_id is None:
                version_id_str = 'null'
            else:
                version_id_str = version_id
            print("vid",version_id)
            command_text = '''$softwareList = Get-Package -Name '{software_name}'  3>$null | Sort-Object -Property Version
                if ($softwareList.Count -eq 0) {{
                    $result = 'False'
                    $highestVersion = $null
                }}else {{
                $highestVersion = $softwareList[-1].Version
                $desiredVersion = '{desired_version}'
                if ($desiredVersion -ne $null -and $desiredVersion -ne 'null') {{
                   if ($highestVersion -ge $desiredVersion ) {{
                     $result = 'True'
                   }} else {{
                     $result = 'False'
                   }}
                 }} else {{
                   $result = 'True'
                 }} 
                }}
                $status = $result + '|' +  $highestVersion
                echo $status
                '''.format(software_name=software_name,desired_version=version_id_str)

            script_result = get_winrm_result(host_name,command_text,is_ntlm)
            print("script_result",script_result)
            if script_result is not None:
                software_status,highest_version = script_result.strip().split('|')
                if software_status.strip().lower() == 'true':
                    result['status'] = True
                    result['note'] = f'{software_name} with version '
                    result['note'] += f'v{highest_version} is already present'
                else:
                    if version_id is not None:
                        result['note'] = f'{software_name} with version greater or '
                        result['note'] += f'equal to v{version_id} is not present'
                    else:
                        result['note'] = f'{software_name} is not present'
    except Exception as exception:
        print(exception)
        result['note'] = str(exception)
    return result




def install_software(host_name : str, source_path : str, software_name = None ,arg_list = None,is_ntlm = True):
    """
    Installs a software package on a remote Windows host.
    Parameters:
    - host_name (str): The hostname or IP address of the remote Windows device.
    - source_path (str): The path to the software installer on the remote device.
    - software_name (str, optional): The name of the software (used for logging purposes).
    - arg_list (str, optional): The list of arguments to be passed to the installer. Defaults to "/S" for silent installation.
    - is_ntlm (bool, optional): Determines whether NTLM authentication is used for the remote connection (default is True).
    Returns:
    dict: A dictionary with the following keys:
        - 'status' (bool): True if the installation script was executed successfully, False otherwise.
        - 'note' (str): A message indicating the success or failure of the installation.
    Raises:
    Exception: If an error occurs during the WinRM execution or result processing.
    """
    from remote_connection_helper import get_winrm_result
    from zif_workflow_helper import get_workflow_config_value
    result  = {'status':False,'note':None}
    script = None
    try:
        if all([host_name, source_path]):
            temp_file_path = get_workflow_config_value("WINDOWS_TEMP_FILE_PATH")
            print(temp_file_path)
            if temp_file_path is not None:            
                installer_name = source_path.split("\\")[-1]
                print('installer',installer_name)
                file_path = temp_file_path + installer_name
                print("file_path",file_path)
                file_name, file_extension = os.path.splitext(file_path)
                print(file_name,file_extension)
                if arg_list is None:
                    print("if arg")
                    arg_list = "/S"
                    print(arg_list)
                else:
                    print('else arg')
                    print(arg_list)
                if file_extension == ".exe":
                    script = "Start-Process -NoNewWindow -FilePath '{filepath}' -ArgumentList '{args}' -Wait".format(filepath=file_path,args=arg_list)
                elif file_extension == ".msi":
                    if software_name is not None:
                        log_path = file_name + "_" + software_name + ".txt"
                    else:
                        current_datetime = datetime.now()
                        date_string = current_datetime.strftime("%Y%m%d%H%M")
                        log_path = file_name + "_" + date_string + ".txt"
                    script = 'Start-Process -NoNewWindow msiexec.exe -ArgumentList "/i {filepath} /L*v {logpath} /quiet" -Wait'.format(filepath=file_path,logpath=log_path)
                print("script")
                print(script)
                if script is not None:
                    command="""if(Test-Path -Path \'{path}\'){{
                            {install_script}
                        }} else {{
                            $False
                        }}""".format(path=file_path, install_script=script)
                    print("command")
                    print(command)
                    script_result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
                    if script_result is not None:
                        result['status'] = True
                        result['note'] = 'Installation script success'
                    else:
                        result['note'] = 'Installation Script Failed'
                else:
                    result['note'] = 'No Script Defined'
    except Exception as exception:
        print(exception)
        result['note'] = str(exception)
    return result

def install_vmware_tools(host_name, installer_path, is_ntlm=True):
    """
    Installs VMware Tools on a remote Windows host.
    Parameters:
    - host_name (str): The hostname or IP address of the remote Windows device.
    - installer_path (str): The full path to the VMware Tools installer on the remote device.
    - is_ntlm (bool, optional): Determines whether NTLM authentication is used for the remote connection (default is True).
    Returns:str: A message indicating the success ("Success") or failure ("Error") of the installation.If an exception occurs, the exception message is returned.
    Raises:
    Exception: If an error occurs during the WinRM execution or result processing.
    """
    from remote_connection_helper import get_winrm_result
    command_text = r'''
    $InstallerPath = "{}"
    $ProcessStartInfo = New-Object System.Diagnostics.ProcessStartInfo;
    $ProcessStartInfo.FileName = $InstallerPath;
    $ProcessStartInfo.Arguments = '/S /v"/qn REBOOT=R ADDLOCAL=ALL" /l C:\Windows\Temp\VMwareToolsInstall.log';
    $ProcessStartInfo.UseShellExecute = $false;
    $PS = New-Object System.Diagnostics.Process;
    $PS.StartInfo = $ProcessStartInfo;
    $Null = $PS.Start();
    $PS.WaitForExit();
    $PS.ExitCode
    '''.format(installer_path)
    try:
        result = get_winrm_result(host_name, command_text, is_ntlm=is_ntlm)
        exit_code = int(result.strip())
        if exit_code == 0:
            return "Success"
        else:
            return "Error"
    except Exception as exception:
        return str(exception)
