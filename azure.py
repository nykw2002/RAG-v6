#!/usr/bin/env python3
"""
Complete Azure OpenAI API Call Setup
Environment Variables + API Implementation + Usage Example
"""

# =============================================================================
# 1. REQUIRED ENVIRONMENT VARIABLES (.env file)
# =============================================================================

"""
# Authentication Variables (Required)
PING_FED_URL=your_ping_federation_oauth_endpoint
KGW_CLIENT_ID=your_client_id  
KGW_CLIENT_SECRET=your_client_secret

# Azure OpenAI Configuration (Required)
KGW_ENDPOINT=your_azure_openai_endpoint
AOAI_API_VERSION=your_api_version
CHAT_MODEL_DEPLOYMENT_NAME=your_gpt4o_deployment_name

# Optional Variables (for O3-mini support)
GPT_O3_MINI_DEPLOYMENT_NAME=your_o3_mini_deployment_name
USE_O3_MINI=false
"""

# =============================================================================
# 2. COMPLETE API IMPLEMENTATION
# =============================================================================

import os
import time
import requests
import json
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    """Azure OpenAI API client"""
    
    def __init__(self):
        self.auth = AzureOpenAIAuth()
        self.endpoint = os.getenv('KGW_ENDPOINT')
        self.api_version = os.getenv('AOAI_API_VERSION')
        self.chat_deployment = os.getenv('CHAT_MODEL_DEPLOYMENT_NAME')
        self.o3_mini_deployment = os.getenv('GPT_O3_MINI_DEPLOYMENT_NAME')
        self.use_o3_mini = os.getenv('USE_O3_MINI', 'false').lower() == 'true'
        
        if not all([self.endpoint, self.api_version, self.chat_deployment]):
            raise ValueError("Missing config: KGW_ENDPOINT, AOAI_API_VERSION, CHAT_MODEL_DEPLOYMENT_NAME")
        
        # Choose deployment (GPT-4o vs O3-mini)
        if self.use_o3_mini and self.o3_mini_deployment:
            self.current_deployment = self.o3_mini_deployment
            print(f"✅ Using O3-mini: {self.current_deployment}")
        else:
            self.current_deployment = self.chat_deployment
            print(f"✅ Using GPT-4o: {self.current_deployment}")
    
    def make_api_call(self, messages: List[Dict], max_tokens: int = 4000, temperature: float = 0.1) -> str:
        """
        Core API call method - This is what actually calls Azure OpenAI
        """
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
                    return result['choices'][0]['message']['content']
                    
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
                    return error_msg
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    error_msg = f"Request failed after {max_retries} attempts: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    return error_msg
                    
                # Wait before retry
                wait_time = (2 ** attempt) + 2
                print(f"Request error, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        return f"Failed after {max_retries} attempts"
    
    def chat(self, system_prompt: str, user_message: str, max_tokens: int = 4000) -> str:
        """Simple chat interface"""
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]
        return self.make_api_call(messages, max_tokens)
    
    def chat_with_history(self, messages: List[Dict], max_tokens: int = 4000) -> str:
        """Chat with conversation history"""
        return self.make_api_call(messages, max_tokens)

# =============================================================================
# 3. USAGE EXAMPLES
# =============================================================================

def example_usage():
    """Example of how to use the Azure OpenAI client"""
    
    try:
        # Initialize client
        client = AzureOpenAIClient()
        
        # Example 1: Simple chat
        print("Example 1: Simple Chat")
        system = "You are a helpful assistant."
        user_msg = "Explain machine learning in simple terms."
        
        response = client.chat(system, user_msg)
        print(f"Response: {response[:200]}...")
        
        # Example 2: Chat with conversation history
        print("\nExample 2: Conversation History")
        messages = [
            {'role': 'system', 'content': 'You are a coding assistant.'},
            {'role': 'user', 'content': 'Write a Python function to calculate fibonacci.'},
            {'role': 'assistant', 'content': 'Here is a fibonacci function...'},
            {'role': 'user', 'content': 'Now optimize it with memoization.'}
        ]
        
        response = client.chat_with_history(messages)
        print(f"Response: {response[:200]}...")
        
        # Example 3: Document summarization (like your summary1.py)
        print("\nExample 3: Document Summarization")
        doc_content = "Your document content here..."
        
        summary_messages = [
            {'role': 'system', 'content': 'You are a document summarizer. Create comprehensive summaries.'},
            {'role': 'user', 'content': f'Summarize this document section:\n\n{doc_content}'}
        ]
        
        summary = client.chat_with_history(summary_messages, max_tokens=1500)
        print(f"Summary: {summary[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")

# =============================================================================
# 4. CONFIGURATION SUMMARY
# =============================================================================

def print_config_info():
    """Print current configuration"""
    print("="*60)
    print("AZURE OPENAI CONFIGURATION")
    print("="*60)
    print(f"Auth Endpoint: {os.getenv('PING_FED_URL', 'NOT SET')}")
    print(f"Client ID: {'SET' if os.getenv('KGW_CLIENT_ID') else 'NOT SET'}")
    print(f"Client Secret: {'SET' if os.getenv('KGW_CLIENT_SECRET') else 'NOT SET'}")
    print(f"Azure Endpoint: {os.getenv('KGW_ENDPOINT', 'NOT SET')}")
    print(f"API Version: {os.getenv('AOAI_API_VERSION', 'NOT SET')}")
    print(f"GPT-4o Deployment: {os.getenv('CHAT_MODEL_DEPLOYMENT_NAME', 'NOT SET')}")
    print(f"O3-mini Deployment: {os.getenv('GPT_O3_MINI_DEPLOYMENT_NAME', 'NOT SET')}")
    print(f"Use O3-mini: {os.getenv('USE_O3_MINI', 'false')}")
    print("="*60)

if __name__ == "__main__":
    print_config_info()
    example_usage()