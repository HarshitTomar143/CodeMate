import os
from google.generativeai import types

from config import MAX_CHARS

def get_file_content(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path= os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: {file_path} is not in the working dir' 
    
    if not os.path.isfile(abs_file_path):
        return f'Error: {file_path} is not a file'

    file_content_string="" 
    try:
        with open(abs_file_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if len(file_content_string) >= MAX_CHARS:
                file_content_string += (
                    f" File: {file_path} [Truncated: File content exceeds maximum character limit]"
                )
        return file_content_string

    except Exception as e:
        return f'Error reading file {file_path}: {str(e)}'    
    
schema_get_files_content = types.FunctionDeclaration(
    name="get_files_content",
    description="Gets the content of the given file as a string , constrained to the working directory.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file, from the working directory.",
            },
        },
        "required": [],
    },
)    