import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

class TokenServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/submit-token' in self.path:
            # Parse the token from URL
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'token' in params:
                token = params['token'][0]
                
                # Save token
                token_data = {
                    "bearer_token": token,
                    "token_expiry": int(time.time()) + 43200
                }
                
                with open('token.json', 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                html = """
                <html>
                <head>
                    <title>Token Received</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                        }
                        h1 { color: #4CAF50; margin: 0 0 20px 0; }
                        p { color: #666; font-size: 16px; }
                        .checkmark {
                            font-size: 64px;
                            color: #4CAF50;
                            animation: scaleIn 0.5s ease-in-out;
                        }
                        @keyframes scaleIn {
                            from { transform: scale(0); }
                            to { transform: scale(1); }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="checkmark">✓</div>
                        <h1>Token Received!</h1>
                        <p>Your authentication token has been saved.</p>
                        <p>You can close this window.</p>
                    </div>
                    <script>
                        setTimeout(() => window.close(), 3000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                print("\n✓ Token received and saved!")
                print(f"Token preview: {token[:50]}...")
                return
        
        # Default response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = "<html><body><h1>FlairsTech Token Server Running</h1></body></html>"
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass

def start_token_server():
    server = HTTPServer(('localhost', 8765), TokenServer)
    print("=" * 60)
    print("   FlairsTech Token Server")
    print("=" * 60)
    print("")
    print("Server running on: http://localhost:8765")
    print("")
    print("Waiting for token from bookmarklet...")
    print("(Press Ctrl+C to stop)")
    print("")
    server.serve_forever()

if __name__ == '__main__':
    start_token_server()