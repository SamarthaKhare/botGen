from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests
import json
import jwt
import ssl
import os
from dotenv import load_dotenv
dir=os.path.dirname(os.path.abspath(__file__))
dotenv_path = f"{dir}/../../.env"
load_dotenv(dotenv_path=dotenv_path)
from zif_workflow_helper import get_workflow_config_value
tokenExpiryTime = 86400

def get_access_token():
    """
    Generates a JWT access token using a private key.
    This function reads a private key from a file, uses it to sign a JWT token, 
    and returns the signed token. The token is generated with an expiration claim 
    and the username claim, which is fetched from the environment variable `GATEWAY_SERVICE`.
    Returns:
        str: A signed JWT token as a string.
    Raises:
        Exception: If there are any issues with reading the private key or generating the token.
    """
    with open('/opt/airflow/dags/jwt-zif-access-key.private.pem', 'rb') as fh:
        signing_key = serialization.load_pem_private_key(
            fh.read(),
            password=None,
            backend=default_backend()
        )
    token_expiry_time = jwt.encode({'username': os.environ['GATEWAY_SERVICE']}, signing_key, algorithm='RS256')
    result = token_expiry_time
    return result


def send_email(payload):
    """
    Sends an email using a configured email service.
    This function prepares the payload for sending an email, including adding the sender email address 
    and email template name from workflow configuration. It generates an access token, constructs the 
    request, and sends the email using a POST request to the email service API. The request is sent over 
    an SSL connection, which may bypass SSL verification depending on the context configuration.
    Args:
        payload (dict): A dictionary containing the email details (subject, recipients, body, etc.).
    Returns:
        str: "SUCCESS" if the email is sent successfully, otherwise None.
    Raises:
        Exception: If an error occurs during the process of sending the email.
    """
    result = None
    try:
        if payload is not None:
            payload["from"] = get_workflow_config_value("SENDER_EMAIL_ADDRESS")
            payload["templateName"] = get_workflow_config_value("EMAIL_TEMPLATE_NAME")
            payload["mailData"] = {"mailBody": payload["mailData"]}
            
            ssl._create_default_https_context = ssl._create_unverified_context
            request_header = get_access_token()
            headers = {"Authorization": "Bearer {}".format(request_header), "Content-Type": "application/json"}
            
            base_resource = os.environ["ZIF_GATEWAY_URL"]
            endpoint = get_workflow_config_value("EMAIL_SERVICE_ENDPOINT")
            api_resource = "{}{}".format(base_resource, endpoint)
            
            response = requests.post(api_resource, data=json.dumps(payload), headers=headers, verify=False)
            if response is not None and response.status_code == 200:
                result = "SUCCESS"
    except Exception as exception:
        print(exception)

    return result
