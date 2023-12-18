import os
import discord
import requests
from osu import Osu
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")
OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")

intents = discord.Intents.default() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


# sync the slash command to your server
@client.event
async def on_ready():
    await tree.sync()
    # await tree.sync(guild=discord.Object(id=931084376803000370))
    # print "ready" in the console when the bot is ready to work
    print("Bot is Ready.")


# make the slash command
@tree.command(name="calcpp", description="pp 계산기")
async def slash_command(interaction: discord.Interaction, star:float, accuracy:float, notes:int, _320:int):
    accuracy = accuracy/100
    maxpp = 8 * pow(max(star - 0.15, 0.05), 2.2) * (1 + 0.1 * min(1, notes / 1500))
    v2acc = accuracy * 0.9375 + 0.0625 * (_320 / notes)
    pp = round(maxpp * max(0, 5 * v2acc - 4), 2)

    await interaction.response.send_message(f"Star : **{star}**\nAccuracy : **{accuracy*100}%**\nTotal notes : **{notes}**\n320 counts : **{_320}**\nResult : **{pp}pp**")


@tree.command(name="chat", description="ChatGPT")
async def slash_command(interaction: discord.Interaction, text:str):
    await interaction.response.defer()

    msg = await interaction.followup.send("답변을 기다리는 중...")

    response = requests.post("https://api.openai.com/v1/chat/completions",
                             headers={"Authorization": f"Bearer {OPEN_AI_TOKEN}"},
                             json={"model": "gpt-3.5-turbo", "messages": [
                                 {"role": "system", "content": "2~3문장으로 대화를 짧게 해야 합니다."},
                                 {"role": "user", "content": text}
                                 ]})
    response = response.json()
    result = response["choices"][0]["message"]["content"]
    
    await msg.edit(content=result)


@tree.command(name="osuinfo", description="osu! 유저 정보 조회")
async def osu_info(interaction: discord.Interaction, username:str):

    osu = Osu(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
    user_info = osu.get_user_info(username)
    
    avatar_url = user_info["avatar_url"]
    global_rank = user_info["statistics"]["global_rank"]
    country_rank = user_info["statistics"]["country_rank"]
    play_count = user_info["statistics"]["play_count"]
    pp = user_info["statistics"]["pp"]
    highest_rank = user_info["rank_highest"]["rank"]
    accuracy = user_info["statistics"]["hit_accuracy"]

    embed = discord.Embed(title=username, color=discord.colour.Color.pink())
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="세계순위", value=f"{global_rank:,}", inline=True)
    embed.add_field(name="국가순위", value=f"{country_rank:,}", inline=True)
    embed.add_field(name="최고순위", value=f"{highest_rank:,}", inline=True)
    embed.add_field(name="PP", value=f"{pp:,}", inline=True)
    embed.add_field(name="정확도", value=f"{round(accuracy,2)}%", inline=True)
    embed.add_field(name="플레이", value=f"{play_count:,}", inline=True)

    await interaction.response.send_message(embed=embed)



# run the bot
client.run(DISCORD_TOKEN)