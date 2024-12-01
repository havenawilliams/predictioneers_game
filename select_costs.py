import fileinput
import re

def list_and_update_cost_dictionary(file_path="cost_dictionaries.py"):
    # Read all dictionary names from the file
    with open(file_path, "r") as file:
        content = file.readlines()
    
    # Extract dictionary names using a regex pattern
    dict_names = [line.split('=')[0].strip() for line in content if re.match(r"^\w+\s*=\s*\{", line)]
    
    print("Available cost dictionaries:")
    for i, name in enumerate(dict_names, start=1):
        print(f"{i}: {name}")
    
    # Prompt user for input
    choice = input("\nEnter the number corresponding to the dictionary you want to set as 'cost_dictionary': ")
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(dict_names):
            selected_dict = dict_names[choice - 1]
            
            # Update the cost_dictionary line in the file
            for line in fileinput.input(file_path, inplace=True):
                if line.strip().startswith("cost_dictionary ="):
                    print(f"cost_dictionary = {selected_dict}", end="\n")
                else:
                    print(line, end="")  # Print lines as-is
            print(f"\n'cost_dictionary' has been updated to '{selected_dict}' in {file_path}.")
        else:
            print("Invalid choice. Please select a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    list_and_update_cost_dictionary()
