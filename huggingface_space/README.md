---
title: ChatGPT Clone
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
---

# ChatGPT Clone

A ChatGPT-style interface powered by Llama 3.2 via Hugging Face Inference API.

## Features

- 💬 Real-time chat interface
- 🧠 Powered by Llama 3.2-1B-Instruct
- 🎨 Clean, modern UI
- 📝 Conversation history
- 🔄 Retry and clear options

## Usage

Simply type your message and press Enter or click Send. The AI will respond to your questions and engage in conversation.

**Note:** The first response may take 20-30 seconds as the model loads. Subsequent responses are much faster.

## Technology

- **Frontend:** Gradio
- **Model:** meta-llama/Llama-3.2-1B-Instruct
- **API:** Hugging Face Inference API
- **Deployment:** Hugging Face Spaces

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:7860 in your browser.
