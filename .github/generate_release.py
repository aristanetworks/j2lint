# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the MIT license
# that can be found in the LICENSE file.
# ruff: noqa: INP001
"""Generate GitHub release note categories.

This script writes `.github/release.yml` in the format used by GitHub's
automatically generated release notes.
"""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
from typing import TypeAlias

YamlValue: TypeAlias = str | list["YamlValue"] | dict[str, "YamlValue"]

BASE_SCOPES = [
    "j2lint",
    "cli",
    "rules",
]

# The shared release-note labeler replaces comma-separated PR scopes with "|"
# before creating the GitHub label.
SCOPES = [
    *BASE_SCOPES,
    *["|".join(scopes) for scope_count in range(2, len(BASE_SCOPES) + 1) for scopes in permutations(BASE_SCOPES, scope_count)],
]

EXCLUDED_TYPES = ["test", "ci"]
BREAKING_TYPES = ["feat", "fix", "cut", "revert", "refactor", "bump"]


def labels_for(commit_type: str, *, breaking: bool = False) -> list[str]:
    """Build release-note labels for a conventional commit type."""
    suffix = "!" if breaking else ""
    labels = [f"rn: {commit_type}({scope}){suffix}" for scope in SCOPES]
    labels.append(f"rn: {commit_type}{suffix}")
    return labels


def build_release_config() -> YamlValue:
    """Build the GitHub release-note configuration."""
    exclude_labels = [label for commit_type in EXCLUDED_TYPES for label in labels_for(commit_type)]
    breaking_labels = [label for commit_type in BREAKING_TYPES for label in labels_for(commit_type, breaking=True)]

    return {
        "changelog": {
            "exclude": {"labels": exclude_labels},
            "categories": [
                {"title": "Breaking Changes", "labels": breaking_labels},
                {"title": "New features and enhancements", "labels": labels_for("feat")},
                {"title": "Fixed issues", "labels": labels_for("fix")},
                {"title": "Documentation", "labels": labels_for("doc")},
                {"title": "Other Changes", "labels": ["*"]},
            ],
        },
    }


def format_scalar(value: str) -> str:
    """Format a scalar for this repository's simple YAML needs."""
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return str(value)


def dump_yaml(value: YamlValue, *, indent: int = 0) -> list[str]:
    """Dump the subset of YAML needed by the release configuration."""
    prefix = " " * indent
    lines: list[str] = []

    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(dump_yaml(item, indent=indent + 2))
            else:
                lines.append(f"{prefix}{key}: {format_scalar(item)}")
        return lines

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                item_lines = dump_yaml(item, indent=indent + 2)
                first_line = item_lines[0].lstrip()
                lines.append(f"{prefix}- {first_line}")
                lines.extend(item_lines[1:])
            else:
                lines.append(f"{prefix}- {format_scalar(item)}")
        return lines

    lines.append(f"{prefix}{format_scalar(value)}")
    return lines


def main() -> None:
    """Generate `.github/release.yml`."""
    release_file = Path(__file__).with_name("release.yml")
    release_file.write_text("\n".join(dump_yaml(build_release_config())) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
