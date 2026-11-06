# osu! Most Played Beatmap Downloader

A simple Python script that fetches your most played beatmaps from the official **osu! API v2** and downloads the `.osz` files automatically using active community mirrors (`catboy.best` and `nerinyan.moe`).

Useful if you are setting up a new PC or lost your local `Songs` folder and want to quickly recover the beatmaps you have played the most.

## Requirements

- Python 3.9+
- `requests` library

Install the required dependency:

```bash
pip install requests
```

## Setup

### 1. Get your osu! OAuth Credentials
Since osu! blocks unauthenticated scraping, you need an API v2 OAuth application token:
1. Go to your [osu! Account Settings](https://osu.ppy.sh/home/account/edit#oauth) and scroll down to the **OAuth** section.
2. Click **"New OAuth Application"**.
3. Set any **Application Name** (e.g., `Beatmap Downloader`) and set `http://localhost` as the **Application Callback URL**.
4. Click **Register Application** and copy your **Client ID** and **Client Secret**.

### 2. Configure `main.py`
Open `main.py` and edit the configuration variables at the top of the file:

```python
USER_ID = "YOUR_USER_ID"           # Your numeric osu! User ID (from your profile URL)
CLIENT_ID = "YOUR_CLIENT_ID"       # OAuth Client ID
CLIENT_SECRET = "YOUR_SECRET"      # OAuth Client Secret
DOWNLOAD_FOLDER = "./downloads"    # Path where .osz files will be saved
LIMIT = 2000                       # Max number of beatmaps to fetch
OFFSET = 0                         # Starting offset
```

> **Tip:** To find your `USER_ID`, go to your osu! profile page in a browser. The number at the end of the URL (`https://osu.ppy.sh/users/12345678`) is your ID.

## Usage

Run the script from your terminal:

```bash
python main.py
```

Once downloaded, move or open the `.osz` files from the `downloads` folder into your osu! `Songs` directory. Any beatmaps that fail to download will be logged in `failed_downloads.txt`.
