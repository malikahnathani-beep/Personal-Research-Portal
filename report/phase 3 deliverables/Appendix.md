# Appendix — Mars Life Research Portal (Phase 3)

---

## A1. Prompt Cards

---

### Prompt Card 1 — Synthesis Memo

**Prompt name:** SYNTHESIS_SYSTEM

**Intent:** Generate a structured synthesis memo that answers a research question using only the retrieved evidence chunks, with verified inline citations.

**Inputs (what you provide):**
- Retrieved evidence blocks (source_id, chunk_id, text, similarity score)
- The original research question
- Overall confidence score

**Outputs (required structure):**
- Introduction
- Key Findings (minimum 400 words)
- Synthesis & Implications
- Limitations & Gaps
- Reference List (source_ids only, one per line)
- Inline citations in format: [source_id:chunk_id]

**Constraints / guardrails:**
- Every factual claim must have an inline citation in [source_id:chunk_id] format
- source_id and chunk_id must be copied verbatim from evidence block headers
- Never invent sources or use "Author et al., YEAR" or numbered references like [1]
- If evidence does not support a claim, write "Evidence not found in corpus"
- Reference list must contain only source_ids — no chunk_ids, author names, years, or journal names
- Do not include word counts or page ranges in section headers
- Minimum 800 words total

**When to use / when not to use:**
- Use when confidence scorer returns can_answer = True
- Do not use when confidence is below threshold — use refusal message instead

**Failure modes to watch for:**
- Chunk_ids leaking into reference list (fixed via post-processing)
- Word counts appearing in section headers, e.g. "Introduction (806-837 words)" (fixed via regex)
- Author et al., YEAR citations from reference-heavy chunks (fixed via reference chunk filter)
- Memo truncating at 400-500 words despite length instruction (model size limitation)

---

### Prompt Card 2 — Gap Finder

**Prompt name:** GAPS_SYSTEM

**Intent:** Identify what the corpus cannot answer for a given query and generate targeted follow-up research questions.

**Inputs (what you provide):**
- Retrieved evidence chunks
- Original research question
- Confidence score and can_answer flag

**Outputs (required structure):**
JSON object with:
- `unanswered_aspects`: list of strings describing coverage gaps
- `suggested_queries`: list of 2-3 follow-up research questions
- `missing_sources`: list of corpus source_ids that may have partial coverage

**Constraints / guardrails:**
- Do not invent source names or IDs — only reference sources that exist in the provided evidence
- Suggested queries must be phrased as research questions beginning with What, How, Does, or Is
- Do not phrase suggestions as search engine instructions ("find peer-reviewed papers showing...")
- Return valid JSON only — no preamble or markdown formatting

**When to use / when not to use:**
- Use for all queries, both answered and refused
- For refused queries, gap output drives the refusal explanation displayed to the user
- For answered queries, gap output appears in the Research Gaps section below the memo

**Failure modes to watch for:**
- Model inventing fake source IDs (e.g. "Schmidt2018_MarsRocks") — prevented by explicit instruction
- Suggested queries phrased as search commands rather than research questions
- JSON parse errors when model includes markdown fences around output

---

### Prompt Card 3 — Evidence Table

**Prompt name:** EVIDENCE_TABLE_SYSTEM

**Intent:** Map each retrieved chunk to a structured evidence row with claim, snippet, citation, confidence label, and quality notes.

**Inputs (what you provide):**
- Individual retrieved chunks (one at a time)
- Similarity score for confidence label assignment

**Outputs (required structure):**
Per chunk:
- `claim`: one-sentence summary of what the chunk asserts
- `snippet`: 1-2 sentence direct excerpt from chunk text
- `citation`: [source_id:chunk_id]
- `confidence_score`: numeric similarity score
- `confidence_label`: High / Medium / Low based on score thresholds
- `notes`: brief quality note (e.g. "strong empirical support", "indirect evidence")

**Constraints / guardrails:**
- Snippet must come directly from chunk text — no paraphrasing
- Citation must match the chunk's actual source_id and chunk_id
- Confidence label thresholds: High >= 0.45, Medium >= 0.30, Low < 0.30

**When to use / when not to use:**
- Use for all answered queries
- Skip for refused queries (no evidence table generated)

**Failure modes to watch for:**
- Model paraphrasing snippet instead of extracting directly
- Confidence label not matching numeric score

---

### Prompt Card 4 — Annotated Bibliography

**Prompt name:** ANNOT_BIB_SYSTEM

