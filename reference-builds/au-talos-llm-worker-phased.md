---
name: AU Talos+LLM Worker (Phased AM5)
type: diy
binding_constraint: budget + future GPU upgrade path + Talos worker compatibility
region: AU
year: 2026
status: designed
---

## What the user wanted

- Join an existing Talos k8s cluster as a worker (existing cluster was full)
- Run small/medium open-source LLMs locally
- Run general k8s workloads alongside LLMs
- Modular: buy platform first, add GPU later
- Budget around AU$2,000, flexible
- Located in Melbourne, energy-cost sensitive
- Comfortable with used parts for the GPU

## Binding constraint

Two constraints fought each other: tight Phase 1 budget *and* the need to support a high-TDP GPU later (Phase 2). This forced a beefy PSU and a board with proper PCIe x16 in Phase 1, both of which would have been "overkill" without the Phase 2 plan.

## Phase 1 — platform (~AU$1,650)

| Part | Choice | Why |
|---|---|---|
| CPU | Ryzen 7 7700 (65W) | Low TDP for energy budget; 8 cores enough for k8s workloads + small LLM CPU offload; AM5 socket has upgrade path through Zen 5 |
| Motherboard | MSI MAG B650 Tomahawk (non-WiFi preferred) | Solid VRM for future CPU upgrades; dual M.2; full x16 slot for Phase 2 GPU; non-WiFi saves cost on a wired homelab node |
| RAM | 64GB DDR5-5200 (2×32GB dual-rank) | Enough for k8s + CPU offload of medium LLMs. Capped at 5200 by Ryzen 7000 spec for 2×32GB dual-rank — do NOT buy 5600 expecting 5600 |
| Storage | WD SN850X 2TB NVMe Gen4 | Model storage + container images + datasets; Gen4 is the sweet spot, Gen5 not worth the price premium |
| PSU | Corsair RM1000x (1000W 80+ Gold) | Sized for Phase 2 (3090 + CPU peak ≈ 450W); runs at <50% load in Phase 2 = efficiency sweet spot. Oversized for Phase 1 alone but locked in for the upgrade path |
| Case | Fractal North Mesh | Good airflow for future GPU; clean aesthetics; standard ATX; fits 170mm cooler |
| Cooler | Thermalright Peerless Assassin 120 SE | Massively over-spec for 65W CPU but cheap and silent; ~AU$50 |

**Phase 1 delivers:** Working Talos worker node; runs general k8s workloads; runs small LLMs (≤8B Q4) on CPU at usable speeds (~5–8 tok/s).

## Phase 2 — GPU (~AU$900–1,200 used)

| Part | Choice | Why |
|---|---|---|
| GPU | Used RTX 3090 (24GB) | Best $/VRAM in 2026 for local LLM. CUDA ecosystem mature on Talos via `nonfree-kmod-nvidia` extension. 24GB fits 13B Q8 / 34B Q4 entirely in VRAM |

**Phase 2 delivers:** Medium LLMs (13–34B Q4) at 30–60 tok/s in VRAM. 70B Q4 possible with CPU offload at ~8–12 tok/s.

## Energy (Melbourne, AU$0.30/kWh)

- Phase 1 always-on: ~45W idle → ~AU$10/month
- Phase 2 always-on + light LLM use (1h/day inference): ~AU$16/month
- Phase 2 + heavy LLM use (8h/day): ~AU$29/month

## What this build deliberately does NOT do

- **Not silent.** 3090 under load is audible. Don't recommend this for a bedroom.
- **Not small.** Mid-tower ATX. Don't recommend if user asked for SFF.
- **Not Apple-compatible.** Talos requirement rules out Mac mini / Mac Studio entirely.
- **Not the cheapest.** A used SFF workstation would be ~AU$600 cheaper if user dropped the GPU upgrade path.

## Honest postmortem flags

- BIOS version on the B650 Tomahawk needs to be 7D75v1A or later for 7000-series support out of the box. Verify before buying — older stock exists.
- The 2×32GB DDR5-5200 ceiling is a real Ryzen 7000 limitation. Architect agents have made the mistake of recommending 5600 kits for this exact configuration.
- AliExpress had this CPU listed at ~AU$220 during a flash sale but couldn't ship to AU. Listing pricing is unreliable for this category — always cross-check shipping availability before recommending.
- Non-WiFi B650 Tomahawk is sometimes hard to find in AU stock — WiFi variant is a fine substitute (~AU$28 more), it's a functional superset.

## When this build is the wrong answer

- User wants silent → look at Mac mini / Mac Studio
- User wants tiny → look at Minisforum MS-01 or used SFF
- User wants <AU$1,000 → look at used HP EliteDesk + RAM upgrade
- User has no Talos / k8s requirement → Mac mini M4 Pro is probably better for LLM-only
- User wants 70B inference at fast speeds → needs 2× 3090 or A6000, this build won't get there
