"""
celparser - Python parser and evaluator for Google Common Expression Language
"""

__version__ = "0.1.0"

from celparser.parser import parse
from celparser.evaluator import evaluate
from celparser.errors import (
    CELError,
    CELSyntaxError,
    CELEvaluationError,
    CELTypeError,
    CELUndefinedError,
)

__all__ = [
    "parse",
    "evaluate",
    "CELError",
    "CELSyntaxError",
    "CELEvaluationError",
    "CELTypeError",
    "CELUndefinedError",
]


def compile(expression, allow_undeclared_vars=True):
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
        return evaluate(ast, context, allow_undeclared_vars)

    return evaluate_with_context
