import os
def disable_smb(host_name, smb_version, is_ntlm=None):
    from remote_connection_helper import get_winrm_result
    """
    Disables the specified SMB (Server Message Block) version on a remote Windows server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        smb_version (int/str): The version of SMB to disable (e.g., '1', '2', '3').
        is_ntlm (bool, optional): A flag indicating whether NTLM authentication is required.
            Defaults to None.

    Returns:
        str: A success message if the SMB version was disabled successfully.
        None: If the command execution fails or the result is None.
        str: An error message if an exception occurs during execution.

    Raises:
        Exception: Captures and prints any exceptions encountered during command execution.
    """
    try:
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $false -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return f"SMB version {smb_version} disabled successfully"
        else:
            return None
    except Exception as exception:
        print(exception)
        return "An error occurred during execution"

def enable_smb(host_name, smb_version, is_ntlm=None):
    from remote_connection_helper import get_winrm_result
    """
    Enables the specified SMB (Server Message Block) protocol version on a remote server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        smb_version (int): The version of SMB protocol to enable (e.g., 1, 2, or 3).
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. Defaults to None.

    Returns:
        str: A success message if the SMB protocol is enabled, or None if the operation failed.
        In case of an error, it prints the exception and returns an error message.
    
    Example:
        enable_smb("192.168.1.10", 3)
    """
    try:
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $true -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return f"SMB version {smb_version} enabled successfully"
        else:
            return None
    except Exception as exception:
        print(exception)
        return 'An error occurred during execution'

def check_smb_status(host_name, smb_version, is_ntlm=True):
    from remote_connection_helper import get_winrm_result
    """
    Checks the status of the specified SMB (Server Message Block) protocol version on a remote server.

    Args:
        host_name (str): The hostname or IP address of the remote server.
        smb_version (int): The version of SMB protocol to check (e.g., 1, 2, or 3).
        is_ntlm (bool, optional): Indicates whether NTLM authentication is required. Defaults to True.

    Returns:
        str: "Enabled" if the specified SMB version is enabled, "Disabled" if it is disabled, 
        or "Error Occurred" if an exception is raised during the execution.
    
    Example:
        check_smb_status("192.168.1.10", 3)
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
        return "Error Occurred"

