from find_artist import get_id
from find_artist import get_top_10
import discord
from typing import Optional
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
import json
import time
import os
import requests
import random

# 設置 Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents)

#確認機器人是否上線
@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print('目前登入身分', bot.user)
    print(f"載入 {len(slash)} 個斜線指令")

# 載入 cookie & token
with open("secret.json") as f:
    data = json.load(f)

# 設置請求 Headers (偽裝成瀏覽器避免被拒絕)
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "cookie": data["PIXIV_COOKIE"],
    "Referer": "https://www.pixiv.net/"
}

# 斜線指令
@bot.tree.command(name="pixiv", description="從指定繪師獲取 Pixiv 圖片")
@app_commands.describe(choice="選擇", artist="繪師名字", time="生成照片張數")
@app_commands.choices(
    choice=[
        Choice(name = "artist", value = 0), #指定作者
        Choice(name = "Top 10 of this month", value = 1), #本月前十
    ]
)
async def pixiv(interaction: discord.Interaction, choice: Choice[int], artist: Optional[str] = "", time: Optional[int] = None):
    await interaction.response.defer()  # 先回應避免超時
    ID = await get_id(interaction, artist)
    await execute(interaction, action = choice.value, artist_name = artist, artist_id = ID, times=time) #artist_name: 繪師名字, times: 張數


async def execute(interaction: discord.Interaction, artist_name: str, action: str, artist_id: str = None, times: int = 0):
    if action == 0:
        # 請求 Pixiv API 以獲取繪師的所有作品 ID
        response = requests.get(f'https://www.pixiv.net/ajax/user/{artist_id}/profile/all', headers=headers).text
        res = json.loads(response)
        
        if "body" not in res or "illusts" not in res["body"]:
            await interaction.followup.send("找不到該繪師的作品！")
            return

        all_illusts = list(res["body"]["illusts"].keys())
        if not all_illusts:
            await interaction.followup.send("該繪師沒有可用的圖片！")
            return
        
        await interaction.followup.send(f'繪師{artist_name}總共有 `{len(all_illusts)}` 張作品')
        for i in range(times):
            random_id = random.choice(all_illusts)
            await get_pic(interaction, random_id, artist_id = artist_id, artist_name = artist_name, action = 0)
    elif action == 1:
        global dic
        dic = await get_top_10()
        for i in range(10):
            rank = i+1
            illust_id = dic[i]["illust_id"]
            artist_name = dic[i]["artist"]
            await get_pic(interaction, illust_id, 1, action = 1, rank = rank)


async def get_pic(interaction: discord.Interaction, ID, artist_id: int = None, artist_name:str = None, action: int = None, rank: int = None):
    link = requests.get(f"https://www.pixiv.net/ajax/illust/{ID}", headers=headers).text
    web_json = json.loads(link)

    # 獲取原始圖片 URL
    img_url = web_json["body"]["urls"]["regular"] #用以壓縮過的檔案
    
    # 修正 Referer 以防止 403
    img_headers = headers.copy()
    img_headers["Referer"] = f"https://www.pixiv.net/artworks/{ID}"

    # 下載圖片
    img_data = requests.get(img_url, headers=img_headers).content

    # 確保 images 資料夾存在
    if not os.path.exists("images"):
        os.mkdir("images")

    file_path = "images/1.jpg"
    with open(file_path, "wb") as file:
        file.write(img_data)

    file = discord.File(file_path, filename="1.jpg")
    # 檢查 Discord 檔案上限 (8MB)
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    if file_size > 8.00:
        await interaction.followup.send(f" 作品 `{ID}` 太大無法傳送！")
        os.remove(file_path)
    
    # 傳送圖片
    if action == 0:
        embed=discord.Embed(title=f"作品: {web_json["body"]["title"]}")
        embed.set_author(name=f"作者: {artist_name}", url=f"https://www.pixiv.net/users/{artist_id}")
        embed.add_field(name="🎨 作品連結: ", value = f"https://www.pixiv.net/artworks/{ID}", inline=True)
        embed.set_image(url=f"attachment://1.jpg")  # 這裡要用固定的 `1.jpg`
        await interaction.followup.send(file = file, embed = embed)
    elif action == 1:
        embed = discord.Embed(title = f"作者: {dic[rank-1]["artist"]}", description = f"作品: {dic[rank-1]["title"]}")
        embed.set_author(name=f"第{rank}名")
        embed.add_field(name="🎨 作品連結: ", value = f"https://www.pixiv.net/artworks/{ID}", inline=True)
        embed.set_image(url=f"attachment://1.jpg")
        await interaction.followup.send(file = file, embed = embed)

        # 刪除暫存圖片
        os.remove(file_path)
        time.sleep(2)

# 啟動 bot
bot.run(data["DISCORD_TOKEN"])