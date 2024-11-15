from datetime import datetime
from logging import exception
import time
import os

from zif_workflow_helper import get_workflow_config_value
from zif_mongo_helper import get_single_document
from string_helper import substring_by_text
from zif_itsm_filter_incidents import get_all_filter_patterns
from uniconn.servicenow import search_incidents



INCIDENT_FILTER_COLLECTION = "incident_polling_parameters"
ITSM_TOOL_NAME = "SERVICENOW"

def get_incident_search_result(workflow_name):
	"""
	Fetches and returns the search result for incidents based on the filter patterns generated for the specified workflow name.
	Arguments:workflow_name (str): The name of the workflow for which incidents are being searched.
	Returns- dict or None: The search result if found, otherwise None.
	"""
	search_result = None
	try:
		filter_pattern = get_all_filter_patterns(ITSM_TOOL_NAME, workflow_name)
		if filter_pattern is not None:
			search_result = search_incidents(filter_pattern)
	except Exception as exception:
		print(exception)

	return search_result

def get_delimiter_pattern(workflow, subcategory, pattern):
	"""
	Retrieves a delimiter pattern containing the "start" and "end" text for a specific workflow and subcategory 
	from the incident filter collection.
	Arguments:
	- workflow (str): The name of the workflow.
	- subcategory (str): The subcategory type to match within the pattern elements.
	- pattern (str): The specific pattern field name to project from the document.
	Returns:- dict: A dictionary containing "start" and "end" keys if a matching delimiter pattern is found, otherwise an empty dictionary.
	"""
	delimiter_pattern = {}
	search_result = None
	try:
		if all([workflow, subcategory,  pattern]):
			search_criteria = {"toolName": ITSM_TOOL_NAME, "workflowName": workflow}
			projection = {pattern}
			search_result = get_single_document(INCIDENT_FILTER_COLLECTION, search_criteria, projection)
		if search_result is not None and pattern in search_result:
			print(search_result[pattern])
			for element in search_result[pattern]:
				if "type" in element and element["type"] == subcategory:
					delimiter_pattern = {"start": element["startText"], "end": element["endText"]} 
	except Exception as exception:
		print(exception)

	return delimiter_pattern

def get_parsed_result(actual_text, start_text, end_text):
	"""
	Parses a substring from the actual text between the specified start and end texts. It also removes unwanted 
	characters such as newlines and trims extra spaces from the result.
	Arguments:
	- actual_text (str): The full text from which to extract the substring.
	- start_text (str): The text marking the start of the substring.
	- end_text (str): The text marking the end of the substring.
	Returns:str or None: The parsed and cleaned substring if found, otherwise None.
	"""
	result = None
	if all([actual_text, start_text, end_text]):
		try:
			result = substring_by_text(actual_text, start_text, end_text)
			if result is not None:
				result = result.replace("\r\n", "")
				result = result.replace("\r", "")
				result = result.replace("\n", "")
				result = result.replace(start_text, "")
				result = result.replace(end_text, "")
				result = result.strip()
		except Exception as exception:
			print(exception)

	return result

def get_pattern_value(workflow, subcategory, description, pattern):
	"""	
	Extracts a delimited value from the incident description by applying a search pattern for a given workflow 
	and subcategory. It uses delimiters defined in the filter collection to parse the result.
	Arguments:
	- workflow (str): The name of the workflow.
	- subcategory (str): The subcategory of the incident.
	- description (str): The description text of the incident.
	- pattern (str): The search pattern field to extract delimiters for parsing.
	Returns:str or None: The extracted and cleaned value from the description if successful, otherwise None.
	"""
	delimited_result = None
	if all([workflow, description]):
		try:
			temp_result = get_delimiter_pattern(workflow, subcategory, pattern)
			print("temp_result", temp_result)
			if temp_result is not None:
				start_value = temp_result.get("start")
				end_value = temp_result.get("end")
				delimited_result = get_parsed_result(description, start_value, end_value)
				print("delimited_result",delimited_result)
		except Exception as exception:
			print(exception)

	return delimited_result		


