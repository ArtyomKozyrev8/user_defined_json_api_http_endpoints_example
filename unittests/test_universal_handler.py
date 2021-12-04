import pytest
from http_server_app.universal_api_json_message_handler.handler import process_data_based_on_rule_schema

# json data received from some outer source and converted to dictionary
# e.g. outer source could be another microservice
json_message_one = {
    "x": "hello world",
    "a": "abc",
    "y": 100,
    "b": 1000,
    "d": "xxxx",
    "z": 15,
    "hh": 98,
    "ggg": 777,
    "zzz": 10,
    "d1": {
        "d6": {
            "d7": 9,
        },
        "d2": {
            "d5": 100,
            "d3": 1,
            "d4": 2,
            "d22": 5,
        },
        "d8": {
            "d9": 5,
        },
        "z2": 1000,
    }
}

json_message_two = {
    "x": "hello world again!",
    "a": "abc",
    "y": -100,
    "b": 1000,
    "d": "xxxx",
    "z": 6,
    "hh": 98,
    "ggg": 777,
    "zzz": 20,
    "d1": {
        "d6": {
            "d7": 9,
        },
        "d2": {
            "d5": 100,
            "d3": 10,
            "d4": 3,
        },
        "d8": {
            "d9": 90,
        },
        "z2": 800,
    }
}

# the data in json converted to dictionary
# the data can be stored as json in database
user_defined_json_scheme = {
    "x": "str",  # in-language operator
    "y": "int",  # in-language operator
    "z": "square",  # function defined inside app code
    "zzz": "power_3_minus_1",  # function defined inside app code
    "d1": {
        "d2":
            {
                "d3": "add_200",   # function defined inside app code
                "d4": "power_3_minus_1",   # function defined inside app code
            },
        "z2": (  # sync function defined by user in json scheme
            "def outer_main(x):"
            "\n\treturn plus_hundred(x)"
            "\ndef plus_hundred(x):"
            "\n\treturn x-10000"
        ),
    },
    "a": "(lambda x: x + 'ijk')",  # lambda function defined by user in json scheme
    "z": (   # sync function defined by user in json scheme
        "def outer_main(x):"
        "\n\treturn plus_hundred(x)"
        "\ndef plus_hundred(x):"
        "\n\treturn x+100"
    ),
}


@pytest.mark.asyncio
async def test_process_data_based_on_rule_schema_1():
    r1 = await process_data_based_on_rule_schema(json_message_one, user_defined_json_scheme)
    assert r1 == {'x': 'hello world', 'y': 100, 'z': 115, 'zzz': 999, 'd1_d2_d3': 201, 'd1_d2_d4': 7, 'd1_z2': -9000,
                  'a': 'abcijk'}


@pytest.mark.asyncio
async def test_process_data_based_on_rule_schema_2():
    r2 = await process_data_based_on_rule_schema(json_message_two, user_defined_json_scheme)
    assert r2 == {'x': 'hello world again!', 'y': -100, 'z': 106, 'zzz': 7999, 'd1_d2_d3': 210, 'd1_d2_d4': 26,
                  'd1_z2': -9200, 'a': 'abcijk'}
