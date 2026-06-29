---
name: Book Recommender Agent
description: A natural-language book recommender — a drenched oxblood "cover" opening onto warm-paper "pages", where books are objects and the tool speaks quietly.
colors:
  ground:          "oklch(0.976 0.006 40)"
  ground-raised:   "oklch(0.992 0.004 45)"
  ink:             "oklch(0.245 0.018 35)"
  ink-soft:        "oklch(0.455 0.018 35)"
  ink-faint:       "oklch(0.585 0.016 38)"
  hairline:        "oklch(0.885 0.010 45)"
  oxblood:         "oklch(0.395 0.115 27)"
  oxblood-deep:    "oklch(0.320 0.105 27)"
  oxblood-ink:     "oklch(0.300 0.100 27)"
  accent:          "oklch(0.470 0.150 28)"
  accent-deep:     "oklch(0.400 0.140 28)"
  cloth-glow:      "oklch(0.46 0.12 30 / 0.55)"
  cover-edge:      "oklch(0.30 0.05 35 / 0.12)"
  sql-ink:         "oklch(0.36 0.05 28)"
  bone:            "oklch(0.955 0.012 70)"
  bone-soft:       "oklch(0.870 0.020 60)"
  gilt:            "oklch(0.860 0.050 65)"
  gilt-hover:      "oklch(0.900 0.050 65)"
  cloth-line:      "oklch(0.500 0.075 28)"
  tab-structured-bg:  "oklch(0.930 0.030 245)"
  tab-structured-ink: "oklch(0.400 0.075 250)"
  tab-semantic-bg:    "oklch(0.935 0.034 330)"
  tab-semantic-ink:   "oklch(0.420 0.090 333)"
  tab-hybrid-bg:      "oklch(0.935 0.034 155)"
  tab-hybrid-ink:     "oklch(0.385 0.072 156)"
  error-bg:        "oklch(0.945 0.035 30)"
  error-border:    "oklch(0.760 0.110 30)"
  error-ink:       "oklch(0.430 0.150 28)"
typography:
  display:
    fontFamily: "Fraunces Variable, Georgia, serif"
    fontSize: "clamp(2.4rem, 6vw, 4rem)"
    fontWeight: 600
    lineHeight: 0.98
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Fraunces Variable, Georgia, serif"
    fontSize: "clamp(1.15rem, 2.5vw, 1.45rem)"
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: "normal"
  title:
    fontFamily: "Fraunces Variable, Georgia, serif"
    fontSize: "1.3rem"
    fontWeight: 600
    lineHeight: 1.18
    letterSpacing: "-0.01em"
  prose:
    fontFamily: "Fraunces Variable, Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
  body:
    fontFamily: "Inter Variable, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  meta:
    fontFamily: "Inter Variable, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "normal"
  label:
    fontFamily: "Inter Variable, system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.06em"
  code:
    fontFamily: "ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "0.83rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
rounded:
  cover: "3px"
  sm: "7px"
  md: "10px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "36px"
  section: "clamp(2rem, 5vw, 3.25rem)"
components:
  button-primary:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.oxblood-deep}"
    rounded: "{rounded.md}"
    padding: "0 1.5rem"
  input-ask:
    backgroundColor: "{colors.ground-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0.95rem 1.05rem"
  prompt-link:
    backgroundColor: "{colors.oxblood}"
    textColor: "{colors.bone}"
    typography: "{typography.prose}"
    padding: "0.1rem 0"
  tab-hybrid:
    backgroundColor: "{colors.tab-hybrid-bg}"
    textColor: "{colors.tab-hybrid-ink}"
    rounded: "{rounded.pill}"
    padding: "0.25rem 0.6rem"
  sql-artifact:
    backgroundColor: "{colors.ground-raised}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.md}"
    padding: "0.7rem 1rem"
---

# Design System: Book Recommender Agent

## 1. Overview

**Creative North Star: "Cloth & Paper"**

The interface is built as a book is bound: a **drenched oxblood cloth "cover"** at the top
carries the ask — the wordmark, the question field, the example prompts — and it opens, across
a fine bone seam, onto warm-paper **"pages"** where the recommendations are read. The two
materials do real work. Cloth (a rich, slightly desaturated oxblood, `oklch(0.395 0.115 27)`)
signals *this is where you ask*; paper (a warm off-white tinted toward the brand's own red,
`oklch(0.976 0.006 40)`) signals *this is where you read*. Nothing is dark, nothing is a
dashboard.

