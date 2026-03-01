"""
src/rag/rag.py — Mars Life Research RAG backend
Phase 3 — Personal Research Portal

Uses Ollama for local LLM inference (no API key required).
Run: ollama serve && ollama pull mistral:7b
"""

from pathlib import Path
import re
import json
import numpy as np
from datetime import datetime
import ollama

# ── Import from retrieve.py ────────────────────────────────────────────────────
from src.rag.retrieve import (
    retrieve_top_k,
    compute_confidence,
    _convert_numpy,
)

# ── Paths ──────────────────────────────────────────────────────────────────────
LOG_PATH     = Path("logs/query_log.jsonl")
THREADS_PATH = Path("logs/threads.jsonl")

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Ollama config ──────────────────────────────────────────────────────────────
OLLAMA_MODEL = "mistral:7b"


# ── Synthesis memo ─────────────────────────────────────────────────────────────
SYNTHESIS_SYSTEM = """You are a research synthesis engine. Answer using ONLY the provided evidence chunks.

ABSOLUTE CITATION RULES — VIOLATIONS WILL INVALIDATE THE MEMO:
- Every factual claim MUST have an inline citation in EXACTLY this format: [source_id:chunk_id]
- source_id and chunk_id must be copied VERBATIM from the evidence block headers — do not modify them
- NEVER invent sources. NEVER use "Author et al., YEAR" or numbered references like [1] or [2]
- If the evidence does not support a claim, write "Evidence not found in corpus" — do not guess

STRUCTURE — follow this exactly, no word counts in headers:
Introduction: (provide context and scope)
Key Findings: (detailed evidence-based findings — this section must be at least 400 words)
Synthesis & Implications: (what the evidence means collectively)
Limitations & Gaps: (what the corpus cannot answer)
Reference List: (sources cited above)

LENGTH: You MUST write at least 800 words. Write thorough, detailed paragraphs. Do not truncate or summarize briefly.

REFERENCE LIST — follow this exactly:
- List only the source_id, one per line, formatted as: - source_id
- Example: - DesMarais2014_HabitableMars
- NEVER include chunk_ids, author names, years, or journal names in this list
- Only list sources you actually cited inline in the memo above
- Do NOT include ANY numbers, ranges, or counts in section headers
    - WRONG: "Introduction (806-837 words)" or "Key Findings (2)" 
    - CORRECT: "Introduction:" or "Key Findings:"""

def generate_synthesis_memo(question: str, retrieved: list, confidence: dict) -> str:
    if not confidence["can_answer"]:
        return build_refusal_message(question, retrieved, confidence)

    evidence_block = "\n\n".join(
        f"[{r['source_id']}:{r['chunk_id']}] (score: {r['score']:.3f})\n{r['text']}"
        for r in retrieved
    )

    valid_citations = "\n".join(f"- [{r['source_id']}:{r['chunk_id']}]" for r in retrieved)

    user_prompt = f"""Research Question: {question}

Evidence Chunks:
{evidence_block}

VALID CITATIONS (use ONLY these exact IDs, no others):
{valid_citations}

Write a synthesis memo of AT LEAST 800 words answering the research question using ONLY the evidence above.
Each section (Introduction, Key Findings, Synthesis & Implications, Limitations & Gaps) must be at least 2 full paragraphs.
Cite every claim inline using ONLY the valid citations listed above as [source_id:chunk_id].
In the Reference List, only write the source_id and chunk_id — do NOT invent author names, journal names, or page numbers.
You MUST write at least 800 words. If you finish a section and have not reached 800 words, keep writing and expand with more analysis.
Do not stop before 800 words."""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user",   "content": user_prompt},
        ],
        options={"num_predict": 1500}
    )
    memo = response["message"]["content"]
    memo = re.sub(r'(Introduction|Key Findings|Synthesis & Implications|Limitations & Gaps|Conclusion|Reference List)\s*\([^)]*\)', r'\1:', memo)
    # Normalize reference list to consistent format
    memo = re.sub(r'(?i)(reference list|references):?\s*\n', 'Reference List:\n', memo)

    # Clean reference list — strip chunk_ids and brackets, keep only source_ids
    def clean_reference_list(memo: str) -> str:
        def fix_ref_line(match):
            line = match.group(0)
            source = re.search(r'\[?([A-Za-z][A-Za-z0-9_]+?)(?::[^\]]+)?\]?$', line)
            if source:
                return f"- {source.group(1)}"
            return line
        return re.sub(r'^- \[?[A-Za-z].*$', fix_ref_line, memo, flags=re.MULTILINE)

    memo = clean_reference_list(memo)
    
    # Validate citations
    cited_source_ids = set(re.findall(r'\[([^\]:\s]+)[:\]]', memo))
    valid_source_ids = {r["source_id"] for r in retrieved}
    invalid_sources  = cited_source_ids - valid_source_ids
    if invalid_sources:
        memo += f"\n\n---\nCITATION NOTE: These source IDs could not be verified: {list(invalid_sources)}"
    return memo


