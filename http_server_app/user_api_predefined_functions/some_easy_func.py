"""
The functions can be used in rule schemas.

These functions should be defined in file where process_data_based_on_rule_schema function if defined or the functions
should be imported to that file.

This should be so due to eval function scope rules.
"""


def square(item: int) -> int:
    """some user defined function"""
    return item**2


def power_3_minus_1(item: int) -> int:
    """another user defined function"""
    return item**3 - 1


def add_200(item: int) -> int:
    """one more user defined function"""
    return item + 200
