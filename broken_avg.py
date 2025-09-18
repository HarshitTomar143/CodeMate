
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
