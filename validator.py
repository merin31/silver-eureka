import re
from datetime import datetime


class Validator:

    @staticmethod
    def is_valid_email(email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone):
        return phone.isdigit() and 10 <= len(phone) <= 15

    @staticmethod
    def is_valid_date(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_user(data):
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "phone",
            "dob",
            "gender",
            "address",
            "role",
        ]

        for field in required_fields:
            if not data.get(field):
                return False, f"Missing required field: {field}"

        if not Validator.is_valid_email(data["email"]):
            return False, "Invalid email format"

        if not Validator.is_valid_phone(data["phone"]):
            return False, "Invalid phone number"

        if not Validator.is_valid_date(data["dob"]):
            return False, "Invalid date format (expected YYYY-MM-DD)"

        if data["gender"] not in ["male", "female", "other"]:
            return False, "Invalid gender value"

        if data["role"] not in ["super_admin", "artist_manager", "artist"]:
            return False, "Invalid role value"

        return True, "Valid"

    @staticmethod
    def validate_login(data):
        required_fields = ["email", "password"]

        for field in required_fields:
            if not data.get(field):
                return False, f"Missing required field: {field}"

        if not Validator.is_valid_email(data["email"]):
            return False, "Invalid email format"

        return True, "Valid"

    @staticmethod
    def validate_artist(data):
        required_fields = [
            "name",
            "dob",
            "gender",
            "address",
            "first_released_year",
            "no_of_album_released",
        ]
        for field in required_fields:
            if not data.get(field):
                return False, f"Missing required field: {field}"
        if not Validator.is_valid_date(data["dob"]):
            return False, "Invalid date format (expected YYYY-MM-DD)"
        return True, "Valid"

    @staticmethod
    def validate_music(data):
        required_fields = ["artist_id", "title", "album_name", "genre"]
        for field in required_fields:
            if not data.get(field):
                return False, f"Missing required field: {field}"
        if data["genre"] not in ["rnb", "country", "classic", "rock", "jazz"]:
            return False, "Invalid genre value"
        return True, "Valid"
