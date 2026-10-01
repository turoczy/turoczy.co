#!/usr/bin/env python3
"""sf_latest.py — bake the five most recent substantive Silicon Florist posts.

Writes the <li> rows for the `#sf-latest` list in the Typing section of
index.html. build.py splices the result between the SF-LATEST markers.

Why baked AND fetched live:
  - Baked (this script, at build time) means the list is never empty — it works
    with JavaScript off, and it survives the WordPress API being down.
  - js/site.js re-fetches the same endpoint on page load and replaces the list
    if it got anything newer. turoczy.co is a booking page; a "latest things
    I'm writing about" block that silently goes three months stale between
    builds is worse than no block at all.

Network failure is NOT a build failure. If the API can't be reached, this exits
0 without writing, and build.py leaves whatever is already in index.html alone.
A booking page should never fail to build because a blog was briefly down.

Roundup filtering: ~27% of recent SF posts are "links arrangement" / weekly
news-roundup posts (measured across the last 30 on 2026-10-01). Those are real
posts, but on a page selling keynotes "Silicon Florist links arrangement for
September 30, 2026" spends a slot without earning it. The lead-in says "Some of
the latest," which is what licenses a subset.

KEEP `SKIP` IN SYNC with the matching regex in js/site.js (`SF latest headlines`).
"""

import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = ("https://public-api.wordpress.com/rest/v1.1/sites/siliconflorist.com"
       "/posts/?number=20&fields=title,URL,date")

SECTION_OUT = ".sf_latest_section.html"
WANT = 5
INDENT = " " * 10

# Posts whose titles match these are curated link roundups / weekly recaps.
SKIP = re.compile(r"links arrangement|startup news for the week|"
                  r"oregon startup news for the week", re.I)


def fetch(url=API, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "turoczy.co build"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def pick(posts, want=WANT):
    out = []
    for p in posts:
        title = html.unescape(p.get("title") or "").strip()
        url = (p.get("URL") or "").strip()
        if not title or not url or SKIP.search(title):
            continue
        out.append((title, url))
        if len(out) == want:
            break
    return out


def render(items):
    rows = []
    for title, url in items:
        rows.append('%s<li><a href="%s">%s</a></li>'
                    % (INDENT, html.escape(url, quote=True), html.escape(title)))
    return "\n".join(rows) + "\n"


def main():
    try:
        data = fetch()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        sys.stderr.write("sf_latest: could not reach the WordPress API (%s)\n" % e)
        sys.stderr.write("sf_latest: leaving the existing baked list in place.\n")
        return 0

    items = pick(data.get("posts") or [])
    if not items:
        sys.stderr.write("sf_latest: API returned no usable posts; "
                         "leaving the existing baked list in place.\n")
        return 0

    io.open(SECTION_OUT, "w", encoding="utf-8").write(render(items))
    print("sf_latest — baked %d headlines into %s" % (len(items), SECTION_OUT))
    for title, _ in items:
        print("  · %s" % title[:72])
    return 0


if __name__ == "__main__":
    sys.exit(main())
