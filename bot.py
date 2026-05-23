import streamlit as st
from google import genai
from groq import Groq

# -------- API --------
api_key = st.secrets.get("GEMINI_API_KEY", None)
client = genai.Client(api_key=api_key) if api_key else None
groq_api_key = st.secrets.get("GROQ_API_KEY", None)
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# -------- MEMORY --------
def update_memory(state, user_input):
    if "history" not in state:
        state["history"] = []
    state["history"].append(user_input)


# -------- PLANNER --------
def agent_planner(user_input, state):
    text = user_input.lower()

    if state["decision"]["active"]:
        return "decision"

    if state["clarity"]["active"]:
        return "clarity"

    if "between" in text:
        return "decision"

    if any(w in text for w in ["confused", "lost", "stuck", "don't know"]):
        return "clarity"

    return "llm"


# -------- LLM TOOL --------
def llm_tool(prompt):

    # -------- 1. TRY GEMINI --------
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception as e:
            gemini_error = str(e)
    else:
        gemini_error = "No Gemini client"


    # -------- 2. FALLBACK TO GROQ --------
    if groq_client:
        try:
            chat = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are GrowBot, an AI mentor helping users think clearly."},
                    {"role": "user", "content": prompt}
                ]
            )
            return chat.choices[0].message.content
        except Exception as e:
            groq_error = str(e)
    else:
        groq_error = "No Groq client"


    # -------- 3. FINAL FALLBACK --------
    return f"""
GrowBot:

⚠️ AI services are currently limited.
Gemini Error: {gemini_error}
Groq Error: {groq_error}
Let’s think this through step-by-step instead.

What exactly are you trying to figure out?
"""

# -------- REFLECTION --------
def is_response_weak(response):
    weak_signals = [
        "i don't know",
        "maybe",
        "not sure",
        "it depends"
    ]

    if len(response) < 40:
        return True

    for signal in weak_signals:
        if signal in response.lower():
            return True

    return False


# -------- RETRY IMPROVER --------
def improve_response(user_input, state, prev_response):
    prompt = f"""
You are improving a weak answer.

User: {user_input}

Previous Answer:
{prev_response}

Give a clearer, more confident, structured answer.
"""

    return llm_tool(prompt)


# -------- DECISION TOOL --------
def decision_tool(user_input, state):

    if not state["active"]:
        state["active"] = True
        state["step"] = 1

        if "between" in user_input:
            parts = user_input.split("between")[1]
            options = parts.split("and")
            state["options"] = [opt.strip() for opt in options]
        else:
            state["options"] = []

        return f"""
You're deciding between:
→ {state['options']}

Which option feels right instinctively?
"""

    if state["step"] == 1:
        state["answers"]["instinct"] = user_input
        state["step"] = 2
        return "Which option is more practical right now?"

    elif state["step"] == 2:
        state["answers"]["practical"] = user_input
        state["step"] = 3
        return "Which option has better long-term growth?"

    elif state["step"] == 3:
        state["answers"]["growth"] = user_input

        result = f"""
Final Analysis:

Options: {state['options']}

Instinct → {state['answers']['instinct']}
Practical → {state['answers']['practical']}
Growth → {state['answers']['growth']}

If all align → that's your answer.
If not → choose what matters most right now.
"""

        state["active"] = False
        state["step"] = 0
        state["answers"] = {}

        return result


# -------- CLARITY TOOL --------
def clarity_tool(user_input, state):

    if not state["active"]:
        state["active"] = True
        state["step"] = 1
        return "What exactly is bothering you?"

    if state["step"] == 1:
        state["answers"]["problem"] = user_input
        state["step"] = 2
        return "What outcome are you afraid of?"

    elif state["step"] == 2:
        state["answers"]["fear"] = user_input
        state["step"] = 3
        return "If everything went right, what would that look like?"

    elif state["step"] == 3:
        state["answers"]["ideal"] = user_input

        result = f"""
Clarity Breakdown:

Problem → {state['answers']['problem']}
Fear → {state['answers']['fear']}
Ideal → {state['answers']['ideal']}

You're not stuck because of lack of options.
You're stuck because of uncertainty.

Take one small step forward.
"""

        state["active"] = False
        state["step"] = 0
        state["answers"] = {}

        return result


# -------- MAIN AGENT LOOP --------
def process_input(user_input, state):

    update_memory(state, user_input)

    action = agent_planner(user_input, state)

    if action == "decision":
        return decision_tool(user_input, state["decision"])

    elif action == "clarity":
        return clarity_tool(user_input, state["clarity"])

    else:
        prompt = f"""
You are GroBot, an AI mentor aligned with Sustainable Development Goals.

Your goal:
- Help users grow
- Provide clarity in decisions
- Guide them toward better futures
"""
        response = llm_tool(prompt)

        # -------- SELF-IMPROVEMENT LOOP --------
        if is_response_weak(response):
            improved = improve_response(user_input, state, response)

            # Only replace if actually better
            if len(improved) > len(response):
                response = improved

        return response
