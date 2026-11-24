#!/usr/bin/env python3
"""Set the Cargo package version for a release tag.

Stable tags (``vX.Y.Z``) must equal the package version already in
``Cargo.toml``; they never rewrite it. Dev tags
(``vX.Y.Z-dev.<commits>.g<short hash>``) rewrite only the checkout copy of
``Cargo.toml`` so build artifacts carry the pre-release version.

Usage:
    set-release-version.py TAG [--manifest Cargo.toml] [--check]
    set-release-version.py --print-version [Cargo.toml]
    set-release-version.py --dev-tag X.Y.Z COUNT SHORT_HASH
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STABLE_TAG = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
DEV_TAG = re.compile(
    r"^v(?P<base>\d+\.\d+\.\d+)-dev\.(?P<count>\d+)\.g(?P<hash>[0-9a-f]+)$"
)
CORE_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
PACKAGE_VERSION_LINE = re.compile(r'^(\s*version\s*=\s*)"[^"]+"')


class ReleaseVersionError(ValueError):
    """A tag or manifest cannot be used for a release."""


def read_package_version(path: Path) -> str:
    """Return the version in the [package] table, ignoring dependency versions."""
    in_package = False
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_package = stripped == "[package]"
            continue
        if not in_package:
            continue
        match = re.match(r'^version\s*=\s*"([^"]+)"', stripped)
        if match:
            return match.group(1)
    raise ReleaseVersionError(f"no package version in {path}")


def write_package_version(path: Path, version: str) -> None:
    """Rewrite only the [package] version line, preserving surrounding text."""
    lines = path.read_text().splitlines(keepends=True)
    in_package = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_package = stripped == "[package]"
            continue
        if not in_package:
            continue
        match = PACKAGE_VERSION_LINE.match(line)
        if match:
            lines[index] = f'{match.group(1)}"{version}"{line[match.end():]}'
            path.write_text("".join(lines))
            return
    raise ReleaseVersionError(f"no package version in {path}")


def release_version(tag: str, current: str) -> str:
    """Return the version a tag should build with, or refuse the tag.

    A stable tag is a no-op and must match ``current`` exactly. A dev tag
    must use the next patch of ``current`` and yields the tag without ``v``.
    """
    stable = STABLE_TAG.fullmatch(tag)
    if stable:
        version = stable.group("version")
        if version != current:
            raise ReleaseVersionError(
                f"stable tag {tag} does not match Cargo.toml version {current}"
            )
        return version

    dev = DEV_TAG.fullmatch(tag)
    if dev:
        expected = next_patch_version(current)
        if dev.group("base") != expected:
            raise ReleaseVersionError(
                f"dev tag {tag} does not use next patch version {expected}"
            )
        return tag[1:]

    raise ReleaseVersionError(f"unsupported release tag: {tag}")


def next_patch_version(version: str) -> str:
    """Return ``version`` with the patch component incremented."""
    match = CORE_VERSION.fullmatch(version)
    if not match:
        raise ReleaseVersionError(f"not a stable version: {version}")
    return f"{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}"


def dev_tag(version: str, count: int, short_hash: str) -> str:
    """Return the dev tag for a base version, commit count and short hash."""
    if count < 0:
        raise ReleaseVersionError(f"invalid commit count: {count}")
    if not re.fullmatch(r"[0-9a-f]+", short_hash):
        raise ReleaseVersionError(f"invalid short hash: {short_hash}")
    return f"v{next_patch_version(version)}-dev.{count}.g{short_hash}"


def version_key(version: str) -> tuple[tuple[int, ...], tuple]:
    """Return a SemVer precedence key (build metadata is ignored)."""
    core, _, prerelease = version.split("+", 1)[0].partition("-")
    if not CORE_VERSION.fullmatch(core):
        raise ReleaseVersionError(f"not a version: {version}")
    numbers = tuple(int(part) for part in core.split("."))
    if not prerelease:
        return numbers, (1,)
    identifiers = tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in prerelease.split(".")
    )
    return numbers, (0, identifiers)


def set_release_version(tag: str, path: Path) -> str:
    """Validate ``tag`` against ``path`` and write a dev version when needed."""
    current = read_package_version(path)
    version = release_version(tag, current)
    if version != current:
        write_package_version(path, version)
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", nargs="?", help="release tag to validate")
    parser.add_argument("--manifest", default="Cargo.toml", type=Path)
    parser.add_argument("--check", action="store_true", help="validate without writing")
    parser.add_argument(
        "--print-version", action="store_true", help="print the current package version"
    )
    parser.add_argument(
        "--dev-tag",
        nargs=3,
        metavar=("VERSION", "COUNT", "SHORT_HASH"),
        help="print the dev tag for a base version and commit",
    )
    args = parser.parse_args(argv)

    try:
        if args.dev_tag:
            version, count, short_hash = args.dev_tag
            print(dev_tag(version, int(count), short_hash))
            return 0
        if args.print_version:
            print(read_package_version(args.tag and Path(args.tag) or args.manifest))
            return 0
        if not args.tag:
            parser.error("tag is required unless --print-version or --dev-tag is used")

        current = read_package_version(args.manifest)
        version = release_version(args.tag, current)
        if version != current and not args.check:
            write_package_version(args.manifest, version)
        print(version)
        return 0
    except (ReleaseVersionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
