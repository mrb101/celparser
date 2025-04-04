"""
Evaluator for CEL expressions
"""

from typing import Dict, Any, Optional, Callable
from celparser.ast import (
    Node,
    Literal,
    Identifier,
    MemberAccess,
    IndexAccess,
    BinaryOp,
    TernaryOp,
    FunctionCall,
)
from celparser.errors import CELEvaluationError, CELTypeError, CELUndefinedError


class Evaluator:
    """
    Evaluator for CEL expressions
    """

    def __init__(
        self,
        context: Optional[Dict[str, Any]] = None,
        allow_undeclared_vars: bool = True,
    ):
        """
        Initialize the evaluator

        Args:
            context (dict): A dictionary of variable values
            allow_undeclared_vars (bool): Whether to allow undeclared variables
        """
        self.context: Dict[str, Any] = context or {}
        self.allow_undeclared_vars = allow_undeclared_vars

        # Built-in functions
        self.functions: Dict[str, Callable[..., Any]] = {
            "size": self.func_size,
            "contains": self.func_contains,
            "startsWith": self.func_startsWith,
            "starts_with": self.func_starts_with,
            "endsWith": self.func_endsWith,
            "ends_with": self.func_ends_with,
            "matches": self.func_matches,
            "int": self.func_int,
            "float": self.func_float,
            "bool": self.func_bool,
            "string": self.func_string,
            "type": self.func_type,
        }

    def evaluate(self, node: Node) -> Any:
        """
        Evaluate an AST node

        Args:
            node: The AST node to evaluate

        Returns:
            The result of evaluating the node
        """
        return node.accept(self)

    def generic_visit(self, node: Node) -> Any:
        """Default visitor method for unsupported node types"""
        raise CELEvaluationError(
            f"Unsupported node type: {type(node).__name__}"
        )

    def visit_Literal(self, node: Literal) -> Any:
        """Evaluate a literal node"""
        return node.value

    def visit_Identifier(self, node: Identifier) -> Any:
        """Evaluate an identifier node"""
        name = node.name

        # Handle boolean literals
        if name == "True":
            return True
        elif name == "False":
            return False
        elif name == "null":
            return None

        if name in self.context:
            return self.context[name]

        if self.allow_undeclared_vars:
            return None

        raise CELUndefinedError(f"Undefined variable: {name}")

    def visit_MemberAccess(self, node: MemberAccess) -> Any:
        """Evaluate a member access node (obj.field)"""
        obj = self.evaluate(node.object)

        if obj is None:
            if self.allow_undeclared_vars:
                return None
            raise CELUndefinedError(
                f"Cannot access field '{node.field}' on null"
            )

        if isinstance(obj, dict):
            if node.field in obj:
                return obj[node.field]
            elif self.allow_undeclared_vars:
                return None
            else:
                raise CELUndefinedError(f"Object has no field: {node.field}")

        try:
            return getattr(obj, node.field)
        except (AttributeError, TypeError):
            if self.allow_undeclared_vars:
                return None
            raise CELUndefinedError(f"Object has no field: {node.field}")

    def visit_IndexAccess(self, node: IndexAccess) -> Any:
        """Evaluate an index access node (obj[index])"""
        obj = self.evaluate(node.object)
        index = self.evaluate(node.index)

        if obj is None:
            return None

        try:
            return obj[index]
        except (TypeError, KeyError, IndexError):
            if self.allow_undeclared_vars:
                return None
            raise CELEvaluationError(f"Cannot access index {index} on {obj}")

    def visit_UnaryOp(self, node):
        """Evaluate a unary operation node"""
        # Get the value of the expression
        value = self.evaluate(node.expr)

        if node.operator == "!":
            # Logical NOT
            if value is None:
                return True
            return not bool(value)

        elif node.operator == "UNARY_MINUS":
            # Unary minus
            if value is None:
                return None

            # Check if the value is boolean (including True, False literals)
            if isinstance(value, bool):
                raise CELTypeError("Cannot apply unary minus to bool")

            if not isinstance(value, (int, float)):
                raise CELTypeError(
                    f"Cannot apply unary minus to {type(value).__name__}"
                )

            return -value

        raise CELEvaluationError(f"Unknown unary operator: {node.operator}")

    def visit_BinaryOp(self, node: BinaryOp) -> Any:
        """Evaluate a binary operation node"""
        # Evaluate left side first
        left = self.evaluate(node.left)

        # Short-circuit evaluation for logical operators
        if node.operator == "&&":
            # Logical AND
            if not left:
                return False
            return bool(self.evaluate(node.right))

        elif node.operator == "||":
            # Logical OR
            if left:
                return True
            return bool(self.evaluate(node.right))

        # Evaluate right side for non-short-circuit operators
        right = self.evaluate(node.right)

        # Handle operations
        if node.operator == "+":
            # Addition or string concatenation
            if left is None or right is None:
                return None

            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left + right

            raise CELTypeError(
                f"Cannot add {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == "-":
            # Subtraction
            if left is None or right is None:
                return None

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left - right

            raise CELTypeError(
                f"Cannot subtract {type(right).__name__} from {type(left).__name__}"
            )

        elif node.operator == "*":
            # Multiplication
            if left is None or right is None:
                return None

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left * right

            # String repetition: "a" * 3 = "aaa"
            if isinstance(left, str) and isinstance(right, int):
                return left * right

            raise CELTypeError(
                f"Cannot multiply {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == "/":
            # Division
            if left is None or right is None:
                return None

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                if right == 0:
                    raise CELEvaluationError("Division by zero")
                return left / right

            raise CELTypeError(
                f"Cannot divide {type(left).__name__} by {type(right).__name__}"
            )

        elif node.operator == "%":
            # Modulo
            if left is None or right is None:
                return None

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                if right == 0:
                    raise CELEvaluationError("Modulo by zero")
                return left % right

            raise CELTypeError(
                f"Cannot apply modulo to {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == "==":
            # Equality
            return left == right

        elif node.operator == "!=":
            # Inequality
            return left != right

        elif node.operator == "<":
            # Less than
            if left is None or right is None:
                return False

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left < right
            elif isinstance(left, str) and isinstance(right, str):
                return left < right

            raise CELTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == "<=":
            # Less than or equal
            if left is None or right is None:
                return False

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left <= right
            elif isinstance(left, str) and isinstance(right, str):
                return left <= right

            raise CELTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == ">":
            # Greater than
            if left is None or right is None:
                return False

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left > right
            elif isinstance(left, str) and isinstance(right, str):
                return left > right

            raise CELTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}"
            )

        elif node.operator == ">=":
            # Greater than or equal
            if left is None or right is None:
                return False

            if isinstance(left, (int, float)) and isinstance(
                right, (int, float)
            ):
                return left >= right
            elif isinstance(left, str) and isinstance(right, str):
                return left >= right

            raise CELTypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__}"
            )

        raise CELEvaluationError(f"Unknown binary operator: {node.operator}")

    def visit_TernaryOp(self, node: TernaryOp) -> Any:
        """Evaluate a ternary conditional node (cond ? true_expr : false_expr)"""
        condition = self.evaluate(node.condition)

        if condition:
            return self.evaluate(node.true_expr)
        else:
            return self.evaluate(node.false_expr)

    def visit_FunctionCall(self, node: FunctionCall) -> Any:
        """Evaluate a function call node"""
        # Check if this is a method call (object.method())
        if isinstance(node.function, MemberAccess):
            obj_node = node.function.object
            method_name = node.function.field
            obj = self.evaluate(obj_node)

            # Evaluate arguments
            args = [self.evaluate(arg) for arg in node.arguments]

            # Check if this is a string method that we need to handle with our built-in functions
            if isinstance(obj, str):
                if method_name == "startsWith" or method_name == "starts_with":
                    return self.func_starts_with(obj, *args)
                elif method_name == "endsWith" or method_name == "ends_with":
                    return self.func_ends_with(obj, *args)
                elif method_name == "contains":
                    return self.func_contains(obj, *args)
                elif method_name == "matches":
                    return self.func_matches(obj, *args)

            # Check if the object has the method
            if obj is not None:
                if isinstance(obj, dict) and method_name in obj:
                    method = obj[method_name]
                    if callable(method):
                        return method(*args)
                elif hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    if callable(method):
                        return method(*args)
        else:
            # Not a method call, evaluate function and arguments
            func = self.evaluate(node.function)
            args = [self.evaluate(arg) for arg in node.arguments]

            # Handle built-in functions referenced by name
            if isinstance(func, str) and func in self.functions:
                # Built-in function
                return self.functions[func](*args)

            # Handle function directly in context
            if callable(func):
                # User-provided function
                return func(*args)

            # Special case for identifiers that should match built-in functions
            if (
                isinstance(node.function, Identifier)
                and node.function.name in self.functions
            ):
                return self.functions[node.function.name](*args)

        raise CELEvaluationError(f"Not a function: {node.function}")

    def visit_ListExpr(self, node):
        """Evaluate a list literal node"""
        return [self.evaluate(element) for element in node.elements]

    def visit_MapExpr(self, node):
        """Evaluate a map literal node"""
        result = {}

        for key_node, value_node in node.entries:
            key = self.evaluate(key_node)
            value = self.evaluate(value_node)

            # Ensure the key is hashable
            if not isinstance(key, (str, int, float, bool, tuple)):
                raise CELTypeError(
                    f"Map key must be a hashable type, got {type(key).__name__}"
                )

            result[key] = value

        return result

    # Built-in functions

    def func_size(self, obj):
        """Get the size of a string, list, or map"""
        if obj is None:
            return 0

        if isinstance(obj, (str, list, dict)):
            return len(obj)

        raise CELTypeError(f"Cannot get size of {type(obj).__name__}")

    def func_contains(self, container, item):
        """Check if a container contains an item"""
        if container is None:
            return False

        if isinstance(container, str) and isinstance(item, str):
            return item in container

        if isinstance(container, (list, dict)):
            return item in container

        raise CELTypeError(
            f"Cannot check if {type(container).__name__} contains {type(item).__name__}"
        )

    def func_starts_with(self, s, prefix):
        """Check if a string starts with a prefix"""
        if s is None or prefix is None:
            return False

        if isinstance(s, str) and isinstance(prefix, str):
            return s.startswith(prefix)

        raise CELTypeError(
            f"Cannot check if {type(s).__name__} starts with {type(prefix).__name__}"
        )

    # Alias for startsWith to handle camelCase method calls
    def func_startsWith(self, s, prefix):
        """Alias for starts_with to handle camelCase method calls"""
        return self.func_starts_with(s, prefix)

    def func_ends_with(self, s, suffix):
        """Check if a string ends with a suffix"""
        if s is None or suffix is None:
            return False

        if isinstance(s, str) and isinstance(suffix, str):
            return s.endswith(suffix)

        raise CELTypeError(
            f"Cannot check if {type(s).__name__} ends with {type(suffix).__name__}"
        )

    # Alias for endsWith to handle camelCase method calls
    def func_endsWith(self, s, suffix):
        """Alias for ends_with to handle camelCase method calls"""
        return self.func_ends_with(s, suffix)

    def func_matches(self, s, pattern):
        """Check if a string matches a regex pattern"""
        if s is None or pattern is None:
            return False

        if isinstance(s, str) and isinstance(pattern, str):
            import re

            try:
                return bool(re.match(pattern, s))
            except re.error as e:
                raise CELEvaluationError(f"Invalid regex pattern: {e}")

        raise CELTypeError(
            f"Cannot match {type(s).__name__} against {type(pattern).__name__}"
        )

    def func_int(self, value):
        """Convert a value to an integer"""
        if value is None:
            return 0

        try:
            return int(value)
        except (ValueError, TypeError):
            raise CELTypeError(f"Cannot convert {type(value).__name__} to int")

    def func_float(self, value):
        """Convert a value to a float"""
        if value is None:
            return 0.0

        try:
            return float(value)
        except (ValueError, TypeError):
            raise CELTypeError(
                f"Cannot convert {type(value).__name__} to float"
            )

    def func_bool(self, value):
        """Convert a value to a boolean"""
        if value is None:
            return False

        return bool(value)

    def func_string(self, value):
        """Convert a value to a string"""
        if value is None:
            return "null"

        return str(value)

    def func_type(self, value):
        """Get the type of a value as a string"""
        if value is None:
            return "null"

        if isinstance(value, bool):
            return "bool"

        if isinstance(value, int):
            return "int"

        if isinstance(value, float):
            return "float"

        if isinstance(value, str):
            return "string"

        if isinstance(value, list):
            return "list"

        if isinstance(value, dict):
            return "map"

        return "unknown"


def evaluate(ast, context=None, allow_undeclared_vars=True):
    """
    Evaluate a parsed CEL expression

    Args:
        ast: The AST node to evaluate
        context (dict): A dictionary of variable values
        allow_undeclared_vars (bool): Whether to allow undeclared variables

    Returns:
        The result of evaluating the expression
    """
    evaluator = Evaluator(context, allow_undeclared_vars)
    return evaluator.evaluate(ast)
