import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from utils.logger import setup_logging
from services.pipeline import process_email

setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="SupportIQ — AI Email Agent",
    page_icon="✦",
    layout="centered",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0b0c0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
.block-container { padding: 2.5rem 1.5rem 4rem !important; max-width: 780px !important; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.8rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #c9a84c;
    border: 1px solid rgba(201,168,76,0.35);
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    margin-bottom: 1.4rem;
    background: rgba(201,168,76,0.06);
}
.hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2rem, 6vw, 3.2rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #f0ece3 !important;
    line-height: 1.08 !important;
    margin-bottom: 0.9rem !important;
}
.hero h1 span { color: #c9a84c; }
.hero p {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.97rem;
    color: #8a8680;
    font-weight: 300;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.65;
}
.divider {
    width: 40px; height: 1px;
    background: linear-gradient(90deg, transparent, #c9a84c55, transparent);
    margin: 2rem auto;
}

/* ── Input card ── */
.input-card {
    background: #13141a;
    border: 1px solid #1f2028;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
}
.input-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5a5850;
    margin-bottom: 0.8rem;
}

/* ── Streamlit textarea override ── */
.stTextArea textarea {
    background: #0e0f14 !important;
    border: 1px solid #252830 !important;
    border-radius: 10px !important;
    color: #d4cfc5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    resize: vertical !important;
    padding: 1rem 1.1rem !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(201,168,76,0.5) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.07) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #3a3830 !important; }
.stTextArea label { display: none !important; }

/* ── Button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #c9a84c 0%, #a8862e 100%) !important;
    color: #0b0c0f !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.8rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(201,168,76,0.22) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(201,168,76,0.35) !important;
    background: linear-gradient(135deg, #d4b55a 0%, #b8922e 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Results section ── */
.results-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a4840;
    margin: 2rem 0 1.2rem;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: #13141a;
    border: 1px solid #1f2028;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.4s ease both;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 12px 12px;
}
.metric-card.intent::after  { background: #4a9eff; }
.metric-card.urgency-high::after   { background: #ff5a5a; }
.metric-card.urgency-medium::after { background: #ffaa33; }
.metric-card.urgency-low::after    { background: #4ade80; }
.metric-card.confidence::after { background: #c9a84c; }

.metric-label {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4a4840;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #f0ece3;
    line-height: 1;
}
.metric-card.intent .metric-value  { color: #6ab4ff; }
.metric-card.urgency-high .metric-value   { color: #ff7070; }
.metric-card.urgency-medium .metric-value { color: #ffbb55; }
.metric-card.urgency-low .metric-value    { color: #4ade80; }
.metric-card.confidence .metric-value { color: #c9a84c; }

/* ── Status banner ── */
.status-banner {
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    font-size: 0.88rem;
    font-weight: 400;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.8rem;
    animation: fadeUp 0.5s ease 0.1s both;
}
.status-banner.human {
    background: rgba(255,90,90,0.08);
    border: 1px solid rgba(255,90,90,0.25);
    color: #ff9090;
}
.status-banner.auto {
    background: rgba(74,222,128,0.07);
    border: 1px solid rgba(74,222,128,0.2);
    color: #6edd9a;
}
.status-icon { font-size: 1rem; flex-shrink: 0; }

/* ── Reasoning box ── */
.reasoning-box {
    background: #0f1015;
    border: 1px solid #1c1e25;
    border-left: 3px solid #c9a84c44;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    animation: fadeUp 0.5s ease 0.15s both;
}
.reasoning-label {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #c9a84c88;
    margin-bottom: 0.4rem;
}
.reasoning-text {
    font-size: 0.9rem;
    color: #7a7670;
    font-weight: 300;
    line-height: 1.6;
    font-style: italic;
}

/* ── Reply cards ── */
.reply-section {
    margin-top: 0.4rem;
    animation: fadeUp 0.5s ease 0.2s both;
}
.reply-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
.reply-card {
    background: #13141a;
    border: 1px solid #1f2028;
    border-radius: 12px;
    overflow: hidden;
}
.reply-card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.9rem 1.2rem;
    border-bottom: 1px solid #1a1c22;
}
.reply-card-lang {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4a4840;
}
.reply-card-flag { font-size: 1rem; }
.reply-card-body {
    padding: 1.2rem;
    font-size: 0.92rem;
    color: #b0ac9f;
    line-height: 1.75;
    font-weight: 300;
    white-space: pre-wrap;
}
.reply-card-body.arabic {
    direction: rtl;
    font-size: 1rem;
    line-height: 1.85;
    text-align: right;
}

/* ── Error card ── */
.error-card {
    background: rgba(255,90,90,0.06);
    border: 1px solid rgba(255,90,90,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
}
.error-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: #ff7070;
    margin-bottom: 0.4rem;
}
.error-body { font-size: 0.82rem; color: #6a4444; line-height: 1.5; }

/* ── Warning card ── */
.warn-card {
    background: rgba(255,170,51,0.06);
    border: 1px solid rgba(255,170,51,0.2);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    font-size: 0.88rem;
    color: #cc9944;
}

/* ── Spinner override ── */
[data-testid="stSpinner"] { color: #c9a84c !important; }

/* ── Footer ── */
.footer {
    text-align: center;
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid #14151a;
    font-size: 0.72rem;
    color: #2e2c28;
    letter-spacing: 0.06em;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ Powered by Groq + Llama 3.3</div>
    <h1>Customer <span>Support</span><br>Email Agent</h1>
    <p>Paste any customer email in English or Arabic — get instant intent classification and bilingual suggested replies.</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Input card ────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card"><div class="input-label">✉ Customer Email</div>', unsafe_allow_html=True)
email_input = st.text_area(
    "Customer Email",
    placeholder="Paste customer email here — English or Arabic...",
    height=180,
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

analyze = st.button("Analyze Email →")

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze:
    if not email_input.strip():
        st.markdown('<div class="warn-card">⚠ Please enter a customer email before analyzing.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Analyzing…"):
            try:
                result = process_email(email_input)
                logger.info("UI: email processed successfully")

                # Urgency CSS class
                urgency_class = f"urgency-{result.urgency}"

                # ── Metrics ──
                st.markdown('<div class="results-header">── Classification Results</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-card intent">
                        <div class="metric-label">Intent</div>
                        <div class="metric-value">{result.intent.capitalize()}</div>
                    </div>
                    <div class="metric-card {urgency_class}">
                        <div class="metric-label">Urgency</div>
                        <div class="metric-value">{result.urgency.capitalize()}</div>
                    </div>
                    <div class="metric-card confidence">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value">{result.confidence:.0%}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Status banner ──
                if result.needs_human:
                    st.markdown("""
                    <div class="status-banner human">
                        <span class="status-icon">⚑</span>
                        <span><strong>Needs Human Review</strong> — Confidence too low or request is complex. Route to a human agent.</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="status-banner auto">
                        <span class="status-icon">✓</span>
                        <span><strong>Auto-handled</strong> — Sufficient confidence to respond automatically.</span>
                    </div>""", unsafe_allow_html=True)

                # ── Reasoning ──
                st.markdown(f"""
                <div class="reasoning-box">
                    <div class="reasoning-label">Model Reasoning</div>
                    <div class="reasoning-text">{result.reasoning}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Replies ──
                st.markdown('<div class="results-header">── Suggested Replies</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="reply-section">
                    <div class="reply-card" style="margin-bottom:0.8rem">
                        <div class="reply-card-header">
                            <span class="reply-card-flag">🇬🇧</span>
                            <span class="reply-card-lang">English Reply</span>
                        </div>
                        <div class="reply-card-body">{result.suggested_reply_en}</div>
                    </div>
                    <div class="reply-card">
                        <div class="reply-card-header">
                            <span class="reply-card-flag">🇸🇦</span>
                            <span class="reply-card-lang">Arabic Reply</span>
                        </div>
                        <div class="reply-card-body arabic">{result.suggested_reply_ar}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                logger.error("UI: pipeline error: %s", e)
                st.markdown(f"""
                <div class="error-card">
                    <div class="error-title">⚠ Analysis Failed</div>
                    <div class="error-body">
                        Check that your <code>GROQ_API_KEY</code> is set correctly in <code>.env</code> and try again.<br><br>
                        <strong>Error:</strong> {e}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    AI Customer Support Agent &nbsp;·&nbsp; Built with Groq + Streamlit &nbsp;·&nbsp; EN / AR
</div>
""", unsafe_allow_html=True)
