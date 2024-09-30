import os
def check_default_website_presence(host_name, is_ntlm=None):
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
    from remote_connection_helper import get_winrm_result
    try:
        command = command = f"""
onProperty -filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' -Value 'False'
if ($?) {{
    echo 'True'
}} else {{
    echo 'False'
}}
"""
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result.strip().lower() == 'true':
            return {'status': True, 'remarks': 'IIS default document disabled successfully'}
        else:
            return {'status': False, 'remarks': 'Error disabling IIS default document'}
    except Exception as exception:
        print(exception)
        return False

def enable_default_document(host_name, is_ntlm=None):
    from remote_connection_helper import get_winrm_result
    try:
        command = command = f"""
Set-WebConfigurationProperty -filter 'system.webserver/defaultdocument' -pspath 'IIS:\\sites\\Default Web Site' -name 'enabled' -Value 'True'
if ($?) {{
    echo 'True'
}} else {{
    echo 'False'
}}
"""
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result.strip().lower() == 'true':
            return {'status': True, 'remarks': 'IIS default document enabled successfully'}
        else:
            return {'status': False, 'remarks': 'Error enabling IIS default document'}
    except Exception as exception:
        print(exception)
        return False
