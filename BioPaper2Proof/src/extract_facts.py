from __future__ import annotations

import json
import re
from pathlib import Path

from schema import (
    Predicate,
    INHIBIT_CUES,
    DRIVE_CUES,
    facts_to_jsonable,
    known_entities_in_text,
    make_fact,
)


SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")


def load_abstracts(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_facts(facts, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(facts_to_jsonable(facts), f, indent=2, ensure_ascii=False)


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_REGEX.split(text) if s.strip()]


def contains_any(text: str, cues: set[str]) -> bool:
    text_lower = text.lower()
    return any(cue in text_lower for cue in cues)


def count_candidate_drugs(entities: set[str]) -> set[str]:
    return {"imatinib", "nilotinib", "dasatinib", "ponatinib"} & entities


def extract_inhibits(sentence: str, pmid: str):
    entities = known_entities_in_text(sentence)
    drugs = count_candidate_drugs(entities)
    targets = {"bcr_abl1_protein"} & entities

    facts = []
    if len(drugs) != 1:
        return facts
    if not targets:
        return facts
    if not contains_any(sentence, INHIBIT_CUES):
        return facts

    drug = next(iter(drugs))
    target = "bcr_abl1_protein"

    fact = make_fact(
        predicate=Predicate.INHIBITS,
        arg1=drug,
        arg2=target,
        pmid=pmid,
        sentence=sentence,
    )
    if fact is not None:
        facts.append(fact)

    return facts


def extract_drives(sentence: str, pmid: str):
    entities = known_entities_in_text(sentence)
    targets = {"bcr_abl1_protein"} & entities
    diseases = {"cml"} & entities

    facts = []
    if not targets or not diseases:
        return facts
    if not contains_any(sentence, DRIVE_CUES):
        return facts

    fact = make_fact(
        predicate=Predicate.DRIVES,
        arg1="bcr_abl1_protein",
        arg2="cml",
        pmid=pmid,
        sentence=sentence,
    )
    if fact is not None:
        facts.append(fact)

    return facts


def deduplicate_facts(facts):
    seen = set()
    deduped = []

    for fact in facts:
        key = (fact.predicate.value, fact.args, fact.pmid, fact.sentence)
        if key not in seen:
            seen.add(key)
            deduped.append(fact)

    return deduped


def extract_facts_from_record(record: dict):
    pmid = record.get("pmid", "")
    abstract = record.get("abstract", "")

    facts = []
    for sentence in split_sentences(abstract):
        facts.extend(extract_inhibits(sentence, pmid))
        facts.extend(extract_drives(sentence, pmid))

    return facts


def main() -> None:
    records = load_abstracts("data/abstracts.json")

    all_facts = []
    for record in records:
        all_facts.extend(extract_facts_from_record(record))

    all_facts = deduplicate_facts(all_facts)
    save_facts(all_facts, "data/facts.json")

    print(f"Extracted {len(all_facts)} facts.")
    print("Saved facts to data/facts.json")


if __name__ == "__main__":
    main()