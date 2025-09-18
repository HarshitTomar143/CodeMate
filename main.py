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
from call_functions import call_function


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


def run_agentic_loop(chat, initial_prompt, messages, history_file, verbose_flag, interactive_flag, available_functions):
    """Run the main agentic loop for continuous conversation and task execution."""
    
    # Add initial user message
    messages.append({"role": "user", "parts": [initial_prompt]})
    
    current_prompt = initial_prompt
    max_iterations = 50  # Increased for complex tasks
    iteration_count = 0
    
    # Track agent state
    task_completed = False
    waiting_for_user = False
    
    while iteration_count < max_iterations and not task_completed:
        iteration_count += 1
        
        if verbose_flag:
            print(f"\n🔄 Iteration {iteration_count}/{max_iterations}")
        
        try:
            # Send message to the model
            response = chat.send_message(current_prompt, tools=[available_functions])
            print_response(response)
            
            # Check if the agent indicates task completion or needs user input
            if response.candidates:
                response_text = ""
                function_calls_made = False
                
                parts = response.candidates[0].content.parts
                for part in parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text
                        messages.append({"role": "model", "parts": [part.text]})
                    
                    elif hasattr(part, "function_call") and part.function_call:
                        function_calls_made = True
                        print(f"\n🔧 Executing: {part.function_call.name}", dict(part.function_call.args))
                        
                        # Execute the function
                        result = call_function(part.function_call, verbose=verbose_flag)
                        print(f"📝 Function Result:\n{result}")
                        
                        # Send result back to the model
                        current_prompt = f"Function result:\n{result}\n\nPlease continue with the task or let me know if you need additional input."
                
                # Check for completion indicators
                completion_phrases = [
                    "task completed", "task is complete", "finished", "done",
                    "successfully completed", "goal achieved", "objective accomplished"
                ]
                
                user_input_phrases = [
                    "need clarification", "need more information", "please specify",
                    "what would you like", "do you want", "need user input"
                ]
                
                response_lower = response_text.lower()
                
                if any(phrase in response_lower for phrase in completion_phrases):
                    print(f"\n✅ Agent reports task completion!")
                    if interactive_flag:
                        user_input = input("\n💬 Do you have another task? (Enter new task or 'quit'): ")
                        if user_input.lower() in ['quit', 'exit', 'stop', '']:
                            task_completed = True
                        else:
                            current_prompt = user_input
                            messages.append({"role": "user", "parts": [user_input]})
                            print(f"\n🆕 New task: {user_input}")
                    else:
                        task_completed = True
                
                elif any(phrase in response_lower for phrase in user_input_phrases):
                    print(f"\n❓ Agent is requesting user input...")
                    if interactive_flag:
                        user_input = input("\n💬 Your response: ")
                        current_prompt = user_input
                        messages.append({"role": "user", "parts": [user_input]})
                    else:
                        print("🚀 Run with --interactive flag for dynamic conversations")
                        task_completed = True
                
                elif not function_calls_made:
                    # No function calls and no clear completion - might need user input
                    if interactive_flag and iteration_count > 3:
                        user_choice = input("\n🤔 Continue, provide input, or quit? (c/i/q): ")
                        if user_choice.lower() == 'q':
                            task_completed = True
                        elif user_choice.lower() == 'i':
                            user_input = input("💬 Your input: ")
                            current_prompt = user_input
                            messages.append({"role": "user", "parts": [user_input]})
                        else:
                            current_prompt = "Please continue with the task. If you're stuck, explain what you need."
                    else:
                        current_prompt = "Please continue working on the task or let me know if you've completed it."
            
            # Save conversation history
            with open(history_file, "w") as f:
                json.dump(messages, f, indent=2)
                
        except Exception as e:
            print(f"\n⚠️ Error in iteration {iteration_count}: {str(e)}")
            if verbose_flag:
                import traceback
                traceback.print_exc()
            
            if interactive_flag:
                retry = input("\n🔄 Retry this iteration? (y/n): ")
                if retry.lower() != 'y':
                    task_completed = True
            else:
                current_prompt = "There was an error. Please try a different approach."
    
    if iteration_count >= max_iterations:
        print(f"\n⏰ Maximum iterations ({max_iterations}) reached.")
        if interactive_flag:
            continue_choice = input("🔄 Continue with more iterations? (y/n): ")
            if continue_choice.lower() == 'y':
                run_agentic_loop(chat, "Please continue from where we left off.", messages, history_file, verbose_flag, interactive_flag, available_functions)
    
    print(f"\n🏁 Agentic session completed after {iteration_count} iterations.")


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    # Configure Gemini client
    genai.configure(api_key=api_key)

    system_prompt = """
        You are a helpful AI coding agent with advanced capabilities.
        
        You can perform multi-turn conversations and work iteratively towards complex goals.
        When given a task, you should:
        1. Break it down into smaller steps if needed
        2. Execute each step using available functions
        3. Reflect on results and adjust your approach
        4. Continue working until the goal is achieved or you need user input
        
        Available operations:
        - get_files_info: List files and directories in the working directory or in sub-directories.
        - get_files_content: Reads the content of the file in the working directory.
        - write_file: Writes to the file(creates or update)
        - run_python_file: Run the python file with optional arguments
        
        When you believe you've completed a task, explain what you accomplished.
        If you need clarification or additional input, ask the user directly.
        If you encounter errors, analyze them and try alternative approaches.
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

    # Get initial prompt from CLI
    if len(sys.argv) < 2:
        print("I need a prompt as a command line argument.")
        sys.exit(1)

    initial_prompt = " ".join(sys.argv[1:])
    verbose_flag = "--verbose" in sys.argv
    interactive_flag = "--interactive" in sys.argv

    print(f"\n🤖 AI Agent Starting...")
    print(f"📝 Initial Task: {initial_prompt}")
    print(f"🔧 Interactive Mode: {'On' if interactive_flag else 'Off'}")
    print(f"🐛 Verbose Mode: {'On' if verbose_flag else 'Off'}")
    print("─" * 50)

    # Start the agentic loop
    run_agentic_loop(chat, initial_prompt, messages, history_file, verbose_flag, interactive_flag, available_functions)


    

if __name__ == "__main__":
    main()
