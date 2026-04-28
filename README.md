# AI Customer Support Email Agent

An intelligent email triage system for e-commerce customer support. Analyzes incoming customer emails in **English and Arabic**, classifies intent and urgency, generates bilingual suggested replies, and flags complex cases for human review.

---

## Problem

Customer support teams handling high email volume face two bottlenecks:
1. **Triage delay** — agents must read every email before routing it
2. **Bilingual overhead** — English-speaking agents cannot respond in Arabic without translation tools

This agent automates both: it reads the email, classifies the request type, judges urgency, drafts replies in both languages, and flags anything it's not confident about for a human agent.

---

## Architecture

```
customer-support-ai-agent/
├── app/
│   ├── config.py            # Settings via environment variables (lru_cache singleton)
│   └── main.py              # Streamlit UI
├── models/
│   ├── llm_handler.py       # Groq API wrapper (lazy init, JSON mode enabled)
│   ├── prompts.py           # System prompt + user prompt builder with language hints
│   └── language.py          # Language detection (langdetect)
├── services/
│   ├── pipeline.py          # Core orchestration: detect → prompt → call → parse → validate
│   ├── classifier.py        # Classification field extractor
│   └── reply_generator.py   # Reply field extractor
├── schemas/
│   └── response_schema.py   # Pydantic v2 output schema with field validators
├── evals/
│   ├── evaluator.py         # Evaluation runner with scoring + results.md writer
│   ├── test_cases.json      # 15 labeled test cases (normal, edge, adversarial)
│   └── results.md           # Auto-generated evaluation results
├── utils/
│   ├── logger.py            # Centralized logging setup
│   └── helpers.py           # Display utilities (confidence labels, color coding)
├── data/
│   └── sample_emails.json   # 8 sample emails for manual testing
├── .env.example             # Environment variable template
├── Makefile                 # Shortcuts: make run, make eval, make install
└── requirements.txt         # Pinned dependencies
```

**Pipeline Flow:**

```
Email Input
    ↓
Language Detection (langdetect)
    ↓
Prompt Builder (adds language hint)
    ↓
Groq LLM — Mixtral-8x7B (JSON mode enforced at API level)
    ↓
JSON Parser (with bracket-extraction fallback)
    ↓
Pydantic v2 Validation
    ↓
Confidence Check → needs_human override if below threshold
    ↓ (on failure: retry once with logged error)
SupportResponse object → Streamlit UI
```

---

## Setup

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### Install

```bash
git clone https://github.com/yourname/customer-support-ai-agent
cd customer-support-ai-agent
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
```

### Run the app

```bash
make run
# or: streamlit run app/main.py
```

### Run evaluations

```bash
make eval
# or: python -m evals.evaluator
```

Results will be printed to the terminal and saved to `evals/results.md`.

---

## Evaluation Results

Evaluated on 15 test cases covering:
- **Normal** (English + Arabic standard requests)
- **Edge** (minimal input, gibberish, mixed-language)
- **Adversarial** (escalation threats, repeated contact, prompt injection)

### Metrics

- Pipeline Success Rate: 93.3%
- Intent Accuracy: 100%
- Urgency Accuracy: 85.7%
- Exact Match Accuracy: 85.7%
- Average Confidence: 0.83
- Human Escalation Rate: 28.6%

The system demonstrates strong performance in intent classification and robust handling of uncertain and adversarial inputs. One failure occurred under a prompt injection scenario, where the model returned invalid structured output, which was safely caught by validation and retry logic.

### Observed Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| complaint/inquiry confusion | Vague emails with no clear ask | Lower confidence → needs_human flag |
| Arabic urgency underestimated | Implicit frustration without punctuation | Few-shot example in system prompt |
| Prompt injection | Adversarial user inputs | Model ignores injection; classified as inquiry |

---

## Tradeoffs

| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|
| LLM Provider | Groq (Mixtral) | OpenAI GPT-4 | Fast inference, free tier for prototyping |
| JSON enforcement | API-level `response_format` | Regex extraction only | Eliminates most parse failures at source |
| Output validation | Pydantic v2 | Manual dict checks | Type safety + clear validation errors |
| UI | Streamlit | FastAPI + React | Speed of development for demo |
| Language detection | langdetect library | Prompt-based detection | Avoids extra LLM call; faster |
| Retry strategy | 2 attempts with logged errors | Exponential backoff | Sufficient for prototype; backoff for production |

**Known limitations:**
- No conversation history — each email processed cold, no prior context
- Arabic quality depends on base model; Mixtral is adequate but not native-level
- `needs_human` threshold is configurable but not yet learned from feedback

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| [Groq](https://groq.com) | — | LLM inference (Llama 3.3 70B) |
| [Pydantic](https://docs.pydantic.dev) | 2.7.1 | Output schema validation |
| [Streamlit](https://streamlit.io) | 1.35.0 | Demo UI |
| [langdetect](https://github.com/Mimino666/langdetect) | 1.0.9 | Input language detection |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 1.0.1 | Environment variable management |

---

## Output Schema

```json
{
  "intent": "refund | exchange | complaint | inquiry",
  "urgency": "high | medium | low",
  "confidence": 0.0,
  "reasoning": "1-2 sentence explanation of classification",
  "suggested_reply_en": "Professional English reply",
  "suggested_reply_ar": "Natural Arabic reply (not a translation)",
  "needs_human": true
}
```
