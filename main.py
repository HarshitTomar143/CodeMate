import os
import sys
import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_files_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


def print_response(resp):
    """Safely print model responses (handles text vs function calls)."""
    if not resp.candidates:
        print("No response candidates.")
        return

    parts = resp.candidates[0].content.parts
    for part in parts:
        if hasattr(part, "function_call") and part.function_call:
            print("Function Call Detected:", part.function_call)
        elif hasattr(part, "text") and part.text:
            print("Model:", part.text)


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    # Configure Gemini client
    genai.configure(api_key=api_key)

    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, you may call the appropriate function.
        Available operations:
        - get_files_info: List files and directories in the working directory or in sub-directories.
        - get_files_content: Reads the content of the file in the working directory.
        - write_file: Writes to the file(creates or update)
        - run_python_file: Run the python file with optional arguments
    """

    # History persistence file
    history_file = "chat_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                messages = json.load(f)
            except json.JSONDecodeError:
                messages = []
    else:
        messages = []

    # Register tools
    available_functions = types.Tool(
        function_declarations=[schema_get_files_info,
                               schema_write_file,
                               schema_get_files_content,
                               schema_run_python_file,
                               ]
    )

    # Pick the model
    model = genai.GenerativeModel(
        "gemini-2.0-flash-001",
        system_instruction=system_prompt,
    )

    # Start chat with history
    chat = model.start_chat(history=messages)

    # Get prompt from CLI
    if len(sys.argv) < 2:
        print("I need a prompt as a command line argument.")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    verbose_flag = len(sys.argv) == 3 and sys.argv[2] == "--verbose"

    # Add user message
    messages.append({"role": "user", "parts": [prompt]})

    # Send message (tools passed directly for your SDK)
    response = chat.send_message(prompt, tools=[available_functions])
    print_response(response)

    # Handle function calls
    if response.candidates:
        parts = response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, "function_call") and part.function_call:
                fn_name = part.function_call.name
                fn_args = {k: v for k, v in part.function_call.args.items()}

                print("Executing:", fn_name, fn_args)

                if fn_name == "get_files_info":
                    result = get_files_info(os.getcwd(), **fn_args)
                    print("Function Result:\n", result)

                    # Send result back to the model
                    follow_up = chat.send_message(f"Function result:\n{result}")
                    print_response(follow_up)

    # Save plain text replies only
    if response.candidates:
        parts = response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, "text") and part.text:
                messages.append({"role": "model", "parts": [part.text]})

    with open(history_file, "w") as f:
        json.dump(messages, f, indent=2)


if __name__ == "__main__":
    main()
