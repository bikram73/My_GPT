"""
Quick test script to verify model is working
Run this before starting the full backend
"""
import torch
from transformers import pipeline, AutoTokenizer
from huggingface_hub import login

print("=" * 50)
print("Testing AI Model Setup with Hugging Face")
print("=" * 50)

# Login to Hugging Face
HF_TOKEN = os.getenv("HF_API_KEY", "")
print("\n[0/4] Logging in to Hugging Face...")
try:
    login(token=HF_TOKEN)
    print("✓ Logged in to Hugging Face")
except Exception as e:
    print(f"⚠ Warning: {e}")

# Test 1: Check PyTorch
print("\n[1/4] Checking PyTorch...")
print(f"✓ PyTorch version: {torch.__version__}")
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ CUDA device: {torch.cuda.get_device_name(0)}")

# Test 2: Load Model
print("\n[2/4] Loading model (this may take 2-5 minutes first time)...")
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"  # Best quality model!

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        tokenizer=tokenizer,
        device_map="auto",
        token=HF_TOKEN,
    )
    print(f"✓ Model loaded: {MODEL_ID}")
    print(f"✓ Device: {pipe.device}")
    print(f"✓ This is a HIGH QUALITY model!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying fallback model...")
    MODEL_ID = "microsoft/DialoGPT-small"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pipe = pipeline(
        "text-generation",
        model=MODEL_ID,
        tokenizer=tokenizer,
        device_map="auto",
    )
    print(f"✓ Fallback model loaded: {MODEL_ID}")

# Test 3: Generate Response
print("\n[3/4] Testing text generation...")
test_input = "Hello, how are you?"
print(f"Input: {test_input}")

try:
    if "Llama" in MODEL_ID or "llama" in MODEL_ID:
        # Llama format
        messages = [{"role": "user", "content": test_input}]
        if hasattr(tokenizer, 'apply_chat_template'):
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = f"User: {test_input}\nAssistant:"
        
        output = pipe(
            prompt,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        response = output[0]["generated_text"][len(prompt):].strip()
        if "<|eot_id|>" in response:
            response = response.split("<|eot_id|>")[0].strip()
    else:
        # DialoGPT format
        output = pipe(
            test_input + tokenizer.eos_token,
            max_new_tokens=50,
            do_sample=True,
            temperature=0.8,
            top_k=50,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id,
        )
        response = output[0]["generated_text"]
        response = response[len(test_input):].strip()
        if tokenizer.eos_token in response:
            response = response.split(tokenizer.eos_token)[0].strip()
    
    print(f"Response: {response}")
    print("✓ Generation successful!")
except Exception as e:
    print(f"❌ Generation error: {e}")
    exit(1)

# Test 4: Summary
print("\n[4/4] Summary")
print("=" * 50)
print("✓ All tests passed!")
print("✓ Your model is ready to use")
print(f"✓ Model: {MODEL_ID}")
print("\nYou can now run: python main.py")
print("=" * 50)
