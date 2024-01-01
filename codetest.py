from src.osu import Osu
import os
from dotenv import load_dotenv
import json

load_dotenv()

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")

osu = Osu(OSU_CLIENT_ID, OSU_CLIENT_SECRET)

print(round(osu.calculate_pp("csk200387")))
# print(json.dumps(osu.get_user_recent("csk200387", limit=1), indent=4, ensure_ascii=False))