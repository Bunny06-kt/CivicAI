import json
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import pyttsx3
import tempfile

from agent import agent

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print(f"🔊 {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    fs = 44100
    duration = 4

    print("\n🎤 Speak...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp.name, fs, recording)

    recognizer = sr.Recognizer()

    with sr.AudioFile(temp.name) as source:
        audio = recognizer.record(source)

    try:
        try:
            text = recognizer.recognize_google(audio, language="kn-IN")
        except:
            try:
                text = recognizer.recognize_google(audio, language="hi-IN")
            except:
                text = recognizer.recognize_google(audio, language="en-IN")

        print(f"🗣 {text}")
        return text

    except:
        return None

# -----------------------------
# MAIN LOOP
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Voice Assistant\n")

    while True:
        user_input = listen()

        if not user_input:
            user_input = input("⌨️ Type: ")

        if user_input.lower() in ["exit", "quit"]:
            speak("Goodbye")
            break

        result = agent(user_input)

        print("\n🤖", json.dumps(result, indent=2, ensure_ascii=False))
        speak(result["response"])