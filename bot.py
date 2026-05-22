import random
import time
import os
from dotenv import load_dotenv
from google import genai

# -------- LOAD API --------
load_dotenv()
import streamlit as st
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# -------- HUMAN-LIKE PRINT --------
def slow_print(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.01)
    print()

# -------- ANALYZE INPUT --------
def analyze_input(user_input):
    text = user_input.lower()
    if any(w in text for w in ["relationship", "love", "girl", "boy"]):
        return "relationship"
    elif any(w in text for w in ["career", "job", "future", "study"]):
        return "career"
    return "general"

# -------- STYLE ENGINE --------
def style_line(style):
    if style == "cold":
        return random.choice([
            "Let’s not sugarcoat this.",
            "I’m going to be direct.",
        ])
    elif style == "empathetic":
        return random.choice([
            "I get why this feels heavy.",
            "Yeah… that’s not easy to deal with.",
        ])
    return random.choice([
        "Hmm… okay.",
        "Alright, let’s think this through.",
    ])

# -------- GEMINI CALL --------
def call_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# -------- DECISION DETECTION --------
def decide_action(user_input):
    text = user_input.lower()

    # PRIORITY 1: decision with options
    if "between" in text:
        return "decision"

    # PRIORITY 2: confusion → go to CLARITY (not reality)
    elif any(word in text for word in ["confused", "don't know", "lost", "stuck"]):
        return "clarity"

    elif any(word in text for word in ["choose", "decision"]) and "between" not in text:
        return "clarity"

    # PRIORITY 3: knowledge
    elif "explain" in text or "what is" in text:
        return "llm"

    return "normal"

# -------- EXTRACT OPTIONS --------
def extract_options(user_input):
    if "between" in user_input:
        parts = user_input.split("between")[1]
        options = parts.split("and")
        return [opt.strip() for opt in options]
    return []

# -------- DECISION START --------
def decision_tool(problem, decision_state):
    options = extract_options(problem)

    decision_state["active"] = True
    decision_state["step"] = 1
    decision_state["answers"] = {}
    decision_state["options"] = options

    return f"""
Relay-Bot:

You're deciding between:
→ {options}

Let’s break this step by step.

Which option excites you more instinctively?
"""

# -------- DECISION RESULT --------
def generate_recommendation(state):
    options = state["options"]
    answers = state["answers"]

    scores = {opt: 0 for opt in options}

    for key in answers:
        for opt in options:
            if opt.lower() in answers[key]:
                scores[opt] += 1

    best_option = max(scores, key=scores.get)

    return f"""
Final Analysis:

Scores:
{scores}

Recommended:
→ {best_option.upper()}

This aligns with your instinct, practicality, and growth.

But answer this honestly:

If you ignore this decision,
which option will still stay in your mind?

That’s your real answer.
"""

# -------- CLARITY START --------
def clarity_tool():
    return """
Relay-Bot:

Alright. Then we don’t need a decision yet.

We need clarity first.

Answer this step by step:

1. What exactly is bothering you right now?
"""

# -------- CLARITY RESULT --------
def generate_clarity_response(answers):
    return f"""
Let’s piece this together.

You said:
- Problem → {answers.get("problem")}
- Fear → {answers.get("fear")}
- Ideal → {answers.get("ideal")}

You’re not stuck because of lack of options.

You’re stuck because:
- There’s uncertainty
- And hesitation to commit

Now take one small step forward.

Not the perfect decision.

Just the next step.
"""

# -------- PATTERN DETECTION --------
def detect_pattern(memory):
    if memory["relationship"] >= 3:
        return "You keep returning to the same relationship issue. That’s a pattern."
    if memory["career"] >= 3:
        return "You seem repeatedly uncertain about your direction. That needs clarity."
    return ""


