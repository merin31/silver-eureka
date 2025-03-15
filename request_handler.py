import http.server
import json
from urllib.parse import urlparse
from auth import AuthService
from users import UserService
from artist import ArtistService
from music import MusicService



class RequestHandler(http.server.BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.auth_service = AuthService()
        self.user_service = UserService()
        self.artist_service = ArtistService()
        self.music_service = MusicService()
        super().__init__(*args, **kwargs)


    def do_POST(self):
        """Handles POST requests."""
        
        path = urlparse(self.path).path

        if path == "/register/":
            self.auth_service.register_user(self)
            print('register')
        elif path == "/login/":
            self.auth_service.login_user(self)
        elif path == "/users/":
            self.user_service.handle_request(self,'POST')
        elif path == "/artists/":
            self.artist_service.handle_request(self, "POST")
        elif path == "/music/":
            self.music_service.handle_request(self, "POST")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid route"}')

    def do_GET(self):
        path = urlparse(self.path).path
        print(path,'path')
        if path == '/users/':
            self.user_service.handle_request(self, "GET")
        elif path.startswith("/artists/"):
            self.artist_service.handle_request(self, "GET")
        elif path.startswith("/music/"):
            self.music_service.handle_request(self, "GET")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_PUT(self):
        path = urlparse(self.path).path
        print(path)
        if "/users/" in path:
            self.user_service.handle_request(self, "PUT")
        elif "/artists/" in path:
            self.artist_service.handle_request(self, "PUT")
        elif "/music/" in path:
            self.music_service.handle_request(self, "PUT")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')


    def do_DELETE(self):
        path = urlparse(self.path).path

        if path.startswith("/users/"):
            self.user_service.handle_request(self, "DELETE")
        elif path.startswith("/artists/"):
            self.artist_service.handle_request(self, "DELETE")
        elif path.startswith("/music/"):
            self.music_service.handle_request(self, "DELETE")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
