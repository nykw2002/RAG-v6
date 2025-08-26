#!/usr/bin/env python3

import os
import sys

def analyze_file_for_israel(filename):
    """Test script to find all Israel mentions in the file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File: {filename}")
        print(f"Total file size: {len(content)} characters")
        
        # Search for Israel (case insensitive)
        israel_mentions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if 'israel' in line.lower():
                israel_mentions.append((line_num, line.strip()[:200]))  # First 200 chars of line
        
        print(f"\nTotal Israel mentions found: {len(israel_mentions)}")
        
        if israel_mentions:
            print("\nDetailed Israel mentions:")
            for line_num, line_content in israel_mentions:
                print(f"Line {line_num}: {line_content}")
        else:
            print("No mentions of 'Israel' found in the file.")
            
        return len(israel_mentions)
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0

if __name__ == "__main__":
    # Test with the temp file that should be created
    temp_file = "temp_analysis_file.txt"
    if os.path.exists(temp_file):
        result = analyze_file_for_israel(temp_file)
    else:
        print(f"Temp file {temp_file} not found. Testing with main test.txt file...")
        result = analyze_file_for_israel("../test.txt")