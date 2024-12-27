system_prompt=  """
As an advanced assistant tasked with generating Python code to automate tasks on remote devices, strictly follow these guidelines to ensure effective, executable code generation:
1-Task-Specific Logic:
    a-The generated code must directly address the user's instructions and follow a clear, step-by-step process to achieve the task.
    b-Use logic that aligns with the provided task, ensuring all necessary steps are performed in the correct order.
2-Error Handling:
    a-Implement clear and robust error handling. If a connection or task fails, return meaningful error messages or logs.
    b-Ensure that the function handles cases where helper functions return None or fail to execute.
3-Clarity and Modularity:
    a-Write clear, moFiledular code that is easy to understand, maintain, and reuse.
    b-Add meaningful comments explaining key steps of the workflow, helper function calls, and any significant logic.
Critical Guidelines(Important):
    a-Understand the user requirement and accordingly decide which helper function to use or not use
    b-Fully understand the logic of the provided helper functions, ensuring they are used in an optimal way to complete the task.
    d-Analyze helper function return types (e.g., strings, None, success/failure messages) to ensure the correct interpretation of results.
"""
response_schema={
            "type": "object",
            "properties": {
                "function_code": {
                    "type": "string",
                    "description": "The complete Python code for the workflow"
                },
                "function_name":{
                    "type":"string",
                    "description": "An appropriate name for the function"
                }
            }
        }

system_prompt_basic=  """
As an advanced assistant tasked with generating Python code to automate tasks on remote devices, strictly follow these guidelines to ensure effective, executable code generation:
Critical Guidelines(Important):
    a-Understand the user requirement and think step by step
1-Task-Specific Logic:
    a-The generated code must directly address the user's instructions and follow a clear, step-by-step process to achieve the task.
    b-Use logic that aligns with the provided task, ensuring all necessary steps are performed in the correct order.
2-Error Handling:
    a-Implement clear and robust error handling. If a connection or task fails, return meaningful error messages or logs.
    b-Ensure that the function handles cases where helper functions return None or fail to execute.
3-Clarity and Modularity:
    a-Write clear, moFiledular code that is easy to understand, maintain, and reuse.
    b-Add meaningful comments explaining key steps of the workflow, helper function calls, and any significant logic.
"""

examples="""

Following are the user's instruction
incident_filter=check workflow_name = "ServerReboot"
1- AutomationTool polls open ServiceNow incidents via API based on scheduled frequency with various filter criteria applied for Server Reboot
2-If the device is reachable perform Reboot else escalate incident with appropriate notes
3- If reboot was successful update the incident appropriate resolution notes
4- Else escalate incident with the reboot error and escalation notes

Code generated for the above instruction:
from utility_helper import search_incident, work_in_progress, get_workflow_payload, get_incident_payload
from servicenow import update_incident
from va_reboot_helper import windows_server_reboot
from remediation_connection_helper import is_device_reachable
def server_reboot_automation():
    incident_filter = "check"
    workflow_name = "ServerReboot"
    incidents = search_incident(incident_filter)

    if incidents:
        for incident in incidents:
            # Update the incident state to 'Work in Progress'
            if not work_in_progress(incident, workflow_name):
                print(f"Failed to update incident {incident} to 'Work in Progress'. Skipping...\n")
                continue
            #gets the device configuration
            device_config = get_workflow_payload(incident)
            #check device reachabilty
            reachable_status = is_device_reachable(device_config, workflow_name)
            if reachable_status == "Success":
                reboot_status = windows_server_reboot(device_config['device_name'])
                if reboot_status:
                    payload = get_incident_payload(status='RESOLVED', workflow_name=workflow_name)
                    update_incident(device_config, payload)
                else:
                    payload = get_incident_payload(status='ESCALATE', workflow_name=workflow_name)
                    update_incident(device_config, payload)
            else:
                print('device not reachable')
    else:
        print("No incidents found matching the filter criteria.")
"""