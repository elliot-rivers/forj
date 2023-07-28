import bumpversion.cli
import click

from .util import deduce, set_version


@click.group(name="version")
def commands():
    """Manage your project's version"""
    pass


@commands.command()
@click.option(
    "--python",
    "-p",
    "is_python_package",
    is_flag=True,
    help="Return a python package compatible version string",
)
def get(is_python_package):
    """Get the deduced project version based on context

    On a user's machine, this will always be "VERSION-local(d)"

    In a release pipeline, it will contain `-rc`.
    In a develop pipeline, it will contain `-dev`
    In a main pipeline, it will be the raw version
    In all other pipelines, it will be a `-PR` version
    """
    click.echo(deduce(is_python_package=is_python_package))


@commands.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def bump(args):
    """Passthrough alias for `bump2version`"""
    args = [*args, "--serialize", "{major}.{minor}.{patch}-dev.{dev}"]
    bumpversion.cli.main(args)


@commands.command(hidden=True)
@click.option(
    "--debug", "-d", is_flag=True, help="Debug mode; be verbose and make no changes"
)
def dev(debug: bool):
    """Bumps the dev version (for use by CI)"""
    args = ["dev"]
    if debug:
        args += ["--dry-run", "--verbose", "--allow-dirty"]
    bumpversion.cli.main(args)


@commands.command(hidden=True)
@click.option(
    "--debug", "-d", is_flag=True, help="Debug mode; be verbose and make no changes"
)
@click.option(
    "--python",
    "-p",
    "is_python_package",
    is_flag=True,
    help="Return a python package compatible version string",
)
def release(debug: bool, is_python_package: bool):
    """Removes the `-dev` field from the current version (for use by CI)"""
    new_version = deduce(is_python_package=is_python_package)
    set_version(new_version, debug=debug)


@commands.command(name="set")
@click.argument("new_version", type=str)
@click.option(
    "--debug", "-d", is_flag=True, help="Debug mode; be verbose and make no changes"
)
def set_(new_version: str, debug: bool):
    """Set the version to something specific, in case of oopsie"""
    set_version(new_version, debug=debug)
