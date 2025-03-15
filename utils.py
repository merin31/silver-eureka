import json
import jwt
import datetime
from config import JWT_CONFIG



def send_response(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())


def generate_jwt(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(
            seconds=JWT_CONFIG.get('token_expiry')
        )
    }
    return jwt.encode(payload, JWT_CONFIG.get('secret_key'), algorithm="HS256")


