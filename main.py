import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ড্যাশবোর্ড থেকে রিকোয়েস্ট আসার অনুমতি
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini এআই সেটআপ
api_key = os.getenv("AIzaSyDsroKDVMvKiX6Q6rdfyCocQSfzn1C5-LM")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/ask-ai")
async def ask_ai(topic: str):
    """
    এই ফাংশনটি সরাসরি Gemini ব্যবহার করবে। এটি অনেক ফাস্ট এবং মেমোরি কম নেয়।
    """
    try:
        # এআই-কে আপনার বিজনেস সম্পর্কে ইনস্ট্রাকশন দেওয়া
        prompt = f"আপনি একজন এক্সপার্ট এআই বিজনেস ম্যানেজার। আপনার ইউজারের নাম বকুলে (Boss)। তার 'Tech Dental' এবং 'Sale Bangladesh' নামে ব্যবসা আছে। এই টাস্কটি সমাধান করুন: {topic}। উত্তরটি সুন্দর এবং প্রফেশনালভাবে দিন।"
        
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "output": response.text
        }
    except Exception as e:
        return {"status": "error", "output": str(e)}

@app.get("/")
def home():
    return {"message": "Chitti AI Online is Live and Running!"}
