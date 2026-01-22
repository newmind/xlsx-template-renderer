"""
xls_template_renderer - Jinja2-style template renderer for xlsx files
"""

from .renderer import render_template
from .exceptions import TemplateError, TemplateSyntaxError, TemplateRenderError

__version__ = "0.2.0"
__all__ = [
    "render_template",
    "TemplateError",
    "TemplateSyntaxError",
    "TemplateRenderError",
]
