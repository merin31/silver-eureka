import json
import re
from urllib.parse import parse_qs
from jwt_middleware import verify_jwt, check_permissions
from database import DatabaseManager
from validator import Validator
from paginator import Paginator
from utils import send_response


class ArtistService:

    def __init__(self):
        self.db = DatabaseManager()

    def list_artists(self, handler, decoded_token):
        query_params = parse_qs(handler.path.split('?')[1] if '?' in handler.path else '')
        page = int(query_params.get('page', [1])[0])
        limit = int(query_params.get('limit', [10])[0])
        offset = (page - 1) * limit

        total_records = self.db.fetch_query("SELECT COUNT(*) FROM artists;")[0][0]

        base_url = "/artists"
        paginator = Paginator(base_url=base_url, page=page, limit=limit, total_records=total_records)

        artists = self.db.fetch_query("""
            SELECT id, name, dob, gender, address, first_released_year, no_of_album_released, created_at, updated_at
            FROM artists
            ORDER BY id
            LIMIT ? OFFSET ?;
        """, (limit, offset))

        artist_list = []
        for artist in artists:
            artist_list.append({
                "id": artist[0],
                "name": artist[1],
                "dob": artist[2],
                "gender": artist[3],
                "address": artist[4],
                "first_released_year": artist[5],
                "no_of_album_released": artist[6],
                "created_at": artist[7],
                "updated_at": artist[8]
            })

        pagination_meta = paginator.get_pagination_meta()
        pagination_meta["data"] = artist_list
        

        send_response(handler, pagination_meta)


    def create_artist(self, handler, decoded_token):
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))

        is_valid, message = Validator.validate_artist(post_data)
        if not is_valid:
            send_response(handler, {"error": message}, status=400)
            return

        self.db.execute_query("""
            INSERT INTO artists (name, dob, gender, address, first_released_year, no_of_album_released, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """, (
            post_data["name"],
            post_data["dob"],
            post_data["gender"],
            post_data["address"],
            post_data["first_released_year"],
            post_data["no_of_album_released"]
        ))

        send_response(handler, {"message": "Artist created successfully"}, status=201)

    def update_artist(self, handler, decoded_token, artist_id):
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))


        fields = []
        values = []

        for field in ["name", "dob", "gender", "address", "first_released_year", "no_of_album_released"]:
            if field in post_data:
                fields.append(f"{field} = ?")
                values.append(post_data[field])

        if not fields:
            send_response(handler, {"error": "Empty body"}, status=400)
            return

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(artist_id)

        query = f"""
            UPDATE artists
            SET {', '.join(fields)}
            WHERE id = ?;
        """

        print(query, values)

        self.db.execute_query(query, values)

        send_response(handler, {"message": f"Artist {artist_id} updated successfully"})

    def delete_artist(self, handler, decoded_token, artist_id):
        artist = self.db.fetch_query("SELECT * FROM artists WHERE id = ?;", (artist_id,))
        if not artist:
            send_response(handler, {"error": "Artist not found"}, status=404)
            return
        self.db.execute_query("DELETE FROM artists WHERE id = ?;", (artist_id,))
        send_response(handler, {"message": f"Artist {artist_id} deleted successfully"})

    def handle_request(self, handler, method):
        decoded_token = verify_jwt(handler)
        if not decoded_token:
            return

        if not check_permissions(handler, decoded_token, "artists", method):
            return

        if method == "GET":
            self.list_artists(handler, decoded_token)
        elif method == "POST":
            self.create_artist(handler, decoded_token)
        elif method == "PUT":
            pattern = re.search(r'/artists/\d+', handler.path)
            artist_id = pattern.group().split('/')[-1]
            self.update_artist(handler, decoded_token, artist_id)
        elif method == "DELETE":
            pattern = re.search(r'/artists/\d+', handler.path)
            artist_id = pattern.group().split('/')[-1]
            self.delete_artist(handler, decoded_token, artist_id)
        else:
            send_response(handler, {"error": "Method not allowed"}, status=405)