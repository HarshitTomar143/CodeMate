import os 
from google.generativeai import types

def write_file(working_directory, file_path, content):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path= os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: {file_path} is not in the working dir' 
    
    parent_dir= os.path.dirname(abs_file_path)

    if not os.path.isdir(parent_dir):
        try:
            os.makedirs(parent_dir)

        except Exception as e:
            return f'Error creating directories for {file_path}: {str(e)}'

    if not os.path.isfile(abs_file_path):
        pass
        
    try:
        with open(abs_file_path, "w") as f:
            f.write(content)
        return f'Success: Wrote to file {file_path}'
    except Exception as e:
        return f'Error writing to file {file_path}: {str(e)}'    
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Overwrites an existing file or writes to a new file if it doesn't exist(and creates required parent directory ), constrained to the working directory .",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The file path to write to, from the working directory.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file as string .",
            },
        },
        "required": [],
    },
)    