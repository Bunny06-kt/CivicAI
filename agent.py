import json
import os
from dotenv import load_dotenv

# -----------------------------
# LOAD GEMINI
# -----------------------------
USE_AI = True

try:
    import google.generativeai as genai
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    USE_AI = False


# -----------------------------
# RULE-BASED INTENT (FAST FALLBACK)
# -----------------------------
def rule_based_intent(user_input):
    text = user_input.lower()

    if "subsidy" in text or "सोलर" in text or "beku" in text:
        return "apply_scheme"

    if "track" in text or "status" in text:
        return "track_application"

    if "office" in text or "near" in text:
        return "nearest_office"

    return "general_query"


# -----------------------------
# GEMINI INTENT (SMART)
# -----------------------------
def ai_intent(user_input):
    if not USE_AI:
        return None

    prompt = f"""
Classify user intent into ONE of:
apply_scheme / track_application / nearest_office / general_query

Input: {user_input}
Output:
"""

    try:
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()

        if intent in ["apply_scheme", "track_application", "nearest_office", "general_query"]:
            return intent
    except:
        return None

    return None


# -----------------------------
# FINAL INTENT (HYBRID)
# -----------------------------
def get_intent(user_input):
    ai_result = ai_intent(user_input)

    if ai_result:
        return ai_result

    return rule_based_intent(user_input)


# -----------------------------
# GEMINI TRANSLATION (OPTIONAL)
# -----------------------------
def ai_translate(user_input, text):
    if not USE_AI:
        return text

    prompt = f"""
Translate the response into the SAME language as input.

Input: {user_input}
Response: {text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text


# -----------------------------
# FALLBACK MULTILINGUAL
# -----------------------------
def fallback_translate(user_input, result):
    text = user_input.lower()

    if any('\u0900' <= ch <= '\u097F' for ch in text):
        lang = "hindi"
    elif any(word in text for word in ["beku", "nanage", "illa", "ide"]):
        lang = "kannada"
    else:
        lang = "english"

    intent = result.get("intent")

    translations = {
        "hindi": {
            "apply_scheme": "आपका सोलर सब्सिडी आवेदन तैयार है।",
            "track_application": "आपका आवेदन समीक्षा में है।",
            "nearest_office": "निकटतम कार्यालय 2 किमी दूर है।",
            "general_query": "मैं आपकी योजनाओं और सेवाओं में मदद कर सकता हूँ।"
        },
        "kannada": {
            "apply_scheme": "ನಿಮ್ಮ ಸೊಲಾರ್ ಸಬ್ಸಿಡಿ ಅರ್ಜಿ ಸಿದ್ಧವಾಗಿದೆ.",
            "track_application": "ನಿಮ್ಮ ಅರ್ಜಿ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ.",
            "nearest_office": "ಹತ್ತಿರದ ಕಚೇರಿ 2 ಕಿಮೀ ದೂರದಲ್ಲಿದೆ.",
            "general_query": "ನಾನು ಯೋಜನೆಗಳು ಮತ್ತು ಸೇವೆಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಬಹುದು."
        }
    }

    if lang in translations and intent in translations[lang]:
        return translations[lang][intent]

    return result["response"]


# -----------------------------
# MAIN AGENT
# -----------------------------
def agent(user_input):
    intent = get_intent(user_input)

    if intent == "apply_scheme":
        result = {
            "intent": intent,
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
                "office_visits_required": "Minimum 1 visit"
            }
        }

    elif intent == "track_application":
        result = {
            "intent": intent,
            "action": "show_status",
            "response": "Your application is under review.",
            "data": {
                "status": "Under Review",
                "office_visits_required": "0–1 visits"
            }
        }

    elif intent == "nearest_office":
        result = {
            "intent": intent,
            "action": "provide_location",
            "response": "Nearest office is 2 km away.",
            "data": {
                "office": "Bangalore Civic Center",
                "timing": "10 AM - 5 PM"
            }
        }

    else:
        result = {
            "intent": "general_query",
            "action": "answer_query",
            "response": "I can help you apply for schemes, track applications, and find nearby services.",
            "data": {}
        }

    # -----------------------------
    # TRANSLATION LOGIC (HYBRID)
    # -----------------------------
    if USE_AI:
        result["response"] = ai_translate(user_input, result["response"])
    else:
        result["response"] = fallback_translate(user_input, result)

    return result


# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Agent (Gemini + Fallback)\n")

    while True:
        user_input = input("🎤 You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent(user_input)

        print("\n🤖 Agent Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "-" * 40)