# whitelist
build a whitelist of bots


`list_bots.py` builds a list of bots in `bot_ids.txt`.

Comment out bots to block in `bot_ids.txt`.

`build_list.py` builds a new `/opt/whitelist` of allowed IPs


## Run in Docker

```
docker compose run --rm ip_whitelist_builder
```