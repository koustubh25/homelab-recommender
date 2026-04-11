# Homelab Build Plan — Balanced Talos + LLM Tower

_A phased AM5 tower that joins a Talos cluster now and adds stronger local inference later._

**Region:** AU / VIC / Melbourne  
**Total (median retail):** AUD 2664  
**Confidence:** high

---

## Why this build

- Keeps Talos worker compatibility intact from day one.
- Leaves a clean path to add NVIDIA CUDA inference later without replacing the platform.
- Balances power draw and upgrade headroom for an always-on homelab node.

## Requirements summary

| Requirement | Value |
|---|---|
| Primary use | LLM inference + general k8s |
| Budget | AUD 2500 flexible, phased OK |
| Region | AU / VIC |
| Existing infra | Talos worker node |
| Energy sensitivity | High |

---

## Phase 1 — Deploy a useful Talos worker immediately

_Talos worker with enough local storage and RAM for general cluster workloads and smaller quantized models._

| Part | Choice | Price (median) | Why | Buy |
|---|---|---|---|---|
| CPU | AMD Ryzen 7 7700 | AUD 499 | Efficient 8-core base for mixed workloads | https://example.com/ryzen-7700 |
| Motherboard | MSI B650 Tomahawk WiFi | AUD 329 | AM5 base with expansion headroom | https://example.com/b650-tomahawk |
| RAM | 64GB DDR5-5200 (2x32GB) | AUD 249 | Enough memory for Talos and model headroom | https://example.com/ddr5-64gb |
| Storage | 2TB NVMe Gen4 SSD | AUD 179 | Enough local storage for images and models | https://example.com/2tb-nvme |

**Phase 1 subtotal:** AUD 1196 - 1326 (median 1256)

### Phase 1 delivers

Talos worker capacity now, with smaller local inference workloads possible before the GPU upgrade.

---

## Phase 2 — Add stronger local inference

_Talos-compatible worker with practical CUDA-based medium-model inference._

| Part | Choice | Price (median) | Why | Buy |
|---|---|---|---|---|
| GPU | Used RTX 3090 24GB | AUD 1199 | Best value CUDA path for medium models | https://example.com/used-3090 |
| PSU | Corsair RM850x | AUD 209 | Headroom for the later GPU | https://example.com/rm850x |

**Phase 2 subtotal:** AUD 1288 - 1518 (median 1408)

---

## Running costs

| Scenario | kWh/month | AUD/month | AUD/year |
|---|---|---|---|
| Always-on worker (idle 23h + light 1h) | 36 | 10.8 | 129.6 |
| Light LLM use (~3h/day inference) | 63 | 18.9 | 226.8 |
| Heavy LLM use (~8h/day inference) | 96 | 28.8 | 345.6 |

**Assumed electricity rate:** AUD 0.30 / kWh

### Energy levers

- Set a 250W GPU power limit for roughly 15% lower phase-2 power with minimal inference loss.

---

## Build order & verification

1. Assemble phase 1, update firmware if needed, and bench boot before installing into the final chassis.
2. Join the node to the Talos cluster and verify storage plus memory visibility.
3. Add the GPU and updated PSU in phase 2, then validate NVIDIA/Talos integration.

**Verification checklist:**
- [ ] Talos node joins the existing cluster successfully
- [ ] Idle wall power remains within the modeled phase-1 range
- [ ] CUDA inference works after the GPU upgrade

---

## Known risks

| Risk | Source | Mitigation |
|---|---|---|
| Used GPU condition can vary between listings | compatibility-report | Bench-test the 3090 before putting the node into production |

---

## Data sources

_Generated 2026-04-11 by homelab-recommender._  
_Prices scraped at: 2026-04-11T00:00:00Z._  
_Retailers queried: Mwave, Scorptec, Centre Com, PCCG, eBay AU._
