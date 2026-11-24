# ty migration follow-up

Track the four diagnostic gaps reproduced against Pyright 1.1.414 with ty
0.0.105 and 0.0.109. All four upstream issues were open when checked on 2026-11-24.
The implementation pins ty 0.0.105 to respect the repository's seven-day
release-age policy; keep these cases under review as that pin is updated.

Recheck these cases when upgrading ty. Close an item only after a released
version used by j2lint reports the expected diagnostic; an upstream issue being
closed alone is not sufficient. Record the verified ty version here and enable
any required opt-in rule in `pyproject.toml`.

Save each example to a temporary Python file and check it from the repository root:

```sh
uv run --group type --group test --group benchmark ty check --project . /tmp/ty_probe.py
```

The expected result is a diagnostic for the specific unsafe operation below.
An unrelated diagnostic or nonzero exit status does not establish coverage.

## Optional TypedDict key access

- [ ] [ty #2810: Diagnose access to a `NotRequired` TypedDict key](https://github.com/astral-sh/ty/issues/2810)

Expected: report that `options["path"]` may access a missing key.

```python
from typing import NotRequired, TypedDict


class Options(TypedDict):
    path: NotRequired[str]


def get_path(options: Options) -> str:
    return options["path"]
```

## Overlapping overload signatures

- [ ] [ty #103: Check for overlapping overloads](https://github.com/astral-sh/ty/issues/103)

Expected: report that the `bool` overload is shadowed by the preceding `int`
overload (`bool` is a subclass of `int`).

```python
from typing import overload


@overload
def convert(value: int) -> int: ...
@overload
def convert(value: bool) -> str: ...
def convert(value: int) -> int | str:
    return 1
```

## Unsafe abstract method calls through super()

- [ ] [ty #1923: Diagnose unsound `super()` calls to abstract methods with trivial bodies](https://github.com/astral-sh/ty/issues/1923)

Expected: report that `super().check()` calls an abstract method with no
implementation. Abstract methods with real implementations are a separate case.

```python
from abc import ABC, abstractmethod


class Base(ABC):
    @abstractmethod
    def check(self) -> int: ...


class Child(Base):
    def check(self) -> int:
        return super().check()
```

## Unhashable dictionary keys

- [ ] [ty #3781: Flag non-hashable objects in sets and dictionaries](https://github.com/astral-sh/ty/issues/3781)

Expected: report that a list cannot be used as a dictionary key because it is
unhashable.

```python
invalid_mapping = {[1, 2]: "value"}
```

See the [migration assessment](type-checking-migration.md) for retained coverage,
configuration choices, and validation results.
