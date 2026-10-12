# 🧠 ResearchMind — Multi-Agent Research Assistant

Type any topic. Four AI stages — search, read, write, critique — collaborate to produce a scored research report.

## ✨ Features

- Topic in, scored research report out — intro, findings, conclusion, sources
- Two tool-calling agents (ReAct) + two deterministic LLM chains in one pipeline
- LLM-as-judge critic scores every report /10 with strengths and improvements
- Streamlit UI with live stage tracking and report download
- CLI mode for quick terminal runs

## 🏗️ Architecture

```mermaid
flowchart LR
    A --> B["🔍 Search Agent<br/>Tavily: 5 results<br/>create_agent (ReAct)"]
    B --> C["🔗 URLs + Snippets"]
    C --> D["📖 Reader Agent<br/>picks the most relevant URL<br/>BeautifulSoup scrape, 3000 chars"]
    D --> E["📝 Article Content"]
    E --> F["✍️ Writer Chain<br/>LLM prompt chain<br/>structured report"]
    F --> G["📄 Draft Report"]
    G --> H["⚖️ Critic Chain<br/>LLM-as-judge<br/>score /10 + feedback"]
    H --> I["🏁 Final Report + Score"]

    S[("Shared State Dict")] -.-> B
    S -.-> D
    S -.-> F
    S -.-> H
```

A shared state dictionary carries data between stages — each stage reads what the previous one wrote. No LangGraph state machine needed at this scale.

## 📁 Project Structure

```
├── app.py               # Streamlit web UI — custom dark theme, live 4-stage tracker
│                        # with per-stage timing, metrics row, tabs
│                        # (Report / Critic feedback / Sources / Scraped content),
│                        # report download as .md
├── pipeline.py          # Core pipeline: runs the 4 stages in order
│                        # (CLI entry: python pipeline.py)
├── pipeline_terminal.py # Earlier standalone variant of the pipeline (no UI callbacks)
├── agents.py            # Two create_agent tool-calling agents + writer/critic chains
├── tools.py             # web_search (Tavily, 5 results) and scrape_url (BeautifulSoup)
├── config.toml          # Streamlit theme — move into a .streamlit/ folder to take effect
└── requirements.txt
```

## 🚀 Quickstart

```bash
pip install -r requirements.txt
```

Create a `.env` file (never commit this):

```
OPENAI_API_KEY=your-key-here
TAVILY_API_KEY=your-key-here
```

**Web UI:**

```bash
streamlit run app.py
```

**Terminal:**

```bash
python pipeline.py
```

## 🧠 Design Decisions

| Choice | Why |
|---|---|
| **Agents for search & read, chains for write & critique** | Agents decide and act — the search path is unknown upfront (which URLs are worth reading?). Writing and critiquing follow a fixed prompt, so deterministic chains are cheaper and more predictable. |
| **`create_agent` (ReAct under the hood)** | Thought → Action → Observation loop: the LLM decides when to call a tool, sees the result, and decides the next step on its own. |
| **Shared state dict** | A plain dictionary is enough to pass data through a linear 4-stage pipeline — no framework overhead. |
| **LLM-as-judge critic** | A second model scoring the first model's output closes the loop: every report ships with a /10 score, strengths, and concrete improvements. |
| **temperature = 0** | Research reports must be factual and consistent — zero temperature removes creative drift. |
| **Character limits on scraped content** | Full articles are huge; scraped text is capped at 3000 chars, search snippets at 300 chars, and the reader only sees the first 800 chars of search results — this controls token cost per run. |
| **Tavily for search** | Built for LLMs — returns clean, relevant snippets instead of raw search-engine HTML. |

## 🛠️ Tech Stack

Python · LangChain (`create_agent`) · OpenAI (GPT-4o-mini) · Tavily · BeautifulSoup4 · Streamlit · Python-dotenv

## 🔜 Roadmap

- Reader scrapes the top **3 URLs** instead of 1, for richer reports
- User approval step before the agent calls tools
