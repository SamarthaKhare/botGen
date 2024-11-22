import time
from remote_connection_helper import get_winrm_script_result,get_ssh_script_result,get_ssh_client

def get_top_cpu_process(host_name,retry_count,count=5,is_ntlm=True):
    """
    Retrieves the top CPU-consuming processes on a remote Windows host using WinRM. The function executes 
    a PowerShell command to gather process IDs, names, and CPU usage, sorted in descending order by CPU 
    usage, and returns the top 'count' results.
    Arguments:
    - host_name (str): The name or IP address of the remote host.
    - retry_count (int): The number of times to retry the operation.
    - count (int, optional): The number of top CPU-consuming processes to retrieve (default is 5).
    - is_ntlm (bool, optional): Specifies whether to use NTLM authentication (default is True).
    Returns- str: A formatted string of top CPU processes with process ID, name, and CPU usage. Returns None if 
    an error occurs.
    """
    result = None
    try:
        if host_name is not None:
            command = """
Get-Counter '\Process(*)\ID Process','\Process(*)\% Processor Time' -ErrorAction SilentlyContinue |
ForEach-Object {
$_.CounterSamples |
Where-Object InstanceName -NotMatch '^(?:idle|_total|system)$' |
Group-Object {Split-Path $_.Path} |
ForEach-Object {
[pscustomobject]@{
    ProcessId = $_.Group |? Path -like '*\ID Process' |% RawValue
    ProcessName = $_.Group[0].InstanceName
    CPUCooked = $_.Group |? Path -like '*\% Processor Time' |% CookedValue
}
} | Sort-Object CPUCooked -Descending |
Select-Object -First 5 |
ForEach-Object {
"{0}|||{1}|||{2} ~~~" -f $_.ProcessId, $_.ProcessName, '{0:P}' -f ($_.CPUCooked / 100 / $env:NUMBER_OF_PROCESSORS)
}
}
"""
            result = get_winrm_script_result(host_name, command,is_ntlm)
            if result is not None:
                result = result.strip()
    except Exception as exception:
            print(exception)
    return result

def get_total_cpu_usage(host_name,retry_count,is_ntlm=True):
     
    """
    Calculates the average total CPU usage on a remote Windows host using WinRM. The function runs a 
    PowerShell command to get the average CPU load percentage.
    Arguments:
    - host_name (str): The name or IP address of the remote host.
    - retry_count (int): The number of times to retry the operation.
    - is_ntlm (bool, optional): Specifies whether to use NTLM authentication (default is True).
    Returns-str: The average CPU load percentage as a string. Returns None if an error occurs.
    """
    result = None
    try:
        if host_name is not None:
            command = """
            $CPUAverage = Get-WmiObject win32_processor | Measure-Object -Property LoadPercentage -Average
            $AverageValue = $CPUAverage | Select-Object Average
            $Result =  $AverageValue | Format-Table -HideTableHeaders
            echo $Result
            """
            result = get_winrm_script_result(host_name, command,is_ntlm)
            if result is not None:
                result = result.strip()
    except Exception as exception:
        print(exception)
    return result

def get_top_memory_process(host_name,retry_count,count=5,is_ntlm=True):
    """
    Retrieves the top memory-consuming processes on a remote Windows host using WinRM. The function 
    executes a PowerShell command to gather process IDs, names, and memory usage, sorted in descending 
    order by memory usage, and returns the top 'count' results.
    Arguments:
    - host_name (str): The name or IP address of the remote host.
    - retry_count (int): The number of times to retry the operation.
    - count (int, optional): The number of top memory-consuming processes to retrieve (default is 5).
    - is_ntlm (bool, optional): Specifies whether to use NTLM authentication (default is True).
    Returns:
    - str: A formatted string of top memory processes with process ID, name, and memory usage percentage.Returns None if an error occurs.
    """    
    result = None
    try:
        if host_name is not None:
            command = """
$TotalMemory = Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory
Get-Counter '\Process(*)\ID Process','\Process(*)\Working Set - Private' -ErrorAction SilentlyContinue |
ForEach-Object {
$_.CounterSamples |
Where-Object InstanceName -NotMatch '^(?:idle|_total|system)$' |
Group-Object {Split-Path $_.Path} |
ForEach-Object {
[pscustomobject]@{
    ProcessId = $_.Group |? Path -like '*\ID Process' |% RawValue
    ProcessName = $_.Group[0].InstanceName
    MemoryUsage = $_.Group |? Path -like '*\Working Set - Private' |% CookedValue
}
} | Sort-Object MemoryUsage -Descending |
Select-Object -First 5 |
ForEach-Object {
"{0}|||{1}|||{2:P}~~~" -f $_.ProcessId, $_.ProcessName, ($_.MemoryUsage / $TotalMemory)
}
}
"""
            result = get_winrm_script_result(host_name, command,is_ntlm)
            if result is not None:
                result = result.strip()
    except Exception as exception:
            print(exception)
    return result

