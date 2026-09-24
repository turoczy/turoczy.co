#!/usr/bin/env python3
"""Check every outbound link on the page and report what's broken.

    python3 checklinks.py            # check them all
    python3 checklinks.py --bad      # only print failures

Citations rot. Run this before you send anyone the link.
"""

import concurrent.futures as cf
import re
import sys
import time
import urllib.error
import urllib.request

SRC = "index.html"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TIMEOUT = 20


def links(path):
    html = open(path, encoding="utf-8").read()
    # preconnect/dns-prefetch hints are not content links
    html = re.sub(r'<link[^>]+rel="(?:preconnect|dns-prefetch)"[^>]*>', "", html)
    found = []
    for m in re.finditer(r'href="(https?://[^"]+)"', html):
        url = m.group(1)
        # the anchor text tells you which entry to fix
        tail = html[m.end():m.end() + 400]
        label = re.sub(r"<[^>]+>", "", tail.split("</a>")[0]).strip()
        label = re.sub(r"\s+", " ", label)[:70]
        found.append((url, label))
    seen, out = set(), []
    for url, label in found:
        if url not in seen:
            seen.add(url)
            out.append((url, label))
    return out


def check(item):
    """Fetch once; back off and retry when a host rate-limits us.

    archive.org throttles aggressively, which reads as a dead link if you
    only look once. It isn't.
    """
    url, label = item
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    last = (0, "unknown")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return url, label, r.status, r.geturl()
        except urllib.error.HTTPError as e:
            last = (e.code, url)
            if e.code not in (429, 503):
                break
        except Exception as e:
            last = (0, type(e).__name__)
        time.sleep(3 * (attempt + 1))
    return url, label, last[0], last[1]


def main():
    only_bad = "--bad" in sys.argv
    items = links(SRC)
    print("checking %d links\n" % len(items))

    rows = []
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(check, items):
            rows.append(row)

    bad = 0
    for url, label, status, final in sorted(rows, key=lambda r: r[2]):
        ok = status == 200
        # 403/999 = bot-blocking (Kickstarter, GeekWire, LinkedIn).
        # 429 = we asked too fast (YouTube, archive.org). Neither is rot,
        # so both are flagged but not counted as broken.
        if not ok and status not in (403, 429, 999):
            bad += 1
        if only_bad and ok:
            continue
        mark = "ok  " if ok else ("bot?" if status in (403, 429, 999) else "FAIL")
        print("%s %-4s %s" % (mark, status or "err", url))
        if label:
            print("        %s" % label)
        if not ok and isinstance(final, str) and final != url:
            print("        -> %s" % final)

    print("\n%d ok, %d broken" % (len(rows) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
