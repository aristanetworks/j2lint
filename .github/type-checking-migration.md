# Pyright to ty

The migration pins ty 0.0.105, the newest release eligible under the repository's
seven-day release-age policy on 2026-11-24. The diagnostic comparison against
Pyright 1.1.414 was verified with ty 0.0.105 and the initially evaluated 0.0.109.
The follow-up checklist records reproductions for rechecking coverage on upgrades.

This migration replaces Pyright in the `type` dependency group, tox, and the
contributor hook, and updates `uv.lock`. CI runs ty through the existing required
prek job; the duplicate standalone typing job is removed. The Python 3.11 target
and scope (`j2lint` and `tests`, including benchmarks) are preserved. Runtime
dependencies are unaffected.

## Why migrate

- ty is a native Rust executable; the type checker no longer needs Pyright's Node.js runtime.
- Diagnostics include source context, expected and actual types, and related locations.
- ty supports watch mode and a language server for editor feedback.

These benefits do not establish equivalent checking. ty is still beta, uses
`0.0.x` versions, and explicitly permits breaking changes between releases,
including diagnostic changes. Both the dependency and hook pin the exact version;
Renovate groups their updates. Review those updates as potential checking changes.

## Configuration choices

The previous Pyright configuration used its default basic mode, not strict mode.
The migration does not remove an existing strict policy.

Two non-default ty settings retain checks that would otherwise be lost:

- `analysis.return-type-inference = "always"` catches incompatible uses of return
  values from unannotated synchronous helpers. This does not enable inference for
  unannotated async functions or generators.
- `rules.possibly-unresolved-reference = "error"` catches references to variables
  initialized on only some control-flow paths.

The hook checks the whole configured scope rather than only changed files, since
changing a function can break callers elsewhere. The official `astral-sh/ty-pre-commit`
hook also runs for configuration-only and deletion-only commits. It pins both ty
and uv and invokes uv's preview `check` command. The hook arguments select the
locked `type`, `test`, and `benchmark` dependency groups without installing the
default development groups. Dependencies come from the project's `uv.lock`,
rather than a duplicated `additional_dependencies` list. `--isolated` prevents
the hook from changing the contributor's `.venv` or lockfile. tox explicitly
selects its own interpreter for import resolution with `ty check --python {envpython}`.
For local and CI commands, see [Development type checks](../README.md#development-type-checks).

The first ty run exposed a dead plugin-loader cleanup block (`file_handle` was
always `None`) and incompatible test helper signatures. The cleanup block was
removed; always-raising test helpers now return `Never`, and a replacement method
accepts keyword arguments. All six Pyright suppression comments could then be
removed without adding ty suppressions or disabling checks.

## What checking we lose

Deliberately invalid standalone probes compared both pinned checkers. This is a
targeted comparison, not proof of full typing-spec parity.

The [migration follow-up checklist](ty_migration_follow_up.md) tracks the four
missing checks with upstream issues and reproductions to rerun on ty upgrades.

| Case | Pyright basic | ty with this configuration |
| --- | --- | --- |
| Wrong argument type | Reports | Reports |
| Wrong annotated return type | Reports | Reports |
| Member access on `str \| None` | Reports | Reports |
| Incompatible method override | Reports | Reports |
| Missing import | Reports | Reports |
| Incorrect `assert_type` on a subclass-preserving `Self` factory | Reports | Reports |
| Possibly unbound local variable | Reports | Reports with the enabled rule |
| Wrong use of an unannotated synchronous function's return | Reports | Reports with inference enabled |
| Access to a `NotRequired` TypedDict key without checking membership | Reports | **Misses** |
| Overlapping overload signatures | Reports | **Misses** |
| `super()` call to an unimplemented abstract method | Reports | **Misses** |
| List used as a dictionary key | Reports | **Misses** |

For example, both checkers accept the declarations below, but only Pyright flags
the unsafe access and invalid dictionary key:

```python
from typing import NotRequired, TypedDict


class Options(TypedDict):
    path: NotRequired[str]


def get_path(options: Options) -> str:
    return options["path"]  # May raise KeyError.


invalid_mapping = {[1, 2]: "value"}  # Raises TypeError.
```

The source currently uses abstract rules and mappings, so those gaps are relevant
to future changes. TypedDicts and overloads are not currently used in `j2lint` or
its tests. Existing tests and linters help but are not equivalent replacements
for the missing static checks.

Pyright also has stricter optional checks without direct ty equivalents, such as
diagnostics for unknown argument/member types and exhaustive `match` handling.
Those checks were not enabled here, so they are future policy options we give up,
rather than lost checks from the existing configuration. Return inference for
unannotated async functions and generators remains another difference; project
functions should continue to have explicit annotations enforced by Ruff.

## Contributor impact and recommendation

Use `ty check` in place of `pyright`, or keep using `tox -e type`. New selective
suppressions use `# ty: ignore[rule-name]`; Pyright diagnostic names do not map
directly. Editors can use ty's language server, but this change does not replace
any contributor's Pylance/Pyright installation. Contributors using those tools
may see different results from CI.

The migration is reasonable if simpler tooling and faster feedback justify the
documented coverage losses. Keep Pyright if preserving all of its existing
diagnostics is a requirement. A passing ty run alone is not evidence of parity.

## Sources

- [ty version policy](https://github.com/astral-sh/ty#version-policy)
- [Migration guide and diagnostic mappings](https://docs.astral.sh/ty/coming-from-mypy-or-pyright/)
- [Configuration reference](https://docs.astral.sh/ty/reference/configuration/)
- [Typing support tracker](https://github.com/astral-sh/ty/issues/1889)
- [Suppression syntax](https://docs.astral.sh/ty/suppression/)
- [Upstream hook at the pinned version](https://github.com/astral-sh/ty-pre-commit/blob/v0.0.105/.pre-commit-hooks.yaml)
