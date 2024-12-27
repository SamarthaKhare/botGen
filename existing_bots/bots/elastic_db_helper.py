from elasticsearch7 import Elasticsearch, helpers
from datetime import datetime
import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
from mongo_db_helper import MongoHelper

class ElasticSearchHelper(MongoHelper):

    def __init__(self, es_index, mongo_collection, **kwargs) -> None:
        """
        Initializes the Elasticsearch and MongoDB connector class.
        Args:
            es_index (str): The name of the Elasticsearch index to be used.
            mongo_collection (str): The MongoDB collection to interact with.
            **kwargs: Additional arguments passed to the parent class initializer.
        Attributes:
            es_client: The Elasticsearch client object.
            es_index (str): The Elasticsearch index name.
            mongo_collection (str): The MongoDB collection name.
        Raises:
            Exception: If an error occurs while initializing the Elasticsearch client or other attributes.
        """
        super().__init__(**kwargs)
        self.es_client = None
        try:
            self.es_client = self.get_es_client()
            self.es_index = es_index
            self.mongo_collection = mongo_collection
        except Exception as exception:
            print(exception)


    def get_es_client(self):
        """
        Creates and returns an Elasticsearch client by connecting to Elasticsearch.
        Returns:Elasticsearch: A client object to interact with the Elasticsearch cluster.
        Raises:
            Exception: If connection to Elasticsearch fails, the exception is caught and an error message is printed.
        """
        from zif_workflow_helper import get_workflow_connection
        es_client = None
        try:
            connection_details = get_workflow_connection("ELASTICSEARCH")
            if connection_details:
                es_client = Elasticsearch(
                    [connection_details['host']],
                    http_auth=(connection_details['username'], connection_details['password']),
                    scheme="http",
                    port=connection_details['port']
                )
        except Exception as e:
            print(f"Failed to connect to Elasticsearch: {str(e)}")
        return es_client


    def is_index_exists(self, index_name: str) -> bool:
        """
        Checks if the specified index exists in Elasticsearch.
        Args:index_name (str): The name of the Elasticsearch index to check
        Returns:bool: True if the index exists, False otherwise.
        Raises:
            Exception: If an error occurs while checking the existence of the index, the exception is caught and logged.
        """
        result = False
        try:
            if index_name and self.es_client:
                result = self.es_client.indices.exists(index=index_name)
        except Exception as e:
            print(f"An error occurred while checking index existence: {str(e)}")
        return result


    def is_document_exists(self, doc_id: str) -> bool:
        """
        Checks if a document with the specified ID exists in the Elasticsearch index.
        Args:doc_id (str): The ID of the document to check.
        Returns:bool: True if the document exists, False otherwise.
        Raises:
            Exception: If an error occurs while checking the existence of the document, the exception is caught and logged.
        """
        result = False
        try:
            if all([self.es_index, doc_id, self.es_client]):
                if self.is_index_exists(self.es_index):
                    result = self.es_client.exists(index=self.es_index, id=doc_id)
                else:
                    print(f"{self.es_index=} does not exist")
        except Exception as e:
            print(f"An error occurred while checking document existence: {str(e)}")
        return result


    def parse_field(self, value, data_type):
        """
        Parses the given value into the specified data type.
        Args:
            value: The value to be parsed.
            data_type (str): The type to which the value should be parsed.Supported types are 'date', 'int', 'bool', and 'str'.
        Returns:
            The parsed value, cast to the specified data type. If an exception occurs, the original value is returned.
        Raises:
            Exception: If an error occurs during parsing, the exception is caught and logged.
        """
        try:
            if data_type == 'date':
                return datetime.strptime(value, "%Y-%m-%d").isoformat() if isinstance(value, str) else value.isoformat()
            elif data_type == 'int':
                return int(value)
            elif data_type == 'bool':
                return bool(value)
            elif data_type == 'str':
                return str(value)
            else:
                return value 
        except Exception as exception:
            print(exception)
            return value


    def insert_single_phishing_document(self, doc_id: str):
        """
        Inserts a phishing document into the Elasticsearch index by retrieving it from MongoDB.
        Args:doc_id (str): The ID of the phishing document to insert.
        Returns:None
        Raises:
            Exception: If an error occurs during the insertion process, the exception is caught and logged.
        """
        from zif_workflow_helper import get_workflow_config_value
        from bson import ObjectId
        try:
            config_key = "ES_" + self.es_index
            config = get_workflow_config_value(config_key)
            if all([self.es_client, config, self.is_index_exists(self.es_index)]):
                fields_config = config['fields']
                query = {"_id": ObjectId(doc_id)}
                mongo_doc = self.get_single_document(self.mongo_collection, query , {"observableVerdict": 0})
                if not mongo_doc:
                    print(f"Document with ID {doc_id} not found in MongoDB.")
                    return

                actions = self.split_and_create_actions(mongo_doc, fields_config)
                
                try:
                    helpers.bulk(self.es_client, actions)
                    print(f"Phishing document {doc_id} successfully inserted into Elasticsearch.")
                except Exception as e:
                    print(f"Error inserting phishing document into Elasticsearch: {str(e)}")

        except Exception as e:
            print(f"Error in insert_phishing_document: {str(e)}")

    def split_and_create_actions(self, mongo_doc, fields_config):
        """
        Splits a MongoDB document into multiple actions for bulk insertion into Elasticsearch.
        Args:
            mongo_doc (dict): The original MongoDB document.
            fields_config (dict): A configuration mapping that defines the data type for each field in the document.
        Returns:
            list: A list of actions, where each action represents a single document to be inserted into Elasticsearch.
            Each action includes the parsed fields and a unique ID for the document.  
        Raises:
            Exception: Any exception during parsing or processing of the document is implicitly caught and logged.
        """
        actions = []
        verdict_reports = mongo_doc.get('verdictReport', [])
        
        mongo_doc.pop("_id")
        for report in verdict_reports:
            new_doc = {
                **{key: mongo_doc.get(key) for key in mongo_doc if key != 'verdictReport'},
                "verdictReport": report
            }

            parsed_doc = {
                key: self.parse_field(new_doc.get(key), fields_config[key])
                if key in fields_config else new_doc.get(key)
                for key in new_doc
            }
            if 'verdictReport' in parsed_doc:
                parsed_doc['verdictReport'] = {
                    key: self.parse_field(report.get(key), fields_config[f'verdictReport.{key}'])
                    for key in report if f'verdictReport.{key}' in fields_config
                }

            action = {
                "_index": self.es_index,
                "_id": str(uuid.uuid4()),  # Generate a new unique ID
                "_op_type": 'index',
                "_source": parsed_doc
            }
            actions.append(action)
        
        return actions


    def insert_single_document(self, doc_id: str):
        """
        Inserts a single MongoDB document into Elasticsearch by retrieving it based on the document ID.
        Args:doc_id (str): The ID of the MongoDB document to be inserted into Elasticsearch.
        Returns:None
        Raises:
            Exception: If an error occurs during the retrieval from MongoDB or insertion into Elasticsearch,the exception is caught and logged.
        """
        from zif_workflow_helper import get_workflow_config_value
        from bson import ObjectId
        try:
            config_key = "ES_" + self.es_index
            config = get_workflow_config_value(config_key)
            if all([self.es_client, config, self.is_index_exists(self.es_index)]):
                fields_config = config['fields']
                query = {"_id": ObjectId(doc_id)}
                print(query)
                mongo_doc = self.get_single_document(self.mongo_collection, query)
                print(mongo_doc)
                if not mongo_doc:
                    print(f"Document with ID {doc_id} not found in MongoDB.")
                    return

                parsed_doc = {
                    key: self.parse_field(mongo_doc.get(key), fields_config[key])
                    for key in fields_config if key in mongo_doc
                }

                action = {
                    "_index": self.es_index,
                    "_id": str(mongo_doc["_id"]),
                    "_op_type": 'index',
                    "_source": parsed_doc
                }

                try:
                    self.es_client.index(index=self.es_index, id=action["_id"], body=action["_source"])
                    print(f"Document {doc_id} successfully inserted into Elasticsearch.")
                except Exception as e:
                    print(f"Error inserting document into Elasticsearch: {str(e)}")

        except Exception as e:
            print(f"Error in insert_single_document: {str(e)}")

