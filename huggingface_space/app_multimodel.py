"""
Multi-Model ChatGPT Clone for Hugging Face Spaces
Intelligently routes to different models based on task type
"""

import gradio as gr
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Hugging Face API Configuration
HF_API_KEY = "your-hugging-face-api-key-here"

class TaskType(Enum):
    """Task categories for model routing"""
    GENERAL_CHAT = "general_chat"
    CODING = "coding"
    REASONING = "reasoning"
    MATH = "math"
    CREATIVE = "creative"
    MULTILINGUAL = "multilingual"
    FAST_RESPONSE = "fast_response"

# Model registry
MODELS = {
    "Mistral 7B (Fast)": {
        "id": "mistralai/Mistral-7B-Instruct-v0.2",
        "tasks": ["general_chat", "fast_response"],
        "format": "standard",
        "description": "⚡ Fast general-purpose chat"
    },
    "Llama 3.2 1B": {
        "id": "meta-llama/Llama-3.2-1B-Instruct",
        "tasks": ["general_chat", "fast_response"],
        "format": "chat",
        "description": "💬 Efficient conversational AI"
    },
    "Qwen Coder 7B": {
        "id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "tasks": ["coding"],
        "format": "chat",
        "description": "💻 Specialized coding assistant"
    },
    "DeepSeek R1 7B": {
        "id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "tasks": ["reasoning", "math"],
        "format": "chat",
        "description": "🧮 Math & reasoning expert"
    },
    "Qwen 7B": {
        "id": "Qwen/Qwen2.5-7B-Instruct",
        "tasks": ["multilingual", "general_chat"],
        "format": "chat",
        "description": "🌍 Multilingual support"
    }
}

def detect_task_type(message: str) -> str:
    """Detect the task type from message content"""
    message_lower = message.lower()
    
    # Coding detection
    code_keywords = ["code", "function", "class", "debug", "error", "python", "javascript", 
                    "java", "c++", "programming", "algorithm", "api", "sql", "html", "css"]
    if any(keyword in message_lower for keyword in code_keywords):
        return "coding"
    
    # Math/Reasoning detection
    math_keywords = ["calculate", "solve", "equation", "math", "proof", "logic", 
                    "reasoning", "analyze", "theorem", "formula"]
    if any(keyword in message_lower for keyword in math_keywords):
        return "reasoning"
    
    # Creative writing detection
    creative_keywords = ["write", "story", "poem", "creative", "imagine", "describe",
                       "narrative", "character", "plot"]
    if any(keyword in message_lower for keyword in creative_keywords):
        return "creative"
    
    # Multilingual detection
    if any(ord(char) > 127 for char in message):
        return "multilingual"
    
    # Fast response for short queries
    if len(message.split()) < 10:
        return "fast_response"
    
    return "general_chat"

def select_model(task_type: str, model_override: Optional[str] = None) -> Tuple[str, Dict]:
    """Select the best model for the task"""
    if model_override and model_override in MODELS:
        return model_override, MODELS[model_override]
    
    # Find models that support this task
    for name, config in MODELS.items():
        if task_type in config["tasks"]:
            return name, config
    
    # Default fallback
    return "Mistral 7B (Fast)", MODELS["Mistral 7B (Fast)"]

def call_chat_api(model_id: str, messages: List[Dict], max_tokens: int = 500) -> str:
    """Call OpenAI-compatible chat API"""
    url = f"https://api-inference.huggingface.co/models/{model_id}/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": messages[-10:],
        "max_tokens": max_tokens,
        "temperature": 0.7,
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
                    return content.strip()
        
        return handle_error(response.status_code)
        
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

def call_standard_api(model_id: str, messages: List[Dict], max_tokens: int = 500) -> str:
    """Call standard HF Inference API"""
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
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
            "temperature": 0.7,
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
                generated = generated.strip()
                if "\nUser:" in generated:
                    generated = generated.split("\nUser:")[0].strip()
                return generated
        
        return handle_error(response.status_code)
        
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

