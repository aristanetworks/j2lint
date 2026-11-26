# ty migration follow-up

Diagnostic gaps verified with ty 0.0.105 and 0.0.109 against Pyright 1.1.414:

- [ ] Optional TypedDict key access: [ty#2810](https://github.com/astral-sh/ty/issues/2810)
- [ ] Overlapping overloads: [ty#103](https://github.com/astral-sh/ty/issues/103)
- [ ] Unsafe abstract method calls through `super()`: [ty#1923](https://github.com/astral-sh/ty/issues/1923)
- [ ] Unhashable dictionary keys: [ty#3781](https://github.com/astral-sh/ty/issues/3781)

Recheck on ty upgrades; close an item once the pinned version detects it.
