#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "test-fixtures"


def load_json(path: Path):
    with path.open() as handle:
        return json.load(handle)


def expect(condition, message, errors):
    if not condition:
        errors.append(message)


def validate_requirements(data, errors):
    expect(isinstance(data.get("use_cases"), list), "requirements.use_cases must be a list", errors)
    region = data.get("region", {})
    expect(isinstance(region.get("country"), str), "requirements.region.country must be a string", errors)
    expect(
        isinstance(region.get("state_or_city"), str) or region.get("state_or_city") is None,
        "requirements.region.state_or_city must be a string or null",
        errors,
    )


def validate_build_candidates(data, errors):
    candidates = data.get("candidates")
    expect(isinstance(candidates, list) and candidates, "build-candidates.candidates must be a non-empty list", errors)
    recommendation = data.get("recommendation", {})
    expect(isinstance(recommendation.get("preferred_candidate"), str), "recommendation.preferred_candidate missing", errors)

    for candidate in candidates or []:
        candidate_id = candidate.get("id", "<missing>")
        candidate_type = candidate.get("type")
        expect(candidate_type in {"diy", "prebuilt", "sbc", "hybrid"}, f"{candidate_id}: invalid candidate type", errors)

        if candidate_type == "diy":
            phases = candidate.get("phases")
            expect(isinstance(phases, list) and phases, f"{candidate_id}: diy candidate must have phases", errors)
        elif candidate_type in {"prebuilt", "sbc"}:
            unit = candidate.get("unit", {})
            expect(isinstance(unit.get("sku"), str), f"{candidate_id}: prebuilt/sbc candidate must have unit.sku", errors)
        elif candidate_type == "hybrid":
            unit = candidate.get("unit", {})
            upgrades = candidate.get("upgrades")
            expect(isinstance(unit.get("sku"), str), f"{candidate_id}: hybrid candidate must have unit.sku", errors)
            expect(isinstance(upgrades, list), f"{candidate_id}: hybrid candidate must have upgrades list", errors)


def extract_priced_items(candidate_type, priced_candidate):
    if candidate_type == "diy":
        items = []
        for phase in priced_candidate.get("phases", []):
            items.extend(phase.get("parts", []))
        return items
    if candidate_type in {"prebuilt", "sbc"}:
        return [priced_candidate.get("unit", {})]
    if candidate_type == "hybrid":
        items = [priced_candidate.get("unit", {})]
        items.extend(priced_candidate.get("upgrades", []))
        return items
    return []


def validate_priced_builds(data, build_candidates, errors):
    expect(isinstance(data.get("currency"), str), "priced-builds.currency must be a string", errors)
    candidate_map = {candidate["id"]: candidate for candidate in build_candidates.get("candidates", [])}

    for candidate in data.get("candidates", []):
        candidate_id = candidate.get("id")
        source = candidate_map.get(candidate_id)
        expect(source is not None, f"priced-builds references unknown candidate {candidate_id}", errors)
        if source is None:
            continue

        candidate_type = source.get("type")
        if candidate_type == "diy":
            phases = candidate.get("phases")
            expect(isinstance(phases, list) and phases, f"{candidate_id}: priced diy candidate must have phases", errors)
            parts = phases[0].get("parts", []) if phases else []
            validate_part_collection(parts, f"{candidate_id}.phases[0].parts", errors)
        elif candidate_type in {"prebuilt", "sbc"}:
            validate_priced_unit(candidate.get("unit"), f"{candidate_id}.unit", errors)
        elif candidate_type == "hybrid":
            validate_priced_unit(candidate.get("unit"), f"{candidate_id}.unit", errors)
            validate_part_collection(candidate.get("upgrades", []), f"{candidate_id}.upgrades", errors)

        total = candidate.get("candidate_total", {})
        expect(isinstance(total.get("median"), (int, float)), f"{candidate_id}.candidate_total.median must be numeric", errors)


def validate_priced_unit(unit, prefix, errors):
    expect(isinstance(unit, dict), f"{prefix} must be an object", errors)
    if not isinstance(unit, dict):
        return
    expect(isinstance(unit.get("sku"), str), f"{prefix}.sku must be a string", errors)
    validate_retail_block(unit.get("retail"), prefix, errors)


