
import logging
import requests
import os
import re
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/.env"
load_dotenv(dotenv_path=dotenv_path)

headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
authentication = HTTPBasicAuth(os.getenv('SN_USERNAME'), os.getenv('SN_PASSWORD'))
def search_incidents(filter_query):
	"""
	This function searches for incidents in ServiceNow using a specified filter pattern.
	Args:filter_pattern (str): The pattern to filter incidents in ServiceNow.
	Returns:The list of all the incident that matches with the filter patter, otherwise None.
	"""
	result = None
	try:
		base = f"https://{os.getenv('SN_INSTANCE')}.service-now.com"
		path =base+ f"/api/now/v2/table/incident?sysparm_query=state=1^ORstate=2^{filter_query}"
		
		response = requests.request("get", path, headers = headers,auth=authentication)
		if response is not None and response.status_code == 200:
			result = response.json()
			return result['result']
	except Exception as exception:
		print(exception)

	return result

res=search_incidents("short_descriptionLIKEcpu resource usage")
print(res)
pattern = r"(\w+(?: \w+)*):\s*([^\n:]+)"
# Find all matches
matches = re.findall(pattern, res[0]['description'])

# Convert matches to a dictionary
key_value_pairs = {key.strip(): value.strip() for key, value in matches}

print(key_value_pairs)



def generate_fresh_bot(instruction,incident_filter,model_name='gemini-1.5-pro'):
    print('generating code for new bot')
    instruction=f"incident_filter={incident_filter}"+" "+","+" "+instruction 
    try:
        model = GenerativeModel(model_name, system_instruction=system_prompt_basic)
        prompt = f"""
        Create a detailed executable python function without any arguments based on the below instruction: 
        {instruction}
        Guidelines for Function Creation:
        [Important] Use incident_filter and workflow_name as provided in the instructions.
        1-Retrieve Incidents:Import and use the search_incident function from utility_helper.py, providing incident_filter as input to get a list of all ServiceNow incidents matching the filter.
        2-Iterate Through Incidents:
            For each incident in the list:
            a-Import and use function work_in_progress(input is device configuration and workflow name) from utility_helper.py and update the state of incident to Work in Progress.Funtion return true is update is successful else false
            b.Import and use the get_workflow_payload function from utility_helper.py, passing the incident as input. This function will 
            return a dictionary (device configuration) containing required fields such as device_name, alert_type, service_name, threshold_value, etc.
            b-To check Device Reachability:Import and use the is_device_reachable function from utility_helper.py, providing the device configuration 
            and workflow name as input if it returns the reachable status as Success, proceed with the next steps in the instructions else terminate the function it handles 
            not reachablity case internally.
            c- Only perform the tasks mentioned in user's instruction.
        Key Points:
            Avoid Syntax Errors and import the relevant packages and modules 
        """
        generation_config = GenerationConfig(
            temperature=0.2,
            top_p=0.2,
            top_k=2,
            max_output_tokens=6000,
            response_mime_type="application/json",
            response_schema=response_schema
        )
        logger.info("Sending request to the model")
        response = model.generate_content(prompt, generation_config=generation_config)
        logger.info("Response received from the model")
        response_json = json.loads(response.text)
        return response_json
    except Exception as e:
        logger.error(f"Error generating function code: {e}")
        return {} # Return an empty dictionary to indicate failure
