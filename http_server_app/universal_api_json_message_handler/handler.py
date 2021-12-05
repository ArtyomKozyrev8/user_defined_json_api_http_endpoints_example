"""
Pay attention that we import all user predefined api function to this file, despite tha fact  that no of
the functions are used in the file code.

We do it due to eval function rules, check global, local scope rules for eval in official Python documentation.
"""

import asyncio
from typing import Dict, Any, Callable
from http_server_app.user_api_predefined_functions.some_easy_func import (
    power_3_minus_1,
    square,
    add_200,
    adouble,
)


async def process_data_based_on_rule_schema(
        json_data: Dict[Any, Any],
        rule_schema: Dict[Any, Any],
) -> Dict[Any, Any]:
    """
    Process some json dictionary-like message in accordance with scheme provided by user
    :param json_data: some json dictionary-like message
    :param rule_schema: user defined scheme to decode the message
    :return: result of decoding
    """
    r = dict()  # storage for results

    def _make_func(create_outer_main_func_code) -> Callable:
        """Creates function from user-defined scheme code"""
        global_dict = {}  # global var scope dictionary
        exec(create_outer_main_func_code, global_dict)  # compile code from user defined json scheme
        return global_dict['outer_main']  # get function object for further use in outer code

    async def _get_key_result(
            _json_data: Dict[Any, Any],
            _schema: Dict[Any, Any],
            key="",
    ) -> None:
        """Process _json_data recursively in accordance with _scheme"""
        if isinstance(_schema, dict):
            for i in _schema.keys():
                await _get_key_result(_json_data[i], _schema[i], "_".join([key, i]))
        else:
            if 'def' not in _schema:  # lambda or predefined function (in app code)
                temp = (eval(f"{_schema}(_json_data)"))
                if asyncio.iscoroutine(temp):
                    r[key.lstrip("_")] = await temp  # async predefined function
                else:
                    r[key.lstrip("_")] = temp  # sync predefined function or lambda function result
            else:  # sync or async function defined in rule schema
                if "async" not in _schema:
                    r[key.lstrip("_")] = _make_func(_schema)(_json_data)
                else:
                    r[key.lstrip("_")] = await _make_func(_schema)(_json_data)

    await _get_key_result(json_data, rule_schema)  # call inner helper function

    return r
