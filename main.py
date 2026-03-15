import os
import re
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini এআই কনফিগারেশন
api_key = os.getenv("AIzaSyDsroKDVMvKiX6Q6rdfyCocQSfzn1C5-LM")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_web_content(text):
    """টেক্সট থেকে ইউআরএল খুঁজে সেটি থেকে মূল কন্টেন্ট বের করা"""
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    if not urls:
        return None
    
    target_url = urls[0]
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # অপ্রয়োজনীয় ট্যাগ বাদ দেওয়া
        for script in soup(["script", "style"]):
            script.decompose()
            
        # মূল টেক্সট নেওয়া (প্রথম ২০০০ ক্যারেক্টার যাতে র‍্যাম শেষ না হয়)
        text_content = soup.get_text(separator=' ', strip=True)
        return f"\n[Website Content from {target_url}]: {text_content[:2000]}..."
    except Exception as e:
        return f"\n[Error accessing {target_url}]: {str(e)}"

@app.get("/ask-ai")
async def ask_ai(topic: str):
    try:
        web_context = extract_web_content(topic)
        
        system_prompt = (
            "আপনি সামিউল (বকুল) ভাইয়ের এক্সপার্ট এআই বিজনেস ম্যানেজার। "
            "ইউজার যদি কোনো লিঙ্ক দেয়, তবে সেই লিঙ্কের কন্টেন্ট বিশ্লেষণ করে উত্তর দিন। "
            "আপনার নলেজে Tech Dental এবং Sale Bangladesh এর তথ্য আছে। "
            f"\nইউজারের প্রশ্ন: {topic}"
        )
        
        if web_context:
            system_prompt += f"\nওয়েবসাইটের তথ্য: {web_context}"

        response = model.generate_content(system_prompt)
        
        return {
            "status": "success",
            "output": response.text
        }
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}

@app.get("/")
def home():
    return {"message": "Chitti AI Detective is Online!"}
