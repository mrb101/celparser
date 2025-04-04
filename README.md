# celparser - Python Common Expression Language Parser

A Python implementation of Google's Common Expression Language (CEL) parser and evaluator.

## Overview

celparser is a Python package that provides parsing and evaluation of Google's Common Expression Language (CEL). CEL is a simple expression language that lets you check whether a condition is true or false at runtime. It's designed to be simple, portable, and safe to execute in constrained environments.

CEL is used in various Google products and open-source projects for policy enforcement, data filtering, and configuration.

## Features

- Parse and evaluate CEL expressions
- Support for basic CEL syntax and operations
- Support for common data types (string, number, boolean, lists, maps)
- Comprehensive error reporting
- Simple API for integration with Python applications
- Built-in functions for common operations
- Extensible with custom functions

## Installation

### Using pip

```bash
pip install celparser
```

### Using uv

```bash
uv pip install celparser
```

### From source

```bash
git clone https://github.com/celparser/celparser.git
cd celparser
pip install .
```

## Requirements

- Python 3.8 or higher

## Usage Examples

### Basic Usage

```python
from celparser import compile

# Compile an expression
expression = compile("a + b * 2")

# Evaluate with a context
result = expression({"a": 10, "b": 5})
print(result)  # Output: 20

# Reuse the same expression with different contexts
result2 = expression({"a": 5, "b": 3})
print(result2)  # Output: 11
```

### Using parse and evaluate directly

```python
from celparser.parser import parse
from celparser.evaluator import evaluate

# Parse the expression into an AST
ast = parse("(a + b) * 2")

# Evaluate the AST with a context
result = evaluate(ast, {"a": 10, "b": 5})
print(result)  # Output: 30
```

### Working with Different Data Types

```python
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

# Built-in functions
expr5 = compile("size(tags)")
print(expr5(context))  # Output: 2

expr6 = compile("contains(tags, 'admin')")
print(expr6(context))  # Output: False

expr7 = compile("type(age)")
print(expr7(context))  # Output: "int"

expr8 = compile("startsWith(name, 'A')")
print(expr8(context))  # Output: True
```

### Error Handling

```python
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
```

### Complex Example: Permission Checking

```python
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
```

## API Reference

### Main Functions

- `compile(expression, allow_undeclared_vars=True)`: Compile a CEL expression for later evaluation
- `parse(expression)`: Parse a CEL expression into an AST
- `evaluate(ast, context=None, allow_undeclared_vars=True)`: Evaluate a parsed CEL expression

### Classes

- `Evaluator`: Main class for evaluating CEL expressions
- `CELSyntaxError`: Exception raised for syntax errors
- `CELEvaluationError`: Base exception for evaluation errors
- `CELTypeError`: Exception raised for type errors
- `CELUndefinedError`: Exception raised for undefined variables

### Built-in Functions

- `size(obj)`: Get the size of a string, list, or map
- `contains(container, item)`: Check if a container contains an item
- `startsWith(s, prefix)` / `starts_with(s, prefix)`: Check if a string starts with a prefix
- `endsWith(s, suffix)` / `ends_with(s, suffix)`: Check if a string ends with a suffix
- `matches(s, pattern)`: Check if a string matches a regex pattern
- `int(value)`: Convert a value to an integer
- `float(value)`: Convert a value to a float
- `bool(value)`: Convert a value to a boolean
- `string(value)`: Convert a value to a string
- `type(value)`: Get the type of a value as a string

## Development

### Setup

1. Clone the repository
2. Install dependencies using `uv sync --all-extras --dev`
3. Run tests using `uv run pytest tests`

### Publishing to PyPI

This project uses GitHub Actions to automatically publish to PyPI when a new release is created.

#### For Maintainers

To publish a new version to PyPI:

1. Update the version number in `setup.py`
2. Create a new release on GitHub with a tag matching the version (e.g., `v0.1.0`)
3. The GitHub Action will automatically build and publish the package to PyPI

#### Setting up PyPI API Token

To set up the PyPI API token for automated publishing:

1. Create an API token on PyPI (https://pypi.org/manage/account/token/)
2. Add the token as a GitHub secret named `PYPI_API_TOKEN` in the repository settings
