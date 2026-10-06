import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os
import sys

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

# Few-shot examples that teach the model how a real guarded student texts.
# These get prepended to every API call so the model always sees correct
# response patterns before generating its own reply.
FEW_SHOT_EXAMPLES = [
    {"role": "user",      "content": "hey"},
    {"role": "assistant", "content": "hey"},
    {"role": "user",      "content": "how are you doing today?"},
    {"role": "assistant", "content": "im okay, just tired"},
    {"role": "user",      "content": "how was your day?"},
    {"role": "assistant", "content": "it was fine, just long"},
    {"role": "user",      "content": "you seem stressed lately, want to talk about it?"},
    {"role": "assistant", "content": "nah im good, just busy with rotations"},
    {"role": "user",      "content": "I'm here if you need to talk"},
    {"role": "assistant", "content": "yeah thanks... i dont really have much to say tho"},
    {"role": "user",      "content": "are you sleeping okay?"},
    {"role": "assistant", "content": "i mean, enough i guess. its med school so"},
]

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress per-request logs for cleaner output
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/chat':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Parse request and force stream=true for SSE
        try:
            payload = json.loads(body)
        except Exception:
            self.send_error(400, "Bad JSON")
            return

        # Prepend few-shot examples ONLY when the history is short (under 4 messages).
        # Once the conversation is active, the history itself acts as the examples.
        # This prevents the context from repeating too much, which causes the model
        # to get confused and output lists of numbers (e.g. 0, 1, 2, 3...).
        user_messages = payload.get('messages', [])
        if len(user_messages) < 4:
            payload['messages'] = FEW_SHOT_EXAMPLES + user_messages
        else:
            payload['messages'] = user_messages
            
        payload['stream'] = True
        modified_body = json.dumps(payload).encode('utf-8')

        ollama_req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=modified_body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(ollama_req) as ollama_res:
                # Send headers for SSE (Server-Sent Events)
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                # Stream each NDJSON line from Ollama straight to the browser
                # with content filtering to stop garbage output
                accumulated = ''
                BLOCKED = ['prost', 'Note:', 'prostit', 'sex trade', 'sexual services',
                           'historical and', 'derogatory', 'In modern times',
                           'End of', 'end of session', 'If the user', 'session.', 'another session']

                for line in ollama_res:
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        token = chunk.get('message', {}).get('content', '')
                        done  = chunk.get('done', False)

                        # Filter out tokens that represent stray count-up lines (e.g. "0", "1", "\n0", "\n1")
                        # If the token contains only digits and optional whitespace/newlines, skip it.
                        clean_token = token.strip()
                        if clean_token.isdigit():
                            continue

                        # Cut off immediately if non-ASCII (foreign language / Hebrew / script) characters appear
                        if any(ord(c) > 127 for c in token):
                            event_data = json.dumps({"token": "", "done": True})
                            self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            break

                        accumulated += token

                        # Stop if we detect garbage content or double newlines
                        lower_acc = accumulated.lower()
                        if any(b.lower() in lower_acc for b in BLOCKED):
                            # Send done signal and stop
                            event_data = json.dumps({"token": "", "done": True})
                            self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            break

                        if '\n\n' in accumulated:
                            # Model started a second paragraph — cut it off
                            event_data = json.dumps({"token": "", "done": True})
                            self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            break

                        event_data = json.dumps({"token": token, "done": done})
                        self.wfile.write(f"data: {event_data}\n\n".encode('utf-8'))
                        self.wfile.flush()

                        if done:
                            break
                    except Exception:
                        continue

        except urllib.error.URLError as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            err = json.dumps({"error": f"Ollama unavailable: {e}"})
            self.wfile.write(err.encode('utf-8'))

def main():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.chdir(PUBLIC_DIR)
    socketserver.TCPServer.allow_reuse_address = True

    print(f"[OK] MedCheck server running -> http://localhost:{PORT}")
    try:
        with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()
