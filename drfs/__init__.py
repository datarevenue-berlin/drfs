# -*- coding: utf-8 -*-

"""Top-level package for drfs."""
__author__ = """Data Revenue GmbH"""
__email__ = "alan@datarevenue.com"

import confuse

config = confuse.LazyConfig("drfs", __name__)

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from .path import DRPath
from .structure import Tree, P
