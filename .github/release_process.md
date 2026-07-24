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

## Manual TestPyPI release

The `release.yml` workflow can be triggered manually to publish a test build to TestPyPI.
Use a PEP 440 version without the leading `v` for `TESTPYPI_VERSION`, for example:

```
1.3.0.dev0
```

## Release version `x.x.x`

TODO - make this a workflow

`x.x.x` is the version to be released

This is to be executed at the top of the repo

1. Checkout the latest version of devel with the correct tag for the release
2. [Optional] Clean dist if required
3. Build the package locally
   ```
   python -m build
   ```
4. Check the package with `twine` (replace with your version)
    ```
    twine check dist/j2lint-x.x.x-py3-none-any.whl
    ```
5. Upload the package to test.pypi
    ```
    twine upload -r testpypi dist/j2lint-x.x.x.*
    ```
6. Verify the package by installing it in a local venv and checking it installs
   and run correctly (run the tests)
   ```
   # In a brand new venv
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple  --no-cache j2lint
   ```
7. Upload the package to pypi
    ```
    twine upload dist/j2lint-x.x.x.*
    ```
8. Like 5 but for normal pypi
   ```
   # In a brand new venv
   pip install j2lint
   ```