def validate_part_collection(parts, prefix, errors):
    expect(isinstance(parts, list), f"{prefix} must be a list", errors)
    if not isinstance(parts, list):
        return
    for index, part in enumerate(parts):
        label = f"{prefix}[{index}]"
        expect(isinstance(part.get("category"), str), f"{label}.category must be a string", errors)
        expect(isinstance(part.get("spec"), str), f"{label}.spec must be a string", errors)
        validate_retail_block(part.get("retail"), label, errors)


def validate_retail_block(retail, prefix, errors):
    expect(isinstance(retail, dict), f"{prefix}.retail must be an object", errors)
    if not isinstance(retail, dict):
        return
    for field in ("min", "median", "max"):
        expect(isinstance(retail.get(field), (int, float)), f"{prefix}.retail.{field} must be numeric", errors)
    expect(isinstance(retail.get("low_confidence"), bool), f"{prefix}.retail.low_confidence must be bool", errors)
    quotes = retail.get("quotes")
    expect(isinstance(quotes, list), f"{prefix}.retail.quotes must be a list", errors)
    for q_index, quote in enumerate(quotes or []):
        q_prefix = f"{prefix}.retail.quotes[{q_index}]"
        expect(
            quote.get("source_quality") in {
                "playwright_direct",
                "webfetch_direct",
                "webfetch_aggregator",
                "search_result",
                "unavailable",
            },
            f"{q_prefix}.source_quality is invalid",
            errors,
        )


def validate_energy_model(data, errors):
    expect(isinstance(data.get("rate_source"), str), "energy-model.rate_source must be a string", errors)
    expect(isinstance(data.get("candidates"), list) and data.get("candidates"), "energy-model.candidates must be non-empty", errors)


def validate_constraint_analysis(data, errors):
    expect(data.get("verdict") in {"clear", "warnings", "blocked"}, "constraint-analysis.verdict is invalid", errors)
    expect(isinstance(data.get("blockers"), list), "constraint-analysis.blockers must be a list", errors)
    expect(isinstance(data.get("warnings"), list), "constraint-analysis.warnings must be a list", errors)


def validate_compatibility_report(data, build_candidates, errors):
    candidate_map = {candidate["id"]: candidate for candidate in build_candidates.get("candidates", [])}
    report_candidates = data.get("candidates")
    expect(isinstance(report_candidates, list) and report_candidates, "compatibility-report.candidates must be a non-empty list", errors)
    for candidate in report_candidates or []:
        candidate_id = candidate.get("id")
        expect(candidate_id in candidate_map, f"compatibility-report references unknown candidate {candidate_id}", errors)
        expect(
            candidate.get("verdict") in {"pass", "pass_with_warnings", "fail"},
            f"{candidate_id}: invalid compatibility verdict",
            errors,
        )
        expect(isinstance(candidate.get("checks"), list), f"{candidate_id}: compatibility checks must be a list", errors)
        expect(isinstance(candidate.get("warnings"), list), f"{candidate_id}: compatibility warnings must be a list", errors)
        expect(isinstance(candidate.get("blockers"), list), f"{candidate_id}: compatibility blockers must be a list", errors)


def validate_cross_file_consistency(requirements, build_candidates, priced_builds, energy_model, errors):
    preferred = build_candidates.get("recommendation", {}).get("preferred_candidate")
    build_map = {candidate["id"]: candidate for candidate in build_candidates.get("candidates", [])}
    priced_map = {candidate["id"]: candidate for candidate in priced_builds.get("candidates", [])}
    energy_map = {candidate["id"]: candidate for candidate in energy_model.get("candidates", [])}

    expect(preferred in build_map, "preferred candidate missing from build-candidates", errors)
    expect(preferred in priced_map, "preferred candidate missing from priced-builds", errors)
    expect(preferred in energy_map, "preferred candidate missing from energy-model", errors)

    region_country = requirements.get("region", {}).get("country")
    expect(priced_builds.get("region") == region_country, "priced-builds.region must match requirements.region.country", errors)
    expect(priced_builds.get("currency") == requirements.get("budget", {}).get("currency"), "priced-builds.currency should match budget currency", errors)
    expect(energy_model.get("currency") == requirements.get("budget", {}).get("currency"), "energy-model.currency should match budget currency", errors)

    for candidate_id, source in build_map.items():
        priced_candidate = priced_map.get(candidate_id)
        if not priced_candidate:
            continue
        items = extract_priced_items(source.get("type"), priced_candidate)
        medians = []
        for item in items:
            retail = item.get("retail", {})
            if isinstance(retail.get("median"), (int, float)):
                medians.append(retail["median"])
        total = priced_candidate.get("candidate_total", {}).get("median")
        if medians and isinstance(total, (int, float)):
            expect(abs(sum(medians) - total) < 0.001, f"{candidate_id}: candidate_total.median must equal sum of item medians", errors)


