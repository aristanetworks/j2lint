"""
utils.py - functions to assist with tests
"""
from contextlib import contextmanager


@contextmanager
def does_not_raise():
    yield


def j2lint_default_rules_string():
    return (
        "Jinja2 lint rules\n"
        "S0: Jinja syntax should be correct\n"
        "S1: A single space shall be added between Jinja2 curly brackets and a variable name: {{ ethernet_interface }}\n"
        "S2: When variables are used in combination with an operator, the operator shall be enclosed by space: '{{ my_value | to_json }}'\n"
        "S3: All J2 statements must be indented by 4 more spaces within jinja delimiter. To close a control, end tag must have same indentation level.\n"
        "S4: Jinja statement should have a single space before and after: '{% statement %}'\n"
        "S5: Indentation are 4 spaces and NOT tabulation\n"
        "S6: Jinja statements should not have {%- or {%+ or -%} as delimiters\n"
        "S7: Jinja statements should be on separate lines\n"
        "V1: All variables shall use lower case: '{{ variable }}'\n"
        "V2: If variable is multi-words, underscore _ shall be used as a separator: '{{ my_variable_name }}'\n"
        "\n"
    )
