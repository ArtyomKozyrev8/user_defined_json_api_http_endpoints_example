import json
from typing import Any, Union, Dict

from aiohttp import web
import sqlite3


class RuleSchemaCrudApi:
    """CRUD methods which are related to user-defined Rule schemas for http api endpoints"""
    @staticmethod
    def _check_rule_schema_consistency(schema: Any) -> Union[web.Response, Dict[Any, Any]]:
        """Validates user-defined rule schema"""
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

        return schema

    @staticmethod
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
                "schema_value": json.loads(i[2]),
            }
            for i in results
        ]
        return web.json_response(results, status=200)

    @staticmethod
    async def create_new_rule_schema(req: web.Request) -> web.Response:
        """Adds new rule schema to database"""
        data = await req.post()
        schema = data.get("json_schema", "")

        schema = RuleSchemaCrudApi._check_rule_schema_consistency(schema)
        if isinstance(schema, web.Response):
            return schema  # means that some error took place

        q = "INSERT INTO user_defined_json_http_api_schemas_table (json_schema_name, json_shema_value) VALUES (?,?)"

        async with req.app["lock"]:
            try:
                cur = await req.app["conn"].cursor()
                await cur.execute(q, (schema["schema_name"], json.dumps(schema)))
                await req.app["conn"].commit()
            except sqlite3.IntegrityError:
                return web.json_response(
                    data={"message": f"schema_name {schema['schema_name']} already exists"},
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
                "schema_value": json.loads(i[2]),
            }
            for i in results
        ]

        if results:
            return web.json_response(results[0], status=200)

        return web.json_response({"message": f"failed to get data about new rule schema in database"}, status=400)

    @staticmethod
    async def update_rule_schema(req: web.Request) -> web.Response:
        """updates existent rule schema in database"""
        schema_id = req.match_info['schema_id']
        data = await req.post()
        schema = data.get("json_schema", "")

        if schema_id == "":
            return web.json_response(
                data={"message": "schema_id Form field should be provided"},
                status=400,
            )

        schema = RuleSchemaCrudApi._check_rule_schema_consistency(schema)
        if isinstance(schema, web.Response):
            return schema  # means that some error took place

        q = (
            "UPDATE user_defined_json_http_api_schemas_table"
            " SET json_schema_name = ?, json_shema_value = ?"
            " WHERE id = ?"
        )

        async with req.app["lock"]:
            try:
                cur = await req.app["conn"].cursor()
                await cur.execute(q, (schema["schema_name"], json.dumps(schema), schema_id))
                await req.app["conn"].commit()
            except sqlite3.IntegrityError:
                return web.json_response(
                    data={"message": f"schema_name {schema['schema_name']} already exists"},
                    status=400,
                )

        return web.Response(text="done", status=200)

    @staticmethod
    async def delete_rule_scheme(req: web.Request) -> web.Response:
        """Delete rule schema from database"""
        schema_id = req.match_info['schema_id']
        q = "DELETE FROM user_defined_json_http_api_schemas_table WHERE id = ?"
        cur = await req.app["conn"].cursor()

        await cur.execute(q, (schema_id, ))
        await req.app["conn"].commit()

        return web.Response(text="done", status=200)
