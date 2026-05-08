from __future__ import annotations

import json
from pathlib import Path


INPUT_FACTS_PATH = "data/facts.json"
OUTPUT_TPTP_PATH = "logic/cml_imatinib.p"


def load_facts(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sanitize_name(text: str) -> str:
    """
    TPTP names should be simple atoms for our use case.
    """
    return (
        text.lower()
        .replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace(".", "_")
    )


def fact_to_tptp_formula(fact: dict, index: int) -> str:
    predicate = sanitize_name(fact["predicate"])
    arg1, arg2 = (sanitize_name(arg) for arg in fact["args"])
    pmid = sanitize_name(fact["pmid"])

    name = f"fact_{index}_{pmid}"
    formula = f"{predicate}({arg1},{arg2})"
    return f"fof({name}, axiom, {formula})."


def build_domain_rule() -> str:
    """
    If a drug inhibits a target and that target drives a disease,
    then the drug is a candidate treatment for that disease via that target.
    """
    return (
        "fof(rule_candidate_treatment_via, axiom, "
        "![Drug,Target,Disease] : "
        "((inhibits(Drug,Target) & drives(Target,Disease)) "
        "=> candidate_treatment_via(Drug,Disease,Target)))."
    )


def build_conjecture(drug: str, disease: str, target: str) -> str:
    drug = sanitize_name(drug)
    disease = sanitize_name(disease)
    target = sanitize_name(target)

    return (
        "fof(goal, conjecture, "
        f"candidate_treatment_via({drug},{disease},{target}))."
    )


def select_demo_facts(facts: list[dict]) -> list[dict]:
    """
    Keep only the strongest facts for the first demo.
    This avoids feeding noisy extractions into the prover.
    """
    allowed_pmids = {
        "38280275",  # strong drives + strong inhibits
        "32711219",  # strong drives
        "21651486",  # strong drives
        "30822403",  # strong inhibits
        "16093432",  # acceptable inhibits
        "22054731",  # acceptable inhibits
    }

    allowed_predicates = {"inhibits", "drives"}
    allowed_args = {"cml", "bcr_abl1_protein", "imatinib"}

    selected = []
    for fact in facts:
        if fact["predicate"] not in allowed_predicates:
            continue
        if fact["pmid"] not in allowed_pmids:
            continue
        if not all(arg in allowed_args for arg in fact["args"]):
            continue
        selected.append(fact)

    return selected


def deduplicate_logical_facts(facts: list[dict]) -> list[dict]:
    """
    Deduplicate by logical content only, ignoring PMID/sentence provenance.
    For the theorem prover, repeated identical atoms are unnecessary.
    """
    seen = set()
    deduped = []

    for fact in facts:
        key = (fact["predicate"], tuple(fact["args"]))
        if key not in seen:
            seen.add(key)
            deduped.append(fact)

    return deduped


def save_tptp(lines: list[str], path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        f.write("% Auto-generated TPTP problem for BioPaper2Proof\n")
        f.write("% Facts extracted from PubMed abstracts\n\n")
        for line in lines:
            f.write(line)
            f.write("\n")


def main() -> None:
    facts = load_facts(INPUT_FACTS_PATH)
    facts = select_demo_facts(facts)
    facts = deduplicate_logical_facts(facts)

    tptp_lines = []

    for i, fact in enumerate(facts, start=1):
        tptp_lines.append(fact_to_tptp_formula(fact, i))

    tptp_lines.append("")
    tptp_lines.append(build_domain_rule())
    tptp_lines.append(build_conjecture("imatinib", "cml", "bcr_abl1_protein"))

    save_tptp(tptp_lines, OUTPUT_TPTP_PATH)

    print(f"Selected {len(facts)} logical facts.")
    print(f"Saved TPTP problem to {OUTPUT_TPTP_PATH}")


if __name__ == "__main__":
    main()