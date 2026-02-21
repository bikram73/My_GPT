# MyGPT - Multi-Model AI Assistant

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node](https://img.shields.io/badge/node-16+-green.svg)

A complete AI chatbot application with intelligent multi-model routing, authentication, and conversation management.

## Features

✅ **Multi-Model Support** - Automatically routes to the best AI model for your task
✅ **9 Specialized Models** - Coding, math, creative writing, multilingual, and more
✅ **User Authentication** - Register/Login with JWT
✅ **Conversation History** - Save and manage your chats
✅ **Real-time AI Chat** - Fast, responsive interface
✅ **Model Selection** - Choose specific models or use auto-routing
✅ **Responsive Design** - ChatGPT-style modern UI
✅ **Dark Theme** - Easy on the eyes

## Available Models

| Model | Best For | Description |
|-------|----------|-------------|
| **Auto Select** | Everything | Automatically chooses the best model |
| **Mistral 7B** | General chat | ⚡ Fast general-purpose conversations |
| **Llama 3.2 3B** | Quick responses | 💬 Efficient everyday assistant |
| **Qwen Coder 7B** | Programming | 💻 Specialized coding assistant |
| **DeepSeek Coder** | Code debugging | 🔧 Expert code analysis |
| **Qwen Math 7B** | Mathematics | 🧮 Math and logical reasoning |
| **DeepSeek R1** | Complex reasoning | 🤔 Deep analytical thinking |
| **Llama 3.1 8B** | Creative writing | ✍️ Stories, poems, content |
| **Qwen 7B** | Multilingual | 🌍 200+ languages supported |
| **GPT-2** | Fallback | 🔄 Reliable backup model |

## Tech Stack

### Backend
- FastAPI (Python web framework)
- Transformers (Hugging Face)
- PyTorch (Deep learning)
- JWT Authentication
- Bcrypt Password Hashing

### Frontend
- React 19
- Vite
- Tailwind CSS
- Axios
- Lucide Icons

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- 4GB+ RAM (8GB+ recommended)
- Internet connection (for first-time model download)

### Quick Start

#### Step 1: Test the Model (Important!)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python test_model.py
```

This will verify everything works before starting the full app.

#### Step 2: Start Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the backend server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Click "Sign up for free" to create an account
3. Start chatting with the AI
4. Your conversations are automatically saved
5. Click on past conversations in the sidebar to reload them

## Model Configuration

The backend uses GPT-2 by default for quick testing. To use better models:

### Option 1: Llama 3.2 (Recommended)
Edit `backend/main.py` line 32:
```python
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
```
Requires Hugging Face token (free): https://huggingface.co/settings/tokens

### Option 2: DialoGPT (Good for conversations)
```python
MODEL_ID = "microsoft/DialoGPT-medium"
```

### Option 3: GPT-OSS-20B (Powerful but needs 16GB+ RAM/GPU)
```python
MODEL_ID = "openai/gpt-oss-20b"
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Chat
- `POST /chat` - Send message and get AI response
- `GET /conversations` - Get all user conversations
- `GET /conversations/{id}` - Get specific conversation
- `DELETE /conversations/{id}` - Delete conversation

### Health
- `GET /health` - Check API and model status

## Production Deployment

### Backend
1. Change `SECRET_KEY` in `main.py`
2. Use a real database (PostgreSQL/MongoDB) instead of in-memory storage
3. Add rate limiting
4. Use environment variables for configuration
5. Deploy to cloud (AWS, GCP, Azure)

### Frontend
1. Update `API_URL` in `App.jsx` to your backend URL
2. Build for production: `npm run build`
3. Deploy to Vercel, Netlify, or any static hosting

## Troubleshooting

### Model Loading Issues
- Ensure you have enough RAM (8GB minimum)
- Try smaller models like GPT-2 or DialoGPT-small
- Check GPU availability: `torch.cuda.is_available()`

### CORS Errors
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`

### Authentication Issues
- Clear browser localStorage
- Check backend logs for JWT errors

## License

MIT License - Feel free to use for personal or commercial projects

## Credits

Built with ❤️ using open-source AI models and modern web technologies
