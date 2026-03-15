import os
import re
import requests
from bs4 import BeautifulSoup
from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ড্যাশবোর্ড কানেক্ট করার অনুমতি
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq ক্লায়েন্ট সেটআপ
# Render-এর Environment Variables-এ 'GROQ_API_KEY' থাকতে হবে
client = Groq(api_key=os.environ.get("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"))

def extract_web_content(text):
    """টেক্সট থেকে ইউআরএল খুঁজে সেটি থেকে মূল কন্টেন্ট বের করা"""
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
        # ওয়েবসাইট কন্টেন্ট চেক করা
        web_info = extract_web_content(topic)
        
        # Groq-কে কমান্ড পাঠানো
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "আপনি বকুল ভাইয়ের পার্সোনাল এআই ম্যানেজার। আপনার নলেজে Tech Dental এবং Sale Bangladesh আছে। সব উত্তর বাংলায় দেবেন।"
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
    return {"message": "Chitti AI (Groq Edition) is Live!"}
