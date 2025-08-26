"""
Exact replication of analysis_engine.py logic adapted for OpenAI instead of Azure
Following the EXACT same logic flow and methodology
"""

import os
import json
import time
import subprocess
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

try:
    import openai
except ImportError:
    print("ERROR: openai package not installed. Please run: pip install openai")
    raise

class OpenAIClient:
    """OpenAI client matching the interface from the original Azure implementation"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        print(f"[OK] Using OpenAI GPT-4o model")
    
    def chat_completions_create(self, model="gpt-4o", messages=None, temperature=0.3, max_tokens=4000):
        """Create chat completion using OpenAI API - matching original interface"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages or [],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return MockResponse(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return MockResponse(f"Error: {str(e)}")
    
    def embeddings_create(self, model="text-embedding-ada-002", input_text=None):
        """Create embeddings using OpenAI API - matching original interface"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=input_text or []
            )
            return MockEmbeddingResponse([data.embedding for data in response.data])
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return MockEmbeddingResponse([])

class MockResponse:
    """Mock response object to match OpenAI client interface - EXACT copy from original"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice object - EXACT copy from original"""
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message object - EXACT copy from original"""
    def __init__(self, content):
        self.content = content

class MockEmbeddingResponse:
    """Mock embedding response object - EXACT copy from original"""
    def __init__(self, embeddings):
        self.data = [MockEmbeddingData(emb) for emb in embeddings]

class MockEmbeddingData:
    """Mock embedding data object - EXACT copy from original"""
    def __init__(self, embedding):
        self.embedding = embedding

# Initialize OpenAI client
client = OpenAIClient()

def get_gpt4o_script(prompt, target_file="test.txt"):
    """Have GPT-4o write a Python script for the given prompt - EXACT copy from original"""
    
    system_prompt = f"""
    You are a Python script generator. Write a complete, executable Python script that:
    1. Reads and analyzes the file '{target_file}' 
    2. Answers this user query: {prompt}
    3. Prints clear, formatted results
    4. Handles errors gracefully (file not found, encoding issues, etc.)
    5. Uses try-except blocks around file operations
    6. Validates data before processing
    
    IMPORTANT FORMATTING RULES:
    - Return ONLY pure Python code
    - Do NOT include markdown formatting like ```
    - Do NOT include any explanations or comments outside the code
    - The response should start directly with Python code (import statements, functions, etc.)
    - The script should be completely self-contained and executable as a .py file
    - Always include proper error handling and data validation
    
    Start your response immediately with Python code, nothing else.
    """
    
    response = client.chat_completions_create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a Python script to: {prompt}"}
        ],
        temperature=0.3
    )
    
    script_content = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if they somehow still appear - EXACT logic from original
    if script_content.startswith("```python"):
        script_content = script_content[9:]
    if script_content.startswith("```"):
        script_content = script_content[3:]
    if script_content.endswith("```"):
        script_content = script_content[:-3]

    return script_content.strip()

def execute_script_and_analyze(script_content, script_name="generated_script.py"):
    """Execute the script and analyze if more processing is needed - EXACT copy from original"""
    
    # Write script to file
    with open(script_name, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"Script content preview (first 200 chars):")
    print(script_content[:200] + "..." if len(script_content) > 200 else script_content)
    print("-" * 40)
    
    # Execute script
    try:
        result = subprocess.run(['python', script_name], 
                              capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'script_file': script_name
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'script_file': script_name
        }

