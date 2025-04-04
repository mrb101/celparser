"""
Exception classes for CEL parsing and evaluation
"""

class CELError(Exception):
    """Base exception class for all CEL-related errors"""
    pass

class CELSyntaxError(CELError):
    """Exception raised for syntax errors in CEL expressions"""
    
    def __init__(self, message, position=None, expression=None):
        self.position = position
        self.expression = expression
        
        if position is not None and expression is not None:
            # Create a visual indicator of the error position
            pointer = ' ' * position + '^'
            message = f"{message}\n{expression}\n{pointer}"
        
        super().__init__(message)

class CELEvaluationError(CELError):
    """Exception raised when evaluation of a CEL expression fails"""
    pass

class CELTypeError(CELEvaluationError):
    """Exception raised when a type error occurs during evaluation"""
    pass

class CELUndefinedError(CELEvaluationError):
    """Exception raised when an undefined variable or field is referenced"""
    pass
