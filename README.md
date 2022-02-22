# Jinja2-Linter

AVD Ecosystem - Jinja2 Linter

The goal of this project is to build a Jinja2 linter that will provide the following capabilities:

- Validate syntax according to [AVD style guide](https://avd.sh/en/latest/docs/contribution/style-guide.html)
- Develop extension that works with VSCode and potentianly others IDEs i.e PyCharm
  - if supporting multiple IDEs adds to much complexity, support for VSCode will take priority
- Capability to run as a GitHub Action and used to enforce style in our CI pipeline

Syntax and code style issues detected by Jinja2 Linter are:

1. S0 Jinja2 syntax should be correct
2. S1 A single space shall be added between Jinja2 curly brackets and a variable's name
3. S2 When variables are used in combination with a filter, | shall be enclosed by space
4. S3 Nested jinja code block shall follow next rules:
   - All J2 statements must be enclosed by 1 space
   - All J2 statements must be indented by 4 more spaces within jinja delimiter
   - To close a control, end tag must have same indentation level
   - Indentation are 4 spaces and NOT tabulation
5. S7 Jinja statements should be on separate lines
6. S8 Jinja statements should not have {%- or {%+ or -%} as delimeters
7. VAR-1 All variables shall use lower case
8. VAR-2 If variable is multi-words, underscore _ shall be used as a separator

## Getting Started

### Install with pip

To get started, you can use Python pip to install j2lint:

```bash
pip install git+https://github.com/aristanetworks/j2lint.git
```

### Git approach

To get started with j2lint code, clone the Jinja2 Linter project on your system:

```
git clone https://github.com/aristanetworks/j2lint.git
```

### Prerequisites

1. Python version 3.6+


### Creating the environment

1. Create a virtual environment and activate it

```bash
python3 -m venv myenv
source myenv/bin/activate
```

1. Install pip, jinja2 and jinja2-linter

```bash
sudo apt-get install python3-pip
pip3 install jinja2
cd jinja2-linter
python setup.py install
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

1. The --ignore option can have one or more of these values: syntax-error, single-space-decorator, filter-enclosed-by-spaces, jinja-statement-single-space, jinja-statements-indentation, no-tabs, single-statement-per-line, jinja-delimeter, jinja-variable-lower-case, jinja-variable-format.
2. If multiple rules are to be ignored, use the --ignore option along with rule descriptions separated by space.

```bash
j2lint <path-to-directory-of-templates> --ignore <rule_description1> <rule_desc>
```

3. If one or more linting rules are to be ignored only for a specific jinja template file, add a Jinja comment at the top of the file. The rule can be disabled using the short description of the rule or the id of the rule.

```jinja2
{# j2lint: disable=S8}

# OR
{# j2lint: disable=jinja-delimeter #}
```

4. Disabling multiple rules

```jinja2
{# j2lint: disable=jinja-delimeter j2lint: disable=S1 #}
```

### Adding custom rules

1. Create a new rules directory under j2lint folder.
2. Add custom rule classes which are similar to classes in j2lint/rules directory.
3. Run the jinja2 linter using --rules-dir option

```bash
j2lint <path-to-directory-of-templates> --rules_dir <custom-rules-directory>
```

> Note: This runs the custom linting rules in addition to the default linting rules.

### Running jinja2 linter help command

```bash
j2lint --help
```

### Running jinja2 linter on STDIN template. This option can be used with VS Code.

```bash
j2lint --stdin
```

## Acknowledgement

This project is based on [salt-lint](https://github.com/warpnet/salt-lint) and [jinjalint](https://github.com/motet-a/jinjalint)
