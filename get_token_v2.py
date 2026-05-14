import time
import json
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

print("=" * 60)
print("       FlairsTech Auto Token Capture")
print("=" * 60)
print("")
print("This will open your browser and capture your token.")
print("Just make sure you're logged into attendance.flairstech.com")
print("")
print("Press ENTER to continue...")
input()

token_captured = None
server_running = True

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global token_captured, server_running
        
        # Capture token from URL parameter
        if '/capture' in self.path:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'token' in params:
                token_captured = params['token'][0]
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <head>
                    <title>Token Captured</title>
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; }
                        h1 { color: green; }
                    </style>
                </head>
                <body>
                    <h1>✓ Token Captured Successfully!</h1>
                    <p>You can close this window and return to the Command Prompt.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                server_running = False
                return
        
        # Serve the token extraction page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # JavaScript to extract token from attendance site
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FlairsTech Token Capture</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }
                .step {
                    background: #f0f0f0;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }
                button {
                    background: #4CAF50;
                    color: white;
                    padding: 15px 32px;
                    font-size: 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 10px;
                }
                button:hover { background: #45a049; }
                #status { margin-top: 20px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>FlairsTech Token Capture</h1>
            
            <div class="step">
                <h3>Step 1: Open Attendance Site</h3>
                <button onclick="openAttendance()">Open Attendance.FlairsTech.com</button>
                <p id="step1status"></p>
            </div>
            
            <div class="step">
                <h3>Step 2: Capture Token</h3>
                <p>After logging in, click this button:</p>
                <button onclick="captureToken()">Capture My Token</button>
                <p id="step2status"></p>
            </div>
            
            <div id="status"></div>
            
            <script>
                let attendanceWindow = null;
                
                function openAttendance() {
                    document.getElementById('step1status').innerHTML = 
                        '<span style="color: blue;">Opening attendance site...</span>';
                    
                    attendanceWindow = window.open(
                        'https://attendance.flairstech.com', 
                        'attendance',
                        'width=1200,height=800'
                    );
                    
                    setTimeout(() => {
                        document.getElementById('step1status').innerHTML = 
                            '<span style="color: green;">✓ Opened! Make sure you are logged in, then click Step 2.</span>';
                    }, 1000);
                }
                
                function captureToken() {
                    if (!attendanceWindow || attendanceWindow.closed) {
                        document.getElementById('step2status').innerHTML = 
                            '<span style="color: red;">Please complete Step 1 first!</span>';
                        return;
                    }
                    
                    document.getElementById('step2status').innerHTML = 
                        '<span style="color: blue;">Attempting to capture token...</span>';
                    
                    // Try to access the window's localStorage
                    try {
                        let token = attendanceWindow.localStorage.getItem('access_token') ||
                                   attendanceWindow.sessionStorage.getItem('access_token');
                        
                        if (token) {
                            // Send token to our server
                            window.location.href = 'http://localhost:8765/capture?token=' + 
                                encodeURIComponent(token);
                        } else {
                            // If not in storage, try to intercept from API calls
                            document.getElementById('step2status').innerHTML = 
                                '<span style="color: orange;">Token not found in storage. Trying alternative method...</span>';
                            
                            // Alternative: inject script to capture from network requests
                            injectTokenCapture();
                        }
                    } catch (e) {
                        document.getElementById('step2status').innerHTML = 
                            '<span style="color: red;">Error: ' + e.message + 
                            '<br/>This might be due to browser security. Try the manual method.</span>';
                    }
                }
                
                function injectTokenCapture() {
                    // This tries to inject code into the attendance window to capture API calls
                    try {
                        attendanceWindow.eval(`
                            (function() {
                                const originalFetch = window.fetch;
                                window.fetch = function(...args) {
                                    return originalFetch.apply(this, args).then(response => {
                                        // Capture authorization header
                                        if (args[1] && args[1].headers) {
                                            const auth = args[1].headers.authorization || 
                                                        args[1].headers.Authorization;
                                            if (auth && auth.startsWith('Bearer ')) {
                                                const token = auth.substring(7);
                                                window.opener.postMessage({
                                                    type: 'TOKEN_CAPTURED',
                                                    token: token
                                                }, '*');
                                            }
                                        }
                                        return response;
                                    });
                                };
                                
                                // Trigger a refresh to capture token
                                window.location.reload();
                            })();
                        `);
                        
                        document.getElementById('step2status').innerHTML = 
                            '<span style="color: blue;">Waiting for network request...</span>';
                        
                    } catch (e) {
                        document.getElementById('step2status').innerHTML = 
                            '<span style="color: red;">Browser security prevented automatic capture.<br/>' +
                            'Please use the manual method: python manual_token.py</span>';
                    }
                }
                
                // Listen for token from injected script
                window.addEventListener('message', function(event) {
                    if (event.data.type === 'TOKEN_CAPTURED') {
                        window.location.href = 'http://localhost:8765/capture?token=' + 
                            encodeURIComponent(event.data.token);
                    }
                });
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def run_server():
    global server_running
    server = HTTPServer(('localhost', 8765), TokenHandler)
    print("✓ Server started on http://localhost:8765")
    while server_running:
        server.handle_request()

# Start server
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

time.sleep(1)

print("✓ Opening browser...")
print("")
print("INSTRUCTIONS:")
print("1. A page will open with two buttons")
print("2. Click 'Open Attendance.FlairsTech.com'")
print("3. Make sure you're logged in")
print("4. Click 'Capture My Token'")
print("")

webbrowser.open('http://localhost:8765')

# Wait for token
timeout = 600  # 10 minutes
start_time = time.time()

print("Waiting for token... (timeout in 10 minutes)")
print("")

while token_captured is None and (time.time() - start_time) < timeout:
    time.sleep(1)

if token_captured:
    # Save token
    token_data = {
        "bearer_token": token_captured,
        "token_expiry": int(time.time()) + 43200  # 12 hours
    }
    
    with open('token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("=" * 60)
    print("SUCCESS! Token captured and saved!")
    print("=" * 60)
    print("")
    print("Token preview: " + token_captured[:50] + "...")
    print("Token length: " + str(len(token_captured)) + " characters")
    print("")
    print("Next step: Run 'python get_locations.py'")
    print("=" * 60)
else:
    print("=" * 60)
    print("TIMEOUT: Could not capture token")
    print("=" * 60)
    print("")
    print("This can happen due to browser security restrictions.")
    print("")
    print("FALLBACK OPTION:")
    print("Run: python manual_token.py")
    print("")
    print("(Don't worry - the main app will handle this automatically")
    print("for end users with a simpler flow)")