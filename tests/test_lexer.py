"""
Tests for the lexer module
"""

import unittest
from pycel.lexer import tokenize
from pycel.errors import CELSyntaxError

class TestLexer(unittest.TestCase):
    """Test cases for the CEL lexer"""
    
    def test_empty_expression(self):
        """Test tokenizing an empty expression"""
        tokens = tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, 'EOF')
    
    def test_literal_tokens(self):
        """Test tokenizing literal values"""
        # Integer
        tokens = tokenize("42")
        self.assertEqual(len(tokens), 2)  # number + EOF
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, '42')
        
        # Float
        tokens = tokenize("3.14")
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, '3.14')
        
        # Scientific notation
        tokens = tokenize("1e10")
        self.assertEqual(tokens[0].type, 'NUMBER')
        self.assertEqual(tokens[0].value, '1e10')
        
        # String with double quotes
        tokens = tokenize('"hello"')
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value['raw'], '"hello"')
        self.assertEqual(tokens[0].value['value'], 'hello')
        
        # String with single quotes
        tokens = tokenize("'world'")
        self.assertEqual(tokens[0].type, 'STRING')
        self.assertEqual(tokens[0].value['raw'], "'world'")
        self.assertEqual(tokens[0].value['value'], 'world')
        
        # String with escaped quotes
        tokens = tokenize('"hello \\"world\\""')
        self.assertEqual(tokens[0].value['value'], 'hello "world"')
    
    def test_identifier_tokens(self):
        """Test tokenizing identifiers"""
        tokens = tokenize("variable_name")
        self.assertEqual(tokens[0].type, 'IDENTIFIER')
        self.assertEqual(tokens[0].value, 'variable_name')
        
        # Reserved words are treated as identifiers
        tokens = tokenize("true")
        self.assertEqual(tokens[0].type, 'IDENTIFIER')
        self.assertEqual(tokens[0].value, 'true')
        
        tokens = tokenize("false")
        self.assertEqual(tokens[0].type, 'IDENTIFIER')
        self.assertEqual(tokens[0].value, 'false')
        
        tokens = tokenize("null")
        self.assertEqual(tokens[0].type, 'IDENTIFIER')
        self.assertEqual(tokens[0].value, 'null')
    
    def test_operator_tokens(self):
        """Test tokenizing operators"""
        operators = ['+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '&&', '||', '!']
        
        for op in operators:
            tokens = tokenize(op)
            self.assertEqual(tokens[0].type, 'OPERATOR')
            self.assertEqual(tokens[0].value, op)
    
    def test_delimiter_tokens(self):
        """Test tokenizing delimiters"""
        delimiters = {
            '.': 'DOT',
            '(': 'LPAREN',
            ')': 'RPAREN',
            '[': 'LBRACKET',
            ']': 'RBRACKET',
            '{': 'LBRACE',
            '}': 'RBRACE',
            ',': 'COMMA',
            ':': 'COLON',
            '?': 'QUESTIONMARK'
        }
        
        for delimiter, token_type in delimiters.items():
            tokens = tokenize(delimiter)
            self.assertEqual(tokens[0].type, token_type)
            self.assertEqual(tokens[0].value, delimiter)
    
    def test_complex_expression(self):
        """Test tokenizing a complex expression"""
        expr = 'a && b || c.field[0] + func(1, "text") ? true : false'
        tokens = tokenize(expr)

        # Verify token count (excluding EOF)
        self.assertEqual(len(tokens) - 1, 21)

        # Sample validation of some tokens
        self.assertEqual(tokens[0].type, 'IDENTIFIER')
        self.assertEqual(tokens[0].value, 'a')

        self.assertEqual(tokens[1].type, 'OPERATOR')
        self.assertEqual(tokens[1].value, '&&')

        self.assertEqual(tokens[4].type, 'IDENTIFIER')
        self.assertEqual(tokens[4].value, 'c')

        self.assertEqual(tokens[5].type, 'DOT')

        self.assertEqual(tokens[17].type, 'QUESTIONMARK')

        self.assertEqual(tokens[18].type, 'IDENTIFIER')
        self.assertEqual(tokens[18].value, 'true')

        self.assertEqual(tokens[19].type, 'COLON')

        self.assertEqual(tokens[20].type, 'IDENTIFIER')
        self.assertEqual(tokens[20].value, 'false')
    
    def test_invalid_syntax(self):
        """Test tokenizing invalid syntax"""
        with self.assertRaises(CELSyntaxError):
            tokenize('$')
        
        with self.assertRaises(CELSyntaxError):
            tokenize('"unterminated string')


if __name__ == '__main__':
    unittest.main()