The whole system is organized around one strategic line from PRODUCT.md — **the books are
the hero**. It shows up as a *dual typographic voice*: the books speak in a literary serif
(Fraunces) — wordmark, titles, the "why this pick" justification; the tool speaks in a quiet
sans (Inter) — input, buttons, meta, the intent chip. It shows up again in the **covers as
physical objects**: each sits on the paper with a soft contact shadow and a hair-thin edge,
liftable on hover, never boxed in a card. And it shows up in the **shelf**: a ranked, annotated
list — serif numeral, cover, title, prose reason — not a grid of identical tiles.

This system explicitly rejects what PRODUCT.md names: the dark Bootstrap/admin dashboard the
app used to be, generic AI-chat UI, Goodreads/Amazon retail clutter, over-designed startup
landing fluff — **and** the AI "cozy-books = cream-sepia-Garamond" reflex. The warmth here is
carried by a committed oxblood, a characterful serif, and the way book covers are presented,
never by a sand-colored body or a sepia wash.

**Key Characteristics:**
- A drenched oxblood "cover" up top; warm-paper "pages" below, joined by a bone seam.
- Dual voice: Fraunces serif for the books, Inter sans for the tool.
- Covers are objects on paper (contact shadow, edge, hover-lift) — never carded.
- Results are a ranked annotated shelf with uniform 140px cover objects.
- One committed accent (oxblood) for actions, links, ranking, ratings; intent uses quiet tabs.
- Transparency styled with dignity: plain-language intent + a framed SQL artifact.

## 2. Colors

A two-material palette: a saturated oxblood cloth and a warm-paper reading ground, joined by
one accent that is simply the cloth color brought to the surface.

### Primary
- **Oxblood Bookcloth** (`oklch(0.395 0.115 27)`): The drenched cover surface — masthead field,
  the ground the ask sits on. Deepens to `oxblood-deep` (`0.320`) at the seam shadow and on
  pressed states.
- **Accent** (`oklch(0.470 0.150 28)`): The same hue brought onto paper — ranking numerals,
  links, disclosure carets, the opening quote mark on each reason. `accent-deep` (`0.400`) for
  hover and the rating star/score.

### Neutral — paper & ink
- **Ground** (`oklch(0.976 0.006 40)`): The warm-paper reading surface. Near-white, chroma
  barely tilted toward the brand red — deliberately NOT cream/sand.
- **Ground Raised** (`oklch(0.992 0.004 45)`): The SQL artifact and the inset ask field.
- **Ink** (`oklch(0.245 0.018 35)`): Primary text on paper — titles, the read line.
- **Ink Soft** (`oklch(0.455 0.018 35)`): Bylines, counts, descriptions, summary labels.
- **Ink Faint** (`oklch(0.585 0.016 38)`): Placeholders, separators, the colophon.
- **Hairline** (`oklch(0.885 0.010 45)`): Entry dividers, the SQL frame, cover edges.

### On-cloth — text & UI sitting on oxblood
- **Bone** (`oklch(0.955 0.012 70)`): Primary text on the cloth — wordmark, prompts, button face.
- **Bone Soft** (`oklch(0.870 0.020 60)`): The tagline and the "Try —" lead. (Verified ≥4.5:1
  against the lightest point of the cloth gradient.)
- **Gilt** (`oklch(0.860 0.050 65)`): The single warm-gold emphasis — the italic word in the
  wordmark and the focus-ring glow on the cloth field. Used sparingly, like foil stamping.
  `gilt-hover` (`0.900`) is the lighter hover state for the button face and the "Try —" prompts.

### Derived & overlay (not new hues — alpha/lightness derivations of the above)
- **Cloth Glow** (`oklch(0.46 0.12 30 / 0.55)`): the lit highlight in the cloth's radial
  vignette — a lighter oxblood at 55% over the cloth field. Material depth, not a new color.
- **Cover Edge** (`oklch(0.30 0.05 35 / 0.12)`): the warm 1px hairline around each cover object,
  the same ink family as the contact shadow.
- **SQL Ink** (`oklch(0.36 0.05 28)`): the monospace text inside the generated-SQL artifact — a
  readable oxblood-leaning ink, distinct from body `ink` so code reads as code.

### Tertiary — intent (quiet catalog tabs, never loud badges)
- **Structured** (bg `oklch(0.930 0.030 245)` / ink `oklch(0.400 0.075 250)`): cool blue tab.
- **Semantic** (bg `oklch(0.935 0.034 330)` / ink `oklch(0.420 0.090 333)`): plum tab.
- **Hybrid** (bg `oklch(0.935 0.034 155)` / ink `oklch(0.385 0.072 156)`): green tab.
- **Error** (bg `oklch(0.945 0.035 30)` / border `oklch(0.760 0.110 30)` / ink `oklch(0.430 0.150 28)`):
  a deeper kin of the brand red, not an alien alert-red.