# ── Evidence table (no LLM) ────────────────────────────────────────────────────
def build_evidence_table(question: str, retrieved: list) -> list:
    rows = []
    q_words = set(re.findall(r'\b\w{4,}\b', question.lower()))

    for r in retrieved:
        text  = r["text"]
        score = r["score"]

        # Claim — first clean sentence
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        claim = sentences[0][:150] if sentences else text[:150]

        # Snippet — first 200 chars cleaned
        snippet = " ".join(text.split())[:200]

        # Citation
        citation = f"[{r['source_id']}:{r['chunk_id']}]"

        # Confidence label
        if score >= 0.85:   conf_label = "High"
        elif score >= 0.70: conf_label = "Medium"
        else:               conf_label = "Low"

        # Notes
        notes = []
        chunk_words = set(re.findall(r'\b\w{4,}\b', text.lower()))
        overlap = len(q_words & chunk_words) / max(len(q_words), 1)

        # Match quality
        if score >= 0.85 and overlap >= 0.3:
            notes.append("Top retrieval match")
        elif score >= 0.85:
            notes.append("High similarity score")
        elif score >= 0.70 and overlap >= 0.3:
            notes.append("Moderate match")
        elif overlap < 0.2:
            notes.append("Weak keyword overlap — may be tangential")

        # Source repetition
        same_source = sum(1 for rr in retrieved if rr["source_id"] == r["source_id"])
        if same_source > 1:
            notes.append(f"Heavy reliance — {same_source} chunks from same paper")

        if not notes:
            notes.append("Good retrieval match")

        rows.append({
            "claim":            claim,
            "snippet":          snippet,
            "citation":         citation,
            "confidence_score": round(score, 3),
            "confidence_label": conf_label,
            "notes":            "; ".join(notes),
        })

    return rows


# ── Annotated bibliography (LLM per source) ────────────────────────────────────
ANNOT_SYSTEM = """You are a research analyst. Given a single evidence chunk from a scientific paper,
extract exactly 4 fields. Be concise — 1-2 sentences each.
Use ONLY information present in the chunk. Do not invent details.
Respond in this exact format:
CLAIM: <what this chunk argues or reports>
METHOD: <how the evidence was gathered e.g. rover analysis, spectroscopy, modeling — or "Not specified" if unclear>
LIMITATIONS: <what is uncertain, missing, or caveated in this chunk — or "Not stated" if none>
WHY IT MATTERS: <why this finding is relevant to Mars habitability or life detection>"""


