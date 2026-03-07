import discord
import ctypes
import json
import os
import asyncio
import platform
import requests

if not os.path.exists("config"):
    os.makedirs("config")

config_path = "config/config.json"
if not os.path.exists(config_path):
    default_config = {
        "token": "Add your token here.",
        "statuses": [
            {"emoji": "⚙️", "text": "Changing my status via DiscordStatusRotation on GitHub"},
            {"emoji": "❤️", "text": "Wanna get a cool status cycle too? github.com/asteroidlordfr/DiscordStatusRotation"},
            {"emoji": "💻", "text": "Using an awesome GitHub tool called DiscordStatusRotation"}
        ],
        "time_til_change": 20
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)

with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)
    token = config.get("token")
    statuses = config.get("statuses", [])
    time_til_change = config.get("time_til_change", 20)

class StatusClient(discord.Client):
    async def on_ready(self):
        if platform.system() == "Windows":
            ctypes.windll.kernel32.SetConsoleTitleW("DiscordStatusRotation")
            os.system('cls')
        else:
            os.system('clear')

        print(f"Logged in as {self.user}")
        print(f"Loaded {len(statuses)} custom statuses")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        self.loop.create_task(self.status())

    async def setstatus(self, emoji, text):
        payload = {"custom_status": {"text": text}}
        if emoji:
            payload["custom_status"]["emoji_name"] = emoji
            payload["custom_status"]["emoji_id"] = None

        try:
            r = await self.loop.run_in_executor(
                None,
                lambda: self.session.patch("https://discord.com/api/v9/users/@me/settings", json=payload)
            )
            if r.status_code == 200:
                print(f"Status updated: {emoji} {text}")
            else:
                print(f"API error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Request failed: {e}")

    async def status(self):
        await self.wait_until_ready()
        while not self.is_closed():
            with open(config_path, "r", encoding="utf-8") as file:
                new_config = json.load(file)
                current_statuses = new_config.get("statuses", [])
                current_time = new_config.get("time_til_change", 20)

            if not current_statuses:
                await asyncio.sleep(current_time)
                continue

            for item in current_statuses:
                emoji = item.get("emoji", "")
                text = item.get("text", "")
                await self.setstatus(emoji, text)
                await asyncio.sleep(current_time)

client = StatusClient()
client.run(token, bot=False)
