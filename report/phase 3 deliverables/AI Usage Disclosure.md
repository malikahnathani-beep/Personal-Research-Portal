# AI Usage Disclosure — Mars Life Research Portal (Phase 3)

---

## Tool Used: Claude (Anthropic) — claude.ai

---

## Usage Log

| # | What I Used AI For | What I Changed Manually Afterward |
|---|-------------------|-----------------------------------|
| 1 | Drafting the `SYNTHESIS_SYSTEM` prompt for Mistral 7B — structure rules, citation format, length guidance | Rewrote citation rules multiple times after testing showed chunk_ids leaking into reference list; added explicit example format; removed contradictory language myself after identifying the conflict |
| 2 | Generating the gap finder prompt (`GAPS_SYSTEM`) | Fixed hallucinated source names appearing in gap output by adding explicit instruction not to invent source IDs; tested and confirmed fix |
| 3 | Suggesting dynamic k selection logic (keyword-based question classification) | Chose the threshold values (7/10/15) and keyword lists myself based on testing; verified behavior on simple vs. broad queries |
| 4 | Debugging the reference chunk filter — identifying that Etiope2019 and Neveu2018 review paper chunks were causing 18 hallucinated citations in Query 3 | Chose the threshold of 5 "et al." patterns empirically after inspecting actual chunk content; verified filter removed the problem without over-filtering |
| 5 | Writing post-processing regex for memo cleanup (section headers, reference list normalization) | Identified the specific bugs from testing output; debugged a triple-quote string literal error in `rag.py` that broke the system after adding the new rule |
| 6 | Suggesting `html.escape()` fix for `</div></div>` rendering bug in eval tab representative examples | Diagnosed root cause myself (memo text injected raw into HTML); confirmed fix resolved the issue |
| 7 | Drafting the README structure and content | Rewrote the full pipeline section after clarifying that `run_pipeline.py` is the correct entry point (not the notebooks); removed overly detailed "How It Works" flowchart section as too verbose for a README |
| 8 | Drafting the Phase 3 final report sections | Verified all architectural details against actual code; filled in evaluation results from real query log output; added word count limitation section based on observed behavior (not AI suggestion) |
| 9 | Drafting the video demo script | Adjusted query examples to match actual corpus; reordered sections to show refusal behavior before export |
| 10 | Debugging `IndentationError` in eval tab after adding `html.escape()` | Fixed indentation myself after identifying that `if ex:` was not properly nested inside the `for` loop |
| 11 | Identifying variable collision (`q` in gap finder loop overwriting outer `query` variable) causing broken HTML in refusal display | Traced the bug myself by inspecting the rendered output; confirmed fix by re-running a refused query |
| 12 | Updating `requirements.txt` — removing Groq, adding Ollama and pdfkit | Verified package names and versions against what was actually installed in the environment |

---

## What I Am Responsible For

- All evaluation results, confidence scores, and citation counts in the final report reflect actual system output from `logs/query_log.jsonl` — not AI-generated numbers.
- Citation format verification was done by running the system and inspecting output, not by trusting AI suggestions.
- All prompt engineering decisions (thresholds, keyword lists, output structure) were tested iteratively and adjusted based on real results.
- The 800-word memo limitation was identified through testing, not assumed — and is documented honestly in the report rather than hidden.
- I reviewed every code change suggested by AI before applying it, and caught multiple errors (wrong variable placement, string literal bug, indentation error) that required manual fixes.

