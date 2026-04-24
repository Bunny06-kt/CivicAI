import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# LOAD ENV

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# CLEAN JSON HELPER

def clean_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")
    return text

# 1. INTENT DETECTION

def detect_intent(user_input):
    prompt = f"""
You are an AI civic services agent.

Classify the user's intent and extract key info.

Intents:
- apply_scheme
- track_application
- find_scheme
- nearest_office
- general_query

Return ONLY valid JSON:

{{
  "intent": "",
  "scheme": "",
  "location": "",
  "language": ""
}}

User Input: {user_input}
"""

    try:
        response = model.generate_content(prompt)
        text = clean_json(response.text)
        return json.loads(text)
    except:
        return {
            "intent": "general_query",
            "scheme": None,
            "location": None,
            "language": "english"
        }


# 2. AGENT DECISION LOGIC

def agent_action(intent_data):
    intent = intent_data.get("intent")
    scheme = intent_data.get("scheme")

    if intent == "apply_scheme":
        return {
            "action": "autofill_form",
            "response": f"Your application for {scheme or 'Solar Subsidy'} is ready.",
            "data": {
                "scheme": scheme or "Solar Subsidy",
                "form_fields": {
                    "name": "Demo User",
                    "income": "3 LPA",
                    "location": "Bangalore"
                }
            }
        }

    elif intent == "find_scheme":
        return {
            "action": "recommend_scheme",
            "response": "You are eligible for Solar Subsidy with up to 40% benefit.",
            "data": {
                "scheme": "Solar Subsidy"
            }
        }

    elif intent == "nearest_office":
        return {
            "action": "provide_location",
            "response": "Nearest service center is 2 km away in Bangalore.",
            "data": {
                "office": "Bangalore Civic Center"
            }
        }

    elif intent == "track_application":
        return {
            "action": "show_status",
            "response": "Your application is currently under review.",
            "data": {
                "status": "Under Review"
            }
        }

    else:
        return {
            "action": "answer_query",
            "response": "I can help you apply for schemes, track applications, or find nearby services.",
            "data": {}
        }


# 3. MULTILINGUAL RESPONSE

def multilingual_response(user_input, response_text):
    prompt = f"""
Respond in the SAME language as the user input.

User Input: {user_input}
Response: {response_text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return response_text


# MAIN FUNCTION (CALL THIS)

def process_user_input(user_input):
    intent_data = detect_intent(user_input)
    action_result = agent_action(intent_data)

    final_response = multilingual_response(
        user_input,
        action_result["response"]
    )

    action_result["response"] = final_response
    action_result["intent_data"] = intent_data  # helpful for debug/demo

    return action_result

# TEST MODE

if __name__ == "__main__":
    print("Civic AI Agent Started (Gemini)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = process_user_input(user_input)

        print("\n🤖 Agent Output:")
        print(json.dumps(result, indent=2))
        print("\n" + "-"*40)