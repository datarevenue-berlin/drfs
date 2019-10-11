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
    if scheme == '':
        scheme = 'file'
    if path.startswith(scheme):
        return path
    else:
        path = path[1:] if path.startswith('/') else path
        return f'{scheme}://{path}'
