import subprocess
import platform

def get_ping_output(host):
    """
    For - PingResponseRemediation it provides the ping status by executing a single ping command to check the reachability of a given host.
    This function is cross-platform and adjusts the `ping` command based on the operating system.
    Arguments:host (str): The hostname or IP address of the target to ping.
    Returns:str: The output of the ping command if successful, or an error message if the host is unreachable or the ping command fails.
    """
    try:
        # Determine the OS and set the appropriate ping command
        if platform.system().lower() == "windows":
            command = ["ping", "-n", "1", "-w", "3000", str(host)]  # Windows-specific flags
        else:
            command = ["/bin/ping" if platform.system().lower() != "darwin" else "/sbin/ping", "-c1", "-w3", str(host)]  # Linux/macOS flags
          # Run the ping command
        response = subprocess.Popen(command, stdout=subprocess.PIPE).stdout.read()
        # Decode and process the response
        response = response.decode()
        if response and response.strip():
            print(response)
            return response
        else:
            return f"ping:{host}: Name or service not known"
    except Exception as e:
        return f"An error occurred: {str(e)}"
