import gradio as gr
import requests
import json
from datetime import datetime

# Hugging Face API Configuration
HF_API_KEY = "your-hugging-face-api-key-here"
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct/v1/chat/completions"

# Store conversation history
conversation_history = []

def generate_response(message, context_messages):
    """
    Generate AI response using Hugging Face Inference API
    """
    # Build full message list
    messages = context_messages + [{"role": "user", "content": message}]
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": messages[-10:],  # Last 5 exchanges
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": False
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Parse OpenAI-compatible response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if content:
                    return content.strip()
            
            return "I received your message but couldn't generate a response. Please try again."
            
        elif response.status_code == 503:
            return "⏳ The AI model is loading (first request takes ~20 seconds). Please try again!"
        elif response.status_code == 401 or response.status_code == 403:
            return "🔑 API authentication issue. Please check the token permissions."
        else:
            return f"⚠️ Error {response.status_code}. Please try again."
            
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

# Create Gradio Interface
with gr.Blocks(title="ChatGPT Clone") as demo:
    gr.Markdown(
        """
        # 🤖 ChatGPT Clone
        ### Powered by Llama 3.2 via Hugging Face
        
        Ask me anything! I'm here to help.
        """
    )
    
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        height=500,
        avatar_images=(None, "https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png"),
    )
    
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
        **Note:** First response may take 20-30 seconds as the model loads. Subsequent responses are faster.
        
        **Model:** meta-llama/Llama-3.2-1B-Instruct  
        **API:** Hugging Face Inference API
        """
    )
    
    def user_message(message, history):
        # Gradio 6.0 uses message format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        if history is None:
            history = []
        history.append({"role": "user", "content": message})
        return "", history
    
    def bot_response(history):
        if not history or history[-1]["role"] != "user":
            return history
        
        user_msg = history[-1]["content"]
        
        # Get conversation context (exclude the last user message we're responding to)
        context_messages = []
        for msg in history[:-1]:
            context_messages.append(msg)
        
        # Generate response
        bot_msg = generate_response(user_msg, context_messages)
        
        # Add assistant response
        history.append({"role": "assistant", "content": bot_msg})
        return history
    
    def clear_chat():
        return []
    
    def retry_last(history):
        if history and len(history) >= 2:
            # Remove last assistant response
            if history[-1]["role"] == "assistant":
                return history[:-1]
        return history
    
    # Event handlers
    txt.submit(user_message, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    submit_btn.click(user_message, [txt, chatbot], [txt, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    clear_btn.click(clear_chat, None, chatbot, queue=False)
    retry_btn.click(retry_last, chatbot, chatbot, queue=False).then(
        bot_response, chatbot, chatbot
    )

# Launch the app
if __name__ == "__main__":
    demo.queue()
    demo.launch(theme=gr.themes.Soft())
