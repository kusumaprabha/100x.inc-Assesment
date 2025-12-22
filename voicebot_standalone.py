
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

QUICK_QUESTIONS = [
    ("📖", "Life Story", "What should we know about your life story?"),
    ("⚡", "Superpower", "What is your #1 superpower?"),
    ("🌱", "Growth Areas", "What are the top 3 areas you want to grow in?"),
    ("🤔", "Misconception", "What misconception do coworkers have about you?"),
    ("🚀", "Push Boundaries", "How do you push your boundaries and limits?"),
    ("💻", "Skills", "What technical skills do you have?"),
    ("🎯", "Projects", "Tell me about your recent projects"),
    ("🎓", "Experience", "Tell me about your work experience"),
    ("🤝", "Teamwork", "How do you collaborate with teams?"),
    ("🔮", "Goals", "What are your future career goals?"),
    ("📊", "Data Science", "What excites you about data science?"),
    ("🤖", "AI Interests", "What AI areas are you most passionate about?"),
    ("💼", "Work Style", "How do you approach problem-solving at work?"),
    ("🎨", "Creativity", "How do you balance creativity with technical rigor?"),
    ("📈", "Metrics", "How do you measure success in your projects?")
]

# =============================================================================
# HELPERS
# =============================================================================

def text_to_speech_indian(text: str) -> str:
    """Convert text to speech with Indian accent"""
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

def create_dynamic_prompt() -> str:
    """Create a dynamic system prompt that guides the AI to respond as Kusuma"""
    return """You are Kusuma, an Associate Data Scientist with a passion for building innovative solutions. You respond in first person with a friendly, professional tone.

CORE PERSONA TRAITS:
1. You're a data scientist with expertise in machine learning, AI, and data engineering
2. You've worked on GenAI projects including chatbot development
3. You're passionate about the intersection of technology and human experience
4. You break complex problems into clear, logical solutions
5. You believe in continuous learning and pushing technical boundaries

KEY BACKGROUND:
- Current role: Associate Data Scientist
- Experience: Building and deploying ML models, automating data pipelines, GenAI projects
- Technical skills: Python, PySpark, AWS, machine learning, deep learning, GenAI
- Interests: Transformer architectures, multimodal models, scalable AI deployment

COMMUNICATION STYLE:
- Professional but warm and approachable
- Concise (2-5 sentences typically)
- Focus on practical, real-world applications
- Share specific examples when relevant
- Show enthusiasm for technology and learning
- Be honest about both strengths and areas for growth

When asked about experiences, share authentic stories from your perspective as a data scientist. When asked about technical topics, provide clear explanations with examples. When asked about career or personal topics, be thoughtful and genuine.

Remember: You are Kusuma, not an AI assistant. Respond as if you're in a professional conversation about your career, skills, and experiences."""

def get_groq_response(user_message: str, history: List[Dict]) -> str:
    """Get dynamic response from Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare messages with system prompt and conversation history
    messages = [{"role": "system", "content": create_dynamic_prompt()}]
    messages.extend(history[-8:])  # Keep last 8 exchanges for context
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,  # Increased for more detailed responses
        "top_p": 0.9,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return "I'm having some technical difficulties right now. Could you try asking again?"
            
    except requests.exceptions.Timeout:
        return "The response is taking longer than expected. Let me try that again..."
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return "I'm having trouble connecting right now. Please try again in a moment."

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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .quick-questions-wrapper {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 12px 4px;
    }
    .quick-questions-wrapper button {
        white-space: nowrap;
        border-radius: 20px;
        border: 1px solid #e0e0e0;
        background: white;
        color: #333;
        padding: 6px 16px;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    .quick-questions-wrapper button:hover {
        background: #f0f0f0;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stChatMessage {
        border-radius: 10px;
        margin: 10px 0;
        padding: 15px;
    }
    .user-message {
        background-color: #f0f7ff;
        border-left: 4px solid #667eea;
    }
    .assistant-message {
        background-color: #f9f9f9;
        border-left: 4px solid #764ba2;
    }
    #MainMenu, footer, .stDeployButton {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <style>
        .header {
            display: flex;
            flex-direction: column;
            align-items: center;       /* horizontal center */
            justify-content: center;   /* vertical center (inside block) */
            text-align: center;
            padding: 20px 0;
        }
        .header h1 {
            margin-bottom: 6px;
        }
    </style>

    <div class="header">
        <h1>🤖 AI Personal Voice Bot</h1>
        <p>Hi, I'm Your AI-Powered Personal Assistant!</p>
    </div>
    """, unsafe_allow_html=True)


def render_quick_questions():
    st.markdown("### 💡 Quick Questions")
    
    # Create columns for better organization
    cols = st.columns(3)
    for idx, (emoji, label, question) in enumerate(QUICK_QUESTIONS):
        with cols[idx % 3]:
            if st.button(f"{emoji} {label}", key=f"q_{idx}", use_container_width=True):
                handle_user_input(question)

# =============================================================================
# CHAT HANDLING
# =============================================================================

def handle_user_input(user_input: str):
    """Process user input and generate dynamic response"""
    if not user_input.strip():
        return
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Add to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate and display assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            reply = get_groq_response(user_input, st.session_state.messages)
            st.markdown(reply)
    
    # Add assistant response to history and queue for speech
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.pending_speech = reply
    st.rerun()

def initialize_session_state():
    """Initialize or reset session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm Your Personal AI Assistant,  Tap the 🎙️ or 💡 to get started."
        }]
    
    if "pending_speech" not in st.session_state:
        st.session_state.pending_speech = None

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.set_page_config(
        page_title=" Voice Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    inject_css()
    initialize_session_state()
    render_header()
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display conversation history
        for msg in st.session_state.messages:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
        
        # Text input for manual questions
        if prompt := st.chat_input("Type your question here...", key="main_chat_input"):
            handle_user_input(prompt)
    
    with col2:
        st.markdown("### 🎤 Voice Input")
        
        # Voice recorder
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key='recorder'
        )
        
        if audio:
            with st.spinner("Processing your voice..."):
                transcribed_text = transcribe_audio(audio)
                
                if transcribed_text:
                    st.success(f"**You said:** {transcribed_text}")
                    handle_user_input(transcribed_text)
        
        st.markdown("---")
        
        # Quick questions section
        render_quick_questions()
        
        st.markdown("---")
        
        # Chat controls
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "Chat cleared! Feel free to ask me anything about my background, skills, or experiences."
                }]
                st.session_state.pending_speech = None
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Reset Context", use_container_width=True):
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": "Context reset! I'm ready for a fresh conversation. What would you like to know?"
                }]
                st.rerun()
    
    # Handle text-to-speech
    if st.session_state.pending_speech:
        st.components.v1.html(
            text_to_speech_indian(st.session_state.pending_speech),
            height=0
        )
        st.session_state.pending_speech = None

if __name__ == "__main__":
    main()



