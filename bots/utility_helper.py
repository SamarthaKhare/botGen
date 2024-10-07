'''
def remove_spaces(value):
    """
    Removes leading and trailing spaces from a given value.
    Args:value: The value to remove spaces from. Can be a string, list, or dictionary.
    Returns:
        The value with spaces removed. If the value is a string, leading and trailing spaces are removed.
        If the value is a list or dictionary, the function recursively calls itself to remove spaces from each element.
        If the value is not a string, list, or dictionary, it is returned unchanged.
    """
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return [remove_spaces(item) for item in value]
    elif isinstance(value, dict):
        return {key: remove_spaces(value) for key, value in value.items()}
    else:
        return value
'''
