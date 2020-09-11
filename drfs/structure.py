import inspect
from copy import copy
from pathlib import Path
from textwrap import indent
from typing import Union

from .path import DRPath, DRPathMixin


def _root_function(value):
    def foo(self):
        return self.root / value

    return foo


class _MetaTree(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name in ["root"] or attr_name.startswith("__"):
                new_attrs[attr_name] = attr_value
            elif isinstance(attr_value, (str, DRPathMixin)):
                new_attrs[attr_name] = property(_root_function(attr_value))
            elif isinstance(attr_value, type) and issubclass(attr_value, Tree):
                new_attrs[attr_name] = attr_value(attr_name)
            else:
                new_attrs[attr_name] = attr_value

        return type.__new__(mcs, name, bases, new_attrs)


class Tree(metaclass=_MetaTree):
    def __init__(self, root):
        self.root = DRPath(root)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        """Recursively set root in this and all child trees."""
        value = DRPath(value)
        self._root = value
        for node_name, node_value in self._get_nodes():
            if isinstance(node_value, Tree):
                node_value = copy(node_value)
                setattr(self, node_name, node_value)
                node_root = getattr(node_value, "__root__", node_name)
                node_value.root = self._root / node_root

    def _get_nodes(self):
        nodes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        nodes = [n for n in nodes if not n[0].startswith("__")]
        return nodes

    def __repr__(self):
        res = ""
        for node_name, node_value in self._get_nodes():
            if isinstance(node_value, DRPathMixin):
                if node_name == "root":
                    continue
                s = f"{node_name}: {node_value}\n"
            elif isinstance(node_value, Tree):
                s = f'{node_name}:\n{indent(str(node_value), "    ")}'
            else:
                s = ""
            res = f"{res}{s}"
        return res

    def add(self, key, value):
        if isinstance(value, (str, DRPathMixin)):
            value = _root_function(value)
        setattr(self, key, value)


# Use this as a type hint for paths for better autocomplete.
P = Union[Path, DRPathMixin]
