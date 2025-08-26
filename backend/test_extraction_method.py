#!/usr/bin/env python3

"""Test the extraction method directly to debug the issue"""

import os
import sys
sys.path.append('.')

from app.services.analysis_engine_exact import manual_query_processor

def test_extraction_method():
    """Test extraction method with the actual file content"""
    
    # Read the actual test.txt file
    test_file_path = "../test.txt"
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        print(f"Original file size: {len(file_content)} characters")
        israel_count = file_content.lower().count('israel')
        print(f"Israel mentions in original file: {israel_count}")
        
        # Test the extraction method directly
        prompt = "How many complaints are for Israel? I need a full list with all of them"
        
        print("\nTesting extraction method...")
        result = manual_query_processor(prompt, method="extraction", file_content=file_content)
        
        print(f"\nExtraction method result:")
        print("="*80)
        print(result)
        print("="*80)
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_extraction_method()