import requests

class Osu:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self):
        response = requests.post("https://osu.ppy.sh/oauth/token",
                                headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Accept": "application/json"},
                                data={"grant_type": "client_credentials",
                                        "client_id": self.client_id,
                                        "client_secret": self.client_secret,
                                        "scope": "public"})
        response = response.json()
        return response["access_token"]
    
    def get_user_info(self, username:str):
        response = requests.get(f"https://osu.ppy.sh/api/v2/users/{username}",
                                headers={"Authorization": f"Bearer {self.bearer_token}",
                                         "Accept": "application/json",
                                         "Content-Type": "application/json"})
        response = response.json()
        return response