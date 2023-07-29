"""some versioning utils"""

import os
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from bumpversion.vcs import Git


def _deduce_python_helper():
    """Deduce the current version compatible with pypi version rules.

    Uses the following rules:
      - on the main branch, X.Y.Z
      - on the dev branch, X.Y.Z.devA
      - on a feature branch, X.Y.Z.devA+B.C
      - on a release branch, X.Y.Z+rcC
      - on a user's machine, X.Y.Z.devA+local
    where:
        X: Major, Y: Minor, Z: Subminor,
        A: Dev count, B: Branch, C: Build number
    """
    ver = from_file()

    def _format_dev(ver: str) -> str:
        ver = ver.replace("-", ".")
        left, right = ver.rsplit(".", 1)
        return left + right

    try:
        # BRANCH_NAME will be main or dev or PR-something
        branch = os.environ["BRANCH_NAME"].lower().replace("-", "")
        build_no = os.environ["BUILD_NUMBER"]
        if branch in {"main", "master"}:
            return ver.split("-")[0]
        if branch in {"dev", "develop"}:
            return _format_dev(ver)
        elif os.environ["CHANGE_BRANCH"].startswith("release/") or os.environ[
            "CHANGE_TARGET"
        ] in {"main", "master"}:
            return f'{ver.split("-")[0]}+rc.{build_no}'
        else:
            return f"{_format_dev(ver)}+{branch}.{build_no}"
    except KeyError:
        # We're in user-land
        return _format_dev(ver) + "+local"


def _deduce_helper():
    """Deduce the current version."""
    ver = from_file()
    try:
        # BRANCH_NAME will be the branch name or PR-something
        branch = os.environ["BRANCH_NAME"].replace('/','-')
        build_no = os.environ["BUILD_NUMBER"]
        if branch in {"main", "master"}:
            return ver.split("-")[0]
        if branch in {"dev", "develop"}:
            return ver
        elif os.getenv("CHANGE_BRANCH", "").startswith("release/") or os.getenv("CHANGE_TARGET", "") in {"main", "master"}:
            return f'{ver.split("-")[0]}-rc.{build_no}'
        else:
            return f'{ver.split("-")[0]}-{branch}.{build_no}'
    except KeyError:
        # We're in user-land
        return ver + "-local"


def deduce(is_python_package: Optional[bool] = None):
    """Deduce the current version

    Uses the following rules:
      - on the main branch, use version triad (without -dev.N)
      - on the dev branch, use version as-is (with -dev.N)
      - on a release branch, use version triad and add `-rc.N`
      - on a feature branch, use the PR and build numbers
      - on a user's machine, use the version cat with `-local`
    """
    return _deduce_python_helper() if is_python_package else _deduce_helper()


def from_file(filename: Optional[Path] = None) -> str:
    cfg = read_bumpversioncfg(filename)
    return cfg.get("bumpversion", "current_version")


def read_bumpversioncfg(filename: Optional[Path] = None) -> ConfigParser:
    """Parse a bumpversion config file"""
    filename = filename or Path(".bumpversion.cfg")
    b2v_config = ConfigParser()
    with open(filename, "rt", encoding="utf-8") as f:
        b2v_config.read_file(f)
    return b2v_config


def set_version(new_version: str, debug=True):
    """Set a specific version in case of oopsie"""
    b2v_config_file = Path(".bumpversion.cfg")

    if not debug:
        Git.assert_nondirty()
    b2v_config = read_bumpversioncfg(b2v_config_file)

    files = [
        (f, Path(f[len("bumpversion:file:") :]))
        for f in b2v_config.sections()
        if f.startswith("bumpversion:file:")
    ]

    current_version = b2v_config.get("bumpversion", "current_version")

    context = {"current_version": current_version, "new_version": new_version}

    for section, path in files:
        opts = b2v_config[section]
        search = opts.get("search", "{current_version}").format(**context)
        replace = opts.get("replace", "{new_version}").format(**context)

        with open(path, "rt") as f:
            file_contents_before = f.read()
            newline = f.newlines

        file_contents_after = file_contents_before.replace(search, replace)

        with open(path, "wt", encoding="utf-8", newline=newline) as f:
            f.write(file_contents_after)

        if not debug:
            Git.add_path(str(path))

    # Finally modify the bumpversion file
    b2v_config.set("bumpversion", "current_version", new_version)
    with open(b2v_config_file, "wt", encoding="utf-8") as f:
        b2v_config.write(f)

    if not debug:
        Git.add_path(str(b2v_config_file))
        Git.commit(f"Bump version: {current_version} → {new_version}", context)
        Git.tag(sign=False, name=f"v{new_version}", message=f"Release v{new_version}")


__all__ = (
    "deduce",
    "from_file",
    "set_version",
)
