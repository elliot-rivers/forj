

import os
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Collection, Optional

import click

from forj.config import get_config
from forj.docker.impl import build as docker_build
from forj.docker import shell as docker_shell


def lint(tools: [str], fix: bool):
    # first make sure we have a current dev docker container
    image = docker_build('dev')

    project_config, _ = get_config()

    if 'black' in tools:
        _lint_black(project_config.python_module_path, image, fix)
    if 'pylint' in tools:
        _lint_pylint(project_config.python_module_path, image, fix)


def _lint_black(src_path: str, image: str, fix: bool):
    click.secho(f"Running linter 'black' in image: {image}", fg="bright_magenta")
    cmd = ['python3', '-m', 'black', src_path]
    if not fix:
        cmd += ['--diff']
    docker_shell(image, cmd, workdir='/app')


def _lint_pylint(src_path: str, image: str, fix: bool):
    click.secho(f"Running linter 'pylint' in image: {image}", fg="bright_magenta")
    if fix:
        click.secho(f"Oops pylint doesn't actually do fixing", fg="bright_yellow")
    cmd = ['python3', '-m', 'pylint', src_path]
    docker_shell(image, cmd, workdir='/app')
