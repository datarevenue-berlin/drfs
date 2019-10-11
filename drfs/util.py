
def prepend_scheme(scheme, path):
    """Prepend scheme to a remote path.

    Scheme is only prepended if not already present

    Parameters
    ----------
    scheme: str
        a scheme like 'file', 's3' or 'gs'
    path: str
        path which will possibly get a scheme prependend

    Returns
    -------
    full_path: str
    """
    if scheme == '':
        scheme = 'file'
    if path.startswith(scheme):
        return path
    else:
        path = path[1:] if path.startswith('/') else path
        return '{}://{}'.format(scheme, path)


def coerce_path(arg):
    warnings.warn("coerce_path was renamed to path2str.", DeprecationWarning)
    return path2str(arg)


def path2str(arg):
    """Convert arg into its string representation.

    This is only done if arg is subclass of PurePath
    """
    if issubclass(type(arg), PurePath):
        return str(arg)
    return arg


def any2path(x, cls=None):
    if isinstance(x, PurePath):
        return x
    if isinstance(x, str):
        cls = cls or _get_path_class(x)
        return cls(x)
    if isinstance(x, (list, tuple, set)):
        if len(x) == 0:
            return x
        cls = cls or _get_path_class(next(iter(x)))  # get first element
        return type(x)(map(cls, x))  # return the same type of iterable
    raise TypeError("Cannot convert type {} to Path.".format(
        type(x).__name__))


def _get_path_class(path):
    if get_filesystem(path, rtype='class').is_remote:
        return RemotePath
    else:
        return Path
