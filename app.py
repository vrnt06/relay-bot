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
    padding-bottom: 120px;
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

/* Floating input bar */
.input-box {
    position: fixed;
    bottom: 20px;
    left: 0;
    right: 0;
    max-width: 700px;
    margin: auto;
    padding: 8px 12px;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.3s ease;
}

/* Glow when typing */
.input-box:focus-within {
    box-shadow: 0 0 0 2px rgba(124,58,237,0.5),
                0 0 20px rgba(124,58,237,0.3);
}

/* ===== REMOVE RED BORDER (FINAL FIX) ===== */
div[data-baseweb="input"],
div[data-baseweb="input"]:focus-within {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-baseweb="input"] input {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: white !important;
    font-size: 15px;
    padding: 8px 12px;
}

/* Remove invalid red */
input:invalid {
    border: none !important;
    box-shadow: none !important;
}

/* Remove "Press Enter" text */
div[data-testid="stForm"] p,
div[data-testid="stForm"] small {
    display: none !important;
}

/* Button */
.stForm button {
    border-radius: 999px !important;
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: white;
    border: none;
    padding: 8px 14px;
    font-weight: bold;
    transition: all 0.2s ease;
}

/* Button hover */
.stForm button:hover {
    transform: scale(1.08);
    box-shadow: 0 5px 25px rgba(124,58,237,0.5);
}

/* Button click animation */
.stForm button:active {
    transform: scale(0.95);
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

/* Cursor blink */
.cursor {
    display: inline-block;
    width: 8px;
    height: 14px;
    background: white;
    margin-left: 4px;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% { opacity: 0; }
}

/* Empty screen */
.empty-screen {
    text-align: center;
    margin-top: 120px;
    color: white;
    animation: fadeIn 1s ease;
}

.empty-screen h1 {
    font-size: 60px;
}

.empty-screen p {
    color: #94a3b8;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px);}
    to { opacity: 1; transform: translateY(0);}
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

# -------- EMPTY SCREEN --------
if len(st.session_state.chat) == 0:
    st.markdown("""
    <div class="empty-screen">
        <h1>🤖</h1>
        <h2>Relay-Bot</h2>
        <p>A Strategic Thinking AI</p>
        <p>Try: I'm confused about my future</p>
    </div>
    """, unsafe_allow_html=True)

# -------- CHAT DISPLAY --------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for sender, msg in st.session_state.chat:
    if sender == "user":
        st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------- INPUT --------
st.markdown('<div class="input-box">', unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6,1])

    with col1:
        user_input = st.text_input(
            "",
            placeholder="Type your message...",
            label_visibility="collapsed"
        )

    with col2:
        submitted = st.form_submit_button("➤")

    if submitted and user_input:
        st.session_state.chat.append(("user", user_input))

        placeholder = st.empty()
        placeholder.markdown(
            '<div class="bot-msg">🤖 Relay-Bot is thinking<span class="dots"></span></div>',
            unsafe_allow_html=True
        )

        time.sleep(0.7)

        response = process_input(user_input, st.session_state.state)

        placeholder.empty()

        st.session_state.chat.append(("bot", response))

        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)