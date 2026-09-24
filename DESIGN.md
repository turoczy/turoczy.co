# Design plan — turoczy.com

## Subject
Rick Turoczy. Portland. 19 years of Silicon Florist. Selling keynotes + consulting. Audience: conference programmers, corporate innovation leads, economic development orgs, founders with budget.

## The idea the design is built on
"Collecting dots, connecting dots" — his TEDxPortland thesis. Dots are the system, not decoration: the nav is a dot rail, sections are marked with dots, the hero is a field of collected dots with a few connections drawn once on load. Second thread: Silicon *Florist* is a joke about the Silicon *Forest* — the small things growing under the canopy. Hence a forest-floor palette, not a tech palette.

## Color
| Token | Hex | Role |
|---|---|---|
| `--ash` | `#E7E8E2` | page ground — pale lichen, cool. Deliberately NOT the cream/#F4F1EA default. |
| `--fir` | `#14241E` | ink — deep Douglas fir. Near-black but unmistakably green. |
| `--moss` | `#5C7F63` | dots, rules, secondary text |
| `--rose` | `#B8365E` | Rose City. Connections, links, primary CTA. The only hot color. |
| `--bloom` | `#F3F2EC` | raised surface, barely lighter than ash |

Dark mode swaps ground/ink; rose and moss hold.

## Type
- **Display: Fraunces** — variable wonky serif, soft optical sizing. Handmade, slightly odd, warm. H1, section headings, pull quotes.
- **Body: Archivo** — grotesque, slightly condensed, newsy. Everything else.
- Fluid scale via `clamp()`. Prose capped at 68ch.

## Layout
```
 ┌──────────────────────────────────────────────┐
 │  RICK TUROCZY            [dot field w/ lines]│   hero, full bleed
 │  headline, big Fraunces                      │
 │  subhead ................  [book] [hire]     │
 ├───┬──────────────────────────────────────────┤
 │ ● │  Hi                                      │   left dot-rail nav is sticky
 │ ● │  ─────────  heading hangs left,          │   on desktop; horizontal
 │ ● │             body in wider right column   │   scroll strip on mobile
 │ ○ │                                          │
 └───┴──────────────────────────────────────────┘
```
Left-aligned throughout. No centered text blocks. Asymmetric two-column sections (hanging heading left, content right) at ≥960px; single column below.

## Principles
1. Dots carry information — nav position, section markers, quote markers. Never sprinkled as texture.
2. One motion moment: the hero draws ~7 connections on load, once, then rests. `prefers-reduced-motion` skips straight to the resting state.
3. No uniform rounded cards with soft grey shadows. Press quotes are hanging blockquotes; talks are a ruled list.
4. Banned chrome: ALL-CAPS eyebrows, `→` on buttons, `A · B · C` meta strings, monospace data labels.
5. Boldness is spent in exactly one place — the hero type + dot field. Everything below is quiet.
