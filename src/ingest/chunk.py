"""
src/ingest/chunk.py
Parse PDFs from manifest and chunk into overlapping text segments.
Called by run_pipeline.py
"""

import os, json, re
from pathlib import Path
import pandas as pd

import pdfplumber

# ── Config ─────────────────────────────────────────────────────────────────────
MANIFEST_PATH = Path("data/data_manifest.csv")
PROCESSED_DIR = Path("data/processed")
CHUNKS_PATH   = PROCESSED_DIR / "chunks.jsonl"

CHUNK_CHARS   = 4000
OVERLAP_CHARS = 400


# ── Text cleaning ──────────────────────────────────────────────────────────────
def clean_text(s: str) -> str:
    if not s:
        return ''
    s = re.sub(r'(\w)-\n(\w)', r'\1\2', s)   # dehyphenate
    s = s.replace('\r', '\n')
    s = re.sub(r'\n{3,}', '\n\n', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    return s.strip()


# ── PDF extraction ─────────────────────────────────────────────────────────────
def extract_pages(pdf_path: Path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            txt = clean_text(page.extract_text() or '')
            pages.append({'page': i, 'text': txt})
    return pages


# ── Chunking ───────────────────────────────────────────────────────────────────
def chunk_text(full_text: str, chunk_chars: int = CHUNK_CHARS, overlap_chars: int = OVERLAP_CHARS):
    full_text = full_text.strip()
    if not full_text:
        return []
    chunks, start, n = [], 0, len(full_text)
    while start < n:
        end   = min(start + chunk_chars, n)
        chunk = full_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap_chars)
    return chunks


# ── Per-source builder ─────────────────────────────────────────────────────────
def build_chunks_for_source(row):
    source_id = row['source_id']
    pdf_path  = Path(row['raw_path']).with_suffix('.pdf')

    try:
        pages = extract_pages(pdf_path)
    except FileNotFoundError:
        print(f"  ERROR: File not found — {pdf_path}")
        return []
    except Exception as e:
        print(f"  ERROR: {source_id}: {e}")
        return []

    nonempty = [p for p in pages if p['text']]
    if not nonempty:
        print(f"  WARNING: No text extracted — {source_id}")
        return []

    full_text = "\n\n".join(p['text'] for p in nonempty)
    chunks    = chunk_text(full_text)

    out = []
    for idx, c in enumerate(chunks):
        out.append({
            'chunk_id':  f"{source_id}_chunk_{idx:04d}",
            'source_id': source_id,
            'title':     row.get('title', ''),
            'authors':   row.get('authors', ''),
            'year':      int(row['year']) if str(row.get('year', '')).isdigit() else row.get('year'),
            'raw_path':  str(pdf_path),
            'text':      c
        })
    return out


# ── Main ───────────────────────────────────────────────────────────────────────
def run():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    assert MANIFEST_PATH.exists(), f"Manifest not found at {MANIFEST_PATH.resolve()}"
    manifest = pd.read_csv(MANIFEST_PATH)
    print(f"Loaded manifest: {len(manifest)} sources\n")

    all_chunks, successful, failed = [], [], []

    for _, row in manifest.iterrows():
        chunks = build_chunks_for_source(row)
        if chunks:
            all_chunks.extend(chunks)
            successful.append(row['source_id'])
            print(f"  ✓ {row['source_id']}: {len(chunks)} chunks")
        else:
            failed.append(row['source_id'])

    with open(CHUNKS_PATH, 'w', encoding='utf-8') as f:
        for ch in all_chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + '\n')

    print(f"\n{'='*50}")
    print(f"CHUNKING COMPLETE")
    print(f"  Sources processed : {len(successful)}/{len(manifest)}")
    print(f"  Total chunks      : {len(all_chunks)}")
    print(f"  Output            : {CHUNKS_PATH}")
    if failed:
        print(f"  Failed            : {failed}")


if __name__ == "__main__":
    run()
