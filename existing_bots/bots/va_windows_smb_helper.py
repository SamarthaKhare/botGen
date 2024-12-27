import os
def disable_smb(host_name, smb_version, is_ntlm=True):
    """
    Disables the specified SMB (Server Message Block) protocol version on a remote Windows server.
    This function connects to a remote Windows server using WinRM and disables the specified SMB protocol version 
    (e.g., SMB1, SMB2, or SMB3). It executes a PowerShell command to disable the SMB protocol for the given version.
    Args:
        host_name (str): The hostname or IP address of the remote Windows server.
        smb_version (int/str): The version of SMB protocol to disable. Should be passed as a number or string ('1', '2', '3').
        is_ntlm (bool, optional): A flag indicating whether NTLM authentication is required. If True, NTLM authentication is used.Defaults to True.
    Returns:
        str: 
            - "SMB version {smb_version} disabled successfully" if the SMB protocol was disabled successfully.
        str: 
            - "SMB version {smb_version} can not be disabled" If the command execution fails or returns no result.
        str: 
            - "An error occurred during execution" if an exception is raised during command execution.
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to disable the specified SMB protocol version
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $false -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return f"SMB version {smb_version} disabled successfully"
        else:
            return f"SMB version {smb_version} can not be disabled"
    except Exception as exception:
        print(exception)
        return "An error occurred during execution"

def enable_smb(host_name, smb_version, is_ntlm=True):
    """
    Enables the specified SMB (Server Message Block) protocol version on a remote Windows server.
    This function connects to a remote Windows server using WinRM and enables the specified SMB protocol version 
    (e.g., SMB1, SMB2, or SMB3). It executes a PowerShell command to enable the SMB protocol for the given version.
    Args:
        host_name (str): The hostname or IP address of the remote Windows server.
        smb_version (int/str): The version of SMB protocol to enable. Should be passed as a number or string ('1', '2', '3').
        is_ntlm (bool, optional): A flag indicating whether NTLM authentication is required. If True, NTLM authentication is used.Defaults to True.
    Returns:
        str: 
            - "SMB version {smb_version} enabled successfully" if the SMB protocol was enabled successfully.
        str: 
            -" SMB version {smb_version} can not be enabled" If the command execution fails or returns no result.
        str: 
            - "An error occurred during execution" if an exception is raised during command execution.
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to enable the specified SMB protocol version
        command = f"""
        Set-SmbServerConfiguration -EnableSMB{smb_version}Protocol $true -Confirm:$false | Out-Null
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if result:
            return f"SMB version {smb_version} enabled successfully"
        else:
            return f"SMB version {smb_version} can not be enabled"
    except Exception as exception:
        print(exception)
        return 'An error occurred during execution'

def check_smb_status(host_name, smb_version, is_ntlm=True):
    """
    """
    from remote_connection_helper import get_winrm_result
    try:
        # PowerShell command to check the status of the specified SMB protocol version
        command = f"""
        Get-SmbServerConfiguration | Select EnableSMB{smb_version}Protocol
        """
        result = get_winrm_result(host_name, command, is_ntlm=is_ntlm)
        if "False" in result:
            result=False
        else:
            result=True
        if result:
            return "Enabled"
        else:
            return "Disabled"
    except Exception as exception:
        print(exception)
        return "Error Occurred"
