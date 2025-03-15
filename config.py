import os
from dotenv import load_dotenv

load_dotenv()

JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY"),
    "token_expiry": int(os.getenv("JWT_TOKEN_EXPIRY", 3600))
}


ROLE_PERMISSIONS_CONFIG = {
    
    "users": {
        "GET": ["super_admin"],
        "POST": ["super_admin"],
        "PUT": ["super_admin"],
        "DELETE": ["super_admin"]
    },
    
    "artists": {
        "GET": ["super_admin", "artist_manager"],
        "POST": ["artist_manager"],
        "PUT": ["artist_manager"],
        "DELETE": ["artist_manager"]
    },
    
    "music": {
        "GET": ["super_admin", "artist_manager", "artist"],
        "POST": ["artist"],
        "PUT": ["artist"],
        "DELETE": ["artist"]
    }
    
}