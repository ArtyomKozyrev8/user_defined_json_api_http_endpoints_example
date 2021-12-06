"""
Pay attention that we import all user predefined api function to this file, despite tha fact  that no of
the functions are used in the file code.

We do it due to eval function rules, check global, local scope rules for eval in official Python documentation.
"""

import asyncio
from typing import Dict, Any, Callable, Coroutine, Tuple
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
    Process some json dictionary-like message in accordance with schema provided by user
    :param json_data: some json dictionary-like message
    :param rule_schema: user defined scheme to decode the message
    :return: result of decoding
    """
    r = dict()  # storage for results

    def _make_func(create_outer_main_func_code) -> Callable:
        """Creates function from user-defined schema code"""
        global_dict = {}  # global var scope dictionary
        exec(create_outer_main_func_code, global_dict)  # compile code from user defined json scheme
        return global_dict['outer_main']  # get function object for further use in outer code

    async def _coroutine_return_dict_key_wrapper(key: Any, coroutine: Coroutine) -> Tuple[Any, Any]:
        """Some _get_key_result results value could be coroutines instead of final results. So we have
        to wrap these coroutine in order to know key, val pairs and then rewrite results in r dictionary"""
        result = await coroutine
        return key, result

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
            if 'def' not in _schema:  # lambda or predefined sync or async function (in app code)
                r[key.lstrip("_")] = (eval(f"{_schema}(_json_data)"))
            else:  # sync or async function defined in rule schema (by user in GUI)
                r[key.lstrip("_")] = _make_func(_schema)(_json_data)

    await _get_key_result(json_data, rule_schema)  # call inner helper function

    # await coroutines which could be in results
    key_vs_cor_res = [_coroutine_return_dict_key_wrapper(k, v) for k, v in r.items() if asyncio.iscoroutine(v)]
    res = await asyncio.gather(*key_vs_cor_res)
    # substitute coroutines with values
    for k, v in res:
        r[k] = v

    return r