def validate_plan_markdown(plan_text, build_candidates, priced_builds, compatibility_report, errors):
    preferred = build_candidates.get("recommendation", {}).get("preferred_candidate")
    candidate_map = {candidate["id"]: candidate for candidate in build_candidates.get("candidates", [])}
    priced_map = {candidate["id"]: candidate for candidate in priced_builds.get("candidates", [])}
    compatibility_map = {candidate["id"]: candidate for candidate in compatibility_report.get("candidates", [])}

    preferred_candidate = candidate_map.get(preferred)
    priced_candidate = priced_map.get(preferred)
    compatibility_candidate = compatibility_map.get(preferred)
    if not preferred_candidate or not priced_candidate or not compatibility_candidate:
        errors.append("PLAN.md validation skipped because preferred candidate is missing upstream")
        return

    expect(plan_text.startswith("# Homelab Build Plan"), "PLAN.md must start with the expected title", errors)
    expect(preferred_candidate.get("name", "") in plan_text, "PLAN.md must include preferred candidate name", errors)

    total = priced_candidate.get("candidate_total", {}).get("median")
    if isinstance(total, (int, float)):
        total_text = str(int(total)) if float(total).is_integer() else str(total)
        expect(total_text in plan_text, "PLAN.md must include preferred candidate median total", errors)

    if compatibility_candidate.get("warnings"):
        expect("Known risks" in plan_text, "PLAN.md must include Known risks section when warnings exist", errors)

    for required_section in ("## Why this build", "## Running costs", "## Build order & verification", "## Data sources"):
        expect(required_section in plan_text, f"PLAN.md missing section: {required_section}", errors)

    if preferred_candidate.get("type") == "diy":
        expect(re.search(r"## Phase 1\b", plan_text) is not None, "DIY PLAN.md must include a Phase 1 section", errors)


def run_fixture(name):
    base = FIXTURES / name
    errors = []
    requirements = load_json(base / "requirements.json")
    build_candidates = load_json(base / "build-candidates.json")
    priced_builds = load_json(base / "priced-builds.json")
    energy_model = load_json(base / "energy-model.json")

    validate_requirements(requirements, errors)
    validate_build_candidates(build_candidates, errors)
    validate_priced_builds(priced_builds, build_candidates, errors)
    validate_energy_model(energy_model, errors)
    return errors


def run_completed_fixture(name):
    base = FIXTURES / name
    errors = []
    requirements = load_json(base / "requirements.json")
    constraint_analysis = load_json(base / "constraint-analysis.json")
    build_candidates = load_json(base / "build-candidates.json")
    priced_builds = load_json(base / "priced-builds.json")
    energy_model = load_json(base / "energy-model.json")
    compatibility_report = load_json(base / "compatibility-report.json")
    plan_text = (base / "PLAN.md").read_text()

    validate_requirements(requirements, errors)
    validate_constraint_analysis(constraint_analysis, errors)
    validate_build_candidates(build_candidates, errors)
    validate_priced_builds(priced_builds, build_candidates, errors)
    validate_energy_model(energy_model, errors)
    validate_compatibility_report(compatibility_report, build_candidates, errors)
    validate_cross_file_consistency(requirements, build_candidates, priced_builds, energy_model, errors)
    validate_plan_markdown(plan_text, build_candidates, priced_builds, compatibility_report, errors)
    return errors


def main():
    fixture_names = ["diy", "prebuilt", "hybrid"]
    failures = {}
    for name in fixture_names:
        errors = run_fixture(name)
        if errors:
            failures[name] = errors

    completed_errors = run_completed_fixture("golden-run")
    if completed_errors:
        failures["golden-run"] = completed_errors

    if failures:
        for name, errors in failures.items():
            print(f"[FAIL] {name}")
            for error in errors:
                print(f"  - {error}")
        return 1

    for name in fixture_names:
        print(f"[OK] {name}")
    print("[OK] golden-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
