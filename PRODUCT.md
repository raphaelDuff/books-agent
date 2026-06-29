# Product

## Register

product

## Users

A single, sophisticated reader who knows roughly what they're in the mood for but
not which book — they can describe a *feeling*, a *vibe*, an *era*, or a hard
constraint ("highly rated fantasy from the 2000s") but can't name the title. In the
immediate term the user is also a **technical interviewer** evaluating this as an AI
Engineer take-home: they will judge product/UX thinking alongside the engineering, so
the surface has to read as both a usable recommender and a deliberate piece of craft.

Context of use: desktop or laptop, a focused single-session lookup. They type a
plain-language request, read a short ranked list, and either pick one or rephrase.
No accounts, no library to manage — one query, one good answer, repeat.

## Product Purpose

Book Recommender Agent turns a natural-language request into a short, ranked list of
books with a one-line justification per pick. Its reason to exist is the *hybrid*
retrieval underneath: an LLM router classifies each request as structured, semantic,
or hybrid, runs SQL filters and/or filtered vector search over ~6,800 books, then
reranks and justifies with an LLM. Pure SQL can't answer "melancholic about memory";
pure embeddings lose "from the 2000s, highly rated" — the combination is the value.

Success: the user reads the picks and thinks "yes, that's what I meant," and a
technically literate viewer can *see how it got there* — the routed intent and the
generated SQL are surfaced as first-class transparency, not hidden plumbing.

## Brand Personality

Warm and inviting, in the key of a thoughtfully designed independent bookshop — the
kind with good paper stock, real typographic care, and books treated as objects worth
looking at. Three words: **literary, considerate, transparent.**

Voice is plain and human (it asks you to "ask in plain language" and means it), never
chatbot-chirpy and never enterprise-stiff. The warmth is carried by typography, paper
tones, and the way covers are presented — not by decoration. Underneath the softness
is quiet engineering confidence: it shows its work without bragging.

## Anti-references

- **Generic AI-chat UI.** No bubble threads, blinking cursors, "assistant is typing,"
  or gradient-purple-everything. This is a recommender, not a chat clone.
- **Bootstrap / admin-template SaaS.** No default-component gray card grids, no dashboard
  chrome, no stock UI-kit feel.
- **Goodreads / Amazon retail clutter.** No dense commerce listings, star-rating noise,
  buy-buttons, or ad-heavy layouts. Restraint over density.
- **Over-designed startup landing.** No big hero gradients, floating 3D mockups, or
  marketing fluff layered over what is fundamentally a working tool.

## Design Principles

1. **The books are the hero.** Covers, titles, and the "why this pick" line are the
   payload; everything else (input, chrome, controls) recedes so the recommendations
   carry the page.
2. **Transparency is a feature, not debug output.** The routed intent and generated SQL
   are presented with intent and care — proof of how the answer was reached, styled to
   be read, not a collapsed dev panel afterthought.
3. **Warmth through craft, not decoration.** Personality comes from type, paper tones,
   spacing rhythm, and cover treatment — never from gradients, glass, or ornament.
4. **One good answer, fast.** The path from question to ranked picks is the whole
   product; protect its directness. No step, control, or flourish that doesn't move
   the user toward a pick.
5. **Show the work without shouting.** Engineering confidence reads as calm and legible,
   not loud — restraint is the tell of a designer who didn't need to over-explain.

## Accessibility & Inclusion

Target **WCAG 2.1 AA.** Body text ≥4.5:1 against its background (large/bold text ≥3:1),
placeholder text held to the same body bar. Visible, non-color focus indicators on every
interactive element; full keyboard operability for the query box, example chips, and the
expandable SQL/description disclosures. Honor `prefers-reduced-motion` with a crossfade or
instant alternative for every transition. Intent badges and ratings must not rely on color
alone — pair with text/labels. Cover images always carry meaningful `alt`.
