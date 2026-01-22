"""
Template parser for xlsx files.
Recognizes control statements, variables, and comments in Jinja2-like syntax.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Types of template tokens"""
    TEXT = auto()           # Plain text
    VARIABLE = auto()       # {{ expression }}
    FOR_START = auto()      # {% for item in items %}
    FOR_END = auto()        # {% endfor %}
    IF_START = auto()       # {% if condition %}
    ELIF = auto()           # {% elif condition %}
    ELSE = auto()           # {% else %}
    IF_END = auto()         # {% endif %}
    COMMENT = auto()        # {# comment #}


@dataclass
class Token:
    """Represents a parsed token"""
    type: TokenType
    content: str            # Original content
    expression: str = ""    # Extracted expression (for variables, conditions)
    loop_var: str = ""      # Loop variable name (for for loops)
    loop_iter: str = ""     # Loop iterable expression (for for loops)


# Regex patterns
VARIABLE_PATTERN = re.compile(r'\{\{\s*(.+?)\s*\}\}')
CONTROL_PATTERN = re.compile(r'^\s*\{%\s*(.+?)\s*%\}\s*$')
COMMENT_PATTERN = re.compile(r'^\s*\{#.*?#\}\s*$')

# Control statement patterns
FOR_START_PATTERN = re.compile(r'^for\s+(\w+)\s+in\s+(.+)$')
FOR_END_PATTERN = re.compile(r'^endfor$')
IF_START_PATTERN = re.compile(r'^if\s+(.+)$')
ELIF_PATTERN = re.compile(r'^elif\s+(.+)$')
ELSE_PATTERN = re.compile(r'^else$')
IF_END_PATTERN = re.compile(r'^endif$')


def parse_cell(content: str) -> Optional[Token]:
    """
    Parse a single cell's content and return a Token if it contains template syntax.
    
    For control statements ({% %}), the entire cell must be the control statement.
    For variables ({{ }}), they can be mixed with text.
    
    Returns None if the cell is plain text without any template syntax.
    """
    if content is None:
        return None
    
    content = str(content)
    
    # Check for comment (entire cell)
    if COMMENT_PATTERN.match(content):
        return Token(type=TokenType.COMMENT, content=content)
    
    # Check for control statement (entire cell)
    control_match = CONTROL_PATTERN.match(content)
    if control_match:
        statement = control_match.group(1).strip()
        return _parse_control_statement(content, statement)
    
    # Check for variables (can be mixed with text)
    if VARIABLE_PATTERN.search(content):
        return Token(type=TokenType.VARIABLE, content=content)
    
    # Plain text
    return None


def _parse_control_statement(content: str, statement: str) -> Optional[Token]:
    """Parse a control statement and return the appropriate Token."""
    
    # {% for item in items %}
    for_match = FOR_START_PATTERN.match(statement)
    if for_match:
        return Token(
            type=TokenType.FOR_START,
            content=content,
            loop_var=for_match.group(1),
            loop_iter=for_match.group(2).strip()
        )
    
    # {% endfor %}
    if FOR_END_PATTERN.match(statement):
        return Token(type=TokenType.FOR_END, content=content)
    
    # {% if condition %}
    if_match = IF_START_PATTERN.match(statement)
    if if_match:
        return Token(
            type=TokenType.IF_START,
            content=content,
            expression=if_match.group(1).strip()
        )
    
    # {% elif condition %}
    elif_match = ELIF_PATTERN.match(statement)
    if elif_match:
        return Token(
            type=TokenType.ELIF,
            content=content,
            expression=elif_match.group(1).strip()
        )
    
    # {% else %}
    if ELSE_PATTERN.match(statement):
        return Token(type=TokenType.ELSE, content=content)
    
    # {% endif %}
    if IF_END_PATTERN.match(statement):
        return Token(type=TokenType.IF_END, content=content)
    
    return None


def is_control_statement(content: str) -> bool:
    """Check if the cell content is a control statement or comment."""
    if content is None:
        return False
    
    content = str(content)
    
    if COMMENT_PATTERN.match(content):
        return True
    
    if CONTROL_PATTERN.match(content):
        return True
    
    return False


def extract_variables(content: str) -> List[str]:
    """
    Extract all variable expressions from a cell content.
    
    Example:
        "Total: {{ price * 1.1 }}원 ({{ name }})" 
        -> ["price * 1.1", "name"]
    """
    if content is None:
        return []
    
    return VARIABLE_PATTERN.findall(str(content))


def substitute_variables(content: str, replacements: dict) -> str:
    """
    Substitute variables in content with their values.
    
    Args:
        content: The cell content with {{ variable }} placeholders
        replacements: Dict mapping expression strings to their values
    
    Returns:
        Content with variables replaced by their values
    """
    if content is None:
        return ""
    
    content = str(content)
    
    def replace_match(match):
        expr = match.group(1).strip()
        if expr in replacements:
            value = replacements[expr]
            return "" if value is None else str(value)
        # Keep original if no replacement found
        return match.group(0)
    
    return VARIABLE_PATTERN.sub(replace_match, content)


def evaluate_condition(condition: str, context: dict) -> bool:
    """
    Evaluate a condition expression in the given context.
    
    Supports:
    - Variable truthiness: {% if items %}
    - Comparison: {% if count > 0 %}
    - Boolean: {% if is_active %}
    """
    from .expressions import evaluate_expression
    
    condition = condition.strip()
    
    # Try to evaluate as a simple expression first
    result = evaluate_expression(condition, context)
    
    if result is not None:
        return bool(result)
    
    # If evaluation failed, try to handle comparison operators
    # This is a simplified version - extend as needed
    comparison_ops = ['==', '!=', '>=', '<=', '>', '<']
    
    for op in comparison_ops:
        if op in condition:
            parts = condition.split(op, 1)
            if len(parts) == 2:
                left = evaluate_expression(parts[0].strip(), context)
                right = evaluate_expression(parts[1].strip(), context)
                
                if left is None or right is None:
                    return False
                
                if op == '==':
                    return left == right
                elif op == '!=':
                    return left != right
                elif op == '>=':
                    return left >= right
                elif op == '<=':
                    return left <= right
                elif op == '>':
                    return left > right
                elif op == '<':
                    return left < right
    
    return False
