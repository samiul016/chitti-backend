import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
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

# Gemini এআই কনফিগারেশন
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# লেটেস্ট মডেল কনফিগারেশন
model = genai.GenerativeModel('gemini-1.5-flash')

def get_web_info(url):
    """ওয়েবসাইট থেকে তথ্য পড়ার একটি সিম্পল ফাংশন"""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string if soup.title else "No Title Found"
    except:
        return "Could not access website"

@app.get("/ask-ai")
async def ask_ai(topic: str):
    try:
        # এআই-কে আপনার ব্যবসার কন্টেক্সট দেওয়া
        system_instruction = (
            "আপনি সামিউল (বকুল) ভাইয়ের পার্সোনাল এআই ম্যানেজার। "
            "তার ব্যবসাগুলো হলো Tech Dental এবং Sale Bangladesh। "
            "আপনি এখন ইন্টারনেটের তথ্যও বুঝতে পারেন। "
            f"ইউজারের কমান্ড: {topic}"
        )
        
        # জেনারেট কন্টেন্ট (লেটেস্ট মেথড)
        response = model.generate_content(system_instruction)
        
        return {
            "status": "success",
            "output": response.text
        }
    except Exception as e:
        # এরর মেসেজটি পরিষ্কারভাবে দেখানো
        error_msg = str(e)
        if "404" in error_msg:
            error_msg = "Google API এখনও মডেলটি খুঁজে পাচ্ছে না। দয়া করে Render-এ Clear Build Cache দিয়ে আবার ডেপ্লয় করুন।"
        return {"status": "error", "output": error_msg}

@app.get("/")
def home():
    return {"message": "Chitti AI Super-Powered Online!"}
