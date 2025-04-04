"""
Abstract Syntax Tree (AST) nodes for CEL expressions
"""

class Node:
    """Base class for all AST nodes"""
    
    def accept(self, visitor):
        """Accept a visitor to process this node"""
        method_name = f"visit_{self.__class__.__name__}"
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)

class Literal(Node):
    """Node representing a literal value (string, number, boolean, etc.)"""
    
    def __init__(self, value, value_type):
        self.value = value
        self.type = value_type  # 'int', 'float', 'bool', 'string', 'null'
    
    def __repr__(self):
        return f"Literal({self.value!r}, {self.type!r})"

class Identifier(Node):
    """Node representing a variable or field reference"""
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name!r})"

class MemberAccess(Node):
    """Node representing a field access on an object (obj.field)"""
    
    def __init__(self, object_expr, field_name):
        self.object = object_expr
        self.field = field_name
    
    def __repr__(self):
        return f"MemberAccess({self.object!r}, {self.field!r})"

class IndexAccess(Node):
    """Node representing an index access (array[idx] or map[key])"""
    
    def __init__(self, object_expr, index_expr):
        self.object = object_expr
        self.index = index_expr
    
    def __repr__(self):
        return f"IndexAccess({self.object!r}, {self.index!r})"

class UnaryOp(Node):
    """Node representing a unary operation (!, -, etc.)"""
    
    def __init__(self, operator, expr):
        self.operator = operator  # '!', '-'
        self.expr = expr
    
    def __repr__(self):
        return f"UnaryOp({self.operator!r}, {self.expr!r})"

class BinaryOp(Node):
    """Node representing a binary operation (&&, ||, +, -, etc.)"""
    
    def __init__(self, operator, left, right):
        self.operator = operator  # '+', '-', '*', '/', '&&', '||', etc.
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.operator!r}, {self.left!r}, {self.right!r})"

class TernaryOp(Node):
    """Node representing a ternary conditional (? :)"""
    
    def __init__(self, condition, true_expr, false_expr):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr
    
    def __repr__(self):
        return f"TernaryOp({self.condition!r}, {self.true_expr!r}, {self.false_expr!r})"

class FunctionCall(Node):
    """Node representing a function call"""
    
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments
    
    def __repr__(self):
        return f"FunctionCall({self.function!r}, {self.arguments!r})"

class ListExpr(Node):
    """Node representing a list literal"""
    
    def __init__(self, elements):
        self.elements = elements
    
    def __repr__(self):
        return f"ListExpr({self.elements!r})"

class MapExpr(Node):
    """Node representing a map literal"""
    
    def __init__(self, entries):
        self.entries = entries  # list of (key, value) tuples
    
    def __repr__(self):
        return f"MapExpr({self.entries!r})"
