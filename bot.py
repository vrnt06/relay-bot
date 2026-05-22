import streamlit as st
from google import genai

# -------- SETUP --------
api_key = st.secrets.get("GEMINI_API_KEY", None)

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


# -------- MEMORY --------
def update_memory(state, user_input):
    state["history"].append(user_input)
    return state


# -------- PLANNER --------
def agent_planner(user_input):
    text = user_input.lower()

    if any(w in text for w in ["choose", "decision", "between"]):
        return "decision"

    if any(w in text for w in ["confused", "lost", "don't know"]):
        return "clarity"

    return "llm"


# -------- LLM TOOL --------
def llm_tool(prompt):
    if not client:
        return "Let’s think this through logically."

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except:
        return "Let’s think this through logically."


# -------- DECISION TOOL --------
def decision_tool(user_input, state):
    if not state["active"]:
        state["active"] = True
        state["step"] = 1
        return "What are the options you're choosing between?"

    if state["step"] == 1:
        state["options"] = user_input
        state["step"] = 2
        return "Which option feels right instinctively?"

    elif state["step"] == 2:
        state["instinct"] = user_input
        state["step"] = 3
        return "Which option is more practical?"

    elif state["step"] == 3:
        state["practical"] = user_input
        state["active"] = False

        return f"""
Decision Analysis:

Options: {state["options"]}

- Instinct points to: {state["instinct"]}
- Practical choice: {state["practical"]}

Final insight:
If both align → that's your answer.
If not → decide what matters more now: emotion or stability.
"""


# -------- CLARITY TOOL --------
def clarity_tool(user_input, state):
    if not state["active"]:
        state["active"] = True
        state["step"] = 1
        return "What exactly is confusing you?"

    if state["step"] == 1:
        state["problem"] = user_input
        state["step"] = 2
        return "What outcome are you afraid of?"

    elif state["step"] == 2:
        state["fear"] = user_input
        state["active"] = False

        return f"""
Clarity Breakdown:

- Problem: {state["problem"]}
- Fear: {state["fear"]}

Insight:
You’re not stuck because of lack of options.
You’re stuck because of uncertainty.

Define the next small step — not the whole future.
"""


# -------- MAIN AGENT --------
def process_input(user_input, global_state):

    # Update memory
    global_state = update_memory(global_state, user_input)

    # Get states
    decision_state = global_state["decision"]
    clarity_state = global_state["clarity"]

    # Continue active tool
    if decision_state["active"]:
        return decision_tool(user_input, decision_state)

    if clarity_state["active"]:
        return clarity_tool(user_input, clarity_state)

    # Plan next step
    action = agent_planner(user_input)

    # Execute tool
    if action == "decision":
        return decision_tool(user_input, decision_state)

    elif action == "clarity":
        return clarity_tool(user_input, clarity_state)

    else:
        prompt = f"""
You are a strategic AI assistant.

User: {user_input}

Respond clearly and intelligently.
"""
        return llm_tool(prompt)
