import json
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL_NAME = "BioPaper2Proof"
EMAIL = "parthw04@gmail.com"  


def build_query(disease_query: str, target_query: str, drug_query: str) -> str:
    return (
        f'("{disease_query}"[Title/Abstract]) AND '
        f'("{target_query}"[Title/Abstract]) AND '
        f'("{drug_query}"[Title/Abstract])'
    )

def search_pubmed(search_query: str, max_results: int) -> list[str]:
    url = f"{EUTILS_BASE}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": search_query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance",
        "tool": TOOL_NAME,
        "email": EMAIL
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    return data["esearchresult"]["idlist"]

def fetch_abstracts(pmids: list[str]) -> list[dict]:
    """
    Use EFetch to retrieve title + abstract for a batch of PMIDs.
    """
    if not pmids:
        return []

    url = f"{EUTILS_BASE}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "tool": TOOL_NAME,
        "email": EMAIL,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    records = []

    for article in root.findall(".//PubmedArticle"):
        pmid_elem = article.find(".//PMID")
        pmid = pmid_elem.text.strip() if pmid_elem is not None and pmid_elem.text else ""

        title = article.findtext(".//ArticleTitle", default="").strip()

        abstract_parts = []
        for abstract_text in article.findall(".//Abstract/AbstractText"):
            label = abstract_text.attrib.get("Label", "").strip()
            section_text = "".join(abstract_text.itertext()).strip()
            if section_text:
                if label:
                    abstract_parts.append(f"{label}: {section_text}")
                else:
                    abstract_parts.append(section_text)

        abstract = " ".join(abstract_parts).strip()

        records.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
            }
        )

    return records


def save_json(records: list[dict], output_path: str) -> None:
    """
    Save records as pretty JSON.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def main() -> None:
    disease = input("Disease: ").strip()
    target = input("Target: ").strip()
    drug = input("Drug: ").strip()

    query = build_query(disease, target, drug)
    print(f"\nPubMed query:\n{query}\n")

    pmids = search_pubmed(query, max_results=20)
    print(f"Found {len(pmids)} PMIDs.")

    records = fetch_abstracts(pmids)
    print(f"Fetched {len(records)} records.")

    save_json(records, "data/abstracts.json")
    print("Saved records to data/abstracts.json")


if __name__ == "__main__":
    main()