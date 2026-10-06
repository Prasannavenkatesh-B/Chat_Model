import json
import urllib.request
import urllib.error
import sys

def chat_with_ollama(messages):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "chat",
        "messages": messages,
        "stream": False
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Please make sure Ollama is running (`ollama serve` or the desktop app).")
        sys.exit(1)

def main():
    print("=" * 60)
    print("Medical Student Chatbot Persona Verification Tool")
    print("=" * 60)
    print("Scenario:")
    print(" - The Chatbot AI acts as a 3rd-year medical student under high stress.")
    print(" - You act as a Mentor, Counselor, Trainer, or Staff member.")
    print(" - Goal: Build rapport and see if the student behaves realistically (guarded, deflecting, casual) and only gradually opens up.")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 60)
    
    # We maintain history. The system prompt is already defined in the Modelfile, 
    # but we can also rely on it being loaded automatically by Ollama.
    messages = []
    
    while True:
        try:
            user_input = input("\nYou (Counselor/Mentor): ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ["exit", "quit"]:
                print("\nEnding session. Goodbye!")
                break
                
            messages.append({"role": "user", "content": user_input})
            
            print("Student is thinking...", end="\r")
            reply = chat_with_ollama(messages)
            
            # Clear the "thinking..." line
            print(" " * 30, end="\r")
            print(f"Student: {reply}")
            
            messages.append({"role": "assistant", "content": reply})
            
        except KeyboardInterrupt:
            print("\nEnding session. Goodbye!")
            break

if __name__ == "__main__":
    main()
