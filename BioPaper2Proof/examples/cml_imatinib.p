% Auto-generated TPTP problem for BioPaper2Proof
% Facts extracted from PubMed abstracts

fof(fact_1_38280275, axiom, drives(bcr_abl1_protein,cml)).
fof(fact_2_38280275, axiom, inhibits(imatinib,bcr_abl1_protein)).

fof(rule_candidate_treatment_via, axiom, ![Drug,Target,Disease] : ((inhibits(Drug,Target) & drives(Target,Disease)) => candidate_treatment_via(Drug,Disease,Target))).
fof(goal, conjecture, candidate_treatment_via(imatinib,cml,bcr_abl1_protein)).
