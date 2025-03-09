import os
from dotenv import load_dotenv

load_dotenv()

JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY"),
    "token_expiry": int(os.getenv("JWT_TOKEN_EXPIRY", 3600))
}
