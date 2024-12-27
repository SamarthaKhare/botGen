
def is_empty(source):
	"""
	Checks if the given string `source` is empty or contains only whitespace characters.
	Args:source (str): The string to be checked for emptiness.
	Returns:bool: True if the `source` is None or empty after stripping whitespace, otherwise False.
	"""
	result = True
	if source is not None and len(source.strip()) > 0:
		result = False
	return result

def substring_by_text(source, start_text, end_text):

	"""
	Extracts a substring from `source` that lies between `start_text` and `end_text`.
	Args:
		source (str): The original string from which to extract the substring.
		start_text (str): The starting text to identify the beginning of the substring.
		end_text (str): The ending text to identify the end of the substring.
	Returns:str or None: The extracted and stripped substring if found, otherwise None.
	"""
	result = None
	if (not (is_empty(source) and is_empty(start_text) and is_empty(end_text))):
		start_index = source.index(start_text) + len(start_text)
		end_index = source.index(end_text, start_index)
		result = source[start_index:end_index]
		result = result.strip()
	return result

def substring_by_text_for_multiple(source, start_text, end_text):
	"""
	Extracts multiple substrings from `source` that are between `start_text` and `end_text`.
	Args:
		source (str): The original string from which to extract substrings.
		start_text (str): The text indicating the start of each substring.
		end_text (str): The text indicating the end of each substring.
	Returns:list or None: A list of extracted substrings if found, otherwise None.
	"""

	result = None
	if (not (is_empty(source) and is_empty(start_text) and is_empty(end_text))):
		result = list()
		tmp = source.split(start_text)
		for par in tmp:
			if end_text in par:
				result.append(par.split(end_text)[0])
	return result

def substring_by_line_pattern(source, search_pattern, is_replace=None):
	"""
	Searches each line of `source` for the `search_pattern` and optionally replaces it.
	Args:
		source (str): The multi-line string to search through.
		search_pattern (str): The pattern to search for in each line.
		is_replace (bool, optional): If True, replaces the `search_pattern` in matching lines with an empty string.
	Returns: list: A list of lines that contain the `search_pattern`. If `is_replace` is True, the pattern is removed.
	"""

	result = list()
	if all([source, search_pattern]):
		for line in source.split("\n"):
			if search_pattern in line and is_replace == True:
				result.append(line.replace(search_pattern, ""))
			elif search_pattern in line:	
				result.append(line)
	return result

def replace_string(source_text, find_pattern, replace_pattern):
	"""
	Replaces all occurrences of `find_pattern` in `source_text` with `replace_pattern`.
	Args:
		source_text (str): The text in which to perform the replacement.
		find_pattern (str): The substring to find and replace.
		replace_pattern (str): The substring to replace `find_pattern` with. If None, `find_pattern` is removed.
	Returns:str: The modified string with replacements made.
	"""
	if all([find_pattern, replace_pattern]):
		source_text = source_text.replace(find_pattern, replace_pattern)
	elif find_pattern is not None and replace_pattern is None:
		source_text = source_text.replace(find_pattern, '')

	return source_text

def substring_by_string_text(source, start_text, end_text):
	"""
	Extracts all substrings from `source` that are between `start_text` and `end_text`, and constructs a single concatenated string of these substrings.
	Args:
		source (str): The original string from which to extract substrings.
		start_text (str): The text indicating the start of each substring.
		end_text (str): The text indicating the end of each substring.
	Returns: str: A concatenated and formatted string of all extracted substrings.
   	"""
	result_data = []
	tmp = source.split(start_text)
	for par in tmp:
		if end_text in par:
			result_data.append(par.strip().split(end_text)[0])
	construct_string_result = "'{}'".format(result_data)
	result = construct_string_result.replace("'", "").replace(" ", "").strip()
	return result
