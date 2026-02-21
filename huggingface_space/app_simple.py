import gradio as gr
import requests

# Hugging Face API Configuration
HF_API_KEY = "your-hugging-face-api-key-here"
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct/v1/chat/completions"

def chat(message, history):
    """Generate AI response"""
    # Build messages
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})
    
    # Call API
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7,
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if content:
                    return content.strip()
        elif response.status_code == 503:
            return "⏳ Model loading... Please try again in 20 seconds!"
        
        return f"⚠️ Error {response.status_code}. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

# Create simple chat interface
demo = gr.ChatInterface(
    fn=chat,
    title="🤖 ChatGPT Clone",
    description="Powered by Llama 3.2 via Hugging Face Inference API",
    examples=["Hello!", "What is AI?", "Tell me a joke"],
    retry_btn="🔄 Retry",
    undo_btn="↩️ Undo",
    clear_btn="🗑️ Clear",
)

if __name__ == "__main__":
    demo.launch()
