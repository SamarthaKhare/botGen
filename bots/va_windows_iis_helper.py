import os

def check_default_website_presence(host_name, is_ntlm=None):
    """
    Checks the presence or status of the default IIS (Internet Information Services) website on a remote server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. Defaults to None.

    Returns:
        bool: True if the default IIS website is enabled, False if it is disabled or an error occurs.

    Example:
        check_default_website_presence("192.168.1.15")
    """
    from remote_connection_helper import get_winrm_result
    try:
        command = "Get-WebConfigurationProperty -Filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' | Select-Object -ExpandProperty value"
        status_result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if status_result is not None:
            status_result = status_result.strip().lower()
            return status_result == 'true'
    except Exception as exception:
        print(exception)
        return False
        
def disable_default_document(host_name, is_ntlm=None):
    """
    Disables the default document setting in IIS (Internet Information Services) for a remote server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. Defaults to None.

    Returns:
        str: A message indicating whether the default IIS document was successfully disabled or an error occurred.

    Example:
        disable_default_document("192.168.1.15")
    """
    from remote_connection_helper import get_winrm_result
    try:
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

def enable_default_document(host_name, is_ntlm=None):
    """
    Enables the default document setting in IIS (Internet Information Services) for a remote server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. Defaults to None.

    Returns:
        str: A message indicating whether the default IIS document was successfully enabled or an error occurred.

    Example:
        enable_default_document("192.168.1.15")
    """
    from remote_connection_helper import get_winrm_result
    try:
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



