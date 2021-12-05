import asyncio
import json
from typing import Dict, Any
import traceback

from aiohttp import web
import aiohttp_jinja2
import jinja2

from http_server_app.init_ops.init_db_ops import init_db
from http_server_app.apis.crud_api import RuleSchemaCrudApi
from http_server_app.universal_api_json_message_handler.handler import process_data_based_on_rule_schema


async def on_start(app: web.Application) -> None:
    """What should be done before aiohttp app starts"""
    app["conn"] = await init_db()


async def on_stop(app: web.Application) -> None:
    """What should be done before aiohttp app stops"""
    if app["conn"]:
        await app["conn"].close()


async def universal_api_handler(req: web.Application) -> web.Response:
    """Preliminary version of universal_api_handler"""
    message = await req.json()

    if not isinstance(message, dict):
        return web.Response(text="Json message should be dictionary like object", status=400)

    schema_name = message.get("schema_name", "")

    if not schema_name:
        return web.Response(text="Json message should have schema_name key", status=400)

    q = ("SELECT json_shema_value FROM user_defined_json_http_api_schemas_table"
         " WHERE json_schema_name = ? LIMIT 1;")

    cur = await req.app["conn"].cursor()
    await cur.execute(q, (str(schema_name), ))
    result = await cur.fetchall()

    if not result:
        return web.Response(text=f"Rule schema name {str(schema_name)} was not found in database", status=400)
    try:
        json_schema: dict = json.loads(result[0][0])
        del json_schema['schema_name']  # have to remove "schema_name" key from schema before validation
    except Exception:
        return web.Response(
            text=f"Rule schema name {str(schema_name)} is not valid json, you have to edit the schema", status=400)

    try:
        res = await process_data_based_on_rule_schema(message, json_schema)
    except Exception:
        tb = traceback.format_exc()
        print(tb)
        return web.Response(
            text=f"Failed to validate the request in accordance with schema. Please check server logs.",
            status=400,
        )

    return web.json_response({"result": str(res)}, status=200)


async def return_components_module(req: web.Application) -> web.Response:
    """provide js components file to main.html"""
    resp = web.FileResponse(r"http_server_app/components/components.js")
    resp.content_type = "application/javascript"
    return resp


@aiohttp_jinja2.template("main.html")
async def main_gui_page(req: web.Request) -> Dict[str, Any]:
    """Just index page"""
    return {}


async def init_func_standalone(args=None) -> web.Application:
    """Application factory for standalone run"""
    app = web.Application()
    app["lock"] = asyncio.Lock()
    app.router.add_get("/main", main_gui_page)
    app.router.add_get("/api/v1/get_endpoint_rule_schemes", RuleSchemaCrudApi.get_list_of_json_rule_schemas)
    app.router.add_post("/api/v1/create_new_rule_schema", RuleSchemaCrudApi.create_new_rule_schema)
    app.router.add_get("/api/v1/delete_endpoint_rule_scheme/{schema_id}", RuleSchemaCrudApi.delete_rule_scheme)
    app.router.add_post("/api/v1/update_rule_schema/{schema_id}", RuleSchemaCrudApi.update_rule_schema)
    app.router.add_post("/api/v1/universal_api_handler", universal_api_handler)
    app.router.add_get("/components/components.js", return_components_module)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("http_server_app/templates"))
    app.add_routes(
        [
            web.static("/static", "http_server_app/static"),
        ]
    )

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_stop)

    return app
