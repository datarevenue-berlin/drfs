# Filesystem imports:
import drfs.filesystems.local
import drfs.filesystems.memory
from drfs.filesystems.base import FILESYSTEMS
from drfs.filesystems.util import get_fs

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

try:
    import drfs.filesystems.azure_datalake
except ImportError:
    pass
