import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from crewai import Agent, Task, Crew, Process, LLM

app = FastAPI()

# ড্যাশবোর্ড থেকে রিকোয়েস্ট আসার অনুমতি (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# অনলাইনে হোস্ট করার সময় আমরা এই Key-টি Render-এর সেটিংসে দিয়ে দেব
gemini_key = os.getenv("AIzaSyDsroKDVMvKiX6Q6rdfyCocQSfzn1C5-LM")

# ১. Gemini মডেল সেটআপ (Flash ভার্সনটি অনেক ফাস্ট এবং ফ্রি)
online_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=gemini_key
)

@app.get("/ask-ai")
def ask_ai(topic: str):
    # আপনার ডাইনামিক ম্যানেজার এজেন্ট
    manager = Agent(
        role='Business AI Manager',
        goal=f'Solve user task: {topic}. Manage projects like Tech Dental or Sale Bangladesh.',
        backstory='You are a master AI running in the cloud. Expert in SEO and E-commerce.',
        llm=online_llm,
        verbose=True
    )

    task = Task(
        description=f'টাস্ক: {topic}। এটি সমাধান করুন এবং সুন্দর রিপোর্ট দিন।',
        expected_output='A professional structured response.',
        agent=manager
    )

    crew = Crew(agents=[manager], tasks=[task])
    result = crew.kickoff()
    
    return {"status": "success", "output": str(result)}

@app.get("/")
def home():
    return {"message": "Chitti AI Online is Live!"}