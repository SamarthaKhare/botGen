import subprocess
import os
def obfuscate_file(file_path, output_folder):
    """Obfuscates a Python file using PyArmor.

    Args:
        file_path (str): Path to the Python file to be obfuscated.
        output_folder (str): Path to the output folder for the obfuscated file.

    Returns:
        None
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    try:
        subprocess.run(
            ["pyarmor", "gen", "-O", output_folder, file_path],
            check=True
        )
        print(f"File '{file_path}' obfuscated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error obfuscating '{file_path}': {e}")

# Replace with your file path and output folder
file_path = "D:/samartha.khare/Desktop/function_details/pyarmor_test.py"
output_folder = "obfuscated_files"

obfuscate_file(file_path, output_folder)