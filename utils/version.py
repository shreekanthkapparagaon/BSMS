import os
import sys
import subprocess


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_git_version():
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return version
    except:
        return None


def get_file_version():
    try:
        with open(resource_path("version.txt"), "r") as f:
            return f.read().strip()
    except:
        return "v1.0.0"


def get_version():
    return get_git_version() or get_file_version()