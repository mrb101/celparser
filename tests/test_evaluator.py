"""
Tests for the evaluator module
"""

import unittest
from celparser.parser import parse
from celparser.evaluator import evaluate
from celparser.errors import CELEvaluationError, CELTypeError, CELUndefinedError


class TestEvaluator(unittest.TestCase):
    """Test cases for the CEL evaluator"""

    def test_literal_evaluation(self):
        """Test evaluating literals"""
        # Integer
        result = evaluate(parse("42"))
        self.assertEqual(result, 42)

        # Float
        result = evaluate(parse("3.14"))
        self.assertEqual(result, 3.14)

        # String
        result = evaluate(parse('"hello"'))
        self.assertEqual(result, "hello")

        # Boolean
        result = evaluate(parse("true"))
        self.assertEqual(result, True)

        result = evaluate(parse("false"))
        self.assertEqual(result, False)

        # Null
        result = evaluate(parse("null"))
        self.assertEqual(result, None)

    def test_identifier_evaluation(self):
        """Test evaluating identifiers"""
        context = {"x": 42, "y": "hello"}

        # With context
        result = evaluate(parse("x"), context)
        self.assertEqual(result, 42)

        # Undefined variable with allow_undeclared_vars=True
        result = evaluate(parse("z"), context, allow_undeclared_vars=True)
        self.assertIsNone(result)

        # Undefined variable with allow_undeclared_vars=False
        with self.assertRaises(CELUndefinedError):
            evaluate(parse("z"), context, allow_undeclared_vars=False)

    def test_member_access_evaluation(self):
        """Test evaluating member access expressions"""
        context = {
            "obj": {"field": 42},
            "person": type("Person", (), {"name": "Alice"})(),
        }

        # Dictionary access
        result = evaluate(parse("obj.field"), context)
        self.assertEqual(result, 42)

        # Object attribute access
        result = evaluate(parse("person.name"), context)
        self.assertEqual(result, "Alice")

        # Undefined field with allow_undeclared_vars=True
        result = evaluate(
            parse("obj.unknown"), context, allow_undeclared_vars=True
        )
        self.assertIsNone(result)

        # Undefined field with allow_undeclared_vars=False
        with self.assertRaises(CELUndefinedError):
            evaluate(
                parse("obj.unknown"), context, allow_undeclared_vars=False
            )

        # Access on null with allow_undeclared_vars=True
        result = evaluate(
            parse("null.field"), context, allow_undeclared_vars=True
        )
        self.assertIsNone(result)

    def test_index_access_evaluation(self):
        """Test evaluating index access expressions"""
        context = {"arr": [1, 2, 3], "map": {"a": 1, "b": 2}, "i": 1}

        # Array access with literal index
        result = evaluate(parse("arr[1]"), context)
        self.assertEqual(result, 2)

        # Array access with variable index
        result = evaluate(parse("arr[i]"), context)
        self.assertEqual(result, 2)

        # Map access with string key
        result = evaluate(parse("map['a']"), context)
        self.assertEqual(result, 1)

        # Out of bounds access with allow_undeclared_vars=True
        result = evaluate(
            parse("arr[10]"), context, allow_undeclared_vars=True
        )
        self.assertIsNone(result)

        # Out of bounds access with allow_undeclared_vars=False
        with self.assertRaises(CELEvaluationError):
            evaluate(parse("arr[10]"), context, allow_undeclared_vars=False)

    def test_unary_operations(self):
        """Test evaluating unary operations"""
        context = {"x": 5, "b": True}

        # Logical NOT
        result = evaluate(parse("!b"), context)
        self.assertEqual(result, False)

        # Logical NOT on non-boolean
        result = evaluate(parse("!x"), context)
        self.assertEqual(result, False)  # Truthy value becomes False

        # Logical NOT on null
        result = evaluate(parse("!null"), context)
        self.assertEqual(result, True)  # null is falsy

        # Unary minus
        result = evaluate(parse("-x"), context)
        self.assertEqual(result, -5)

        # Unary minus on non-numeric value
        with self.assertRaises(CELTypeError):
            evaluate(parse("-b"), context)

    def test_binary_arithmetic_operations(self):
        """Test evaluating binary arithmetic operations"""
        context = {"x": 10, "y": 3, "s1": "hello", "s2": "world"}

        # Addition
        result = evaluate(parse("x + y"), context)
        self.assertEqual(result, 13)

        # String concatenation
        result = evaluate(parse("s1 + s2"), context)
        self.assertEqual(result, "helloworld")

        # Mixed type concatenation
        result = evaluate(parse("s1 + x"), context)
        self.assertEqual(result, "hello10")

        # Subtraction
        result = evaluate(parse("x - y"), context)
        self.assertEqual(result, 7)

        # Multiplication
        result = evaluate(parse("x * y"), context)
        self.assertEqual(result, 30)

        # String repetition
        result = evaluate(parse("'a' * 3"), context)
        self.assertEqual(result, "aaa")

        # Division
        result = evaluate(parse("x / y"), context)
        self.assertEqual(result, 10 / 3)

        # Division by zero
        with self.assertRaises(CELEvaluationError):
            evaluate(parse("x / 0"), context)

        # Modulo
        result = evaluate(parse("x % y"), context)
        self.assertEqual(result, 1)

        # Modulo by zero
        with self.assertRaises(CELEvaluationError):
            evaluate(parse("x % 0"), context)

        # Type error
        with self.assertRaises(CELTypeError):
            evaluate(parse("s1 - s2"), context)

    def test_binary_comparison_operations(self):
        """Test evaluating binary comparison operations"""
        context = {"x": 10, "y": 3, "z": 10, "s1": "hello", "s2": "world"}

        # Equality
        result = evaluate(parse("x == z"), context)
        self.assertTrue(result)

        result = evaluate(parse("x == y"), context)
        self.assertFalse(result)

        # Inequality
        result = evaluate(parse("x != y"), context)
        self.assertTrue(result)

        # Less than
        result = evaluate(parse("y < x"), context)
        self.assertTrue(result)

        # String comparison
        result = evaluate(parse("s1 < s2"), context)
        self.assertTrue(result)

        # Mixed type comparison
        with self.assertRaises(CELTypeError):
            evaluate(parse("x < s1"), context)

    def test_binary_logical_operations(self):
        """Test evaluating binary logical operations"""
        context = {"t": True, "f": False, "n": None}

        # Logical AND
        result = evaluate(parse("t && t"), context)
        self.assertTrue(result)

        result = evaluate(parse("t && f"), context)
        self.assertFalse(result)

        # Short-circuit AND
        result = evaluate(
            parse("f && unknown"), context, allow_undeclared_vars=True
        )
        self.assertFalse(result)  # Should not evaluate the right side

        # Logical OR
        result = evaluate(parse("t || f"), context)
        self.assertTrue(result)

        result = evaluate(parse("f || f"), context)
        self.assertFalse(result)

        # Short-circuit OR
        result = evaluate(
            parse("t || unknown"), context, allow_undeclared_vars=True
        )
        self.assertTrue(result)  # Should not evaluate the right side

        # Logical operations with non-boolean values
        result = evaluate(parse("1 && 2"), context)
        self.assertTrue(result)  # Both are truthy

        result = evaluate(parse("0 || 1"), context)
        self.assertTrue(result)  # Second is truthy

        # Null handling
        result = evaluate(parse("n || t"), context)
        self.assertTrue(result)

        result = evaluate(parse("n && t"), context)
        self.assertFalse(result)

    def test_ternary_operation(self):
        """Test evaluating ternary operations"""
        context = {"x": 10, "y": 20}

        # Basic ternary
        result = evaluate(parse("x < y ? 'less' : 'greater'"), context)
        self.assertEqual(result, "less")

        result = evaluate(parse("x > y ? 'less' : 'greater'"), context)
        self.assertEqual(result, "greater")

        # Nested ternary
        result = evaluate(
            parse("x < y ? (x == 0 ? 'zero' : 'positive') : 'negative'"),
            context,
        )
        self.assertEqual(result, "positive")

        # Short-circuit evaluation
        result = evaluate(
            parse("true ? x : unknown"), context, allow_undeclared_vars=True
        )
        self.assertEqual(result, 10)  # Should not evaluate the false branch

    def test_function_calls(self):
        """Test evaluating function calls"""
        context = {
            "greet": lambda name: f"Hello, {name}!",
            "arr": [1, 2, 3],
            "str": "hello",
        }

        # User-defined function
        result = evaluate(parse("greet('world')"), context)
        self.assertEqual(result, "Hello, world!")

        # Built-in function: size
        result = evaluate(parse("size(arr)"), context)
        self.assertEqual(result, 3)

        result = evaluate(parse("size(str)"), context)
        self.assertEqual(result, 5)

        # Built-in function: contains
        result = evaluate(parse("contains(arr, 2)"), context)
        self.assertTrue(result)

        result = evaluate(parse("contains(str, 'lo')"), context)
        self.assertTrue(result)

        # Built-in function: startsWith/endsWith
        result = evaluate(parse("startsWith(str, 'he')"), context)
        self.assertTrue(result)

        result = evaluate(parse("endsWith(str, 'lo')"), context)
        self.assertTrue(result)

        # Built-in function: type conversion
        result = evaluate(parse("int('42')"), context)
        self.assertEqual(result, 42)

        result = evaluate(parse("string(42)"), context)
        self.assertEqual(result, "42")

        # Unknown function
        with self.assertRaises(CELEvaluationError):
            evaluate(parse("unknown()"), context)

    def test_list_expressions(self):
        """Test evaluating list expressions"""
        context = {"x": 1, "y": 2}

        # Empty list
        result = evaluate(parse("[]"), context)
        self.assertEqual(result, [])

        # List with literals
        result = evaluate(parse("[1, 2, 3]"), context)
        self.assertEqual(result, [1, 2, 3])

        # List with expressions
        result = evaluate(parse("[x, y, x + y]"), context)
        self.assertEqual(result, [1, 2, 3])

    def test_map_expressions(self):
        """Test evaluating map expressions"""
        context = {"x": 1, "y": 2}

        # Empty map
        result = evaluate(parse("{}"), context)
        self.assertEqual(result, {})

        # Map with literal keys and values
        result = evaluate(parse("{'a': 1, 'b': 2}"), context)
        self.assertEqual(result, {"a": 1, "b": 2})

        # Map with expressions
        result = evaluate(parse("{'x': x, 'sum': x + y}"), context)
        self.assertEqual(result, {"x": 1, "sum": 3})

        # Non-hashable key
        with self.assertRaises(CELTypeError):
            evaluate(parse("{[1]: 'value'}"), context)

    def test_complex_expressions(self):
        """Test evaluating complex expressions"""
        context = {
            "person": {
                "name": "Alice",
                "age": 30,
                "address": {"city": "New York", "zip": "10001"},
                "contacts": [
                    {"type": "email", "value": "alice@example.com"},
                    {"type": "phone", "value": "555-1234"},
                ],
            },
            "isAdmin": True,
        }

        # Complex property access
        result = evaluate(parse("person.address.city"), context)
        self.assertEqual(result, "New York")

        # Complex array and map access
        result = evaluate(parse("person.contacts[0].value"), context)
        self.assertEqual(result, "alice@example.com")

        # Complex conditional
        result = evaluate(
            parse(
                "isAdmin && person.age > 18 ? 'Welcome, ' + person.name : 'Access denied'"
            ),
            context,
        )
        self.assertEqual(result, "Welcome, Alice")

        # Complex calculation with multiple operations
        result = evaluate(
            parse(
                "person.name.startsWith('A') && (person.age >= 30 || person.address.city == 'New York')"
            ),
            context,
        )
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
