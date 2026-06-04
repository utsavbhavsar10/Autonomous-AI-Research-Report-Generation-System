"""
Autonomous AI Research System — Streamlit Dashboard

Run:
    streamlit run streamlit_app.py

Make sure the FastAPI backend is up first:
    uvicorn app.main:app --reload
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

API_BASE = os.getenv("RESEARCH_API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="Autonomous AI Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# Styling — animated aurora background + glassmorphism panels
# ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Static background */
    .stApp {
        background: #0b1024;
        color: #e6e8f5;
    }

    /* Glass panels */
    .glass {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 22px 26px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        margin-bottom: 18px;
    }

    /* Heading */
    .hero {
        text-align: center;
        padding: 18px 0 6px 0;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #ec4899, #38bdf8);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero p {
        color: #a5acc7;
        margin: 6px 0 0 0;
        font-size: 0.98rem;
    }

    /* Status pills */
    .pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .pill-queued    { background: rgba(148,163,184,0.18); color: #cbd5e1; }
    .pill-searching { background: rgba(56,189,248,0.18);  color: #7dd3fc; }
    .pill-analyzing { background: rgba(168,85,247,0.20);  color: #d8b4fe; }
    .pill-generating{ background: rgba(236,72,153,0.20);  color: #f9a8d4; }
    .pill-processing{ background: rgba(250,204,21,0.18);  color: #fde68a; }
    .pill-complete  { background: rgba(34,197,94,0.20);   color: #86efac; }
    .pill-failed    { background: rgba(239,68,68,0.20);   color: #fca5a5; }

    /* Agent feed (Claude Code / Copilot style) */
    .feed-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 12px;
        border-left: 2px solid rgba(167,139,250,0.6);
        margin: 6px 0;
        background: rgba(255,255,255,0.03);
        border-radius: 0 10px 10px 0;
        font-family: 'Fira Code', 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        animation: feedIn 0.35s ease-out;
    }
    @keyframes feedIn {
        from { opacity: 0; transform: translateX(-6px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    .feed-icon { font-size: 1.1rem; }
    .feed-time { color: #6b7280; font-size: 0.75rem; }
    .feed-text { color: #e5e7eb; }

    /* Thinking dots */
    .thinking {
        display: inline-block;
    }
    .thinking::after {
        content: '';
        animation: dots 1.4s steps(4, end) infinite;
    }
    @keyframes dots {
        0%, 20% { content: ''; }
        40%     { content: '.'; }
        60%     { content: '..'; }
        80%,100% { content: '...'; }
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #6366f1, #ec4899);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 8px 18px;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(99,102,241,0.45);
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background: rgba(15, 20, 45, 0.55) !important;
        color: #e6e8f5 !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 12px !important;
    }
    .stSelectbox > div > div {
        background: rgba(15, 20, 45, 0.55) !important;
        border-radius: 12px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(11, 16, 36, 0.7) !important;
        backdrop-filter: blur(14px);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Ensure content sits above stars */
    .block-container { position: relative; z-index: 1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────────────────────────────
def api_get(path: str, **kwargs):
    return requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)

def api_post(path: str, **kwargs):
    return requests.post(f"{API_BASE}{path}", timeout=30, **kwargs)

def start_job(query: str, depth: str) -> dict | None:
    try:
        r = api_post("/research", json={"query": query, "depth": depth, "format": "markdown"})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Failed to start research: {e}")
        return None

def fetch_job(job_id: str) -> dict | None:
    try:
        r = api_get(f"/research/{job_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def fetch_jobs(limit: int = 20) -> list[dict]:
    try:
        r = api_get(f"/research?limit={limit}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

def fetch_reports() -> list[dict]:
    try:
        r = api_get("/reports")
        if r.status_code == 200:
            return r.json()
    except Exception:
        return []
    return []

def download_report_bytes(filename: str, as_pdf: bool) -> bytes | None:
    try:
        suffix = "/pdf" if as_pdf else ""
        r = api_get(f"/reports/{filename}{suffix}")
        if r.status_code == 200:
            return r.content
    except Exception as e:
        st.error(f"Download failed: {e}")
    return None

# ──────────────────────────────────────────────────────────────────────
# Status helpers
# ──────────────────────────────────────────────────────────────────────
STATUS_ICONS = {
    "queued":     "🕐",
    "searching":  "🔎",
    "analyzing":  "🧪",
    "generating": "✍️",
    "processing": "⚙️",
    "complete":   "✅",
    "failed":     "❌",
}

AGENT_PIPELINE = [
    ("queued",     "Planner Agent",  "Job queued, planning sub-tasks"),
    ("searching",  "Research Agent", "Searching the web and gathering sources"),
    ("analyzing",  "Analyst Agent",  "Evaluating source quality and relevance"),
    ("generating", "Writer Agent",   "Drafting the structured report"),
    ("complete",   "Reviewer Agent", "Finalized — report saved"),
]

def status_pill(status: str) -> str:
    cls = f"pill pill-{status}" if status in STATUS_ICONS else "pill pill-queued"
    icon = STATUS_ICONS.get(status, "•")
    return f'<span class="{cls}">{icon} {status}</span>'

def feed_entry(icon: str, text: str, ts: str | None = None) -> str:
    ts = ts or datetime.now().strftime("%H:%M:%S")
    return (
        f'<div class="feed-item">'
        f'<span class="feed-icon">{icon}</span>'
        f'<span style="flex:1;"><span class="feed-text">{text}</span></span>'
        f'<span class="feed-time">{ts}</span>'
        f'</div>'
    )

# ──────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────
if "active_job_id" not in st.session_state:
    st.session_state.active_job_id = None
if "feed" not in st.session_state:
    st.session_state.feed = []   # list[str] of rendered feed entries
if "last_status" not in st.session_state:
    st.session_state.last_status = None
if "last_progress" not in st.session_state:
    st.session_state.last_progress = None

# ──────────────────────────────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>🧠 Autonomous AI Research System</h1>
        <p>Multi-agent pipeline · Planner → Research → Analyst → Writer → Reviewer</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────
# Sidebar — API health + recent jobs
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System")
    try:
        h = api_get("/research/health/check")
        if h.status_code == 200:
            st.success(f"API online · {API_BASE}")
        else:
            st.warning(f"API status: {h.status_code}")
    except Exception:
        st.error(f"API offline · {API_BASE}")
        st.caption("Start the backend:  `uvicorn app.main:app --reload`")

    st.markdown("---")
    st.markdown("### 📜 Recent Jobs")
    recent = fetch_jobs(limit=10)
    if not recent:
        st.caption("No jobs yet.")
    for j in recent:
        jid = j["job_id"]
        short = jid[:8]
        label = (j["query"][:40] + "…") if len(j["query"]) > 40 else j["query"]
        if st.button(f"{STATUS_ICONS.get(j['status'], '•')} {short} — {label}", key=f"recent_{jid}", use_container_width=True):
            st.session_state.active_job_id = jid
            st.session_state.feed = []
            st.session_state.last_status = None
            st.session_state.last_progress = None
            st.rerun()

# ──────────────────────────────────────────────────────────────────────
# Tabs — Research / Live Agent / Reports
# ──────────────────────────────────────────────────────────────────────
tab_run, tab_live, tab_reports = st.tabs(["🚀  New Research", "🤖  Live Agent Feed", "📚  Reports"])

# ─────────── Tab 1 — Submit new query ───────────
with tab_run:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Start a new research job")

    query = st.text_area(
        "Research query",
        placeholder="e.g. Generate AI semiconductor market research for NVIDIA and AMD",
        height=110,
        key="query_input",
    )
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        depth = st.selectbox("Depth", ["quick", "standard", "deep"], index=1)
    with c2:
        st.markdown(" ")
        launch = st.button("🚀 Launch Research", use_container_width=True)
    with c3:
        st.caption("**Pipeline:** Planner → Research → Analyst → Writer → Reviewer → PDF + Markdown")

    st.markdown("</div>", unsafe_allow_html=True)

    if launch:
        q = (query or "").strip()
        if len(q) < 10:
            st.warning("Query must be at least 10 characters.")
        else:
            with st.spinner("Submitting to backend…"):
                resp = start_job(q, depth)
            if resp:
                st.session_state.active_job_id = resp["job_id"]
                st.session_state.feed = [
                    feed_entry("🚀", f"Job <b>{resp['job_id'][:8]}</b> queued — depth: <b>{depth}</b>")
                ]
                st.session_state.last_status = "queued"
                st.session_state.last_progress = None
                st.success(f"Job started: {resp['job_id']}")
                st.info("Switch to the **Live Agent Feed** tab to watch the agents work.")

# ─────────── Tab 2 — Live agent feed ───────────
with tab_live:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    job_id = st.session_state.active_job_id

    cols = st.columns([3, 1])
    with cols[0]:
        st.subheader("🤖 Agent activity")
        if job_id:
            st.caption(f"Watching job · `{job_id}`")
        else:
            st.caption("No active job. Submit one from the **New Research** tab or pick one from the sidebar.")
    with cols[1]:
        auto_refresh = st.toggle("Auto-refresh", value=True)

    if job_id:
        job = fetch_job(job_id)
        if not job:
            st.error("Could not fetch job from API.")
        else:
            status = job.get("status", "unknown")
            progress = job.get("progress")

            # Append new feed entries on status/progress change
            if status != st.session_state.last_status:
                icon = STATUS_ICONS.get(status, "•")
                # Pretty agent name based on stage
                agent_label = {
                    "queued":     "Planner Agent",
                    "searching":  "Research Agent",
                    "analyzing":  "Analyst Agent",
                    "generating": "Writer Agent",
                    "processing": "Orchestrator",
                    "complete":   "Reviewer Agent",
                    "failed":     "System",
                }.get(status, status.title())
                st.session_state.feed.append(
                    feed_entry(icon, f"<b>{agent_label}</b> · status → <code>{status}</code>")
                )
                st.session_state.last_status = status

            if progress and progress != st.session_state.last_progress:
                st.session_state.feed.append(feed_entry("💭", progress))
                st.session_state.last_progress = progress

            # Header pill + meta
            meta1, meta2, meta3 = st.columns(3)
            with meta1:
                st.markdown("**Status**")
                st.markdown(status_pill(status), unsafe_allow_html=True)
            with meta2:
                st.markdown("**Sources**")
                st.markdown(f"`{job.get('sources_count') or 0}`")
            with meta3:
                st.markdown("**Duration**")
                dur = job.get("duration_seconds")
                st.markdown(f"`{dur:.1f}s`" if dur else "`—`")

            st.markdown("---")
            st.markdown("##### 📌 Query")
            st.markdown(f"> {job.get('query', '')}")

            # Agent pipeline visual
            st.markdown("##### 🧬 Pipeline progress")
            stage_order = ["queued", "searching", "analyzing", "generating", "complete"]
            current_idx = stage_order.index(status) if status in stage_order else (4 if status == "complete" else -1)
            cols = st.columns(len(AGENT_PIPELINE))
            for i, (stage, name, desc) in enumerate(AGENT_PIPELINE):
                with cols[i]:
                    if status == "failed":
                        emoji = "❌" if i == current_idx else "•"
                        color = "#fca5a5"
                    elif i < current_idx or status == "complete":
                        emoji, color = "✅", "#86efac"
                    elif i == current_idx:
                        emoji, color = STATUS_ICONS.get(stage, "•"), "#fde68a"
                    else:
                        emoji, color = "•", "#6b7280"
                    st.markdown(
                        f"<div style='text-align:center; color:{color};'>"
                        f"<div style='font-size:1.5rem;'>{emoji}</div>"
                        f"<div style='font-weight:600; font-size:0.85rem;'>{name}</div>"
                        f"<div style='font-size:0.72rem; opacity:0.7;'>{desc}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            # Live feed
            st.markdown("##### 🧠 Agent feed")
            feed_html = "".join(st.session_state.feed)
            if status not in ("complete", "failed"):
                feed_html += (
                    f'<div class="feed-item"><span class="feed-icon">⏳</span>'
                    f'<span class="feed-text"><i>working<span class="thinking"></span></i></span></div>'
                )
            st.markdown(feed_html or "<i style='color:#6b7280;'>Waiting for activity…</i>", unsafe_allow_html=True)

            if job.get("error"):
                st.error(f"Error: {job['error']}")

            # When done, offer downloads
            if status == "complete" and job.get("report_path"):
                st.markdown("---")
                st.success("Report ready 🎉")
                filename = Path(job["report_path"]).name
                d1, d2 = st.columns(2)
                with d1:
                    md_bytes = download_report_bytes(filename, as_pdf=False)
                    if md_bytes:
                        st.download_button(
                            "⬇️ Download Markdown",
                            md_bytes,
                            file_name=filename,
                            mime="text/markdown",
                            use_container_width=True,
                        )
                with d2:
                    pdf_bytes = download_report_bytes(filename, as_pdf=True)
                    if pdf_bytes:
                        pdf_name = Path(filename).with_suffix(".pdf").name
                        st.download_button(
                            "⬇️ Download PDF",
                            pdf_bytes,
                            file_name=pdf_name,
                            mime="application/pdf",
                            use_container_width=True,
                        )

                with st.expander("📖 Preview report"):
                    try:
                        st.markdown(md_bytes.decode("utf-8") if md_bytes else "_unavailable_")
                    except Exception:
                        st.caption("Could not render preview.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-refresh while job is in flight
    if job_id and auto_refresh:
        job = fetch_job(job_id)
        if job and job.get("status") not in ("complete", "failed"):
            time.sleep(2)
            st.rerun()

# ─────────── Tab 3 — Reports gallery ───────────
with tab_reports:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 Generated reports")
    st.caption("Download Markdown or PDF — your browser saves them anywhere you choose.")

    reports = fetch_reports()
    md_reports = [r for r in reports if r["filename"].endswith(".md")]

    if not md_reports:
        st.info("No reports yet. Run a research job to generate one.")
    else:
        for r in md_reports:
            fname = r["filename"]
            with st.container():
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    st.markdown(f"**📄 {fname}**")
                with c2:
                    md_bytes = download_report_bytes(fname, as_pdf=False)
                    if md_bytes:
                        st.download_button(
                            "MD",
                            md_bytes,
                            file_name=fname,
                            mime="text/markdown",
                            key=f"md_{fname}",
                            use_container_width=True,
                        )
                with c3:
                    if st.button("PDF", key=f"pdfbtn_{fname}", use_container_width=True):
                        with st.spinner("Rendering PDF…"):
                            pdf_bytes = download_report_bytes(fname, as_pdf=True)
                        if pdf_bytes:
                            st.session_state[f"pdfdata_{fname}"] = pdf_bytes
                    if st.session_state.get(f"pdfdata_{fname}"):
                        pdf_name = Path(fname).with_suffix(".pdf").name
                        st.download_button(
                            "⬇️ Save PDF",
                            st.session_state[f"pdfdata_{fname}"],
                            file_name=pdf_name,
                            mime="application/pdf",
                            key=f"pdfdl_{fname}",
                            use_container_width=True,
                        )

    st.markdown("</div>", unsafe_allow_html=True)
