# -*- coding: utf-8 -*-

from .encoder import Encoder
def dumps(obj, *, indent = None, **kwargs):
    return Encoder(indent = indent, **kwargs).encode(obj)
    
def dump(obj, fp, *, indent = None, **kwargs):
    fp.write(dumps(obj, indent = indent, **kwargs))



from .decoder import parse as loads
def load(fp, *, resolve_names = True, dont_raise = False, **kwargs):
    return loads(fp.read(), resolve_names = resolve_names, dont_raise = dont_raise, **kwargs)

__all__ = ['dump', 'dumps', 'load', 'loads']