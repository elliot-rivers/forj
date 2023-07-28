from pathlib import Path

import click

from forj.config import get_config

from . import helm


class Helm:
    """
    Helm utilities
    Requires a chart_dir, set either in your `forj init` command or with this class.

    Args:
        chart_dir (str): path to your charts. Will override the chart dir (if any) set in your forj init.

    Raises:
        ValueError if a chart dir is not set at forj init or with this class.
    """

    def __init__(self, chart_dir: str):
        project_config, _ = get_config()
        self.chart_dir: str = (
            Path(chart_dir) if chart_dir else Path(project_config.chart_dir)
        )

        if not self.chart_dir:
            raise ValueError(
                "must set a chart option in your `forj helm` command or forj init."
            )


@click.group(name="helm")
@click.option(
    "--chart-dir",
    type=str,
    default=None,
    help="override the chart dir in your forj init.",
)
@click.pass_context
def commands(ctx, chart_dir):
    """Various commands for helm charts.

    You must indicate where your charts are located either by:

    \b
    1) setting the chart_dir during forj init
    2) override the init chart dir in a forj helm command: `forj helm --chart-dir "./my-chart/" lint`

    """

    ctx.obj = Helm(chart_dir)


@commands.command()
@click.option(
    "--skip-refresh",
    "-s",
    is_flag=True,
    help="when updating dependecies during packaging, skip refresh",
)
@click.option(
    "--skip-auto-version",
    is_flag=True,
    help="When packaging, don't change the chart version to the locally deduced value",
)
@click.option(
    "--skip-auto-app-version",
    is_flag=True,
    help="When packaging, don't change the chart app version to the locally deduced value",
)
@click.pass_context
def package(ctx, skip_refresh, skip_auto_version, skip_auto_app_version):
    """Package a chart directory into a chart archive"""

    helm.package(
        ctx.obj.chart_dir,
        skip_refresh,
        (not skip_auto_version),
        (not skip_auto_app_version),
    )


@commands.command()
@click.pass_context
def push(ctx):
    """Push a helm chart to the chartmuseum"""

    helm.push(ctx.obj.chart_dir)


@commands.command()
@click.pass_context
def lint(ctx):
    """lint a helm chart"""

    helm.lint(ctx.obj.chart_dir)
