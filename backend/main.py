import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import jwt
from passlib.context import CryptContext
import requests

app = FastAPI(title="ChatGPT Clone API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# --- HUGGING FACE API CONFIGURATION ---
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Configuration: Use simple fallback since HF models are deprecated
USE_SERVERLESS = False  # Disabled - models return 410
SERVERLESS_MODEL = "microsoft/DialoGPT-medium"
HF_ROUTER_URL = "https://router.huggingface.co/v1/chat/completions"
USE_SIMPLE_FALLBACK = True  # Always use fallback for now

print("=" * 50)
print("ChatGPT Clone API - Fallback Mode")
print("⚠️ HF Inference API models deprecated (410)")
print("✓ Using enhanced fallback responses")
print("✓ To use real AI: Deploy to Hugging Face Spaces")
print("=" * 50)

# Simple in-memory storage (replace with real database in production)
users_db = {}
conversations_db = {}

# Models
class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model_preference: Optional[str] = None  # Allow users to specify preferred model

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth endpoints
@app.post("/auth/register")
async def register(user: UserRegister):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    users_db[user.email] = {
        "email": user.email,
        "name": user.name,
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    
    token = create_access_token({"sub": user.email})
    return {"token": token, "user": {"email": user.email, "name": user.name}}

@app.post("/auth/login")
async def login(user: UserLogin):
    if user.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    stored_user = users_db[user.email]
    if not pwd_context.verify(user.password, stored_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email})
    return {"token": token, "user": {"email": user.email, "name": stored_user["name"]}}

@app.get("/auth/me")
async def get_current_user(email: str = Depends(verify_token)):
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    user = users_db[email]
    return {"email": user["email"], "name": user["name"]}

# Optional token verification for guest users
async def optional_verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    if credentials is None:
        return None  # Guest user
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except:
        return None  # Invalid token, treat as guest

# Enhanced fallback responses when API fails
def get_simple_response(message: str) -> str:
    """Enhanced rule-based responses as fallback"""
    message_lower = message.lower()
    
    # Greetings
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]
    if any(g in message_lower for g in greetings):
        return "Hello! I'm MyGPT, your AI assistant. I'm currently running in fallback mode because Hugging Face Inference API models are deprecated. How can I help you today?"
    
    # How are you
    if "how are you" in message_lower:
        return "I'm doing well, thank you! I'm running in fallback mode right now. For full AI capabilities, this app needs to be deployed to Hugging Face Spaces or use a different API provider."
    
    # Identity questions
    if any(q in message_lower for q in ["your name", "who are you", "what are you"]):
        return "I'm MyGPT, an AI assistant with multi-model support. Currently in fallback mode due to API limitations. I can help with basic questions!"
    
    # Capabilities
    if any(q in message_lower for q in ["what can you do", "help me", "help", "capabilities"]):
        return "I'm designed to help with:\n• General conversation\n• Coding questions (9 specialized models)\n• Math and reasoning\n• Creative writing\n• Multilingual support\n\nNote: Full AI features require deployment to Hugging Face Spaces or a working API endpoint."
    
    # Date/Time
    if any(q in message_lower for q in ["date", "time", "today", "day"]):
        from datetime import datetime
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}. The current time is {now.strftime('%I:%M %p')}."
    
    # Coding questions
    if any(q in message_lower for q in ["code", "python", "javascript", "programming", "function"]):
        return "I can help with coding! However, I'm in fallback mode right now. For full coding assistance with specialized models (Qwen Coder, DeepSeek), please deploy this app to Hugging Face Spaces."
    
    # Math questions
    if any(q in message_lower for q in ["calculate", "math", "solve", "equation"]):
        return "I can help with math! In fallback mode, I have limited capabilities. For advanced math reasoning with DeepSeek R1 or Qwen Math models, deploy to Hugging Face Spaces."
    
    # Questions
    if "?" in message:
        return "That's an interesting question! I'm currently in fallback mode with limited AI capabilities. For intelligent responses powered by 9 specialized models, this app needs to be deployed to Hugging Face Spaces where the Inference API works properly."
    
    # Default
    return "I understand. I'm running in fallback mode right now. For full AI-powered conversations, please deploy this app to Hugging Face Spaces or configure a working API endpoint."

