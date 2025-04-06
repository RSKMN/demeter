import streamlit as st
# from PIL import Image
# import pytesseract
import requests
# from my_api import api_key


api_key = st.secrets["groq_api_key"]
# Groq API Endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_chat_response(messages, max_tokens=1000):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"⚠️ API Error: {e}"

# Initialize chat memory
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "system", "content": "You are an expert in recipe anlysis that answers queries regarding conversions of informal measures of cups/ spoons.. into metric systems. (Answer the query in short)"}
    ]

st.title("Demeter! The AI Chef!!")

st.subheader("💬 Ask your query in the bottom!")
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").markdown(msg["content"])

user_input = st.chat_input("Type your question here...")
if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.spinner("Assistant is thinking..."):
        response = get_chat_response(st.session_state.chat_messages)
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()
