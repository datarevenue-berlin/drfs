def prepend_scheme(scheme, path):
    """Prepend scheme to a remote path.

    Scheme is only prepended if not already present

    Parameters
    ----------
    scheme: str
        a scheme like 'file', 's3' or 'gs'
    path: str
        path which will possibly get a scheme prepended

    Returns
    -------
    full_path: str
    """
    if scheme == "":
        scheme = "file"
    if path.startswith(scheme + "://"):
        return path
    else:
        path = path[1:] if path.startswith("/") else path
        return f"{scheme}://{path}"


def remove_scheme(path, raise_=True):
    """Remove scheme from a path

    Parameters
    ----------
    path: str
        path with scheme prepended e.g. s3fs://bucket/key/to/file.txt
    raise_: bool
        if set to True (default) raise a ValueError if the path does not contain a
        scheme else just return path as it was given if no scheme is detected.

    Returns
    -------
    simple_path: str
        path without scheme
    """
    try:
        scheme, rest = path.split("://")
    except ValueError as e:
        if raise_:
            if "is not iterable" in str(e):
                raise ValueError(f"Could not detect any scheme in path: {path}")
            raise
        else:
            rest = path
    return rest
