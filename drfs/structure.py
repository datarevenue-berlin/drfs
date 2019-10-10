from textwrap import indent
import inspect
from pathlib import Path

from .path import DRPath
from typing import Union


class _MetaTree(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name in ['root'] or attr_name.startswith('__'):
                new_attrs[attr_name] = attr_value
                continue
            elif isinstance(attr_value, (str, DRPath)):
                new_attrs[attr_name] = mcs._make_property(attr_value)
            elif isinstance(attr_value, type):
                new_attrs[attr_name] = attr_value(attr_name)
            else:
                new_attrs[attr_name] = attr_value
        
        return type.__new__(mcs, name, bases, new_attrs)
    
    @classmethod
    def _make_property(mcs, value):
        def foo(self):
            return self.root / value
        
        foo = property(foo)
        return foo


class _BaseTree:
    def __init__(self, root):
        self.root = DRPath(root)
    
    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, value):
        value = DRPath(value)
        self._root = value
        for node_name, node_value in self._get_nodes():
            if isinstance(node_value, _BaseTree):
                node_root = getattr(node_value, '__root__', node_name)
                node_value.root = self._root / node_root
    
    def _get_nodes(self):
        nodes = inspect.getmembers(
            self,
            lambda a: not (inspect.isroutine(a)),
        )
        nodes = [n for n in nodes if not n[0].startswith('__')]
        return nodes
    
    def __str__(self):
        res = ""
        for node_name, node_value in self._get_nodes():
            if isinstance(node_value, DRPath):
                if node_name == 'root':
                    continue
                s = f'{node_name}: {node_value}'
            elif isinstance(node_value, _BaseTree):
                s = f'{node_name}:\n{indent(str(node_value), "    ")}'
            else:
                s = ''
            res = f'{res}{s}\n'
        return res


class Tree(_BaseTree, metaclass=_MetaTree):
    """Subclass from this to create your file structure."""
    pass


P = Union[Path, DRPath]


# ------- EXAMPLE --------


class _ExampleStructure(Tree):
    # This is the simplest way of defining a path.
    raw = 'raw'
    
    # Use P type hint for better autocomplete. Use DRPath type to reuse path.
    data: P = DRPath('data')
    
    # You can reuse paths defined earlier as DRPaths.
    processed = data / 'processed'
    
    # Of course, you can also have templates and wildcards.
    dataset = processed / '{date}' / '*'
    
    # Nest another tree to group paths. Name of tree will be used as parent
    # folder.
    class migrated(Tree):
        things: P = 'thngs'
        stuff: P = 'stf'
    
    # You can override name of parent folder by defining __root__ attribute.
    class report(Tree):
        __root__ = 'rprt'
        evaluation = 'eval'


# Instantiate the defined class giving it a name of root directory.
_example_structure = _ExampleStructure('ROOT')
# You can update root directory at any time. All paths will reflect this.
_example_structure.root = 'NEW_ROOT'

# This is what the structure looks like now:
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
