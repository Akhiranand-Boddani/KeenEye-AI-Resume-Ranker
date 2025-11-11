import requests
import time
from typing import Dict, Any


class GroqHTTPClient:
    """
    Pure HTTP implementation of Groq API client
    Use this as replacement if groq SDK has issues
    """
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = 3
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if API key is valid"""
        try:
            # Simple test request
            self.generate("Say 'test'", max_tokens=5)
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                raise ValueError("Invalid Groq API key")
    
    def generate(self, prompt: str, max_tokens: int = 1024, 
                 temperature: float = 0.3) -> str:
        """Generate LLM response using HTTP requests"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert HR analyst specializing in resume-job matching."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise Exception(f"Groq HTTP API failed after {self.max_retries} attempts: {str(e)}")
    
    def chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        Compatible with OpenAI-style chat completions
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()


# Test function
def test_groq_http():
    """Test the HTTP client"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return False
    
    try:
        client = GroqHTTPClient(api_key=api_key)
        response = client.generate("Say 'HTTP client working' and nothing else", max_tokens=10)
        
        if "http client working" in response.lower() or "working" in response.lower():
            print("✅ Groq HTTP Client working!")
            print(f"   Response: {response}")
            return True
        else:
            print(f"⚠️ Unexpected response: {response}")
            return False
    
    except Exception as e:
        print(f"❌ Groq HTTP Client failed: {e}")
        return False


if __name__ == "__main__":
    test_groq_http()
