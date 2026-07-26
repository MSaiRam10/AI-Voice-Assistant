from uuid import uuid4
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

st.title("AI VOICE ASSISTANT")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

audio_value = st.audio_input("Click to record")

if audio_value:
    transcript = requests.post(
        "http://api:8000/transcribe",
        files={"audio": ("audio.wav", audio_value, "audio/wav")}
    )
    question = transcript.json()["text"]
    st.write(f"You said: {question}")

    answer = requests.post(
        "http://api:8000/chat",
        json={"question": question, "thread_id": st.session_state.thread_id}
    )
    answer_text = answer.json()["answer"]
    st.write(f"Answer: {answer_text}")

    speech = requests.post(
        "http://api:8000/speak",
        json={"text": answer_text}
    )
    st.audio(speech.content, format="audio/mpeg")