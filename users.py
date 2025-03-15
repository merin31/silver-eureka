import json
import re
from urllib.parse import urlparse, parse_qs
from database import DatabaseManager
from utils import send_response, generate_jwt
from validator import Validator
from jwt_middleware import verify_jwt, check_permissions
from paginator import Paginator


class UserService:
    def __init__(self):
        self.db = DatabaseManager()

    def list_users(self, handler, decoded_token):
        
        query_params = parse_qs(handler.path.split('?')[1] if '?' in handler.path else '')
        page = int(query_params.get('page', [1])[0])
        limit = int(query_params.get('limit', [10])[0])
        offset = (page - 1) * limit

        total_records = self.db.fetch_query("SELECT COUNT(*) FROM users;")[0][0]

        paginator = Paginator(base_url=urlparse(handler.path).path, page=page, limit=limit, total_records=total_records)

        users = self.db.fetch_query("""
            SELECT id, first_name, last_name, email, phone, role, created_at, updated_at
            FROM users
            ORDER BY id
            LIMIT ? OFFSET ?;
        """, (limit, offset))
        self.db.close()
        user_list = []
        
        for user in users:
            user_list.append({
                "id": user[0],
                "first_name": user[1],
                "last_name": user[2],
                "email": user[3],
                "phone": user[4],
                "role": user[5],
                "created_at": user[6],
                "updated_at": user[7],
            })
        pagination_meta = paginator.get_pagination_meta()
        pagination_meta["data"] = user_list
        
        send_response(handler, paginated_data)


    def create_user(self, handler, decoded_token):
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))

        is_valid, message = Validator.validate_user(post_data)
        if not is_valid:
            send_response(handler, {"error": message}, status=400)
            return

        hashed_pwd = self.db.hash_password(post_data["password"])
        email = post_data.get("email")
        user = self.db.fetch_query("SELECT * FROM users WHERE email = ?;", (email,))

        if user:
            send_response(
                handler,
                {
                    "error": "Email already exists"
                }, status=400
            )
            return

        try:
            self.db.execute_query("""
                INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                post_data["first_name"], post_data["last_name"], post_data["email"],
                hashed_pwd, post_data["phone"], post_data["dob"], post_data["gender"],
                post_data["address"], post_data["role"]
            ))
        except Exception as e:
            send_response(handler, {"error": str(e)}, status=400)
            return
        finally:
            print('in final')
            self.db.close()

        send_response(handler, {"message": "User created successfully"}, status=201)

    def update_user(self, handler, decoded_token, user_id):
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))

        if "role" in post_data and post_data["role"] not in ["super_admin", "artist_manager", "artist"]:
            send_response(handler, {"error": "Invalid role"}, status=400)
            return

        fields = []
        values = []

        for field in ["first_name", "last_name", "email", "phone", "dob", "gender", "address", "role"]:
            if field in post_data:
                fields.append(f"{field} = ?")
                values.append(post_data[field])
        print(fields,'fields')

        if "password" in post_data:
            fields.append("password = ?")
            values.append(self.db.hash_password(post_data["password"]))

        if "email" in post_data:
            user = self.db.fetch_query("SELECT * FROM users WHERE email = ?;", (post_data["email"],))
            if user and user[0][0] != int(user_id):
                send_response(handler, {"error": "Email already exists"}, status=400)
                return

        if not fields:
            send_response(handler, {"error": "No fields to update"}, status=400)
            return

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(fields)}
            WHERE id = ?;
        """

        self.db.execute_query(query, values)
        self.db.close()

        send_response(handler, {"message": f"User {user_id} updated successfully"})

    def delete_user(self, handler, decoded_token, user_id):
        print(decoded_token,'decoded_token')
        print(user_id,'user')
        user = self.db.fetch_query("SELECT * FROM users WHERE id = ? AND role != 'super_admin';", (user_id,))
        print(user,'user')
        if not user:
            send_response(handler, {"error": "User not found"}, status=404)
            return
        self.db.execute_query("DELETE FROM users WHERE id = ?;", (user_id,))
        self.db.close()
        send_response(handler, {"message": f"User {user_id} deleted successfully"})
    



    def handle_request(self, handler, method):
        decoded_token = verify_jwt(handler)
        if not decoded_token:
            return

        if not check_permissions(handler, decoded_token, "users", method):
            return

        if method == "GET":
            self.list_users(handler, decoded_token)
        elif method == "POST":
            self.create_user(handler, decoded_token)
        elif method == "PUT":
            pattern = re.search(r'/users/\d+', handler.path)
            user_id = pattern.group().split('/')[-1]
            self.update_user(handler, decoded_token, user_id)
        elif method == "DELETE":
            pattern = re.search(r'/users/\d+', handler.path)
            user_id = pattern.group().split('/')[-1]
            # user_id = handler.path.split('/')[-1]
            print(user_id,'user i')
            self.delete_user(handler, decoded_token, user_id)
        else:
            send_response(handler, {"error": "Method not allowed"}, status=405)


