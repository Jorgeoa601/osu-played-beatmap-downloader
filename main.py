import os
import re
import requests

USER_ID = "YOUR_USER_ID"           # Your numeric osu! User ID (from your profile URL)
CLIENT_ID = "YOUR_CLIENT_ID"       # OAuth Client ID from https://osu.ppy.sh/home/account/edit#oauth
CLIENT_SECRET = "YOUR_SECRET"      # OAuth Client Secret
DOWNLOAD_FOLDER = "./downloads"    # Path where .osz files will be saved
LIMIT = 2000                       # Max number of beatmaps to fetch
OFFSET = 0                         # Starting offset


def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def get_osu_token(client_id: str, client_secret: str) -> str:
    token_url = "https://osu.ppy.sh/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public",
    }
    response = requests.post(token_url, json=payload, timeout=15)
    if response.status_code == 200:
        return response.json().get("access_token")
    raise RuntimeError(
        f"Failed to authenticate with osu! API (Status {response.status_code}): {response.text}"
    )


def download_single_beatmap(beatmap_id: int, song_title: str) -> bool:
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    safe_title = sanitize_filename(song_title)
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{beatmap_id} - {safe_title}.osz")

    if os.path.exists(file_path):
        print(f"Skipping {beatmap_id} - {song_title} (already exists).")
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    mirrors = [
        f"https://catboy.best/d/{beatmap_id}",
        f"https://api.nerinyan.moe/d/{beatmap_id}",
    ]

    for url in mirrors:
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=60)
            if response.status_code == 200 and len(response.content) > 0:
                with open(file_path, "wb") as osz_file:
                    osz_file.write(response.content)
                return True
        except requests.RequestException as e:
            print(f"Mirror error ({url}): {e}")

    print(f"Failed to download {beatmap_id} - {song_title}")
    return False


def download_beatmaps(beatmaps: list[dict]):
    failed_downloads = []
    total = len(beatmaps)

    try:
        for index, item in enumerate(beatmaps, start=1):
            beatmapset = item.get("beatmapset", {})
            beatmapset_id = beatmapset.get("id") or item.get("beatmap", {}).get("beatmapset_id")
            song_title = beatmapset.get("title", f"beatmapset_{beatmapset_id}")

            print(f"[{index}/{total}] Downloading: {beatmapset_id} - {song_title}...")
            if not download_single_beatmap(beatmapset_id, song_title):
                failed_downloads.append(f"{beatmapset_id} - {song_title}\n")
    except Exception as e:
        print(f"Error downloading beatmaps: {e}")
    finally:
        if failed_downloads:
            with open("failed_downloads.txt", "a", encoding="utf-8") as failed_file:
                for failed in failed_downloads:
                    failed_file.write(failed)


def retrieve_most_played_beatmaps(user_id: str, limit: int, offs: int = 0):
    if not CLIENT_ID or CLIENT_ID == "YOUR_CLIENT_ID" or not CLIENT_SECRET or CLIENT_SECRET == "YOUR_SECRET":
        print("Error: Please set your USER_ID, CLIENT_ID, and CLIENT_SECRET in main.py before running.")
        return

    print("Authenticating with osu! API v2...")
    token = get_osu_token(CLIENT_ID, CLIENT_SECRET)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    offset = offs
    step = 50

    while offset < limit:
        url = f"https://osu.ppy.sh/api/v2/users/{user_id}/beatmapsets/most_played?limit={step}&offset={offset}"
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"Encountered status code: {response.status_code} - {response.text}")
                break

            data = response.json()
            if not data:
                print("\nFinished downloading all most played beatmaps.")
                break

            print(f"\n--- Processing beatmaps {offset + 1} to {offset + len(data)} ---")
            download_beatmaps(data)
            offset += step
        except Exception as e:
            print(f"Error fetching offset {offset}: {e}")
            break


def main():
    retrieve_most_played_beatmaps(USER_ID, LIMIT, OFFSET)


if __name__ == "__main__":
    main()
