"""
This module serves as an example of file structure definition in a project.
"""
from drfs import DRPath, P, Tree


class Structure(Tree):
    # This is the simplest way of defining a path.
    # All paths will be instances of DRPath even if they were defined as str.
    raw = 'raw'
    
    # Use P type hint for better autocomplete. Use DRPath type to reuse path.
    data: P = DRPath('data')
    
    # You can reuse paths defined earlier as DRPaths.
    processed = data / 'processed'
    
    # Of course, you can also have templates and wildcards.
    dataset = processed / '{date}' / '*'
    
    # Nest another tree to group paths. Name of class will be used as parent
    # folder name.
    class migrated(Tree):
        things: P = 'thngs'
        stuff: P = 'stf'
    
    # You can override name of parent folder by defining __root__ attribute.
    class report(Tree):
        __root__ = 'rprt'
        evaluation = 'eval'


# Instantiate defined class giving it a name of root directory.
structure = Structure('ROOT')

# You can update root directory at any time. All paths will reflect this.
structure.root = 'NEW_ROOT'

# This is what the structure looks like now (obtained by `str(structure)`).
"""
_root: NEW_ROOT
data: NEW_ROOT/data
dataset: NEW_ROOT/data/processed/{date}/*
migrated:
    _root: NEW_ROOT/migrated
    stuff: NEW_ROOT/migrated/stf
    things: NEW_ROOT/migrated/thngs

processed: NEW_ROOT/data/processed
raw: NEW_ROOT/raw
report:
    _root: NEW_ROOT/rprt
    evaluation: NEW_ROOT/rprt/eval
"""
