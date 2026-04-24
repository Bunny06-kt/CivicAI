import json
import os
from dotenv import load_dotenv

# Disable AI for stable demo
USE_AI = False


# -----------------------------
# RULE-BASED INTENT
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
# FINAL INTENT
# -----------------------------
def get_intent(user_input):
    return rule_based_intent(user_input)


# -----------------------------
# MULTILINGUAL RESPONSE (FIXED)
# -----------------------------
def translate_response(user_input, result):
    text = user_input.lower()

    # Improved Language Detection
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
                "office_visits_required": "Minimum 1 visit",
                "form_fields": {
                    "name": "Demo User",
                    "income": "3 LPA",
                    "location": "Bangalore"
                }
            }
        }

    elif intent == "track_application":
        result = {
            "intent": intent,
            "action": "show_status",
            "response": "Your application is under review.",
            "data": {
                "status": "Under Review",
                "office_visits_required": "0–1 visits",
                "next_step": "Wait for approval"
            }
        }

    elif intent == "nearest_office":
        result = {
            "intent": intent,
            "action": "provide_location",
            "response": "Nearest office is 2 km away.",
            "data": {
                "office": "Bangalore Civic Center",
                "timing": "10 AM - 5 PM",
                "office_visits_required": "1 visit"
            }
        }

    else:
        result = {
            "intent": "general_query",
            "action": "answer_query",
            "response": "I can help you apply for schemes, track applications, and find nearby services.",
            "data": {}
        }

    # Multilingual conversion
    result["response"] = translate_response(user_input, result)

    return result


# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Agent (Stable Multilingual Demo)\n")

    while True:
        user_input = input("🎤 You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent(user_input)

        print("\n🤖 Agent Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "-" * 40)