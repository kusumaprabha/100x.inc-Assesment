
########## PRESENT WORKING #########
#!/usr/bin/env python3

"""
Streamlit Voice Bot – AI-Powered Personal Assistant 
"""

import streamlit as st
import requests
import os
import base64
import io
from gtts import gTTS
from typing import Dict, List
from streamlit_mic_recorder import mic_recorder
import tempfile

# =============================================================================
# CONFIG
# =============================================================================

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"



PERSONAL_INFO = {
    "life_story": "Hi, I'm Kusuma, currently working as an Associate Data Scientist, passionate about building innovative solutions that make a real impact, where I build and deploy machine learning models, automate data pipelines, and work closely with cross-functional teams to translate business needs into data-driven solutions. I've also worked on GenAI projects/POC like chatbot development. I've been on an incredible journey of continuous learning, working on everything from applications to AI-powered tools. What drives me is the intersection of technology and human experience—creating solutions that are not just functional, but truly delightful to use.",

    "superpower": "My superpower is taking complex problems and breaking them into clear, logical, and automated solutions. Whether it's building a GenAI chatbot, designing a data validation engine in PySpark, or optimizing deep learning models, I'm able to think end-to-end — from understanding the business goal to turning it into a working system.",

    "growth_areas": "The top 3 areas I'd like to grow in are: First, I want to deepen my expertise in LLMOps and scalable deployment of GenAI systems. Second, I'm focusing on advanced deep learning—especially transformer architectures and multimodal models. And third, I want to grow my leadership and mentoring abilities so I can guide teams on AI/ML projects.",

    "misconception": "People sometimes assume I'm quiet because I'm focused, but once I start working on a problem, I communicate very clearly and collaborate actively. I just like to understand the problem deeply before sharing solutions — and once I do, I'm very engaged and proactive.",

    "push_boundaries": "I push my boundaries by taking on projects that challenge me technically. For example, building a GenAI chatbot POC, designing a PySpark-based validation engine, and deploying APIs on AWS — all of these were outside my comfort zone initially, but I took them head-on. I constantly upskill myself, experiment with new tools, and set targets that force me to grow faster than the environment around me."
}

QUICK_QUESTIONS = [
    ("📖", "Life Story", "What should we know about your life story?"),
    ("⚡", "Superpower", "What is your #1 superpower?"),
    ("🌱", "Growth", "What are the top 3 areas you want to grow in?"),
    ("🤔", "Misconception", "What misconception do coworkers have about you?"),
    ("🚀", "Limits", "How do you push your boundaries and limits?"),
    ("💻", "Skills", "What technical skills do you have?"),
    ("🎯", "Projects", "Tell me about your recent projects"),
    ("🎓", "Experience", "Tell me about your work experience"),
    ("🤝", "Teamwork", "How do you collaborate with teams?"),
    ("🔮", "Goals", "What are your future career goals?")
]

# =============================================================================
# HELPERS
# =============================================================================

def text_to_speech_indian(text: str) -> str:
    tts = gTTS(text=text, lang="en", tld="co.in")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    audio_b64 = base64.b64encode(buf.read()).decode()
    return f"""
    <audio autoplay style="display:none">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg">
    </audio>
    """

def transcribe_audio(audio_data: dict) -> str:
    """Convert audio to text using Groq Whisper API"""
    try:
        # Get the audio bytes from the recorder
        audio_bytes = audio_data.get('bytes')
        if not audio_bytes:
            return None
            
        # Save to temporary file with .wav extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', mode='wb') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Use Groq Whisper API for transcription
        with open(tmp_path, 'rb') as audio_file:
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": ("audio.wav", audio_file, "audio/wav")},
                data={"model": "whisper-large-v3"}
            )
        
        # Clean up
        os.unlink(tmp_path)
        
        if response.status_code == 200:
            return response.json().get('text', '').strip()
        else:
            st.error(f"Transcription error: {response.status_code}")
            return None
        
    except Exception as e:
        st.error(f"Speech recognition error: {str(e)}")
        return None

def create_system_prompt() -> str:
    return f"""
You are Kusuma speaking in first person.

Life Story:
{PERSONAL_INFO['life_story']}

Superpower:
{PERSONAL_INFO['superpower']}

Growth Areas:
{PERSONAL_INFO['growth_areas']}

Misconception:
{PERSONAL_INFO['misconception']}

Push Boundaries:
{PERSONAL_INFO['push_boundaries']}

Guidelines:
- Friendly, professional
- 2–5 sentences
"""

def get_groq_response(user_message: str, history: List[Dict]) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": create_system_prompt()}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 400
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]

    st.error(f"Groq Error {response.status_code}: {response.text}")
    return "I'm having trouble responding right now."

# =============================================================================
# UI
# =============================================================================

def inject_css():
    st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg,#667eea,#764ba2);
        padding: 20px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }
    .quick-questions-wrapper {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 10px;
        padding: 10px 4px;
        white-space: nowrap;
    }
    .quick-questions-wrapper button {
        white-space: nowrap !important;
        border-radius: 20px !important;
    }
    #MainMenu, footer, .stDeployButton {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div class="header">
        <h1>🤖 AI-Powered Personal Voice Bot</h1>
        <p>Tap the mic, ask questions, hear answers</p>
    </div>
    """, unsafe_allow_html=True)

def render_quick_questions():
    st.markdown("### 💡 Quick Questions")
    st.markdown('<div class="quick-questions-wrapper">', unsafe_allow_html=True)

    for i, (emoji, label, question) in enumerate(QUICK_QUESTIONS):
        if st.button(f"{emoji} {label}", key=f"q_{i}"):
            handle_user_input(question)

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# CHAT
# =============================================================================

def handle_user_input(user_input: str):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            reply = get_groq_response(user_input, st.session_state.messages)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.pending_speech = reply
    st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    st.set_page_config(page_title="Personal Voice Bot", page_icon="🤖", layout="wide")
    inject_css()

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hi! I'm Your Personal AI Assistant, Tap the 🎙️ or choose 💡 to get started."
        }]

    if "pending_speech" not in st.session_state:
        st.session_state.pending_speech = None

    render_header()

    col1, col2 = st.columns([2, 1])

    with col1:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type your question..."):
            handle_user_input(prompt)

    with col2:
        st.markdown("### 🎤 Ask a Question")

        # Voice recorder
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key='recorder'
        )

        if audio:
            st.info("🔄 Processing your voice...")
            transcribed_text = transcribe_audio(audio)
            
            if transcribed_text:
                st.success(f"📝 You said: {transcribed_text}")
                handle_user_input(transcribed_text)

        render_quick_questions()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Chat cleared! Ask me anything."
            }]
            st.session_state.pending_speech = None
            st.rerun()

    if st.session_state.pending_speech:
        st.components.v1.html(
            text_to_speech_indian(st.session_state.pending_speech),
            height=0
        )
        st.session_state.pending_speech = None

if __name__ == "__main__":
    main()

