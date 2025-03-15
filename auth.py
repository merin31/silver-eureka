import json
from database import DatabaseManager
from utils import send_response, generate_jwt
from validator import Validator


class AuthService:
    def __init__(self):
        self.db = DatabaseManager()

    def register_user(self, handler):
        content_length = int(handler.headers['Content-Length'])
        print(content_length,'content_length')
        # print(handler.rfile.read(content_length),'handler.rfile.read(content_length)')

        if content_length == 0:
            send_response(
                handler,
                {
                    "error": "No data provided"
                }, status=400
            )
            return

        # if not all([first_name, last_name, email, password, phone, dob, gender, address, role]):
        #     send_response(
        #         handler,
        #         {
        #             "error": "Missing required fields"
        #         }, status=400
        #     )
        #     return
        
        post_data = json.loads(handler.rfile.read(content_length))
        print(post_data,'post_data')

        is_valid, message = Validator.validate_user(post_data)
        print(is_valid, message,'is_valid, message')
        if not is_valid:
            send_response(
                handler,
                {
                    "error": message
                }, status=400
            )
            return
        
        first_name = post_data.get("first_name")
        last_name = post_data.get("last_name")
        email = post_data.get("email")
        password = post_data.get("password")
        phone = post_data.get("phone")
        dob = post_data.get("dob")
        gender = post_data.get("gender")
        address = post_data.get("address")
        role = post_data.get("role")
        hashed_pwd = self.db.hash_password(password)
        
        if email:
            user = self.db.fetch_query("SELECT * FROM users WHERE email = ?;", (post_data["email"],))
            if user:
                send_response(
                    handler,
                    {
                        "error": "Email already exists"
                    }, status=400
                )
                return
        try:
            self.db.execute_query(
                """
                    INSERT INTO users (
                        first_name, last_name, email,
                        password, phone, dob,
                        gender, address, role) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, 
                (
                    first_name, last_name, email,
                    hashed_pwd, phone, dob,
                    gender, address, role
                )
            )
        except Exception as e:
            send_response(
                handler,
                {
                    "error": str(e)
                }, status=400
            )
            return
        finally:
            self.db.close()
        
        send_response(
            handler,
            {
                "message": "User registered successfully!"
            }, status=201
        )
        return

    def login_user(self, handler):
        content_length = int(handler.headers['Content-Length'])
        print(content_length,'content_length')

        if content_length == 0:
            send_response(
                handler,
                {
                    "error": "No data provided"
                }, status=400
            )
            return
        
        post_data = json.loads(handler.rfile.read(content_length))
        is_valid, message = Validator.validate_login(post_data)
        print(is_valid, message,'is_valid, message')

        if not is_valid:
            send_response(
                handler,
                {
                    "error": message
                }, status=400
            )
            return
        
        email = post_data.get("email")
        password = post_data.get("password")
        hashed_pwd = self.db.hash_password(password)

        user = self.db.fetch_query(
            """
                SELECT id, first_name, role FROM users WHERE email=? AND password=?;
            """,
            (email, hashed_pwd)
        )
        if user:
            user_id, first_name, role = user[0]
            token = generate_jwt(user_id, role)
            send_response(
                handler,
                {
                    "message": "User logged in successfully!",
                    "user": {
                        "id": user_id,
                        "first_name": first_name,
                        "role": role,
                    },
                    "token": token
                    
                }, 
            )
        else:
            send_response(
                handler,
                {
                    "error": "Invalid email or password"
                }, status=401
            )