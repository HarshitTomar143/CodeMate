from functions.get_files_info import  get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file


working_directory = "."

def call_function(function_call_part, verbose=False):
    if verbose:
        print("Function call part:", function_call_part)
    else:
        print("Function call:", function_call_part.name)

    result = ""    

    if function_call_part.name == "get_files_info":
        result = get_files_info(working_directory, **function_call_part.args)

    elif function_call_part.name == "get_files_content":
        result = get_file_content(working_directory, **function_call_part.args)

    elif function_call_part.name == "run_python_file":
        result = run_python_file(working_directory, **function_call_part.args)

    elif function_call_part.name == "write_file":
        result = write_file(working_directory, **function_call_part.args)    

    if result == "":            
        return f"Error: Unknown Function: {function_call_part.name}"

    return result              