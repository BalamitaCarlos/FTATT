import time
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading

print("=" * 60)
print("       FlairsTech Token Extractor")
print("=" * 60)
print("")
print("This will:")
print("1. Open the attendance website in your browser")
print("2. You log in normally (Microsoft SSO)")
print("3. We'll capture your token automatically")
print("4. Token will be saved to token.json")
print("")
print("Press ENTER to start...")
input()

token_captured = None
server_running = True

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global token_captured, server_running
        
        if '/capture' in self.path:
            match = re.search(r'token=([^&]+)', self.path)
            if match:
                token_captured = match.group(1)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = "<html><body><h1>Token Captured!</h1><p>You can close this window.</p></body></html>"
                self.wfile.write(response.encode())
                server_running = False
                return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """<html>
<head><title>FlairsTech Token Capture</title></head>
<body>
<h2>Redirecting to login...</h2>
<script>
    window.location.href = 'https://attendance.flairstech.com/';
    
    setTimeout(function() {
        var token = localStorage.getItem('access_token') || 
                   sessionStorage.getItem('access_token');
        
        if (token) {
            window.location.href = 'http://localhost:8765/capture?token=' + token;
        }
    }, 3000);
</script>
</body>
</html>"""
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass

def run_server():
    global server_running
    server = HTTPServer(('localhost', 8765), TokenHandler)
    while server_running:
        server.handle_request()

print("Starting local server on http://localhost:8765")
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

time.sleep(1)
print("Opening browser... Please log in normally.")
webbrowser.open('http://localhost:8765')

timeout = 300
start_time = time.time()

while token_captured is None and (time.time() - start_time) < timeout:
    time.sleep(1)
    
if token_captured:
    token_data = {
        "bearer_token": token_captured,
        "token_expiry": int(time.time()) + 43200
    }
    
    with open('token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("")
    print("Token saved successfully!")
    print("Token (first 50 chars): " + token_captured[:50] + "...")
    print("")
    print("You're ready to run the main app!")
else:
    print("")
    print("Timeout: Could not capture token automatically")
    print("")
    print("MANUAL METHOD:")
    print("1. Go to https://attendance.flairstech.com and log in")
    print("2. Press F12 to open DevTools")
    print("3. Go to Application tab -> Local Storage")
    print("4. Find 'access_token' and copy its value")
    print("5. Run: python manual_token.py")