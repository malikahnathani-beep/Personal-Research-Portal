# Prompt Kit — Phase 1

# Task 1 — Paper Triage

## Prompt A

Read the following research paper excerpt and summarize it using the following fields:

Contribution:
Method:
Data:
Findings:
Limitations:

---

## Prompt B

You are a research assistant producing a structured paper triage.

Use ONLY the provided text.  
Do NOT use outside knowledge.  

If a field is not supported by the text, write:

Not stated in provided excerpt.

Output format (exact):

Contribution:
Method:
Data:
Findings:
Limitations:

Include at least one citation per field using the format (source_id).

---

## Why These Constraints Exist

- Fixed fields enforce consistent summaries across papers.
- "Use ONLY the provided text" reduces hallucination and leakage of outside knowledge.
- "Not stated in provided excerpt" prevents the model from guessing missing information.
- Requiring at least one citation per field enforces grounding and traceability.
- Exact output format enables easier comparison and evaluation.

---

# Task 2 — Claim–Evidence Extraction

## Prompt A

Extract five key claims from the following text and provide supporting evidence.

---

## Prompt B

Extract five key claims from the following text and provide supporting evidence.  
You are extracting claims with direct textual evidence.

Use ONLY the provided text.  
Each claim must be supported by a direct quote or snippet from the text.  
Each row must include a citation in the format (source_id).

If fewer than five supported claims are present, output fewer rows and state:

Insufficient evidence in provided excerpt.

Output format (exact):

Claim | Direct quote/snippet | Citation (source_id)

---

## Why These Constraints Exist

- Claim + quote pairing forces explicit linkage between assertion and evidence.
- Table structure creates machine-checkable, consistent outputs.
- Citation per row enables auditing and later mapping to source documents.
- "Use ONLY the provided text" reduces fabrication.
- Insufficient-evidence rule encourages abstention rather than forced completion.