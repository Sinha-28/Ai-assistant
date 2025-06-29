import google.generativeai as genai
import pyttsx3
import webbrowser
import datetime
from config import gemini_api_key

# Voice Engine Setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Slightly slower speech

def speak(text):
    """Improved text-to-speech with error handling"""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# Gemini AI Setup
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

def get_voice_input():
    """Enhanced voice input with better feedback"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("\n🎤 Listening... (Say 'text mode' to switch)")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=8, phrase_time_limit=10)
            query = r.recognize_google(audio).lower()
            print(f"👤 You (voice): {query}")
            return query
    except sr.WaitTimeoutError:
        print("No speech detected")
    except Exception as e:
        print(f"Voice Error: {e}")
    return None

def get_text_input():
    """Text input with clear prompts"""
    try:
        query = input("\n⌨️ You (text): ").strip().lower()
        if query:
            return query
        return None
    except EOFError:
        return "exit"

def handle_commands(query, current_mode):
    """All special commands in one place"""
    commands = {
        # Mode switching
        "text mode": ("Switching to text mode", "text"),
        "voice mode": ("Switching to voice mode", "voice"),
        
        # Websites
        "open youtube": ("Opening YouTube", lambda: webbrowser.open("https://youtube.com")),
        "open google": ("Opening Google", lambda: webbrowser.open("https://google.com")),
        
        # Utilities
        "time": (f"The time is {datetime.datetime.now().strftime('%I:%M %p')}", None),
        "date": (f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}", None),
        
        # Exit
        "exit": ("Goodbye!", "exit")
    }
    
    for cmd, (response, action) in commands.items():
        if cmd in query:
            speak(response)
            
            if isinstance(action, str):
                return action  # New mode or exit signal
            elif callable(action):
                action()  # Execute function (e.g., open website)
            
            return current_mode  # Stay in current mode
    
    return None  # No command matched

def main():
    speak("Gemini Assistant Ready")
    
    # Initial mode selection
    while True:
        mode = input("Choose mode:\n1. Voice\n2. Text\n> ").strip()
        if mode in ("1", "2"):
            current_mode = "voice" if mode == "1" else "text"
            speak(f"Entering {current_mode} mode. Say 'help' for commands.")
            break
    
    # Main interaction loop
    while True:
        try:
            # Get input based on mode
            query = get_voice_input() if current_mode == "voice" else get_text_input()
            if not query:
                continue
            
            # Handle special commands
            result = handle_commands(query, current_mode)
            if result == "exit":
                break
            elif result in ("voice", "text"):
                current_mode = result
                continue
            
            # Get AI response
            print("\n🤖 Gemini is thinking...")
            response = chat.send_message(query)
            print(f"🤖 Gemini: {response.text}")
            speak(response.text)
            
        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, I encountered an error")

if __name__ == "__main__":
    main()
