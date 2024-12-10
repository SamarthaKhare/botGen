import pymongo
import json
import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)

def get_connection():
    """
    Establishes and returns a MongoDB connection session using environment variables for the connection URL and database name.
    The function retrieves the MongoDB connection string (`MONGO_DB_URL`) and the database name (`ZIF_DB`) from environment variables.
    It then creates a client connection using the `pymongo.MongoClient` and selects the specified database.
    Returns:
        mongo_connection (pymongo.database.Database or None): A reference to the MongoDB database session if the connection is successful,
        otherwise None.
    Raises:
        Exception: If an error occurs while connecting to MongoDB, the exception will be caught and printed.
    """

    try:
        """
        MONGO_DB_URL=mongodb://zifwuser:zifwuser@172.27.130.5:27017,172.27.130.6:27017,172.27.130.7:27017/?authSource=admin&replicaSet=zif-rs&readPreference=secondaryPreferred&ssl=false
        ZIF_DB=zif
        """
        data_source = os.environ["MONGO_DB_URL"]
        database = os.environ["ZIF_DB"]
        mongo_client = pymongo.MongoClient(data_source)
        mongo_session = mongo_client[database]
        #print(mongo_session)
        if mongo_session is not None:
            return mongo_session
    except Exception as exception:
        print(exception)

    return mongo_session


def get_collection(collection_name):
    """
    Retrieves a specified MongoDB collection from the database.
    Args:collection_name (str): The name of the MongoDB collection to retrieve.
    Returns:mongo_collection (pymongo.collection.Collection or None): The MongoDB collection object if found, otherwise None.
    Raises:
        Exception: If an error occurs while retrieving the collection, the exception will be caught and printed.
    """
    mongo_collection = None
    try:
        mongo_connection = get_connection()
        #print(mongo_connection)
        #print(collection_name)
        if collection_name:
            mongo_collection = mongo_connection[collection_name]
    except Exception as exception:
        print(exception)

    return mongo_collection


def get_single_document(collection_name, query, projection=None):
    """
    Retrieves a single document from a specified MongoDB collection based on a query.
    Args:
        collection_name (str): The name of the MongoDB collection to query.
        query (dict): A MongoDB query to filter documents.
        projection (dict, optional): A projection to specify which fields to include or exclude. Defaults to None.
    Returns:mongo_document (dict or None): The first document that matches the query, or None if no match is found.
    Raises:
        Exception: If an error occurs while querying the document, the exception will be caught and printed.
    """
    mongo_document = None
    try:
        mongo_collection = get_collection(collection_name)
        if collection_name and query:
            if projection is not None:
                mongo_document = mongo_collection.find_one(query, projection)
            else:
                mongo_document = mongo_collection.find_one(query)
    except Exception as exception:
        print(exception)

    return mongo_document


def get_all_documents(query,collection_name='remediate_alerts',projection=None):
    """
    Retrieves all documents from a specified MongoDB collection based on a query.
    Args:
        query (dict): A MongoDB query to filter documents.
        projection (dict, optional): A projection to specify which fields to include or exclude. Defaults to None.
    Returns:mongo_documents (list or None): A list of documents that match the query, or None if no matches are found.
    """
    mongo_documents = None
    try:
        mongo_collection = get_collection(collection_name)
        #print(mongo_collection)
        if collection_name and query:
            if projection is not None:
                mongo_documents = list(
                    mongo_collection.find(query, projection))
            else:
                #print(query)
                mongo_documents = list(mongo_collection.find(query))

            if mongo_documents is None or len(mongo_documents) == 0:
                mongo_documents = None
    except Exception as exception:
        print(exception)

    return mongo_documents


def insert_single_document(collection_name, values):
    """
    Inserts a single document into a specified MongoDB collection.
    Args:
        collection_name (str): The name of the MongoDB collection to insert the document into.
        values (dict): The document to be inserted.
    Returns:result (bool): True if the document was successfully inserted, otherwise False.
    Raises:
        Exception: If an error occurs while inserting the document, the exception will be caught and printed.
    """
    result = False
    mongo_document = None

    try:
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, collection_name, values]):
            mongo_document = mongo_collection.insert_one(values)

        if all([mongo_document, mongo_document.inserted_id]):
            result = True
    except Exception as exception:
        print(exception)

    return result

