# Generated script for iteration 1
# Prompt: How many complaints are from Israel, i need a full list
# Target file: temp_analysis_file.txt

import os

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except UnicodeDecodeError:
        print(f"Error: The file '{file_path}' could not be decoded.")
        return None

def validate_and_extract_complaints(data):
    if not data:
        return []
    complaints = []
    for line in data:
        if "Israel" in line:
            complaints.append(line.strip())
    return complaints

def main():
    file_path = 'temp_analysis_file.txt'
    data = read_file(file_path)
    complaints_from_israel = validate_and_extract_complaints(data)
    
    if complaints_from_israel:
        print(f"Number of complaints from Israel: {len(complaints_from_israel)}")
        print("Complaints List:")
        for complaint in complaints_from_israel:
            print(complaint)
    else:
        print("No complaints from Israel found or file is empty.")

if __name__ == "__main__":
    main()