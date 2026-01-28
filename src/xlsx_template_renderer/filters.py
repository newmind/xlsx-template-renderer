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


# === String Filters ===

@register_filter('upper')
def filter_upper(value: Any) -> str:
    """
    Convert string to uppercase.
    
    Usage: {{ name|upper }}
    """
    if value is None:
        return ''
    return str(value).upper()


@register_filter('lower')
def filter_lower(value: Any) -> str:
    """
    Convert string to lowercase.
    
    Usage: {{ name|lower }}
    """
    if value is None:
        return ''
    return str(value).lower()


@register_filter('title')
def filter_title(value: Any) -> str:
    """
    Convert string to title case.
    
    Usage: {{ name|title }}
    """
    if value is None:
        return ''
    return str(value).title()


@register_filter('trim')
def filter_trim(value: Any) -> str:
    """
    Remove leading and trailing whitespace.
    
    Usage: {{ text|trim }}
    """
    if value is None:
        return ''
    return str(value).strip()


@register_filter('replace')
def filter_replace(value: Any, old: str, new: str) -> str:
    """
    Replace occurrences of old with new.
    
    Usage: {{ text|replace('a', 'b') }}
    """
    if value is None:
        return ''
    return str(value).replace(old, new)


# === Number Filters ===

@register_filter('round')
def filter_round(value: Any, precision: int = 0) -> float:
    """
    Round a number to a given precision.
    
    Usage: {{ price|round }} or {{ price|round(2) }}
    """
    if value is None:
        return 0.0
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return 0.0


@register_filter('abs')
def filter_abs(value: Any) -> Any:
    """
    Return the absolute value.
    
    Usage: {{ value|abs }}
    """
    if value is None:
        return 0
    try:
        return abs(value)
    except TypeError:
        try:
            return abs(float(value))
        except (ValueError, TypeError):
            return 0


@register_filter('int')
def filter_int(value: Any, default: int = 0) -> int:
    """
    Convert value to integer.
    
    Usage: {{ num|int }}
    """
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


@register_filter('float')
def filter_float(value: Any, default: float = 0.0) -> float:
    """
    Convert value to float.
    
    Usage: {{ num|float }}
    """
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# === List Filters ===

@register_filter('first')
def filter_first(value: Any) -> Any:
    """
    Return the first element of a sequence.
    
    Usage: {{ items|first }}
    """
    if value is None:
        return None
    try:
        return value[0] if len(value) > 0 else None
    except (TypeError, KeyError):
        return None


@register_filter('last')
def filter_last(value: Any) -> Any:
    """
    Return the last element of a sequence.
    
    Usage: {{ items|last }}
    """
    if value is None:
        return None
    try:
        return value[-1] if len(value) > 0 else None
    except (TypeError, KeyError):
        return None


def get_filter(name: str) -> Optional[Callable]:
    """Get a filter function by name."""
    return FILTERS.get(name)


def apply_filter(value: Any, filter_name: str, args: Optional[List[Any]] = None) -> Any:
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


def _unescape_string(s: str) -> str:
    """
    Process escape sequences in a string.
    
    Examples:
        '\\n' -> '\n' (newline)
        '\\t' -> '\t' (tab)
    """
    return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\\\', '\\')


def _parse_arg_value(value_str: str) -> Any:
    """
    Parse a single argument value.
    
    Examples:
        "'hello'" -> 'hello'
        "'line1\\nline2'" -> 'line1\nline2'
        "123" -> 123
        "12.5" -> 12.5
    """
    value_str = value_str.strip()
    
    # String literal
    if (value_str.startswith("'") and value_str.endswith("'")) or \
       (value_str.startswith('"') and value_str.endswith('"')):
        return _unescape_string(value_str[1:-1])
    
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
