import click
import docker

from .docker import shell as docker_shell
from .docker import test as docker_test
from .impl import build as build_impl
from .impl import get_docker_image


@click.group(name="docker")
def commands():
    """Build, test, and manage your docker artifacts"""


@commands.command()
@click.option(
    "--target",
    type=str,
    default="dev",
    help='A Dockerfile target to build (Default: "dev")',
)
def build(target):
    """Build a docker container"""
    # TODO we should reevaluate this on scale-out since multi-stage builds are not universal
    build_impl(target)


@commands.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
)
@click.option(
    "--target",
    type=str,
    default="dev",
    help='A Dockerfile target to run (Default: "dev")',
)
@click.argument("cmd", nargs=-1, type=click.UNPROCESSED)
def shell(target, cmd):
    """Run a command in a docker container (default `/bin/bash`)"""
    cmd = cmd or ["/bin/bash"]
    image = ":".join(get_docker_image(target))

    click.secho("docker run", fg="bright_magenta")
    click.secho(f"  image: {image}", fg="magenta")
    click.secho(f'  command: {" ".join(cmd)}', fg="magenta")

    docker_shell(image, cmd)


@commands.command()
@click.option(
    "--target",
    type=str,
    default="dev",
    help='A Dockerfile target to build (Default: "dev")',
)
def push(target: str):
    """Push a docker image built from a particular TARGET"""
    image, tag = get_docker_image(target)
    docker_client = docker.from_env()

    click.secho("docker push", fg="bright_magenta")
    click.secho(f"  image: {image}:{tag}", fg="magenta")

    docker_client.images.push(image, tag)


@commands.command()
@click.argument("mark_expr", type=str, default="not integration")
@click.option("--target", type=str, default="dev")
def test(mark_expr: str, target: str):
    """Run scripts/run-tests.sh in a built container

    MARK_EXPR is whatever that means in context of run-tests.sh

    This command automatically builds your container for you if it hasn't been already
    """
    # Make sure this has been built
    image = build_impl(target)
    docker_test(image, mark_expr)


@commands.command()
@click.option("--target", type=str, default="dev")
def get_image(target: str):
    """Spit out the computed name for a docker image"""
    image_name = ":".join(get_docker_image(target))
    click.echo(image_name)
