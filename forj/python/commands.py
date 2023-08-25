import click
#import docker

from .python import lint as python_lint


@click.group(name="python")
def commands():
    """Interact with your python repo"""


@commands.command()
@click.option(
    '--all',
    'tools',
    flag_value=['black','pylint'],
    help='Run all available linters',
    default=True,
)
@click.option(
    '--black',
    'tools',
    flag_value=['black'],
    help='Run the black linter',
)
@click.option(
    '--pylint',
    'tools',
    flag_value=['pylint'],
    help='Run the pylint linter',
)
@click.option(
    '--fix/--no-fix',
    default=False,
    help='Apply fixes',
)
def lint(tools, fix):
    """Lint your local codebase"""
    python_lint(tools, fix)
