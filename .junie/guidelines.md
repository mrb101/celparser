# celparser Python Style Guide

This document outlines the coding standards and best practices for the PyCEL project, a Python parser and evaluator for Google Common Expression Language (CEL).

## General Principles

- **Readability**: Code should be easy to read and understand.
- **Simplicity**: Prefer simple solutions over complex ones.
- **Consistency**: Follow established patterns in the codebase.
- **Maintainability**: Write code that is easy to maintain and extend.

## Code Style

### Formatting

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions.
- Use 4 spaces for indentation (no tabs).
- Maximum line length of 79 characters for code, 72 for comments and docstrings.
- Use blank lines to separate logical sections of code.
- Use spaces around operators and after commas.
- No trailing whitespace.

### Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Use absolute imports when possible.
- For multiple imports from a single module, use parenthesized imports:
  ```python
  from celparser.ast import (
      Literal, Identifier, MemberAccess, IndexAccess,
      UnaryOp, BinaryOp, TernaryOp, FunctionCall,
      ListExpr, MapExpr
  )
  ```

### Naming Conventions

- **Classes**: Use `CamelCase` (e.g., `Evaluator`, `CELSyntaxError`).
- **Functions/Methods**: Use `snake_case` (e.g., `parse`, `evaluate`, `visit_Literal`).
- **Variables**: Use `snake_case` (e.g., `token_type`, `allow_undeclared_vars`).
- **Constants**: Use `UPPER_SNAKE_CASE` (e.g., `MAX_RECURSION_DEPTH`).
- **Private methods/attributes**: Prefix with a single underscore (e.g., `_evaluate_internal`).

## Documentation

### Docstrings

- Use triple double quotes (`"""`) for docstrings.
- Include a brief description of the function/class purpose.
- For functions and methods, document:
  - Parameters (using `Args:` section)
  - Return values (using `Returns:` section)
  - Exceptions raised (using `Raises:` section, if applicable)
- Example:
  ```python
  def compile(expression, allow_undeclared_vars=True):
      """
      Compile a CEL expression for later evaluation.
      
      Args:
          expression (str): The CEL expression to compile
          allow_undeclared_vars (bool): Whether to allow undeclared variables during evaluation
          
      Returns:
          A compiled expression object that can be evaluated against different contexts
      """
  ```

### Comments

- Use comments sparingly and only when necessary to explain complex logic.
- Keep comments up-to-date with code changes.
- Use complete sentences with proper capitalization and punctuation.

## Architecture and Design Patterns

### Visitor Pattern

- Use the visitor pattern for traversing and evaluating AST nodes.
- Implement `visit_*` methods for each node type.
- Provide a `generic_visit` method for handling unknown node types.

### Error Handling

- Use a hierarchy of custom exception classes.
- Base exceptions on a common `CELError` class.
- Create specific exception types for different error categories (e.g., `CELSyntaxError`, `CELEvaluationError`).
- Include meaningful error messages that help diagnose the issue.

### Programming Paradigms

- Use a mix of functional and object-oriented programming styles as appropriate.
- Prefer composition over inheritance.
- Use classes for stateful components (e.g., `Evaluator`).
- Use pure functions for stateless operations.
- Avoid global state and mutable shared state.

## Testing

- Write unit tests for all functionality.
- Use the `unittest` framework.
- Organize tests in classes that inherit from `unittest.TestCase`.
- Use descriptive test method names prefixed with `test_`.
- Include docstrings for test methods explaining what they test.
- Test both positive cases (valid inputs) and negative cases (invalid inputs).
- Aim for high test coverage, especially for core functionality.

## Common Pitfalls to Avoid

- **Mutable default arguments**: Never use mutable objects as default arguments.
  ```python
  # Bad
  def func(items=[]):
      items.append(1)
      return items
  
  # Good
  def func(items=None):
      if items is None:
          items = []
      items.append(1)
      return items
  ```

- **Circular imports**: Avoid circular dependencies between modules.
- **Deep nesting**: Limit nesting depth to improve readability.
- **Complex boolean expressions**: Break complex conditions into named variables.
- **Reinventing the wheel**: Use standard library functions when available.
- **Premature optimization**: Focus on correctness first, then optimize if needed.

## Python Version Compatibility

- The project supports Python 3.8 and above.
- Avoid using features not available in Python 3.8.
- Document any version-specific code with comments.

## Version Control

- Write clear, concise commit messages.
- Keep commits focused on a single logical change.
- Use feature branches for new functionality.
- Run tests before committing changes.
