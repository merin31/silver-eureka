import json
import re
from urllib.parse import parse_qs
from jwt_middleware import verify_jwt, check_permissions
from database import DatabaseManager
from validator import Validator
from paginator import Paginator
from utils import send_response


class MusicService:
    def __init__(self):
        self.db = DatabaseManager()

    def list_music(self, handler, decoded_token):
        query_params = parse_qs(
            handler.path.split("?")[1] if "?" in handler.path else ""
        )
        artist_id = query_params.get("artist_id", [None])[0]
        print(query_params.get("artist_id",0))
        print(artist_id,'artist id')
        page = int(query_params.get("page", [1])[0])
        limit = int(query_params.get("limit", [10])[0])
        offset = (page - 1) * limit


        music_count_query = "SELECT COUNT(*) FROM music;"
        music_query = """
            SELECT id, artist_id, title, album_name, genre, created_at, updated_at
            FROM music
            ORDER BY id
            LIMIT ? OFFSET ?;
        """
        if artist_id:
            music_count_query = f"SELECT COUNT(*) FROM music WHERE artist_id = {artist_id};"
            print(music_count_query)
            music_query = """
                SELECT id, artist_id, title, album_name, genre, created_at, updated_at
                FROM music
                WHERE artist_id = ?
                ORDER BY id
                LIMIT ? OFFSET ?;
            """
        
        
        # if artist_id:
        #     music_count_query = """
        #         SELECT id, artist_id, title, album_name, genre, created_at, updated_at
        #         FROM music
        #         WHERE artist_id = ?
        #         ORDER BY id
        #         LIMIT ? OFFSET ?;
        #     """
            
        #     music_list = self.db.fetch_query(
        #         music_query, (artist_id, limit, offset)
        #     )
        #     if not music_list:
        #         send_response(handler, {"error": "No music found for the artist"}, status=404)
        #         return
        total_records = self.db.fetch_query(music_count_query)[0][0]

        base_url = "/music"
        paginator = Paginator(
            base_url=base_url, page=page, limit=limit, total_records=total_records
        )

        music_list = self.db.fetch_query(
            music_query, (limit, offset) if not artist_id else (artist_id, limit, offset)
        )

        music_records = []
        for music in music_list:
            music_records.append(
                {
                    "id": music[0],
                    "artist_id": music[1],
                    "title": music[2],
                    "album_name": music[3],
                    "genre": music[4],
                    "created_at": music[5],
                    "updated_at": music[6],
                }
            )
        pagination_meta = paginator.get_pagination_meta()
        pagination_meta["data"] = music_records

        send_response(handler, pagination_meta)

    def create_music(self, handler, decoded_token):
        content_length = int(handler.headers.get("Content-Length", 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))

        is_valid, message = Validator.validate_music(post_data)
        if not is_valid:
            send_response(handler, {"error": message}, status=400)
            return

        artist_id = post_data.get("artist_id")
        artist = self.db.fetch_query("SELECT * FROM artists WHERE id = ?;", (artist_id,))
        if not artist:
            send_response(handler, {"error": "Artist not found"}, status=404)
            return
        self.db.execute_query(
            """
            INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """,
            (
                post_data["artist_id"],
                post_data["title"],
                post_data["album_name"],
                post_data["genre"],
            ),
        )

        send_response(handler, {"message": "Music created successfully"}, status=201)

    def update_music(self, handler, decoded_token, music_id):
        content_length = int(handler.headers.get("Content-Length", 0))
        if content_length == 0:
            send_response(handler, {"error": "Empty request body"}, status=400)
            return

        post_data = json.loads(handler.rfile.read(content_length))

        if "genre" in post_data and post_data["genre"] not in [
            "rnb",
            "country",
            "classic",
            "rock",
            "jazz",
        ]:
            send_response(handler, {"error": "Invalid genre"}, status=400)
            return

        fields = []
        values = []

        music = self.db.fetch_query("SELECT * FROM music WHERE id = ?;", (music_id,))
        if not music:
            send_response(handler, {"error": "Music not found"}, status=404)
            return

        for field in ["artist_id", "title", "album_name", "genre"]:
            if field in post_data:
                fields.append(f"{field} = ?")
                values.append(post_data[field])

        if not fields:
            send_response(handler, {"error": "No fields to update"}, status=400)
            return

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(music_id)

        query = f"""
            UPDATE music
            SET {', '.join(fields)}
            WHERE id = ?;
        """
        print(query, values)

        self.db.execute_query(query, values)

        send_response(handler, {"message": f"Music {music_id} updated successfully"})

    def delete_music(self, handler, decoded_token, music_id):
        
        music = self.db.fetch_query("SELECT * FROM music WHERE id = ?;", (music_id,))
        if not music:
            send_response(handler, {"error": "Music not found"}, status=404)
            return
        self.db.execute_query("DELETE FROM music WHERE id = ?;", (music_id,))
        send_response(handler, {"message": f"Music {music_id} deleted successfully"})

    def handle_request(self, handler, method):
        decoded_token = verify_jwt(handler)
        if not decoded_token:
            return
        if not check_permissions(handler, decoded_token, "music", method):
            return

        if method == "GET":
            self.list_music(handler, decoded_token)
        elif method == "POST":
            self.create_music(handler, decoded_token)
        elif method == "PUT":
            pattern = re.search(r'/music/\d+', handler.path)
            music_id = pattern.group().split('/')[-1]
            self.update_music(handler, decoded_token, music_id)
        elif method == "DELETE":
            pattern = re.search(r'/music/\d+', handler.path)
            music_id = pattern.group().split('/')[-1]
            self.delete_music(handler, decoded_token, music_id)
        else:
            send_response(handler, {"error": "Method not allowed"}, status=405)
