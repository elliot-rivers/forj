from pathlib import Path

import click
import json

from .config import Project, configfile_name


@click.group(name="config")
def commands():
    """Configure forj for your project"""

@commands.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
)
@click.option(
    "--project-name",
    type=str,
    required=True,
    help="The name of your project; used for artifact naming (like docker containers). Prefer hyphens between words"
)
@click.option(
    "--chart-dir",
    type=str,
    default=None,
    help="Full path from root to helm chart directory (Default: None)",
)
@click.option(
    "--docker-image-path",
    type=str,
    default=None,
    help="Any STUFF you want between the docker registry and the image name/version (Default: '')",
)
def init(path, project_name, chart_dir, docker_image_path):
    """Initialize a new project

    Functionally,  this command creates a configuration file in the specified directory

    [PATH]: Optional, The root of the project to initialize (usually git root)
            Default: .
    """
    path = Path(path).resolve()
    click.secho(f"Initializing project {project_name} in {path}", fg="cyan")

    if (path / configfile_name).exists():
        click.secho("Error: This project is already initialized", fg="red")
        raise RuntimeError(f'Will not init new project in "{path}".')
    f = Project(
        name=project_name,
        chart_dir=chart_dir,
        docker_path=docker_image_path,
    )
    f.dump(path / configfile_name)

# The args here should be the same as above, except nothing required
@commands.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
)
@click.option(
    "--project-name",
    type=str,
    default=None,
    help="The name of your project (with hyphens between words)"
)
@click.option(
    "--chart-dir",
    type=str,
    default=None,
    help="Full path from root to helm chart directory (Default: None)",
)
@click.option(
    "--docker-image-path",
    type=str,
    default=None,
    help="Any STUFF you want between the docker registry and the image name/version (Default: '')",
)
def update(path, project_name, chart_dir, docker_image_path):
    """Update the configuration of an existing project

    [PATH]: Optional, The root of the project to initialize (usually git root)
            Default: .
    """
    path = Path(path).resolve()
    click.secho(f"Updating configuration of project {project_name} in {path}", fg="cyan")

    if not (path).exists():
        click.secho("Error: Cannot find a configuration in this directory", fg="red")
        raise RuntimeError(f'Cannot update config in "{path}".')

    update_args = {k: v for k, v in {
        'name': project_name,
        'chart_dir': chart_dir,
        'docker_path': docker_image_path,
    }.items() if k is not None}

    f = Project.update(path, **update_args)
    f.dump(path / configfile_name)

@commands.command()
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    default=".",
)
def upgrade(path):
    """Perform an interactive upgrade of your configuration file"""
    with open(path / configfile_name, "r") as f:
        data = json.load(f)

    missing_keys = Project.get_missing(set(data.keys()))

    if not missing_keys:
        click.secho("No upgrade necessary; all keys are present", fg="green")

    else:
        click.secho("Please enter values for the following missing keys:", fg="cyan")
        for key in missing_keys:
            value = click.prompt(key, type=str)
            data[key] = value
        Project(**data).dump(path / configfile_name)
        click.secho("Configuration updated!", fg="green")
