from gppt import GetPixivToken

def get_refresh_token() -> str:
    with open("data.txt", "w+") as f:
        if refresh_token := f.read().strip():
            return refresh_token

        g = GetPixivToken(headless=True)
        refresh_token = g.login(username="no_anime-nolife", password="Mitsuha3131!")["refresh_token"]
        access_token = g.login(username="no_anime-nolife", password="Mitsuha3131!")["access_token"]
        print(f"access token : {access_token}")
        print(f"refresh token : {refresh_token}")
        print(f"access token : {access_token}", file=f)
        print(f"refresh token : {refresh_token}", file=f)
        return refresh_token

token = get_refresh_token()