"""
Filter functions for template expressions.
Provides Jinja2-like filters: default, length, join, etc.
"""

import re
from typing import Any, Callable, Dict, List, Optional


# Filter registry
FILTERS: Dict[str, Callable] = {}


def register_filter(name: str):
    """Decorator to register a filter function."""
    def decorator(func: Callable) -> Callable:
        FILTERS[name] = func
        return func
    return decorator


@register_filter('default')
def filter_default(value: Any, default_value: Any = '') -> Any:
    """
    Return default_value if value is None or undefined.
    
    Usage: {{ value|default('N/A') }}
    """
    if value is None:
        return default_value
    return value


@register_filter('length')
def filter_length(value: Any) -> int:
    """
    Return the length of a sequence or string.
    
    Usage: {{ items|length }}
    """
    if value is None:
        return 0
    try:
        return len(value)
    except TypeError:
        return 0


@register_filter('join')
def filter_join(value: Any, separator: str = '') -> str:
    """
    Join a list with a separator.
    
    Usage: {{ items|join(',') }}
    """
    if value is None:
        return ''
    if not isinstance(value, (list, tuple)):
        return str(value)
    return separator.join(str(item) for item in value)


def get_filter(name: str) -> Optional[Callable]:
    """Get a filter function by name."""
    return FILTERS.get(name)


def apply_filter(value: Any, filter_name: str, args: List[Any] = None) -> Any:
    """
    Apply a filter to a value.
    
    Args:
        value: The value to filter
        filter_name: Name of the filter
        args: Optional arguments for the filter
    
    Returns:
        Filtered value, or original value if filter not found
    """
    filter_func = get_filter(filter_name)
    if filter_func is None:
        return value
    
    if args:
        return filter_func(value, *args)
    return filter_func(value)


def parse_filter_expression(expression: str) -> tuple:
    """
    Parse a filter expression like "value|filter1|filter2('arg')".
    
    Returns:
        (base_expression, [(filter_name, [args]), ...])
    """
    if '|' not in expression:
        return expression, []
    
    # Split by | but be careful with strings containing |
    parts = _split_filters(expression)
    
    if len(parts) < 2:
        return expression, []
    
    base_expr = parts[0].strip()
    filters = []
    
    for filter_part in parts[1:]:
        filter_part = filter_part.strip()
        filter_name, args = _parse_single_filter(filter_part)
        if filter_name:
            filters.append((filter_name, args))
    
    return base_expr, filters


def _split_filters(expression: str) -> List[str]:
    """
    Split expression by | while respecting strings.
    """
    parts = []
    current = []
    in_string = False
    string_char = None
    paren_depth = 0
    
    for char in expression:
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
            current.append(char)
        elif char == string_char and in_string:
            in_string = False
            string_char = None
            current.append(char)
        elif char == '(' and not in_string:
            paren_depth += 1
            current.append(char)
        elif char == ')' and not in_string:
            paren_depth -= 1
            current.append(char)
        elif char == '|' and not in_string and paren_depth == 0:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    
    if current:
        parts.append(''.join(current))
    
    return parts


def _parse_single_filter(filter_str: str) -> tuple:
    """
    Parse a single filter like "default('N/A')" or "length".
    
    Returns:
        (filter_name, [args])
    """
    # Match filter name (must start with letter or underscore) and optional arguments
    match = re.match(r'^([a-zA-Z_]\w*)(?:\((.*)\))?$', filter_str.strip())
    if not match:
        return None, []
    
    filter_name = match.group(1)
    args_str = match.group(2)
    
    if args_str is None:
        return filter_name, []
    
    # Parse arguments
    args = _parse_filter_args(args_str)
    return filter_name, args


def _parse_filter_args(args_str: str) -> List[Any]:
    """
    Parse filter arguments string.
    
    Examples:
        "'hello'" -> ['hello']
        "'a', 'b'" -> ['a', 'b']
        "10" -> [10]
    """
    if not args_str.strip():
        return []
    
    args = []
    current = []
    in_string = False
    string_char = None
    
    for char in args_str:
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
            current.append(char)
        elif char == string_char and in_string:
            in_string = False
            string_char = None
            current.append(char)
        elif char == ',' and not in_string:
            arg_value = ''.join(current).strip()
            if arg_value:
                args.append(_parse_arg_value(arg_value))
            current = []
            continue
        else:
            current.append(char)
    
    # Last argument
    if current:
        arg_value = ''.join(current).strip()
        if arg_value:
            args.append(_parse_arg_value(arg_value))
    
    return args


def _parse_arg_value(value_str: str) -> Any:
    """
    Parse a single argument value.
    
    Examples:
        "'hello'" -> 'hello'
        "123" -> 123
        "12.5" -> 12.5
    """
    value_str = value_str.strip()
    
    # String literal
    if (value_str.startswith("'") and value_str.endswith("'")) or \
       (value_str.startswith('"') and value_str.endswith('"')):
        return value_str[1:-1]
    
    # Integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Return as string
    return value_str
