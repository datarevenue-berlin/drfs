from pathlib import Path


# What Path() returns depends on the OS, that's why we're not subclassing Path
# directly.
class DRPath(type(Path())):
    @property
    def istemplate(self):
        s = str(self)
        return '{' in s and '}' in s
    
    @property
    def iswildcard(self):
        return '*' in self._parts
    
    @property
    def flag(self):
        return self / '_SUCCESS'
    
    def format(self, *args, **kwargs):
        return DRPath(str(self).format(*args, **kwargs))