def get_total_memory_usage(host_name,retry_count,is_ntlm=True):
    """
    Calculates the total memory usage percentage on a remote Windows host using WinRM. The function runs 
    a PowerShell command to fetch the total visible memory size and free physical memory to compute memory 
    usage.
    Arguments:
    - host_name (str): The name or IP address of the remote host.
    - retry_count (int): The number of times to retry the operation.
    - is_ntlm (bool, optional): Specifies whether to use NTLM authentication (default is True).
    Returns- str: The memory usage percentage as a formatted string. Returns None if an error occurs.
    """

    result = None
    try:
        if host_name is not None:
            command = """$Result = gwmi -Class win32_operatingsystem | Select-Object @{Name = 'MemoryUsage'; 
                Expression = {'{0:N2}' -f ((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) * 100) / $_.TotalVisibleMemorySize)}}
                $Result = $Result | Format-Table -HideTableHeaders
                echo $Result"""
            result = get_winrm_script_result(host_name, command,is_ntlm)
            print(f" result of get_total_memory_usage is:{result}")
            if result is not None:
                result = result.strip()
    except Exception as exception:
        print(exception)
    return result

def get_top_cpu_consuming_process(host_name, process_count, retry_count):
    """
    Fetches the top CPU-consuming processes on a remote Linux host. The function executes a command over 
    SSH to retrieve process IDs, names, and normalized CPU usage, and returns a list of the specified 
    number of top CPU-consuming processes.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - process_count (int): The number of top CPU-consuming processes to retrieve.
    - retry_count (int): The number of times to retry the operation.
    Returns:-list: A list of dictionaries containing process ID, command name, and CPU usage percentage. Returns an empty list if an error occurs.
    """
    command_result = None
    cpu_process = []
    try:
        if host_name is not None:
            process_count += 1
            command = f"ps -eo pid,comm,%cpu --sort=-%cpu | head -{process_count} | awk -v cores=$(nproc) '{{print $1, $2, $3/cores}}'"
            command_result = get_ssh_script_result(host_name, command)
            if command_result is not None:
                command_result.pop(0)
                for return_result in command_result:
                    process_list = return_result.split()
                    cpu_process.append({
                        "PID": process_list[0],
                        "COMMAND": ' '.join(process_list[1:len(process_list)-1]),
                        "CPU USAGE IN %": f"{process_list[len(process_list)-1]}%"
                    })
    except Exception as exception:
        print(exception)
    return cpu_process

def get_top_memory_consuming_process(host_name,process_count,retry_count):
    """
    Retrieves the top memory-consuming processes on a remote Linux host. The function executes a command 
    over SSH to gather process IDs, names, and memory usage percentages, and returns a list of the 
    specified number of top memory-consuming processes.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - process_count (int): The number of top memory-consuming processes to retrieve.
    - retry_count (int): The number of times to retry the operation.
    Returns:-list: A list of dictionaries containing process ID, command name, and memory usage percentage.Returns an empty list if an error occurs.
    """
    command_result = None
    process_count=process_count+1
    memory_process=[]
    try:
        if host_name is not None:
            command = "ps -eo pid,command,%mem --sort=-%mem | head -{num}".format(num=process_count)
            command_result = get_ssh_script_result(host_name, command)
            if command_result is not None:
                command_result.pop(0)
                for return_result in command_result:
                    process_list = return_result.split()
                    memory_process.append({"PID":process_list[0],"COMMAND":' '.join(process_list[1:len(process_list)-1]),"MEMORY USAGE IN %":process_list[len(process_list)-1]+"%"})
    except Exception as exception:
        print(exception)
    return memory_process

