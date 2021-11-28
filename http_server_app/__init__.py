import asyncio
import json
from typing import Dict, Any

from aiohttp import web
import aiohttp_jinja2
import jinja2
import sqlite3


from http_server_app.init_ops.init_db_ops import init_db


async def on_start(app: web.Application) -> None:
    """What should be done before aiohttp app starts"""
    app["conn"] = await init_db()


async def on_stop(app: web.Application) -> None:
    """What should be done before aiohttp app stops"""
    if app["conn"]:
        await app["conn"].close()


@aiohttp_jinja2.template("main.html")
async def main_gui_page(req: web.Request) -> Dict[str, Any]:
    """Just index page"""
    return {}


async def get_list_of_json_rule_schemas(req: web.Request) -> web.Response:
    """Returns list of all rule schemas defined by api users"""
    q = "SELECT id, json_schema_name, json_shema_value FROM user_defined_json_http_api_schemas_table"
    cur = await req.app["conn"].cursor()
    await cur.execute(q)
    results = await cur.fetchall()
    results = [
        {
            "schema_id": i[0],
            "schema_name": i[1],
            "schema_value": i[2],
        }
        for i in results
    ]
    return web.json_response(results, status=200)


async def create_new_rule_schema(req: web.Request) -> web.Response:
    """Adds new schema rule to database"""
    data = await req.post()
    schema = data.get("json_schema", "")

    if schema == "":
        return web.json_response(
            data={"message": "json_schema Form field should be provided"},
            status=400,
        )
    try:
        schema = json.loads(schema)
    except Exception:
        return web.json_response(
            data={"message": "json_schema field value should be correct json object"},
            status=400,
        )
    if not isinstance(schema, dict):
        return web.json_response(
            data={"message": "json_schema field value should dictionary-like object"},
            status=400,
        )

    schema_name = schema.get("schema_name", "")
    if not schema_name:
        return web.json_response(
            data={"message": "json_schema field value should contain schema_name key"},
            status=400,
        )

    if not isinstance(schema_name, str):
        return web.json_response(
            data={"message": "schema_name key value should be string or integer"},
            status=400,
        )

    q = "INSERT INTO user_defined_json_http_api_schemas_table (json_schema_name, json_shema_value) VALUES (?,?)"

    async with req.app["lock"]:
        try:
            cur = await req.app["conn"].cursor()
            await cur.execute(q, (schema_name, json.dumps(schema)))
            await req.app["conn"].commit()
        except sqlite3.IntegrityError:
            return web.json_response(
                data={"message": f"schema_name {schema_name} already exists"},
                status=400,
            )

        _id = cur.lastrowid

    q = "SELECT id, json_schema_name, json_shema_value" \
        " FROM user_defined_json_http_api_schemas_table WHERE id = ?"

    await cur.execute(q, (_id, ))
    results = await cur.fetchall()
    results = [
        {
            "schema_id": i[0],
            "schema_name": i[1],
            "schema_value": i[2],
        }
        for i in results
    ]

    return web.json_response(results, status=200)


async def delete_rule_scheme(req: web.Request) -> web.Response:
    """Delete endpoint rule scheme from database"""
    schema_id = req.query.get("schema_id", "")
    q = "DELETE FROM user_defined_json_http_api_schemas_table WHERE id = ?"
    cur = await req.app["conn"].cursor()
    print(schema_id)
    async with req.app["lock"]:
        await cur.execute(q, (schema_id, ))
        await req.app["conn"].commit()

    return web.Response(text="done", status=200)


async def init_func_standalone(args=None) -> web.Application:
    """Application factory for standalone run"""
    app = web.Application()
    app["lock"] = asyncio.Lock()
    app.router.add_get("/main", main_gui_page)
    app.router.add_get("/api/get_endpoint_rule_schemes", get_list_of_json_rule_schemas)
    app.router.add_post("/api/create_new_rule_schema", create_new_rule_schema)
    app.router.add_get("/api/delete_endpoint_rule_scheme", delete_rule_scheme)
    app.router.add_post("/api/update_rule_schema", create_new_rule_schema)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("http_server_app/templates"))
    app.add_routes(
        [
            web.static("/static", "http_server_app/static"),
        ]
    )

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_stop)

    return app
