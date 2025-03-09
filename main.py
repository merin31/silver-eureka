import json
from request_handler import RequestHandler
import http.server

PORT = 8080



if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), RequestHandler)
    print(f"Server running on port {PORT}...")
    server.serve_forever()