def get_workflow_payload(workflow,incident):
	"""	
	This function returns device configuration for an incident based on the given workflow and incident details. 
	It extracts relevant fields such as device name, service name, alert type, and threshold values by parsing the 
	incident description and applying search patterns.
	Arguments:
	- workflow (str): The name of the workflow, such as "HIGH RESOURCE USAGE" or "SERVICERESTART".
	- incident (dict): A dictionary containing incident details, which may include "subcategory", "description", 
	"sys_id", "number", "alertType", etc.
	Returns:
	dict or None: A dictionary containing the constructed payload with fields such as "sysId", "number", 
	"deviceName", "thresholdValue", "alertType", and "conditionLinuxCheck". If essential data is missing, 
	it returns None.
	"""
	payload = {}
	subcategory = None
	description = None
	device_name = None
	alert_type = None
	search_pattern = None
	service_name=None
	if incident is not None:
		search_pattern = "deviceNamePatterns"
		subcategory = incident.get("subcategory")
		description = incident.get("description")			
		payload["sysId"] = incident.get("sys_id")
		payload["number"] = incident.get("number")
		device_name = get_pattern_value(workflow, subcategory, description, search_pattern)
		if device_name is not None:
			device_name = device_name.strip()
		else:
			print("No device name in incident details")
	
	if workflow == "CPUMemoryResourceRemediation":
		alert_type = incident.get("alertType")
		search_pattern = "thresholdValuePatterns"
		temp_subcategory = "{} {}".format(subcategory, alert_type)
		threshold_value = get_pattern_value(workflow, temp_subcategory, description, search_pattern)
		print("threshold_value", threshold_value)
		if threshold_value is not None:
			payload["thresholdValue"] = threshold_value.strip()
		else:
			payload = None
		payload["alertType"] = alert_type
		is_linux_pattern = "linuxConditionPatterns"
		is_linux = get_pattern_value(workflow, subcategory, description, is_linux_pattern)
		print(is_linux)
		if "linux" in is_linux.lower():
			payload["conditionLinuxCheck"] = True
		else:
			payload["conditionLinuxCheck"] = False
		if all([payload["sysId"],payload["number"],device_name,alert_type,threshold_value]):
			if ("lnx" in device_name.lower() or payload["conditionLinuxCheck"] == True):
				is_linux = True
			else:
				is_linux = False
			is_sql = "sql" in device_name.lower()
			is_comment_code = "comment" in device_name.lower()
			print('is linux', is_linux)
			is_vault_agent = "vault" in device_name.lower()
			resolver_details = get_workflow_config_value("CPUMEMORY_RESOLVER_GROUP")
			if is_linux:
				resolver_group = resolver_details.get("lnx", None)
			if is_sql:
				resolver_group = resolver_details.get("sql", None)
			if is_comment_code:
				resolver_group = resolver_details.get("commentCode", None)
			if is_vault_agent:
				resolver_group = resolver_details.get("vaultAgent", None)
			if not (is_linux or is_sql or is_comment_code or is_vault_agent):
				resolver_group = resolver_details.get("others", None)
			resolver_id=resolver_group.get('resolverGroup', None)
			resolver = resolver_group.get('resolver', None)
			mail_address = resolver_group.get('mailAddress', None)
			device_config = {'sys_id'        : payload["sys_id"],
					'incident_id'    : payload["number"],
					'device_name'    : device_name,
					'alert_type'     : alert_type.upper(),
					'threshold_value': threshold_value,
					'is_linux'       : is_linux,
					'is_sql'         : is_sql,
					'is_comment_code': is_comment_code,
					'is_vault_agent' : is_vault_agent,
					'resolver_id'    : resolver_id,
					'resolver'       : resolver,
					'mail_address'   : mail_address
					}
			print('device config is')
			print(device_config)
			return device_config
	elif workflow=="ServiceRestartRemediation":
		service_name=get_pattern_value(workflow,subcategory,description,"serviceNamePatterns")
		service_name=service_name.strip()
	
	if device_name is not None:
		payload["deviceName"] = device_name
	if service_name is not None:
		payload["serviceName"] = service_name
	
	print("payload", payload)		
	return payload
