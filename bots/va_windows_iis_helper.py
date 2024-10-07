import os
'''
def check_default_website_presence(host_name, is_ntlm=None):
    """
    This function check the default status of iis 
    Args: host_name
    Returns : A string either "true" or "false"  
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
'''
'''
def disable_default_document(host_name, is_ntlm=None):
    """
    This function disables the default document 
    Args: host_name
    Returns : A string either 'IIS default document disabled successfully' or 'Error disabling IIS default document'
    """
    from remote_connection_helper import get_winrm_result
    try:
        command = f"""
        onProperty -filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' -Value 'False'
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
'''
'''
def enable_default_document(host_name, is_ntlm=None):
    """
    This function enables the default document  
    Args: host_name
    Returns : A string either 'IIS default document enabled successfully' or 'Error enabling IIS default document' 
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
'''
