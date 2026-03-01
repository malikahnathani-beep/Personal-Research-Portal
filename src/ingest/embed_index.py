"""
src/ingest/embed_index.py
Embed chunks with e5-base-v2 and build FAISS index.
Called by run_pipeline.py
"""

from pathlib import Path
import numpy as np
import orjson
import faiss
from sentence_transformers import SentenceTransformer

# ── Config ─────────────────────────────────────────────────────────────────────
CHUNKS_PATH   = Path("data/processed/chunks.jsonl")
VECTOR_DIR    = Path("data/vector_store")
EMBED_MODEL   = "intfloat/e5-base-v2"
BATCH_SIZE    = 32


# ── Main ───────────────────────────────────────────────────────────────────────
def run():
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    # Load chunks
    chunks = [orjson.loads(line) for line in CHUNKS_PATH.open("rb") if line.strip()]
    print(f"Loaded {len(chunks)} chunks")

    # Load model
    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    # Embed
    texts = [f"passage: {c['text']}" for c in chunks]
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)
    print(f"Embeddings shape: {embeddings.shape}")

    # Build FAISS index
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Save artifacts
    faiss.write_index(index, str(VECTOR_DIR / "faiss.index"))

    id_map = [{"source_id": c["source_id"], "chunk_id": c["chunk_id"]} for c in chunks]
    with (VECTOR_DIR / "id_map.json").open("wb") as f:
        f.write(orjson.dumps(id_map))

    np.save(VECTOR_DIR / "embeddings.npy", embeddings)

    print(f"\n{'='*50}")
    print(f"EMBEDDING & INDEXING COMPLETE")
    print(f"  Index size : {index.ntotal}")
    print(f"  Saved to   : {VECTOR_DIR}")


if __name__ == "__main__":
    run()
