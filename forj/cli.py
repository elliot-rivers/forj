from os import chdir

import click

from .docker import commands as docker_commands
from .helm import commands as helm_commands
from .config import commands as config_commands
from .util import find_project_root
from .version import commands as version_commands


@click.group()
@click.pass_context
def main(ctx):
    """forj build tool

    Dig around and ask subcommands for help with `forj <command> --help`
    """
    try:
        chdir(find_project_root())
    except FileNotFoundError:
        # Don't warn users about their initfile if they're trying to configure it rn
        if ctx.invoked_subcommand != "config":
            click.secho(
                "Warning: can't find project initfile. (Have you run `forj config init` in your project root?)",
                fg="yellow",
            )


main.add_command(docker_commands)
main.add_command(config_commands)
main.add_command(version_commands)
main.add_command(helm_commands)
