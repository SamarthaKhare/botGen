
from cpu_memory_process import get_total_cpu_usage, get_top_cpu_process, get_total_memory_usage, get_top_memory_process,get_top_cpu_consuming,get_top_memory_consuming,get_top_cpu_consuming_process,get_top_memory_consuming_process
from utility_helper import device_unreachable_status

def get_actual_threshold(device_config):
    """
    for-CPUMemoryResourceRemediation Determines and retrieves the total usage of cpu/memory  for a given device based on its configuration.
    The function takes in the `device_config` dictionary containing device settings such as alert type, 
    OS type, and device name.If the threshold is successfully retrieved, it is processed and returned 
    as a cleaned string else this function update incident with an escalation status.
    Args:device_config (dict): A dictionary containing the following keys:
            - "alert_type" (str): The type of alert, either 'CPU' or 'MEMORY'.
            - "is_linux" (bool): Specifies if the device is a Linux machine.
            - "device_name" (str): The name or identifier of the device.
    Returns:str or None: Returns the numerical value of actual threshold as string or None if an error occurs or the threshold is unavailable.
    """
    try:
        actual_threshold = None
        if device_config:
            alert_type = device_config["alertType"]
            is_linux = device_config['isLinux']
            device_name = device_config["hostName"]
            retry_count=3
            if alert_type == 'CPU':
                if is_linux:
                    actual_threshold = get_top_cpu_consuming(device_name,retry_count)
                else:
                    actual_threshold = get_total_cpu_usage(device_name,retry_count)
            elif alert_type == 'MEMORY':
                if is_linux:
                    actual_threshold = get_top_memory_consuming(device_name,retry_count)
                else:
                    actual_threshold = get_total_memory_usage(device_name,retry_count)
            if actual_threshold is not None:
                actual_threshold = actual_threshold.encode().decode().strip()
                device_config['total_usage']=actual_threshold
                print(f'actual thresold is {actual_threshold}')
            else:
                print("Threshold empty")
                device_unreachable_status(device_config,"SSH Failure","CPUMemoryResourceRemediation")
        else:
            print("Device Config is None")
        return actual_threshold
    except Exception as exception:
        print(exception)


def get_top_utilization_process(device_config):
    """
    If users want the top utilization process this function retrives the top five resource consuming processes (e.g top cpu or memory consuming) for the device
    based on whether it's Linux or not.
    Arguments:
    - device_config (dict): A dictionary containing device configuration details, such as device name, 
    alert type, and is_linux(flag for linux based devices)
    Return: Top resource consuming process on the device
    """
    top_process=None
    if device_config["alertType"] == 'CPU':
        if device_config['isLinux']:
            print("linux case")
            top_process = get_top_cpu_consuming_process(device_config['hostName'])
        else:
            top_process = get_top_cpu_process(device_config["hostName"])
    elif device_config["alertType"] == 'MEMORY':
        if device_config['isLinux']:
            print('linux case')
            top_process = get_top_memory_consuming_process(device_config['hostName'])
        else:
            top_process = get_top_memory_process(device_config["hostName"])
    else:
        print("Alert type is unknown")
    return top_process
    