def generate_annotated_bibliography(retrieved: list) -> list:
    entries = []
    seen_sources = set()

    for r in retrieved:
        # One entry per unique source
        if r["source_id"] in seen_sources:
            continue
        seen_sources.add(r["source_id"])

        prompt = f"""Evidence chunk from [{r['source_id']}:{r['chunk_id']}]:

{r['text'][:1500]}

Extract the 4 fields as instructed."""

        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": ANNOT_SYSTEM},
                    {"role": "user",   "content": prompt},
                ],
            )
            content = response["message"]["content"]

            def extract_field(label, text):
                match = re.search(rf'{label}:\s*(.+?)(?=\n(?:CLAIM|METHOD|LIMITATIONS|WHY IT MATTERS):|$)', text, re.DOTALL)
                if not match:
                    return "Not extracted"
                val = match.group(1).strip()
                # Remove any leaked next-field headers
                val = re.sub(r'\n?WHY IT MATTERS:.*', '', val, flags=re.DOTALL).strip()
                return val

            entries.append({
                "source_id":      r["source_id"],
                "chunk_id":       r["chunk_id"],
                "claim":          extract_field("CLAIM", content),
                "method":         extract_field("METHOD", content),
                "limitations":    extract_field("LIMITATIONS", content),
                "why_it_matters": extract_field("WHY IT MATTERS", content),
            })
        except Exception as e:
            entries.append({
                "source_id":      r["source_id"],
                "chunk_id":       r["chunk_id"],
                "claim":          "Error generating entry",
                "method":         str(e),
                "limitations":    "",
                "why_it_matters": "",
            })

    return entries


# ── Main ask function ──────────────────────────────────────────────────────────
# Dynamic k based on question complexity
    q_lower = question.lower()
    if any(w in q_lower for w in ["compare", "contrast", "all", "every", "comprehensive", "overview", "survey"]):
        k = 15  # broad questions need more sources
    elif any(w in q_lower for w in ["what is", "define", "how does", "who", "when"]):
        k = 7   # simple factual questions need fewer
    else:
        k = 10  # default for most research questions

def ask(question: str, k: int = 7) -> dict:

    retrieved      = retrieve_top_k(question, k)
    # Filter out reference-list chunks — they cause the LLM to hallucinate Author et al., YEAR citations
    retrieved = [r for r in retrieved if len(re.findall(r'[A-Z][a-z]+ et al\.', r["text"])) <= 5]
    
    confidence     = compute_confidence(question, retrieved)
    memo           = generate_synthesis_memo(question, retrieved, confidence)
    # Extract citations — handle [source:chunk], [source : chunk], and [source] formats
    valid_source_ids = {r["source_id"] for r in retrieved}
    chunk_map = {r["source_id"]: r["chunk_id"] for r in retrieved}
    citations = set()
    # Format 1: [source_id:chunk_id] with optional spaces
    for s, c in re.findall(r'\[([^\]\s:][^\]:]*?)\s*:\s*([^\]]+?)\]', memo):
        s = s.strip()
        if s in valid_source_ids:
            citations.add((s, c.strip()))
    # Format 2: [source_id] without chunk
    for s in re.findall(r'\[([A-Za-z][A-Za-z0-9_]+)\]', memo):
        if s in valid_source_ids:
            citations.add((s, chunk_map.get(s, "")))
    citations = list(citations)
    evidence_table = build_evidence_table(question, retrieved)
    annot_bib      = generate_annotated_bibliography(retrieved)

    gaps = find_gaps(question, retrieved, confidence)

    result = {
        "query":          question,
        "memo":           memo,
        "citations":      citations,
        "retrieved":      retrieved,
        "confidence":     confidence,
        "evidence_table": evidence_table,
        "annot_bib":      annot_bib,
        "gaps":           gaps,
        "timestamp":      datetime.now().isoformat(),
    }
    _log(result)
    return result


# ── Logging ────────────────────────────────────────────────────────────────────
def _log(result: dict):
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(_convert_numpy(result)) + "\n")

def save_thread(thread: dict):
    with THREADS_PATH.open("a") as f:
        f.write(json.dumps(_convert_numpy(thread)) + "\n")

def load_threads() -> list:
    if not THREADS_PATH.exists():
        return []
    threads = []
    with THREADS_PATH.open() as f:
        for line in f:
            if line.strip():
                try: threads.append(json.loads(line))
                except: pass
    return threads


