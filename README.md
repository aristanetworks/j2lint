[![GitHub license](https://badgen.net/github/license/aristanetworks/j2lint)](https://github.com/aristanetworks/j2lint/blob/devel/LICENSE)
[![PyPI version fury.io](https://badge.fury.io/py/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![PyPI status](https://img.shields.io/pypi/status/j2lint.svg)](https://pypi.python.org/pypi/j2lint/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/aristanetworks/j2lint/graphs/commit-activity)
[![codecov](https://codecov.io/gh/aristanetworks/j2lint/graph/badge.svg?token=OJYHSUIPG4)](https://codecov.io/gh/aristanetworks/j2lint)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=aristanetworks_j2lint&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=aristanetworks_j2lint)

# Jinja2-Linter

AVD Ecosystem - Jinja2 Linter

## Project Goals

Build a Jinja2 linter that will provide the following capabilities:

- Validate syntax according to [AVD style guide](https://avd.arista.com/stable/docs/contribution/style-guide.html).
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
| S7   | `single-statement-per-line`     | Jinja statements should be on separate lines, ignoring raw block contents |
| V1   | `jinja-variable-lower-case`     | All variables should use lower case |
| V2   | `jinja-variable-format`         | If variable is multi-words, underscore `_` should be used as a separator |

## Getting Started

### Requirements

Minimum Python version: 3.11

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

### Install For Development

Create a virtual environment, then install the project in editable mode with the dependency groups you need:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . --group dev --group test --group lint --group type
```

If you only need a subset of the contributor tooling, install only the relevant groups.

Install the Git hook to run checks automatically before committing:

```bash
prek install
```

If you previously installed the hook with pre-commit, run `prek install -f` once to replace it.
The repository uses prek with `.pre-commit-config.yaml` so Renovate can maintain hook revisions and dependencies.

### Common Contributor Commands

```bash
pytest
tox -e lint
tox -e type
prek run                     # Check staged files
prek run --all-files         # Check all files matched by the hook configuration
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

### Running the linter with custom file extensions

```bash
j2lint <path-to-directory-of-templates> --extensions j2,html,yml
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

### Strict input checking

Use `--strict-inputs` to fail on missing paths, unsupported file extensions,
unreadable files, invalid UTF-8, or directory scan failures:

```bash
j2lint --strict-inputs templates/
```

This is opt-in. Directory scans still filter by extension, and empty scans succeed.
Input failures exit with code `1` (`E0` in JSON output); lint errors use code `2`.

Python callers can use `get_files(..., strict_inputs=True)` and
`collection.run(path, strict_inputs=True)`, and catch `InputError` for input failures.

### Ignoring rules

1. The `--ignore` option can have one or more rule IDs or short descriptions:
   `S0`, `S1`, `S2`, `S3`, `S4`, `S5`, `S6`, `S7`, `V1`, `V2`,
   `jinja-syntax-error`, `single-space-decorator`,
   `operator-enclosed-by-spaces`, `jinja-statements-single-space`,
   `jinja-statements-indentation`, `jinja-statements-no-tabs`,
   `single-statement-per-line`, `jinja-statements-delimiter`,
   `jinja-variable-lower-case`, `jinja-variable-format`.

2. If multiple rules are to be ignored, use the --ignore option along with rule descriptions separated by space.

    ```bash
    j2lint <path-to-directory-of-templates> --ignore <rule_description1> <rule_desc>
    ```

> **Note**
> When using the `-i/--ignore` or `-w/--warn` options, the arguments MUST either:
>
> - Be entered at the end of the CLI as in the example above
> - Be entered as the last options before the `<path-to-directory-of-templates>`
>   with `--` separator.  e.g.
>
>   ```bash
>   j2lint --ignore <rule_description1> <rule_desc> -- <path-to-directory-of-templates>
>   ```

3. If one or more linting rules are to be ignored only for a specific jinja template file, add a Jinja comment at the top of the file. The rule can be disabled using the short description of the rule or the id of the rule.

    ```jinja2
    {# j2lint: disable=S6 #}

    # OR
    {# j2lint: disable=jinja-statements-delimiter #}
    ```

4. Disabling multiple rules

    ```jinja2
    {# j2lint: disable=jinja-statements-delimiter j2lint: disable=S1 #}
    ```

### Adding custom rules

1. Create a new rules directory under j2lint folder.
2. Add custom rule classes which are similar to classes in j2lint/rules directory:
    The file name of rules should be in snake_case and the class name should be the PascalCase version of the file name. For example:
    - File name: `jinja_operator_has_spaces_rule.py`
    - Class name: `JinjaOperatorHasSpacesRule`

3. Run the jinja2 linter using the `-r` or `--rules_dir` option

    ```bash
    j2lint <path-to-directory-of-templates> -r <custom-rules-directory>
    ```

> **Note**
> This runs the custom linting rules in addition to the default linting rules.

### Running jinja2 linter help command

```bash
j2lint --help
```

### Running jinja2 linter on STDIN template. This option can be used with VS Code

```bash
j2lint --stdin
```

### Using j2lint with prek or pre-commit

1. Add the j2lint hook to your repository's `.pre-commit-config.yaml`. Both prek and pre-commit support this configuration.

    ```yaml
    repos:
      - repo: https://github.com/aristanetworks/j2lint.git
        rev: <release_tag/sha>
        hooks:
          - id: j2lint
    ```

2. Run `prek run --all-files`, or `pre-commit run --all-files` if you use pre-commit.

> **Note**
> When using `-i/--ignore` or `-w/--warn` arguments with either runner, use the
> following syntax
>
> ```yaml
> repos:
>   - repo: https://github.com/aristanetworks/j2lint.git
>     rev: <release_tag/sha>
>     hooks:
>       - id: j2lint
>         # Using -- to separate the end of ignore from the positional arguments
>         # passed to j2lint
>         args: [--ignore, S3, jinja-statements-single-space, --]
> ```

## Acknowledgments

This project is based on [salt-lint](https://github.com/warpnet/salt-lint) and [jinjalint](https://github.com/motet-a/jinjalint)
