.. _examples:

Examples
=======

This page provides additional examples of using the celparser package for various use cases.

Basic Examples
------------

Simple Arithmetic
~~~~~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # Basic arithmetic
    expr = compile("(10 + 5) * 2 / 5")
    result = expr({})
    print(result)  # Output: 6.0

    # Variables in arithmetic
    expr = compile("(x + y) * z")
    result = expr({"x": 10, "y": 5, "z": 2})
    print(result)  # Output: 30

String Operations
~~~~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # String concatenation
    expr = compile("'Hello, ' + name + '!'")
    result = expr({"name": "World"})
    print(result)  # Output: "Hello, World!"

    # String functions
    expr = compile("size(text)")
    result = expr({"text": "Hello, World!"})
    print(result)  # Output: 13

    expr = compile("text.startsWith('Hello')")
    result = expr({"text": "Hello, World!"})
    print(result)  # Output: True

Boolean Logic
~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # Simple conditions
    expr = compile("age >= 18")
    print(expr({"age": 20}))  # Output: True
    print(expr({"age": 16}))  # Output: False

    # Complex conditions
    expr = compile("age >= 18 && (role == 'admin' || hasPermission)")
    context = {"age": 25, "role": "user", "hasPermission": True}
    print(expr(context))  # Output: True

    context = {"age": 25, "role": "admin", "hasPermission": False}
    print(expr(context))  # Output: True

    context = {"age": 16, "role": "admin", "hasPermission": True}
    print(expr(context))  # Output: False

Lists and Maps
~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # List operations
    expr = compile("items[0] + items[1]")
    result = expr({"items": [10, 20, 30]})
    print(result)  # Output: 30

    expr = compile("contains(items, 'apple')")
    result = expr({"items": ["banana", "apple", "orange"]})
    print(result)  # Output: True

    # Map operations
    expr = compile("user.name + ' is ' + string(user.age)")
    result = expr({"user": {"name": "Alice", "age": 30}})
    print(result)  # Output: "Alice is 30"

    expr = compile("user.address.city")
    result = expr({"user": {"address": {"city": "New York"}}})
    print(result)  # Output: "New York"

Advanced Examples
--------------

Data Filtering
~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # Sample data
    users = [
        {"name": "Alice", "age": 30, "role": "admin"},
        {"name": "Bob", "age": 25, "role": "user"},
        {"name": "Charlie", "age": 35, "role": "user"},
        {"name": "Dave", "age": 20, "role": "guest"}
    ]

    # Filter users by age
    age_filter = compile("user.age > 25")
    filtered_users = [user for user in users if age_filter({"user": user})]
    print([user["name"] for user in filtered_users])  # Output: ["Alice", "Charlie"]

    # Filter users by role
    role_filter = compile("user.role == 'admin' || user.role == 'user'")
    filtered_users = [user for user in users if role_filter({"user": user})]
    print([user["name"] for user in filtered_users])  # Output: ["Alice", "Bob", "Charlie"]

    # Complex filter
    complex_filter = compile("user.age > 25 && user.role != 'admin'")
    filtered_users = [user for user in users if complex_filter({"user": user})]
    print([user["name"] for user in filtered_users])  # Output: ["Charlie"]

Permission Checking
~~~~~~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # Define a permission check expression
    permission_check = compile("""
        user.active && 
        (user.role == 'admin' || 
         (contains(user.permissions, permission) && 
          user.department == requiredDepartment))
    """)

    # User data
    user1 = {
        "active": True,
        "role": "admin",
        "permissions": ["read", "write"],
        "department": "Engineering"
    }

    user2 = {
        "active": True,
        "role": "user",
        "permissions": ["read", "write"],
        "department": "Engineering"
    }

    user3 = {
        "active": True,
        "role": "user",
        "permissions": ["read"],
        "department": "Engineering"
    }

    user4 = {
        "active": False,
        "role": "admin",
        "permissions": ["read", "write"],
        "department": "Engineering"
    }

    # Check permissions
    context1 = {"user": user1, "permission": "write", "requiredDepartment": "Engineering"}
    print(permission_check(context1))  # Output: True (admin role)

    context2 = {"user": user2, "permission": "write", "requiredDepartment": "Engineering"}
    print(permission_check(context2))  # Output: True (has permission and correct department)

    context3 = {"user": user3, "permission": "write", "requiredDepartment": "Engineering"}
    print(permission_check(context3))  # Output: False (doesn't have write permission)

    context4 = {"user": user4, "permission": "write", "requiredDepartment": "Engineering"}
    print(permission_check(context4))  # Output: False (not active)

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from celparser import compile

    # Define validation rules
    validation_rules = {
        "name": compile("size(config.name) > 0"),
        "age": compile("config.age >= 18 && config.age < 100"),
        "email": compile("config.email.contains('@')"),
        "settings": compile("size(config.settings) > 0")
    }

    # Configuration to validate
    config = {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
        "settings": {"theme": "dark", "notifications": True}
    }

    # Validate configuration
    validation_results = {}
    for field, rule in validation_rules.items():
        validation_results[field] = rule({"config": config})

    print(validation_results)
    # Output: {'name': True, 'age': True, 'email': True, 'settings': True}

    # Invalid configuration
    invalid_config = {
        "name": "",
        "age": 15,
        "email": "invalid-email",
        "settings": {}
    }

    # Validate invalid configuration
    validation_results = {}
    for field, rule in validation_rules.items():
        validation_results[field] = rule({"config": invalid_config})

    print(validation_results)
    # Output: {'name': False, 'age': False, 'email': False, 'settings': False}