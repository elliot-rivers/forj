"""Implementation of commands so click is real thin"""

import os
from pathlib import Path

import click
import docker

from forj.config import get_config
from forj.version.util import deduce as deduce_version


def get_docker_image(target: str):
    project_config, static_config = get_config()
    version = deduce_version()
    # This is kinda hacky and bespoke but like :shrug:
    suffix = "d" if target == "dev" else ""
    docker_path = f"{project_config.docker_path}/" if project_config.docker_path else ""
    image = f"{static_config.DOCKER_REGISTRY}/{docker_path}{project_config.name}"
    tag = f"{version}{suffix}"
    return (image, tag)


def build(target: str):
    image = ":".join(get_docker_image(target))
    docker_client = docker.from_env()

    click.echo(click.style("docker build", fg="bright_magenta"))
    click.echo(click.style(f"  target: {target}", fg="magenta"))
    click.echo(click.style(f"  image: {image}", fg="magenta"))

    _config, static_config = get_config()
    try:
        docker_client.images.build(
            path=str(Path()),
            rm=True,
            network_mode="host",
            target=target,
            buildargs={
                "docker_registry": static_config.DOCKER_REGISTRY,
            },
            tag=image,
        )
        click.echo(click.style("Success!", fg="green"))
    except docker.errors.BuildError as ex:
        click.echo(click.style("Build failure:", fg="red"))
        click.echo(ex.msg)
        for chunk in ex.build_log:
            click.echo(chunk)
        raise ex

    return image


__all__ = (
    "get_docker_image",
    "build",
)
