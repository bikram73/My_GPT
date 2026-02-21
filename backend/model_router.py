"""
Multi-Model Router for Hugging Face Inference API
Routes requests to the best model based on task type and requirements
"""

import os
import requests
from typing import List, Dict, Optional, Tuple
from enum import Enum

class TaskType(Enum):
    """Task categories for model routing"""
    GENERAL_CHAT = "general_chat"
    CODING = "coding"
    REASONING = "reasoning"
    MATH = "math"
    CREATIVE = "creative"
    MULTILINGUAL = "multilingual"
    VISION = "vision"
    FAST_RESPONSE = "fast_response"

class ModelRouter:
    """
    Intelligent model router that selects the best Hugging Face model
    based on task requirements, context, and availability
    """
    
    def __init__(self, hf_api_key: str):
        self.hf_api_key = hf_api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Model registry with capabilities and endpoints
        # Using WORKING models that are available on HF Inference API
        self.models = {
            # Fast & Efficient Models - WORKING
            "mistral-7b": {
                "id": "mistralai/Mistral-7B-Instruct-v0.3",
                "tasks": [TaskType.GENERAL_CHAT, TaskType.FAST_RESPONSE],
                "priority": 1,
                "format": "chat"
            },
            "llama-3.2-3b": {
                "id": "meta-llama/Llama-3.2-3B-Instruct",
                "tasks": [TaskType.GENERAL_CHAT, TaskType.FAST_RESPONSE],
                "priority": 2,
                "format": "chat"
            },
            
            # Coding Specialists - WORKING
            "qwen-coder-7b": {
                "id": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "tasks": [TaskType.CODING],
                "priority": 1,
                "format": "chat"
            },
            "deepseek-coder": {
                "id": "deepseek-ai/deepseek-coder-6.7b-instruct",
                "tasks": [TaskType.CODING],
                "priority": 2,
                "format": "chat"
            },
            
            # Reasoning & Math - WORKING
            "qwen-math": {
                "id": "Qwen/Qwen2.5-Math-7B-Instruct",
                "tasks": [TaskType.REASONING, TaskType.MATH],
                "priority": 1,
                "format": "chat"
            },
            "deepseek-r1": {
                "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "tasks": [TaskType.REASONING, TaskType.MATH],
                "priority": 2,
                "format": "chat"
            },
            
            # Creative Writing - WORKING
            "llama-8b": {
                "id": "meta-llama/Llama-3.1-8B-Instruct",
                "tasks": [TaskType.CREATIVE, TaskType.GENERAL_CHAT],
                "priority": 1,
                "format": "chat"
            },
            
            # Multilingual - WORKING
            "qwen-multilingual": {
                "id": "Qwen/Qwen2.5-7B-Instruct",
                "tasks": [TaskType.MULTILINGUAL, TaskType.GENERAL_CHAT],
                "priority": 1,
                "format": "chat"
            },
            
            # Backup - Simple and reliable
            "gpt2": {
                "id": "openai-community/gpt2",
                "tasks": [TaskType.GENERAL_CHAT, TaskType.FAST_RESPONSE],
                "priority": 10,
                "format": "standard"
            }
        }
        
        # Default fallback model - most reliable
        self.default_model = "llama-3.2-3b"
    
    def detect_task_type(self, message: str, conversation_history: List[Dict]) -> TaskType:
        """
        Analyze message content to determine the best task type
        """
        message_lower = message.lower()
        
        # Coding detection
        code_keywords = ["code", "function", "class", "debug", "error", "python", "javascript", 
                        "java", "c++", "programming", "algorithm", "api", "sql", "html", "css"]
        if any(keyword in message_lower for keyword in code_keywords):
            return TaskType.CODING
        
        # Math/Reasoning detection
        math_keywords = ["calculate", "solve", "equation", "math", "proof", "logic", 
                        "reasoning", "analyze", "theorem", "formula"]
        if any(keyword in message_lower for keyword in math_keywords):
            return TaskType.REASONING
        
        # Creative writing detection
        creative_keywords = ["write", "story", "poem", "creative", "imagine", "describe",
                           "narrative", "character", "plot"]
        if any(keyword in message_lower for keyword in creative_keywords):
            return TaskType.CREATIVE
        
        # Multilingual detection (non-English characters)
        if any(ord(char) > 127 for char in message):
            return TaskType.MULTILINGUAL
        
        # Fast response for short queries
        if len(message.split()) < 10:
            return TaskType.FAST_RESPONSE
        
        return TaskType.GENERAL_CHAT
    
    def select_model(self, task_type: TaskType, fallback: bool = True) -> Tuple[str, Dict]:
        """
        Select the best model for the given task type
        Returns: (model_key, model_config)
        """
        # Find models that support this task
        candidates = [
            (key, config) for key, config in self.models.items()
            if task_type in config["tasks"]
        ]
        
        if not candidates and fallback:
            # Use default model as fallback
            return self.default_model, self.models[self.default_model]
        
        # Sort by priority (lower is better)
        candidates.sort(key=lambda x: x[1]["priority"])
        
        return candidates[0] if candidates else (self.default_model, self.models[self.default_model])
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        task_type: Optional[TaskType] = None,
        model_override: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate response using the appropriate model
        
        Args:
            messages: Conversation history in chat format
            task_type: Optional task type override
            model_override: Optional specific model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dict with 'content', 'model_used', 'task_type'
        """
        # Detect task type if not provided
        if task_type is None and messages:
            last_message = messages[-1]["content"]
            task_type = self.detect_task_type(last_message, messages[:-1])
        
        # Select model
        if model_override and model_override in self.models:
            model_key = model_override
            model_config = self.models[model_override]
        else:
            model_key, model_config = self.select_model(task_type or TaskType.GENERAL_CHAT)
        
        model_id = model_config["id"]
        format_type = model_config["format"]
        
        print(f"🎯 Task: {task_type.value if task_type else 'general'}")
        print(f"🤖 Selected Model: {model_key} ({model_id})")
        
        # Call appropriate API format
        if format_type == "chat":
            return self._call_chat_api(model_id, messages, max_tokens, temperature, model_key, task_type)
        else:
            return self._call_standard_api(model_id, messages, max_tokens, temperature, model_key, task_type)
    
    def _call_chat_api(
        self, 
        model_id: str, 
        messages: List[Dict], 
        max_tokens: int, 
        temperature: float,
        model_key: str,
        task_type: Optional[TaskType]
    ) -> Dict:
        """Call OpenAI-compatible chat completion API"""
        url = f"{self.base_url}/{model_id}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages[-10:],  # Last 5 exchanges
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    if content:
                        return {
                            "content": content.strip(),
                            "model_used": model_key,
                            "model_id": model_id,
                            "task_type": task_type.value if task_type else "general",
                            "status": "success"
                        }
            
            return self._handle_error(response.status_code, response.text, model_key)
            
        except Exception as e:
            return {
                "content": f"❌ Error: {str(e)[:100]}",
                "model_used": model_key,
                "model_id": model_id,
                "task_type": task_type.value if task_type else "general",
                "status": "error"
            }
    
    def _call_standard_api(
        self, 
        model_id: str, 
        messages: List[Dict], 
        max_tokens: int, 
        temperature: float,
        model_key: str,
        task_type: Optional[TaskType]
    ) -> Dict:
        """Call standard HF Inference API"""
        url = f"{self.base_url}/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build conversation text
        conversation_text = ""
        for msg in messages[-6:]:
            if msg["role"] == "user":
                conversation_text += f"User: {msg['content']}\n"
            else:
                conversation_text += f"Assistant: {msg['content']}\n"
        conversation_text += "Assistant:"
        
        payload = {
            "inputs": conversation_text,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated = result.get("generated_text", "")
                else:
                    generated = ""
                
                if generated:
                    # Clean up response
                    generated = generated.strip()
                    if "\nUser:" in generated:
                        generated = generated.split("\nUser:")[0].strip()
                    
                    return {
                        "content": generated,
                        "model_used": model_key,
                        "model_id": model_id,
                        "task_type": task_type.value if task_type else "general",
                        "status": "success"
                    }
            
            return self._handle_error(response.status_code, response.text, model_key)
            
        except Exception as e:
            return {
                "content": f"❌ Error: {str(e)[:100]}",
                "model_used": model_key,
                "model_id": model_id,
                "task_type": task_type.value if task_type else "general",
                "status": "error"
            }
    
    def _handle_error(self, status_code: int, error_text: str, model_key: str) -> Dict:
        """Handle API errors with user-friendly messages"""
        error_messages = {
            503: "⏳ Model is loading (first request takes ~20 seconds). Please try again!",
            401: "🔑 API authentication failed. Please check your Hugging Face token.",
            403: "🔑 API authentication failed. Please check your Hugging Face token.",
            429: "⏸️ Rate limit reached. Please wait a moment and try again.",
            410: "⚠️ Model endpoint is no longer available. Trying fallback model..."
        }
        
        content = error_messages.get(status_code, f"⚠️ AI service error ({status_code}). Please try again.")
        
        return {
            "content": content,
            "model_used": model_key,
            "task_type": "error",
            "status": "error",
            "error_code": status_code
        }
    
    def list_available_models(self) -> List[Dict]:
        """Get list of all available models with their capabilities"""
        return [
            {
                "key": key,
                "id": config["id"],
                "tasks": [t.value for t in config["tasks"]],
                "priority": config["priority"]
            }
            for key, config in self.models.items()
        ]
