"""A really ~stunted~ bespoke docker API

We may want to exhibit standard, comforting docker behavior sometimes --
e.g. seeing all the trash it prints out -- rather than use the fancy API.

So here's this gross module to do that.

Sorry.
"""

import os
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Collection, Optional

import click


def build(tag: str, target: Optional[str] = None):
    cmd = [
        "docker",
        "build",
        "--network=host",
        "-t",
        tag,
    ]
    if target:
        cmd += [f"--target={target}"]
    cmd += ["."]
    click.secho(" ".join(cmd), fg="bright_magenta")
    run(" ".join(cmd), shell=True, check=True)


def shell(image: str, cmd: Collection[str], workdir=None):
    """Run a docker shell"""
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-it",
        "-v",
        f"{Path().resolve()}:/app",
        "--network",
        "host",
        "--env-file",
        ".env.example",
    ]
    if workdir:
        docker_cmd += ['--workdir', workdir]
    docker_cmd += [image, *cmd]

    try:
        run(" ".join(docker_cmd), shell=True, check=True)
    except CalledProcessError:
        click.secho("Container failed to run with provided arguments:", fg="red")
        click.secho(f'    {" ".join(cmd)}', fg="red")


def test(image: str, mark_expr: str):
    """Do run-tests in a docker shell"""
    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        "host",
        "--env-file",
        ".env.example",
        image,
        "scripts/run-tests.sh",
        f'"{mark_expr}"',
    ]
    run(" ".join(cmd), shell=True, check=True)


__all__ = (
    "build",
    "shell",
    "test",
)