def handle_error(status_code: int) -> str:
    """Handle API errors"""
    error_messages = {
        503: "⏳ Model is loading (first request takes ~20 seconds). Please try again!",
        401: "🔑 API authentication failed.",
        403: "🔑 API authentication failed.",
        429: "⏸️ Rate limit reached. Please wait a moment.",
    }
    return error_messages.get(status_code, f"⚠️ Error {status_code}. Please try again.")

def generate_response(message: str, history: List[Dict], model_choice: str = "Auto") -> Tuple[str, str, str]:
    """
    Generate AI response with automatic model selection
    Returns: (response_text, model_used, task_detected)
    """
    # Detect task type
    task_type = detect_task_type(message)
    
    # Select model
    model_override = None if model_choice == "Auto" else model_choice
    model_name, model_config = select_model(task_type, model_override)
    
    # Build messages
    messages = []
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": message})
    
    # Generate response
    if model_config["format"] == "chat":
        response = call_chat_api(model_config["id"], messages)
    else:
        response = call_standard_api(model_config["id"], messages)
    
    return response, model_name, task_type

# Create Gradio Interface
with gr.Blocks(title="Multi-Model ChatGPT Clone", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🤖 Multi-Model ChatGPT Clone
        ### Intelligent AI that automatically selects the best model for your task
        
        💻 **Coding?** → Uses specialized coding models  
        🧮 **Math?** → Routes to reasoning experts  
        💬 **Chat?** → Fast general-purpose models  
        🌍 **Multilingual?** → Language-optimized models
        """
    )
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                height=500,
                avatar_images=(None, "https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png"),
            )
        
        with gr.Column(scale=1):
            model_selector = gr.Dropdown(
                choices=["Auto"] + list(MODELS.keys()),
                value="Auto",
                label="Model Selection",
                info="Auto = Smart routing"
            )
            
            current_model = gr.Textbox(
                label="Current Model",
                value="Not started",
                interactive=False
            )
            
            task_detected = gr.Textbox(
                label="Task Detected",
                value="None",
                interactive=False
            )
            
            gr.Markdown(
                """
                ### Available Models:
                """
            )
            
            for name, config in MODELS.items():
                gr.Markdown(f"**{name}**  \n{config['description']}")
    
    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Type your message here...",
            container=False,
        )
        submit_btn = gr.Button("Send", scale=1, variant="primary")
    
    with gr.Row():
        clear_btn = gr.Button("🗑️ Clear Chat")
        retry_btn = gr.Button("🔄 Retry")
    
    gr.Markdown(
        """
        ---
        **Note:** First response may take 20-30 seconds as models load. Subsequent responses are faster.
        
        **Try asking:**
        - "Write a Python function to sort a list" (→ Coding model)
        - "Solve: 2x + 5 = 15" (→ Math model)
        - "Tell me a story about a robot" (→ Creative model)
        - "你好，你会说中文吗？" (→ Multilingual model)
        """
    )
    
    def user_message(message, history, model_choice):
        if history is None:
            history = []
        
        # Generate response
        response, model_used, task = generate_response(message, history, model_choice)
        
        # Add to history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        
        return "", history, model_used, task.replace("_", " ").title()
    
    def clear_chat():
        return [], "Not started", "None"
    
    def retry_last(history):
        if history and len(history) >= 2:
            if history[-1]["role"] == "assistant":
                return history[:-1]
        return history
    
    # Event handlers
    txt.submit(
        user_message, 
        [txt, chatbot, model_selector], 
        [txt, chatbot, current_model, task_detected], 
        queue=False
    )
    
    submit_btn.click(
        user_message, 
        [txt, chatbot, model_selector], 
        [txt, chatbot, current_model, task_detected], 
        queue=False
    )
    
    clear_btn.click(clear_chat, None, [chatbot, current_model, task_detected], queue=False)
    
    retry_btn.click(retry_last, chatbot, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    demo.queue()
    demo.launch()
