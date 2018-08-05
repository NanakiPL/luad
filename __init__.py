# -*- coding: utf-8 -*-

from .decoder import parse as loads

def load(fp, *, return_only = False, dont_raise = False, **kwargs):
    return loads(fp.read(), return_only = return_only, dont_raise = dont_raise, **kwargs)

__all__ = ['load', 'loads']