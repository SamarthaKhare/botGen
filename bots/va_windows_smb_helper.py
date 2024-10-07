import os

'''
def disable_smb(host_name, smb_version, is_ntlm=None):
    from remote_connection_helper import get_winrm_result
    """
    This function disables the smb 
    Args: host_name,smb version 
    Returns :
    The return is a output string if result is not None 
    """
    try:
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $false -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return "SMB version {smb_version} disabled successfully"
        else:
            return None
    except Exception as exception:
        print(exception)
        return "An error occurred during execution"
'''
'''
def enable_smb(host_name, smb_version, is_ntlm=None):
    from remote_connection_helper import get_winrm_result
    """
    This function enables the smb 
    Args: host_name,smb version 
    Returns :
    The return is a string if result is not None other wise None is returned 
    """
    try:
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $true -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return "SMB version {smb_version} enabled successfully"
        else:
            return None
    except Exception as exception:
        print(exception)
        return 'An error occurred during execution'
'''
'''
def check_smb_status(host_name, smb_version, is_ntlm=True):
    from remote_connection_helper import get_winrm_result
    """
    This function check the status of smb (enabled or disabled) 
    Args: host_name,smb version
    Returns : A string either "Enabled", "Disabled" or "Error Occured" 
    """
    try:
        command = f"""
        Get-SmbServerConfiguration | Select EnableSMB{smb_version}Protocol
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return "Enabled"
        else:
            return "Disabled"
    except Exception as exception:
        print(exception)
        return "Error Occured"
'''
