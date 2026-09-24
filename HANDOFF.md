# turoczy.co — session handoff

**Date:** 2026-09-24 · **Repo:** `~/GitHub/turoczy.co` (origin: `github.com/turoczy/turoczy.co`) · **Status:** built, iterating, committed locally

Personal branding one-pager. Purpose: book **keynotes** and **consulting**. Will later host a Soqratic bot.

---

## Run it

```bash
cd ~/GitHub/turoczy.co
python3 -m http.server 8787     # then open http://localhost:8787/
```

**After ANY edit to `index.html`, `css/site.css`, or `js/site.js`, run:**

```bash
python3 build.py
```

It regenerates `llm.md` **and** re-stamps the `?v=` cache-buster on the CSS/JS tags. Without it Chrome silently serves a stale stylesheet — this bit us mid-session and made edits look like no-ops.

```bash
python3 checklinks.py          # verify every outbound link
python3 checklinks.py --bad    # failures only
```

`403`/`429`/`999` are bot-blocking or throttling (Kickstarter, GeekWire, LinkedIn, YouTube, archive.org), **not** dead links. The checker flags them `bot?` and does not count them as broken. Don't re-run it in a loop — YouTube and archive.org will start throttling, which looks like breakage but isn't.

---

## Files

| File | What it is |
|---|---|
| `index.html` | The page. Single file, hand-edited. |
| `css/site.css` | All styles. |
| `js/site.js` | Theme toggle · hero dot field · index filters · scrollspy. |
| `index_data.py` | **Source of truth for the index section.** Edit here, not in the HTML. |
| `build.py` | Generates `llm.md` from `index.html`; stamps asset versions. |
| `checklinks.py` | Verifies every outbound link. |
| `llm.md` | Generated. Linked from nav as "AI kibble". Never hand-edit. |
| `DESIGN.md` | Design rationale — palette, type, the dot system. |

### How to change an index entry

1. Edit `index_data.py`
2. `python3 index_data.py` → writes `/tmp/index_section.html`
3. Splice it into `index.html` between `<section class="section" id="index">` and the `<!-- BOT -->` comment
4. `python3 build.py`

The splice is currently manual. **Worth automating** — it's the most error-prone step left.

---

## Design

Dots are the system — his own "collecting dots / connecting dots" thesis. Nav is a dot rail; the hero is a field where dots arrive one at a time and then get connected, permanently, building a matrix over ~60s. Nothing is ever removed. Pauses off-screen; `prefers-reduced-motion` gets the finished state instantly.

Palette: Douglas-fir ink `#14241E`, lichen ground `#E7E8E2`, Rose City accent `#B8365E`. Fraunces (display) + Archivo (body). Light/dark toggle, top right, follows OS until clicked, then remembered in `localStorage`.

All buttons are pills (`border-radius: 999px`) — CTAs, index chips, theme toggle.

---

## Page structure

Hero → Hello, I'm Rick → Talks → Receipts → Hire me → Writing → Work (CV) → Index → Ask a bot → Say hello → AI kibble

