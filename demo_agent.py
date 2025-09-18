#!/usr/bin/env python3
"""
Demo script to showcase the agentic capabilities of the CodingTool.
This script creates sample tasks for the agent to work on.
"""

def create_sample_task_file():
    """Create a sample Python file for the agent to work with."""
    sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Calculate first 10 Fibonacci numbers
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
'''
    
    with open("sample_fib.py", "w") as f:
        f.write(sample_code)
    
    print("Created sample_fib.py for agent testing")

def create_broken_code():
    """Create intentionally broken code for the agent to fix."""
    broken_code = '''
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    count = 0
    
    for num in numbers:
        total += num
        # Bug: forgot to increment count
    
    return total / count  # This will cause division by zero

def main():
    numbers = [1, 2, 3, 4, 5]
    avg = calculate_average(numbers)
    print(f"Average: {avg}")

if __name__ == "__main__":
    main()
'''
    
    with open("broken_avg.py", "w") as f:
        f.write(broken_code)
    
    print("Created broken_avg.py for agent debugging practice")

if __name__ == "__main__":
    create_sample_task_file()
    create_broken_code()
    
    print("\n" + "="*50)
    print("DEMO TASKS FOR AGENTIC LOOP")
    print("="*50)
    print("\n1. Basic Task (Non-interactive):")
    print("   uv run main.py \"analyze and run the sample_fib.py file\"")
    
    print("\n2. Interactive Task:")
    print("   uv run main.py \"fix the bug in broken_avg.py\" --interactive")
    
    print("\n3. Complex Task with Verbose Output:")
    print("   uv run main.py \"create a unit test file for sample_fib.py and run the tests\" --verbose --interactive")
    
    print("\n4. Code Review Task:")
    print("   uv run main.py \"review all .py files in this directory and suggest improvements\" --interactive")
    
    print("\nFlags:")
    print("  --interactive: Enable dynamic conversation")
    print("  --verbose: Show detailed execution information")
    print("\nPress Ctrl+C to stop the agent at any time")