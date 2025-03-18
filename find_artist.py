from pixivpy3 import AppPixivAPI
import discord

# 用 refresh_token 認證
REFRESH_TOKEN = "KP3T1f26AKGfeCXvzVRodcURy5MCzIfX92E1jMPiNq4"
api = AppPixivAPI()
api.auth(refresh_token=REFRESH_TOKEN)

async def get_id(interaction: discord.Interaction, artist):
    user_result = api.search_user(artist)
    if not user_result.user_previews or not user_result.user_previews[0].illusts:
        await interaction.followup.send("找不到該使用者的作品或該使用者")
        return
    user_id = user_result.user_previews[0].user.id
    return user_id


async def get_top_10():
    ranking = api.illust_ranking(mode = "month")
    # save top 10 information
    top_10 = []
    for i, illust in enumerate(ranking.illusts[:10]): 
        info = {
            "rank": i + 1,                 # ranking
            "title": illust.title,         # title
            "illust_id": illust.id,        # illust id
            "artist": illust.user.name,    # artist name
            "artist_id": illust.user.id,   # artist ID
        }
        top_10.append(info)
    return top_10
