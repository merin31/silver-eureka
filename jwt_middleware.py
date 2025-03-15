import jwt
from utils import send_response
from config import JWT_CONFIG, ROLE_PERMISSIONS_CONFIG


def verify_jwt(handler):
    
    auth_header = handler.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        send_response(handler, {"error": "Missing or invalid token"}, status=401)
        return None

    token = auth_header.split(" ")[1]

    try:
        decoded_token = jwt.decode(
            token,
            JWT_CONFIG.get('secret_key'),
            algorithms=["HS256"]
        )
        return decoded_token
    except jwt.ExpiredSignatureError:
        send_response(handler, {"error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        send_response(handler, {"error": "Invalid token"}, status=401)

    return None


def check_permissions(handler, decoded_token, resource, method):
    allowed_roles = ROLE_PERMISSIONS_CONFIG.get(resource, {}).get(method, [])

    if decoded_token["role"] not in allowed_roles:
        send_response(handler, {"error": "Permission denied"}, status=403)
        return False

    return True

