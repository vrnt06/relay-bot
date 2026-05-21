import streamlit as st
from bot import process_input
import time

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Relay-Bot", page_icon="🤖", layout="centered")

# -------- CSS --------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #020617);
}

/* Chat container */
.chat-container {
    max-width: 700px;
    margin: auto;
    padding-bottom: 100px;
}

/* User message */
.user-msg {
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: white;
    padding: 10px 14px;
    border-radius: 18px;
    margin: 6px 0;
    text-align: right;
    width: fit-content;
    max-width: 80%;
    margin-left: auto;
}

/* Bot message */
.bot-msg {
    background: rgba(30, 41, 59, 0.85);
    backdrop-filter: blur(10px);
    color: white;
    padding: 10px 14px;
    border-radius: 18px;
    margin: 6px 0;
    width: fit-content;
    max-width: 80%;
}

/* Chat input text color */
textarea, input {
    color: white !important;
    caret-color: #7c3aed !important;
}

/* Placeholder */
::placeholder {
    color: #94a3b8 !important;
}

/* Typing dots */
.dots::after {
    content: '';
    animation: dots 1.5s steps(3, end) infinite;
}

@keyframes dots {
    0% { content: ''; }
    33% { content: '.'; }
    66% { content: '..'; }
    100% { content: '...'; }
}

/* Empty screen */
.empty-screen {
    text-align: center;
    margin-top: 120px;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -------- HEADER --------
st.title("🤖 Relay-Bot")
st.caption("A Strategic Thinking AI")

# -------- SESSION --------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "state" not in st.session_state:
    st.session_state.state = {
        "decision": {"active": False, "step": 0, "answers": {}, "options": []},
        "clarity": {"active": False, "step": 0, "answers": {}}
    }

# -------- TYPEWRITER INTRO --------
if len(st.session_state.chat) == 0:
    placeholder = st.empty()
    text = "Relay-Bot"
    displayed = ""

    for char in text:
        displayed += char
        placeholder.markdown(
            f"<div class='empty-screen'><h2>{displayed}</h2></div>",
            unsafe_allow_html=True
        )
        time.sleep(0.05)

    st.markdown(
        "<div class='empty-screen'><p>A Strategic Thinking AI</p></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='empty-screen'><p>Try: I'm confused about my future</p></div>",
        unsafe_allow_html=True
    )

# -------- CHAT DISPLAY --------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for sender, msg in st.session_state.chat:
    if sender == "user":
        st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------- INPUT (ENTER WORKS HERE) --------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat.append(("user", user_input))

    placeholder = st.empty()
    placeholder.markdown(
        '<div class="bot-msg">🤖 Relay-Bot is thinking<span class="dots"></span></div>',
        unsafe_allow_html=True
    )

    time.sleep(0.6)

    response = process_input(user_input, st.session_state.state)

    placeholder.empty()

    st.session_state.chat.append(("bot", response))

    st.rerun()
