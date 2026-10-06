import json
import urllib.request
import urllib.error
import time
import sys

# Reconfigure stdout to support UTF-8 characters on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def query_ollama(messages):
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
        # Set a timeout of 60 seconds for the request to load/respond
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("message", {}).get("content", "")
    except Exception as e:
        return f"[Error: {e}]"

def run_scenario(name, conversation_steps):
    print(f"\n==========================================", flush=True)
    print(f"SCENARIO: {name}", flush=True)
    print(f"==========================================", flush=True)
    
    messages = []
    for step in conversation_steps:
        print(f"\nMentor: {step}", flush=True)
        messages.append({"role": "user", "content": step})
        
        # Query Ollama
        reply = query_ollama(messages)
        print(f"Student: {reply}", flush=True)
        messages.append({"role": "assistant", "content": reply})
        time.sleep(1)

def main():
    print("Starting automated persona verification...", flush=True)
    
    # Scenario 1: Counselor is direct and nosey immediately. 
    run_scenario(
        "Direct/Nosey Approach",
        [
            "Hey, you look super stressed out and I heard you're having personal issues. You need to open up to me so we can fix it.",
            "But you're failing your rounds and you look like you haven't slept in days. What's really going on?"
        ]
    )

    # Scenario 2: Counselor builds rapport.
    run_scenario(
        "Empathetic & Rapport-Building Approach",
        [
            "Hey, do you have a few minutes? I was just grabbing a coffee and wanted to check in and see how your week is going.",
            "Yeah, rotation blocks are absolutely brutal. I remember my 3rd year was just a blur of exams and sleep deprivation. How are you holding up with the workload?",
            "Honestly, it's totally okay to feel exhausted. It is a lot of pressure, and you don't have to carry all of it on your own. If you ever want to grab a coffee and just vent, I'm here. No pressure at all."
        ]
    )

if __name__ == "__main__":
    main()
