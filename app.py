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

/* Floating input */
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
}

/* Glow */
.input-box:focus-within {
    box-shadow: 0 0 0 2px rgba(124,58,237,0.5),
                0 0 20px rgba(124,58,237,0.3);
}

/* Remove ALL borders */
div[data-baseweb="input"],
div[data-baseweb="input"] input {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: white !important;
}

/* Button */
.stButton button {
    border-radius: 999px !important;
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: white;
    border: none;
    padding: 8px 14px;
    transition: 0.2s;
}

.stButton button:hover {
    transform: scale(1.08);
}

.stButton button:active {
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

/* Empty screen */
.empty-screen {
    text-align: center;
    margin-top: 120px;
    color: white;
}

#typewriter {
    font-size: 28px;
    font-weight: bold;
}

#subtitle {
    color: #94a3b8;
    margin-top: 10px;
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

# -------- EMPTY SCREEN WITH TYPEWRITER --------
if len(st.session_state.chat) == 0:
    st.markdown("""
    <div class="empty-screen">
        <h1>🤖</h1>
        <h2 id="typewriter"></h2>
        <p id="subtitle"></p>
    </div>

    <script>
    const text1 = "Relay-Bot";
    const text2 = "A Strategic Thinking AI";
    const text3 = "Try: I'm confused about my future";

    let i = 0;
    let j = 0;
    let k = 0;

    function typeTitle() {
        if (i < text1.length) {
            document.getElementById("typewriter").innerHTML += text1.charAt(i);
            i++;
            setTimeout(typeTitle, 80);
        } else {
            setTimeout(typeSubtitle, 400);
        }
    }

    function typeSubtitle() {
        if (j < text2.length) {
            document.getElementById("subtitle").innerHTML += text2.charAt(j);
            j++;
            setTimeout(typeSubtitle, 40);
        } else {
            setTimeout(typeHint, 400);
        }
    }

    function typeHint() {
        if (k < text3.length) {
            document.getElementById("subtitle").innerHTML += "<br>" + text3.charAt(k);
            k++;
            setTimeout(typeHint, 30);
        }
    }

    typeTitle();
    </script>
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

col1, col2 = st.columns([6,1])

with col1:
    user_input = st.text_input(
        "",
        placeholder="Type your message...",
        label_visibility="collapsed"
    )

with col2:
    submitted = st.button("➤")

if submitted and user_input:
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

st.markdown('</div>', unsafe_allow_html=True)
