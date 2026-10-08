"""pyui.core - describe a UI as a tree of Elements and render it to HTML."""
import html

VOID_TAGS = {"input", "br", "hr", "img"}
EVENT_PROPS = {"on_click", "on_submit"}


class Raw:
    """Text that must NOT be escaped (used for <style> content)."""
    def __init__(self, text):
        self.text = text


class Element:
    """One node of the UI tree: a tag, props (attributes/handlers), children."""
    def __init__(self, tag, props, children):
        self.tag = tag
        self.props = props
        self.children = _flatten(children)


def _flatten(children):
    out = []
    for c in children:
        if c is None or c is False:
            continue
        if isinstance(c, (list, tuple)):
            out.extend(_flatten(c))
        else:
            out.append(c)
    return out


def _make_tag(tag):
    def build(*children, **props):
        return Element(tag, props, children)
    build.__name__ = tag
    return build


# Tag helpers: div("hello", class_="box") -> Element
div, span, p, h1, h2, ul, li, button, form, label, style = (
    _make_tag(t) for t in
    ["div", "span", "p", "h1", "h2", "ul", "li", "button", "form", "label", "style"]
)
input_ = _make_tag("input")


class Renderer:
    """Turns an Element tree into an HTML string.
    Event handlers found in props are stored in self.handlers under an id,
    and the HTML points at that id (/_event/<id>)."""

    def __init__(self):
        self.handlers = {}
        self._count = 0

    def _register(self, fn):
        self._count += 1
        hid = f"h{self._count}"
        self.handlers[hid] = fn
        return hid

    def render(self, node):
        if isinstance(node, Raw):
            return node.text
        if not isinstance(node, Element):
            return html.escape(str(node))

        props = dict(node.props)
        extra = ""

        # on_submit: the <form> itself posts to the server
        if "on_submit" in props:
            hid = self._register(props.pop("on_submit"))
            props["method"] = "post"
            props["action"] = f"/_event/{hid}"

        # on_click: a button is wrapped in a tiny form that posts the click
        on_click = props.pop("on_click", None)

        attrs = self._attrs(props)
        if node.tag in VOID_TAGS:
            inner = f"<{node.tag}{attrs}>"
        else:
            kids = "".join(self.render(c) for c in node.children)
            inner = f"<{node.tag}{attrs}>{kids}</{node.tag}>"

        if on_click:
            hid = self._register(on_click)
            return (f'<form method="post" action="/_event/{hid}" '
                    f'class="inline">{inner}</form>')
        return inner

    @staticmethod
    def _attrs(props):
        parts = []
        for k, v in props.items():
            if v is False or v is None:
                continue
            k = k.rstrip("_").replace("_", "-")   # class_ -> class
            parts.append(f" {k}" if v is True else f' {k}="{html.escape(str(v))}"')
        return "".join(parts)
