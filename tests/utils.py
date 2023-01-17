"""
utils.py - functions to assist with tests
"""
from contextlib import contextmanager


@contextmanager
def does_not_raise():
    """
    Provides a context manager that does not raise anything
    for pytest tests
    """
    yield


def j2lint_default_rules_string():
    """
    The description of the default rules
    """
    return (
        "─────────────────────────── Rules in the Collection ────────────────────────────\n"
        "📄 Origin: BUILT-IN\n"
        "├── S0 Jinja syntax should be correct (jinja-syntax-error)\n"
        "├── S1 A single space shall be added between Jinja2 curly brackets and a \n"
        "│   variable name: {{ ethernet_interface }} (single-space-decorator)\n"
        "├── S2 When variables are used in combination with an operator, the operator \n"
        "│   shall be enclosed by space: '{{ my_value | to_json }}' \n"
        "│   (operator-enclosed-by-spaces)\n"
        "├── S3 All J2 statements must be indented by 4 more spaces within jinja \n"
        "│   delimiter. To close a control, end tag must have same indentation level. \n"
        "│   (jinja-statements-indentation)\n"
        "├── S4 Jinja statement should have a single space before and after: '{% \n"
        "│   statement %}' (jinja-statements-single-space)\n"
        "├── S5 Indentation are 4 spaces and NOT tabulation (jinja-statements-no-tabs)\n"
        "├── S6 Jinja statements should not have {%- or {%+ or -%} as delimiters \n"
        "│   (jinja-statements-delimiter)\n"
        "├── S7 Jinja statements should be on separate lines (single-statement-per-line)\n"
        "├── V1 All variables shall use lower case: '{{ variable }}' \n"
        "│   (jinja-variable-lower-case)\n"
        "└── V2 If variable is multi-words, underscore _ shall be used as a separator: \n"
        "    '{{ my_variable_name }}' (jinja-variable-format)\n"
    )


NO_ERROR_NO_WARNING_JSON = """{
  "ERRORS": [],
  "WARNINGS": []
}
"""
ONE_ERROR_JSON = """{
  "ERRORS": [
    {
      "id": "T0",
      "message": "test rule 0",
      "filename": "dummy.j2",
      "line_number": 1,
      "line": "dummy",
      "severity": "LOW"
    }
  ],
  "WARNINGS": []
}
"""

ONE_ERROR_ONE_WARNING_JSON = """{
  "ERRORS": [
    {
      "id": "T0",
      "message": "test rule 0",
      "filename": "dummy.j2",
      "line_number": 1,
      "line": "dummy",
      "severity": "LOW"
    }
  ],
  "WARNINGS": [
    {
      "id": "T0",
      "message": "test rule 0",
      "filename": "dummy.j2",
      "line_number": 1,
      "line": "dummy",
      "severity": "LOW"
    }
  ]
}
"""

ONE_ERROR = (
    "────────────────────────────── JINJA2 LINT ERRORS ──────────────────────────────\n"
    "📄 dummy.j2\n"
    "└── dummy.j2:1 test rule 0 (test-rule-0)\n"
    "\n"
    "Jinja2 linting finished with 1 error(s) and 0 warning(s)\n"
)

# Cannot use """ because of the trailing whitspaces generated in rich Tree
ONE_WARNING_VERBOSE = (
    "───────────────────────────── JINJA2 LINT WARNINGS ─────────────────────────────\n"
    "📄 dummy.j2\n"
    "└── Linting rule: T0\n"
    "    Rule description: test rule 0\n"
    "    Error line: dummy.j2:1 dummy\n"
    "    Error message: test rule 0\n"
    "    \n"
    "\n"
    "Jinja2 linting finished with 0 error(s) and 1 warning(s)\n"
)

# Cannot use """ because of the trailing whitspaces generated in rich Tree
ONE_ERROR_ONE_WARNING_VERBOSE = (
    "────────────────────────────── JINJA2 LINT ERRORS ──────────────────────────────\n"
    "📄 tests/data/test.j2\n"
    "└── Linting rule: T0\n"
    "    Rule description: test rule 0\n"
    "    Error line: dummy.j2:1 dummy\n"
    "    Error message: test rule 0\n"
    "    \n"
    "───────────────────────────── JINJA2 LINT WARNINGS ─────────────────────────────\n"
    "📄 tests/data/test.j2\n"
    "└── Linting rule: T0\n"
    "    Rule description: test rule 0\n"
    "    Error line: dummy.j2:1 dummy\n"
    "    Error message: test rule 0\n"
    "    \n"
    "\n"
    "Jinja2 linting finished with 1 error(s) and 1 warning(s)\n"
)


ONE_ERROR_REGEX = (
    r"────────────────────────────── JINJA2 LINT ERRORS ────────────────────────────── "
    r"📄 .*.j2 "
    r"└── (.*.j2):1 Jinja statement should have a single space before and "
    r"after: '{% statement %}' \(jinja-statements-single-space\) "
    r"Jinja2 linting finished with 1 error\(s\) and 0 warning\(s\)"
)
