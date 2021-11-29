from aiohttp import ClientSession
import asyncio
import json

SERVER = "http://localhost:5879/api/v1/"

SCHEMA = {
    "schema_name": "df",
    "x": {
        "y": {
            "y1": 10,
            "y2": 100,
        },
        "z": 10,
    },
    "a": {
        "ba": 1000,
        "ca": "xh1",
    }
}

UPDATE_ID = 200


async def create_new_json_schema(session: ClientSession) -> None:
    url = f"{SERVER.rstrip('/')}/create_new_rule_schema"
    data = {
        "json_schema": json.dumps(SCHEMA),
    }
    async with session.post(url, data=data) as r:
        if r.status == 200:
            mes = await r.json()
            print(f"OK: {r.status}. Schema create: {mes}")
        elif r.status == 400:
            mes = await r.json()
            print(f"Incorrect scheme error {r.status}. {mes}")
        else:
            text = await r.text('utf8')
            print(f"Unexpected error {r.status}. {text}")


async def update_existent_json_schema(session: ClientSession) -> None:
    url = f"{SERVER.rstrip('/')}/update_rule_schema/{UPDATE_ID}"
    data = {
        "json_schema": json.dumps(SCHEMA),
    }

    async with session.post(url, data=data) as r:
        if r.status == 200:
            print(f"OK: {r.status}. Schema updated")
        elif r.status == 400:
            mes = await r.json()
            print(f"Incorrect scheme error {r.status}. {mes}")
        else:
            text = await r.text('utf8')
            print(f"Unexpected error {r.status}. {text}")


async def main_wrapper():
    async with ClientSession() as session:
        # await create_new_json_schema(session)
        await update_existent_json_schema(session)


if __name__ == '__main__':
    asyncio.run(main_wrapper())