def ask_gpt4o_for_decision(prompt, execution_result):
    """Ask GPT-4o if another script is needed - EXACT copy from original"""
    
    decision_prompt = f"""
    Original user query: {prompt}
    
    Script execution result:
    Success: {execution_result['success']}
    Output: {execution_result['output']}
    Error: {execution_result['error']}
    
    Based on this output, respond with either:
    - "DONE: [final answer summary]" if the query is fully answered
    - "CONTINUE: [what additional processing is needed]" if more scripts are required
    
    Be concise in your response.
    """
    
    response = client.chat_completions_create(
        model="gpt-4o",
        messages=[{"role": "user", "content": decision_prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def autonomous_analysis_loop(user_prompt, target_file="test.txt", max_iterations=3):
    """Main loop where GPT-4o writes and executes scripts autonomously - EXACT copy from original"""
    
    print(f"Starting autonomous script generation for: {user_prompt}")
    print("=" * 60)
    
    for iteration in range(1, max_iterations + 1):
        print(f"\nITERATION {iteration}")
        print("-" * 30)
        
        # 1. GPT-4o writes a script
        print("GPT-4o is writing a Python script...")
        try:
            script_content = get_gpt4o_script(user_prompt, target_file)
            
            script_filename = f"gpt4o_script_iter_{iteration}.py"
            print(f"Script saved as: {script_filename}")
            
            # Save script for debugging - keep the last one
            debug_script = f"debug_last_generated_script.py"
            with open(debug_script, 'w', encoding='utf-8') as f:
                f.write(f"# Generated script for iteration {iteration}\n")
                f.write(f"# Prompt: {user_prompt}\n")
                f.write(f"# Target file: {target_file}\n\n")
                f.write(script_content)
            print(f"DEBUG: Script saved for inspection at: {debug_script}")
            
            # 2. Execute the script
            print("Executing script...")
            execution_result = execute_script_and_analyze(script_content, script_filename)
            print(f"DEBUG: execution_result type = {type(execution_result)}")
            print(f"DEBUG: execution_result content = {execution_result}")
            
            if execution_result['success']:
                print("[SUCCESS] Script executed successfully")
                print("Output:", execution_result['output'][:300] + "..." if len(execution_result['output']) > 300 else execution_result['output'])
            else:
                print("[ERROR] Script execution failed")
                print("Error:", execution_result['error'])
                
                # If there's still a syntax error, let's debug
                if "SyntaxError" in execution_result['error']:
                    print("Debugging syntax error...")
                    print("First few lines of generated script:")
                    lines = script_content.split('\n')[:5]
                    for i, line in enumerate(lines, 1):
                        print(f"  {i}: {repr(line)}")
            
            # 3. GPT-4o decides if more processing is needed
            print("\nGPT-4o is analyzing results...")
            decision = ask_gpt4o_for_decision(user_prompt, execution_result)
            
            print(f"Decision: {decision}")
            
            if decision.startswith("DONE"):
                final_answer = decision[5:].strip()
                print(f"\nFINAL ANSWER: {final_answer}")
                
                # If the execution result contains detailed lists or data, return that instead of summary - EXACT logic from original
                if execution_result and isinstance(execution_result, dict) and execution_result.get('success') and execution_result.get('output'):
                    output_text = execution_result['output']
                    # Debug: Show what we're checking
                    print(f"DEBUG: Checking output text for detailed data")
                    print(f"DEBUG: output length: {len(output_text)}")
                    print(f"DEBUG: newline count: {output_text.count('\n')}")
                    print(f"DEBUG: dash count: {output_text.count('-')}")
                    print(f"DEBUG: contains 'detailed': {'detailed' in output_text.lower()}")
                    print(f"DEBUG: contains 'list': {'list' in output_text.lower()}")
                    
                    if (("list" in output_text.lower() and "detailed" in output_text.lower()) or
                        output_text.count('\n') > 5 or  # Multi-line detailed output
                        output_text.count('-') > 3):   # Bullet points or numbered items
                        print("SUCCESS: Returning detailed execution result instead of summary")
                        cleanup_generated_files()  # Clean up before returning
                        return output_text  # Return the actual output text, not the dict
                
                cleanup_generated_files()  # Clean up before returning
                return final_answer
            elif decision.startswith("CONTINUE"):
                next_step = decision[9:].strip()
                print(f"Continuing with: {next_step}")
                user_prompt = f"{user_prompt} (Previous attempt had issues, try a different approach)"
            else:
                print("WARNING: Unclear decision from GPT-4o, stopping.")
                break
                
        except Exception as e:
            print(f"Error in iteration {iteration}: {str(e)}")
            print(f"Full error details: {type(e).__name__}: {e}")
            break
    
    # Cleanup: Delete generated script files
    cleanup_generated_files()
    
    return "Analysis completed after maximum iterations"

def cleanup_generated_files():
    """Delete generated Python script files to keep workspace clean - EXACT copy from original"""
    try:
        import glob
        script_files = glob.glob("gpt4o_script_iter_*.py")
        for file_path in script_files:
            try:
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        
        if script_files:
            print(f"Cleaned up {len(script_files)} generated script files")
    except Exception as e:
        print(f"Cleanup error: {e}")

# RAG Implementation - EXACT copy from original with modifications for memory-based content

def create_embeddings(texts):
    """Create embeddings using ada-002 - EXACT copy from original"""
    try:
        response = client.embeddings_create(
            model="text-embedding-ada-002",
            input_text=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return []

def prepare_document_chunks(content, chunk_size=300, debug=True):
    """Split document into manageable chunks - adapted from original for memory content"""
    try:
        if debug:
            print(f"DEBUG - Content length: {len(content)} chars")
            print(f"DEBUG - First 200 chars: {content[:200]}")
        
        # Simple chunking by words - EXACT logic from original
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        print(f"Document split into {len(chunks)} chunks")
        
        if debug and chunks:
            print(f"DEBUG - First chunk preview: {chunks[0][:150]}...")
        
        return chunks
        
    except Exception as e:
        print(f"Error preparing chunks: {e}")
        return []

def retrieve_relevant_chunks(query_embedding, chunks, chunk_embeddings, top_k=10, similarity_threshold=0.1, debug=True):
    """Find most relevant chunks using cosine similarity - EXACT copy from original"""
    try:
        if not query_embedding or not chunk_embeddings:
            return chunks[:top_k]  # Fallback to first chunks
            
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        
        # Get all chunks above similarity threshold, up to top_k - EXACT logic from original
        relevant_indices = []
        sorted_indices = np.argsort(similarities)[::-1]  # Sort descending
        
        for idx in sorted_indices:
            if similarities[idx] >= similarity_threshold and len(relevant_indices) < top_k:
                relevant_indices.append(idx)
        
        # If no chunks meet threshold, take top 5 anyway - EXACT logic from original
        if not relevant_indices:
            relevant_indices = sorted_indices[:5]
        
        relevant_chunks = [chunks[i] for i in relevant_indices]
        print(f"DEBUG Retrieved {len(relevant_chunks)} relevant chunks (threshold: {similarity_threshold})")
        
        if debug:
            print(f"DEBUG DEBUG - Top similarity scores: {similarities[relevant_indices]}")
            print(f"DEBUG DEBUG - Retrieved chunks preview:")
            for i, (chunk, idx) in enumerate(zip(relevant_chunks, relevant_indices)):
                # Clean chunk text for safe printing - EXACT logic from original
                safe_chunk = chunk.replace('\uf0b7', '•').replace('\uf020', ' ').replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')[:150]
                # Remove any other problematic Unicode characters
                safe_chunk = ''.join(char if ord(char) < 65536 else '?' for char in safe_chunk)
                print(f"    Chunk {i+1} (idx {idx}, score {similarities[idx]:.3f}): {safe_chunk}...")
                print(f"    ---")
        
        return relevant_chunks
        
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return chunks[:top_k]

def generate_rag_response(prompt, relevant_chunks):
    """Generate response using retrieved context - EXACT copy from original"""
    
    context = "\n\n".join(relevant_chunks)
    
    rag_prompt = f"""
    Based on the following context, answer the user's question thoroughly and accurately:
    
    CONTEXT:
    {context}
    
    QUESTION: {prompt}
    
    Instructions:
    - Provide a detailed, accurate answer based only on the information in the context
    - If comparing to previous periods, look for historical data in the context
    - Include specific numbers and counts when available
    - If CAPA information is mentioned, summarize it
    - Be precise and factual in your response
    """
    
    try:
        response = client.chat_completions_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": rag_prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating RAG response: {e}"

def rag_analysis(prompt, file_content):
    """RAG-based analysis using top 20 most relevant chunks - adapted from original for memory content"""
    
    print(f"Starting RAG analysis for: {prompt}")
    print("=" * 60)
    
    # 1. Read and chunk the document
    print("Preparing document chunks...")
    chunks = prepare_document_chunks(file_content)
    
    if not chunks:
        return "Error: Could not process document for RAG analysis"
    
    # 2. Create embeddings for chunks
    print("Creating embeddings for document chunks...")
    chunk_embeddings = create_embeddings(chunks)
    
    # 3. Create query embedding
    print("Creating query embedding...")
    query_embeddings = create_embeddings([prompt])
    
    if not query_embeddings:
        return "Error: Could not create query embedding"
    
    query_embedding = query_embeddings[0]
    
    # 4. Find top 25 most relevant chunks - EXACT parameters from original
    print("DEBUG Finding top 25 most relevant chunks...")
    relevant_chunks = retrieve_relevant_chunks(query_embedding, chunks, chunk_embeddings, top_k=25, similarity_threshold=0.05)
    
    # 5. Generate answer with context
    print("AI Generating response with context...")
    response = generate_rag_response(prompt, relevant_chunks)
    
    print("RAG analysis completed")
    return response

def manual_query_processor(prompt, method="extraction", file_content=""):
    """
    Process query with manual method selection - EXACT copy from original adapted for memory content
    
    Args:
        prompt: User query
        method: "extraction" or "reasoning"
        file_content: File content to analyze
    """
    
    if method == "extraction":
        print(f"Using SCRIPT GENERATION for: {prompt[:50]}...")
        # For extraction method, we need to create a temporary file for the script to read
        temp_file = "temp_analysis_file.txt"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # Debug: verify file was written correctly
            with open(temp_file, 'r', encoding='utf-8') as f:
                temp_content = f.read()
            print(f"DEBUG: Temp file created with {len(temp_content)} chars (original: {len(file_content)} chars)")
            print(f"DEBUG: File content sample: {temp_content[:200]}...")
            
            # Quick check for Israel in temp file
            israel_count = temp_content.lower().count('israel')
            print(f"DEBUG: Found {israel_count} mentions of 'Israel' in temp file")
            
            # Modify the prompt to reference the temporary file
            result = autonomous_analysis_loop(prompt, temp_file)
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
            
            return result
        except Exception as e:
            return f"Error in extraction analysis: {str(e)}"
    
    elif method == "reasoning":
        print(f"Using RAG ANALYSIS for: {prompt[:50]}...")
        return rag_analysis(prompt, file_content)
    
    else:
        raise ValueError("Method must be 'extraction' or 'reasoning'")

# Global analysis function that matches the expected interface
def analyze_with_exact_logic(prompt: str, method: str, file_content: str, filename: str = "uploaded_file.txt") -> str:
    """
    Main analysis function that uses EXACT logic from analysis_engine.py
    """
    return manual_query_processor(prompt, method, file_content)