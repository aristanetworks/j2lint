# Notes

Notes regarding how to release

## Bumping version

In a branch specific for this, use the `bumpver` tool.
Install the maintainer dependencies first:

```
python -m pip install -e . --group dev
```

It is configured to update:
* pyproject.toml
* j2lint/__init__.py
* tests/test_cli.py (where a test verifies the version output)

For instance to bump a patch version:
```
bumpver update --patch
```

and for a minor version

```
bumpver update --minor
```

Tip: It is possible to check what the changes would be using `--dry`

```
bumpver update --minor --dry
```

## Creating release on Github

Create the release on Github with the appropriate tag `vx.x.x`

## Release notes

GitHub release notes are generated from `rn: ...` labels applied to merged pull requests.
The `pull-request-rn-labeler.yml` workflow applies these labels from pull request titles.

Use the repo's existing title style:

* `Feat: ...` for new features and enhancements
* `Fix: ...` for bug fixes
* `Doc: ...` for documentation
* `Refactor: ...` for refactoring
* `Bump: ...` for dependency or version bumps
* `Cut: ...` for removed features
* `CI: ...` for CI changes excluded from release notes
* `Test: ...` for test-only changes excluded from release notes

The generated labels are lowercase, for example `rn: feat`, `rn: fix`, and `rn: ci`.
Use `!` for breaking changes, for example `Fix!: remove deprecated behavior`.
Optional scopes can be included in titles, for example `Fix(rules): ignore raw block contents`.
Supported scopes are `j2lint`, `cli`, and `rules`.

## Manual TestPyPI release

The `release.yml` workflow can be triggered manually to publish a test build to TestPyPI.
Use a PEP 440 version without the leading `v` for `TESTPYPI_VERSION`, for example:

```
1.3.0.dev0
```

## Release version `x.x.x`

`x.x.x` is the version to be released

The primary release path is the `Tag & Release management` workflow.

1. Checkout the latest `devel` branch.
2. Bump the version and open a pull request.
   ```
   bumpver update --minor
   ```
3. Merge the version bump after CI passes.
4. Create a GitHub release with the tag `vx.x.x`, matching the package version.
5. The release workflow verifies the release tag matches the package version.
6. The release workflow builds the package and publishes it to TestPyPI.
7. The release workflow installs the TestPyPI package and runs the tests on Python 3.10, 3.11, 3.12, 3.13, and 3.14.
8. After the TestPyPI validation passes, the release workflow publishes the same distribution to PyPI.

Optional local package validation before creating the release:

```
python -m build
twine check dist/j2lint-x.x.x-py3-none-any.whl
```
