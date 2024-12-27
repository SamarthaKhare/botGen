import os
import sys
import pymssql
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)


class SQLFeed(object):
    sql_db_connection = None
    error_message = "Error: {}"

    def __init__(self, tds_version=None):
        """
        Initializes a connection to a SQL Server database using the given TDS version.
        Parameters:
        - tds_version (str, optional): The TDS version to use for the connection. If None, the default version is used.
        Raises:
        Exception: If the connection to the database cannot be established.
        """
        server, database, username, password = [None]*4
        try:
            from zif_workflow_helper import get_workflow_connection

            connection_attributes = get_workflow_connection("SQLSERVICEREMEDIATEACCOUNT")
            if connection_attributes is not None:
                server = connection_attributes["host"]
                database = connection_attributes["database"]
                username = connection_attributes["username"]
                password = connection_attributes["password"]
            
            if all([server, database, username, password]):
                if tds_version is not None:
                    self.sql_db_connection = pymssql.connect(host = server, database = database,
                        user = username, password = password, tds_version = tds_version)
                else:
                    self.sql_db_connection = pymssql.connect(host = server, database = database, 
                        user = username, password = password)
                    
        except Exception as exception:
            self.sql_db_connection = None
            print(self.error_message.format(exception))

    @property
    def connection(self):
        """
        Retrieves the active database connection.
        Returns:
        pymssql.Connection: The active connection object to the SQL Server database.
        """
        return self.sql_db_connection
        
    def get_command_result(self, command_text):
        """
        Executes a given SQL command and returns the result as a list of dictionaries.
        Parameters:
        - command_text (str): The SQL command to be executed.
        Returns:
        list or None: A list of dictionaries where each dictionary represents a row in the result set.
        Returns None if no results are found or an error occurs.
        Raises:
        Exception: If there is an error executing the command or processing the results.
        """
        result = []
        try:
            if all([self.connection, command_text]):
                with self.connection.cursor() as cursor:
                    cursor.execute(command_text)
                    for row_item in cursor:
                        column_list = {}
                        for field_name, field_value in zip(cursor.description, row_item):
                            column_list[field_name[0]] = field_value
                        result.append(column_list)

        except Exception as exception:
            print(self.error_message.format(exception))
        if type(result is list) and len(result) == 0:
            result = None
        return result

    def modify_db_data(self, command_text):
        """
        Executes a SQL command that modifies data in the database (INSERT, UPDATE, DELETE).
        Parameters:
        - command_text (str): The SQL command to be executed.
        Returns:
        int: The number of rows affected by the command. Returns -1 if an error occurs.
        Raises:
        Exception: If there is an error executing the command.
        """
        try:
            if self.connection is not None:
                with self.connection.cursor() as cursor:
                    cursor.execute(command_text)
                    rows_affected = cursor.rowcount
                    self.connection.commit()
                    return rows_affected
                
        except Exception as exception:
            print(self.error_message.format(exception))
        return -1

    def update_record(self, table_name, update_values, condition):
        """
        Updates records in a specified table based on the provided condition.
        Parameters:
        - table_name (str): The name of the table where the records will be updated.
        - update_values (dict): A dictionary containing the column names and their new values.
        - condition (str): A SQL condition string to specify which records to update.
        Returns:
        int: 1 if the update is successful, -1 if no records were updated, and 0 if an error occurs.
        Raises:
        Exception: If there is an error during the update process.
        """
        try:
            if all([self.connection, table_name, update_values, condition]):
                where_condition = f"{condition} AND {' AND '.join([f'{key}={value}' for key, value in update_values.items()])}"
                select_query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_condition}"
                with self.connection.cursor() as cursor:
                    cursor.execute(select_query)
                    row_count = cursor.fetchone()[0]
                if row_count > 0:
                    return -1
                else:
                    update_str = ', '.join([f"{key}={value}" for key, value in update_values.items()])
                    command_text = f"UPDATE {table_name} SET {update_str} WHERE {condition}"
                    rows_affected = self.modify_db_data(command_text)
                    if rows_affected > 0:
                        return 1
                    else:
                        return -1
                    
        except Exception as exception:
            print(self.error_message.format(exception))
        return 0

    def insert_record(self, table_name, data_values):
        """
        Inserts a new record into the specified table in the database.
        Args:
            table_name (str): The name of the table where the new record should be inserted.
            data_values (dict): A dictionary containing the field names and their corresponding values to be inserted.
        Returns:
            int: Returns 1 if the record was successfully inserted, -1 if the insertion failed, and 0 if there was an error.
        Raises:
            Exception: If an error occurs during the insertion process, the exception will be caught and printed.
        """
        try:
            if self.connection and table_name and data_values is not None:
                field_list = ', '.join(data_values.keys())
                value_list = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in data_values.values()])
                if value_list: 
                    command_text = f"INSERT INTO {table_name} ({field_list}) VALUES ({value_list})"
                    if self.modify_db_data(command_text):  
                        return 1
                    else:
                        return -1
                        
        except Exception as exception:
            print(self.error_message.format(exception))
        return 0


def delete_record(self, table_name, condition):
    """
    Deletes a record from the specified table in the database based on a condition.
    Args:
        table_name (str): The name of the table from which the record should be deleted.
        condition (dict): A dictionary containing the conditions to identify the record(s) to delete.The keys are the column names, and the values are the corresponding values to match.
    Returns:
        int: Returns 1 if the record was successfully deleted, -1 if the deletion failed, and 0 if there was an error.
    Raises:
        Exception: If an error occurs during the deletion process, the exception will be caught and printed.
    """
    try:
        if all([self.connection, table_name, condition]):
            where_clause = " AND ".join([f"{key} = '{value}'" for key, value in condition.items()])
            command_text = f"DELETE FROM {table_name} WHERE {where_clause}"
            rows_affected = self.modify_db_data(command_text)
            self.connection.commit()
            if rows_affected > 0:
                return 1
            else:
                return -1
                
    except Exception as exception:
        print(self.error_message.format(exception))
    return 0