def update_single_document(collection_name, query, new_values):
    """
    Updates a single document in a specified MongoDB collection based on the query.
    Args:
        collection_name (str): The name of the MongoDB collection where the document exists.
        query (dict): The filter used to select the document to update.
        new_values (dict): The new values to update the document with.
    Returns:result (bool): True if the document was successfully updated, otherwise False.
    Raises:
        Exception: If an error occurs while updating the document, the exception will be caught and printed.
    """
    result = False
    mongo_document = None
    try:
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, query, new_values]):
            set_values = {'$set': new_values}
            mongo_document = mongo_collection.update_one(query, set_values)

        if mongo_document is not None and mongo_document.modified_count > 0:
            result = True
    except Exception as exception:
        print(exception)

    return result


def update_all_documents(collection_name, query, new_values):
    """
    Updates multiple documents in a specified MongoDB collection based on the query.
    Args:
        collection_name (str): The name of the MongoDB collection where the documents exist.
        query (dict): The filter used to select the documents to update.
        new_values (dict): The new values to update the documents with.
    Returns:result (bool): True if any documents were successfully updated, otherwise False.
    e.g it uses the set command to upsert newvalues 
    """
    result = False
    mongo_document = None
    try:
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, query, new_values]):
            set_values = {'$set': new_values}
            mongo_document = mongo_collection.update_many(query, set_values)

        if mongo_document is not None and mongo_document.modified_count > 0:
            result = True
    except Exception as exception:
        print(exception)

    return result


def upsert_single_document(query,new_values,collection_name='remediate_alerts'):
    """
    Updates a single document if it exists, or inserts a new document if it does not (upsert) in a MongoDB collection.
    Args:
        query (dict): The filter used to select the document to update or insert.
        new_values (dict): The new values to update the document with.
    Returns:result (bool): True if the document was successfully upserted, otherwise False.
    e.g it uses $set command to set new values in the document like {'$set': new_values}
    """
    result = False
    mongo_document = None
    try:
        mongo_collection = get_collection(collection_name)
        if all([ query, new_values]):
            set_values = {'$set': new_values}
            print(set_values)  
            mongo_document = mongo_collection.update_one(query, set_values, upsert=True)
        if mongo_document is not None and mongo_document.modified_count > 0:
            result = True
    except Exception as exception:
        print(exception)

    return result


def upsert_all_documents(collection_name, query, new_values):
    """
    Updates multiple documents if they exist, or inserts new documents if they do not (upsert) in a MongoDB collection.
    Args:
        collection_name (str): The name of the MongoDB collection where the documents exist.
        query (dict): The filter used to select the documents to update or insert.
        new_values (dict): The new values to update the documents with.
    Returns:result (bool): True if the documents were successfully upserted, otherwise False.
    e.g it uses $set command to set new values in the document like {'$set': new_values}
    """
    result = False
    mongo_document = None
    try:
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, query, new_values]):
            set_values = {'$set': new_values}
            mongo_document = mongo_collection.update_many(
                query, set_values, upsert=True)

        if mongo_document is not None and mongo_document.modified_count > 0:
            result = True
    except Exception as exception:
        print(exception)

    return result


def aggregate_query(collection_name, query, projection=None, unwind=None, child_object=None):
    """
   
    """
    mongo_documents = None
    try:
        mongo_collection = get_collection(collection_name)
        if all([mongo_collection, collection_name, query]):
            if unwind == True:
                if projection is not None:
                    mongo_documents = list(mongo_collection.aggregate([{"$unwind": child_object}, query, {"$project": projection}]))
                else:
                    mongo_documents = list(mongo_collection.aggregate([{"$unwind": str(child_object)}, query]))
            else:
                if projection is not None:
                    mongo_documents = list(mongo_collection.aggregate([query, {"$project": projection}]))
                else:
                    mongo_documents = list(mongo_collection.aggregate([query]))
    except Exception as exception:
        print(exception)

    return mongo_documents


def get_value_by_field_name(collection_name, primary_key_field_name, field_value, specific_field_name):
    """
    Retrieves the value of a specific field from a document in a MongoDB collection based on the primary key.
    Args:
        collection_name (str): The name of the MongoDB collection to query.
        primary_key_field_name (str): The field name of the primary key used to match the document.
        field_value (str): The value of the primary key to filter the document.
        specific_field_name (str): The field name whose value needs to be retrieved.
    Returns:result (any or None): The value of the specific field if the document is found, otherwise None.
    Raises:
        Exception: If an error occurs while retrieving the field value, the exception will be caught and printed.
    """
    result = None
    try:
        mongo_connection = get_connection()
        if mongo_connection is not None:
            collection = mongo_connection[collection_name]
            document = collection.aggregate([{"$match": {primary_key_field_name: field_value}}, {"$project": {"_id": 0, specific_field_name: f"${specific_field_name}"}}])
            for index in document:
                result = index[specific_field_name]
    except Exception as exception:
        print(exception)

    return result
