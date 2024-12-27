import os

def check_default_website_presence(host_name, is_ntlm=True):
    """
    Checks the presence or status of the default IIS (Internet Information Services) website's default document on a remote Windows server.
    This function connects to the remote server using WinRM, queries the default IIS website, and checks whether 
    the default document feature is enabled.
    Args:
        host_name (str): The hostname or IP address of the remote Windows server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. If True, NTLM authentication is used. Defaults to True.
            - True if the default IIS website's default document feature is enabled.
            - False if it is disabled, or if an error occurs during the check.
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to check the enabled status of the default IIS website
        command = "Get-WebConfigurationProperty -Filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' | Select-Object -ExpandProperty value"
        status_result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if status_result is not None:
            status_result = status_result.strip().lower()
            return status_result == 'true'
    except Exception as exception:
        print(exception)
        return False
        
def disable_default_document(host_name, is_ntlm=True):
    """
    Disables the default document setting in IIS (Internet Information Services) for a remote Windows server.
    The function connects to the remote server using WinRM and executes a PowerShell command to disable the default 
    document feature of the IIS default website. It also checks for command success and returns a message accordingly.
    Args:
        host_name (str): The hostname or IP address of the remote Windows server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. If True, NTLM authentication is used. Defaults to True.
    Returns: str: 
            - 'IIS default document disabled successfully' if the operation is successful.
            - 'Error disabling IIS default document' if an error occurs or the operation fails.
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to disable the default document in IIS
        command = f"""
        Set-WebConfigurationProperty -filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' -Value 'False'
        if ($?) {{
            echo 'True'
        }} else {{
            echo 'False'
        }}
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result.strip().lower() == 'true':
            return 'IIS default document disabled successfully'
        else:
            return 'Error disabling IIS default document'
    except Exception as exception:
        print(exception)
        return 'Error disabling IIS default document'

def enable_default_document(host_name, is_ntlm=True):
    """
    Enables the default document setting in IIS (Internet Information Services) for a remote Windows server.
    This function connects to the remote server using WinRM and runs a PowerShell command to enable the default 
    document feature of the IIS default website. It checks for success and returns an appropriate message.
    Args:
        host_name (str): The hostname or IP address of the remote Windows server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. If True, NTLM authentication is used.Defaults to True.
    Returns: str: 
            - 'IIS default document enabled successfully' if the operation is successful.
            - 'Error enabling IIS default document' if an error occurs or the operation fails.
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to enable the default document in IIS
        command = f"""
        Set-WebConfigurationProperty -filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' -Value 'True'
        if ($?) {{
            echo 'True'
        }} else {{
            echo 'False'
        }}
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result.strip().lower() == 'true':
            return 'IIS default document enabled successfully'
        else:
            return 'Error enabling IIS default document'
    except Exception as exception:
        print(exception)
        return 'Error enabling IIS default document'
