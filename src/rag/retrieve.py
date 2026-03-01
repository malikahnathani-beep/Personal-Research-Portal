"""
src/rag/retrieve.py
Retrieval + confidence scoring from Phase 2 notebook 3.
Can be run standalone: python src/rag/retrieve.py "your question here"
"""

from pathlib import Path
import numpy as np
import orjson
import faiss
from sentence_transformers import SentenceTransformer
import re
import json
from datetime import datetime
import sys

# ── Config ─────────────────────────────────────────────────────────────────────
CHUNKS_PATH = Path("data/processed/chunks.jsonl")
FAISS_PATH  = Path("data/vector_store/faiss.index")
LOG_PATH    = Path("logs/query_log.jsonl")

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Load corpus ────────────────────────────────────────────────────────────────
chunks = [orjson.loads(line) for line in CHUNKS_PATH.open("rb") if line.strip()]
index  = faiss.read_index(str(FAISS_PATH))
model  = SentenceTransformer("intfloat/e5-base-v2")


# ── Retrieval ──────────────────────────────────────────────────────────────────
def retrieve_top_k(query: str, k: int = 5) -> list:
    q_emb = model.encode(
        [f"query: {query}"],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)
    scores, idxs = index.search(q_emb, k)
    return [
        {
            "score":     float(scores[0][i]),
            "source_id": chunks[idxs[0][i]]["source_id"],
            "chunk_id":  chunks[idxs[0][i]]["chunk_id"],
            "text":      chunks[idxs[0][i]]["text"],
        }
        for i in range(k)
    ]


# ── Confidence scoring ─────────────────────────────────────────────────────────
def compute_confidence(question: str, retrieved: list) -> dict:
    if not retrieved:
        return {"overall_confidence": 0.0, "can_answer": False, "reasoning": "No chunks retrieved"}

    retrieval_conf = float(np.mean([r["score"] for r in retrieved[:3]]))

    q_words    = set(re.findall(r'\b\w{4,}\b', question.lower())) - {"what", "does", "how", "mars", "corpus"}
    text_words = set(re.findall(r'\b\w{4,}\b', " ".join(r["text"].lower() for r in retrieved[:3])))
    overlap    = len(q_words & text_words) / max(len(q_words), 1)

    q_lower         = question.lower()
    is_strong_claim = any(p in q_lower for p in [
        "confirmed", "verified", "definitive", "proof",
        "does the corpus contain", "is there", "does any"
    ])

    confirmation = 1.0
    if is_strong_claim:
        combined  = " ".join(r["text"].lower() for r in retrieved[:3])
        sentences = re.split(r'[.!?]+', combined)
        conf_words  = ["confirmed", "definitive", "proof", "proven", "demonstrated"]
        claim_words = [w for w in ["present", "current", "biological", "fossil", "active", "ecosystem"] if w in q_lower]
        found = any(
            any(cw in s for cw in conf_words) and any(cl in s for cl in claim_words)
            for s in sentences
        )
        confirmation = 1.0 if found else 0.0

    if is_strong_claim:
        overall   = 0.2 * retrieval_conf + 0.2 * overlap + 0.6 * confirmation
        threshold = 0.7
    else:
        overall   = 0.5 * retrieval_conf + 0.3 * overlap + 0.2 * confirmation
        threshold = 0.5

    can_answer = overall >= threshold

    reasons = []
    if is_strong_claim and confirmation == 0.0:
        reasons.append("Query asks for confirmed evidence but corpus lacks explicit confirmation language")
    if retrieval_conf < 0.7:
        reasons.append(f"Low retrieval confidence ({retrieval_conf:.2f})")
    if overlap < 0.3:
        reasons.append(f"Low keyword overlap ({overlap:.2f})")

    return {
        "overall_confidence":    float(overall),
        "retrieval_confidence":  retrieval_conf,
        "lexical_overlap":       float(overlap),
        "confirmation_strength": float(confirmation),
        "can_answer":            bool(can_answer),
        "reasoning":             "; ".join(reasons) if reasons else "Sufficient evidence found",
        "threshold":             threshold,
    }


# ── Build extractive answer ────────────────────────────────────────────────────
def build_answer(question: str, retrieved: list, min_score: float = 0.20) -> tuple:
    if not retrieved or max(r["score"] for r in retrieved) < min_score:
        return "No relevant evidence found.", [], {"overall_confidence": 0.0, "can_answer": False}

    confidence = compute_confidence(question, retrieved)

    if not confidence["can_answer"]:
        answer = (
            f"INSUFFICIENT EVIDENCE\n\n"
            f"Confidence: {confidence['overall_confidence']:.2f} (threshold: {confidence['threshold']:.2f})\n"
            f"Reason: {confidence['reasoning']}\n\n"
            f"Suggested next step: Try rephrasing or broadening the question."
        )
        return answer, [], confidence

    citation_threshold = 0.85
    used = [r for r in retrieved[:5] if r["score"] >= citation_threshold] or retrieved[:2]

    conf_label = "High" if confidence["overall_confidence"] >= 0.8 else \
                 "Medium" if confidence["overall_confidence"] >= 0.6 else "Low"

    lines = [f"Answer [Confidence: {conf_label} ({confidence['overall_confidence']:.2f})]\n"]
    citations = []
    for r in used:
        cid     = f"[{r['source_id']}:{r['chunk_id']}]"
        snippet = " ".join(r["text"].split())[:400]
        lines.append(f"- {snippet}... {cid}")
        citations.append((r["source_id"], r["chunk_id"]))

    return "\n".join(lines), citations, confidence


# ── Log ────────────────────────────────────────────────────────────────────────
def _convert_numpy(obj):
    if isinstance(obj, dict):  return {k: _convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):  return [_convert_numpy(v) for v in obj]
    if isinstance(obj, (np.bool_, np.integer, np.floating)): return obj.item()
    return obj

def query_and_log(question: str, k: int = 5):
    """Single command interface: retrieve, answer, and log."""
    retrieved  = retrieve_top_k(question, k)
    answer, citations, confidence = build_answer(question, retrieved)

    print("=" * 70)
    print(f"QUERY: {question}")
    print("=" * 70)
    print(answer)
    print(f"\nCitations: {citations}")
    print(f"Confidence: {confidence['overall_confidence']:.2f}")

    with LOG_PATH.open("a") as f:
        f.write(json.dumps(_convert_numpy({
            "query":      question,
            "answer":     answer,
            "citations":  citations,
            "confidence": confidence,
            "retrieved":  retrieved,
            "timestamp":  datetime.now().isoformat(),
        })) + "\n")

    print(f"\n✓ Saved to {LOG_PATH}")
    return answer, citations, confidence


# ── Standalone run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
               "What evidence did Curiosity find in Gale Crater?"
    query_and_log(question)
