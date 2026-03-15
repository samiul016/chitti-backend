import os
import re
import requests
from bs4 import BeautifulSoup
from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq ক্লায়েন্ট সেটআপ
client = Groq(api_key=os.environ.get("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"))

def extract_web_content(text):
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    if not urls:
        return ""
    
    target_url = urls[0]
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text(separator=' ', strip=True)
        return f"\n[Web Content from {target_url}]: {text_content[:2000]}..."
    except:
        return ""

@app.get("/ask-ai")
async def ask_ai(topic: str):
    try:
        web_info = extract_web_content(topic)
        
        # এখানে নতুন মডেল 'llama-3.1-8b-instant' ব্যবহার করা হয়েছে
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": "আপনি বকুল ভাইয়ের পার্সোনাল এআই ম্যানেজার। Tech Dental এবং Sale Bangladesh আপনার নলেজে আছে। উত্তর বাংলায় দেবেন।"
                },
                {
                    "role": "user", 
                    "content": f"{topic} {web_info}"
                }
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        return {
            "status": "success",
            "output": completion.choices[0].message.content
        }
    except Exception as e:
        return {"status": "error", "output": f"Groq Error: {str(e)}"}

@app.get("/")
def home():
    return {"message": "Chitti AI (Updated Edition) is Live!"}
