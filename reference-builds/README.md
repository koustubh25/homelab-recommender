## What this folder is

A small library of **example builds** the architect agent has seen work in practice. They exist to broaden the architect's search space — not to narrow it.

## What this folder is NOT

- A list of recommended builds
- A default the architect should fall back to
- A pattern to match against the user's requirements

## How the architect must use these

**Read the user's requirements first. Design from those.** Reference builds are inspiration for *what's possible* in similar problem spaces, not templates to copy.

When evaluating a reference build:

1. Does the user's binding constraint match this build's binding constraint? If not, ignore it.
2. For every part you'd reuse, can you justify it against *this user's* requirements — not against the build it came from? If not, pick something else.
3. If the user's requirements point somewhere none of these builds go (different region, different ecosystem, different form factor), design from scratch. The absence of a matching reference build is not a reason to recommend a poor fit.

The reference builds are AU-centric and skewed toward Talos/k8s + LLM use cases because that's what the project started with. **Do not let that bias your recommendations** for users with different needs.

## File format

Each build is a markdown file with frontmatter:

```yaml
---
name: Short build name
type: diy | prebuilt | sbc | hybrid
binding_constraint: What this build was optimized for
region: AU
year: 2026
status: built | designed | retired
---
```

The body documents the parts, the rationale at the time, what the user actually wanted, and (if known) how it performed. Honest postmortems are more valuable than glossy spec sheets — if a part disappointed, write that down.

## Adding a new reference build

Only add builds where you can say *why* the choices were made and *what constraints they were solving*. A parts list with no rationale is noise, not signal. Better to have 3 well-documented references than 30 anonymous ones.
