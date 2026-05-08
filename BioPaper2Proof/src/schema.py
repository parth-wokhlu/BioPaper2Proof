from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Predicate(str, Enum):
    INHIBITS = "inhibits"
    DRIVES = "drives"


class EntityType(str, Enum):
    DRUG = "drug"
    TARGET = "target"
    DISEASE = "disease"


CANONICAL_ENTITIES: dict[str, dict[str, object]] = {
    "cml": {
        "type": EntityType.DISEASE,
        "aliases": {
            "cml",
            "chronic myeloid leukemia",
            "chronic myelogenous leukemia",
            "philadelphia chromosome-positive chronic myeloid leukemia",
            "ph+ cml",
        },
    },
    "bcr_abl1_protein": {
        "type": EntityType.TARGET,
        "aliases": {
            "bcr-abl",
            "bcr-abl1",
            "bcr abl",
            "bcr/abl",
            "bcr-abl fusion protein",
            "bcr-abl tyrosine kinase",
            "bcr-abl kinase",
            "bcr-abl oncoprotein",
            "bcr-abl1 fusion protein",
            "abl protein",
        },
    },
    "imatinib": {
        "type": EntityType.DRUG,
        "aliases": {
            "imatinib",
            "imatinib mesylate",
            "gleevec",
            "sti571",
        },
    },
    "nilotinib": {
        "type": EntityType.DRUG,
        "aliases": {
            "nilotinib",
        },
    },
    "dasatinib": {
        "type": EntityType.DRUG,
        "aliases": {
            "dasatinib",
        },
    },
    "ponatinib": {
        "type": EntityType.DRUG,
        "aliases": {
            "ponatinib",
        },
    },
}


PREDICATE_SIGNATURES: dict[Predicate, tuple[EntityType, EntityType]] = {
    Predicate.INHIBITS: (EntityType.DRUG, EntityType.TARGET),
    Predicate.DRIVES: (EntityType.TARGET, EntityType.DISEASE),
}


INHIBIT_CUES = {
    "inhibit",
    "inhibits",
    "inhibitor",
    "binds",
    "binding",
    "target",
    "targets",
    "selective inhibitor",
    "tyrosine kinase inhibitor",
    "kinase inhibitor",
}

DRIVE_CUES = {
    "driver",
    "drives",
    "caused by",
    "causes",
    "constitutively active",
    "oncogenic",
    "hallmark",
    "fusion protein",
    "fusion gene",
    "originating from",
}


@dataclass(frozen=True)
class Fact:
    predicate: Predicate
    args: tuple[str, str]
    pmid: str
    sentence: str
    method: str = "rule_based"

    def to_dict(self) -> dict[str, object]:
        return {
            "predicate": self.predicate.value,
            "args": list(self.args),
            "pmid": self.pmid,
            "sentence": self.sentence,
            "method": self.method,
        }


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def build_alias_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical_name, info in CANONICAL_ENTITIES.items():
        aliases = info["aliases"]
        assert isinstance(aliases, set)
        for alias in aliases:
            lookup[normalize_text(alias)] = canonical_name
    return lookup


ALIAS_TO_CANONICAL = build_alias_lookup()


def canonicalize_entity(text: str) -> str | None:
    return ALIAS_TO_CANONICAL.get(normalize_text(text))


def entity_type(entity_name: str) -> EntityType:
    info = CANONICAL_ENTITIES[entity_name]
    entity_kind = info["type"]
    assert isinstance(entity_kind, EntityType)
    return entity_kind


def validate_fact(predicate: Predicate, args: tuple[str, str]) -> bool:
    expected_types = PREDICATE_SIGNATURES[predicate]
    actual_types = tuple(entity_type(arg) for arg in args)
    return actual_types == expected_types


def known_entities_in_text(text: str) -> set[str]:
    text_norm = normalize_text(text)
    found: set[str] = set()

    for alias, canonical in ALIAS_TO_CANONICAL.items():
        if alias in text_norm:
            found.add(canonical)

    return found


def make_fact(
    predicate: Predicate,
    arg1: str,
    arg2: str,
    pmid: str,
    sentence: str,
    method: str = "rule_based",
) -> Fact | None:
    args = (arg1, arg2)
    if not validate_fact(predicate, args):
        return None
    return Fact(
        predicate=predicate,
        args=args,
        pmid=pmid,
        sentence=sentence,
        method=method,
    )


def facts_to_jsonable(facts: Iterable[Fact]) -> list[dict[str, object]]:
    return [fact.to_dict() for fact in facts]