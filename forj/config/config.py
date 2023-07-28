import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

configfile_name = Path(".forjproject")


def find_project_config():
    cur_dir = Path().resolve()
    for p in (cur_dir, *cur_dir.parents):
        if (p / configfile_name).is_file():
            return p / configfile_name
    raise FileNotFoundError("Can't find project configfile")


@dataclass
class Project:
    """A Forj project config file representation"""

    # The name of this project
    name: str
    # Location of helm chart (if applicable)
    chart_dir: str
    # STUFF between the docker registry and image name:
    # {DOCKER_REGYSTRY}/{self.docker_path}/{self.name}:{version}
    docker_path: str

    def dump(self, path):
        with open(path, "w") as f:
            json.dump(asdict(self), f)

    @staticmethod
    def load(path):
        with open(path, "r") as f:
            data = json.load(f)
        return Project(**data)

    @staticmethod
    def update(path, **kwargs):
        with open(path, "r") as f:
            data = json.load(f)
        return Project(**(data|kwargs))

    @classmethod
    def get_missing(cls, keys: {str}):
        """Return which dataclass fields are missing from a set of keys"""
        return set(cls.__dataclass_fields__.keys()) - set(keys)


@dataclass
class Static:
    DOCKER_REGISTRY = os.getenv(
        "DOCKER_REGISTRY", "docker.elliotrivers.rip"
    )


_project = None
_static = Static()


def get_config():
    global _project
    if not _project:
        try:
            _project = Project.load(find_project_config())
        except TypeError:
            raise TypeError("Unable to load project config. Maybe you need to `forj config init` or `for config upgrade`?")
    return _project, _static
