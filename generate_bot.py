import os
import re
import logging
from torch.nn.functional import softmax
import json
from vertexai.generative_models import GenerativeModel, GenerationConfig
from datetime import datetime
import pandas as pd
from system_variable import system_prompt,response_schema,system_prompt_basic
import pickle
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Google Cloud credentials (consider more secure methods than environment variables)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'emerald-bastion-433109-e0-fb7a9d5222ab.json'
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
model = RobertaForSequenceClassification.from_pretrained("./query_utils/fine_tuned_model")
tokenizer = RobertaTokenizer.from_pretrained("./query_utils/fine_tuned_model")
label_mapping = {0: ["ServiceRestartRemediation","short_descriptionLIKEcheck for service restart"], 1: ["PingResponseRemediation","short_descriptionLIKEhost not responding"],2:["CPUMemoryResourceRemediation","short_descriptionLIKEcpu has high resource usage"],3:'backup'}

def get_class(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = softmax(logits,dim=1)
    max_prob = torch.max(probabilities, dim=1)
    print(probabilities)
    print(max_prob)
    if max_prob[0][0] < 0.9:
        print("No label found")
        return "No label found"
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    print("Predicted filter:", label_mapping[predicted_label])
    return label_mapping[predicted_label]

def generate_function_code(instruction: str, df: pd.DataFrame,incident_filter,model_name: str = "gemini-1.5-pro", top_n: int = 5) -> dict:
    from  utils.helper import find_relevant_helpers
    try:
        model = GenerativeModel(model_name, system_instruction=system_prompt)
        logger.info("GenerativeModel created successfully")
        relevant_functions = find_relevant_helpers(instruction,df, top_n)  
        print(relevant_functions)
        logger.info(f"Found {len(relevant_functions)} relevant functions")
        instruction=f"incident_filter={incident_filter}"+" "+","+" "+instruction 
        context = "Use these following relevant helper functions to create a function code:\n\n"
        for _, func in relevant_functions.iterrows():
            code_string = func['function_code'] #Access using column name
            #functionName_parameters = re.search(r"def\s+(\w+)\s*\(", code_string).group(1) #Extract function name using regex
            match = re.search(r'"""(.*?)"""', code_string, re.DOTALL)
            func_detail = match.group(1).strip() if match else ""
            context += f"Function name: {func['function_name']}\nFilepath: {func['filepath']}\n" #Access using column names
            if func_detail:
                context += f"\nFunction details:\n{func_detail}\n\n"
        prompt = f"""
        Create a detailed executable python function without any arguments based on the below instruction : 
        {instruction}
        Guidelines for Function Creation:
        [Important] Use incident_filter and workflow_name as provided in the instructions.
        1-Retrieve Incidents:Import and use the search_incident function from utility_helper.py, providing incident_filter as input to get a list of all ServiceNow incidents matching the filter.
        2-Iterate Through Incidents:
            For each incident in the list:
            a-Import and use function work_in_progress(input is device configuration and workflow name) from utility_helper.py and update the state of incident to Work in Progress.Funtion return true is update is successful else false
            b.Import and use the get_workflow_payload function from utility_helper.py, passing the incident as input. This function will 
            return a dictionary (device configuration) containing required fields such as device_name, alert_type, service_name, threshold_value, etc.
            b-Check Device Reachability:Import and use the is_device_reachable function from utility_helper.py, providing the device configuration 
            and workflow name as input if it returns the reachable status as Success, proceed with the next steps in the instructions else terminate.
            *Device unreachablity is handled internally. 
            c-Only perform the tasks mentioned in user's instruction. 
            d-To get the payload for updating the ticket import and use get_incident_payload(status,device configuration and process_result=None as its input) from utility_helper.py.
             Process_result is used for specific ask of user 
            e-To update the incident ticket use the update_incident(device configuration and payload as input) from servicenow.py 
        Below are some relevant function understand them use whichever needed
        {context}
        Key Points:
            Import the functions used in the code and do not assume anything beyond the given context.
            Process result 
            Avoid Syntax Errors
        """
        generation_config = GenerationConfig(
            temperature=0.2,
            top_p=0.2,
            top_k=2,
            max_output_tokens=6000,
            response_mime_type="application/json",
            response_schema=response_schema
        )
        logger.info("Sending request to the model")
        response = model.generate_content(prompt, generation_config=generation_config)
        logger.info("Response received from the model")
        response_json = json.loads(response.text)
        return response_json

    except Exception as e:
        logger.error(f"Error generating function code: {e}")
        return {} # Return an empty dictionary to indicate failure



if __name__ == "__main__":
    user_query=\
"""
 install software on windows machine
"""
    
    #label=get_class(user_query)
    label=['InstallSoftware','check']
    incident_filter=label[1]
    workflow_name=label[0]
    os.environ["WORKFLOW_NAME"]=str(workflow_name)
    str=f"workflow_name={workflow_name}"
    instruction = str+" "+user_query
    with open('dataframe.pkl', 'rb') as f:
        df = pickle.load(f)
    response_json = generate_function_code(instruction, df,incident_filter)
    code = response_json.get("function_code", "")
    function_name = response_json.get("function_name", "generated_function")
    dir_path = os.path.dirname(os.path.abspath(__file__))
    save_path=os.path.join(dir_path, "existing_bots", "bots", f"latest_{label[0]}.py")
    if code:
        try:
            with open(save_path, "w") as f:
                f.write(code)
            logger.info(f"Function code saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving function code: {e}")
    else:
        logger.warning("No code was generated.")
