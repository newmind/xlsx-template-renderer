"""
xls_template_renderer - Jinja2-style template renderer for xlsx files
"""

from .renderer import render_template, render_template_to_file
from .exceptions import TemplateError, TemplateSyntaxError, TemplateRenderError

__version__ = "0.6.0"
__all__ = [
    "render_template",
    "render_template_to_file",
    "TemplateError",
    "TemplateSyntaxError",
    "TemplateRenderError",
]
