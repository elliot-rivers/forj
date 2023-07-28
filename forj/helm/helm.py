import os
from subprocess import run

import click
import requests

from forj.version.util import deduce as deduce_version

"""helm utils"""


def dependency_update(chart_dir, skip_refresh):
    """update helm dependencies"""

    if skip_refresh:
        cmd = f"helm dependency update {chart_dir} --skip-refresh"
    else:
        cmd = f"helm dependency update {chart_dir}"
    click.secho(cmd, fg="yellow")
    run(cmd, shell=True, check=True)


def package(chart_dir, skip_refresh, auto_version=True, auto_app_version=False):
    """Package a chart directory into a chart archive"""

    # update dependencies
    dependency_update(chart_dir=chart_dir, skip_refresh=skip_refresh)

    # lint chart dir
    lint(chart_dir)

    version_args = ""
    if auto_version:
        version_args += f"--version {deduce_version()} "
    if auto_app_version:
        version_args += f"--app-version {deduce_version()}"

    # package chart dir
    cmd = f"helm package {chart_dir} -d {chart_dir.parent} {version_args}"
    click.secho(cmd, fg="magenta")
    run(cmd, shell=True, check=True)


def push(chart_dir):
    """Push a packaged chart to chart museum"""

    try:
        chartmuseum_creds = os.environ["CHARTMUSEUM_CREDS"]
        chart_repo = os.environ["CHART_REPO"]
    except KeyError:
        raise KeyError(
            "Missing CHART_REPO or CHARTMUSEUM_CREDS environment variable(s)."
        )

    chartmuseum_uname, chartmuseum_pwd = chartmuseum_creds.split(":")

    try:
        packaged_chart = list(chart_dir.parent.glob(f"{chart_dir.name}*.tgz"))[0]
    except IndexError:
        click.secho(
            "Could not find packaged chart. Have you run forj helm package?",
            fg="yellow",
        )

    url = f"{chart_repo}/api/charts"
    with open(packaged_chart, "rb") as f:
        data = f.read()

    response = requests.post(
        url,
        data=data,
        auth=(chartmuseum_uname, chartmuseum_pwd),
    )
    click.secho(response.status_code, fg="green")


def lint(chart_dir):
    """lint a helm chart"""

    cmd = f"helm lint {chart_dir}"
    click.secho(cmd, fg="green")
    run(cmd, shell=True, check=True)
