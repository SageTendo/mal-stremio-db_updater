import os

from flask import Flask, request
from httpx import AsyncClient

from db import anime_mapping
from pymongo import UpdateOne

app = Flask(__name__)


@app.route("/")
def index():
    return {
        "message": "Hello, World!"
    }


def get_authorization():
    if not request.headers.get("authorization"):
        return False, {
            "status": "error",
            "message": "No API key provided"
        }

    if request.headers.get("authorization") != os.getenv("CRON_SECRET"):
        return False, {
            "status": "error",
            "message": "Unauthorized"
        }
    return True


@app.route("/api/rebuild", methods=["GET"])
async def clear():
    res, error = get_authorization()
    if not res:
        return error

    async with AsyncClient() as client:
        res = await client.get(
            "https://raw.githubusercontent.com/Fribb/anime-lists/refs/heads/master/anime-list-full.json")

        if not res.is_success:
            return {
                "status": "error",
                "code": res.status_code,
                "message": res.text
            }

        if len(res.json()) == 0:
            return {
                "status": "error",
                "message": "No data"
            }

    anime_mapping.delete_many({})
    anime_mapping.insert_many(res.json())
    return {
        "status": "Mapping database rebuilt",
        "num_total": len(res.json()),
    }


@app.route("/api/update", methods=["GET"])
async def update():
    res, error = get_authorization()
    if not res:
        return error

    async with AsyncClient() as client:
        res = await client.get(
            "https://raw.githubusercontent.com/Fribb/anime-lists/refs/heads/master/anime-list-full.json")

        if not res.is_success:
            return {
                "status": "error",
                "code": res.status_code,
                "message": res.text
            }

        if len(res.json()) == 0:
            return {
                "status": "error",
                "message": "No data"
            }

    bulk_writes = []
    for anime in res.json():
        key = next(iter(anime))
        bulk_writes.append(
            UpdateOne({key: anime[key]}, {"$setOnInsert": anime}, True)
        )

    anime_mapping.bulk_write(bulk_writes)
    return {
        "status": "Updated mapping database",
        "num_total": len(res.json()),
    }


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
