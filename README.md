# Mars Life Research Portal

An evidence-grounded Retrieval-Augmented Generation (RAG) system for querying peer-reviewed literature on Mars habitability and astrobiology. Built for Phase 3 of the research-grade RAG project. Runs entirely locally via Ollama — no API keys, no rate limits, no hallucinated sources.

---

## 🚀 Get Running in 5 Minutes

### Prerequisites

**1. Start Ollama** (local LLM server):
```bash
ollama serve
```

**2. Pull the model** (one-time, in a new terminal):
```bash
ollama pull mistral:7b
```

### Launch the Portal

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the web UI — then open http://localhost:8501
streamlit run src/app/app.py
```

That's it. Type a research question and the system retrieves evidence, scores confidence, generates a synthesis memo, evidence table, and annotated bibliography — all grounded in the 20-paper corpus.

---

## 📚 What Is This?

The Mars Life Research Portal is an intelligent research assistant that synthesizes answers strictly from a curated corpus of peer-reviewed astrobiology papers. It combines:

- **Semantic retrieval** (sentence-transformers + FAISS) to find relevant passages
- **Local LLM synthesis** (Mistral 7B via Ollama) to generate citation-backed memos
- **Trust-first design** — refuses to answer rather than hallucinate a source
- **Three research artifacts** per query: synthesis memo, evidence table, annotated bibliography
- **Gap finder** — identifies what the corpus *can't* answer and suggests follow-up queries

**Corpus:** 20 peer-reviewed papers on Mars habitability, biosignatures, and astrobiology  
**Chunks:** 421 text chunks (4000-char, 400-char overlap)  
**Embeddings:** `intfloat/e5-base-v2` (768-dim, normalized)

---

## 🎯 Core Features

### 1. Research Tab — Ask the Corpus
- Enter any research question
- System retrieves top chunks using dynamic k (adjusts based on question complexity)
- Confidence scoring: retrieval + lexical overlap + confirmation strength
- Generates synthesis memo with inline `[source_id:chunk_id]` citations
- **Refuses** queries with insufficient evidence rather than guessing

### 2. Three Research Artifacts
| Artifact | Description |
|----------|-------------|
| Synthesis Memo | Structured memo: Introduction → Key Findings → Synthesis → Limitations → References |
| Evidence Table | Every chunk mapped to a claim, citation, confidence score, and notes — exportable as CSV |
| Annotated Bibliography | Per-source annotations: claim, method, limitations, why it matters |

### 3. Gap Finder (Stretch Goal)
- LLM-based analysis of what's missing for the specific query
- Suggests targeted follow-up research questions
- Identifies corpus sources that may have partial coverage
- No hardcoded keywords — fully generative

### 4. Trust & Citation Accuracy
- Every claim must cite `[source_id:chunk_id]` from the actual retrieved evidence
- Citations verified against corpus after generation
- Unverified sources flagged with a warning note
- Hallucinated "Author et al., YEAR" style citations blocked by system prompt

### 5. Evaluation Tab
- View live query log with confidence scores
- Run full 20-query batch evaluation
- Summary metrics: answered/refused/avg confidence/citation accuracy
- Representative examples: high confidence, medium confidence, and refused

### 6. Export Tab
- Synthesis memo → Markdown or PDF (HTML fallback, print to PDF)
- Evidence table → CSV
- Annotated bibliography → Markdown
- Full query log → JSONL
- Research threads → JSONL

---

## 📁 Project Structure

```
.
├── README.md
├── requirements.txt
├── run_pipeline.py                # Chunks + embeddings, one-time setup
├── data/
│   ├── data_manifest.csv          # Corpus metadata (20 papers)
│   ├── raw/                       # Original PDFs
│   ├── processed/
│   │   └── chunks.jsonl           # 421 text chunks with metadata
│   └── vector_store/
│       ├── faiss.index            # FAISS vector index
│       ├── id_map.json            # Chunk ID mappings
│       └── embeddings.npy         # 421×768 embedding matrix
├── logs/
│   ├── query_log.jsonl            # All queries with confidence + citations
│   └── threads.jsonl              # Saved research threads
├── report/
│   ├── phase 1 deliverables/      # Phase 1 deliverables
│   └── phase 2 deliverables/      # Phase 2 deliverables
├── src/
│   ├── rag/
│   ├── ├── retrieve.py            # Query and evaluate (from Phase 2)
│   │   └── rag.py                 # Full RAG pipeline 
│   ├── ingest/
│   ├── ├── embed_index.py         # Create embeddings and index
│   │   └── chunk.py               # Parse and chunk documents
│   └── app/
│       └── app.py                 # Streamlit web UI
├── Phase 3 Final Report.pdf       # Final Report
├── AI Usage Disclosure.md        
└── Appendix.md       
```

---

## 🔧 Setup: Full Pipeline

**Step 1 — Build the index** (chunks + embeddings, one-time setup):
```bash
python3 run_pipeline.py
```
Output: `data/processed/chunks.jsonl` + `data/vector_store/faiss.index`

**Step 2 — Launch the portal:**
```bash
streamlit run src/app/app.py
```

> If `data/vector_store/faiss.index` already exists, skip to Step 2.

---

## 📊 Evaluation

**Test set:** 20 queries spanning factual retrieval, synthesis, and edge cases (refusal detection)

| Metric | Result |
|--------|--------|
| Queries answered | ~15/20 |
| Queries correctly refused | ~5/20 |
| Avg confidence (answered) | ~0.81 |
| Citation accuracy | 100% (corpus-verified) |

Run the full eval from the Evaluation tab in the UI, or see `logs/query_log.jsonl` for individual results.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `ollama: command not found` | Run `ollama serve` in a separate terminal |
| `mistral:7b not found` | Run `ollama pull mistral:7b` |
| `FileNotFoundError: chunks.jsonl` | Run `1.chunking.ipynb` first |
| `FAISS index not found` | Run `2.embed_and_index.ipynb` after chunking |
| Low confidence / all refused | Expected for edge-case queries — system refuses by design |
| Port 8501 unavailable | Another Streamlit app is running; close it or use `--server.port 8502` |

---

## 🔬 References

- Embedding model: [intfloat/e5-base-v2](https://huggingface.co/intfloat/e5-base-v2)
- Vector store: [FAISS](https://github.com/facebookresearch/faiss)
- Local LLM: [Ollama](https://ollama.com) + [Mistral 7B](https://mistral.ai)
- PDF parsing: [pdfplumber](https://github.com/jsvine/pdfplumber)
- UI: [Streamlit](https://streamlit.io)

---

**System Version:** v3.0 — Phase 3 Portal  
**Corpus:** 20 peer-reviewed papers · 421 chunks · Mars habitability & astrobiology
