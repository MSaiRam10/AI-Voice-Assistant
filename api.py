from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.responses import Response
from openai import OpenAI
from pydantic import BaseModel
from agent import agent

load_dotenv()

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    thread_id: str

class SpeakRequest(BaseModel):
    text: str

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=(audio.filename, audio_bytes, audio.content_type)
    )
    return {"text": transcript.text}

@app.post("/chat")
def user_question(request: QuestionRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    response = agent.invoke({
        "question": request.question,
        "messages": [],
        "answer": "",
    }, config=config)
    return {"answer": response["answer"]}

@app.post("/speak")
def speak(request: SpeakRequest):
    audio = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=request.text
    )
    return Response(content=audio.content, media_type="audio/mpeg")