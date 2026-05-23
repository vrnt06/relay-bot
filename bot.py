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

def detect_sdg(user_input):
    text = user_input.lower()

    # SDG 4: Education & learning
    if any(w in text for w in [
        "study", "career", "future", "choose", "college",
        "course", "learn", "education", "what should i do"
    ]):
        return "SDG 4: Quality Education"

    # SDG 3: Mental well-being
    if any(w in text for w in [
        "stress", "anxiety", "overthinking", "lost",
        "confused", "mental", "pressure", "tired"
    ]):
        return "SDG 3: Good Health & Well-being"

    # SDG 8: Jobs & growth
    if any(w in text for w in [
        "job", "salary", "money", "income",
        "growth", "promotion", "work", "business"
    ]):
        return "SDG 8: Decent Work & Economic Growth"

    # Default fallback
    return "General Guidance"

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
    if not response:
        return True

    weak_signals = ["i don't know", "maybe", "not sure"]

    if len(response) < 25:
        return True

    return any(signal in response.lower() for signal in weak_signals)

# -------- RETRY IMPROVER --------
def improve_response(user_input, state, prev_response):
    prompt = f"""
You are GrowBot.

Rewrite the answer to make it:
- Shorter
- More personal
- Focused on the user

STRICT RULES:
- Max 6 lines total
- Include 1 personal reflection line
- No bullet points
- No headings like "Option 1"

User: {user_input}
Previous Answer:
{prev_response}
"""
    return llm_tool(prompt)
    
def is_general_query(user_input):
    keywords = ["what is", "who is", "tell me", "define", "explain"]
    return any(k in user_input.lower() for k in keywords)

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

    elif action == "llm":
        response = ""  # safety
    
        sdg = detect_sdg(user_input)
    
        if is_general_query(user_input):
            prompt = f"""
            You are GrowBot, an AI mentor aligned with {sdg}.
            
            The user asked a general question.
            
            STRICT FORMAT (MUST FOLLOW):
            
            1. Direct Answer (2–3 lines max)
            2. Why it matters (growth / career / SDG)
            3. Personal Reflection (1–2 lines ONLY, directly addressing the user)
            
            DO NOT:
            - Give long explanations
            - Give multiple sections or options
            - Add unnecessary details
            
            User: {user_input}
            """
        else:
            prompt = f"""
    You are GrowBot, an AI mentor aligned with {sdg}.
    
    Your goal:
    - Help users think clearly
    - Guide real-life decisions
    - Align responses with personal growth
    
    STRICT INSTRUCTIONS:
    - Do NOT introduce yourself
    - Be clear and structured
    - Relate everything to the user's life
    - End with ONE actionable or reflective question
    
    Conversation history:
    {state.get("history", [])[-3:]}
    
    User: {user_input}
    """
    
        # 🔥 CALL LLM
        response = llm_tool(prompt)
    
        # -------- SELF-IMPROVEMENT LOOP --------
        if response and is_response_weak(response):
            improved = improve_response(user_input, state, response)
    
            if improved and len(improved) > len(response):
                response = improved
    
        return response