# -------- MAIN BOT --------
def relay_bot():
    print("🤖 Relay-Bot Activated")
    print("This isn’t just a chatbot. This is a thinking system.")
    print("(Type 'exit' to quit)\n")

    memory = {"relationship": 0, "career": 0, "general": 0}

    decision_state = {"active": False, "step": 0, "answers": {}, "options": []}
    clarity_state = {"active": False, "step": 0, "answers": {}}

    style = "balanced"

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            slow_print("Relay-Bot: Think clearly. Act deliberately. Goodbye.")
            break

        # -------- STYLE SWITCH --------
        if "be harsh" in user_input.lower():
            style = "cold"
            slow_print("Relay-Bot: Alright. I’ll be direct.")
            continue
        elif "be nice" in user_input.lower():
            style = "empathetic"
            slow_print("Relay-Bot: Got it. I’ll go easier.")
            continue

        # -------- DECISION FLOW --------
        if decision_state["active"]:
            step = decision_state["step"]
            options = decision_state["options"]

            if step == 1:
                decision_state["answers"]["instinct"] = user_input.lower()
                decision_state["step"] = 2
                slow_print("\nRelay-Bot:")
                slow_print("Which option is more practical right now?")
                continue

            elif step == 2:
                decision_state["answers"]["practical"] = user_input.lower()
                decision_state["step"] = 3
                slow_print("\nRelay-Bot:")
                slow_print("Which option has better long-term growth?")
                continue

            elif step == 3:
                decision_state["answers"]["growth"] = user_input.lower()

                result = generate_recommendation(decision_state)
                slow_print("\nRelay-Bot:")
                slow_print(result)

                decision_state["active"] = False
                continue

        # -------- CLARITY FLOW --------
        if clarity_state["active"]:
            step = clarity_state["step"]

            if step == 1:
                clarity_state["answers"]["problem"] = user_input
                clarity_state["step"] = 2
                slow_print("\nRelay-Bot:")
                slow_print("What outcome are you afraid of?")
                continue

            elif step == 2:
                clarity_state["answers"]["fear"] = user_input
                clarity_state["step"] = 3
                slow_print("\nRelay-Bot:")
                slow_print("If everything went right, what would that look like?")
                continue

            elif step == 3:
                clarity_state["answers"]["ideal"] = user_input

                result = generate_clarity_response(clarity_state["answers"])
                slow_print("\nRelay-Bot:")
                slow_print(result)

                clarity_state["active"] = False
                continue

        # -------- AGENT DECISION --------
        action = decide_action(user_input)

        if action == "decision":
            slow_print(decision_tool(user_input, decision_state))
            continue

        elif action == "clarity":
            clarity_state["active"] = True
            clarity_state["step"] = 1
            slow_print(clarity_tool())
            continue

        elif action == "llm":
            prompt = f"""
You are a strategic AI.
Be clear, logical, and structured.

User: {user_input}
"""
            response = call_gemini(prompt)
            slow_print("\nRelay-Bot:")
            slow_print(response)

        else:
            category = analyze_input(user_input)
            memory[category] += 1

            slow_print("\nRelay-Bot:")
            slow_print(style_line(style))
            slow_print("Let’s think this through.")

        # -------- PATTERN --------
        pattern = detect_pattern(memory)
        if pattern:
            slow_print("\nRelay-Bot:")
            slow_print(pattern)

def process_input(user_input, state):
    # Access states
    decision_state = state["decision"]
    clarity_state = state["clarity"]

    # -------- DECISION FLOW --------
    if decision_state["active"]:
        step = decision_state["step"]
        options = decision_state["options"]

        if step == 1:
            decision_state["answers"]["instinct"] = user_input.lower()
            decision_state["step"] = 2
            return "Which option is more practical right now?"

        elif step == 2:
            decision_state["answers"]["practical"] = user_input.lower()
            decision_state["step"] = 3
            return "Which option has better long-term growth?"

        elif step == 3:
            decision_state["answers"]["growth"] = user_input.lower()
            result = generate_recommendation(decision_state)
            decision_state["active"] = False
            return result

    # -------- CLARITY FLOW --------
    if clarity_state["active"]:
        step = clarity_state["step"]

        if step == 1:
            clarity_state["answers"]["problem"] = user_input
            clarity_state["step"] = 2
            return "What outcome are you afraid of?"

        elif step == 2:
            clarity_state["answers"]["fear"] = user_input
            clarity_state["step"] = 3
            return "If everything went right, what would that look like?"

        elif step == 3:
            clarity_state["answers"]["ideal"] = user_input
            result = generate_clarity_response(clarity_state["answers"])
            clarity_state["active"] = False
            return result

    # -------- NEW INPUT --------
    action = decide_action(user_input)

    if action == "decision":
        return decision_tool(user_input, decision_state)

    elif action == "clarity":
        clarity_state["active"] = True
        clarity_state["step"] = 1
        return clarity_tool()

    elif action == "llm":
        prompt = f"""
You are a strategic AI.
Be clear and logical.

User: {user_input}
"""
        return call_gemini(prompt)

    else:
        prompt = f"""
You are Relay-Bot, a strategic thinking AI.

User said: {user_input}

Respond naturally but intelligently.
If it's casual, respond casually.
If it's deep, guide thinking.

Keep it short and engaging.
"""
        return call_gemini(prompt)

# -------- RUN --------
if __name__ == "__main__":
    relay_bot()
