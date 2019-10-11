import inspect
from pathlib import Path
from textwrap import indent
from typing import Union

from .path import DRPath, DRPathMixin


class _MetaTree(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name in ['root'] or attr_name.startswith('__'):
                new_attrs[attr_name] = attr_value
                continue
            elif isinstance(attr_value, (str, DRPathMixin)):
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


class Tree(metaclass=_MetaTree):
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
            if isinstance(node_value, Tree):
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
            if isinstance(node_value, DRPathMixin):
                if node_name == 'root':
                    continue
                s = f'{node_name}: {node_value}'
            elif isinstance(node_value, Tree):
                s = f'{node_name}:\n{indent(str(node_value), "    ")}'
            else:
                s = ''
            res = f'{res}{s}\n'
        return res


# Use this as a type hint for paths for better autocomplete.
P = Union[Path, DRPathMixin]
