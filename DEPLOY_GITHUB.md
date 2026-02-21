# Deploy MyGPT to GitHub

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit: MyGPT with multi-model support"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `mygpt` (or your preferred name)
3. Description: "AI chatbot with multi-model support powered by Hugging Face"
4. Choose Public or Private
5. **DO NOT** initialize with README (you already have one)
6. Click "Create repository"

### 1.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/mygpt.git
git branch -M main
git push -u origin main
```

## Step 2: Secure Your API Keys

### 2.1 Update .env.example
The `.env.example` file is already configured. Users will need to:
1. Copy `.env.example` to `.env`
2. Add their own Hugging Face API key

### 2.2 Verify .gitignore
Make sure `.env` is in `.gitignore` (already done)

## Step 3: Update README for GitHub

Your README.md already has installation instructions. Add this badge at the top:

```markdown
# MyGPT - Multi-Model AI Assistant

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node](https://img.shields.io/badge/node-16+-green.svg)

[Live Demo](#) | [Documentation](#) | [Report Bug](https://github.com/YOUR_USERNAME/mygpt/issues)
```

## Step 4: Deployment Options

### Option A: Deploy Backend to Render (Free)

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: mygpt-backend
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python main.py`
   - **Environment Variables**:
     - `HF_API_KEY`: your-hugging-face-key
     - `SECRET_KEY`: generate-random-string

### Option B: Deploy Backend to Railway (Free)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables:
   - `HF_API_KEY`
   - `SECRET_KEY`
5. Railway will auto-detect Python and deploy

### Option C: Deploy Frontend to Vercel (Free)

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**:
     - `VITE_API_URL`: your-backend-url (from Render/Railway)

### Option D: Deploy Frontend to Netlify (Free)

1. Go to https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect GitHub
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Environment variables**:
     - `VITE_API_URL`: your-backend-url

## Step 5: Update Frontend API URL

After deploying backend, update `frontend/src/App.jsx`:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Then set environment variable in Vercel/Netlify:
```
VITE_API_URL=https://your-backend.onrender.com
```

## Step 6: Enable CORS for Production

Update `backend/main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend.vercel.app",
        "https://your-frontend.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 7: Test Your Deployment

1. Visit your frontend URL
2. Try chatting with different models
3. Test authentication
4. Verify conversation history

## Troubleshooting

### Backend Issues
- Check Render/Railway logs
- Verify environment variables are set
- Ensure HF API key has correct permissions

### Frontend Issues
- Check browser console for errors
- Verify VITE_API_URL is correct
- Check CORS settings in backend

### API Key Issues
- Get new token from https://huggingface.co/settings/tokens
- Ensure "Inference API" permission is enabled
- Use "Fine-grained" token type

## Free Tier Limits

### Render
- 750 hours/month free
- Sleeps after 15 min inactivity
- 512 MB RAM

### Railway
- $5 free credit/month
- No sleep
- 512 MB RAM

### Vercel
- Unlimited deployments
- 100 GB bandwidth/month
- Automatic HTTPS

### Netlify
- 100 GB bandwidth/month
- 300 build minutes/month
- Automatic HTTPS

## Repository Structure

```
mygpt/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── model_router.py      # Multi-model router
│   ├── requirements.txt     # Python dependencies
│   └── test_*.py           # Test scripts
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── .env.example            # Environment template
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── DEPLOY_GITHUB.md       # This file
```

## Next Steps

1. ⭐ Star the repository
2. 📝 Update README with your deployment URLs
3. 🐛 Report issues on GitHub
4. 🚀 Share your deployment!

## License

MIT License - feel free to use for personal or commercial projects!
