.. _usage:

Usage Guide
===========

This guide provides an overview of how to use the celparser package to parse and evaluate CEL expressions.

Basic Usage
-----------

The simplest way to use celparser is with the ``compile`` function, which combines parsing and evaluation:

.. code-block:: python

    from celparser import compile

    # Compile an expression
    expression = compile("a + b * 2")

    # Evaluate with a context
    result = expression({"a": 10, "b": 5})
    print(result)  # Output: 20

    # Reuse the same expression with different contexts
    result2 = expression({"a": 5, "b": 3})
    print(result2)  # Output: 11

Using parse and evaluate directly
--------------------------------

If you need more control, you can use the ``parse`` and ``evaluate`` functions directly:

.. code-block:: python

    from celparser.parser import parse
    from celparser.evaluator import evaluate

    # Parse the expression into an AST
    ast = parse("(a + b) * 2")

    # Evaluate the AST with a context
    result = evaluate(ast, {"a": 10, "b": 5})
    print(result)  # Output: 30

Working with Different Data Types
-------------------------------

CEL supports various data types, including strings, numbers, booleans, lists, and maps:

.. code-block:: python

    from celparser import compile

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

    # String concatenation
    expr1 = compile("name + ' is ' + string(age) + ' years old'")
    print(expr1(context))  # Output: "Alice is 30 years old"

    # Ternary operator
    expr2 = compile("isAdmin ? 'Administrator' : 'Regular user'")
    print(expr2(context))  # Output: "Administrator"

    # List indexing
    expr3 = compile("tags[0] + ' account'")
    print(expr3(context))  # Output: "user account"

    # Map access
    expr4 = compile("profile.email")
    print(expr4(context))  # Output: "alice@example.com"

Built-in Functions
-----------------

CEL provides several built-in functions:

.. code-block:: python

    # Size function
    expr5 = compile("size(tags)")
    print(expr5(context))  # Output: 2

    # Contains function
    expr6 = compile("contains(tags, 'admin')")
    print(expr6(context))  # Output: False

    # Type function
    expr7 = compile("type(age)")
    print(expr7(context))  # Output: "int"

    # String functions
    expr8 = compile("startsWith(name, 'A')")
    print(expr8(context))  # Output: True

Error Handling
--------------

celparser provides comprehensive error handling:

.. code-block:: python

    from celparser import compile
    from celparser.errors import CELSyntaxError, CELEvaluationError

    # Syntax error
    try:
        expr = compile("a + * b")
    except CELSyntaxError as e:
        print(f"Syntax error caught: {e}")

    # Evaluation error (division by zero)
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
        expr = compile("a + b", allow_undeclared_vars=False)
        result = expr({"a": 10})  # 'b' is missing
    except CELEvaluationError as e:
        print(f"Undefined variable error caught: {e}")

Advanced Usage
--------------

For more complex scenarios, you can combine multiple CEL expressions:

.. code-block:: python

    from celparser import compile

    # User data
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
    print(f"User has required permissions: {has_permission}")  # Output: True

    # Complex data access and manipulation
    project_info = compile("""
        size(projects) > 0 ?
          projects[0].id + ' (' + projects[0].access + ')' :
          'No projects'
    """)

    result = project_info(user)
    print(f"First project info: {result}")  # Output: "proj1 (full)"
