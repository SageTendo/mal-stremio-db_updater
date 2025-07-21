import logging
import os
from datetime import datetime

from flask import Flask, request
from httpx import AsyncClient
from waitress import serve

from db import anime_mapping
from pymongo import UpdateOne

app = Flask(__name__)
app.config.from_object("config.Config")
ANIME_DB_SOURCE = "https://raw.githubusercontent.com/Fribb/anime-lists/refs/heads/master/anime-list-full.json"
POSSIBLE_KEYS = ["mal_id", "kitsu_id", "thetvdb_id", "anilist_id", "anidb_id", "simkl_id", "livechart_id",
                 "anisearch_id", "imdb_id", "notify.moe_id", "themoviedb_id", "anime-planet_id", "animecountdown_id"
                 ]


@app.route("/")
def index():
    logging.info("Hello, World!")
    return {"message": "Hello, World!"}


def get_authorization():
    if not request.headers.get("authorization"):
        logging.error("No API key provided")
        return False, {"status": "error", "message": "No API key provided"}

    auth_token = request.headers.get("authorization", "Bearer NO_TOKEN").split(" ")[1]
    if auth_token != os.getenv("CRON_SECRET"):
        logging.error(
            "Unauthorized request, " + request.headers.get("authorization") + " != " + os.getenv("CRON_SECRET"))
        return False, {"status": "error", "message": "Unauthorized"}
    return True, None


async def fetch_database():
    async with AsyncClient() as client:
        res = await client.get(ANIME_DB_SOURCE)
        if not res.is_success:
            logging.error(f"Failed to fetch database: {res.status_code} -> {res.text}")
            return False, {"status": "error", "code": res.status_code, "message": res.text}

        if len(res.json()) == 0:
            logging.error("No data returned from mapping db source")
            return False, {"status": "error", "message": "No data"}
    return True, res.json()


@app.route("/api/rebuild", methods=["GET"])
async def rebuild_mongo_database():
    res, error = get_authorization()
    if not res:
        return error

    success, data = await fetch_database()
    if not success:
        return data

    anime_mapping.delete_many({})

    last_updated = datetime.now()
    data_with_last_updated = []
    for anime in data:
        # Check if anime has a key
        key = next((key for key in POSSIBLE_KEYS if key in anime), None)
        if not key:
            continue
        anime["last_updated"] = last_updated
        data_with_last_updated.append(anime)

    logging.info(f"Rebuilding mapping database with {len(data_with_last_updated)} entries")
    anime_mapping.insert_many(data_with_last_updated, ordered=False)
    logging.info(f"Rebuilt mapping database with {len(data_with_last_updated)} entries")
    return {"status": "Mapping database rebuilt", "num_total": len(data)}


@app.route("/api/update", methods=["GET"])
async def update_mongo_database():
    res, error = get_authorization()
    if not res:
        return error

    success, data = await fetch_database()
    if not success:
        return data

    bulk_writes = []
    last_updated = datetime.now()
    for anime in data:
        # Check if anime has a key
        key = next((key for key in POSSIBLE_KEYS if key in anime), None)
        if not key:
            continue

        anime["last_updated"] = last_updated
        bulk_writes.append(UpdateOne({key: anime[key]}, {"$setOnInsert": anime}, True))

    logging.info(f"Updating mapping database with {len(bulk_writes)} entries")
    anime_mapping.bulk_write(bulk_writes, ordered=False)
    logging.info(f"Updated mapping database with {len(bulk_writes)} entries")
    return {"status": "Updated mapping database", "num_total": len(bulk_writes)}


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=3000)
