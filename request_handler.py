import http.server
import json
from urllib.parse import urlparse
from auth import AuthService

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.auth_service = AuthService()
        super().__init__(*args, **kwargs)


    def do_POST(self):
        """Handles POST requests."""
        
        path = urlparse(self.path).path

        if path == "/register/":
            self.auth_service.register_user(self)
            print('register')
        elif path == "/login/":
            self.auth_service.login_user(self)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid route"}')