- **H1:** "Community, startups, innovation… all of the buzzwords" (Rick's line)
- **Tagline:** "More than mildly obsessed with connecting dots in the startup community" — his LinkedIn headline, sits under the H1 where the dots animate
- **CTAs:** "Get me on your stage" / "Put me to work" → `mailto:rick@piepdx.com`
- **Index:** 99 entries, 6 groups, filter chips (Everything · Talks · Shows · Press · Books & decks · Kickstarters · Organizing)

Copy came from @writer, structure from @CMO.

---

## ⚠️ The big lesson: the research docs are unreliable

Three source docs on the Desktop (`Rick Turoczy Media Mentions.md`, `Rick Turoczy Media Appearances Archive.md`, and a pasted PBS analysis) are AI-generated and **confidently wrong** in ways that matter.

**What they got wrong:**

- Claimed Rick organized **Demolicious, Ignite Portland, Beer and Blog** — he did not. (He organized TechfestNW, 30 Hour Day, PIE Demo Days, Open Source Bridge, Built Festival, and is Pitch Black production crew.)
- Wrong dates: PR Talk 2018→**2017**, And Uhhh Jul→**May 30 2018**, Overcommitted "archival"→**Nov 2025**, OPB Feb→**Sep 25 2017**, TEDxPortland listed as both 2016 and 2018 (**2018** used).
- Wrong titles: "3 Minutes on a Train"→**"Four minutes on the train…"**, "Pump Your Own Shampoo"→**"Pour Your Own Shampoo From a Tap"**, "The Intersectional"→**"The Intersection"**, "Seattle and Portland: BFFs?"→**"Seattle and Portland should do more to become BFFs"**
- The **PBS doc never once said Rick was in the segment** it described in eleven paragraphs. (He is — verified independently.)

**Rule going forward: verify every claim from those docs before it goes on the page. Never construct a URL from a title.**

### Two mistakes I made — don't repeat them

1. **Deleted a real credit.** Removed "Solve Podcast / Paden Squires" as fabricated because the show name was wrong. It's real — Rick's YouTube playlist proved it. Restored.
2. **Replaced a real article.** Told Rick the GeekWire "Google tosses support to PIE" piece didn't exist and swapped in a different one. It exists. Restored.

Both times the error was concluding *absence of evidence = fabrication* after only searching one way.

---

## What actually finds sources

Ranked by what worked:

1. **Wayback CDX enumeration** — the single most effective tool. Lists every archived URL under a path, sidestepping bot-blocking entirely.
   ```bash
   curl -s "http://web.archive.org/cdx/search/cdx?url=DOMAIN%2FPATH*&output=json&limit=8000&filter=statuscode:200&collapse=urlkey&fl=original"
   ```
   Found: all 4 GeekWire 2011 articles, all 9 SlideShare decks, the full PBS transcript, the original Open Source Bridge site.
2. **Rick's own vault** (`~/Documents/brain/`) — Twitter archive and SF posts. Found 30 Hour Day, Portland Makers, the 2013 OPB appearance, both Kickstarter URLs.
3. **ChromeBoost** for anything paywalled or bot-blocked (PBJ, GeekWire, bizjournals).
4. **iTunes Search API** — free, no key, finds podcasts and exact episodes:
   ```
   https://itunes.apple.com/search?term=X&entity=podcast
   https://itunes.apple.com/lookup?id=<collectionId>&entity=podcastEpisode&limit=200
   ```
5. **YouTube playlist scraping** — Rick's "Talks" playlist had 19 items we didn't have.

---

## Open items

### Uncited index entries (7)
Likely no public record: **SXSW** Pitch judging · **OEN PubTalk** · **Kobe, Japan** · **Muscat, Oman**

Should exist, not yet found:
- **2013 OPB Think Out Loud, "Northwest Technology Update"** — shortlink resolves to `opb.org/thinkoutloud/shows/northwest-technology-update/`, now 404, **no Wayback snapshot**. Entry says so explicitly.
- **2014 Willamette Week** PIE Demo Day livestream post
- **2011 The Oregonian** — Mike Rogoway on the PIE launch

**Next step:** run Wayback CDX enumeration against `wweek.com/portland/*` and `oregonlive.com/*` — the technique that cracked GeekWire.

### Questions outstanding for Rick
- **TEDxPortland year conflict** — his own docs say both 2016 and 2018. Page says 2018.
- **"Rick Turoczy: Minimizer of Friction"** (Social Venturers) — replaced with the verified S04E08 episode. Is the original a separate real piece?
- **The Digital Native Ep. 11** — now cited via YouTube, but no podcast by that name exists on Apple.
- Whether **Receipts** still earns its spot now that **The index** exists — they overlap.
- Whether the **Soqratic bot placeholder** (only square-cornered element left) should be rounded.
- Whether **30 Hour Day** should join the "Hi, I'm Rick" prose.

### Known soft spots
- **"What it looks like"** paragraph under Hire me is @writer's *guess* at how Return scopes engagements. It's the money paragraph and needs Rick's real words.
- Index splice into `index.html` is manual — automate it.
- Hero is content-bound (~669px tall), so CTAs clear the fold down to ~640px viewport, not below.

---

## Not done

- **Nothing committed.** `git init` only, no commits, no remote.
- No deploy. No domain. No analytics. No favicon. No OG image.
- Soqratic bot is a placeholder `div#soqratic-slot`.
