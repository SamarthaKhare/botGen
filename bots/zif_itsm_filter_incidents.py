import pymongo
import json
import sys
import os

ITSM_INCIDENT_FILTER_COLLECTION = "incident_polling_parameters"

def get_mongodb_connection():
	"""	
	This function establishes a connection to a MongoDB database using the connection URL and database name.
	Returns:pymongo.database.Database or None: The MongoDB database connection object if successful, otherwise None.
	"""
	result = None
	try:
		data_source = os.environ["MONGO_DB_URL"]
		database = os.environ["ZIF_DB"]
		mongo_client = pymongo.MongoClient(data_source)
		mongo_collection = mongo_client[database]
		if mongo_collection is not None:
			result = mongo_collection
	except Exception as exception:
		print(exception)

	return result

def get_incident_filter_parameters(tool_name, workflow_name):
	"""
	This function retrieves the filter parameters for incidents from a MongoDB collection based on the given tool and workflow names.
	Args:
		tool_name (str): The name of the tool (e.g., "ServiceNow") for which the filter parameters are required.
		workflow_name (str): The name of the workflow for which the filter parameters are needed.
	Returns: list or None: A list of filter patterns if found, otherwise None.
	"""
	result = None
	try:
		mongo_connection = get_mongodb_connection()
		if mongo_connection is not None and tool_name is not None and workflow_name is not None:
			collection = mongo_connection[ITSM_INCIDENT_FILTER_COLLECTION]
			query = {"toolName": tool_name, "workflowName": workflow_name, "active": 1}
			projection = {"filterPatterns": 1}
			document = collection.find_one(query, projection)
			if document is not None:
				result = document["filterPatterns"]
	except Exception as exception:
		print(exception)

	return result

def get_all_filter_patterns(tool_name, workflow_name):
	"""
	This function constructs a combined filter query string from all the filter patterns associated with a given 
	tool and workflow. The query string is formatted for use in the ServiceNow API.
	Args:
		tool_name (str): The name of the tool (e.g., "ServiceNow") for which the filter patterns are needed.
		workflow_name (str): The name of the workflow for which the filter patterns are required.
	Returns: str or None: A formatted query string combining all filter patterns if successful, otherwise None.
	"""

	result = None
	try:
		incident_filters = get_incident_filter_parameters(tool_name, workflow_name)
		if incident_filters is not None:
			index = 0
			for filter_pattern in incident_filters:
				if index == 0:
					result = filter_pattern["value"]
				else:
					result = "{}%5ENQ{}".format(result, filter_pattern["value"])
				index = index + 1	
		if result is not None:
			result = "{}&sysparm_fields=sys_id,number,description,subcategory".format(result)		
	except Exception as exception:
		print(exception)

	return result
