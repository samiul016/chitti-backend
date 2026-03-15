import os
import re
import requests
from bs4 import BeautifulSoup
from groq import Groq
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- কনফিগারেশন (আপনার দেওয়া ডাটা অনুযায়ী) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
# আপনার দেওয়া লম্বা এক্সেস টোকেনটি এখানে বসিয়েছি
WHATSAPP_ACCESS_TOKEN = "EAAX2pwxRERCBQ5VrDLxxo8E6pjNXqziBKsRaIim35DVXltuZAPE7ZAmib10ii7tbJEAwIJZBaJNwfTEYEBTlkAj0i0WYM4vjZBbaIZCHpCqOzzA3gjfo0GKZA1QGr6BTEe5pvaCcI0qHl02kEiTL3BJZA k5N07Jxu22cc5WiJQXCZAbitczn8m6QHyZBerIxg5HiHLZCnOrddtYDDGm5DzNcnyFLbIDQUiwvzyZAi8BMDj1tx03ZCv2AMTB4GrfsRIYuZAUKsDctJywlqlSNHxcF02Bsvgwgc"
PHONE_NUMBER_ID = "981138588423812"
VERIFY_TOKEN = "CHITTI_SECRET_123" # এটি মেটা ড্যাশবোর্ডের 'Verify Token' বক্সে লিখবেন

client = Groq(api_key=GROQ_API_KEY)

# --- ওয়েব কন্টেন্ট এক্সট্রাক্টর ---
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

# --- মাস্টার এআই ফাংশন (কমন লজিক) ---
def get_ai_response(user_input):
    web_info = extract_web_content(user_input)
    system_prompt = (
        "আপনি বকুল ভাইয়ের পার্সোনাল এআই মাস্টার এজেন্ট। Tech Dental এবং Sale Bangladesh আপনার নলেজে আছে। "
        "আপনি সরাসরি ড্যাশবোর্ড কন্ট্রোল করতে পারেন। যদি ইউজার কোনো অ্যাকশন চায়, উত্তরের শেষে JSON ফরমেটে কমান্ড দেবেন। "
        "যেমন: {'action': 'SWITCH_TAB', 'target': 'tasks'}। উত্তর বাংলায় দেবেন।"
    )
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_input} {web_info}"}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    return completion.choices[0].message.content

# --- ১. ড্যাশবোর্ড চ্যাটবোর্ড এন্ডপয়েন্ট ---
@app.get("/ask-ai")
async def ask_ai(topic: str):
    try:
        output = get_ai_response(topic)
        return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "output": f"Error: {str(e)}"}

# --- ২. হোয়াটসঅ্যাপ ওয়েবহুক (মেটা ভেরিফিকেশন) ---
@app.get("/whatsapp-webhook")
async def verify_whatsapp(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return "Verification Failed", 403

# --- ৩. হোয়াটসঅ্যাপ মেসেজ হ্যান্ডলার ---
@app.post("/whatsapp-webhook")
async def whatsapp_post(request: Request):
    data = await request.json()
    try:
        # মেসেজ চেক করা
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            from_number = message['from']
            text = message['text']['body']

            # এআই থেকে উত্তর নেওয়া
            ai_reply = get_ai_response(text)

            # হোয়াটসঅ্যাপে রিপ্লাই পাঠানো
            send_whatsapp_msg(from_number, ai_reply)
            
    except:
        pass
    return {"status": "received"}

def send_whatsapp_msg(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)

@app.get("/")
def home():
    return {"message": "Chitti Master AI with WhatsApp Integration is Live!"}
