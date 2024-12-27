import pymongo
import json
import sys
import os
from bson import ObjectId
from datetime import datetime


WORKFLOW_CONFIGURATION_COLLECTION = "automation_airflow_config"
WORKFLOW_CONNECTION_COLLECTION = "automation_workflow_connection"
INCIDENT_CREATION_PARAMETERS = "automation_incident_configuration"
WORKFLOW_CONNECTION_MONITORING_COLLECTION = "automation_workflow_monitoring"

mongo_client = pymongo.MongoClient(os.environ["MONGO_DB_URL"])
mongo_session = mongo_client[os.environ["ZIF_DB"]]

decrypt = lambda x: x

def get_mongodb_connection():
    """
    Establishes a connection to a MongoDB database using environment variables for the connection details.
    This function retrieves the MongoDB URL and database name from environment variables and 
    creates a connection to the MongoDB database. If the connection is successful, it returns 
    the MongoDB connection object; otherwise, it returns None.
    Returns:MongoClient or None: A MongoDB client connection object if successful, None if an error occurs.
    Raises:
        Exception: If the connection attempt fails due to issues with environment variables or MongoDB.
    """
    result = None
    try:
        data_source = os.environ["MONGO_DB_URL"]
        database = os.environ["ZIF_DB"]
        mongo_client = pymongo.MongoClient(data_source)
        mongo_connection = mongo_client[database]
        if mongo_connection is not None:
            result = mongo_connection
    except Exception as exception:
        print(exception)

    return result


def get_workflow_config_value(key):
    """
    Retrieves the configuration value for a given key from the workflow configuration collection.
    This function queries the workflow configuration collection in MongoDB to fetch the value 
    corresponding to the provided key. If the key exists in the collection, the value is returned.
    Args:key (str): The key whose corresponding configuration value needs to be retrieved.
    Returns:str or None: The value associated with the provided key, or None if not found or an error occurs.
    Raises:
        Exception: If the MongoDB connection or query fails.
    """
    result = None
    try:
        mongo_connection = get_mongodb_connection()
        if mongo_connection is not None and key is not None:
            collection = mongo_connection[WORKFLOW_CONFIGURATION_COLLECTION]
            document = collection.find_one({"key": key}, {"value": 1})
            if document is not None:
                result = document["value"]
    except Exception as exception:
        print(exception)

    return result


def get_workflow_connection(connection_id):
    """
    Retrieves connection details for a workflow connection based on the provided connection ID.
    This function queries the workflow connection collection in MongoDB to fetch connection 
    details such as host, username, password, port, and extra metadata. It also decrypts 
    the username and password if needed.
    Args:connection_id (str): The unique identifier for the workflow connection.
    Returns:
        dict or None: A dictionary containing connection details such as host, username, password, 
        port, and extra metadata, or None if the connection is not found or an error occurs.
    Raises:
        Exception: If the MongoDB connection or query fails.
    """
    result = None
    user_name = ''
    password = ''
    try:
        mongo_connection = get_mongodb_connection()
        if mongo_connection is not None and connection_id is not None:
            collection = mongo_connection[WORKFLOW_CONNECTION_COLLECTION]
            document = collection.find_one({"connId": connection_id}, {"connId": 0, "connType": 0})
            user_name = decrypt(document["login"])
            if user_name is None:
                user_name = document["login"]

            password = decrypt(document["password"])
            if password is None:
                password = document["password"]

            if document is not None:
                result = {
                    "host": document["host"],
                    "username": user_name,
                    "password": password,
                    "port": document["port"],
                    "extra": document["extra"]
                }
                if "database" in document:
                    result["database"] = document["database"]
                return result
    except Exception as exception:
        print(exception)

    return result


def get_incident_creation_config(workflow_name):
    """
    """
    result = None
    try:
        mongo_connection = get_mongodb_connection()
        if mongo_connection is not None and workflow_name is not None:
            collection = mongo_connection[INCIDENT_CREATION_PARAMETERS]
            document = collection.find_one({"workflowName": workflow_name}, {"_id": 0})
            if document is not None:
                result = document
    except Exception as exception:
        print(exception)

    return result


def get_sccm_workflow_connection(connection_id):
    """
    Retrieves connection details for an SCCM workflow connection using a connection ID.
    This function fetches the SCCM workflow connection details such as host, username, password, 
    and port from the MongoDB collection based on the connection ID provided.
    Args:connection_id (str): The unique identifier for the SCCM workflow connection.
    Returns:
        dict or None: A dictionary containing the connection details (host, username, password, port, extra), 
        or None if not found or an error occurs.
    Raises:Exception: If the MongoDB connection or query fails.
    """
    result = None
    try:
        mongo_connection = mongo_session
        if mongo_connection is not None and connection_id is not None:
            collection = mongo_connection[WORKFLOW_CONNECTION_COLLECTION]
            document = collection.find_one({"connId": connection_id}, {"connId": 0, "connType": 0})
            if document is not None:
                result = {
                    "host": document["host"],
                    "username": document["login"],
                    "password": document["password"],
                    "port": document["port"],
                    "extra": document["extra"]
                }
                return result
    except Exception as exception:
        print(exception)

    return result

