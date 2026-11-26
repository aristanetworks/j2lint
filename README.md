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

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then create an editable
development environment from the committed `uv.lock`:

```bash
uv sync --locked --group test --group lint --group type --group benchmark
source .venv/bin/activate
```

The `dev` group is included by default. Select fewer groups if you only need a subset of the
contributor tooling. The `benchmark` group is also needed when linting or type-checking the benchmark tests.
Standard pip installations remain supported, but do not use the lock file.

CI uses locked dependencies for a Python 3.11 test job, linting, type checking, and benchmarks.
The Python 3.11–3.15 tox matrix resolves dependencies independently to check compatibility with
current releases. Running tox locally also resolves dependencies independently of `uv.lock`.

After changing dependency declarations or bumping the project version, run `uv lock` and include
the updated lock file in the same pull request. Use `uv lock --upgrade-package PACKAGE` for a
targeted upgrade or `uv lock --upgrade` to refresh all locked dependencies. Renovate opens weekly
lock maintenance pull requests; uv excludes releases less than seven days old, including transitive
dependencies. This delay applies when resolving dependencies, without preventing CI from using
the existing lock. Published package dependency ranges are unchanged by the lock file.

Install the Git hook to run checks automatically before committing:

```bash
prek install
```

If you previously installed the hook with pre-commit, run `prek install -f` once to replace it.
The repository uses prek with `.pre-commit-config.yaml` so Renovate can maintain hook revisions and dependencies.

### Performance Benchmarks

Install the optional benchmark dependencies and run the self-contained suite explicitly:

```bash
uv sync --locked --no-default-groups --group test --group benchmark
uv run --no-sync python -m pytest --codspeed --no-cov -o addopts= -q tests/benchmark
```

`uv sync` removes dependencies outside the selected groups; rerun the development setup command
above to restore the full contributor environment.

Normal `pytest` and tox test runs exclude `tests/benchmark`. The suite generates deterministic
templates inside j2lint, with no AVD dependency or external template downloads. It measures the
complete built-in rule collection on clean templates, templates with lint errors, and raw blocks,
plus statement extraction at increasing sizes. Input creation and correctness assertions are outside
the measured calls; full-rule benchmarks include file reading but exclude CLI startup and final output.

CI uses CodSpeed's simulation mode with Python 3.12.16 from `actions/setup-python` and locked
dependencies to compare CPU performance across commits; it does not measure memory. The benchmark
Python version is pinned separately from `uv.lock`, and uv installs dependencies using that exact
interpreter. CI checks the selected version and logs the runtime, packages, and CPU details.
Update the benchmark interpreter deliberately and establish a new baseline when changing it.
Hosted runner hardware and images can still change; check CodSpeed's environment warnings before
attributing a performance difference to code. The reusable `codspeed.yml` workflow runs after the
supported-version tests on upstream pushes and pull requests, and can also be started manually. Uploads authenticate
using GitHub OIDC, as in ANTA; the repository must be enabled in CodSpeed. Local runs use CodSpeed's
wall-time measurement by default; CI's simulated measurements require the CodSpeed runner.

### Common Contributor Commands

```bash
uv run --no-sync python -m pytest
uv run --no-sync ruff check .
uv run --no-sync ruff format . --check
uv run --no-sync pylint j2lint
uv run --no-sync pylint tests
prek run ty --all-files
prek run                     # Check staged files
prek run --all-files         # Check all files matched by the hook configuration
```

The commands above assume the development environment has been synced. Pre-commit hooks create
their own environments from `.pre-commit-config.yaml`; their dependencies are not controlled by `uv.lock`.

### Updating GitHub Actions

Workflow action versions use readable tags; `.github/workflows/actions.lock` pins
their commits, including transitive action dependencies. Renovate updates the version
tags and lockfile together. External reusable workflows keep inline SHA pins because
the lockfile does not cover them.

After adding a workflow or changing an action reference, regenerate and verify the lockfile:

```bash
gh extension install github/gh-actions-lock --pin v0.5.0
gh actions-lock
gh actions-lock --verify
```

Commit the workflow changes and generated lockfile together. CI verifies coverage and
upstream provenance. Review changed commits and repository identities in lockfile diffs;
do not edit the generated file by hand. To deliberately advance a moved branch or
partial version tag after reviewing the upstream changes, run `gh actions-lock --relock`.

The verifier warns that PyPI Publish's generated local Docker action cannot be followed.
The publisher and its remote action dependencies are locked; the generated local action
and container image are outside the lockfile's coverage.

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

The equivalent `--output-format json` option is also available. The default is
`--output-format text`. Do not combine `--json` with `--output-format`.

### Showing annotations in GitHub Actions

Use `--output-format github` to emit GitHub Actions error and warning annotations
with the diagnostic's file, line number, rule ID, and message. After checking out
your repository and installing j2lint, add a step such as:

```yaml
- name: Lint Jinja templates
  run: j2lint --output-format github templates/
```

Rules selected by `--warn` produce warning annotations. Lint errors still return
exit code `2`, failing the step; warnings alone return `0`. A clean run produces no
annotations, including with `--verbose`. Annotation levels follow `--warn`, not the
rule's LOW/MEDIUM/HIGH severity. GitHub controls annotation display and limits.

Run from the repository root so relative filenames match checked-out files.
Stdin diagnostics omit file and line properties because their temporary file is
deleted. Console logs requested with `--stdout` go to stderr in GitHub mode to
keep stdout dedicated to annotations. Rule listing (`--list`) does not support
GitHub output.

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
