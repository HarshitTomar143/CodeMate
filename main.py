import os
import sys
import json
from dotenv import load_dotenv
import google.generativeai as genai
from functions.get_files_info import get_files_info

# Load environment variables
def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    # Configure Gemini client
    genai.configure(api_key=api_key)

    # History persistence file
    history_file = "chat_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                messages = json.load(f)
            except json.JSONDecodeError:
                messages = []  # fallback if file is empty or corrupt
    else:
        messages = []

    # Pick the model you want
    model = genai.GenerativeModel("gemini-2.0-flash-001")

    # Start chat with our own plain message list
    chat = model.start_chat(history=messages)

    # Get prompt from CLI
    if len(sys.argv) < 2:
        print("I need a prompt as a command line argument.")
        sys.exit(1)

    verbose_flag= False
    if len(sys.argv)== 3 and sys.argv[2]=="--verbose":
        verbose_flag=True

    prompt = " ".join(sys.argv[1:])

    # Add user message to our list
    messages.append({"role": "user", "parts": [prompt]})

    # Generate response
    response = chat.send_message(prompt)

    print(response.text)
    if response.usage_metadata:
        if verbose_flag:
            print("User Prompt: ", prompt)
            print(f"Input tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Output tokens: {response.usage_metadata.candidates_token_count}")

    # Add model reply to our list
    messages.append({"role": "model", "parts": [response.text]})

    # Save updated history
    with open(history_file, "w") as f:
        json.dump(messages, f, indent=2)



print(get_files_info("calculator", "pkg"))
# main()