"""
Lexer for CEL expressions
"""

import re
from typing import List, Dict, Tuple, Union, Pattern
from celparser.errors import CELSyntaxError


class Token:
    """Token class for storing token type and value"""

    def __init__(
        self, token_type: str, value: Union[str, Dict[str, str]], position: int
    ):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r}, {self.position})"


class Lexer:
    """Lexer for tokenizing CEL expressions"""

    # Token types
    TOKEN_TYPES: Dict[str, str] = {
        "IDENTIFIER": r"[a-zA-Z_][a-zA-Z0-9_]*",
        "NUMBER": r"(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?",
        "STRING": r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'',
        "OPERATOR": r"==|!=|<=|>=|&&|\|\||[+\-*/%<>!]",
        "DOT": r"\.",
        "LPAREN": r"\(",
        "RPAREN": r"\)",
        "LBRACKET": r"\[",
        "RBRACKET": r"\]",
        "LBRACE": r"\{",
        "RBRACE": r"\}",
        "COMMA": r",",
        "COLON": r":",
        "QUESTIONMARK": r"\?",
        "WHITESPACE": r"\s+",
    }

    # Compile regexes for each token type
    TOKEN_REGEXES: List[Tuple[str, Pattern[str]]] = [
        (token_type, re.compile(pattern))
        for token_type, pattern in TOKEN_TYPES.items()
    ]

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """
        Tokenize the input text and return a list of tokens

        Returns:
            list: A list of Token objects

        Raises:
            CELSyntaxError: If the input contains invalid syntax
        """
        while self.position < len(self.text):
            matched = False

            for token_type, regex in self.TOKEN_REGEXES:
                match = regex.match(self.text, self.position)
                if match:
                    value = match.group(0)

                    # Skip whitespace tokens
                    if token_type != "WHITESPACE":
                        # For strings, strip quotes
                        if token_type == "STRING":
                            # Keep quotes in the token value but also store the actual string value
                            if value.startswith('"'):
                                actual_value = (
                                    value[1:-1]
                                    .replace('\\"', '"')
                                    .replace("\\\\", "\\")
                                )
                            else:
                                actual_value = (
                                    value[1:-1]
                                    .replace("\\'", "'")
                                    .replace("\\\\", "\\")
                                )
                            token = Token(
                                token_type,
                                {"raw": value, "value": actual_value},
                                self.position,
                            )
                        else:
                            token = Token(token_type, value, self.position)
                        self.tokens.append(token)

                    self.position = match.end()
                    matched = True
                    break

            if not matched:
                # No token matched at the current position
                char = self.text[self.position]
                raise CELSyntaxError(
                    f"Unexpected character: '{char}'", self.position, self.text
                )

        # Add an EOF token
        self.tokens.append(Token("EOF", "", self.position))
        return self.tokens


def tokenize(expression: str) -> List[Token]:
    """
    Tokenize a CEL expression

    Args:
        expression (str): The expression to tokenize

    Returns:
        list: A list of Token objects

    Raises:
        CELSyntaxError: If the expression contains invalid syntax
    """
    lexer = Lexer(expression)
    return lexer.tokenize()