### Named Rules
**The Cloth-and-Paper Rule.** Oxblood is *where you ask*; paper is *where you read*. Never put
long reading prose on the cloth, and never tint the paper toward sand to "warm it up" — the
warmth is the cloth's job, carried by accent, type, and covers.

**The One-Hue Accent Rule.** The accent is the cloth color surfaced — every interactive and
ranking mark on paper is one oxblood hue (27–28). The three intent tints are *status semantics*,
quiet and desaturated; they never compete with the accent for attention.

## 3. Typography

**Display / Book voice:** Fraunces Variable (with Georgia, serif) — optical-sizing on.
**Tool voice:** Inter Variable (with system-ui, sans).
**Code voice:** system monospace (`ui-monospace, SF Mono, Menlo`).

**Character:** A deliberate contrast pairing — an old-style literary serif with personality
(Fraunces, optical sizing lets titles take the high-contrast cut) against a neutral humanist
grotesque (Inter). The split is semantic, not decorative: serif = the books, sans = the machine.

### Hierarchy
- **Display / Wordmark** (Fraunces 600, `clamp(2.4rem, 6vw, 4rem)`, lh 0.98, -0.02em): the
  masthead lockup only. One italic word set in gilt.
- **Headline / Read line** (Fraunces 500, `clamp(1.15rem, 2.5vw, 1.45rem)`, lh 1.35): the
  plain-language "how I read your request" sentence.
- **Title** (Fraunces 600, 1.3rem, lh 1.18): book titles.
- **Prose / Reason** (Fraunces 400, 1.0625rem, lh 1.55, ≤64ch): the "why this pick" justification
  and descriptions — the book's own voice, given room.
- **Body** (Inter 400, 1.0625rem, lh 1.5, ≤46ch): the cloth tagline.
- **Meta** (Inter 400, 0.875rem): byline (author · year · ★rating), counts.
- **Label** (Inter 600, 0.78rem, 0.06em; uppercase on the SQL summary): the intent tab and the
  "Generated SQL" disclosure.
- **Rank** (Fraunces 500, 1.5rem, lining numerals): the ranked sequence markers.
- **Code** (mono, 0.83rem, lh 1.6): the generated SQL.

### Named Rules
**The Dual-Voice Rule.** If it's part of a book — a title, a reason, a description — it's set in
the serif. If it's part of the tool — a button, a field, a label, a count — it's set in the
sans. Never a display serif on a control; never sans on the reading prose.

**The Earned-Numeral Rule.** Serif rank numerals appear only because the picks are a genuine
ranked sequence. They are not a decorative `01 / 02 / 03` scaffold and appear nowhere else.

## 4. Elevation

A light system that uses **soft, warm shadows as a deliberate material** — a shift from the old
flat baseline. Shadows are reserved for two jobs: making book covers read as physical objects on
the paper, and lifting the SQL artifact a touch off the page. The cloth carries depth differently —
through a radial vignette and a shadowed seam where it meets the paper, not a drop shadow.

### Shadow Vocabulary
- **Cover Contact** (`0 1px 1px …/0.10, 0 8px 18px …/0.16`, warm-tinted): every cover at rest —
  a soft contact shadow that sets the book on the paper.
- **Cover Lift** (`0 2px 3px …/0.12, 0 16px 34px …/0.24`): the cover on hover/focus, paired with a
  4px rise — the book being picked up.
- **Artifact** (`0 1px 2px …/0.05, 0 6px 16px …/0.07`): the framed SQL receipt, barely raised.
- **Cloth Seam** (`box-shadow: 0 -10px 24px …/0.45` under a 1px bone rule): the cloth→paper hinge.

### Named Rules
**The Object-or-Frame Rule.** Shadow exists to make a book an object or to frame the one query
artifact — nothing else. No shadowed cards, no decorative drop shadows on text or panels.

## 5. Components

### Buttons
- **Shape:** 10px radius.
- **Primary ("Recommend"):** bone face (`oklch(0.955 0.012 70)`) with oxblood-deep ink, Inter 600,
  sitting on the cloth — like a label sewn onto cloth. Hover warms toward gilt and rises 1px.
- **Disabled:** 0.55 opacity, `not-allowed`. Loading swaps the label to "Reading…".

