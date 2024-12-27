import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils.helper import generate_embeddings
import os
import git
import shutil
import pandas as pd
from pathlib import Path
import stat
import re
import pickle
import subprocess
DEF_PREFIXES = ['def ', 'async def ']
NEWLINE = '\n'
from pathlib import Path

def get_details(df):
    df['func_details']=None
    for idx, func in df.iterrows():
        code_string = func['function_code'] #Access using column name
        #functionName_parameters = re.search(r"def\s+(\w+)\s*\(", code_string).group(1) #Extract function name using regex
        match = re.search(r'"""(.*?)"""', code_string, re.DOTALL)
        func_detail = match.group(1).strip() if match else ""
        if func_detail=="":
            func_detail="ignore"
        df.at[idx, 'func_details'] = func_detail


def clone_github_repo(repo_url, folder_name,local_path):
    # Clone the repository into a local directory
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    os.chmod(local_path, 0o777) 
    git.Repo.clone_from(repo_url, local_path)
    
    # Check if the folder exists in the cloned repo
    folder_path = os.path.join(local_path, folder_name)
    
    if os.path.exists(folder_path):
        print(f"Folder '{folder_name}' has been cloned successfully.")
        return folder_path
    else:
        print(f"Folder '{folder_name}' not found in the repository.")
        return None

def get_function_name(code):
    """
    Extract function name from a line beginning with 'def' or 'async def'.
    """
    for prefix in DEF_PREFIXES:
        if code.startswith(prefix):
            return code[len(prefix): code.index('(')]


def get_until_no_space(all_lines, i):
    """
    Get all lines until a line outside the function definition is found.
    """
    ret = [all_lines[i]]
    for j in range(i + 1, len(all_lines)):
        if len(all_lines[j]) == 0 or all_lines[j][0] in [' ', '\t', ')']:
            ret.append(all_lines[j])
        else:
            break
    return NEWLINE.join(ret)


def get_functions(filepath):
    """
    Get all functions in a Python file.
    """
    with open(filepath, 'r') as file:
        all_lines = file.read().replace('\r', NEWLINE).split(NEWLINE)
        for i, l in enumerate(all_lines):
            for prefix in DEF_PREFIXES:
                if l.startswith(prefix):
                    code = get_until_no_space(all_lines, i)
                    function_name = get_function_name(code)
                    yield {
                        'function_code': code,
                        'function_name': function_name,
                        'filepath': filepath,
                    }
                    break


def extract_functions_from_repo(code_root):
    """
    Extract all .py functions from the repository.
    """
    print("code_root",code_root)
    code_files = list(code_root.glob('**/*.py'))
    print("code files",code_files)

    num_files = len(code_files)
    print(f'Total number of .py files: {num_files}')

    if num_files == 0:
        print('Verify openai-python repo exists and code_root is set correctly.')
        return None

    all_funcs = [
        func
        for code_file in code_files
        for func in get_functions(str(code_file))
    ]

    num_funcs = len(all_funcs)
    print(f'Total number of functions extracted: {num_funcs}')
    return all_funcs


def process_dataframe(df: pd.DataFrame, code_root: str) -> pd.DataFrame:
    # Create a new column for embeddings
    df['code_embedding'] = None
    
    # Process each row individually
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        try:
            # Generate embedding for the current row's code
            if df['func_details'] is not None:
                embedding = generate_embeddings(row['func_details'])
                df.at[index, 'code_embedding'] = embedding  # Store the embedding in the DataFrame
        except Exception as e:
            print(row['function_name'])
            print(f"Error processing row {index}: {e}")
            df.at[index, 'code_embedding'] = None  # Handle errors by setting None
    
    # Process filepath to be relative to the given code root
    df['filepath'] = df['filepath'].map(lambda x: str(Path(x).relative_to(code_root)))
    
    return df

def obfuscate_files_in_folder(folder_path, output_folder):
    for filename in os.listdir(folder_path):
        if filename.endswith(".py"):
            file_path = os.path.join(folder_path, filename)
            obfuscate_code_with_pyarmor(file_path, output_folder)

def obfuscate_code_with_pyarmor(file_path, output_folder):
    # Ensure the output folder exists and has write permissions
    try:
        subprocess.run(["pyarmor", "gen", "-O", output_folder, file_path],check=True)
        print(f"File '{file_path}' obfuscated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error obfuscating '{file_path}': {e}")


# Main execution
if __name__ == "__main__":
    repo_url = 'https://github.com/SamarthaKhare/botGen.git'  
    folder_name = 'bots'  
    local_path='D:/samartha.khare/Desktop/back-up/function_details/existing_bots'
    code_root = Path(clone_github_repo(repo_url, folder_name,local_path))
    obs_folder='D:/samartha.khare/Desktop/back-up/function_details/existing_bots/bots'
    if code_root:
        # Extract functions and process embeddings
        all_funcs = extract_functions_from_repo(code_root)
        df = pd.DataFrame(all_funcs)
        get_details(df)
        processed_df = process_dataframe(df, code_root)
        os.chmod(local_path+'/bots', 0o777) 
        #obfuscate_files_in_folder(local_path+'/bots',obs_folder)
        with open('dataframe.pkl', 'wb') as f:
            pickle.dump(df, f)
        #print(processed_df['code_embedding'][0].dtype)
        processed_df.to_csv("data/code_search_openai-python.csv", index=False)
        print("Processed data saved to data/code_search_openai-python.csv")
