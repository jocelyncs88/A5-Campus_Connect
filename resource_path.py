import os
import sys


def resource_path(relative_path):
    """Return an absolute path to a resource, compatible with normal Python and bundled exe."""
    if os.path.isabs(relative_path):
        return relative_path

    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


def asset_path(*parts):
    """Return a full asset path from the project root or bundled resource path."""
    return resource_path(os.path.join(*parts))