### Inputs / Fields
- **Ask field:** paper-white (`ground-raised`) inset into the cloth with an inner shadow, no
  visible border at rest — sewn-in, not bolted-on. 10px radius, Inter 1.0625rem.
- **Focus:** a gilt glow ring (`0 0 0 3px gilt/0.55`), not a hard outline — warm, on-brand.
- **Placeholder:** `ink-faint`, held to the same contrast bar as body.

### Prompt links ("Try —")
- **Style:** Fraunces serif, bone, on the cloth, with a hairline underline — understated
  invitations, deliberately NOT pills. Hover shifts text and underline to gilt.

### Intent tabs
- **Style:** small Inter pill, desaturated tinted background + darker ink of the same hue, with a
  leading filled dot. One of structured / semantic / hybrid. Reads as a quiet catalog tab.
- **Pairing:** always accompanied by the plain-language read line and a text label — never
  color-only.

### The Shelf — annotated recommendation entry (signature)
- **Structure:** a 3-column grid — serif rank numeral / cover object / body — with a hairline
  divider between entries. No card, no border box.
- **Cover:** 2:3 image, 3px radius (`--radius-cover`), contact shadow + 1px warm edge
  (`cover-edge`); a uniform **`140px`** across every entry. Wrapped in a link to the book; hover lifts it.
- **Body:** serif title, Inter byline (author · year · ★rating in accent), then the serif reason
  opened by an accent quote mark (a bookplate mark, not an uppercase eyebrow). Optional
  "Full description" disclosure in serif.
- **Order:** entries are uniform; rank is carried by the leading serif numeral alone, never by
  resizing one entry. (Earlier revisions enlarged the #1 pick; that hierarchy was removed in
  favour of a calm, even shelf.)
- **Responsive:** under 560px the grid recomposes — rank tucks above the cover, body spans beside;
  covers step down to `110px`.

### The Generated-SQL artifact (signature)
- **Style:** a framed receipt on `ground-raised` with a hairline and the faint Artifact shadow.
  An uppercase Inter "Generated SQL" summary with a rotating accent caret; the SQL itself in
  monospace, wrapped, ink-soft, divided by a hairline. Open by default — transparency presented
  with pride, not hidden in a muted dev panel.

### States
- **First-run:** an italic serif invitation on the paper that teaches what to ask for; the cloth
  masthead is the hero.
- **Loading:** paper-toned skeleton shelf entries with a shimmer — never a center spinner.
- **Error:** a warm error note (deeper brand-red kin) with a plain-language repair suggestion.
- **No matches:** an italic serif line suggesting how to loosen the request.

## 6. Do's and Don'ts

### Do:
- **Do** keep oxblood as *where you ask* and paper as *where you read*; carry warmth through the
  cloth, the serif, and the covers — never by tinting the paper toward sand.
- **Do** set every book element (title, reason, description) in Fraunces serif and every tool
  element (control, label, count) in Inter sans — the Dual-Voice Rule.
- **Do** present covers as objects on the paper: contact shadow, 3px radius, 1px edge, hover-lift.
  Every cover is a uniform 140px object; ranking is carried by the serif numeral, not by resizing.
- **Do** keep the one oxblood accent for actions, links, ranking and ratings; keep the three
  intent tints quiet and desaturated, always paired with a text label.
- **Do** present the routed intent in plain language and frame the generated SQL as a dignified
  artifact, open by default.
- **Do** hold all text to WCAG AA (≥4.5:1) — including bone-soft on the cloth gradient's lightest
  point; give the cloth field a visible gilt focus ring.

### Don't:
- **Don't** revert toward the old **dark Bootstrap/admin-template dashboard** (`#0f1115` field,
  blue accent) — the explicit anti-reference this redesign replaced.
- **Don't** drift into **generic AI-chat UI** (bubble threads, blinking cursors, gradient-purple)
  or **Goodreads/Amazon retail clutter** (dense listings, star-rating noise, buy buttons).
- **Don't** fall into the **cozy-books AI reflex**: cream/sand body, sepia wash, or a generic
  Garamond. The body is a near-white at the brand's own hue; the serif is characterful Fraunces.
- **Don't** box the picks in a **card grid** — the shelf is a ranked, annotated list, ordered by
  the serif numerals (uniform entries, not resized tiles).
- **Don't** use an **uppercase tracked eyebrow** above the reason (the old "WHY THIS PICK") — the
  accent quote mark carries it; numerals appear only as the real ranked sequence.
- **Don't** add shadow as decoration — shadow makes a book an object or frames the SQL artifact,
  nothing else.
