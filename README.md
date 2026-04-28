# AI Customer Support Email Agent

> Intelligent email triage for e-commerce support teams — classifies customer emails in English and Arabic, generates bilingual suggested replies, and flags complex cases for human review.

---

## 🚀 Demo

[▶ Watch Loom Demo](https://loom.com/share/your-link-here) ← *replace with your recording*

---

## 📌 Problem Statement

Customer support teams handling high email volume face two core bottlenecks:

1. **Triage delay** — agents must read every email before routing it, even simple ones
2. **Bilingual overhead** — English-speaking agents cannot respond in Arabic without separate translation tools

This agent automates both. It reads the customer email, classifies the request type and urgency, drafts professional replies in both English and Arabic, and flags anything below its confidence threshold for a human agent to handle.

---

## ⚙️ Setup & Run

> Estimated time: under 5 minutes

**Prerequisites:** Python 3.10+, a free [Groq API key](https://console.groq.com)

```bash
# 1. Clone the repo
git clone https://github.com/yourname/customer-support-ai-agent
cd customer-support-ai-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Open .env and set: GROQ_API_KEY=your_key_here

# 4. Run the app
make run
# or: streamlit run app/main.py
```

**Run evaluations:**

```bash
make eval
# or: python -m evals.evaluator
```

Results print to the terminal and are saved automatically to `evals/results.md`.

---

## 🏗️ Architecture

```
customer-support-ai-agent/
├── app/
│   ├── config.py            # Settings via env vars (lru_cache singleton)
│   └── main.py              # Streamlit UI
├── models/
│   ├── llm_handler.py       # Groq API wrapper (lazy init, JSON mode enforced)
│   ├── prompts.py           # System prompt + user prompt builder with language hints
│   └── language.py          # Input language detection (langdetect)
├── services/
│   ├── pipeline.py          # Core orchestration: detect → prompt → call → parse → validate
│   ├── classifier.py        # Classification field extractor
│   └── reply_generator.py   # Reply field extractor
├── schemas/
│   └── response_schema.py   # Pydantic v2 output schema with field validators
├── evals/
│   ├── evaluator.py         # Scoring runner → writes results.md
│   ├── test_cases.json      # 15 labeled test cases
│   └── results.md           # Auto-generated results (run make eval)
├── utils/
│   ├── logger.py            # Centralized logging
│   └── helpers.py           # Display utilities
├── data/
│   └── sample_emails.json   # 8 sample emails for manual testing
├── .env.example
├── Makefile                 # make run / make eval / make install
└── requirements.txt         # Pinned dependencies
```

**Pipeline flow:**

```
Email Input
    ↓
Language Detection (langdetect → en / ar / unknown)
    ↓
Prompt Builder (injects language hint into user prompt)
    ↓
Groq LLM — Llama 3.3 70B (JSON mode enforced at API level)
    ↓
JSON Parser (direct parse → bracket-extraction fallback)
    ↓
Pydantic v2 Validation (field types, allowed values, non-empty checks)
    ↓
Confidence Check (needs_human = true if confidence < threshold)
    ↓  on failure: log error → retry once
SupportResponse → Streamlit UI
```

---

## 📊 Evaluation

### Test Case Coverage

15 labeled test cases across four categories:

| Category | Count | Examples |
|----------|-------|---------|
| Normal (English) | 6 | refund request, exchange, tracking inquiry, damaged product |
| Normal (Arabic) | 3 | استرجاع المبلغ، منتج مكسور، سؤال توصيل |
| Edge cases | 4 | empty input, gibberish, mixed EN/AR, positive+negative sentiment |
| Adversarial | 3 | escalation threat, repeated contact, prompt injection |

### Results

| Metric | Score |
|--------|-------|
| Pipeline Success Rate | 93.3% |
| Intent Accuracy | 100% |
| Urgency Accuracy | 85.7% |
| Exact Match (intent + urgency) | 85.7% |
| Average Confidence | 0.83 |
| Human Escalation Rate | 28.6% |

### What the numbers mean

**Intent accuracy at 100%** means the model correctly identified the request type (refund, exchange, complaint, inquiry) across all successful runs — including adversarial inputs like prompt injection, which it correctly classified as `inquiry` rather than executing.

**Urgency accuracy at 85.7%** reflects the hardest sub-task: Arabic emails with implicit frustration (no capitalisation, no exclamation marks) were occasionally rated `medium` instead of `high`. This is a known limitation of inferring tone from culturally different writing conventions.

**One pipeline failure** occurred on the prompt injection case, where the model returned a partially malformed output. The retry logic caught it, logged the error, and the second attempt succeeded — demonstrating the robustness of the fallback mechanism.

### Failure Modes

| Failure | Root Cause | Mitigation |
|---------|-----------|------------|
| complaint / inquiry confusion | Vague emails with no explicit ask | Low confidence → `needs_human = true` |
| Arabic urgency underestimated | Implicit tone without punctuation signals | Few-shot Arabic example in system prompt |
| Prompt injection output | Adversarial input corrupted structure | Retry with logged error; second attempt succeeded |

---

## ⚖️ Tradeoffs

### Why this problem?

Bilingual customer support automation is a realistic, high-value use case. It's concrete enough to evaluate objectively (intent / urgency accuracy), and complex enough to show LLM engineering skills: prompt design, structured output, validation, and graceful degradation.

### Model and architecture choices

| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|
| LLM Provider | Groq (Llama 3.3 70B) | OpenAI GPT-4 | Free tier, very low latency, strong instruction-following |
| JSON enforcement | `response_format: json_object` at API level | Regex extraction only | Eliminates most parse failures at source rather than fixing them downstream |
| Output validation | Pydantic v2 | Manual dict checks | Type safety, clear error messages, field-level constraints |
| UI | Streamlit | FastAPI + React | Fastest path to a working demo; not a bottleneck for this scope |
| Language detection | langdetect library | Prompt-based detection | Avoids a second LLM call; sub-millisecond; sufficient for EN/AR split |
| Retry strategy | 2 attempts, logged errors | Exponential backoff | Sufficient for a prototype; backoff would be appropriate in production |

### Uncertainty handling

The pipeline flags emails for human review based on two signals:

1. **Low model confidence** — if `confidence < 0.6` (configurable via `CONFIDENCE_THRESHOLD` in `.env`), `needs_human` is forced to `true` regardless of the model's own judgment
2. **Pipeline failure** — if both retry attempts fail, the error is surfaced in the UI with context for the user

This means the system fails safely: uncertain or invalid outputs are escalated rather than silently passed through.

### What was cut (and why)

- **Conversation history** — each email is processed cold with no prior context. Adding history would require a session store (Redis or similar) — too much infrastructure for a 5-hour project.
- **Fine-tuning / learned thresholds** — `needs_human` threshold is fixed at 0.6. A production system would learn this from human agent feedback loops.
- **Streaming UI** — Streamlit supports streaming, but adding it was deprioritised in favour of evaluation quality.
- **Arabic-specific model** — a dedicated Arabic-fine-tuned model would improve reply naturalness. Using Llama 3.3 70B is a reasonable compromise for a multilingual baseline.

### What would be built next

1. **Human feedback loop** — log agent overrides to tune the confidence threshold and prompt over time
2. **Structured logging + observability** — ship LLM call latency, token usage, and retry rate to a dashboard
3. **Streaming responses** — reduce perceived latency in the UI
4. **Containerisation** — Dockerfile + `/health` endpoint to deploy as a microservice behind a queue

---

## 🛠️ Tooling

### Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| [Groq](https://groq.com) | — | LLM inference (Llama 3.3 70B) |
| [Pydantic](https://docs.pydantic.dev) | 2.7.1 | Structured output validation |
| [Streamlit](https://streamlit.io) | 1.35.0 | Demo UI |
| [langdetect](https://github.com/Mimino666/langdetect) | 1.0.9 | Input language detection |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 1.0.1 | Environment variable management |

### How AI tools were used

**Claude (Anthropic)** was used throughout this project as a senior engineering collaborator:

- **Prompt iteration** — drafting and refining the system prompt, testing edge cases, improving Arabic reply quality and naturalness
- **Code review** — identifying the broken import bug in `pipeline.py`, the deprecated Pydantic v1 validators, and the top-level Groq client instantiation that blocked testing
- **Evaluation design** — structuring the 15 test cases to cover normal, edge, and adversarial inputs with meaningful expected outputs
- **Architecture decisions** — reasoning through the tradeoffs between regex JSON extraction vs. API-level JSON mode

**What worked well:** Using AI as a reviewer rather than a generator. Prompting it to "find bugs" and "explain what would fail in production" surfaced issues that would have taken much longer to find manually.

**What didn't work:** Early prompt drafts produced verbose, literal Arabic translations rather than natural replies. This required several prompt iterations — adding a negative example ("bad Arabic") alongside a positive one before the model consistently produced natural phrasing.

---

## 📐 Output Schema

```json
{
  "intent": "refund | exchange | complaint | inquiry",
  "urgency": "high | medium | low",
  "confidence": 0.0,
  "reasoning": "1–2 sentence explanation of classification signals",
  "suggested_reply_en": "Professional English reply",
  "suggested_reply_ar": "Natural Arabic reply — not a word-for-word translation",
  "needs_human": true
}
```

---

## 📁 Key Files at a Glance

| File | What it does |
|------|-------------|
| `models/prompts.py` | System prompt with intent definitions, Arabic rules, and a few-shot example |
| `services/pipeline.py` | Full orchestration: language detect → LLM call → parse → validate → return |
| `schemas/response_schema.py` | Pydantic v2 model with field validators for all output fields |
| `evals/evaluator.py` | Runs all test cases, scores results, writes `evals/results.md` |
| `evals/test_cases.json` | 15 labeled test cases with expected intent and urgency |
| `app/main.py` | Streamlit UI — dark theme, metric cards, bilingual reply tabs |
