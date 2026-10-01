# turoczy.co — working instructions

Personal one-pager. Purpose: book keynotes and consulting.

## The #index section is generated. Do not hand-edit it.

`index_data.py` owns every index entry. `build.py` runs it and splices the
result into `index.html` between `<section class="section" id="index">` and its
close. Anything typed into that markup by hand is erased by the next build.

Everything else in `index.html` — hero, Talking, Typing, **Receipts**, Hire,
Work, Bot, Say hi — is hand-written and is the source of truth, **with one
exception noted below**. Receipts in particular is a curated highlight reel, not
generated: adding an entry to `index_data.py` does **not** put it in Receipts,
and vice versa.

## The SF headline list inside Typing is also generated

There are **two** generated regions, not one. Inside the otherwise hand-written
Typing section, the `<ul id="sf-latest">` between the `<!-- SF-LATEST:START -->`
and `<!-- SF-LATEST:END -->` markers is owned by `sf_latest.py`. The surrounding
prose — including the "Some of the latest things I'm writing about:" lead-in —
is hand-written and yours to edit.

It is baked **and** fetched live, deliberately:

- `sf_latest.py` bakes the current five at build time, so the list renders with
  JavaScript off and survives the WordPress API being down.
- The `SF latest headlines` block in `js/site.js` re-fetches the same endpoint on
  page load and replaces the list. This is a booking page; a "latest things I'm
  writing about" block that quietly goes three months stale between builds is
  worse than no block.

Two things to know:

- **Link roundups are filtered out.** ~27% of recent SF posts are "links
  arrangement" / weekly-recap posts. The `SKIP` regex drops them so the five
  slots go to substantive posts. **That regex exists twice — `sf_latest.py` and
  `js/site.js` — and the two must stay in sync.**
- **A network failure is not a build failure.** `sf_latest.py` exits 0 without
  writing when the API is unreachable, and `build.py` then leaves whatever is
  already baked in `index.html` untouched. Verified: with the API host broken,
  the build still exits 0 and `index.html` comes out byte-identical.

One command after any edit to `index.html`, `css/site.css`, `js/site.js`,
`index_data.py`, or `sf_latest.py`:

```bash
python3 build.py          # splice #index + SF headlines, stamp ?v=, regenerate llm.md
python3 build.py --no-splice   # only when deliberately leaving both generated regions alone
```

Skipping it serves a stale stylesheet and lets `llm.md` drift.

## Removing one of two duplicate entries: name the loss first

`index_data.py` exits 2 on any URL listed twice, so a duplicate cannot reach
the page. It cannot tell you which copy to keep — that is judgment, and it is
where this goes wrong.

**Before dropping either copy, state out loud what detail each one carries that
the other does not** — a year, a slide count, a fuller headline, a byline, a
venue — and carry that detail across to the survivor. Then remove.

Naming the loss *after* the removal is the failure mode. It cost a revert on
2026-09-26: the `2008 Portland Tech Recap` SlideShare was filed as both a talk
and a deck, the talk copy was kept, and only afterwards did it come up that the
deck copy was the one carrying "64 slides." The right half had to be restored
and the talk's `2008–09` year hand-carried over.

## Verifying entries

- **Never infer a video's nature from its title.** Check the channel:
  `yt-dlp --print "%(channel)s %(upload_date)s %(view_count)s" <url>`.
  Self-published uploads belong in *Shows I host*; outside stages belong in
  *Keynotes, conference talks, and panels*. Five entries sat in *Writing* on
  2026-09-26 because nobody checked.
- **Upload year ≠ event year.** A conference often posts months later.
- `python3 checklinks.py --bad` before sending anyone the link. `403`/`429`/`999`
  from Kickstarter, Wefunder, Slack, LinkedIn, GeekWire, YouTube and archive.org
  are bot-blocks, not rot. Don't loop it — that triggers real throttling.

## Git

Commit locally. **Never push** — that is Rick's call, every time.
