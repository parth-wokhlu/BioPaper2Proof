# BioPaper2Proof

Biomedical literature contains a large amount of noisy, unstructured information about diseases, the molecular mechanisms that drive them, and the drugs that target them. This makes it difficult to reason mechanically over prior results. BioPaper2Proof is a pipeline that ingests PubMed abstracts, extracts structured biomedical facts, converts them into first-order logic, and uses Vampire to test whether a therapeutic or mechanistic hypothesis follows from the extracted evidence and a small set of domain rules.

For example, given PubMed abstracts about Chronic Myeloid Leukemia (CML), the BCR-ABL1 fusion protein, and the drug imatinib, BioPaper2Proof can test whether `candidate_treatment_via(imatinib, cml, bcr_abl1_protein)` follows. In other words, it asks: is imatinib a plausible treatment for CML via inhibition of BCR-ABL1?

## Input
PubMed abstracts about a disease, its molecular driver, and a drug family

## Output
A TPTP first-order logic file containing extracted facts, domain rules, and a target conjecture for Vampire

## Core predicates
`inhibits(drug, target)`  
`drives(target, disease)`  
`treated_by(disease, drug)`  
`candidate_treatment_via(drug, disease, target)`

## Domain rule
`inhibits(Drug, Target) & drives(Target, Disease) => candidate_treatment_via(Drug, Disease, Target)`
