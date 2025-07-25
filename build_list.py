import requests

STATUS_URL = "https://search-engine-ip-tracker.merj.com/status"
BOT_IDS_FILE = "bot_ids.txt"
ALLOWED_IPS_FILE = "manual_allow.txt"
OUTPUT_WHITELIST_FILE = "whitelisted_ips.txt"

def fetch_status_json():
    r = requests.get(STATUS_URL)
    r.raise_for_status()
    return r.json()

def fetch_ip_ranges(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def read_allowed_ips():
    try:
        with open(ALLOWED_IPS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except FileNotFoundError:
        return []

def build_whitelist():
    # Load filtered bot IDs
    with open(BOT_IDS_FILE, "r") as f:
        wanted_bot_ids = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    status_json = fetch_status_json()

    # Map bot_id => url
    id_to_url = {}
    for bot in status_json.get("data", []):
        bot_id = bot.get("source", {}).get("id")
        url = bot.get("source", {}).get("url")
        if bot_id and url:
            id_to_url[bot_id] = url

    bot_prefixes = {}  # Map bot_id to list of IPv4 prefixes only
    for bot_id in wanted_bot_ids:
        url = id_to_url.get(bot_id)
        if not url:
            print(f"Warning: bot id '{bot_id}' not found in status JSON, skipping.")
            continue

        try:
            ip_ranges_json = fetch_ip_ranges(url)
        except Exception as e:
            print(f"Failed to fetch IPs for {bot_id}: {e}")
            continue

        ipv4_prefixes = []
        for prefix_obj in ip_ranges_json.get("prefixes", []):
            if "ipv4Prefix" in prefix_obj:
                ipv4_prefixes.append(prefix_obj["ipv4Prefix"])

        if ipv4_prefixes:
            bot_prefixes[bot_id] = ipv4_prefixes
        else:
            print(f"{bot_id} has no IPv4 prefixes; skipping.")

    allowed_ips = read_allowed_ips()

    with open(OUTPUT_WHITELIST_FILE, "w") as f:
        #f.write("# Auto-generated whitelist - do not edit manually\n\n")

        # Write static IPs from allowed.txt
        if allowed_ips:
            #f.write("# Static IPs from allowed.txt\n")
            for ip in allowed_ips:
                f.write(f"{ip} ALLOW\n")
            f.write("\n")

        # Write dynamic IPs grouped by bot (only ipv4)
        for bot_id, prefixes in bot_prefixes.items():
            #f.write(f"# {bot_id}\n")
            for prefix in prefixes:
                f.write(f"{prefix} ALLOW\n")
            f.write("\n")

    total_prefixes = sum(len(p) for p in bot_prefixes.values()) + len(allowed_ips)
    print(f"Wrote {total_prefixes} IPv4 prefixes to {OUTPUT_WHITELIST_FILE}")

if __name__ == "__main__":
    build_whitelist()
