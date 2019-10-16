import drfs.filesystems.local
from drfs.filesystems.base import FILESYSTEMS, get_fs

try:
    import drfs.filesystems.gcs
except ImportError:
    pass

try:
    import drfs.filesystems.s3
except ImportError:
    pass

try:
    import drfs.filesystems.azure_blob
except ImportError:
    pass