def get_workflow_monitoring_connection(connection_id):
    """
    Retrieves connection details for monitoring workflows based on a connection ID.
    This function queries the MongoDB collection that stores monitoring workflow connection details 
    to fetch host, username, password, and other connection information for the specified connection ID.
    Args:connection_id (str): The unique identifier for the monitoring workflow connection.
    Returns:
        dict or None: A dictionary containing the connection details such as host, username, password, 
        port, and extra metadata, or None if not found or an error occurs.
    Raises:
        Exception: If the MongoDB connection or query fails.
    """
    result = None
    try:
        mongo_connection = get_mongodb_connection()
        if mongo_connection is not None and connection_id is not None:
            collection = mongo_connection[WORKFLOW_CONNECTION_MONITORING_COLLECTION]
            document = collection.find_one({"connId": connection_id}, {"connId": 0, "connType": 0})
            if document is not None:
                result = {
                    "host": document["host"],
                    "username": document["login"],
                    "password": document["password"],
                    "port": document["port"],
                    "extra": document["extra"]
                }
                if "database" in document and document["database"] is not None:
                    result["database"] = document["database"]
                return result
    except Exception as exception:
        print(exception)

    return result

def get_va_configuration_document(title, os_version):
    """
    Retrieves the VA configuration document based on the VA title and OS version.
    This function queries the MongoDB collection containing VA configurations and retrieves 
    the configuration document that matches the provided VA title and OS version.
    Args:
        title (str): The VA title to search for.
        os_version (str): The OS version to search for (regex search with case-insensitivity).
    Returns:dict or None: The VA configuration document if found, otherwise None.
    Raises:
        Exception: If the MongoDB query fails.
    """
    from zif_mongo_helper import get_single_document
    try:
        collection_name = "automation_va_configuration"
        search_filter = {"vaTitle": title, "osVersion": {"$regex": os_version, "$options": "i"}}
        document = get_single_document(collection_name, search_filter)
        if document is not None and len(document) > 0:
            result = document
        else:
            result = None
    except Exception as exception:
        print(exception)
    return result

def get_va_transaction_document(objectId: str):
    """
    """
    from zif_mongo_helper import get_single_document
    result = None
    try:
        today: datetime = datetime.today()
        month, year = today.strftime("%B"), today.year
        print(month, year)
        collection_name = "automation_va_transaction"
        search_filter = {"_id": ObjectId(objectId), 'status': 'New'}
        projection = {'_id': 0}
        document = get_single_document(collection_name, search_filter, projection)
        if document is not None and len(document) > 0:
            result = document
    except Exception as exception:
        print(exception)
    return result


def get_input_values_by_title(document_details: dict, title: str):
    """
    Retrieves input values from a document based on a specified title.
    Args:
        document_details (dict): The document that contains the input settings.
        title (str): The title of the input for which values are to be retrieved.
    Returns:list: A list of input values that match the specified title, or an empty list if no match is found.
    Raises:
        Exception: Logs any exceptions encountered during the processing.
    """
    try:
        input_values = []
        if document_details is not None:
            registry_inputs = document_details.get("inputSettings")
            for input_setting in registry_inputs:
                input_title = input_setting.get("title")
                if input_title == title:
                    input_values = input_setting.get("inputValues")
                    break
        return input_values
    except Exception as exception:
        print(exception)


def update_va_transaction_status(document_id: str, status: str, remarks: str, execution_date=None, rollback_params=None):
    """
    """
    from datetime import datetime
    from bson.objectid import ObjectId
    from zif_mongo_helper import upsert_single_document
    try:
        query = {"_id": ObjectId(document_id)}
        current_date_time = datetime.now()
        new_values = {'status': status, 'remarks': remarks, 'updatedDateTime': current_date_time}
        if execution_date is not None:
            new_values['workflowExecutionDateTime'] = execution_date
        if rollback_params is not None:
            new_values['rollbackParams'] = rollback_params
        upsert_single_document("automation_va_transaction", query, new_values)
    except Exception as exception:
        print(exception)


def insert_va_reboot_document(values: dict):
    """
    Inserts a new VA reboot document into the 'automation_va_transaction' MongoDB collection.
    Args:values (dict): The dictionary containing the values to insert into the new document.
    Returns:str: The unique identifier (_id) of the newly inserted document, or None if the insertion failed.
    Raises:
        Exception: Logs any exceptions encountered during the insertion operation.
    """
    result = None
    mongo_document = None
    from zif_mongo_helper import get_collection
    try:
        collection_name = "automation_va_transaction"
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, collection_name, values]):
            mongo_document = mongo_collection.insert_one(values)
        else:
            print("mongo collection or name none")
        if all([mongo_document, mongo_document.inserted_id]):
            result = mongo_document.inserted_id
        else:
            print("mongo document or id empty")
    except Exception as exception:
        print(exception)

    return result