**Intent:** Generate per-source annotations that summarize the claim, method, limitations, and relevance of each unique source in the retrieved set.

**Inputs (what you provide):**
- Unique source chunks (deduplicated by source_id)

**Outputs (required structure):**
Per source:
- `source_id`
- `chunk_id`
- `claim`: main argument or finding of the source
- `method`: how the evidence was gathered or what type of study it is
- `limitations`: what the source cannot address
- `why_it_matters`: relevance to Mars habitability research

**Constraints / guardrails:**
- Base all annotations strictly on the provided chunk text
- Do not invent methodological details not present in the chunk
- Keep each field to 1-3 sentences

**When to use / when not to use:**
- Use for all answered queries
- Skip for refused queries

**Failure modes to watch for:**
- Generic annotations that could apply to any paper
- Method field speculating about study design not mentioned in chunk

---

## A2. Evaluation Rows

**Scoring rubric:**
- Groundedness/Faithfulness (1-4): 1=fabricated, 2=partially grounded, 3=mostly grounded, 4=fully grounded or correct refusal
- Citation Correctness (1-4): 1=all wrong, 2=some wrong, 3=minor issues, 4=all citations verified
- Usefulness (1-4): 1=unhelpful, 2=partial, 3=adequate, 4=directly answers query

**Prompt ID:** SYNTHESIS_SYSTEM + Mistral 7B (mistral:7b via Ollama)

---

| Task ID | Query | Retrieved Evidence IDs (top 3) | Conf Score | Groundedness (1-4) | Citation Correctness (1-4) | Usefulness (1-4) | Notes | Failure Tag |
|---------|-------|-------------------------------|------------|-------------------|--------------------------|-----------------|-------|-------------|
| Q01 | What evidence did the Curiosity rover find in Gale Crater that suggests past habitability? | DesMarais2014:chunk_0000, Grotzinger2014:chunk_0000, Kite2025:chunk_0009 | 0.82 | 3 | 4 | 3 | Solid answer with adequate sourcing. | none |
| Q02 | What types of organic molecules were detected in Gale Crater sediments? | Freissinet2015:chunk_0000, Kite2025:chunk_0007, Hays2017:chunk_0033 | 0.80 | 3 | 4 | 3 | Solid answer with adequate sourcing. | none |
| Q03 | What mechanisms are proposed to explain methane detections in the Martian atmosphere? | Yung2018:chunk_0000, Lacy2006:chunk_0000, Etiope2019:chunk_0012 | 0.84 | 3 | 4 | 3 | Etiope2019 reference chunk filtered — zero hallucinations confirmed. | none |
| Q04 | What minerals indicate long-term water-rock interaction on Mars? | Ehlmann2012:chunk_0000, Ehlmann2012:chunk_0008, Ehlmann2012:chunk_0001 | 0.92 | 4 | 4 | 4 | High confidence, well-grounded answer. | none |
| Q05 | How do carbonates serve as indicators of past CO2-rich environments? | Hays2017:chunk_0036, Kite2025:chunk_0003, Ehlmann2012:chunk_0001 | 0.76 | 3 | 4 | 3 | Limited source diversity — 2 sources. | limited_sources |
| Q06 | What factors affect biosignature preservation on Mars? | Hays2017:chunk_0004, Hays2017:chunk_0028, Hays2017:chunk_0026 | 0.93 | 4 | 4 | 4 | High confidence, single-source depth. | none |
| Q07 | What energy sources are modeled for hydrothermal systems in Eridania basin? | LaRowe2021:chunk_0000, LaRowe2021:chunk_0002, LaRowe2021:chunk_0001 | 0.92 | 4 | 4 | 4 | High confidence, well-grounded answer. | none |
| Q08 | What does olivine alteration reveal about aqueous activity on Mars? | Murray2024:chunk_0001, Murray2024:chunk_0000, Freissinet2015:chunk_0022 | 0.77 | 3 | 4 | 3 | Limited source diversity — 2 sources. | limited_sources |
| Q09 | How might methane be generated abiotically on Mars? | Yung2018:chunk_0000, Yung2018:chunk_0019, Etiope2019:chunk_0012 | 0.78 | 3 | 4 | 3 | Solid answer with adequate sourcing. | none |
| Q10 | What criteria define a habitable environment in planetary science? | Neveu2018:chunk_0001, Grotzinger2014:chunk_0001, Hays2017:chunk_0003 | 0.77 | 3 | 4 | 3 | Limited source diversity. | limited_sources |
| Q11 | Compare methane-based life arguments with hydrothermal vent habitability arguments. | Yung2018:chunk_0000, Yung2018:chunk_0020, LaRowe2021:chunk_0001 | 0.85 | 3 | 4 | 3 | Synthesis query — multi-source comparison attempted. | none |
| Q12 | How does mineralogical evidence support or contradict methane-based biosignature claims? | Hays2017:chunk_0040, Yung2018:chunk_0000, Neveu2018:chunk_0017 | 0.77 | 3 | 4 | 3 | Limited source diversity. | limited_sources |
| Q13 | Compare Gale Crater findings with Eridania basin models. | LaRowe2021:chunk_0002, Kite2025:chunk_0020, Wolfe2023:chunk_0022 | 0.84 | 3 | 4 | 3 | Comparison query — Eridania weighted more heavily than Gale Crater. | limited_sources |
| Q14 | What are the main failure modes of interpreting organic molecule detection as evidence for life? | Neveu2018:chunk_0017, Neveu2018:chunk_0000, Neveu2018:chunk_0028 | 0.78 | 3 | 4 | 3 | Single-source answer — Neveu2018 dominates. | limited_sources |
| Q15 | Across the corpus, which type of evidence appears most reliable? | Neveu2018:chunk_0027, Neveu2018:chunk_0017, Neveu2018:chunk_0016 | 0.75 | 3 | 4 | 3 | Broad synthesis — limited to one source perspective. | limited_sources |
| Q16 | Does the corpus contain confirmed evidence of present-day microbial life on Mars? | Neveu2018:chunk_0036, Fais2022:chunk_0002, Hays2017:chunk_0047 | 0.23 | 4 | 4 | 2 | Correctly refused — confirmation language detected, conf 0.23 < 0.70 threshold. | edge_case_correct |
| Q17 | Is there definitive proof that methane on Mars is biological in origin? | Yung2018:chunk_0000, Yung2018:chunk_0024, Lacy2006:chunk_0000 | 0.26 | 4 | 4 | 2 | Correctly refused — "definitive proof" triggers high-stakes mode. | edge_case_correct |
| Q18 | Does any paper claim Mars currently supports active ecosystems? | Celekli2024:chunk_0019, Fais2022:chunk_0002, Ehlmann2012:chunk_0015 | 0.23 | 4 | 4 | 2 | Correctly refused — corpus lacks active ecosystem claims. | edge_case_correct |
| Q19 | Does the corpus show that all methane detections have been independently verified? | Lacy2006:chunk_0000, Yung2018:chunk_0024, Etiope2019:chunk_0012 | 0.29 | 4 | 4 | 2 | Correctly refused — confirmation strength near zero. | edge_case_correct |
| Q20 | Is there direct fossil evidence of Martian organisms in the dataset? | Hays2017:chunk_0050, Mckay2003:chunk_0000, Hays2017:chunk_0039 | 0.28 | 4 | 4 | 2 | Correctly refused — no fossil evidence claims in corpus. | edge_case_correct |

