from cryptography.fernet import Fernet
key = Fernet.generate_key()
fernet = Fernet(key)

def encrypt(value):
    """
    Encrypts the given value using the Fernet encryption algorithm.
    Parameters:
    value (str): The string to be encrypted.
    Returns:
    str: The encrypted value as a string, or None if an error occurs.
    """
    result = None
    if value:
        try:
            result = fernet.encrypt(bytes(value, 'utf-8')).decode()
        except Exception as exception:
            print(exception)
    return result

def decrypt(value):
    """
    Decrypts the given value using the Fernet encryption algorithm.
    Parameters:
    value (str): The encrypted string to be decrypted.
    Returns:
    str: The decrypted value as a string, or None if an error occurs.
    """
    result = None
    if value:
        try:
            result = fernet.decrypt(bytes(value, 'utf-8')).decode()
        except Exception as exception:
            print(exception)
    return result
