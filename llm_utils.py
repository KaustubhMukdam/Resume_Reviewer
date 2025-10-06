import os
import requests
import json
from groq import Groq

# Available model configurations
AVAILABLE_MODELS = {
    "local": {
        "llama3": "llama3",
        "mistral": "mistral", 
        "phi3": "phi3",
        "phi3.5": "phi3.5:3.8b",
        "deepseek-coder": "deepseek-coder:6.7b",
        "qwen2.5-coder": "qwen2.5-coder:7b"
    },
    "groq": {
        "llama-3.1-8b-instant": "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
        "llama-4-maverick-17b": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "gpt-oss-20b": "openai/gpt-oss-20b",
        "gpt-oss-120b": "openai/gpt-oss-120b",
        "compound-mini": "groq/compound-mini",
        "compound": "groq/compound",
        "qwen3-32b": "qwen/qwen3-32b"
    }
}

def list_available_models():
    """Display all available models for user selection"""
    print("\n=== AVAILABLE MODELS ===")
    print("LOCAL MODELS (via Ollama):")
    for key, model in AVAILABLE_MODELS["local"].items():
        print(f"  - {key}: {model}")
    print("\nGROQ API MODELS:")
    for key, model in AVAILABLE_MODELS["groq"].items():
        print(f"  - {key}: {model}")
    print("="*30)

def generate_feedback_groq(prompt, model="llama3-70b-8192"):
    """Generate feedback using Groq API"""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI resume reviewer. Provide detailed, actionable feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=model,
            temperature=0.3,
            max_tokens=1024
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error with Groq API: {str(e)}"

def generate_feedback_local(prompt, model="llama3", ollama_url="http://localhost:11434"):
    """Generate feedback using local Ollama models"""
    try:
        data = {
            "model": model,
            "prompt": f"""You are an expert AI resume reviewer. Provide detailed, actionable feedback.

{prompt}

Please provide your response in the following format:
STRENGTHS:
- [List key strengths]

WEAKNESSES:
- [List areas for improvement]

SUGGESTIONS:
- [Provide specific actionable recommendations]
""",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1024
            }
        }
        
        response = requests.post(f"{ollama_url}/api/generate", json=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response generated')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error with local model: {str(e)}"

def generate_feedback(prompt, provider="local", model_key="llama3"):
    """
    Generate feedback using specified provider and model
    Args:
        prompt: The feedback prompt
        provider: "local" or "groq"
        model_key: Key from AVAILABLE_MODELS dict
    """
    if provider.lower() == "local":
        if model_key not in AVAILABLE_MODELS["local"]:
            print(f"Warning: {model_key} not found in local models, using llama3")
            model_key = "llama3"
        model_name = AVAILABLE_MODELS["local"][model_key]
        return generate_feedback_local(prompt, model=model_name)
    
    elif provider.lower() == "groq":
        if model_key not in AVAILABLE_MODELS["groq"]:
            print(f"Warning: {model_key} not found in Groq models, using llama3-70b")
            model_key = "llama3-70b"
        model_name = AVAILABLE_MODELS["groq"][model_key]
        return generate_feedback_groq(prompt, model=model_name)
    
    else:
        raise ValueError("Provider must be 'local' or 'groq'")
