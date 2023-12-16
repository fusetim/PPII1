from mistune import HTMLRenderer, escape
import mistune

class CuliVertRenderer(HTMLRenderer):
    def link(self, text, url, title=None):
        return "<span>" + escape(url) + "</span>"

    def image(self, alt, url, title=None):
        return "<span>[image: "+ alt +"]</span>"


def markdown_render(content):
    markdown = mistune.create_markdown(renderer=CuliVertRenderer(), escape=True, plugins=None)
    return markdown(content)