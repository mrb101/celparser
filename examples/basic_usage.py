"""
Basic usage examples for the PyCEL package
"""

import sys
import os

# Add the current directory to the path so we can import the pycel package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from modules to avoid package import issues
from pycel.parser import parse
from pycel.evaluator import evaluate, Evaluator
from pycel.errors import CELSyntaxError, CELEvaluationError

# Recreate the compile function from __init__.py
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
            
        # Add built-in functions to the context
        evaluator = Evaluator(context, allow_undeclared_vars)
        
        # Add built-in functions to the context
        for func_name in ['size', 'contains', 'startsWith', 'endsWith', 
                         'matches', 'int', 'float', 'bool', 'string', 'type']:
            context[func_name] = func_name
            
        return evaluator.evaluate(ast)
    
    return evaluate_with_context

def simple_example():
    """Simple expression evaluation example"""
    print("=== Simple Example ===")
    
    # Using the compile helper
    expression = compile("a + b * 2")
    result = expression({"a": 10, "b": 5})
    print(f"a + b * 2 = {result}")  # Should print 20
    
    # Using parse and evaluate directly
    ast = parse("(a + b) * 2")
    result = evaluate(ast, {"a": 10, "b": 5})
    print(f"(a + b) * 2 = {result}")  # Should print 30

def data_types_example():
    """Example showing different data types"""
    print("\n=== Data Types Example ===")
    
    context = {
        "name": "Alice",
        "age": 30,
        "isAdmin": True,
        "tags": ["user", "member"],
        "profile": {
            "email": "alice@example.com",
            "active": True
        }
    }
    
    examples = [
        "name + ' is ' + string(age) + ' years old'",
        "isAdmin ? 'Administrator' : 'Regular user'",
        "tags[0] + ' account'",
        "profile.email",
        "size(tags)",
        "contains(tags, 'admin')",
        "type(age)",
        "startsWith(name, 'A')"
    ]
    
    for expr_str in examples:
        try:
            expr = compile(expr_str)
            result = expr(context)
            print(f"{expr_str} => {result}")
        except (CELSyntaxError, CELEvaluationError) as e:
            print(f"{expr_str} => ERROR: {e}")

def error_handling_example():
    """Example showing error handling"""
    print("\n=== Error Handling Example ===")
    
    # Syntax error
    try:
        expr = compile("a + * b")
    except CELSyntaxError as e:
        print(f"Syntax error caught: {e}")
    
    # Evaluation error
    try:
        expr = compile("a / b")
        result = expr({"a": 10, "b": 0})
    except CELEvaluationError as e:
        print(f"Evaluation error caught: {e}")
    
    # Type error
    try:
        expr = compile("a < b")
        result = expr({"a": 10, "b": "not a number"})
    except CELEvaluationError as e:
        print(f"Type error caught: {e}")
    
    # Undefined variable
    try:
        expr = compile("a + b")
        # Set allow_undeclared_vars to False in the compile function
        expr = compile("a + b", allow_undeclared_vars=False)
        result = expr({"a": 10})
    except CELEvaluationError as e:
        print(f"Undefined variable error caught: {e}")

def complex_example():
    """Complex expression example"""
    print("\n=== Complex Example ===")
    
    # Real-world scenario: Evaluating user permissions
    user = {
        "name": "Alice",
        "role": "editor",
        "department": "Engineering",
        "permissions": ["read", "write"],
        "active": True,
        "manager": {
            "name": "Bob",
            "role": "admin"
        },
        "projects": [
            {"id": "proj1", "access": "full"},
            {"id": "proj2", "access": "read-only"}
        ]
    }
    
    # Complex permission check
    permission_check = compile("""
        active && 
        (role == 'admin' || 
         (contains(permissions, 'write') && 
          (department == 'Engineering' || manager.role == 'admin')))
    """)
    
    has_permission = permission_check(user)
    print(f"User has required permissions: {has_permission}")
    
    # Complex data access and manipulation
    project_info = compile("""
        size(projects) > 0 ?
          projects[0].id + ' (' + projects[0].access + ')' :
          'No projects'
    """)
    
    result = project_info(user)
    print(f"First project info: {result}")

if __name__ == "__main__":
    simple_example()
    data_types_example()
    error_handling_example()
    complex_example()
