"""
DEWA Smart Assistant — Streamlit app
Showcases: tool use, vision, prompt caching, multi-turn, streaming, extended thinking
"""

import streamlit as st
from assistant.client import has_api_key
from utils.image_utils import encode_image

if has_api_key():
    from assistant.agent import DEWAAgent as ActiveAgent
    DEMO_MODE = False
else:
    from assistant.mock_agent import MockDEWAAgent as ActiveAgent  # type: ignore
    DEMO_MODE = True

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DEWA Smart Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #00703c10; }
    .tool-badge {
        display: inline-block;
        background: #e8f4fd;
        border: 1px solid #90cdf4;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        margin: 2px;
        color: #2b6cb0;
    }
    .feature-pill {
        display: inline-block;
        background: #f0fff4;
        border: 1px solid #9ae6b4;
        border-radius: 10px;
        padding: 1px 8px;
        font-size: 0.75rem;
        color: #276749;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # [{role, content, tools_used?}]
if "agent" not in st.session_state:
    st.session_state.agent = ActiveAgent()
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None   # encoded image dict
if "stream_mode" not in st.session_state:
    st.session_state.stream_mode = True
if "deep_mode" not in st.session_state:
    st.session_state.deep_mode = False

agent = st.session_state.agent

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ DEWA Smart Assistant")
    if DEMO_MODE:
        st.warning("**Demo Mode** — no API key found.\nAdd `ANTHROPIC_API_KEY` to `.env` for real Claude responses.", icon="🔑")
    else:
        st.caption("Powered by Claude AI")
    st.divider()

    st.markdown("### Claude Features Active")
    st.markdown("""
    <span class="feature-pill">Tool Use</span>
    <span class="feature-pill">Vision</span>
    <span class="feature-pill">Prompt Caching</span>
    <span class="feature-pill">Multi-turn</span>
    <span class="feature-pill">Streaming</span>
    <span class="feature-pill">Extended Thinking</span>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("### Options")
    st.session_state.stream_mode = st.toggle("Stream responses", value=True)
    st.session_state.deep_mode   = st.toggle(
        "Deep analysis (extended thinking)", value=False,
        help="Enables Claude's extended thinking for thorough bill analysis. Slower but more insightful."
    )
    st.divider()

    st.markdown("### 📄 Bill Analysis")
    uploaded = st.file_uploader(
        "Upload a DEWA bill photo",
        type=["jpg", "jpeg", "png"],
        help="Photo of your bill for AI-powered analysis"
    )
    if uploaded:
        st.image(uploaded, caption="Uploaded bill", use_column_width=True)
        if st.button("🔍 Analyse this bill", type="primary", use_container_width=True):
            st.session_state.pending_image = encode_image(uploaded)
            st.session_state.messages.append({
                "role": "user",
                "content": (
                    "Please analyse this DEWA bill. Extract: account number, billing period, "
                    "total amount due, electricity and water consumption (kWh / gallons), "
                    "breakdown of charges, and give me 3 personalised recommendations to lower my bill."
                ),
                "has_image": True,
            })
            st.rerun()

    st.divider()
    st.markdown("### Quick questions")
    QUICK = [
        ("📋 Tariff rates",             "What are the current residential electricity tariff rates?"),
        ("💰 Save 20%",                  "How much would I save if I cut my electricity usage by 20%? I currently use 1800 kWh/month."),
        ("📊 Account summary",           "Show me my account summary and analyse my consumption trend."),
        ("🔌 Downtown outage?",          "Are there any power outages in Downtown Dubai right now?"),
        ("♻️ Green energy tips",          "Give me the top 5 ways to reduce electricity and water bills in Dubai."),
    ]
    for label, question in QUICK:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_image = None
        st.rerun()

# ── Main chat area ────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# ⚡ DEWA Smart Assistant")
    st.caption("Dubai Electricity & Water Authority — AI-powered billing & support assistant")
with col2:
    if DEMO_MODE:
        st.markdown('<br><span style="background:#FEF3C7;border:1px solid #F59E0B;border-radius:8px;padding:4px 12px;font-size:0.85rem;color:#92400E">🔑 Demo Mode</span>', unsafe_allow_html=True)
    else:
        st.markdown('<br><span style="background:#D1FAE5;border:1px solid #10B981;border-radius:8px;padding:4px 12px;font-size:0.85rem;color:#065F46">✅ Live Mode</span>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.info(
        "**Welcome!** I can help you:\n"
        "- Analyse your DEWA bill (upload a photo in the sidebar)\n"
        "- Explain tariff structures and charges\n"
        "- Calculate how much you'd save with energy-saving changes\n"
        "- Check outage status by area\n"
        "- Review your consumption history and spot trends\n\n"
        "Ask me anything or pick a quick question on the left."
    )

# Render existing messages
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role, avatar="⚡" if role == "assistant" else None):
        st.markdown(msg["content"])
        if msg.get("tools_used"):
            badges = "".join(
                f'<span class="tool-badge">🔧 {t}</span>' for t in msg["tools_used"]
            )
            st.markdown(f"<small>Tools used: {badges}</small>", unsafe_allow_html=True)

# ── Process the latest user message ──────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    latest = st.session_state.messages[-1]

    # Build API-compatible history (exclude the latest — we pass it separately)
    history = []
    for m in st.session_state.messages[:-1]:
        history.append({"role": m["role"], "content": m["content"]})

    image_data = st.session_state.pending_image if latest.get("has_image") else None

    with st.chat_message("assistant", avatar="⚡"):
        if st.session_state.stream_mode and not image_data and not st.session_state.deep_mode:
            # ── Streaming path ─────────────────────────────────────────────
            response_text = st.write_stream(
                agent.stream_chat(latest["content"], history)
            )
        else:
            # ── Non-streaming path (tool use / vision / deep analysis) ─────
            with st.spinner("Thinking..." if not st.session_state.deep_mode else "Deep analysis in progress..."):
                response_text = agent.chat(
                    latest["content"],
                    history,
                    image_data=image_data,
                    deep_analysis=st.session_state.deep_mode,
                )
            st.markdown(response_text)

    if image_data:
        st.session_state.pending_image = None

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
    })

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your bill, tariffs, outages…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
