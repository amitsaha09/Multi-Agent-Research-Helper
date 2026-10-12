"""
Multi-Agent Research Desk — Streamlit front end for pipeline.py

Run:  streamlit run app.py
"""

import re
import time

import streamlit as st

from pipeline import run_resarch_pipeline

st.set_page_config(
    page_title="Multi-Agent Research Desk",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Design tokens
#   ink #0E1220 · panel #171C30 · line #2A3150 · text #E8EAF4 · muted #8F97B8
#   agents: search cyan · read violet · write rose · critic amber
# --------------------------------------------------------------------------

STAGES = [
    {"name": "Search agent", "desc": "Finds recent sources on the web", "color": "#3CD7E6"},
    {"name": "Reader agent", "desc": "Scrapes the strongest page in depth", "color": "#8B7CFF"},
    {"name": "Writer chain", "desc": "Drafts the report from both inputs", "color": "#FF6B9A"},
    {"name": "Critic chain", "desc": "Reviews the draft and flags gaps", "color": "#FFB547"},
]

EXAMPLES = [
    "Solid-state batteries in 2026",
    "How retrieval-augmented generation is evolving",
    "State of open-source LLMs",
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

:root {
  --ink: #0E1220; --panel: #171C30; --line: #2A3150;
  --text: #E8EAF4; --muted: #8F97B8;
  --cyan: #3CD7E6; --violet: #8B7CFF; --rose: #FF6B9A; --amber: #FFB547;
}

html, body, .stApp { background: var(--ink); color: var(--text); font-family: 'Inter', sans-serif; }
header[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; height: 0; }
.block-container { max-width: 1080px; padding: 2.5rem 1.25rem 4rem; }

/* ---------- hero ---------- */
.hero h1 {
  font-family: 'Sora', sans-serif; font-weight: 800; letter-spacing: -0.03em;
  font-size: clamp(2.1rem, 5.5vw, 3.7rem); line-height: 1.05; margin: 0 0 .9rem; color: var(--text);
}
.hero p { color: var(--muted); font-size: clamp(1rem, 2vw, 1.15rem); max-width: 40rem; line-height: 1.6; margin: 0 0 1.6rem; }

/* ---------- inputs ---------- */
div[data-baseweb="input"] { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 12px !important; }
div[data-baseweb="input"]:focus-within { border-color: var(--violet) !important; box-shadow: 0 0 0 3px rgba(139,124,255,.25); }
div[data-baseweb="input"] input { font-size: 1.05rem; padding: .8rem .9rem; color: var(--text); }

.stButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: var(--panel); color: var(--text);
  font-weight: 500; transition: border-color .15s, background .15s;
}
.stButton > button:hover { border-color: var(--violet); color: var(--text); }
.stButton > button:focus-visible { outline: 2px solid var(--violet); outline-offset: 2px; }
.stButton > button[kind="primary"] {
  background: var(--violet); border-color: var(--violet); color: #0E1220;
  font-family: 'Sora', sans-serif; font-weight: 700; padding: .72rem 1rem; width: 100%;
}
.stButton > button[kind="primary"]:hover { background: #A094FF; border-color: #A094FF; }

/* ---------- pipeline tracker (the one memorable element) ---------- */
.tracker { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.8rem 0 1.2rem; }
.stage {
  --c: #fff; background: var(--panel); border: 1px solid var(--line); border-top: 3px solid var(--line);
  border-radius: 12px; padding: 1rem 1rem 1.1rem; min-height: 150px;
  display: flex; flex-direction: column; gap: .35rem; transition: border-color .3s, opacity .3s;
}
.stage[data-state="waiting"] { opacity: .55; }
.stage[data-state="working"] { border-top-color: var(--c); border-color: var(--c); animation: glow 1.6s ease-in-out infinite; }
.stage[data-state="done"] { border-top-color: var(--c); }
.stage[data-state="error"] { border-top-color: #FF5A5A; border-color: #FF5A5A; }
.badge {
  width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center;
  font-family: 'Sora', sans-serif; font-weight: 700; font-size: .85rem;
  border: 1.5px solid var(--c); color: var(--c); margin-bottom: .35rem;
}
.stage[data-state="done"] .badge { background: var(--c); color: var(--ink); }
.s-name { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 1.02rem; }
.s-desc { color: var(--muted); font-size: .86rem; line-height: 1.45; flex: 1; }
.s-state { font-size: .82rem; font-weight: 600; color: var(--muted); }
.stage[data-state="working"] .s-state { color: var(--c); }
.stage[data-state="done"] .s-state { color: var(--text); }
.stage[data-state="error"] .s-state { color: #FF5A5A; }
@keyframes glow { 0%,100% { box-shadow: 0 0 0 0 transparent; } 50% { box-shadow: 0 0 22px -4px var(--c); } }

/* ---------- metrics ---------- */
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 0 0 1.4rem; }
.metric { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: .9rem 1rem; }
.metric b { display: block; font-family: 'Sora', sans-serif; font-size: 1.55rem; font-weight: 700; }
.metric span { color: var(--muted); font-size: .85rem; }

/* ---------- reading surfaces ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-family: 'Sora', sans-serif; font-weight: 500; color: var(--muted); padding: .6rem 1rem; }
.stTabs [aria-selected="true"] { color: var(--text); }
.st-key-report, .st-key-critic, .st-key-raw {
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 1.4rem 1.6rem; margin-top: 1rem;
}
.st-key-report p, .st-key-report li { font-family: 'Source Serif 4', serif; font-size: 1.08rem; line-height: 1.75; max-width: 70ch; }
.st-key-report h1, .st-key-report h2, .st-key-report h3 { font-family: 'Sora', sans-serif; letter-spacing: -0.01em; }
.st-key-critic { border-left: 4px solid var(--amber); }
.src { display: block; padding: .55rem 0; border-bottom: 1px solid var(--line); color: var(--cyan); word-break: break-all; text-decoration: none; }
.src:hover { text-decoration: underline; }

.foot { margin-top: 3rem; color: var(--muted); font-size: .85rem; border-top: 1px solid var(--line); padding-top: 1rem; }
.foot a { color: var(--violet); }

/* ---------- responsive ---------- */
@media (max-width: 820px) {
  .tracker { grid-template-columns: repeat(2, 1fr); }
  .metrics { grid-template-columns: repeat(2, 1fr); }
  .st-key-report, .st-key-critic, .st-key-raw { padding: 1rem; }
}
@media (prefers-reduced-motion: reduce) { .stage { animation: none !important; transition: none; } }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def to_text(value) -> str:
    """Agent outputs can be a str or a list of content blocks; always return str."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for block in value:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return "\n".join(p for p in parts if p)
    return str(value)


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s\)\]>\"'*]+", text)
    seen, unique = set(), []
    for u in urls:
        u = u.rstrip(".,;")
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def extract_score(feedback: str) -> str:
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", feedback)
    return f"{match.group(1)}/10" if match else "n/a"


def tracker_html(states: list[str], labels: list[str]) -> str:
    cards = []
    for i, stage in enumerate(STAGES):
        badge = "✓" if states[i] == "done" else str(i + 1)
        cards.append(
            f'<div class="stage" data-state="{states[i]}" style="--c:{stage["color"]}">'
            f'<div class="badge">{badge}</div>'
            f'<div class="s-name">{stage["name"]}</div>'
            f'<div class="s-desc">{stage["desc"]}</div>'
            f'<div class="s-state">{labels[i]}</div></div>'
        )
    return f'<div class="tracker">{"".join(cards)}</div>'


def idle_labels() -> list[str]:
    return ["Waiting"] * 4


def set_topic(value: str) -> None:
    st.session_state.topic = value


# --------------------------------------------------------------------------
# sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### How it works")
    st.markdown(
        "1. **Search agent** queries the web for recent sources.\n"
        "2. **Reader agent** picks the best URL and scrapes it.\n"
        "3. **Writer chain** combines both into a structured report.\n"
        "4. **Critic chain** reviews the report and lists improvements.\n"
    )
    st.caption("Built with 2 LangChain agents, 2 LLM chains, Streamlit and Python.")

# --------------------------------------------------------------------------
# hero + input
# --------------------------------------------------------------------------

st.markdown(
    '<div class="hero"><h1>Two agents research your topic. Two chains write and review it.</h1>'
    "<p>Enter a topic. A search agent finds sources, a reader agent scrapes the best one, then a writer chain "
    "drafts the report and a critic chain reviews it. You watch each step happen live.</p></div>",
    unsafe_allow_html=True,
)

if "topic" not in st.session_state:
    st.session_state.topic = ""

in_col, btn_col = st.columns([4, 1], vertical_alignment="bottom")
with in_col:
    st.text_input(
        "Research topic",
        key="topic",
        placeholder="e.g. Solid-state batteries in 2026",
        label_visibility="collapsed",
    )
with btn_col:
    run_clicked = st.button("Run research", type="primary")

chip_cols = st.columns(len(EXAMPLES))
for col, example in zip(chip_cols, EXAMPLES):
    col.button(example, key=f"ex_{example}", on_click=set_topic, args=(example,), use_container_width=True)

tracker_slot = st.empty()

# --------------------------------------------------------------------------
# run the pipeline
# --------------------------------------------------------------------------

if run_clicked:
    topic = st.session_state.topic.strip()
    if not topic:
        st.warning("Enter a topic first, or pick one of the examples above.")
    else:
        states = ["waiting"] * 4
        labels = idle_labels()
        started = {}
        durations = {}
        current = {"i": 0}

        def on_step(index: int, status: str) -> None:
            """Called by pipeline.py before (working) and after (done) every stage."""
            current["i"] = index
            states[index] = status
            if status == "working":
                started[index] = time.time()
                labels[index] = "Working…"
            else:
                durations[index] = time.time() - started.get(index, time.time())
                labels[index] = f"Done in {durations[index]:.0f}s"
            tracker_slot.markdown(tracker_html(states, labels), unsafe_allow_html=True)

        tracker_slot.markdown(tracker_html(states, labels), unsafe_allow_html=True)
        t0 = time.time()
        try:
            result = run_resarch_pipeline(topic, on_step=on_step)
            st.session_state.result = {
                "topic": topic,
                "state": {k: to_text(v) for k, v in result.items()},
                "durations": durations,
                "elapsed": time.time() - t0,
            }
        except Exception as exc:  # surface the real cause instead of a blank page
            states[current["i"]] = "error"
            labels[current["i"]] = "Failed"
            tracker_slot.markdown(tracker_html(states, labels), unsafe_allow_html=True)
            st.error(
                f"The {STAGES[current['i']]['name'].lower()} stopped with an error: {exc}\n\n"
                "Check your API keys in .env and your network connection, then run it again."
            )
            st.session_state.pop("result", None)

# --------------------------------------------------------------------------
# results (kept in session_state so downloads and tab clicks don't wipe them)
# --------------------------------------------------------------------------

res = st.session_state.get("result")

if res:
    s = res["state"]
    tracker_slot.markdown(
        tracker_html(
            ["done"] * 4,
            [f"Done in {res['durations'].get(i, 0):.0f}s" for i in range(4)],
        ),
        unsafe_allow_html=True,
    )

    urls = extract_urls(s.get("search_results", ""))
    words = len(s.get("report", "").split())
    st.markdown(
        '<div class="metrics">'
        f'<div class="metric"><b>{res["elapsed"]:.0f}s</b><span>Total time</span></div>'
        f'<div class="metric"><b>{len(urls)}</b><span>Sources found</span></div>'
        f'<div class="metric"><b>{words:,}</b><span>Words in report</span></div>'
        f'<div class="metric"><b>{extract_score(s.get("feedback", ""))}</b><span>Critic score</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    tab_report, tab_critic, tab_sources, tab_raw = st.tabs(
        ["Report", "Critic feedback", "Sources", "Scraped content"]
    )

    with tab_report:
        with st.container(key="report"):
            st.markdown(s.get("report", ""))
        st.download_button(
            "Download report (.md)",
            data=s.get("report", ""),
            file_name=re.sub(r"\W+", "_", res["topic"]).strip("_").lower() + "_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        with st.container(key="critic"):
            st.markdown(s.get("feedback", ""))

    with tab_sources:
        if urls:
            links = "".join(f'<a class="src" href="{u}" target="_blank" rel="noopener">{u}</a>' for u in urls)
            st.markdown(links, unsafe_allow_html=True)
        else:
            st.info("No links were found in the search output.")
        with st.expander("Raw search output"):
            st.text(s.get("search_results", ""))

    with tab_raw:
        with st.container(key="raw"):
            st.markdown(s.get("scraped_content", ""))

elif not run_clicked:
    tracker_slot.markdown(tracker_html(["waiting"] * 4, idle_labels()), unsafe_allow_html=True)


st.markdown(
    '<div class="foot">Built by Amit Saha · '
    '<a href="https://www.linkedin.com/in/amitsaha09/" target="_blank">LinkedIn</a> · '
    '<a href="https://github.com/amitsaha09/Multi-Agent-Research-Helper" target="_blank">Source code</a></div>',
    unsafe_allow_html=True,
)
