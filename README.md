# homelab-recommender

A homelab hardware recommendation workflow that runs as a Claude Code plugin and can also be used directly from Codex. It considers DIY builds, prebuilts (Mac mini, Mac Studio, NUC, Beelink, Minisforum), used SFF workstations, and SBCs (Raspberry Pi, Rock 5, Jetson). It fetches live prices and models running costs.

It works especially well for choosing hardware for local AI inference, where tradeoffs like memory bandwidth, VRAM, power draw, noise, and upgrade path matter as much as raw CPU/GPU specs.

## Prerequisite: Playwright MCP (recommended)

Live prices from major retailers (Mwave, Scorptec, Amazon, Apple, etc.) require a headless browser. Without it, the plugin falls back to lower-quality price sources. Set this up **before** installing the plugin.

Add to your Claude Code MCP config:

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

Or add manually to `~/.claude.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Then restart Claude Code.

## Install In Claude Code

```
/plugin marketplace add koustubh25/homelab-recommender
/plugin install homelab-recommender@homelab-recommender
```

## Use In Claude Code

```
/homelab-recommend
```

## Use In Codex

This repo can also be run directly in Codex without extra plugin packaging.

Open the repo in Codex and ask it to run the homelab recommender workflow from this repository.

Example prompt:

```text
Run the homelab recommender.
```

If you want live retailer pricing in Codex, add Playwright MCP there as well:

```bash
codex mcp add playwright -- npx @playwright/mcp@latest
```

Then restart Codex. Without Playwright MCP, the workflow can still run, but the pricing stage will fall back to weaker sources.

## Runtime Model

- Claude Code uses the packaged plugin under `.claude-plugin/`.
- Codex uses the repo directly and follows the same workflow prompts in the repository.
- `commands/`, `agents/`, `lib/`, and `test-fixtures/` are shared across both runtimes.
- `homelab-run/` is the artifact directory in both runtimes.

## Validate Contracts

```bash
python3 scripts/validate_contracts.py
```

This checks the documented JSON handoff shapes across the agents, including DIY, prebuilt, and hybrid candidates.

It also validates a completed golden run fixture under `test-fixtures/golden-run/`, including `constraint-analysis.json`, `compatibility-report.json`, and `PLAN.md`.

The workflow will:

1. Ask you a few questions about what you want the machine to do
2. Check your requirements for impossible combinations
3. Design 1–3 candidate builds
4. **Pause** so you can react before expensive price scraping
5. Fetch live prices from region-appropriate retailers
6. Model running costs in your local currency
7. Verify compatibility
8. Write a `PLAN.md` with parts, prices, buy links, and risks

You can change requirements at any checkpoint and the plugin will re-run only the affected stages.

## Agents

The workflow is a pipeline of seven specialized agents:

- **intake-advisor** — Asks one focused question at a time to build a structured requirements profile. Supports patch mode for changing requirements mid-flow.
- **constraint-analyzer** — Catches impossible requirement intersections (e.g. "ARM + Talos + modular + under $2k") before any build design happens.
- **architect** — Designs 1–3 candidate builds across DIY, prebuilt, mini PC, SBC, and hybrid types. Reasons from requirements, not from patterns.
- **price-scraper** — Fetches live prices from region-appropriate retailers using Playwright (preferred), WebFetch, or WebSearch. Reports min/median/max with source quality tiers.
- **energy-modeler** — Computes idle and load power draw, converts to monthly/yearly cost in local currency, and identifies energy-saving levers.
- **compatibility-checker** — Verifies socket/RAM/PSU/case fit, BIOS support, OS/distro compatibility, and SKU drift between architect and scraped prices.
- **plan-writer** — Renders the final `PLAN.md` with parts tables, buy links, energy costs, and risks. Pure synthesis — no new decisions.

## Region

Defaults to Australia. Other regions are supported via `lib/retailers.json` and `lib/electricity-rates.json` — contributions welcome.
