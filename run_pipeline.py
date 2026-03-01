"""
run_pipeline.py — Single command entrypoint
Usage:
    python run_pipeline.py

    # Run a query (retrieval + answer + log)
    python run_pipeline.py --query "What evidence did Curiosity find in Gale Crater?"

Requires Ollama running locally:
    ollama serve
    ollama pull llama3.2
"""

import sys
import argparse
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingest.chunk import run as run_chunking
from src.ingest.embed_index import run as run_embedding
from src.rag.retrieve import query_and_log


def run_pipeline():
    print("\n" + "="*60)
    print("MARS LIFE RESEARCH PORTAL — FULL PIPELINE")
    print("="*60 + "\n")

    print("STAGE 1: Chunking PDFs...")
    print("-"*40)
    run_chunking()

    print("\nSTAGE 2: Embedding & Indexing...")
    print("-"*40)
    run_embedding()

    print("\nSTAGE 3: Smoke Test — Retrieval + Answer + Log")
    print("-"*40)
    query_and_log("What evidence did Curiosity find in Gale Crater?")

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("Run the portal: streamlit run src/app/app.py")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mars Life Research Portal")
    parser.add_argument("--query", type=str, default=None, help="Run a single query and log results")
    args = parser.parse_args()

    if args.query:
        # Single query mode — retrieval + answer + log
        query_and_log(args.query)
    else:
        # Full pipeline mode — chunk + embed + index + smoke test
        run_pipeline()
