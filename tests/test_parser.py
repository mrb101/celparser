"""
Tests for the parser module
"""

import unittest
from celparser.parser import parse
from celparser.ast import (
    Literal,
    Identifier,
    MemberAccess,
    IndexAccess,
    UnaryOp,
    BinaryOp,
    TernaryOp,
    FunctionCall,
    ListExpr,
    MapExpr,
)
from celparser.errors import CELSyntaxError


class TestParser(unittest.TestCase):
    """Test cases for the CEL parser"""

    def test_literal_expressions(self):
        """Test parsing literals"""
        # Integer
        ast = parse("42")
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, 42)
        self.assertEqual(ast.type, "int")

        # Float
        ast = parse("3.14")
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, 3.14)
        self.assertEqual(ast.type, "float")

        # String
        ast = parse('"hello"')
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, "hello")
        self.assertEqual(ast.type, "string")

        # Boolean (true)
        ast = parse("true")
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, True)
        self.assertEqual(ast.type, "bool")

        # Boolean (false)
        ast = parse("false")
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, False)
        self.assertEqual(ast.type, "bool")

        # Null
        ast = parse("null")
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.value, None)
        self.assertEqual(ast.type, "null")

    def test_identifier_expressions(self):
        """Test parsing identifiers"""
        ast = parse("variable_name")
        self.assertIsInstance(ast, Identifier)
        self.assertEqual(ast.name, "variable_name")

    def test_member_access_expressions(self):
        """Test parsing member access expressions"""
        ast = parse("obj.field")
        self.assertIsInstance(ast, MemberAccess)
        self.assertIsInstance(ast.object, Identifier)
        self.assertEqual(ast.object.name, "obj")
        self.assertEqual(ast.field, "field")

        # Chained member access
        ast = parse("obj.field1.field2")
        self.assertIsInstance(ast, MemberAccess)
        self.assertIsInstance(ast.object, MemberAccess)
        self.assertEqual(ast.field, "field2")
        self.assertEqual(ast.object.field, "field1")
        self.assertIsInstance(ast.object.object, Identifier)
        self.assertEqual(ast.object.object.name, "obj")

    def test_index_access_expressions(self):
        """Test parsing index access expressions"""
        ast = parse("arr[0]")
        self.assertIsInstance(ast, IndexAccess)
        self.assertIsInstance(ast.object, Identifier)
        self.assertEqual(ast.object.name, "arr")
        self.assertIsInstance(ast.index, Literal)
        self.assertEqual(ast.index.value, 0)

        # Expression as index
        ast = parse("arr[i + 1]")
        self.assertIsInstance(ast, IndexAccess)
        self.assertIsInstance(ast.index, BinaryOp)
        self.assertEqual(ast.index.operator, "+")

    def test_unary_operations(self):
        """Test parsing unary operations"""
        # Logical NOT
        ast = parse("!expr")
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.operator, "!")
        self.assertIsInstance(ast.expr, Identifier)
        self.assertEqual(ast.expr.name, "expr")

        # Unary minus
        ast = parse("-42")
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.operator, "UNARY_MINUS")
        self.assertIsInstance(ast.expr, Literal)
        self.assertEqual(ast.expr.value, 42)

    def test_binary_operations(self):
        """Test parsing binary operations"""
        # Addition
        ast = parse("a + b")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "+")
        self.assertIsInstance(ast.left, Identifier)
        self.assertEqual(ast.left.name, "a")
        self.assertIsInstance(ast.right, Identifier)
        self.assertEqual(ast.right.name, "b")

        # Comparison
        ast = parse("a == b")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "==")

        # Logical operators
        ast = parse("a && b")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "&&")

        ast = parse("a || b")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "||")

    def test_operator_precedence(self):
        """Test operator precedence"""
        # Multiplication has higher precedence than addition
        ast = parse("a + b * c")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "+")
        self.assertIsInstance(ast.right, BinaryOp)
        self.assertEqual(ast.right.operator, "*")

        # Parentheses override precedence
        ast = parse("(a + b) * c")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "*")
        self.assertIsInstance(ast.left, BinaryOp)
        self.assertEqual(ast.left.operator, "+")

        # Complex expression
        ast = parse("a && b || c")
        self.assertIsInstance(ast, BinaryOp)
        self.assertEqual(ast.operator, "||")
        self.assertIsInstance(ast.left, BinaryOp)
        self.assertEqual(ast.left.operator, "&&")

    def test_ternary_expressions(self):
        """Test parsing ternary expressions"""
        ast = parse("condition ? true_expr : false_expr")
        self.assertIsInstance(ast, TernaryOp)
        self.assertIsInstance(ast.condition, Identifier)
        self.assertEqual(ast.condition.name, "condition")
        self.assertIsInstance(ast.true_expr, Identifier)
        self.assertEqual(ast.true_expr.name, "true_expr")
        self.assertIsInstance(ast.false_expr, Identifier)
        self.assertEqual(ast.false_expr.name, "false_expr")

        # Nested ternaries
        ast = parse("c1 ? (c2 ? a : b) : c")
        self.assertIsInstance(ast, TernaryOp)
        self.assertIsInstance(ast.true_expr, TernaryOp)

    def test_function_calls(self):
        """Test parsing function calls"""
        ast = parse("func()")
        self.assertIsInstance(ast, FunctionCall)
        self.assertIsInstance(ast.function, Identifier)
        self.assertEqual(ast.function.name, "func")
        self.assertEqual(len(ast.arguments), 0)

        # Function call with arguments
        ast = parse("func(a, 1, true)")
        self.assertIsInstance(ast, FunctionCall)
        self.assertEqual(len(ast.arguments), 3)
        self.assertIsInstance(ast.arguments[0], Identifier)
        self.assertEqual(ast.arguments[0].name, "a")
        self.assertIsInstance(ast.arguments[1], Literal)
        self.assertEqual(ast.arguments[1].value, 1)
        self.assertIsInstance(ast.arguments[2], Literal)
        self.assertEqual(ast.arguments[2].value, True)

        # Method call
        ast = parse("obj.method()")
        self.assertIsInstance(ast, FunctionCall)
        self.assertIsInstance(ast.function, MemberAccess)
        self.assertEqual(ast.function.field, "method")

    def test_list_expressions(self):
        """Test parsing list expressions"""
        ast = parse("[]")
        self.assertIsInstance(ast, ListExpr)
        self.assertEqual(len(ast.elements), 0)

        # List with elements
        ast = parse("[1, 'a', true]")
        self.assertIsInstance(ast, ListExpr)
        self.assertEqual(len(ast.elements), 3)
        self.assertIsInstance(ast.elements[0], Literal)
        self.assertEqual(ast.elements[0].value, 1)
        self.assertIsInstance(ast.elements[1], Literal)
        self.assertEqual(ast.elements[1].value, "a")
        self.assertIsInstance(ast.elements[2], Literal)
        self.assertEqual(ast.elements[2].value, True)

    def test_map_expressions(self):
        """Test parsing map expressions"""
        ast = parse("{}")
        self.assertIsInstance(ast, MapExpr)
        self.assertEqual(len(ast.entries), 0)

        # Map with entries
        ast = parse("{'a': 1, 'b': true}")
        self.assertIsInstance(ast, MapExpr)
        self.assertEqual(len(ast.entries), 2)

        key1, value1 = ast.entries[0]
        self.assertIsInstance(key1, Literal)
        self.assertEqual(key1.value, "a")
        self.assertIsInstance(value1, Literal)
        self.assertEqual(value1.value, 1)

        key2, value2 = ast.entries[1]
        self.assertIsInstance(key2, Literal)
        self.assertEqual(key2.value, "b")
        self.assertIsInstance(value2, Literal)
        self.assertEqual(value2.value, True)

    def test_complex_expressions(self):
        """Test parsing complex expressions"""
        ast = parse("a && b || c.field[0] + func(1, 'text') ? true : false")
        self.assertIsInstance(ast, TernaryOp)
        self.assertIsInstance(ast.condition, BinaryOp)  # || operation
        self.assertIsInstance(ast.condition.left, BinaryOp)  # && operation
        self.assertIsInstance(ast.condition.right, BinaryOp)  # + operation
        self.assertIsInstance(ast.condition.right.left, IndexAccess)
        self.assertIsInstance(ast.condition.right.right, FunctionCall)
        self.assertIsInstance(ast.true_expr, Literal)
        self.assertEqual(ast.true_expr.value, True)
        self.assertIsInstance(ast.false_expr, Literal)
        self.assertEqual(ast.false_expr.value, False)

    def test_invalid_expressions(self):
        """Test parsing invalid expressions"""
        with self.assertRaises(CELSyntaxError):
            parse("a +")  # Incomplete expression

        with self.assertRaises(CELSyntaxError):
            parse("(a + b")  # Unclosed parenthesis

        with self.assertRaises(CELSyntaxError):
            parse("a ? b")  # Incomplete ternary

        with self.assertRaises(CELSyntaxError):
            parse("func(a,)")  # Invalid function call


if __name__ == "__main__":
    unittest.main()
