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
    - Logical operators: {% if a and b %}, {% if a or b %}, {% if not a %}
    - In operator: {% if item in items %}
    """
    from .expressions import evaluate_expression
    
    condition = condition.strip()
    
    # Handle 'or' operator (lowest precedence)
    or_result = _split_logical_operator(condition, ' or ')
    if or_result:
        left_cond, right_cond = or_result
        return evaluate_condition(left_cond, context) or evaluate_condition(right_cond, context)
    
    # Handle 'and' operator
    and_result = _split_logical_operator(condition, ' and ')
    if and_result:
        left_cond, right_cond = and_result
        return evaluate_condition(left_cond, context) and evaluate_condition(right_cond, context)
    
    # Handle 'not' operator
    if condition.startswith('not '):
        inner_condition = condition[4:].strip()
        return not evaluate_condition(inner_condition, context)
    
    # Handle 'in' operator: item in items
    in_result = _split_in_operator(condition)
    if in_result:
        item_expr, collection_expr = in_result
        item_value = evaluate_expression(item_expr, context)
        collection_value = evaluate_expression(collection_expr, context)
        
        if collection_value is None:
            return False
        
        try:
            return item_value in collection_value
        except TypeError:
            return False
    
    # Handle 'not in' operator: item not in items
    not_in_result = _split_not_in_operator(condition)
    if not_in_result:
        item_expr, collection_expr = not_in_result
        item_value = evaluate_expression(item_expr, context)
        collection_value = evaluate_expression(collection_expr, context)
        
        if collection_value is None:
            return True
        
        try:
            return item_value not in collection_value
        except TypeError:
            return True
    
    # Try to evaluate as a simple expression first
    result = evaluate_expression(condition, context)
    
    if result is not None:
        return bool(result)
    
    # If evaluation failed, try to handle comparison operators
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


def _split_logical_operator(condition: str, operator: str) -> Optional[Tuple[str, str]]:
    """
    Split condition by logical operator, respecting parentheses and strings.
    
    Returns (left, right) if operator found at top level, None otherwise.
    """
    depth = 0
    in_string = False
    string_char = None
    i = 0
    
    while i < len(condition):
        char = condition[i]
        
        # Handle strings
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
        # Handle parentheses
        elif char == '(' and not in_string:
            depth += 1
        elif char == ')' and not in_string:
            depth -= 1
        # Check for operator at top level
        elif depth == 0 and not in_string:
            if condition[i:].startswith(operator):
                left = condition[:i].strip()
                right = condition[i + len(operator):].strip()
                if left and right:
                    return (left, right)
        
        i += 1
    
    return None


def _split_in_operator(condition: str) -> Optional[Tuple[str, str]]:
    """
    Split condition by 'in' operator.
    
    Returns (item_expr, collection_expr) if 'in' found, None otherwise.
    """
    # Match pattern: expr in expr (but not 'not in')
    match = re.search(r'(?<!\bnot)\s+in\s+', condition)
    if match:
        left = condition[:match.start()].strip()
        right = condition[match.end():].strip()
        if left and right:
            return (left, right)
    return None


def _split_not_in_operator(condition: str) -> Optional[Tuple[str, str]]:
    """
    Split condition by 'not in' operator.
    
    Returns (item_expr, collection_expr) if 'not in' found, None otherwise.
    """
    match = re.search(r'\s+not\s+in\s+', condition)
    if match:
        left = condition[:match.start()].strip()
        right = condition[match.end():].strip()
        if left and right:
            return (left, right)
    return None
