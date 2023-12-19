import os
import json
import requests
from datetime import datetime


class Osu:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self) -> str:
        if os.path.isfile("osu_token.json"):
            with open("osu_token.json", "r") as f:
                token = json.load(f)
            if datetime.fromtimestamp(token["expires_at"]) < datetime.now():
                token = self._generate_bearer_token()
                with open("osu_token.json", "w") as f:
                    json.dump({"token": token, "expires_at": datetime.now().timestamp() + 86400}, f)
            else:
                token = token["token"]
        else:
            token = self._generate_bearer_token()
            with open("osu_token.json", "w") as f:
                json.dump({"token": token, "expires_at": datetime.now().timestamp() + 86400}, f)
        return token

    def _generate_bearer_token(self) -> str:
        response = requests.post("https://osu.ppy.sh/oauth/token",
                                headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Accept": "application/json"},
                                data={"grant_type": "client_credentials",
                                        "client_id": self.client_id,
                                        "client_secret": self.client_secret,
                                        "scope": "public"})
        response = response.json()
        return response["access_token"]
    
    def get_user_info(self, username:str) -> dict:
        response = requests.get(f"https://osu.ppy.sh/api/v2/users/{username}/mania",
                                headers={"Authorization": f"Bearer {self.bearer_token}",    
                                         "Accept": "application/json",
                                         "Content-Type": "application/json"})
        response = response.json()
        return response

    def get_user_best(self, username:str, limit=5, offset=0) -> list:
        with open("osu_user_table.json", "r") as f:
            user_table = json.load(f)
        if username not in user_table:
            userid = self.get_user_info(username)["id"]
            user_table[username] = userid
            with open("osu_user_table.json", "w") as f:
                json.dump(user_table, f)
        else:
            userid = user_table[username]

        response = requests.get(f"https://osu.ppy.sh/api/v2/users/{userid}/scores/best",
                                headers={"Authorization": f"Bearer {self.bearer_token}",    
                                         "Accept": "application/json",
                                         "Content-Type": "application/json"},
                                params={"mode": "mania",
                                        "limit": limit,
                                        "offset": offset})
        response = response.json()
        return response
    
    def generate_user_best(self, username:str, limit, offset) -> str:
        user_info = self.get_user_best(username, limit, offset)
    
        res = []
        for data in user_info:
            title = data["beatmapset"]["title"]
            artist = data["beatmapset"]["artist"]
            version = data["beatmap"]["version"]
            diff = data["beatmap"]["difficulty_rating"]
            accuracy = round(data["accuracy"] * 100, 2)
            rank = data["rank"]
            pp = int(data["pp"])
            rank_pp = int(data["weight"]["pp"])
            date = data["created_at"].split("T")[0]
            mods = data["mods"]

            res.append(f"""🎵 {title} - {artist}
{version} - {diff}★ ({accuracy}% {rank}) ({pp}P / {rank_pp}P)
날짜 : {date}""" + (f" ({', '.join(mods)})" if mods else ""))
        
        return "```" + "\n\n".join(res) + "```"