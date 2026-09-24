#!/usr/bin/env python3
"""Build llm.md from index.html.

The page is the source of truth. Run this after editing index.html so the
Markdown never drifts from what a person actually sees:

    python3 build.py
"""

import html
import io
import re
from html.parser import HTMLParser

SRC = "index.html"
OUT = "llm.md"

SKIP_TAGS = {"script", "style", "svg", "button", "nav"}
INLINE = {"a", "b", "i", "em", "strong", "span", "q", "cite", "br"}


class Node:
    def __init__(self, tag=None, attrs=None):
        self.tag = tag
        self.attrs = dict(attrs or {})
        self.kids = []
        self.text = ""

    def cls(self):
        return self.attrs.get("class", "").split()


class Tree(HTMLParser):
    """Just enough DOM to walk the page's semantic structure."""

    VOID = {"meta", "link", "br", "img", "input", "hr", "circle", "path", "line"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.stack = [self.root]
        self.muted = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.muted += 1
            return
        if self.muted or tag in self.VOID:
            return
        node = Node(tag, attrs)
        self.stack[-1].kids.append(node)
        self.stack.append(node)

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.muted = max(0, self.muted - 1)
            return
        if self.muted or tag in self.VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.muted or not data.strip():
            return
        leaf = Node("#text")
        leaf.text = data
        self.stack[-1].kids.append(leaf)


def inline(node):
    """Render a node's contents as inline Markdown."""
    out = []
    for k in node.kids:
        if k.tag == "#text":
            out.append(k.text)
        elif k.tag == "a" and k.attrs.get("href"):
            href = k.attrs["href"]
            label = inline(k).strip()
            out.append("[%s](%s)" % (label, href) if label else "")
        elif k.tag in ("strong", "b"):
            out.append("**%s**" % inline(k).strip())
        elif k.tag in ("em", "i", "cite"):
            out.append("*%s*" % inline(k).strip())
        elif k.tag == "q":
            out.append('"%s"' % inline(k).strip())
        else:
            out.append(inline(k))
    return re.sub(r"[ \t]+", " ", "".join(out))


def find(node, pred, hits=None):
    hits = [] if hits is None else hits
    for k in node.kids:
        if pred(k):
            hits.append(k)
        find(k, pred, hits)
    return hits


def first(node, pred):
    hits = find(node, pred)
    return hits[0] if hits else None


def render_body(node, lines):
    """Walk a .section-body (or the hero) and emit Markdown blocks."""
    for k in node.kids:
        if k.tag == "#text":
            continue
        if k.tag in ("h3",):
            lines.append("")
            lines.append("### " + inline(k).strip())
            lines.append("")
        elif k.tag == "p":
            t = inline(k).strip()
            if t:
                lines.append(t)
                lines.append("")
        elif k.tag == "blockquote":
            t = inline(k).strip()
            t = re.sub(r"\s*\n\s*", " ", t)
            lines.append("> " + t)
            lines.append("")
        elif k.tag in ("ul", "ol"):
            for li in [x for x in k.kids if x.tag == "li"]:
                spans = [c for c in li.kids if c.tag == "span"]
                blocks = [c for c in li.kids if c.tag in ("h3", "p")]

                if spans and any("ix-yr" in c.cls() or "cv-org" in c.cls() for c in spans):
                    # index / CV row: year — entry, or org — role — dates
                    parts = [inline(c).strip() for c in spans]
                elif blocks:
                    # talk card: heading, then description, then where
                    parts = []
                    for c in blocks:
                        txt = inline(c).strip()
                        if not txt:
                            continue
                        parts.append("**%s**" % txt if c.tag == "h3" else txt)
                else:
                    parts = [inline(li).strip()]

                parts = [x for x in parts if x]
                if parts:
                    lines.append("- " + " — ".join(parts))
            lines.append("")
        else:
            render_body(k, lines)


def stamp_assets():
    """Bump the ?v= on css/js so a browser can't serve a stale stylesheet."""
    import time
    v = time.strftime("%Y%m%d%H%M")
    doc = io.open(SRC, encoding="utf-8").read()
    out = re.sub(r'href="css/site\.css(\?v=\d+)?"', 'href="css/site.css?v=%s"' % v, doc)
    out = re.sub(r'src="js/site\.js(\?v=\d+)?"', 'src="js/site.js?v=%s"' % v, out)
    if out != doc:
        io.open(SRC, "w", encoding="utf-8").write(out)
        print("stamped assets v=%s" % v)


def main():
    stamp_assets()
    doc = io.open(SRC, encoding="utf-8").read()
    t = Tree()
    t.feed(doc)

    lines = ["# Rick Turoczy", ""]

    hero = first(t.root, lambda n: "hero-inner" in n.cls())
    if hero:
        tag = first(hero, lambda n: "tagline" in n.cls())
        h1 = first(hero, lambda n: n.tag == "h1")
        lede = first(hero, lambda n: "lede" in n.cls())
        if tag:
            lines.append("*%s*" % inline(tag).strip())
            lines.append("")
        if h1:
            lines.append("> %s" % inline(h1).strip())
            lines.append("")
        if lede:
            lines.append(inline(lede).strip())
            lines.append("")

    lines.append("Portland, Oregon. Available for keynotes and consulting.")
    lines.append("Contact: rick@piepdx.com")
    lines.append("")
    lines.append("---")
    lines.append("")

    for sec in find(t.root, lambda n: n.tag == "section" and "section" in n.cls() and n.attrs.get("id")):
        head = first(sec, lambda n: n.tag == "h2")
        body = first(sec, lambda n: "section-body" in n.cls())
        if not head or not body:
            continue
        lines.append("## " + inline(head).strip())
        lines.append("")
        render_body(body, lines)
        lines.append("---")
        lines.append("")

    md = "\n".join(lines)
    md = html.unescape(md)
    md = re.sub(r"\n{3,}", "\n\n", md).rstrip() + "\n"
    io.open(OUT, "w", encoding="utf-8").write(md)
    print("wrote %s — %d lines, %d bytes" % (OUT, md.count("\n"), len(md)))


if __name__ == "__main__":
    main()
