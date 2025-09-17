from functions.get_files_info import  get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from google.generativeai import types


working_directory = "calculator"

def call_function(function_call_part, verbose=False):
    if verbose:
        print("Function call part:", function_call_part)
    else:
        print("Function call:", function_call_part.name)

    result= ""    

    if function_call_part.name == "get_files_info":
        result = get_file_content(working_directory, **function_call_part.args)

    if function_call_part.name == "get_file_content":
        result = get_file_content(working_directory, **function_call_part.args)

    if function_call_part.name == "run_python_file":
        result = run_python_file(working_directory, **function_call_part.args)

    if function_call_part.name == "write_file":
        result = write_file(working_directory, **function_call_part.args)    

    if result == "":            

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name= function_call_part.name,
                    response={"error": f"Unknown Function: {function_call_part.name}"},
                )
            ]
        ) 

    return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name= function_call_part.name,
                    response={"result: ",result},
                )
            ]
        )              