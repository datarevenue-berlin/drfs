import os

from drfs.filesystems import get_fs


def glob(path, opts=None):
    """Filesystem-agnostic glob."""
    return get_fs(path, opts=opts).glob(path)


def exists(path, opts=None):
    """Filesystem-agnostic exists."""
    return get_fs(path, opts=opts).exists(path)


def open(path, mode, opts=None):
    """Filesystem-agnostic open."""
    return get_fs(path, opts=opts).open(path, mode)


def mv(src, dst, opts=None):
    """Filesystem-agnostic mv."""
    return get_fs(src, opts=opts).mv(src, dst)


def makedirs(path, *args, opts=None, **kwargs):
    """Filesystem-agnostic makedirs."""
    return get_fs(path, opts=opts).makedirs(path, *args, **kwargs)


def rmdir(path, opts=None):
    """Filesystem-agnostic rmdir."""
    return get_fs(path, opts=opts).rmdir(path)


def savefig(path, *args, opts=None, **kwargs):
    """Filesystem-agnostic savefig."""
    import matplotlib.pyplot as plt

    path = str(path)  # in case it's pathlib object
    fmt = os.path.splitext(path)[1][1:]
    with open(path, "wb", opts=opts) as f:
        plt.savefig(f, format=fmt, *args, **kwargs)
