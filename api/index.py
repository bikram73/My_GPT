"""
Minimal Vercel serverless function for MyGPT
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime

app = FastAPI(title="MyGPT API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model_preference: Optional[str] = None

# Simple storage
conversations_db = {}

def get_simple_response(message: str) -> str:
    """Enhanced fallback responses"""
    message_lower = message.lower()
    
    if any(g in message_lower for g in ["hi", "hello", "hey", "greetings"]):
        return "Hello! I'm MyGPT, your AI assistant. How can I help you today?"
    
    if "how are you" in message_lower:
        return "I'm doing well, thank you! How can I assist you?"
    
    if any(q in message_lower for q in ["your name", "who are you", "what are you"]):
        return "I'm MyGPT, an AI assistant with multi-model support. I can help with coding, math, creative writing, and more!"
    
    if any(q in message_lower for q in ["what can you do", "help me", "help", "capabilities"]):
        return "I can help with:\n• General conversation\n• Coding questions\n• Math and reasoning\n• Creative writing\n• Multilingual support\n\nNote: Currently in demo mode. Full AI features coming soon!"
    
    if any(q in message_lower for q in ["date", "time", "today", "day"]):
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}. The current time is {now.strftime('%I:%M %p')}."
    
    if any(q in message_lower for q in ["code", "python", "javascript", "programming"]):
        return "I can help with coding! Ask me about Python, JavaScript, or any programming language."
    
    if "?" in message:
        return "That's an interesting question! I'm here to help. Could you provide more details?"
    
    return "I understand. How can I assist you further?"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    conv_id = request.conversation_id or f"guest_{datetime.utcnow().timestamp()}"
    
    if conv_id not in conversations_db:
        conversations_db[conv_id] = {
            "id": conv_id,
            "messages": [],
            "created_at": datetime.utcnow().isoformat()
        }
    
    conversation = conversations_db[conv_id]
    
    # Add user message
    user_msg = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    conversation["messages"].append(user_msg)
    
    # Generate response
    response_text = get_simple_response(request.message)
    
    # Add assistant message
    assistant_msg = {
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.utcnow().isoformat()
    }
    conversation["messages"].append(assistant_msg)
    
    return {
        "response": response_text,
        "conversation_id": conv_id,
        "is_guest": True,
        "model_used": "fallback",
        "task_type": "general"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api": "MyGPT Vercel API",
        "mode": "demo"
    }

@app.get("/")
async def root():
    return {
        "message": "MyGPT API is running",
        "endpoints": ["/chat", "/health"],
        "status": "online"
    }

# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
