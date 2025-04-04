"""
Flask web application for demonstrating the celparser library
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json

# Add the current directory to the path so we can import the celparser package
sys.path.insert(0, os.path.abspath("."))

# Import from the local celparser package
from celparser.parser import parse
from celparser.evaluator import Evaluator


# Define a wrapper for the compile function
def cel_compile(expression, allow_undeclared_vars=True):
    """
    Compile a CEL expression for later evaluation.

    Args:
        expression (str): The CEL expression to compile
        allow_undeclared_vars (bool): Whether to allow undeclared variables during evaluation

    Returns:
        A compiled expression object that can be evaluated against different contexts
    """
    ast = parse(expression)

    def evaluate_with_context(context=None):
        """
        Evaluate the compiled expression with the given context

        Args:
            context (dict): A dictionary mapping variable names to values

        Returns:
            The result of evaluating the expression
        """
        if context is None:
            context = {}

        # Create an evaluator with the context and built-in functions
        evaluator = Evaluator(context, allow_undeclared_vars)

        # Add built-in functions to the context
        for func_name in [
            "size",
            "contains",
            "startsWith",
            "endsWith",
            "matches",
            "int",
            "float",
            "bool",
            "string",
            "type",
        ]:
            context[func_name] = func_name

        return evaluator.evaluate(ast)

    return evaluate_with_context


app = Flask(__name__)


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate_expression():
    """Evaluate a CEL expression"""
    data = request.json
    expression = data.get("expression", "")
    context = data.get("context", {})

    try:
        # Compile and evaluate the expression
        compiled_expr = cel_compile(expression)
        result = compiled_expr(context)

        return jsonify(
            {"success": True, "result": result, "type": type(result).__name__}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/examples")
def examples():
    """Return some example expressions and contexts"""
    examples = [
        {
            "name": "Simple arithmetic",
            "expression": "a + b * 2",
            "context": {"a": 10, "b": 5},
            "description": "Basic arithmetic operations with variables",
        },
        {
            "name": "String manipulation",
            "expression": 'name + " is " + string(age) + " years old"',
            "context": {"name": "Alice", "age": 30},
            "description": "String concatenation with type conversion",
        },
        {
            "name": "Logical operations",
            "expression": 'isAdmin && age > 18 ? "Access granted" : "Access denied"',
            "context": {"isAdmin": True, "age": 30},
            "description": "Conditional expression with logical operators",
        },
        {
            "name": "List operations",
            "expression": 'contains(tags, "admin") && size(tags) > 1',
            "context": {"tags": ["user", "admin", "member"]},
            "description": "List membership testing and size operations",
        },
        {
            "name": "Map/object access",
            "expression": "user.profile.email",
            "context": {"user": {"profile": {"email": "test@example.com"}}},
            "description": "Nested object property access",
        },
        {
            "name": "Combined example",
            "expression": """
                active && 
                (role == "admin" || 
                 (contains(permissions, "write") && 
                  (department == "Engineering" || manager.role == "admin")))
            """,
            "context": {
                "active": True,
                "role": "editor",
                "permissions": ["read", "write"],
                "department": "Engineering",
                "manager": {"role": "admin"},
            },
            "description": "Complex permission checking logic",
        },
    ]

    return jsonify(examples)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
