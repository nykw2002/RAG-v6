"""
Azure OpenAI client for AI analysis processing
Migrated from standard OpenAI API to Azure OpenAI with OAuth2 authentication
Falls back to standard OpenAI if Azure credentials are not configured
"""

import os
import json
import time
import subprocess
import numpy as np
import logging
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging to use uvicorn logger
import uvicorn
logger = uvicorn.logger if hasattr(uvicorn, 'logger') else logging.getLogger("uvicorn")

# Load environment variables
load_dotenv()

# Try to import OpenAI for fallback
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available for fallback")

def _has_azure_config() -> bool:
    """Check if all required Azure OpenAI environment variables are configured"""
    required_vars = [
        'PING_FED_URL',
        'KGW_CLIENT_ID', 
        'KGW_CLIENT_SECRET',
        'KGW_ENDPOINT',
        'AOAI_API_VERSION',
        'CHAT_MODEL_DEPLOYMENT_NAME'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.strip() == "":
            logger.info(f"Azure config missing: {var}")
            return False
    
    return True

class AzureOpenAIAuth:
    """Handle OAuth2 authentication with PingFed"""
    
    def __init__(self):
        self.ping_fed_url = os.getenv('PING_FED_URL')
        self.kgw_client_id = os.getenv('KGW_CLIENT_ID')
        self.kgw_client_secret = os.getenv('KGW_CLIENT_SECRET')
        self.access_token = None
        self.token_expires_at = None
        
        if not all([self.ping_fed_url, self.kgw_client_id, self.kgw_client_secret]):
            raise ValueError("Missing Azure auth config: PING_FED_URL, KGW_CLIENT_ID, KGW_CLIENT_SECRET")
    
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
            raise Exception(f"Azure auth failed: {response.status_code} - {response.text}")

class OpenAIClient:
    """Hybrid OpenAI client - Uses Azure OpenAI when configured, falls back to standard OpenAI"""
    
    def __init__(self):
        self.use_azure = _has_azure_config()
        
        if self.use_azure:
            logger.info("✅ Azure OpenAI configuration detected - using Azure OpenAI")
            try:
                self.auth = AzureOpenAIAuth()
                self.endpoint = os.getenv('KGW_ENDPOINT')
                self.api_version = os.getenv('AOAI_API_VERSION')
                self.chat_deployment = os.getenv('CHAT_MODEL_DEPLOYMENT_NAME')
                self.o3_mini_deployment = os.getenv('GPT_O3_MINI_DEPLOYMENT_NAME')
                self.use_o3_mini = os.getenv('USE_O3_MINI', 'false').lower() == 'true'
                
                # Choose deployment (GPT-4o vs O3-mini)
                if self.use_o3_mini and self.o3_mini_deployment:
                    self.current_deployment = self.o3_mini_deployment
                    self.model = "o3-mini"
                    logger.info(f"[OK] Using Azure O3-mini deployment: {self.current_deployment}")
                else:
                    self.current_deployment = self.chat_deployment
                    self.model = "gpt-4o"
                    logger.info(f"[OK] Using Azure GPT-4o deployment: {self.current_deployment}")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self.use_azure = False
        
        if not self.use_azure:
            logger.info("⚠️ Azure OpenAI not configured - falling back to standard OpenAI")
            if not OPENAI_AVAILABLE:
                raise ValueError("Neither Azure OpenAI nor standard OpenAI is properly configured")
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("Missing OPENAI_API_KEY for fallback")
            
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"
            logger.info(f"[OK] Using standard OpenAI GPT-4o model")
    
    def chat_completions_create(self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 4000) -> Dict[str, Any]:
        """Create chat completion using Azure OpenAI or standard OpenAI (fallback)"""
        
        if self.use_azure:
            return self._azure_chat_completion(messages, temperature, max_tokens)
        else:
            return self._standard_chat_completion(messages, temperature, max_tokens)
    
    def _azure_chat_completion(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Create chat completion using Azure OpenAI API"""
        try:
            # Get OAuth2 access token
            access_token = self.auth.get_access_token()
            
            # Build Azure OpenAI endpoint URL
            url = f"{self.endpoint}/openai/deployments/{self.current_deployment}/chat/completions?api-version={self.api_version}"
            
            # Prepare headers with Bearer token
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            # Prepare Azure OpenAI Chat Completions payload
            payload = {
                'messages': messages,
                'max_completion_tokens': max_tokens,  # Azure uses max_completion_tokens
                'temperature': temperature
            }
            
            # Make HTTP POST request with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        # Success - return response in OpenAI format for compatibility
                        result = response.json()
                        # Create mock response object that matches OpenAI interface
                        mock_response = type('MockResponse', (), {
                            'choices': [type('Choice', (), {
                                'message': type('Message', (), {
                                    'content': result['choices'][0]['message']['content']
                                })()
                            })()]
                        })()
                        return mock_response
                        
                    elif response.status_code == 429:
                        # Rate limit - exponential backoff
                        wait_time = (2 ** attempt) + 3
                        logger.warning(f"Azure API rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                        
                    else:
                        # API error
                        error_msg = f"Azure API Error: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                        
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Azure API request failed after {max_retries} attempts: {str(e)}")
                        raise
                        
                    # Wait before retry
                    wait_time = (2 ** attempt) + 2
                    logger.warning(f"Azure API request error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
            
            raise Exception(f"Azure API failed after {max_retries} attempts")
            
        except Exception as e:
            logger.error(f"Error in Azure chat completion: {e}")
            raise
    
    def _standard_chat_completion(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Create chat completion using standard OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            logger.error(f"Error in standard OpenAI chat completion: {e}")
            raise
    
    def embeddings_create(self, input_texts: List[str]) -> List[List[float]]:
        """Create embeddings using Azure OpenAI or standard OpenAI (fallback)"""
        
        if self.use_azure:
            return self._azure_embeddings(input_texts)
        else:
            return self._standard_embeddings(input_texts)
    
    def _azure_embeddings(self, input_texts: List[str]) -> List[List[float]]:
        """Create embeddings using Azure OpenAI API"""
        try:
            # Get OAuth2 access token
            access_token = self.auth.get_access_token()
            
            # Build Azure OpenAI embeddings endpoint URL
            # Note: For Azure OpenAI embeddings, use the standard model endpoint
            url = f"{self.endpoint}/openai/embeddings?api-version={self.api_version}"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            payload = {
                'input': input_texts,
                'model': 'text-embedding-ada-002'
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return [data['embedding'] for data in result['data']]
            else:
                logger.error(f"Azure embeddings API error: {response.status_code} - {response.text}")
                raise Exception(f"Azure embeddings API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error creating Azure embeddings: {e}")
            raise
    
    def _standard_embeddings(self, input_texts: List[str]) -> List[List[float]]:
        """Create embeddings using standard OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=input_texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error creating standard OpenAI embeddings: {e}")
            raise

class AIAnalysisEngine:
    """Main AI analysis engine with two methods: extraction and reasoning"""
    
    def __init__(self):
        self.client = OpenAIClient()
        self.temp_dir = Path("temp_analysis")
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_script(self, prompt: str, file_content: str, filename: str = "uploaded_file.txt") -> str:
        """Generate Python script for data extraction (extraction method)"""
        
        system_prompt = f"""
        You are a Python script generator. Write a complete, executable Python script that:
        1. Analyzes the provided file content for the query: {prompt}
        2. Processes the data to answer the user's question
        3. Prints clear, formatted results
        4. Handles errors gracefully
        5. Uses try-except blocks around operations
        6. Validates data before processing
        
        The file content will be available as a string variable called 'file_content'.
        
        IMPORTANT FORMATTING RULES:
        - Return ONLY pure Python code
        - Do NOT include markdown formatting like ```
        - Start directly with Python code (import statements, functions, etc.)
        - The script should be completely self-contained
        - Always include proper error handling
        - Process the 'file_content' variable, not file I/O operations
        
        Start your response immediately with Python code, nothing else.
        """
        
        # Truncate file content for context window management
        content_preview = file_content[:2000] + "..." if len(file_content) > 2000 else file_content
        
        user_prompt = f"""
        File content:
        {content_preview}
        
        Query: {prompt}
        
        Generate a Python script to process this data.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.chat_completions_create(
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating script with Azure OpenAI: {e}")
            return f"# Error generating script: {str(e)}\n# Please check Azure OpenAI configuration"
    
    def execute_script_safely(self, script_code: str, file_content: str) -> Dict[str, Any]:
        """Execute generated Python script safely with file content"""
        try:
            # Create a safe execution environment
            safe_globals = {
                'file_content': file_content,
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'enumerate': enumerate,
                    'range': range,
                    'zip': zip,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'sorted': sorted,
                    'any': any,
                    'all': all,
                }
            }
            safe_locals = {}
            
            # Execute script and capture output
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(script_code, safe_globals, safe_locals)
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            return {
                "success": True,
                "stdout": stdout_output,
                "stderr": stderr_output,
                "variables": {k: str(v) for k, v in safe_locals.items() if not k.startswith('_')}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    def process_with_extraction(self, prompt: str, file_content: str, filename: str = "uploaded_file") -> str:
        """Process using extraction method (script generation)"""
        try:
            max_iterations = 3
            
            for iteration in range(max_iterations):
                logger.info(f"Azure OpenAI script generation attempt {iteration + 1}")
                
                # Generate script
                script_code = self.generate_script(prompt, file_content, filename)
                
                if not script_code or "Error generating script" in script_code:
                    continue
                
                # Execute script
                execution_result = self.execute_script_safely(script_code, file_content)
                
                if execution_result["success"]:
                    output = execution_result["stdout"]
                    if output.strip():
                        return f"Analysis Results:\n{output}"
                
                # If script failed, try to get GPT to improve it
                if iteration < max_iterations - 1:
                    logger.warning(f"Script execution failed, refining... (attempt {iteration + 1})")
                    
                    # Ask Azure OpenAI to fix the script
                    fix_prompt = f"""
                    The previous script had an error:
                    {execution_result.get('error', 'Unknown error')}
                    
                    Please provide a corrected Python script for: {prompt}
                    
                    Previous script:
                    {script_code[:1000]}...
                    
                    Generate a fixed version.
                    """
                    
                    messages = [
                        {"role": "system", "content": "You are a Python debugging expert. Fix the script to work correctly."},
                        {"role": "user", "content": fix_prompt}
                    ]
                    
                    try:
                        response = self.client.chat_completions_create(messages=messages, max_tokens=2000)
                        script_code = response.choices[0].message.content
                    except Exception as e:
                        logger.error(f"Error refining script: {e}")
                        break
            
            return f"Script generation completed after {max_iterations} attempts. Please check the results."
            
        except Exception as e:
            logger.error(f"Error in extraction processing: {e}")
            return f"Error in analysis: {str(e)}"
    
    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split document into overlapping chunks for RAG processing"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if chunk]
    
    def find_similar_chunks(self, query_embedding: List[float], chunk_embeddings: List[List[float]], chunks: List[str], top_k: int = 5) -> List[str]:
        """Find most similar chunks using cosine similarity"""
        try:
            query_array = np.array(query_embedding).reshape(1, -1)
            chunk_arrays = np.array(chunk_embeddings)
            
            similarities = cosine_similarity(query_array, chunk_arrays)[0]
            
            # Get top-k most similar chunks
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Filter by similarity threshold
            threshold = 0.7
            relevant_chunks = []
            for idx in top_indices:
                if similarities[idx] >= threshold:
                    relevant_chunks.append(chunks[idx])
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}")
            return chunks[:top_k]  # Fallback to first chunks
    
    def process_with_rag(self, prompt: str, file_content: str, filename: str = "uploaded_file") -> str:
        """Process using RAG method (reasoning with embeddings)"""
        try:
            # Chunk the document
            chunks = self.chunk_document(file_content, chunk_size=1000)
            logger.info(f"Created {len(chunks)} chunks for RAG processing")
            
            if not chunks:
                return "No content available for analysis."
            
            # Create embeddings for chunks
            try:
                chunk_embeddings = self.client.embeddings_create(chunks)
                query_embedding = self.client.embeddings_create([prompt])[0]
            except Exception as e:
                logger.warning(f"Embeddings failed, using first chunks: {e}")
                # Fallback: use first few chunks if embeddings fail
                relevant_chunks = chunks[:5]
            else:
                # Find relevant chunks
                relevant_chunks = self.find_similar_chunks(query_embedding, chunk_embeddings, chunks)
            
            if not relevant_chunks:
                relevant_chunks = chunks[:3]  # Fallback
            
            # Build context
            context = "\n\n".join(relevant_chunks)
            
            # Analyze with context
            analysis_prompt = f"""
            Based on the provided context, please analyze and answer the user's question.
            
            Context:
            {context[:3000]}  # Limit context to manage token usage
            
            User Question: {prompt}
            
            Please provide a comprehensive analysis based on the context above.
            """
            
            messages = [
                {"role": "system", "content": "You are an expert analyst. Provide detailed, accurate analysis based on the provided context."},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self.client.chat_completions_create(
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {e}")
            return f"Error in analysis: {str(e)}"
    
    def analyze(self, prompt: str, method: str, file_content: str, filename: str = "uploaded_file") -> str:
        """Main analysis method - routes to extraction or reasoning"""
        try:
            if method == "extraction":
                return self.process_with_extraction(prompt, file_content, filename)
            elif method == "reasoning":
                return self.process_with_rag(prompt, file_content, filename)
            else:
                raise ValueError(f"Unknown analysis method: {method}")
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return f"Analysis failed: {str(e)}"

# Global AI engine instance
ai_engine = AIAnalysisEngine()

def get_ai_engine() -> AIAnalysisEngine:
    """Get the global AI engine instance"""
    return ai_engine