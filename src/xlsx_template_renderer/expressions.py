"""
Expression evaluator for template variables.
Supports: arithmetic (+, -, *, /), string concatenation, attribute access, index access,
filters (|), and ternary operator (if...else).
"""

import re
import ast
import operator
from typing import Any, Dict, List

from .filters import parse_filter_expression, apply_filter


# Supported operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

# Comparison operators
COMPARE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# String comparison operators (order matters: longer ones first)
STR_COMPARE_OPS = ['==', '!=', '>=', '<=', '>', '<']

# Mapping from string operator to operator function
STR_COMPARE_FUNCS = {
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '<=': operator.le,
    '>': operator.gt,
    '<': operator.lt,
}


def _extract_comparison(expression: str) -> tuple:
    """
    Extract comparison operator from expression, respecting strings and parentheses.
    
    For expressions like "items|length == 1", returns:
        ("items|length", "==", "1")
    
    For expressions without comparison, returns:
        (expression, None, None)
    """
    in_string = False
    string_char = None
    paren_depth = 0
    
    i = 0
    while i < len(expression):
        char = expression[i]
        
        # Handle string boundaries
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
        elif char == '(' and not in_string:
            paren_depth += 1
        elif char == ')' and not in_string:
            paren_depth -= 1
        elif not in_string and paren_depth == 0:
            # Check for comparison operators (longer ones first)
            for op in STR_COMPARE_OPS:
                if expression[i:i+len(op)] == op:
                    left = expression[:i].strip()
                    right = expression[i+len(op):].strip()
                    return (left, op, right)
        
        i += 1
    
    return (expression, None, None)


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
        - Filters: value|default('N/A'), items|length
        - Filter with comparison: items|length == 1, items|length > 0
        - Ternary: 'yes' if condition else 'no'
        
        Returns the evaluated value, or None if evaluation fails.
        """
        expression = expression.strip()
        
        if not expression:
            return None
        
        # Check for filter + comparison combination (e.g., "items|length == 1")
        left, op, right = _extract_comparison(expression)
        if op and '|' in left:
            # Evaluate left side with filters
            left_val = self._evaluate_with_filters(left)
            # Evaluate right side normally
            right_val = self.evaluate(right)
            
            if left_val is None or right_val is None:
                return None
            
            return STR_COMPARE_FUNCS[op](left_val, right_val)
        
        # Parse filters first (e.g., "value|default('N/A')")
        base_expr, filters = parse_filter_expression(expression)
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(base_expr, mode='eval')
            result = self._eval_node(tree.body)
            
            # Apply filters
            for filter_name, filter_args in filters:
                result = apply_filter(result, filter_name, filter_args)
            
            return result
        except (SyntaxError, ValueError, TypeError, KeyError):
            return None
    
    def _evaluate_with_filters(self, expression: str) -> Any:
        """Evaluate an expression with filters applied."""
        base_expr, filters = parse_filter_expression(expression.strip())
        
        try:
            tree = ast.parse(base_expr, mode='eval')
            result = self._eval_node(tree.body)
            
            for filter_name, filter_args in filters:
                result = apply_filter(result, filter_name, filter_args)
            
            return result
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
            # Index/key access: items[0], dict["key"], dict[var]
            obj = self._eval_node(node.value)
            if obj is None:
                return None
            
            # Get the key/index
            key = self._eval_subscript_key(node.slice)
            if key is None:
                # Try old path-based approach for simple cases
                path = self._get_subscript_path(node)
                return resolve_path(self.context, path)
            
            # Access the value
            try:
                if isinstance(obj, dict):
                    return obj.get(key)
                elif isinstance(obj, (list, tuple)) and isinstance(key, int):
                    if 0 <= key < len(obj):
                        return obj[key]
                    return None
            except (KeyError, IndexError, TypeError):
                return None
            
            return None
        
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
            # Unary operations: -x, +x, not x
            operand = self._eval_node(node.operand)
            
            if isinstance(node.op, ast.USub):
                if operand is None:
                    return None
                return -operand
            elif isinstance(node.op, ast.UAdd):
                if operand is None:
                    return None
                return +operand
            elif isinstance(node.op, ast.Not):
                # not operator: not x
                return not operand
            else:
                return None
        
        elif isinstance(node, ast.IfExp):
            # Ternary operator: 'yes' if condition else 'no'
            condition = self._eval_node(node.test)
            if condition:
                return self._eval_node(node.body)
            else:
                return self._eval_node(node.orelse)
        
        elif isinstance(node, ast.Compare):
            # Comparison: a > b, a == b, etc.
            left = self._eval_node(node.left)
            if left is None:
                return None
            
            # Handle chained comparisons: a < b < c
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator)
                if right is None:
                    return None
                
                op_type = type(op)
                if op_type in COMPARE_OPS:
                    if not COMPARE_OPS[op_type](left, right):
                        return False
                    left = right
                else:
                    return None
            
            return True
        
        elif isinstance(node, ast.BoolOp):
            # Boolean operations: and, or
            if isinstance(node.op, ast.And):
                for value in node.values:
                    result = self._eval_node(value)
                    if not result:
                        return False
                return True
            elif isinstance(node.op, ast.Or):
                for value in node.values:
                    result = self._eval_node(value)
                    if result:
                        return True
                return False
            return None
        
        elif isinstance(node, ast.Dict):
            # Dictionary literal: {"a": 1, "b": 2}
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                key = self._eval_node(key_node)
                value = self._eval_node(value_node)
                if key is not None:
                    result[key] = value
            return result
        
        elif isinstance(node, ast.List):
            # List literal: [1, 2, 3]
            return [self._eval_node(elem) for elem in node.elts]
        
        elif isinstance(node, ast.Tuple):
            # Tuple literal: (1, 2, 3)
            return tuple(self._eval_node(elem) for elem in node.elts)
        
        elif isinstance(node, ast.Call):
            # Method call: dict.get(key, default)
            return self._eval_call(node)
        
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
    
    def _eval_subscript_key(self, slice_node: ast.AST) -> Any:
        """Evaluate the key/index in a subscript expression."""
        # Handle different slice types
        if isinstance(slice_node, ast.Constant):
            return slice_node.value
        elif isinstance(slice_node, ast.Num):
            # Python 3.7 compatibility
            return slice_node.n
        elif isinstance(slice_node, ast.Str):
            # Python 3.7 compatibility
            return slice_node.s
        elif isinstance(slice_node, ast.Index):
            # Python 3.8 compatibility
            return self._eval_subscript_key(slice_node.value)
        elif isinstance(slice_node, ast.Name):
            # Variable as key: dict[var]
            return resolve_path(self.context, slice_node.id)
        elif isinstance(slice_node, ast.Attribute):
            # Attribute as key: dict[obj.attr]
            path = self._get_attribute_path(slice_node)
            return resolve_path(self.context, path)
        else:
            return None
    
    def _eval_call(self, node: ast.Call) -> Any:
        """Evaluate a method call like dict.get(key, default)."""
        # Get the object and method name
        if isinstance(node.func, ast.Attribute):
            obj = self._eval_node(node.func.value)
            method_name = node.func.attr
            
            if obj is None:
                return None
            
            # Evaluate arguments
            args = [self._eval_node(arg) for arg in node.args]
            
            # Handle known safe methods
            if isinstance(obj, dict):
                if method_name == 'get':
                    if len(args) >= 1:
                        key = args[0]
                        default = args[1] if len(args) >= 2 else None
                        return obj.get(key, default)
                elif method_name == 'keys':
                    return list(obj.keys())
                elif method_name == 'values':
                    return list(obj.values())
                elif method_name == 'items':
                    return list(obj.items())
            elif isinstance(obj, str):
                if method_name == 'upper':
                    return obj.upper()
                elif method_name == 'lower':
                    return obj.lower()
                elif method_name == 'strip':
                    return obj.strip()
                elif method_name == 'split':
                    sep = args[0] if args else None
                    return obj.split(sep)
                elif method_name == 'replace':
                    if len(args) >= 2:
                        return obj.replace(args[0], args[1])
            elif isinstance(obj, (list, tuple)):
                if method_name == 'index':
                    if args:
                        try:
                            return obj.index(args[0])
                        except ValueError:
                            return -1
        
        return None
    
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
