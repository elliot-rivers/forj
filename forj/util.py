from .config import find_project_config


def find_project_root():
    return find_project_config().parent
