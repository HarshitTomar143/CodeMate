import os
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def run_python_file(working_directory: str, file_path: str, args= []):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: {file_path} is not in the working dir' 
    
    print("DEBUG abs_file_path:", abs_file_path)

    if not os.path.isfile(abs_file_path):
        return f'Error: {file_path} is not a file'

    if not file_path.endswith(".py"):
        return f'Error: {file_path} is not a Python file'
    
    try:
        final_args= ["python",file_path]
        final_args.extend(args)
        output = subprocess.run(
            final_args,
            cwd=abs_working_directory,
            timeout=30,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONUTF8": "1"} 
        )

        final_string = f"""
        STDOUT:{output.stdout}
        STDERR:{output.stderr}
"""

        if not output.stdout and not output.stderr:
            final_string += "No output from the script\n"

        if output.returncode != 0:
            final_string += f"Process exited with code {output.returncode}"

        return final_string

    except Exception as e: 
        return f"Error executing file {file_path}: {str(e)}"
