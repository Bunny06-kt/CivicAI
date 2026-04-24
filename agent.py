import json
import os
from dotenv import load_dotenv

# -----------------------------
# SAFE GEMINI SETUP (OPTIONAL)
# -----------------------------
USE_AI = False  # TURN OFF for full safety

try:
    import google.generativeai as genai
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.0-pro")
        USE_AI = True
except:
    USE_AI = False


# -----------------------------
# RULE-BASED INTENT (PRIMARY)
# -----------------------------
def rule_based_intent(user_input):
    text = user_input.lower()

    if any(word in text for word in [
        "subsidy", 
        "solar",
        "सोलर",
        "सब्सिडी", 
        "beku"
    ]):
        return "apply_scheme"

    if any(word in text for word in [
        "track", 
        "status",
        "स्थिति"
    ]):
        return "track_application"

    if any(word in text for word in [
        "office", 
        "near",
        "केंद्र",
        "पास"
    ]):
        return "nearest_office"

    return "general_query"
# -----------------------------
# OPTIONAL AI INTENT (SAFE)
# -----------------------------
def ai_intent(user_input):
    if not USE_AI:
        return None

    prompt = f"""
Classify into ONE:
apply_scheme / track_application / nearest_office / general_query

Input: {user_input}
Answer:
"""

    try:
        response = model.generate_content(prompt)
        intent = response.text.strip().lower().replace("\n", "")

        if intent in ["apply_scheme", "track_application", "nearest_office", "general_query"]:
            return intent
    except:
        return None

    return None


# -----------------------------
# FINAL INTENT
# -----------------------------
def get_intent(user_input):
    ai_result = ai_intent(user_input)
    return ai_result if ai_result else rule_based_intent(user_input)


# -----------------------------
# LANGUAGE DETECTION
# -----------------------------
def detect_language(user_input):
    text = user_input.lower()

    if any('\u0900' <= ch <= '\u097F' for ch in text):
        return "hindi"
    elif any(word in text for word in ["beku", "nanage", "illa", "ide"]):
        return "kannada"
    else:
        return "english"


# -----------------------------
# MULTILINGUAL RESPONSES (SAFE)
# -----------------------------
def translate_response(intent, lang):
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
        },
        "english": {
            "apply_scheme": "Your Solar Subsidy application is ready.",
            "track_application": "Your application is under review.",
            "nearest_office": "Nearest office is 2 km away.",
            "general_query": "I can help you with schemes and services."
        }
    }

    return translations.get(lang, translations["english"]).get(intent, "OK")


# -----------------------------
# MAIN AGENT
# -----------------------------
def agent(user_input):
    intent = get_intent(user_input)
    lang = detect_language(user_input)

    # APPLY
    if intent == "apply_scheme":
        result = {
            "intent": intent,
            "action": "autofill_form",
            "data": {
                "scheme": "Solar Subsidy",
                "documents_required": [
                    "Aadhaar Card",
                    "Electricity Bill",
                    "Bank Passbook",
                    "Income Certificate"
                ],
                "office_visits_required": "Minimum 1 visit",
                "next_step": "Submit online or visit office"
            }
        }

    # TRACK
    elif intent == "track_application":
        result = {
            "intent": intent,
            "action": "show_status",
            "data": {
                "status": "Under Review",
                "office_visits_required": "0–1 visits",
                "next_step": "Wait for approval"
            }
        }

    # OFFICE
    elif intent == "nearest_office":
        result = {
            "intent": intent,
            "action": "provide_location",
            "data": {
                "office": "Bangalore Civic Center",
                "timing": "10 AM - 5 PM",
                "next_step": "Visit during working hours"
            }
        }

    # DEFAULT
    else:
        result = {
            "intent": "general_query",
            "action": "answer_query",
            "data": {}
        }

    # SAFE RESPONSE (NO API)
    result["response"] = translate_response(intent, lang)

    return result


# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Production Agent (Stable + Offline Ready)\n")

    while True:
        user_input = input("🎤 You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent(user_input)

        print("\n🤖 Agent Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "-" * 40)