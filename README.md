# drfs
[![PyPI](https://img.shields.io/pypi/v/drfs.svg)](https://pypi.org/project/drfs)

* Free software: MIT license
* Documentation: https://drfs.readthedocs.io

## File systems

All filesystems defined in this package should:
- accept full paths in methods like `ls` etc.
  (_full_ means: including protocol and all other parts of path)
- return full paths or their lists from methods like `ls` etc.
- paths returned from methods like `ls`  should be `DRPath` objects
  (`DRPath` is our version of `pathlib.Path` supporting remote paths
  and few other features)

Above functionalities are implemented in `FileSystemBase` class. When adding
a new filesystem, one should subclass from it and set an underlying backend
filesystem as `fs_cls` attribute (see existing implementations).

### Relation to fsspec
[fsspec](https://filesystem-spec.readthedocs.io/en/latest/?badge=latest)
is an attempt to unify interfaces of various filesystems. It also serves
as a tool that `dask` uses to support them.

drfs doesn't agree with fsspec in (at least) one assumption: in fsspec
methods like `ls` return paths without protocol. That's why we can't use
classes that adhere to fsspec directly.

However, such classes can (and should) be used as backends for filesystems
defined here in drfs. This way we ensure that paths handled by drfs can
also be handled by `dask` (because importing a backend filesystem that adheres
to fsspec makes it available for Dask).

>For example, `drfs.filesystems.s3.S3Filesystem`
>uses `s3fs.S3FileSystem` as backend which adheres to fsspec.


## Features

* TODO