def kill_cpu_consuming_process(host_name,kill_count):
    """
    Terminates the top CPU-consuming processes on a remote Linux host. The function retrieves the process 
    IDs of the specified number of top CPU-consuming processes and sends a kill signal to terminate them.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - kill_count (int): The number of top CPU-consuming processes to terminate.
    Returns- list: A list of dictionaries containing process ID and the result of the kill command. Returns an empty list if an error occurs.
    """
    command_result = None
    kill_count=kill_count+1
    return_result=[]
    try:
        get_pid="ps -eo pid --sort=-%cpu | head -{num}".format(num=kill_count)
        top_pid=get_ssh_script_result(host_name, get_pid)
        if top_pid is not None:
           top_pid.pop(0)
           for id in top_pid:
               command="kill -9 {pid}".format(pid=id)
               command_result = get_ssh_script_result(host_name, command)
               return_result.append({"PID":id,"RESULT":command_result})
    except Exception as exception:
        print(exception)
    return return_result

def kill_memory_consuming_process(host_name,kill_count):
    """
    Terminates the top memory-consuming processes on a remote Linux host. The function retrieves the 
    process IDs of the specified number of top memory-consuming processes and sends a kill signal to 
    terminate them.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - kill_count (int): The number of top memory-consuming processes to terminate.
    Returns-list: A list of dictionaries containing process ID and the result of the kill command. Returns an 
    empty list if an error occurs.
    """
    command_result = None
    kill_count=kill_count+1
    return_result=[]
    try:
        get_pid="ps -eo pid --sort=-%mem | head -{num}".format(num=kill_count)
        top_pid=get_ssh_script_result(host_name, get_pid)
        if top_pid is not None:
            top_pid.pop(0)
            for id in top_pid:
                command="kill -9 {pid}".format(pid=id)
                command_result = get_ssh_script_result(host_name, command)
                return_result.append({"PID":id,"RESULT":command_result})
    except Exception as exception:
        print(exception)
    return return_result

def get_top_cpu_consuming(host_name,retry_count):

    """
    Calculates the average CPU consumption on a remote Linux host over three samples. The function executes 
    a command over SSH to retrieve the CPU usage percentage and averages the results, retrying up to the 
    specified number of times if the operation fails.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - retry_count (int): The number of times to retry the operation if it fails.
    Returns:- str: The average CPU consumption as a string. Returns None if an error occurs.
    """
    average_cpu_consumption = None
    try:
        if host_name and retry_count is not None:
            success = False
            command = "top -b -n1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
            num_retries = 0
            while not success and num_retries < int(retry_count):
                try:
                    client = get_ssh_client(host_name)
                    if client is not None:
                        total_cpu_consumption = 0
                        for i in range(3):
                            stdin, stdout, stderr = client.exec_command(command)
                            if stdout is not None:
                                cpu_consumption = float(stdout.read().decode('utf-8').strip())
                                if cpu_consumption is not None and type(cpu_consumption) == float:
                                    print(f"cpu at {num_retries } is {cpu_consumption} ")
                                    total_cpu_consumption += cpu_consumption
                                    time.sleep(2)
                                else:
                                    print("cpu_consumption is none")
                        average_cpu_consumption = str(total_cpu_consumption / 3)
                        success = True
                    else:
                        print(f"client failed retrying for {num_retries} time")
                        num_retries += 1
                except Exception as exception:
                    print(exception)
                    print(f"retrying for {num_retries} time")
                    num_retries += 1
        else:
            print("2 none")
    except Exception as exception:
        print(exception)
    return average_cpu_consumption

def get_top_memory_consuming(host_name,retry_count):

    """
    Fetches the memory usage percentage on a remote Linux host. The function executes a command over SSH to 
    retrieve the memory usage percentage and returns the result.
    Arguments:
    - host_name (str): The name or IP address of the remote Linux host.
    - retry_count (int): The number of times to retry the operation.
    Returns:- str: The memory usage percentage as a string. Returns None if an error occurs or if the result is not found.
    """
    result = None
    try:
        if host_name and retry_count is not None:
            command = "free | awk 'FNR == 2 {used = $3 / $2 * 100.0; print used}'"
            memory_result = get_ssh_script_result(host_name,command)
            if memory_result is not None and len(memory_result) > 0:
                result = memory_result[0]
            else:
                print("memory result is none")
        else:
            print("2 none")
    except Exception as exception:
        print(exception)
    return result
