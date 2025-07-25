import requests

STATUS_URL = "https://search-engine-ip-tracker.merj.com/status"
OUTPUT_FILE = "bot_ids.txt"

def fetch_bot_ids():
    r = requests.get(STATUS_URL)
    r.raise_for_status()
    data = r.json()

    bot_ids = []
    for bot in data.get("data", []):
        bot_id = bot.get("source", {}).get("id")
        if bot_id:
            bot_ids.append(bot_id)

    with open(OUTPUT_FILE, "w") as f:
        for bot_id in bot_ids:
            f.write(bot_id + "\n")
    print(f"Wrote {len(bot_ids)} bot IDs to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_bot_ids()
