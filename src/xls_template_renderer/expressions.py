"""
Expression evaluator for template variables.
Supports: arithmetic (+, -, *, /), string concatenation, attribute access, index access.
"""

import re
import ast
import operator
from typing import Any, Dict


# Supported operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def resolve_path(data: Dict[str, Any], path: str) -> Any:
    """
    Resolve a dotted path with optional index access from data.
    
    Examples:
        - "name" -> data["name"]
        - "item.name" -> data["item"]["name"]
        - "items[0]" -> data["items"][0]
        - "items[0].name" -> data["items"][0]["name"]
    
    Returns None if path cannot be resolved.
    """
    if not path:
        return None
    
    # Pattern to match attribute or index access
    # e.g., "items[0].name" -> ["items", "[0]", "name"]
    token_pattern = re.compile(r'(\w+)|\[(\d+)\]')
    
    current = data
    pos = 0
    
    while pos < len(path):
        # Skip dots
        if path[pos] == '.':
            pos += 1
            continue
        
        # Try to match token
        match = token_pattern.match(path, pos)
        if not match:
            return None
        
        if match.group(1):
            # Attribute access
            key = match.group(1)
            if isinstance(current, dict):
                if key not in current:
                    return None
                current = current[key]
            elif hasattr(current, key):
                current = getattr(current, key)
            else:
                return None
        elif match.group(2):
            # Index access
            index = int(match.group(2))
            if isinstance(current, (list, tuple)):
                if index >= len(current):
                    return None
                current = current[index]
            else:
                return None
        
        pos = match.end()
    
    return current


class ExpressionEvaluator:
    """
    Evaluates simple expressions with variable substitution.
    """
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
    
    def evaluate(self, expression: str) -> Any:
        """
        Evaluate an expression string.
        
        Supports:
        - Variable access: name, item.price, items[0].name
        - Arithmetic: price * 1.1, 10 + 5
        - String concatenation: "hello" + name
        
        Returns the evaluated value, or None if evaluation fails.
        """
        expression = expression.strip()
        
        if not expression:
            return None
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body)
        except (SyntaxError, ValueError, TypeError, KeyError):
            return None
    
    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate an AST node."""
        
        if isinstance(node, ast.Constant):
            # Literal values: strings, numbers
            return node.value
        
        elif isinstance(node, ast.Num):
            # Python 3.7 compatibility
            return node.n
        
        elif isinstance(node, ast.Str):
            # Python 3.7 compatibility
            return node.s
        
        elif isinstance(node, ast.Name):
            # Simple variable: name
            return resolve_path(self.context, node.id)
        
        elif isinstance(node, ast.Attribute):
            # Attribute access: item.name
            path = self._get_attribute_path(node)
            return resolve_path(self.context, path)
        
        elif isinstance(node, ast.Subscript):
            # Index access: items[0]
            path = self._get_subscript_path(node)
            return resolve_path(self.context, path)
        
        elif isinstance(node, ast.BinOp):
            # Binary operations: +, -, *, /
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            
            if left is None or right is None:
                return None
            
            op_type = type(node.op)
            if op_type in OPERATORS:
                return OPERATORS[op_type](left, right)
            else:
                return None
        
        elif isinstance(node, ast.UnaryOp):
            # Unary operations: -x
            operand = self._eval_node(node.operand)
            if operand is None:
                return None
            
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
            else:
                return None
        
        else:
            return None
    
    def _get_attribute_path(self, node: ast.Attribute) -> str:
        """Build a dotted path from an Attribute node."""
        parts = []
        current = node
        
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.append(current.id)
        elif isinstance(current, ast.Subscript):
            parts.append(self._get_subscript_path(current))
        else:
            return ""
        
        parts.reverse()
        return ".".join(parts)
    
    def _get_subscript_path(self, node: ast.Subscript) -> str:
        """Build a path with index access from a Subscript node."""
        # Get the index
        if isinstance(node.slice, ast.Constant):
            index = node.slice.value
        elif isinstance(node.slice, ast.Num):
            # Python 3.7 compatibility
            index = node.slice.n
        elif isinstance(node.slice, ast.Index):
            # Python 3.8 compatibility
            if isinstance(node.slice.value, ast.Constant):
                index = node.slice.value.value
            elif isinstance(node.slice.value, ast.Num):
                index = node.slice.value.n
            else:
                return ""
        else:
            return ""
        
        # Get the base path
        if isinstance(node.value, ast.Name):
            base = node.value.id
        elif isinstance(node.value, ast.Attribute):
            base = self._get_attribute_path(node.value)
        elif isinstance(node.value, ast.Subscript):
            base = self._get_subscript_path(node.value)
        else:
            return ""
        
        return f"{base}[{index}]"


def evaluate_expression(expression: str, context: Dict[str, Any]) -> Any:
    """
    Convenience function to evaluate an expression with given context.
    
    Args:
        expression: The expression string to evaluate
        context: Dictionary containing variable values
    
    Returns:
        The evaluated result, or None if evaluation fails
    """
    evaluator = ExpressionEvaluator(context)
    return evaluator.evaluate(expression)
