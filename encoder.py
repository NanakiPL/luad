# -*- coding: utf-8 -*-

from collections import OrderedDict
from collections.abc import Sequence, Mapping

from pprint import pprint

class Encoder():
    show_repr = False
    break_list = None
    
    _pretty = False
    _indent = None
    _depth = 0
    
    _ids = set()
    
    def indent(self):
        if self._indent is None:
            return ''
        return self._indent * self._depth
    
    def __init__(self, indent = None, show_repr = False, break_list = 5, sorted = True):
        if indent is True:
            self._pretty = True
            self._indent = '\t'
        elif isinstance(indent, int):
            self._pretty = True
            self._indent = ' ' * indent
        
        self.break_list = break_list
        self.show_repr = show_repr
        self.sorted = sorted
        
    def sort(self, obj):
        if self.sorted:
            return sorted(obj, key = keyfunc)
        return obj
    
    def encode(self, obj):
        if isinstance(obj, tuple):
            res = []
            for v in obj:
                res += [self._encode(v)]
            return ', '.join(res)
        return self._encode(obj)
            
    def _encode(self, obj, show_repr = True):
        if obj is None:
            return 'nil'
        elif obj is True:
            return 'true'
        elif obj is False:
            return 'false'
        elif isinstance(obj, int):
            return int.__str__(obj)
        elif isinstance(obj, float):
            return float.__repr__(obj)
        
        elif isinstance(obj, str):
            return self._str(obj)
        elif isinstance(obj, (list, tuple)):
            return self._list(obj)
        elif isinstance(obj, set):
            return self._list(self.sort(list(obj)))
        elif isinstance(obj, dict):
            return self._dict(obj)
            
        elif isinstance(obj, Sequence):
            return self._list(list(obj))
        elif isinstance(obj, Mapping):
            return self._dict(dict(obj))
        
        if self.show_repr and show_repr:
            return 'nil--[[{!r}]]'.format(obj)
        return 'nil'
        
    def _str(self, obj):
        return repr(obj)
    
    def _list(self, obj):
        if len(obj) == 0:
            return '{}'
        
        objid = id(obj)
        if objid in self._ids:
            raise ValueError("Circular reference detected")
        
        _break = False
        if self.break_list is not None and len(obj) > self.break_list:
            _break = True
        
        self._ids.add(objid)
        self._depth += 1
        res = []
        for o in obj:
            res += [self._encode(o)]
            if isinstance(o, (dict, list, tuple)):
                _break = True
        self._ids.remove(objid)
        
        if self._pretty and _break:
            s2 = ',\n' + self.indent()
            self._depth -= 1
            s1 = '\n' + self.indent()
            return '{' + s2[1:] + s2.join(res) + s1 + '}'
        else:
            self._depth -= 1
            return '{' + ', '.join(res) + '}'
    
    def _dict(self, obj):
        keys = obj.keys()
        if len(keys) == 0: return '{}'
        
        objid = id(obj)
        if objid in self._ids:
            raise ValueError("Circular reference detected")
        
        if not isinstance(obj, OrderedDict):
            keys = self.sort(keys)
        
        self._ids.add(objid)
        self._depth += 1
        res = []
        for k in keys:
            res += ['[{}] = {}'.format(self._encode(k, show_repr = False), self._encode(obj[k]))]
        self._ids.remove(objid)
        
        if self._pretty:
            s2 = ',\n' + self.indent()
            self._depth -= 1
            s1 = '\n' + self.indent()
            return '{' + s2[1:] + s2.join(res) + s1 + '}'
        else:
            self._depth -= 1
            return '{' + ', '.join(res) + '}'

# Hacky way to sort different types
def keyfunc(k):
    if isinstance(k, int):
        return '{:010d}'.format(k)
    else:
        return ':' + repr(k)