import json
import os
from dotenv import load_dotenv

# Try to load Gemini (optional)
USE_AI = True

try:
    import google.generativeai as genai
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    USE_AI = False


# -----------------------------
# RULE-BASED INTENT (FAST + SAFE)
# -----------------------------
def rule_based_intent(user_input):
    text = user_input.lower()

    if "subsidy" in text or "सब्सिडी" in text or "beku" in text:
        return "apply_scheme"

    if "track" in text or "status" in text:
        return "track_application"

    if "office" in text or "near" in text:
        return "nearest_office"

    return "general_query"


# -----------------------------
# OPTIONAL AI INTENT (MULTILINGUAL BOOST)
# -----------------------------
def ai_intent(user_input):
    if not USE_AI:
        return None

    prompt = f"""
Detect intent of user.

Return ONLY one word:
apply_scheme / track_application / nearest_office / general_query

Input: {user_input}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except:
        return None


# -----------------------------
# FINAL INTENT DECISION
# -----------------------------
def get_intent(user_input):
    ai_result = ai_intent(user_input)

    if ai_result in ["apply_scheme", "track_application", "nearest_office"]:
        return ai_result

    return rule_based_intent(user_input)


# -----------------------------
# MULTILINGUAL RESPONSE (AI)
# -----------------------------
def translate_response(user_input, response_text):
    if not USE_AI:
        return response_text

    prompt = f"""
Respond in SAME language as input.

Input: {user_input}
Response: {response_text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return response_text


# -----------------------------
# MAIN AGENT LOGIC
# -----------------------------
def agent(user_input):
    intent = get_intent(user_input)

    # APPLY SCHEME
    if intent == "apply_scheme":
        result = {
            "action": "autofill_form",
            "response": "Your Solar Subsidy application is ready.",
            "data": {
                "scheme": "Solar Subsidy",
                "documents_required": [
                    "Aadhaar Card",
                    "Electricity Bill",
                    "Bank Passbook",
                    "Income Certificate"
                ],
                "office_visits_required": "Minimum 1 visit",
                "form_fields": {
                    "name": "Demo User",
                    "income": "3 LPA",
                    "location": "Bangalore"
                }
            }
        }

    # TRACK
    elif intent == "track_application":
        result = {
            "action": "show_status",
            "response": "Your application is under review.",
            "data": {
                "status": "Under Review",
                "office_visits_required": "0–1 visits",
                "next_step": "Wait for approval"
            }
        }

    # OFFICE
    elif intent == "nearest_office":
        result = {
            "action": "provide_location",
            "response": "Nearest office is 2 km away.",
            "data": {
                "office": "Bangalore Civic Center",
                "timing": "10 AM - 5 PM",
                "office_visits_required": "1 visit"
            }
        }

    # DEFAULT
    else:
        result = {
            "action": "answer_query",
            "response": "I can help you apply for schemes, track applications, and find nearby services.",
            "data": {}
        }

    # Apply multilingual response
    result["response"] = translate_response(user_input, result["response"])

    return result


# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Hybrid Agent (Multilingual + Safe)\n")

    while True:
        user_input = input("🎤 You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent(user_input)

        print("\n🤖 Agent Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "-" * 40)