# Helper function for Serverless or Router API
def generate_response(messages: List[dict], model_preference: Optional[str] = None) -> dict:
    """
    Generate AI response using Serverless Inference API or HF Router
    """
    try:
        # Skip API calls - go straight to fallback
        if USE_SIMPLE_FALLBACK:
            last_msg = messages[-1].get("content", "") if messages else ""
            return {
                "content": get_simple_response(last_msg),
                "model_used": "fallback",
                "task_type": "fallback",
                "status": "success"
            }
        
        if USE_SERVERLESS:
            # Use Serverless Inference API - works with basic tokens
            url = f"https://api-inference.huggingface.co/models/{SERVERLESS_MODEL}"
            headers = {
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Build conversation text
            conversation_text = ""
            for msg in messages[-6:]:  # Last 3 exchanges
                if msg.get("role") == "user":
                    conversation_text += f"{msg.get('content', '')}\n"
            
            payload = {
                "inputs": conversation_text,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True
                },
                "options": {
                    "wait_for_model": True
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated = result.get("generated_text", "")
                else:
                    generated = ""
                
                if generated:
                    # Clean up response
                    generated = generated.replace(conversation_text, "").strip()
                    
                    return {
                        "content": generated if generated else "I'm here to help! Could you rephrase that?",
                        "model_used": SERVERLESS_MODEL,
                        "task_type": "general",
                        "status": "success"
                    }
            
            # Handle errors
            if response.status_code == 503:
                if USE_SIMPLE_FALLBACK:
                    last_msg = messages[-1].get("content", "") if messages else ""
                    return {
                        "content": get_simple_response(last_msg),
                        "model_used": "simple_fallback",
                        "task_type": "fallback",
                        "status": "success"
                    }
                return {
                    "content": "⏳ Model is loading (first request takes ~20 seconds). Please try again!",
                    "model_used": "loading",
                    "task_type": "error",
                    "status": "loading"
                }
            elif response.status_code in [401, 403]:
                if USE_SIMPLE_FALLBACK:
                    last_msg = messages[-1].get("content", "") if messages else ""
                    return {
                        "content": get_simple_response(last_msg),
                        "model_used": "simple_fallback",
                        "task_type": "fallback",
                        "status": "success"
                    }
                return {
                    "content": "🔑 API key issue. Please check your Hugging Face token permissions.",
                    "model_used": "error",
                    "task_type": "error",
                    "status": "error"
                }
            elif response.status_code == 410:
                if USE_SIMPLE_FALLBACK:
                    last_msg = messages[-1].get("content", "") if messages else ""
                    return {
                        "content": get_simple_response(last_msg),
                        "model_used": "simple_fallback",
                        "task_type": "fallback",
                        "status": "success"
                    }
                return {
                    "content": "⚠️ Model endpoint deprecated. Using fallback mode.",
                    "model_used": "error",
                    "task_type": "error",
                    "status": "error"
                }
            else:
                if USE_SIMPLE_FALLBACK:
                    last_msg = messages[-1].get("content", "") if messages else ""
                    return {
                        "content": get_simple_response(last_msg),
                        "model_used": "simple_fallback",
                        "task_type": "fallback",
                        "status": "success"
                    }
                error_msg = response.text[:200]
                return {
                    "content": f"⚠️ Error {response.status_code}. Please try again.",
                    "model_used": "error",
                    "task_type": "error",
                    "status": "error"
                }
        
        else:
            # Use HF Router (requires special token permissions)
            headers = {
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            }
            
            formatted_messages = []
            for msg in messages[-10:]:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",
                "messages": formatted_messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(HF_ROUTER_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    if content:
                        return {
                            "content": content.strip(),
                            "model_used": "HF Router",
                            "task_type": "general",
                            "status": "success"
                        }
            
            return {
                "content": f"⚠️ Error {response.status_code}. Router requires special API token permissions.",
                "model_used": "error",
                "task_type": "error",
                "status": "error"
            }
        
    except Exception as e:
        print(f"Exception in generate_response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "content": f"❌ Technical error: {str(e)}",
            "model_used": "error",
            "task_type": "error",
            "status": "error"
        }

# Chat endpoints
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, email: Optional[str] = Depends(optional_verify_token)):
    # For guest users, use temporary ID
    user_id = email if email else "guest"
    
    # Get or create conversation
    conv_id = request.conversation_id or f"{user_id}_{datetime.utcnow().timestamp()}"
    
    if conv_id not in conversations_db:
        conversations_db[conv_id] = {
            "id": conv_id,
            "user_email": user_id,
            "title": request.message[:50],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_guest": email is None
        }
    
    conversation = conversations_db[conv_id]
    
    # Add user message
    user_msg = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    conversation["messages"].append(user_msg)
    
    try:
        # Generate response using multi-model router
        result = generate_response(conversation["messages"], request.model_preference)
        
        response_text = result.get("content", "Error generating response")
        model_used = result.get("model_used", "unknown")
        task_type = result.get("task_type", "general")
        
        # Add assistant message with metadata
        assistant_msg = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": model_used,
            "task_type": task_type
        }
        conversation["messages"].append(assistant_msg)
        conversation["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "response": response_text,
            "conversation_id": conv_id,
            "is_guest": email is None,
            "model_used": model_used,
            "task_type": task_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.get("/conversations")
async def get_conversations(email: str = Depends(verify_token)):
    user_conversations = [
        {
            "id": conv["id"],
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "message_count": len(conv["messages"])
        }
        for conv in conversations_db.values()
        if conv["user_email"] == email
    ]
    return sorted(user_conversations, key=lambda x: x["updated_at"], reverse=True)

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, email: str = Depends(verify_token)):
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations_db[conversation_id]
    if conversation["user_email"] != email:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return conversation

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, email: str = Depends(verify_token)):
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations_db[conversation_id]
    if conversation["user_email"] != email:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del conversations_db[conversation_id]
    return {"message": "Conversation deleted"}

@app.get("/health")
async def health_check():
    if USE_SERVERLESS:
        return {
            "status": "healthy",
            "api": "Serverless Inference API",
            "model": SERVERLESS_MODEL,
            "works_with": "basic API tokens"
        }
    else:
        return {
            "status": "healthy",
            "api": "HF Router",
            "requires": "inference API token permissions"
        }

@app.get("/models")
async def list_models():
    """Get list of all available models and their capabilities"""
    if USE_HF_ROUTER:
        return {
            "mode": "router",
            "message": "Using HF Router for automatic model selection"
        }
    else:
        return {
            "models": model_router.list_available_models(),
            "task_types": [t.value for t in TaskType]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
