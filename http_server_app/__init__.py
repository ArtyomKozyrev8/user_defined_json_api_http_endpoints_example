import asyncio
from typing import Dict, Any

from aiohttp import web
import aiohttp_jinja2
import jinja2

from http_server_app.init_ops.init_db_ops import init_db
from http_server_app.apis.crud_api import RuleSchemaCrudApi


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
        return web.json_response({"message": "Json message should be dictionary like object"}, status=400)

    schema_name = message.get("schema_name", "")

    if not schema_name:
        return web.json_response({"message": "Json message should have schema_name key"}, status=400)

    return web.json_response({"result": "ok"}, status=200)


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
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("http_server_app/templates"))
    app.add_routes(
        [
            web.static("/static", "http_server_app/static"),
        ]
    )

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_stop)

    return app
