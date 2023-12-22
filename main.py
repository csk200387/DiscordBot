import os
import discord
import requests
from src.osu import Osu
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")
OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")

if not DISCORD_TOKEN:
    raise Exception("디스코드 토큰이 없습니다.")
if not OPEN_AI_TOKEN:
    raise Exception("오픈AI 토큰이 없습니다.")
if not OSU_CLIENT_ID:
    raise Exception("OSU 클라이언트 ID가 없습니다.")
if not OSU_CLIENT_SECRET:
    raise Exception("OSU 클라이언트 시크릿이 없습니다.")

OSU_BEST_PAGENUM = 1


intents = discord.Intents.default() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


# sync the slash command to your server
@client.event
async def on_ready():
    # await client.change_presence(status=discord.Status.online, activity=discord.Game(name="/ 로 봇을 사용하세요"))
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="/ 로 봇을 사용하세요"))
    await tree.sync()
    print("Bot is Ready.")



# make the slash command
@tree.command(name="calcpp", description="osu! PP 계산기")
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
    username = username.strip()
    
    osu = Osu(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
    user_info = osu.get_user_info(username)
    
    user_id = user_info["id"]
    avatar_url = user_info["avatar_url"]
    global_rank = user_info["statistics"]["global_rank"] if user_info["statistics"]["global_rank"] else 0
    country_rank = user_info["statistics"]["country_rank"] if user_info["statistics"]["country_rank"] else 0
    play_count = user_info["statistics"]["play_count"]
    pp = user_info["statistics"]["pp"]
    highest_rank = user_info["rank_highest"]["rank"]
    accuracy = user_info["statistics"]["hit_accuracy"]

    embed = discord.Embed(title=username, url=f"https://osu.ppy.sh/users/{user_id}", color=discord.colour.Color.from_rgb(255, 121, 184))
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="세계순위", value=f"{global_rank:,}", inline=True)
    embed.add_field(name="국가순위", value=f"{country_rank:,}", inline=True)
    embed.add_field(name="최고순위", value=f"{highest_rank:,}", inline=True)
    embed.add_field(name="PP", value=f"{pp:,}", inline=True)
    embed.add_field(name="정확도", value=f"{round(accuracy,2)}%", inline=True)
    embed.add_field(name="플레이", value=f"{play_count:,}", inline=True)

    await interaction.response.send_message(embed=embed)



@tree.command(name="osubest", description="osu! 최고 성과 조회")
async def button_test(interaction:discord.Interaction, username:str):
    osu = Osu(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
    global OSU_BEST_PAGENUM
    OSU_BEST_PAGENUM = 1

    prev = discord.ui.Button(label="<", style=discord.ButtonStyle.secondary)
    next = discord.ui.Button(label=">", style=discord.ButtonStyle.secondary)

    view = discord.ui.View()
    view.add_item(prev)
    view.add_item(next)

    async def next_page(interaction:discord.Interaction):
        global OSU_BEST_PAGENUM
        if OSU_BEST_PAGENUM >= 8:
            return
        OSU_BEST_PAGENUM += 1
        message = osu.generate_user_best(username, 5, 5*(OSU_BEST_PAGENUM-1))
        await interaction.response.edit_message(content=f"```{message}\n{OSU_BEST_PAGENUM}/8 page```")
    
    async def prev_page(interaction:discord.Interaction):
        global OSU_BEST_PAGENUM
        if OSU_BEST_PAGENUM <= 1:
            return
        OSU_BEST_PAGENUM -= 1
        message = osu.generate_user_best(username, 5, 5*(OSU_BEST_PAGENUM-1))
        await interaction.response.edit_message(content=f"```{message}\n{OSU_BEST_PAGENUM}/8 page```")
    
    prev.callback = prev_page
    next.callback = next_page

    await interaction.response.send_message(f"```{osu.generate_user_best(username, 5, 0)}\n{OSU_BEST_PAGENUM}/8 page```", view=view)


@tree.command(name="changestatus", description="bot의 상태를 변경합니다.")
async def change_status(interaction:discord.Interaction):
    view = discord.ui.View()

    options = [
        discord.SelectOption(label="온라인", description="온라인 상태로 변경합니다. 초록색", value="온라인"),
        discord.SelectOption(label="자리 비움", description="자리비움 상태로 변경합니다. 노란색", value="자리비움"),
        discord.SelectOption(label="다른 용무 중", description="다른 용무 중 상태로 변경합니다.", value="다른 용무 중"),
        discord.SelectOption(label="오프라인", description="오프라인 상태로 변경합니다.", value="오프라인"),
    ]
    select = discord.ui.Select(placeholder="상태를 선택하세요", options=options)
    view.add_item(select)

    async def change(interaction:discord.Interaction):
        match interaction.data['values'][0]:
            case "온라인":
                await client.change_presence(status=discord.Status.online)
            case "자리비움":
                await client.change_presence(status=discord.Status.idle)
            case "다른 용무 중":
                await client.change_presence(status=discord.Status.dnd)
            case "오프라인":
                await client.change_presence(status=discord.Status.offline)
        
        await interaction.response.edit_message(content=f"상태가 {interaction.data['values'][0]}로 변경되었습니다.")
    
    select.callback = change
    await interaction.response.send_message("상태를 선택하세요", view=view)


# run the bot
client.run(DISCORD_TOKEN)