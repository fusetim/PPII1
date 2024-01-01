"""
Markdown renderer module.

This module contains the renderer for markdown to html, using mistune.
It is primarly used to render the description of a recipe.
"""

import mistune
from mistune import HTMLRenderer, escape


class CuliVertRenderer(HTMLRenderer):
    """
    Custom renderer for mistune, to render markdown to html.

    This renderer is used to render the description of a recipe, and therefore disable all
    external (and internal too) links and images.
    """

    def link(self, text, url, title=None):
        return "<span>" + escape(url) + "</span>"

    def image(self, alt, url, title=None):
        return "<span>[image: " + alt + "]</span>"


def markdown_render(content):
    """
    Render markdown to html, using our custom renderer.

    Args:
        content: The markdown content to render.

    Returns:
        The rendered html, it should be safe and escaping user inputs.
    """
    markdown = mistune.create_markdown(
        renderer=CuliVertRenderer(), escape=True, plugins=None
    )
    return markdown(content)