**Summary:**
- Answered: 15/20
- Refused: 5/20 (all correct)
- Mean Groundedness: 3.35
- Mean Citation Correctness: 4.00
- Mean Usefulness: 2.90
- Total hallucinated citations: 0

---

## A3. Source Metadata Schema

Minimum required fields per source in `data/data_manifest.csv`:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| source_id | string | Unique identifier used in citations | `Grotzinger2014_GaleLake` |
| title | string | Full paper title | `A Habitable Fluvio-Lacustrine Environment at Yellowknife Bay, Gale Crater, Mars` |
| authors | string | Author list (Last, First; Last, First) | `Grotzinger, J.P.; Sumner, D.Y.; et al.` |
| year | integer | Publication year | `2014` |
| source_type | string | peer-reviewed / working-paper / report / survey | `peer-reviewed` |
| venue | string | Journal or conference name | `Science` |
| url_or_doi | string | DOI or URL | `https://doi.org/10.1126/science.1242777` |
| raw_path | string | Path to original PDF | `data/raw/Grotzinger2014_GaleLake.pdf` |
| processed_path | string | Path to parsed text (optional) | `data/processed/Grotzinger2014_GaleLake.txt` |
| tags | string | Comma-separated topic tags | `habitability, Gale Crater, mineralogy, Curiosity` |
| relevance_note | string | 1-2 sentence note on why this source was selected | `Primary source for Curiosity rover findings at Gale Crater, directly relevant to habitability sub-questions.` |
