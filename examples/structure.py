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
structure = Structure('/root')

# You can update root directory at any time. All paths will reflect this.
structure.root = 's3://bucket'

# This is what the structure looks like now (obtained by `print(structure)`).
"""
_root: s3://bucket
data: s3://bucket/data
dataset: s3://bucket/data/processed/{date}/*
migrated:
    _root: s3://bucket/migrated
    stuff: s3://bucket/migrated/stf
    things: s3://bucket/migrated/thngs
processed: s3://bucket/data/processed
raw: s3://bucket/raw
report:
    _root: s3://bucket/rprt
    evaluation: s3://bucket/rprt/eval
"""
