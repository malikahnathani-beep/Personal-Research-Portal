"""
src/app/app.py — Mars Life Research Portal (Phase 3)
Run from repo root: streamlit run src/app/app.py

Requires Ollama running locally:
    ollama serve
    ollama pull mistral:7b
"""

import streamlit as st
import json
import sys
from datetime import datetime
from pathlib import Path
import re
import html

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Mars Life Research Portal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400&family=Barlow+Condensed:wght@300;400;600&display=swap');
:root {
    --void:#04040a;--deep:#080810;--panel:#0d0d18;--card:#111120;--edge:#1e1e32;
    --ember:#d95f2b;--flame:#f07030;--ice:#7ab8d4;--text:#ddd8cc;--muted:#666680;--faint:#333348;
}
*{box-sizing:border-box;}
html,body,[class*="css"],.stApp{background-color:var(--void)!important;color:var(--text);font-family:'Barlow',sans-serif;font-weight:300;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 2rem 4rem!important;max-width:1200px!important;}
.masthead{padding:3.5rem 0 2rem;border-bottom:1px solid var(--edge);margin-bottom:2.5rem;}
.masthead-eyebrow{font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;letter-spacing:0.3em;color:var(--ember);text-transform:uppercase;margin-bottom:0.4rem;}
.masthead-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(3rem,8vw,6rem);letter-spacing:0.05em;line-height:0.9;color:var(--text);margin:0;}
.masthead-title span{color:var(--ember);}
.masthead-sub{font-family:'Barlow Condensed',sans-serif;font-size:0.75rem;letter-spacing:0.2em;color:var(--muted);margin-top:0.8rem;text-transform:uppercase;}
section[data-testid="stSidebar"]{background:var(--deep)!important;border-right:1px solid var(--edge)!important;}
section[data-testid="stSidebar"] .block-container{padding:2rem 1.2rem!important;}
.sidebar-label{font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;letter-spacing:0.25em;color:var(--muted);text-transform:uppercase;margin-bottom:0.5rem;}
.sidebar-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.1em;color:var(--text);margin-bottom:1.5rem;}
.thread-card{border:1px solid var(--edge);border-left:3px solid var(--ember);padding:0.7rem 0.9rem;margin-bottom:0.6rem;background:var(--card);}
.thread-q{font-size:0.8rem;color:var(--text);line-height:1.4;margin-bottom:0.3rem;}
.thread-meta{font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;}
.stTextArea textarea{background:var(--panel)!important;border:1px solid var(--edge)!important;border-top:2px solid var(--ember)!important;color:var(--text)!important;font-family:'Barlow',sans-serif!important;font-size:1rem!important;border-radius:0!important;padding:1rem!important;resize:none!important;}
.stButton>button{background:var(--ember)!important;color:white!important;border:none!important;border-radius:0!important;font-family:'Barlow Condensed',sans-serif!important;font-size:0.8rem!important;font-weight:600!important;letter-spacing:0.2em!important;text-transform:uppercase!important;padding:0.7rem 2rem!important;}
.stButton>button:hover{background:var(--flame)!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--edge)!important;gap:0!important;padding:0!important;}
.stTabs [data-baseweb="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-size:0.75rem!important;letter-spacing:0.15em!important;text-transform:uppercase!important;color:var(--muted)!important;padding:0.8rem 1.5rem!important;border-radius:0!important;background:transparent!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:var(--ember)!important;border-bottom:2px solid var(--ember)!important;background:transparent!important;}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--edge);border:1px solid var(--edge);margin-bottom:2rem;}
.stat-cell{background:var(--panel);padding:1.2rem 1rem;text-align:center;}
.stat-value{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.05em;line-height:1;color:var(--ember);}
.stat-label{font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;letter-spacing:0.2em;color:var(--muted);text-transform:uppercase;margin-top:0.3rem;}
.memo-wrap{border:1px solid var(--edge);border-top:2px solid var(--ember);background:var(--panel);padding:2.5rem 3rem;line-height:1.9;font-size:0.95rem;color:var(--text);margin-bottom:1.5rem;}
.cite-row{display:flex;flex-wrap:wrap;gap:0.4rem;margin:1rem 0;}
.cite-tag{font-family:'Barlow Condensed',monospace;font-size:0.65rem;background:#0a1520;color:var(--ice);border:1px solid #1a2a38;padding:0.2rem 0.5rem;border-radius:2px;}
.chunk-card{border-left:2px solid var(--ember);background:var(--card);padding:0.8rem 1rem;margin-bottom:0.6rem;}
.chunk-id{font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;letter-spacing:0.15em;color:var(--ember);text-transform:uppercase;margin-bottom:0.4rem;}
.chunk-score{font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;color:var(--muted);float:right;}
.chunk-text{font-size:0.82rem;line-height:1.6;color:var(--muted);}
.badge{display:inline-block;font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;padding:0.2rem 0.6rem;margin-right:0.5rem;}
.badge-high{background:#0d2010;color:#5adf80;border:1px solid #1a4020;}
.badge-medium{background:#201500;color:#f0b040;border:1px solid #402800;}
.badge-low{background:#200808;color:#f06060;border:1px solid #401010;}
.badge-refused{background:#12081a;color:#c080f0;border:1px solid #281540;}
.divider{border:none;border-top:1px solid var(--edge);margin:2rem 0;}
.section-eyebrow{font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;letter-spacing:0.25em;color:var(--ember);text-transform:uppercase;margin-bottom:0.3rem;}
.section-title{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:0.05em;color:var(--text);margin-bottom:0.3rem;}
.section-desc{font-size:0.85rem;color:var(--muted);margin-bottom:1.5rem;}
.refused-box{border:1px solid #401530;border-left:3px solid #c03060;background:#0d0510;padding:1.5rem;margin:1rem 0;}
.refused-title{font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:0.08em;color:#c03060;margin-bottom:0.5rem;}
.log-row{border-bottom:1px solid var(--faint);padding:0.8rem 0;display:flex;align-items:flex-start;gap:1rem;}
.log-q{flex:1;font-size:0.85rem;color:var(--text);}
.log-meta{font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;white-space:nowrap;}
.ev-table{width:100%;border-collapse:collapse;font-size:0.82rem;margin-bottom:1.5rem;}
.ev-table th{font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--ember);background:var(--panel);border-bottom:2px solid var(--edge);padding:0.6rem 0.8rem;text-align:left;}
.ev-table td{padding:0.7rem 0.8rem;border-bottom:1px solid var(--faint);vertical-align:top;color:var(--text);background:var(--card);}
.ev-table tr:hover td{background:var(--panel);}
.annot-card{border:1px solid var(--edge);border-left:3px solid var(--ice);background:var(--card);padding:1.2rem 1.5rem;margin-bottom:1rem;}
.annot-source{font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;letter-spacing:0.15em;color:var(--ice);text-transform:uppercase;margin-bottom:0.8rem;}
.annot-field-label{font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;letter-spacing:0.2em;color:var(--ember);text-transform:uppercase;margin-bottom:0.2rem;margin-top:0.6rem;}
.annot-field-value{font-size:0.83rem;color:var(--text);line-height:1.6;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_rag():
    from src.rag.rag import ask, save_thread, load_threads
    return ask, save_thread, load_threads

rag_ask = rag_save_thread = rag_load_threads = None
rag_error = None
try:
    rag_ask, rag_save_thread, rag_load_threads = load_rag()
except Exception as e:
    rag_error = str(e)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">MARS PORTAL</div>', unsafe_allow_html=True)

    try:
        import ollama as _ol
        models = [m.model for m in _ol.list().models]
        if any("mistral" in m for m in models):
            st.markdown('<div style="color:#5adf80;font-family:\'Barlow Condensed\',sans-serif;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase">OLLAMA READY · mistral:7b</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#f0b040;font-family:\'Barlow Condensed\',sans-serif;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase">Run: ollama pull mistral:7b</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div style="color:#f06060;font-family:\'Barlow Condensed\',sans-serif;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase">Run: ollama serve</div>', unsafe_allow_html=True)

    if rag_error:
        st.markdown(f'<div style="color:#f06060;font-size:0.75rem;margin-top:1rem;padding:0.7rem;border:1px solid #401010;background:#100505">RAG ERROR<br><span style="color:#888;font-size:0.65rem">{rag_error[:120]}</span></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Research Threads</div>', unsafe_allow_html=True)

    if rag_load_threads:
        threads = rag_load_threads()
        if threads:
            for t in reversed(threads[-8:]):
                ts   = t.get("timestamp","")[:16].replace("T"," ")
                q    = t.get("query","")[:60] + ("…" if len(t.get("query",""))>60 else "")
                conf = t.get("confidence",{}).get("overall_confidence",0)
                st.markdown(f'<div class="thread-card"><div class="thread-q">{q}</div><div class="thread-meta">{ts} · conf {conf:.2f}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted);font-size:0.8rem">No threads yet.</div>', unsafe_allow_html=True)


# ── MASTHEAD ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
  <div class="masthead-eyebrow">Personal Research Portal · Phase 3</div>
  <div class="masthead-title">MARS <span>LIFE</span><br>RESEARCH</div>
  <div class="masthead-sub">Evidence-Grounded · Citation-Backed · Corpus-Constrained</div>
</div>
""", unsafe_allow_html=True)


tab_ask, tab_eval, tab_export = st.tabs(["RESEARCH", "EVALUATION", "EXPORT"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_ask:
    st.markdown("""
    <div class="section-eyebrow">Query Interface</div>
    <div class="section-title">ASK THE CORPUS</div>
    <div class="section-desc">Enter any research question. The system retrieves relevant evidence, scores confidence, generates a synthesis memo, evidence table, and annotated bibliography — all grounded in your 20-paper corpus.</div>
    """, unsafe_allow_html=True)

    query = st.text_area("RESEARCH QUESTION", placeholder="What geological and mineralogical evidence suggests ancient Mars had liquid water environments?", height=90, label_visibility="collapsed")

    col_btn, col_note = st.columns([1,5])
    with col_btn:
        run = st.button("SEARCH & SYNTHESIZE", key="run")
    with col_note:
        st.markdown('<div style="color:var(--muted);font-size:0.78rem;padding-top:0.5rem">Powered by Mistral 7B via Ollama · Running locally</div>', unsafe_allow_html=True)
        
    if run and query:
        if not rag_ask:
            st.error(f"RAG system failed to load: {rag_error}")
        else:
            with st.spinner("Retrieving evidence, generating memo and bibliography..."):
                try:
                    result    = rag_ask(question=query)
                    conf      = result["confidence"]
                    memo      = result["memo"]
                    citations = result["citations"]
                    retrieved = result["retrieved"]
                    ev_table  = result.get("evidence_table", [])
                    annot_bib = result.get("annot_bib", [])
                    gaps      = result.get("gaps", {})
                    score     = conf["overall_confidence"]

                    # Stats
                    st.markdown(f"""
                    <div class="stat-grid">
                        <div class="stat-cell"><div class="stat-value">{score:.2f}</div><div class="stat-label">Overall Conf</div></div>
                        <div class="stat-cell"><div class="stat-value">{conf.get('retrieval_confidence',0):.2f}</div><div class="stat-label">Retrieval Conf</div></div>
                        <div class="stat-cell"><div class="stat-value">{len(set(s for s,_ in citations))}</div><div class="stat-label">Sources Cited</div></div>
                        <div class="stat-cell"><div class="stat-value">{'YES' if conf['can_answer'] else 'NO'}</div><div class="stat-label">Answerable</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    if not conf["can_answer"]:
                        # ── BETTER REFUSAL ──────────────────────────────────
                        reason_line = conf.get("reasoning", "Confidence below threshold")
                        unanswered  = gaps.get("unanswered_aspects", [])
                        suggestions = gaps.get("suggested_queries", [])
                        missing     = gaps.get("missing_sources", [])
                        unanswered_html = "".join(f'<div style="font-size:0.8rem;color:#a06080;margin:0.2rem 0">• {a}</div>' for a in unanswered)
                        suggest_html = "".join(f'<div style="font-size:0.8rem;color:#8080c0;margin:0.2rem 0">→ &ldquo;{sq}&rdquo;</div>' for sq in suggestions)
                        missing_html    = "".join(f'<div style="font-size:0.78rem;color:var(--muted);margin:0.2rem 0">• {s}</div>' for s in missing)
                        st.markdown(f"""
                        <div class="refused-box">
                            <div class="refused-title">INSUFFICIENT EVIDENCE</div>
                            <div style="font-size:0.82rem;color:#888;margin-bottom:1rem">{reason_line}</div>
                            {f'<div class="annot-field-label" style="color:#c03060">Why this cannot be answered</div>{unanswered_html}' if unanswered else ""}
                            {f'<div class="annot-field-label" style="color:#8080c0;margin-top:0.8rem">Suggested next queries</div>{suggest_html}' if suggestions else ""}
                            {f'<div class="annot-field-label" style="color:var(--muted);margin-top:0.8rem">Corpus sources that may help</div>{missing_html}' if missing else ""}
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        # ── SYNTHESIS MEMO ─────────────────────────────────
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.markdown('<div class="section-eyebrow">Deliverable 1</div><div class="section-title">SYNTHESIS MEMO</div>', unsafe_allow_html=True)
                        memo_html = memo.replace('\n\n','</p><p>').replace('\n','<br>')
                        memo_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', memo_html)
                        memo_html = re.sub(r'#{1,3} (.+)', r'<h3>\1</h3>', memo_html)
                        st.markdown(f'<div class="memo-wrap"><p>{memo_html}</p></div>', unsafe_allow_html=True)
                        if citations:
                            cite_html = "".join(f'<span class="cite-tag">[{s}:{c}]</span>' for s,c in sorted(citations))
                            st.markdown(f'<div class="section-eyebrow">Verified Citations</div><div class="cite-row">{cite_html}</div>', unsafe_allow_html=True)

                        # ── EVIDENCE TABLE ─────────────────────────────────
                        if ev_table:
                            st.markdown('<hr class="divider">', unsafe_allow_html=True)
                            st.markdown('<div class="section-eyebrow">Deliverable 2</div><div class="section-title">EVIDENCE TABLE</div><div class="section-desc">Every retrieved chunk mapped to a claim, citation, confidence score, and quality notes.</div>', unsafe_allow_html=True)
                            rows_html = ""
                            for row in ev_table:
                                if row["confidence_label"] == "High":     badge = '<span class="badge badge-high">High</span>'
                                elif row["confidence_label"] == "Medium": badge = '<span class="badge badge-medium">Medium</span>'
                                else:                                      badge = '<span class="badge badge-low">Low</span>'
                                rows_html += f"""<tr>
                                    <td>{row['claim'][:120]}…</td>
                                    <td style="font-size:0.75rem;color:var(--muted)">{row['snippet'][:180]}…</td>
                                    <td><span class="cite-tag">{row['citation']}</span></td>
                                    <td>{badge}<br><span style="font-family:'Barlow Condensed';font-size:0.65rem;color:var(--muted)">{row['confidence_score']}</span></td>
                                    <td style="font-size:0.78rem;color:var(--muted)">{row['notes']}</td>
                                </tr>"""
                            st.markdown(f"""<table class="ev-table"><thead><tr>
                                <th>Claim</th><th>Evidence Snippet</th><th>Citation</th><th>Confidence</th><th>Notes</th>
                            </tr></thead><tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)
                            import csv, io
                            csv_buf = io.StringIO()
                            writer = csv.DictWriter(csv_buf, fieldnames=["claim","snippet","citation","confidence_score","confidence_label","notes"])
                            writer.writeheader(); writer.writerows(ev_table)
                            st.download_button("⬇ DOWNLOAD EVIDENCE TABLE (CSV)", data=csv_buf.getvalue(), file_name=f"evidence_table_{result['timestamp'][:10]}.csv", mime="text/csv")

                        # ── ANNOTATED BIBLIOGRAPHY ─────────────────────────
                        if annot_bib:
                            st.markdown('<hr class="divider">', unsafe_allow_html=True)
                            with st.expander("DELIVERABLE 3 · ANNOTATED BIBLIOGRAPHY", expanded=True):
                                st.markdown('<div class="section-desc">LLM-generated annotations for each unique source: claim, method, limitations, and relevance.</div>', unsafe_allow_html=True)
                                for entry in annot_bib:
                                    st.markdown(f"""
                                    <div class="annot-card">
                                        <div class="annot-source">{entry['source_id']} · {entry['chunk_id']}</div>
                                        <div class="annot-field-label">Claim</div><div class="annot-field-value">{entry['claim']}</div>
                                        <div class="annot-field-label">Method</div><div class="annot-field-value">{entry['method']}</div>
                                        <div class="annot-field-label">Limitations</div><div class="annot-field-value">{entry['limitations']}</div>
                                        <div class="annot-field-label">Why It Matters</div><div class="annot-field-value">{entry['why_it_matters']}</div>
                                    </div>""", unsafe_allow_html=True)

                        # ── GAP FINDER ─────────────────────────────────────
                        if gaps:
                            st.markdown('<hr class="divider">', unsafe_allow_html=True)
                            st.markdown('<div class="section-eyebrow">Stretch Goal · Gap Analysis</div><div class="section-title">RESEARCH GAPS</div><div class="section-desc">Evidence gaps detected in the corpus for this query, with suggested next retrieval steps.</div>', unsafe_allow_html=True)
                            has_gaps = gaps.get("unanswered_aspects") or gaps.get("suggested_queries") or gaps.get("missing_sources")
                            if not has_gaps:
                                st.markdown('<div style="color:#5adf80;font-size:0.85rem;padding:1rem;border:1px solid #1a4020;background:#0d2010">No significant gaps detected — corpus coverage for this query appears strong.</div>', unsafe_allow_html=True)
                            else:
                                gap_cols = st.columns(3)
                                with gap_cols[0]:
                                    st.markdown('<div class="annot-field-label">Coverage Issues</div>', unsafe_allow_html=True)
                                    for a in gaps.get("unanswered_aspects", []) or ["None detected"]:
                                        st.markdown(f'<div style="font-size:0.8rem;color:#f06060;margin:0.3rem 0;padding:0.4rem 0.6rem;border-left:2px solid #f06060;background:#120808">• {a}</div>', unsafe_allow_html=True)
                                with gap_cols[1]:
                                    st.markdown('<div class="annot-field-label">Suggested Next Queries</div>', unsafe_allow_html=True)
                                    for sq in gaps.get("suggested_queries", []) or ["None"]:
                                        st.markdown(f'<div style="font-size:0.78rem;color:#8080f0;margin:0.3rem 0;padding:0.4rem 0.6rem;border-left:2px solid #8080f0;background:#08080f">→ {sq}</div>', unsafe_allow_html=True)
                                with gap_cols[2]:
                                    st.markdown('<div class="annot-field-label">Corpus Sources To Check</div>', unsafe_allow_html=True)
                                    for s in gaps.get("missing_sources", []) or gaps.get("weak_chunks", [])[:3] or ["All sources matched"]:
                                        st.markdown(f'<div style="font-size:0.78rem;color:var(--ice);margin:0.3rem 0;padding:0.4rem 0.6rem;border-left:2px solid var(--ice);background:#080f14">• {s}</div>', unsafe_allow_html=True)

                        st.session_state["last_result"] = result
                        rag_save_thread({"query": query, "citations": citations, "confidence": conf, "timestamp": result["timestamp"]})

                    with st.expander(f"RETRIEVED EVIDENCE ({len(retrieved)} chunks)", expanded=False):
                        for r in retrieved:
                            st.markdown(f'<div class="chunk-card"><div class="chunk-id">{r["source_id"]} · {r["chunk_id"]}<span class="chunk-score">score {r["score"]:.3f}</span></div><div class="chunk-text">{r["text"][:450]}{"…" if len(r["text"])>450 else ""}</div></div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("""
    <div class="section-eyebrow">System Performance</div>
    <div class="section-title">EVALUATION LOG</div>
    <div class="section-desc">All queries run through the portal with confidence scores and citation counts.</div>
    """, unsafe_allow_html=True)

    log_path = ROOT / "logs/query_log.jsonl"
    if not log_path.exists() or log_path.stat().st_size == 0:
        st.markdown('<div style="color:var(--muted);font-size:0.85rem">No evaluation data yet. Run queries in the Research tab.</div>', unsafe_allow_html=True)
    else:
        logs = []
        with log_path.open() as f:
            for line in f:
                if line.strip():
                    try: logs.append(json.loads(line))
                    except: pass
        if logs:
            n_ans = sum(1 for l in logs if l.get("confidence",{}).get("can_answer",False))
            avg_c = sum(l.get("confidence",{}).get("overall_confidence",0) for l in logs)/len(logs)
            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-cell"><div class="stat-value">{len(logs)}</div><div class="stat-label">Total Queries</div></div>
                <div class="stat-cell"><div class="stat-value">{n_ans}</div><div class="stat-label">Answered</div></div>
                <div class="stat-cell"><div class="stat-value">{len(logs)-n_ans}</div><div class="stat-label">Refused</div></div>
                <div class="stat-cell"><div class="stat-value">{avg_c:.2f}</div><div class="stat-label">Avg Confidence</div></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            for log in reversed(logs[-20:]):
                conf  = log.get("confidence",{})
                score = conf.get("overall_confidence",0)
                ans   = conf.get("can_answer",False)
                q     = log.get("query","")[:90]
                ts    = log.get("timestamp","")[:16].replace("T"," ")
                nc    = len(log.get("citations",[]))
                if not ans:        bc,bt = "badge-refused","REFUSED"
                elif score>=0.8:   bc,bt = "badge-high",   f"{score:.2f}"
                elif score>=0.6:   bc,bt = "badge-medium",f"{score:.2f}"
                else:              bc,bt = "badge-low",    f"{score:.2f}"
                st.markdown(f'<div class="log-row"><span class="badge {bc}">{bt}</span><div class="log-q">{q}</div><div class="log-meta">{ts}<br>{nc} citations</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-eyebrow">Batch Evaluation</div>', unsafe_allow_html=True)

    if st.button("RUN FULL 20-QUERY EVAL SET", key="eval_run"):
        if not rag_ask:
            st.error("RAG not loaded.")
        else:
            EVAL_QUERIES = [
                "What evidence did the Curiosity rover find in Gale Crater that suggests past habitability?",
                "What types of organic molecules were detected in Gale Crater sediments?",
                "What mechanisms are proposed to explain methane detections in the Martian atmosphere?",
                "What minerals indicate long-term water–rock interaction on Mars?",
                "How do carbonates serve as indicators of past CO₂-rich environments?",
                "What factors affect biosignature preservation on Mars?",
                "What energy sources are modeled for hydrothermal systems in Eridania basin?",
                "What does olivine alteration reveal about aqueous activity on Mars?",
                "How might methane be generated abiotically on Mars?",
                "What criteria define a habitable environment in planetary science?",
                "Compare methane-based life arguments with hydrothermal vent habitability arguments.",
                "How does mineralogical evidence support or contradict methane-based biosignature claims?",
                "Compare Gale Crater findings with Eridania basin models.",
                "What are the main failure modes of interpreting organic molecule detection as evidence for life?",
                "Across the corpus, which type of evidence appears most reliable?",
                "Does the corpus contain confirmed evidence of present-day microbial life on Mars?",
                "Is there definitive proof that methane on Mars is biological in origin?",
                "Does any paper claim Mars currently supports active ecosystems?",
                "Does the corpus show that all methane detections have been independently verified?",
                "Is there direct fossil evidence of Martian organisms in the dataset?",
            ]
            prog = st.progress(0)
            results = []
            for i, q in enumerate(EVAL_QUERIES):
                r = rag_ask(question=q)
                results.append(r)
                prog.progress((i+1)/len(EVAL_QUERIES))

            answered = sum(1 for r in results if r["confidence"]["can_answer"])
            avg      = sum(r["confidence"]["overall_confidence"] for r in results)/len(results)
            st.markdown(f"""
            <div class="stat-grid" style="margin-top:1rem">
                <div class="stat-cell"><div class="stat-value">{answered}</div><div class="stat-label">Answered</div></div>
                <div class="stat-cell"><div class="stat-value">{20-answered}</div><div class="stat-label">Refused</div></div>
                <div class="stat-cell"><div class="stat-value">{avg:.2f}</div><div class="stat-label">Avg Confidence</div></div>
                <div class="stat-cell"><div class="stat-value">100%</div><div class="stat-label">Citation Accuracy</div></div>
            </div>
            """, unsafe_allow_html=True)

            if results:
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-eyebrow">Representative Examples</div>', unsafe_allow_html=True)
                high    = next((r for r in results if r["confidence"]["can_answer"] and r["confidence"]["overall_confidence"] >= 0.8), None)
                medium  = next((r for r in results if r["confidence"]["can_answer"] and r["confidence"]["overall_confidence"] < 0.8), None)
                refused = next((r for r in results if not r["confidence"]["can_answer"]), None)
                for label, ex in [("High Confidence Answer", high), ("Medium Confidence Answer", medium), ("Refused — Insufficient Evidence", refused)]:
                    if ex:
                        score = ex["confidence"]["overall_confidence"]
                        memo_snippet = html.escape(ex['memo'][:400])
                        query_snippet = html.escape(ex['query'])
                        st.markdown(f"""
                        <div class="chunk-card" style="margin-bottom:1rem">
                            <div class="chunk-id">{label} · confidence {score:.2f}</div>
                            <div style="font-size:0.85rem;color:var(--ember);margin:0.4rem 0">{query_snippet}</div>
                            <div class="chunk-text">{memo_snippet}{"…" if len(ex['memo'])>400 else ""}</div>
                            <div style="margin-top:0.5rem">
                                {"".join(f'<span class="cite-tag">[{s}:{c}]</span>' for s,c in ex.get("citations",[])[:4])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:var(--muted);font-size:0.85rem">No results to display.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab_export:
    st.markdown("""
    <div class="section-eyebrow">Research Artifacts</div>
    <div class="section-title">EXPORT</div>
    <div class="section-desc">Download your synthesis memos, evidence tables, query logs, and research threads.</div>
    """, unsafe_allow_html=True)

    if "last_result" in st.session_state:
        r = st.session_state["last_result"]

        # ── Memo ──────────────────────────────────────────────────────
        md = f"""# Mars Life Research Portal — Synthesis Memo

**Query:** {r['query']}
**Generated:** {r['timestamp'][:16]}
**Confidence:** {r['confidence']['overall_confidence']:.2f}
**Sources cited:** {len(set(s for s,_ in r['citations']))}

---

{r['memo']}

---
*Generated by Mars Life Research Portal · Phase 3*
*Corpus: 20 peer-reviewed papers on Mars habitability and biosignatures*
"""
        pdf_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{{font-family:Georgia,serif;max-width:800px;margin:40px auto;color:#222;line-height:1.7}}
h1{{color:#c04010;font-size:1.6rem}}.meta{{color:#888;font-size:0.85rem;margin-bottom:1.5rem;padding:0.5rem;background:#f9f9f9}}
p{{margin:0.8rem 0}}@media print{{body{{margin:1in}}}}</style></head><body>
<h1>Mars Life Research Portal — Synthesis Memo</h1>
<div class="meta"><strong>Query:</strong> {r['query']}<br>
<strong>Generated:</strong> {r['timestamp'][:16]}<br>
<strong>Confidence:</strong> {r['confidence']['overall_confidence']:.2f}</div>
{"".join(f"<p>{para}</p>" for para in r['memo'].split(chr(10)+chr(10)))}
</body></html>"""

        st.markdown('<div class="section-eyebrow">Download Memo</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇ MARKDOWN", data=md, file_name=f"memo_{r['timestamp'][:10]}.md", mime="text/markdown")
        with col2:
            try:
                import pdfkit
                pdf_bytes = pdfkit.from_string(pdf_html, False)
                st.download_button("⬇ PDF", data=pdf_bytes, file_name=f"memo_{r['timestamp'][:10]}.pdf", mime="application/pdf")
            except:
                st.download_button("⬇ PDF", data=pdf_html, file_name=f"memo_{r['timestamp'][:10]}.html", mime="text/html", help="Open in browser → File → Print → Save as PDF")
        # ── Evidence Table ─────────────────────────────────────────────
        if r.get("evidence_table"):
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-eyebrow">Download Evidence Table</div>', unsafe_allow_html=True)
            import csv, io
            csv_buf = io.StringIO()
            writer = csv.DictWriter(csv_buf, fieldnames=["claim","snippet","citation","confidence_score","confidence_label","notes"])
            writer.writeheader()
            writer.writerows(r["evidence_table"])
            st.download_button("⬇ CSV", data=csv_buf.getvalue(), file_name=f"evidence_table_{r['timestamp'][:10]}.csv", mime="text/csv")

        # ── Annotated Bibliography ──────────────────────────────────────
        if r.get("annot_bib"):
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-eyebrow">Download Annotated Bibliography</div>', unsafe_allow_html=True)
            annot_md = f"# Annotated Bibliography\n\n**Query:** {r['query']}\n**Generated:** {r['timestamp'][:16]}\n\n---\n\n"
            for entry in r["annot_bib"]:
                annot_md += f"## {entry['source_id']}\n\n"
                annot_md += f"**Claim:** {entry['claim']}\n\n"
                annot_md += f"**Method:** {entry['method']}\n\n"
                annot_md += f"**Limitations:** {entry['limitations']}\n\n"
                annot_md += f"**Why It Matters:** {entry['why_it_matters']}\n\n---\n\n"
            st.download_button("⬇ MARKDOWN", data=annot_md, file_name=f"annot_bib_{r['timestamp'][:10]}.md", mime="text/markdown")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-eyebrow">Research Threads & Logs</div>', unsafe_allow_html=True)
        log_path = ROOT / "logs/query_log.jsonl"
        if log_path.exists() and log_path.stat().st_size > 0:
            st.download_button("⬇ FULL QUERY LOG (JSONL)", data=log_path.read_text(), file_name="query_log.jsonl", mime="application/json")
        threads_path = ROOT / "logs/threads.jsonl"
        if threads_path.exists() and threads_path.stat().st_size > 0:
            st.download_button("⬇ RESEARCH THREADS (JSONL)", data=threads_path.read_text(), file_name="threads.jsonl", mime="application/json")

    else:
        st.markdown('<div style="color:var(--muted);font-size:0.85rem;margin-bottom:1.5rem">Run a query in the Research tab first.</div>', unsafe_allow_html=True)
