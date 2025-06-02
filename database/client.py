import json
from pymongo import MongoClient
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import random
from bson import ObjectId


class YouTubeDB:
    def __init__(self, mongo_uri, db_name="youtube_maze"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.secret_collection = self.db["client_secrets"]
        self.channel_collection = self.db["channels"]
        self.SCOPES = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.upload",
        ]

    def add_client_secret(self, secret_json_path):
        """Add new client secret to DB with channel count = 0"""
        with open(secret_json_path, "r") as f:
            client_secret_data = json.load(f)

        result = self.secret_collection.insert_one(
            {"secret": client_secret_data, "channel_count": 0}
        )

        print(f"✅ Client secret added with ID: {result.inserted_id}")

    def add_channel(self, video_duration=None, levels=None, solution_position=None, test=False):
        """Authorize a new channel using the least-used client secret"""
        # Find a client secret with channel count < 30 and not equal to 30
        client_doc = self.secret_collection.find_one({"channel_count": {"$lt": 31}})
        if not client_doc:
            raise Exception("❌ No available client secrets with less than 6 channels")

        client_secret = client_doc["secret"]

        # Run OAuth2 installed app flow
        flow = InstalledAppFlow.from_client_config(client_secret, self.SCOPES)
        creds = flow.run_local_server()

        # Get channel ID
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", credentials=creds)
        response = youtube.channels().list(part="id,snippet", mine=True).execute()

        if not response["items"]:
            raise Exception("❌ Unable to retrieve channel info")

        channel_data = response["items"][0]
        channel_id = channel_data["id"]

        # Check if channel already exists
        if self.channel_collection.find_one({"channel_id": channel_id}):
            raise Exception(f"❌ Channel with ID {channel_id} already exists")

        # video_duration = input("Enter the video duration in seconds: ")
        try:
            video_duration = int(video_duration)
        except ValueError:
            raise Exception("❌ Invalid video duration. Please enter a valid integer.")

        # levels = input(
        #     "Enter the levels for this channel (B, M, H) separated by commas: "
        # )
        # levels = "B, M, H"  # Default levels for testing
        # levels = [
        #     level.strip().upper()
        #     for level in levels.split(",")
        #     if level.strip().upper() in ["B", "M", "H"]
        # ]
        if levels is None:
            levels = ["H"]*(video_duration//30)
        # levels = list(set(levels))  # Remove duplicates
        # sort in the order of B, M, H
        levels.sort(key=lambda x: ["B", "M", "H"].index(x))
        if not levels:
            raise Exception("❌ No valid levels provided. Please enter B, M, or H.")

        # solution_position = input(
        #     "Enter the solution position (0 for mid, 1 for last and -1 for no solution): "
        # )
        if solution_position is None:
            solution_position = -1
        try:
            solution_position = int(solution_position)
        except ValueError:
            raise Exception("❌ Invalid solution position. Please enter -1, 0, or 1.")
        if solution_position not in [-1, 0, 1]:
            raise Exception("❌ Invalid solution position. Please enter -1, 0, or 1.")

        if solution_position != -1:
            # solution_duration = input("Enter the solution duration in seconds: ")
            # solution_duration = 3
            try:
                match video_duration:
                    case 60:
                        solution_duration = 2
                    case 90:
                        solution_duration = 4
                    case 120:
                        solution_duration = 6
                    case 150:
                        solution_duration = 8
                    case 180:
                        solution_duration = 10
                # solution_duration = int(solution_duration)
            except ValueError:
                raise Exception(
                    "❌ Invalid solution duration. Please enter a valid integer."
                )
        else:
            solution_duration = 0

        # get all font schemes from the database
        font_schemes = self.db["font_schemes"].find({})
        if not font_schemes:
            raise Exception(
                "❌ No font schemes found in the database. Please add some first."
            )

        font_scheme = ObjectId(random.choice(list(font_schemes))["_id"])

        # color_scheme = input("Enter the colour scheme (dark, light): ").strip().lower()
        color_scheme = "dark"
        # color_scheme = "light"
        if color_scheme not in ["dark", "light"]:
            raise Exception(
                "❌ Invalid colour scheme. Please enter 'default', 'dark', or 'light'."
            )

        # get all color schemes from the database
        color_schemes = self.db["color_schemes"].find({"type": color_scheme})
        if not color_schemes:
            raise Exception(
                "❌ No color schemes found in the database. Please add some first."
            )

        color_scheme = ObjectId(random.choice(list(color_schemes))["_id"])

        # Save credentials and channel info to DB
        self.channel_collection.insert_one(
            {
                "channel_id": channel_id,
                "channel_title": channel_data["snippet"]["title"],
                "levels": levels,
                "video_duration": video_duration,
                "solution_position": solution_position,
                "solution_duration": solution_duration,
                "color_scheme": color_scheme,
                "font_scheme": font_scheme,
                "test": test,
                "credentials": json.loads(creds.to_json()),
                "client_id": ObjectId(client_doc["_id"]),
            }
        )

        # Increment the channel count
        self.secret_collection.update_one(
            {"_id": client_doc["_id"]}, {"$inc": {"channel_count": 1}}
        )

        print(
            f"✅ Channel {channel_data['snippet']['title']} added with ID {channel_id}"
        )

    def get_channel_data(self, channel_id):
        """Return the stored credentials for a given channel_id"""
        channel_doc = self.channel_collection.find_one(
            {"channel_id": channel_id},
            {"_id": 0},
        )
        if not channel_doc:
            raise Exception("❌ Channel ID not found")

        creds_data = channel_doc["credentials"]
        font_scheme = channel_doc.get("font_scheme")
        color_scheme = channel_doc.get("color_scheme")
        font_scheme = (
            self.db["font_schemes"].find_one({"_id": font_scheme}, {"_id": 0})
            if font_scheme
            else None
        )
        color_scheme = (
            self.db["color_schemes"].find_one(
                {"_id": color_scheme}, {"_id": 0, "type": 0}
            )
            if color_scheme
            else None
        )
        color_scheme = {
            k: {sk: tuple(sv) for sk, sv in v.items()} for k, v in color_scheme.items()
        }

        levels = channel_doc["levels"]
        total_duration = channel_doc["video_duration"]
        solution_duration = channel_doc["solution_duration"]
        solution_position = channel_doc["solution_position"]

        creds = Credentials.from_authorized_user_info(creds_data, self.SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update the credentials in the database
                self.channel_collection.update_one(
                    {"channel_id": channel_id},
                    {"$set": {"credentials": json.loads(creds.to_json())}},
                )
            else:
                raise Exception(
                    "Invalid or expired credentials. Please re-authenticate."
                )
        return (
            creds,
            font_scheme,
            color_scheme,
            levels,
            total_duration,
            solution_duration,
            solution_position,
        )

    def get_all_channels(self, test=False):
        """Return all channels in the database"""
        return list(self.channel_collection.find({"test": test}, {"_id": 0, "channel_id": 1}))

    def add_color_scheme(self, color_scheme, many=False):
        """Add a new color scheme to the database"""
        if many:
            if not isinstance(color_scheme, list):
                raise ValueError("Color scheme must be a list of dictionaries")
            for cs in color_scheme:
                if not isinstance(cs, dict):
                    raise ValueError("Each color scheme must be a dictionary")
                if "type" not in cs or "maze" not in cs or "video" not in cs:
                    raise ValueError(
                        "Color scheme must contain 'type', 'maze', and 'video' keys"
                    )
            result = self.db["color_schemes"].insert_many(color_scheme)
            # print(f"✅ Color schemes added with IDs: {result.inserted_ids}")
            return
        if not isinstance(color_scheme, dict):
            raise ValueError("Color scheme must be a dictionary")
        if (
            "type" not in color_scheme
            or "maze" not in color_scheme
            or "video" not in color_scheme
        ):
            raise ValueError(
                "Color scheme must contain 'type', 'maze', and 'video' keys"
            )

        result = self.db["color_schemes"].insert_one(color_scheme)
        print(f"✅ Color scheme added with ID: {result.inserted_id}")

    def add_font_scheme(self, font_scheme, many=False):
        """Add a new font scheme to the database"""
        if many:
            if not isinstance(font_scheme, list):
                raise ValueError("Font scheme must be a list of dictionaries")
            for fs in font_scheme:
                if not isinstance(fs, dict):
                    raise ValueError("Each font scheme must be a dictionary")
                if (
                    "text_font" not in fs
                    or "timer_font" not in fs
                    or "cta_font" not in fs
                ):
                    raise ValueError(
                        "Font scheme must contain 'text_font', 'timer_font', and 'cta_font' keys"
                    )
            result = self.db["font_schemes"].insert_many(font_scheme)
            # print(f"✅ Font schemes added with IDs: {result.inserted_ids}")
            return
        if not isinstance(font_scheme, dict):
            raise ValueError("Font scheme must be a dictionary")
        if (
            "text_font" not in font_scheme
            or "timer_font" not in font_scheme
            or "cta_font" not in font_scheme
        ):
            raise ValueError(
                "Font scheme must contain 'text_font', 'timer_font', and 'cta_font' keys"
            )

        result = self.db["font_schemes"].insert_one(font_scheme)
        print(f"✅ Font scheme added with ID: {result.inserted_id}")


if __name__ == "__main__":
    import os
    mongo_uri = os.environ.get("MONGO_URI")
    db = YouTubeDB(mongo_uri)

    # db.channel_collection.update_many({}, {"$set": {"test": False}})

    # Add a new client secret
    # db.add_client_secret(r"client_secret.json")

    # Add a new channel
    # for i in [-1]:
    #     for j in [24, 30, 36, 42, 48]:
    #         db.add_channel(video_duration=j, solution_position=i, levels=["B", "M", "H"])
    #         time.sleep(2)

    # db.add_channel(
    #     video_duration=60, solution_position=0, levels=["B", "M", "H"], test=True
    # )

    # Get credentials for a specific channel
    # creds = db.get_credentials('CHANNEL_ID_HERE')
    # print(creds)

    # Get all channels
    # channels = db.get_all_channels()
    # for channel in channels:
    #     print(f"Channel ID: {channel['channel_id']}, Title: {channel['channel_title']}, Levels: {', '.join(channel['levels'])}")

    # Add a new color scheme
    # db.add_color_scheme(color_schemes, many=True)
    # Add a new font scheme
    # db.add_font_scheme(font_schemes, many=True)
