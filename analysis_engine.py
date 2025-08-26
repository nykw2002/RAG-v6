import subprocess
import os
import json
import numpy as np
import time
import requests
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables from .env file
load_dotenv()

class AzureOpenAIAuth:
    """Handle OAuth2 authentication with PingFed"""
    
    def __init__(self):
        self.ping_fed_url = os.getenv('PING_FED_URL')
        self.kgw_client_id = os.getenv('KGW_CLIENT_ID')
        self.kgw_client_secret = os.getenv('KGW_CLIENT_SECRET')
        self.access_token = None
        self.token_expires_at = None
        
        if not all([self.ping_fed_url, self.kgw_client_id, self.kgw_client_secret]):
            raise ValueError("Missing auth config: PING_FED_URL, KGW_CLIENT_ID, KGW_CLIENT_SECRET")
    
    def get_access_token(self) -> str:
        """Get or refresh OAuth2 access token"""
        # Return cached token if still valid
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
        
        # Request new token from PingFed
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.kgw_client_id,
            'client_secret': self.kgw_client_secret
        }
        
        response = requests.post(self.ping_fed_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Cache with 5-minute buffer
            self.token_expires_at = time.time() + token_data.get('expires_in', 3600) - 300
            return self.access_token
        else:
            raise Exception(f"Auth failed: {response.status_code} - {response.text}")

class AzureOpenAIClient:
    """Azure OpenAI client matching azure.py implementation"""
    
    def __init__(self):
        self.auth = AzureOpenAIAuth()
        self.endpoint = os.getenv('KGW_ENDPOINT')
        self.api_version = os.getenv('AOAI_API_VERSION')
        self.chat_deployment = os.getenv('CHAT_MODEL_DEPLOYMENT_NAME')
        
        if not all([self.endpoint, self.api_version, self.chat_deployment]):
            raise ValueError("Missing config: KGW_ENDPOINT, AOAI_API_VERSION, CHAT_MODEL_DEPLOYMENT_NAME")
        
        self.current_deployment = self.chat_deployment
        print(f"✅ Using GPT-4o deployment: {self.current_deployment}")
    
    def make_api_call(self, messages, max_tokens=4000, temperature=0.3):
        """Core API call method matching azure.py"""
        # Step 1: Get OAuth2 access token
        access_token = self.auth.get_access_token()
        
        # Step 2: Build Azure OpenAI endpoint URL
        url = f"{self.endpoint}/openai/deployments/{self.current_deployment}/chat/completions?api-version={self.api_version}"
        
        # Step 3: Prepare headers with Bearer token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Step 4: Prepare OpenAI Chat Completions payload
        payload = {
            'messages': messages,
            'max_completion_tokens': max_tokens,  # For newer models
            'temperature': temperature
        }
        
        # Step 5: Make HTTP POST request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 200:
                    # Success - extract response content
                    result = response.json()
                    return MockResponse(result['choices'][0]['message']['content'])
                    
                elif response.status_code == 429:
                    # Rate limit - exponential backoff
                    wait_time = (2 ** attempt) + 3
                    print(f"Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    # API error
                    error_msg = f"API Error: {response.status_code} - {response.text}"
                    print(f"ERROR: {error_msg}")
                    return MockResponse(error_msg)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    error_msg = f"Request failed after {max_retries} attempts: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    return MockResponse(error_msg)
                    
                # Wait before retry
                wait_time = (2 ** attempt) + 2
                print(f"Request error, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        return MockResponse(f"Failed after {max_retries} attempts")
    
    def chat_completions_create(self, model="gpt-4o", messages=None, temperature=0.3, max_tokens=4000):
        """Create chat completion using Azure OpenAI"""
        return self.make_api_call(messages or [], max_tokens, temperature)
    
    def embeddings_create(self, model="text-embedding-ada-002", input_text=None):
        """Create embeddings using Azure OpenAI"""
        # For embeddings, we'll use the same auth pattern but different endpoint
        access_token = self.auth.get_access_token()
        
        # Assume embeddings deployment name matches model name
        deployment_name = model
        url = f"{self.endpoint}/openai/deployments/{deployment_name}/embeddings?api-version={self.api_version}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        payload = {
            'input': input_text or []
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return MockEmbeddingResponse([data['embedding'] for data in result['data']])
            else:
                print(f"Embeddings API Error: {response.status_code} - {response.text}")
                return MockEmbeddingResponse([])
                
        except Exception as e:
            print(f"Embeddings Request Error: {str(e)}")
            return MockEmbeddingResponse([])

class MockResponse:
    """Mock response object to match OpenAI client interface"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice object"""
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message object"""
    def __init__(self, content):
        self.content = content

class MockEmbeddingResponse:
    """Mock embedding response object"""
    def __init__(self, embeddings):
        self.data = [MockEmbeddingData(emb) for emb in embeddings]

class MockEmbeddingData:
    """Mock embedding data object"""
    def __init__(self, embedding):
        self.embedding = embedding

# Initialize Azure OpenAI client
client = AzureOpenAIClient()

def get_gpt4o_script(prompt, target_file="test.txt"):
    """Have GPT-4o write a Python script for the given prompt"""
    
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
    - Do NOT include markdown formatting like ``````
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
    
    # Remove markdown code blocks if they somehow still appear
    if script_content.startswith("```python"):
        script_content = script_content[9:]
    if script_content.startswith("```"):
        script_content = script_content[3:]
    if script_content.endswith("```"):
        script_content = script_content[:-3]

    return script_content.strip()

def execute_script_and_analyze(script_content, script_name="generated_script.py"):
    """Execute the script and analyze if more processing is needed"""
    
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
    """Ask GPT-4o if another script is needed"""
    
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

def autonomous_analysis_loop(user_prompt, max_iterations=3):
    """Main loop where GPT-4o writes and executes scripts autonomously"""
    
    print(f"Starting autonomous script generation for: {user_prompt}")
    print("=" * 60)
    
    for iteration in range(1, max_iterations + 1):
        print(f"\nITERATION {iteration}")
        print("-" * 30)
        
        # 1. GPT-4o writes a script
        print("GPT-4o is writing a Python script...")
        try:
            script_content = get_gpt4o_script(user_prompt)
            
            script_filename = f"gpt4o_script_iter_{iteration}.py"
            print(f"Script saved as: {script_filename}")
            
            # 2. Execute the script
            print("Executing script...")
            execution_result = execute_script_and_analyze(script_content, script_filename)
            print(f"DEBUG: execution_result type = {type(execution_result)}")
            print(f"DEBUG: execution_result content = {execution_result}")
            
            if execution_result['success']:
                print("Script executed successfully")
                print("Output:", execution_result['output'][:300] + "..." if len(execution_result['output']) > 300 else execution_result['output'])
            else:
                print("✗ Script execution failed")
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
                
                # If the execution result contains detailed lists or data, return that instead of summary
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
    """Delete generated Python script files to keep workspace clean"""
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

# RAG Implementation
def create_embeddings(texts):
    """Create embeddings using ada-002"""
    try:
        response = client.embeddings_create(
            model="text-embedding-ada-002",
            input_text=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return []

def prepare_document_chunks(filename, chunk_size=300, debug=True):
    """Split document into manageable chunks"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if debug:
            print(f"DEBUG - File: {filename}")
            print(f"DEBUG - Content length: {len(content)} chars")
            print(f"DEBUG - First 200 chars: {content[:200]}")
        
        # Simple chunking by words
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
    """Find most relevant chunks using cosine similarity"""
    try:
        if not query_embedding or not chunk_embeddings:
            return chunks[:top_k]  # Fallback to first chunks
            
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        
        # Get all chunks above similarity threshold, up to top_k
        relevant_indices = []
        sorted_indices = np.argsort(similarities)[::-1]  # Sort descending
        
        for idx in sorted_indices:
            if similarities[idx] >= similarity_threshold and len(relevant_indices) < top_k:
                relevant_indices.append(idx)
        
        # If no chunks meet threshold, take top 5 anyway
        if not relevant_indices:
            relevant_indices = sorted_indices[:5]
        
        relevant_chunks = [chunks[i] for i in relevant_indices]
        print(f"DEBUG Retrieved {len(relevant_chunks)} relevant chunks (threshold: {similarity_threshold})")
        
        if debug:
            print(f"DEBUG DEBUG - Top similarity scores: {similarities[relevant_indices]}")
            print(f"DEBUG DEBUG - Retrieved chunks preview:")
            for i, (chunk, idx) in enumerate(zip(relevant_chunks, relevant_indices)):
                # Clean chunk text for safe printing
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
    """Generate response using retrieved context"""
    
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

def rag_analysis(prompt, target_file="test.txt"):
    """RAG-based analysis using top 20 most relevant chunks"""
    
    print(f"Starting RAG analysis for: {prompt}")
    print("=" * 60)
    
    # 1. Read and chunk the document
    print("Preparing document chunks...")
    chunks = prepare_document_chunks(target_file)
    
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
    
    # 4. Find top 25 most relevant chunks
    print("DEBUG Finding top 25 most relevant chunks...")
    relevant_chunks = retrieve_relevant_chunks(query_embedding, chunks, chunk_embeddings, top_k=25, similarity_threshold=0.05)
    
    # 5. Generate answer with context
    print("AI Generating response with context...")
    response = generate_rag_response(prompt, relevant_chunks)
    
    print("RAG analysis completed")
    return response

def manual_query_processor(prompt, method="extraction", target_file="test.txt"):
    """
    Process query with manual method selection
    
    Args:
        prompt: User query
        method: "extraction" or "reasoning"
        target_file: File to analyze
    """
    
    if method == "extraction":
        print(f"Using SCRIPT GENERATION for: {prompt[:50]}...")
        return autonomous_analysis_loop(prompt)
    
    elif method == "reasoning":
        print(f"Using RAG ANALYSIS for: {prompt[:50]}...")
        return rag_analysis(prompt, target_file)
    
    else:
        raise ValueError("Method must be 'extraction' or 'reasoning'")

def check_requirements():
    """Check if all requirements are met"""
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("ERROR .env file not found!")
        print("Please create a .env file with Azure OpenAI credentials")
        return False
    
    # Check for Azure OpenAI credentials (matching azure.py)
    ping_fed_url = os.getenv("PING_FED_URL")
    kgw_client_id = os.getenv("KGW_CLIENT_ID")
    kgw_client_secret = os.getenv("KGW_CLIENT_SECRET")
    kgw_endpoint = os.getenv("KGW_ENDPOINT")
    aoai_api_version = os.getenv("AOAI_API_VERSION")
    chat_deployment = os.getenv("CHAT_MODEL_DEPLOYMENT_NAME")
    
    missing_vars = []
    if not ping_fed_url:
        missing_vars.append("PING_FED_URL")
    if not kgw_client_id:
        missing_vars.append("KGW_CLIENT_ID")
    if not kgw_client_secret:
        missing_vars.append("KGW_CLIENT_SECRET")
    if not kgw_endpoint:
        missing_vars.append("KGW_ENDPOINT")
    if not aoai_api_version:
        missing_vars.append("AOAI_API_VERSION")
    if not chat_deployment:
        missing_vars.append("CHAT_MODEL_DEPLOYMENT_NAME")
    
    if missing_vars:
        print(f"ERROR Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    # Check for required packages
    try:
        import sklearn
        import numpy
    except ImportError as e:
        print(f"ERROR Missing required package: {e}")
        print("Please install: pip install scikit-learn numpy")
        return False
    
    # Check for test.txt
    if not os.path.exists('test.txt'):
        print("⚠️ test.txt not found. Creating sample file...")
        sample_data = """Complaint ID: 001 - Israel - Product defect - substantiated
Complaint ID: 002 - Germany - Service issue - unsubstantiated  
Complaint ID: 003 - Israel - Packaging problem - substantiated
Complaint ID: 004 - France - Delivery delay - unsubstantiated
Previous period: 15 substantiated complaints, 12 unsubstantiated complaints
Complaint ID: 005 - Israel - Quality issue - under investigation
CAPA-001: Implemented additional quality checks for Israel shipments
CAPA-002: Enhanced packaging procedures ongoing
Complaint ID: 006 - Israel - Manufacturing defect - substantiated
Current period: 18 substantiated complaints, 10 unsubstantiated complaints
Complaint ID: 007 - Israel - Labeling issue - substantiated
Complaint ID: 008 - UK - Shipping delay - unsubstantiated
Complaint ID: 009 - Israel - Color variation - substantiated
CAPA-003: Revised quality control procedures for color consistency
Previous review period data: January-March had 8 substantiated, 15 unsubstantiated
Current review period data: April-June had 12 substantiated, 8 unsubstantiated"""
        
        with open('test.txt', 'w', encoding='utf-8') as f:
            f.write(sample_data)
        print("✓ Sample test.txt created!")
    
    return True

# Updated queries with manual method selection
QUERIES = [
    ("How many complaints are for Israel, i need a list with all of them please", "extraction"),
    ("Analyze overall complaint numbers and compare to previous period. State the total number of substantiated and unsubstantiated complaints during the review period. Do NOT provide PPM analysis - only state counts. Compare to previous review period using phrasing: 'The number of substantiated complaints increased/decreased/remained the same compared to the last period'. If negative trend identified, summarize any CAPA implemented or ongoing.", "reasoning")
]

def interactive_mode():
    """Interactive mode for dynamic query processing"""
    
    print("SYSTEM Welcome to the Interactive Analysis System!")
    print("=" * 60)
    print("Available methods:")
    print("  EXTRACTION extraction  - Script generation for data extraction, counting, parsing")
    print("  REASONING reasoning   - RAG analysis for complex reasoning and comparison")
    print("  ❓ help       - Show examples")
    print("  EXIT quit       - Exit the system")
    print("=" * 60)
    
    while True:
        print("\n" + "="*50)
        
        # Get user input
        user_input = input("\nINPUT Enter your query (or 'help'/'quit'): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("GOODBYE Goodbye!")
            break
            
        if user_input.lower() in ['help', 'h']:
            show_examples()
            continue
            
        if not user_input:
            print("⚠️ Please enter a query!")
            continue
        
        # Get method selection
        method = input("\nCONFIG Select method (extraction/reasoning): ").strip().lower()
        
        if method not in ['extraction', 'reasoning']:
            print("⚠️ Please choose 'extraction' or 'reasoning'")
            continue
        
        # Process the query
        print(f"\nPROCESSING Processing your query using {method.upper()}...")
        print("-" * 60)
        
        try:
            result = manual_query_processor(user_input, method)
            
            print(f"\nSUCCESS RESULT:")
            print("=" * 40)
            print(result)
            print("=" * 40)
            
        except Exception as e:
            print(f"ERROR Error processing query: {e}")
        
        # Ask if user wants to continue
        continue_choice = input("\nCONTINUE Process another query? (y/n): ").strip().lower()
        if continue_choice in ['n', 'no']:
            print("GOODBYE Thanks for using the system!")
            break

def show_examples():
    """Show example queries for each method"""
    
    print("\nEXAMPLES EXAMPLE QUERIES:")
    print("=" * 50)
    
    print("\nEXTRACTION EXTRACTION Examples (Script Generation):")
    print("  • How many complaints are for Israel?")
    print("  • List all substantiated complaints")
    print("  • Count complaints by country")
    print("  • Extract all CAPA numbers")
    print("  • Find complaints with specific keywords")
    
    print("\nREASONING REASONING Examples (RAG Analysis):")
    print("  • Analyze complaint trends compared to previous period")
    print("  • Summarize CAPA actions and their effectiveness")
    print("  • Compare substantiated vs unsubstantiated complaint patterns")
    print("  • Assess overall quality issues and recommendations")
    print("  • Explain the relationship between complaints and implemented actions")
    
    print("\nTIP TIP: Use 'extraction' for counting/listing, 'reasoning' for analysis/comparison")

def batch_mode():
    """Process predefined queries (original functionality)"""
    
    print("CONTINUE Running predefined queries...")
    
    # Original queries
    QUERIES = [
        ("How many complaints are for Israel, i need a list with all of them please", "extraction"),
        ("Analyze overall complaint numbers and compare to previous period. State the total number of substantiated and unsubstantiated complaints during the review period. Do NOT provide PPM analysis - only state counts. Compare to previous review period using phrasing: 'The number of substantiated complaints increased/decreased/remained the same compared to the last period'. If negative trend identified, summarize any CAPA implemented or ongoing.", "reasoning")
    ]
    
    for i, (prompt, method) in enumerate(QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"PROCESSING QUERY {i} [{method.upper()}]: {prompt[:50]}...")
        print(f"{'='*80}")
        
        try:
            result = manual_query_processor(prompt, method)
            print(f"\nSUCCESS Completed query {i}")
            print(f"Result: {result}")
        except Exception as e:
            print(f"ERROR Error processing query {i}: {e}")

def main_menu():
    """Main menu for selecting mode"""
    
    print("SYSTEM Enhanced Analysis System: Script Generation + RAG")
    print("=" * 60)
    
    while True:
        print("\nSelect mode:")
        print("  1️⃣  Interactive mode - Ask your own questions")
        print("  2️⃣  Batch mode - Run predefined queries")
        print("  3️⃣  Single query - One-time query processing")
        print("  4️⃣  Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            interactive_mode()
            break
        elif choice == '2':
            batch_mode()
            break
        elif choice == '3':
            single_query_mode()
            break
        elif choice == '4':
            print("GOODBYE Goodbye!")
            break
        else:
            print("⚠️ Please enter 1, 2, 3, or 4")

def single_query_mode():
    """Process a single query and exit"""
    
    print("\nSingle Query Mode")
    print("-" * 30)
    
    query = input("Enter your query: ").strip()
    if not query:
        print("WARNING: No query entered!")
        return
    
    method = input("CONFIG Select method (extraction/reasoning): ").strip().lower()
    if method not in ['extraction', 'reasoning']:
        print("⚠️ Invalid method!")
        return
    
    print(f"\nPROCESSING Processing query using {method.upper()}...")
    
    try:
        result = manual_query_processor(query, method)
        print(f"\nSUCCESS RESULT:")
        print("=" * 40)
        print(result)
        print("=" * 40)
    except Exception as e:
        print(f"ERROR Error: {e}")

# This file is now used as a module for the FastAPI application
# The main menu and interactive functions are replaced by web API endpoints