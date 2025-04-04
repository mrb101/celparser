"""
Parser for CEL expressions
"""

from pycel.lexer import tokenize
from pycel.ast import (
    Literal, Identifier, MemberAccess, IndexAccess, 
    UnaryOp, BinaryOp, TernaryOp, FunctionCall,
    ListExpr, MapExpr
)
from pycel.errors import CELSyntaxError

class Parser:
    """Parser for CEL expressions"""
    
    # Operator precedence (higher number = higher precedence)
    PRECEDENCE = {
        '||': 1,
        '&&': 2,
        '==': 3, '!=': 3,
        '<': 4, '<=': 4, '>': 4, '>=': 4,
        '+': 5, '-': 5,
        '*': 6, '/': 6, '%': 6,
        '!': 7, 'UNARY_MINUS': 7,
    }
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        """
        Parse a CEL expression
        
        Returns:
            A parsed AST node
            
        Raises:
            CELSyntaxError: If the expression cannot be parsed
        """
        result = self.expression()
        
        # Ensure we've consumed all input
        if self.current_token().type != 'EOF':
            raise CELSyntaxError(
                f"Unexpected token: {self.current_token().value}",
                self.current_token().position,
                " ".join(token.value if isinstance(token.value, str) else token.value.get('raw', '') 
                         for token in self.tokens[:-1])
            )
        
        return result
    
    def current_token(self):
        """Get the current token"""
        return self.tokens[self.pos]
    
    def consume(self, expected_type=None):
        """
        Consume the current token and advance
        
        Args:
            expected_type (str, optional): The expected token type
            
        Returns:
            The consumed token
            
        Raises:
            CELSyntaxError: If the current token doesn't match the expected type
        """
        token = self.current_token()
        
        if expected_type and token.type != expected_type:
            # Prepare a representation of the input for the error message
            input_repr = " ".join(
                token.value if isinstance(token.value, str) else token.value.get('raw', '')
                for token in self.tokens[:-1]  # Skip EOF
            )
            
            raise CELSyntaxError(
                f"Expected {expected_type}, got {token.type} instead",
                token.position,
                input_repr
            )
        
        self.pos += 1
        return token
    
    def match(self, token_type):
        """Check if the current token matches the given type"""
        return self.current_token().type == token_type
    
    def expression(self):
        """Parse a top-level expression"""
        return self.ternary_expr()
    
    def ternary_expr(self):
        """Parse a ternary expression (condition ? true_expr : false_expr)"""
        condition = self.logical_or()
        
        if self.match('QUESTIONMARK'):
            self.consume('QUESTIONMARK')
            true_expr = self.expression()
            self.consume('COLON')
            false_expr = self.expression()
            return TernaryOp(condition, true_expr, false_expr)
        
        return condition
    
    def logical_or(self):
        """Parse a logical OR expression (expr || expr)"""
        return self.binary_op(self.logical_and, ['||'])
    
    def logical_and(self):
        """Parse a logical AND expression (expr && expr)"""
        return self.binary_op(self.equality, ['&&'])
    
    def equality(self):
        """Parse an equality expression (expr == expr, expr != expr)"""
        return self.binary_op(self.relational, ['==', '!='])
    
    def relational(self):
        """Parse a relational expression (expr < expr, expr > expr, etc.)"""
        return self.binary_op(self.additive, ['<', '<=', '>', '>='])
    
    def additive(self):
        """Parse an additive expression (expr + expr, expr - expr)"""
        return self.binary_op(self.multiplicative, ['+', '-'])
    
    def multiplicative(self):
        """Parse a multiplicative expression (expr * expr, expr / expr, expr % expr)"""
        return self.binary_op(self.unary, ['*', '/', '%'])
    
    def binary_op(self, next_method, operators):
        """Parse binary operators with the same precedence"""
        left = next_method()
        
        while (self.match('OPERATOR') and self.current_token().value in operators):
            operator = self.consume('OPERATOR').value
            right = next_method()
            left = BinaryOp(operator, left, right)
        
        return left
    
    def unary(self):
        """Parse a unary expression (!expr, -expr)"""
        if self.match('OPERATOR') and self.current_token().value in ['!', '-']:
            operator = self.consume('OPERATOR').value
            expr = self.unary()
            # For unary minus, use a special operator name to distinguish from binary minus
            if operator == '-':
                return UnaryOp('UNARY_MINUS', expr)
            return UnaryOp(operator, expr)
        
        return self.primary()
    
    def primary(self):
        """Parse a primary expression"""
        expr = self.atom()
        
        # Parse member access, index access, and function calls
        while True:
            if self.match('DOT'):
                # Member access: obj.field
                self.consume('DOT')
                field = self.consume('IDENTIFIER').value
                expr = MemberAccess(expr, field)
            
            elif self.match('LBRACKET'):
                # Index access: obj[index]
                self.consume('LBRACKET')
                index = self.expression()
                self.consume('RBRACKET')
                expr = IndexAccess(expr, index)
            
            elif self.match('LPAREN'):
                # Function call: func(args)
                self.consume('LPAREN')
                args = []
                
                if not self.match('RPAREN'):
                    args.append(self.expression())
                    
                    while self.match('COMMA'):
                        self.consume('COMMA')
                        args.append(self.expression())
                
                self.consume('RPAREN')
                expr = FunctionCall(expr, args)
            
            else:
                break
        
        return expr
    
    def atom(self):
        """Parse an atomic expression (literals, identifiers, parenthesized expressions)"""
        if self.match('NUMBER'):
            # Parse number literal
            token = self.consume('NUMBER')
            value = token.value
            
            # Determine if it's an integer or float
            if '.' in value or 'e' in value.lower():
                return Literal(float(value), 'float')
            else:
                return Literal(int(value), 'int')
        
        elif self.match('STRING'):
            # Parse string literal (value already has quotes removed)
            token = self.consume('STRING')
            return Literal(token.value['value'], 'string')
        
        elif self.match('IDENTIFIER'):
            # Parse identifier or boolean/null literals
            token = self.consume('IDENTIFIER')
            value = token.value
            
            # Check for boolean and null literals
            if value == 'true':
                return Literal(True, 'bool')
            elif value == 'false':
                return Literal(False, 'bool')
            elif value == 'null':
                return Literal(None, 'null')
            else:
                return Identifier(value)
        
        elif self.match('LPAREN'):
            # Parse parenthesized expression
            self.consume('LPAREN')
            expr = self.expression()
            self.consume('RPAREN')
            return expr
        
        elif self.match('LBRACKET'):
            # Parse list literal
            self.consume('LBRACKET')
            elements = []
            
            if not self.match('RBRACKET'):
                elements.append(self.expression())
                
                while self.match('COMMA'):
                    self.consume('COMMA')
                    elements.append(self.expression())
            
            self.consume('RBRACKET')
            return ListExpr(elements)
        
        elif self.match('LBRACE'):
            # Parse map literal
            self.consume('LBRACE')
            entries = []
            
            if not self.match('RBRACE'):
                key = self.expression()
                self.consume('COLON')
                value = self.expression()
                entries.append((key, value))
                
                while self.match('COMMA'):
                    self.consume('COMMA')
                    key = self.expression()
                    self.consume('COLON')
                    value = self.expression()
                    entries.append((key, value))
            
            self.consume('RBRACE')
            return MapExpr(entries)
        
        else:
            # Unexpected token
            token = self.current_token()
            input_repr = " ".join(t.value if isinstance(t.value, str) else t.value.get('raw', '') 
                                 for t in self.tokens[:-1])
            
            raise CELSyntaxError(
                f"Unexpected token: {token.value}",
                token.position,
                input_repr
            )


def parse(expression):
    """
    Parse a CEL expression
    
    Args:
        expression (str): The expression to parse
        
    Returns:
        An AST node representing the parsed expression
        
    Raises:
        CELSyntaxError: If the expression contains invalid syntax
    """
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()