# ── Gap finder ────────────────────────────────────────────────────────
def find_gaps(question: str, retrieved: list, confidence: dict) -> dict:
    """LLM-based gap finder — dynamically identifies missing evidence and suggests next queries."""
    
    # Detect basic structural issues (no LLM needed)
    unanswered = []
    if confidence["overall_confidence"] < 0.6:
        unanswered.append("Overall confidence is low — corpus may lack direct evidence on this question")
    if len(set(r["source_id"] for r in retrieved)) <= 2:
        unanswered.append("Only 1-2 unique sources retrieved — evidence base is narrow")

    # LLM-based gap analysis
    source_list = list(set(r["source_id"] for r in retrieved))
    prompt = f"""A researcher asked this specific question: "{question}"

The RAG system retrieved these sources: {source_list}
Overall confidence: {confidence['overall_confidence']:.2f}

Focusing ONLY on the specific question asked:
1. What specific aspect of THIS question is not well covered by the retrieved sources?
2. Suggest 2 short, natural follow-up queries (under 15 words each) that a scientist would ask 
   when searching peer-reviewed Mars astrobiology papers for related evidence.

Write them as direct research questions starting with "What", "How", "Does", or "Is".
Never include phrases like "peer-reviewed papers", "find studies", or "locate datasets".
Do NOT give generic Mars astrobiology gaps. Stay focused on exactly what was asked.
Do NOT mention or invent source names.
Respond EXACTLY in this format:
GAP: one sentence about what's missing for this specific question
QUERY1: specific follow-up query
QUERY2: specific follow-up query"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]

        def extract(label, text):
            match = re.search(rf'{label}:\s*(.+?)(?=\n[A-Z]+:|$)', text, re.DOTALL)
            return match.group(1).strip() if match else ""

        gap    = extract("GAP", content).split("\n")[0].strip()
        query1 = extract("QUERY1", content).split("\n")[0].strip()
        query2 = extract("QUERY2", content).split("\n")[0].strip()

        # Remove any leaked HTML, quotes, or QUERY2 fragments
        for bad in ['</div>', '<div', 'QUERY2:', 'QUERY1:', '"']:
            gap    = gap.replace(bad, "").strip()
            query1 = query1.replace(bad, "").strip()
            query2 = query2.replace(bad, "").strip()

        if gap:
            unanswered.append(gap)

        suggested = [q for q in [query1, query2] if q and len(q) > 10]

        return {
            "unanswered_aspects": unanswered,
            "suggested_queries":  suggested,
            "missing_sources":    [],
            "weak_chunks":        [r["source_id"] for r in retrieved if r["score"] < 0.75],
        }
    except Exception as e:
        return {
            "unanswered_aspects": unanswered,
            "suggested_queries":  [],
            "missing_sources":    [],
            "weak_chunks":        [],
        }


def build_refusal_message(question: str, retrieved: list, confidence: dict) -> str:
    """Better refusal message with specific next retrieval steps."""
    gaps = find_gaps(question, retrieved, confidence)

    lines = [
        "INSUFFICIENT EVIDENCE\n",
        f"Confidence: {confidence['overall_confidence']:.2f} (threshold: {confidence['threshold']:.2f})",
        f"Reason: {confidence['reasoning']}\n",
    ]

    if gaps["unanswered_aspects"]:
        lines.append("Why this query cannot be answered:")
        for a in gaps["unanswered_aspects"]:
            lines.append(f"  • {a}")
        lines.append("")

    if gaps["suggested_queries"]:
        lines.append("Suggested next queries:")
        for q in gaps["suggested_queries"]:
            lines.append(f"  → \"{q}\"")
        lines.append("")

    if gaps["missing_sources"]:
        lines.append("Corpus sources that may address this:")
        for s in gaps["missing_sources"]:
            lines.append(f"  • {s}")

    return "\n".join(lines)
