# -*- coding: utf-8  -*-
from luaparser import ast, astnodes

def parse(str, return_only = False, dont_raise = False):
    tree = ast.parse(str)
    return ASTConverter(return_only=return_only, dont_raise=dont_raise).convert(tree)

class ASTConverter:
    __names = {}
    
    def __init__(self, return_only = False, dont_raise = False):
        self.return_only = return_only
        self.dont_raise = dont_raise
    
    def convert(self, node):
        if isinstance(node, astnodes.Node):
            return getattr(self, '_' + node.__class__.__name__)(node)
        else:
            raise ValueError('Non-node ({})'.format(node))
        
    def __raise(self, e):
        if self.dont_raise: return e
        raise e
    
    # Variables
    def __set_Name(self, name, value):
        if isinstance(value, astnodes.Node):
            self.__names[name.id] = {'node': value}
        else:
            self.__names[name.id] = {'converted': value}
    
    def __get_Name(self, name, context = None):
        try:
            v = self.__names[name.id]
            try:
                return v['converted']
            except KeyError:
                v['converted'] = self.convert(self.__names[name.id]['node'])
                return v['converted']
        except KeyError:
            return None # undefined vars return nil in Lua
    
    # Base
    def _Chunk(self, node):
        return self.convert(node.body)
    def _Block(self, node):
        for n in node.body:
            if isinstance(n, astnodes.Return):
                return self.convert(n)
            if isinstance(n, astnodes.Node):
                getattr(self, '_' + n.__class__.__name__)(n)
    
    def _Return(self, node):
        res = []
        for r in node.values:
            res += [self.convert(r)]
        if len(res) > 1:
            return tuple(res)
        return res[0]
    
    # Assigns
    def _Assign(self, node):
        if self.return_only: return
        for i,name in enumerate(node.targets):
            if isinstance(name, astnodes.Name):
                self.__set_Name(name, node.values[i])
    
    _LocalAssign = _Assign
    def _LocalAssign(self, node):
        return self._Assign(node)
        
    # Bad values
    def _Function(self, node):
        e = self.__raise(BadValue('Unsuppoted type: function', node))
        if isinstance(node.name, astnodes.Name):
            self.__set_Name(node.name, e)
        elif isinstance(node.name, astnodes.Index):
            self.__raise(BadValue('Table indexes aren\'t supported yet', node))
        
    _LocalFunction = _Function
    def _AnonymousFunction(self, node):
        return self.__raise(BadValue('Unsuppoted type: function', node))
        
    # Variables
    def _Name(self, node, getValue = False):
        if getValue: return node.id
        return self.__get_Name(node)
    def _Index(self, node):
        return self.__raise(BadValue('Table indexes aren\'t supported yet', node))
    
    # Types and values
    def _Nil(self, node):
        return None
    def _TrueExpr(self, node):
        return True
    def _FalseExpr(self, node):
        return False
    def _Number(self, node):
        return node.n
    def _String(self, node):
        return node.s
    def _Table(self, node):
        res = {}
        m = 0
        for field in node.fields:
            if isinstance(field.key, astnodes.Name):
                key = field.key.id
            else:
                key = self.convert(field.key)
            value = self.convert(field.value)
            res[key] = value
            if isinstance(key, int): m = max(m, key)
        
        if list(res.keys()) == list(range(1, m+1)):
            return [v for k,v in sorted(res.items())]
        return res
    
    # Arithmetic Operators
    def _AddOp(self, node):
        return self.convert(node.left) + self.convert(node.right)
    def _SubOp(self, node):
        return self.convert(node.left) - self.convert(node.right)
    def _MultOp(self, node):
        return self.convert(node.left) * self.convert(node.right)
    def _FloatDivOp(self, node):
        return self.convert(node.left) / self.convert(node.right)
    def _FloorDivOp(self, node):
        return self.convert(node.left) // self.convert(node.right)
    def _ModOp(self, node):
        return self.convert(node.left) % self.convert(node.right)
    def _ExpoOp(self, node):
        return self.convert(node.left) ** self.convert(node.right)
    
    # Unary Operators
    def _UMinusOp(self, node):
        return -self.convert(node.operand)
    def _UBNotOp(self, node):
        return not self.convert(node.operand)
        
class BadValue(ValueError):
    def __init__(self, msg, node = None):
        self.msg = msg
        self.node = node
    def __str__(self):
        return self.msg
    def __repr__(self):
        return 'BadValue({})'.format(repr(self.msg))