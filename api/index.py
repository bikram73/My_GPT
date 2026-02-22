"""
Minimal Vercel serverless function for MyGPT
Pure Python handler without heavy dependencies
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        self._set_headers()
        
        if self.path == '/health':
            response = {
                "status": "healthy",
                "api": "MyGPT Vercel API",
                "mode": "demo"
            }
        else:
            response = {
                "message": "MyGPT API is running",
                "endpoints": ["/chat (POST)", "/health (GET)"],
                "status": "online"
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                message = data.get('message', '')
                
                # Generate response
                response_text = self.get_simple_response(message)
                
                response = {
                    "response": response_text,
                    "conversation_id": f"guest_{datetime.utcnow().timestamp()}",
                    "is_guest": True,
                    "model_used": "fallback",
                    "task_type": "general"
                }
                
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self._set_headers(500)
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def get_simple_response(self, message: str) -> str:
        """Enhanced fallback responses"""
        message_lower = message.lower()
        
        if any(g in message_lower for g in ["hi", "hello", "hey", "greetings"]):
            return "Hello! I'm MyGPT, your AI assistant. How can I help you today?"
        
        if "how are you" in message_lower:
            return "I'm doing well, thank you! How can I assist you?"
        
        if any(q in message_lower for q in ["your name", "who are you", "what are you"]):
            return "I'm MyGPT, an AI assistant with multi-model support. I can help with coding, math, creative writing, and more!"
        
        if any(q in message_lower for q in ["what can you do", "help me", "help", "capabilities"]):
            return "I can help with:\n• General conversation\n• Coding questions\n• Math and reasoning\n• Creative writing\n• Multilingual support\n\nNote: Currently in demo mode on Vercel."
        
        if any(q in message_lower for q in ["date", "time", "today", "day"]):
            now = datetime.now()
            return f"Today is {now.strftime('%A, %B %d, %Y')}. The current time is {now.strftime('%I:%M %p')}."
        
        if any(q in message_lower for q in ["code", "python", "javascript", "programming"]):
            return "I can help with coding! Ask me about Python, JavaScript, or any programming language."
        
        if "?" in message:
            return "That's an interesting question! I'm here to help. Could you provide more details?"
        
        return "I understand. How can I assist you further?"

