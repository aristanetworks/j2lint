[![GitHub license](https://badgen.net/github/license/aristanetworks/j2lint)](https://github.com/aristanetworks/j2lint/blob/devel/LICENSE)
[![PyPI version fury.io](https://badge.fury.io/py/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![PyPI status](https://img.shields.io/pypi/status/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/aristanetworks/j2lint/graphs/commit-activity)

# Jinja2-Linter

AVD Ecosystem - Jinja2 Linter

## Project Goals

Build a Jinja2 linter that will provide the following capabilities:

- Validate syntax according to [AVD style guide](https://avd.sh/en/stable/docs/contribution/style-guide.html).
- Capability to run as part of a CI pipeline to enforce j2lint rules.
- Develop an extension that works with VSCode and potentially other IDEs i.e PyCharm.

## Syntax and code style issues

| Code | Short Description | Description |
|------|-------------------|-------------|
| S0   | `jinja-syntax-error`            | Jinja2 syntax should be correct |
| S1   | `single-space-decorator`        | A single space should be added between Jinja2 curly brackets and a variable's name |
| S2   | `operator-enclosed-by-spaces`   | When variables are used in combination with an operator, the operator shall be enclosed by space |
| S3   | `jinja-statements-indentation`  | Nested jinja code block should follow next rules:<br>- All J2 statements must be enclosed by 1 space<br>- All J2 statements must be indented by 4 more spaces within jinja delimiter<br>- To close a control, end tag must have same indentation level |
| S4   | `jinja-statements-single-space` | Jinja statement should have at least a single space after '{%' and a single space before '%}' |
| S5   | `jinja-statements-no-tabs`      | Indentation should not use tabulation but 4 spaces |
| S6   | `jinja-statements-delimiter`    | Jinja statements should not have {%- or {%+ or -%} as delimiters |
| S7   | `single-statement-per-line`     | Jinja statements should be on separate lines |
| V1   | `jinja-variable-lower-case`     | All variables should use lower case |
| V2   | `jinja-variable-format`         | If variable is multi-words, underscore `_` should be used as a separator |

## Getting Started

### Requirements

Python version 3.8+

### Install with pip

To get started, you can use Python pip to install j2lint:

**Install the latest stable version:**

```bash
pip3 install j2lint
```

**Install the latest development version:**

```bash
pip3 install git+https://github.com/aristanetworks/j2lint.git
```

## Running the linter

```bash
j2lint <path-to-directory-of-templates>
```

### Running the linter on a specific file

```bash
j2lint <path-to-directory-of-templates>/template.j2
```

### Listing linting rules

```bash
j2lint --list
```

### Running the linter with verbose linter error output

```bash
j2lint <path-to-directory-of-templates> --verbose
```

### Running the linter with logs enabled. Logs saved in jinja2-linter.log in the current directory

```bash
j2lint <path-to-directory-of-templates> --log
```

To enable debug logs, use both options:

```bash
j2lint <path-to-directory-of-templates> --log --debug
```

### Running the linter with JSON format for linter error output

```bash
j2lint <path-to-directory-of-templates> --json
```

### Ignoring rules

1. The --ignore option can have one or more of these values: syntax-error, single-space-decorator, filter-enclosed-by-spaces, jinja-statement-single-space, jinja-statements-indentation, no-tabs, single-statement-per-line, jinja-delimiter, jinja-variable-lower-case, jinja-variable-format.

2. If multiple rules are to be ignored, use the --ignore option along with rule descriptions separated by space.

    ```bash
    j2lint <path-to-directory-of-templates> --ignore <rule_description1> <rule_desc>
    ```

> **Note**
> This runs the custom linting rules in addition to the default linting rules.
> When using the `-i/--ignore` or `-w/--warn` options, the arguments MUST either:
> * Be entered at the end of the CLI as in the example above
> * Be entered as the last options before the `<path-to-directory-of-templates>`
>   with `--` separator.  e.g.
>   ```bash
>   j2lint --ignore <rule_description1> <rule_desc> -- <path-to-directory-of-templates>
>   ```

3. If one or more linting rules are to be ignored only for a specific jinja template file, add a Jinja comment at the top of the file. The rule can be disabled using the short description of the rule or the id of the rule.

    ```jinja2
    {# j2lint: disable=S6}

    # OR
    {# j2lint: disable=jinja-delimiter #}
    ```

4. Disabling multiple rules

    ```jinja2
    {# j2lint: disable=jinja-delimiter j2lint: disable=S1 #}
    ```

### Adding custom rules

1. Create a new rules directory under j2lint folder.
2. Add custom rule classes which are similar to classes in j2lint/rules directory:
    The file name of rules should be in snake_case and the class name should be the PascalCase version of the file name. For example:
    - File name: `jinja_operator_has_spaces_rule.py`
    - Class name: `JinjaOperatorHasSpacesRule`

3. Run the jinja2 linter using --rules-dir option

    ```bash
    j2lint <path-to-directory-of-templates> --rules-dir <custom-rules-directory>
    ```

> **Note**
> This runs the custom linting rules in addition to the default linting rules.

### Running jinja2 linter help command

```bash
j2lint --help
```

### Running jinja2 linter on STDIN template. This option can be used with VS Code.

```bash
j2lint --stdin
```

### Using j2lint as a pre-commit-hook

1. Add j2lint pre-commit hook inside your repository in .pre-commit-config.yaml.

    ```bash
    - repo: https://github.com/aristanetworks/j2lint.git
        rev: <release_tag/sha>
        hooks:
        - id: j2lint
    ```

2. Run pre-commit -> `pre-commit run --all-files`

> **Note**
> When using `-i/--ignore` or `-w/--warn` argument in pre-commit, use the
> following syntax
>
> ```bash
> - repo: https://github.com/aristanetworks/j2lint.git
>     rev: <release_tag/sha>
>     hooks:
>     - id: j2lint
>     # Using -- to separate the end of ignore from the positional arguments
>     # passed to j2lint
>       args: [--ignore, S3, jinja-statements-single-space, --]
> ```

## Acknowledgments

This project is based on [salt-lint](https://github.com/warpnet/salt-lint) and [jinjalint](https://github.com/motet-a/jinjalint)
