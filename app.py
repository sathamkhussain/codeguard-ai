"""
CodeGuard AI — Code Vulnerability Scanner
Powered by Claude AI

Claude features: Tool Use, Vision, Prompt Caching, Multi-turn, Streaming, Extended Thinking
"""

import streamlit as st
from scanner.client import has_api_key
from utils.image_utils import encode_image

if has_api_key():
    from scanner.agent import CodeGuardAgent as ActiveAgent
    DEMO_MODE = False
else:
    from scanner.mock_agent import MockCodeGuardAgent as ActiveAgent  # type: ignore
    DEMO_MODE = True

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Base dark theme */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] * { color: #c9d1d9 !important; }

    /* Dark toolbar / top header */
    [data-testid="stHeader"] {
        background-color: #161b22 !important;
        border-bottom: 1px solid #30363d !important;
    }
    [data-testid="stHeader"] * { color: #c9d1d9 !important; }
    [data-testid="stToolbar"] { background-color: #161b22 !important; }
    .stDeployButton { color: #8b949e !important; }

    /* Toggle — blue accent */
    .stToggle input:checked + div { background-color: #1f6feb !important; }

    /* Typography */
    h1 { color: #58a6ff !important; font-family: monospace !important; letter-spacing: -1px; }
    h2, h3 { color: #58a6ff !important; }
    p, li { color: #c9d1d9; }

    /* Code input area */
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #79c0ff !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 0.875rem !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:focus { border-color: #58a6ff !important; box-shadow: 0 0 0 2px #58a6ff33 !important; }

    /* Primary scan button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover { opacity: 0.85 !important; transform: translateY(-1px); }

    /* Secondary buttons */
    .stButton > button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    .stButton > button:hover { border-color: #58a6ff !important; color: #58a6ff !important; }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 6px !important;
    }

    /* Divider */
    hr { border-color: #30363d !important; }

    /* Feature pills */
    .feature-pill {
        display: inline-block;
        background: #1f6feb22;
        border: 1px solid #1f6feb;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        color: #58a6ff;
        margin: 2px 2px 2px 0;
        font-family: monospace;
    }

    /* Status badges */
    .badge-live {
        background: #0d1f3c;
        border: 1px solid #58a6ff;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #58a6ff;
        font-family: monospace;
    }
    .badge-demo {
        background: #1a1100;
        border: 1px solid #e3b341;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #e3b341;
        font-family: monospace;
    }

    /* Scan result container */
    .scan-output {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
        margin-top: 16px;
    }

    /* Demo banner */
    .demo-banner {
        background: #1a1100;
        border: 1px solid #e3b341;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #e3b341;
        margin-bottom: 8px;
    }

    /* Welcome screen */
    .welcome-box {
        text-align: center;
        padding: 64px 24px;
        border: 1px dashed #30363d;
        border-radius: 12px;
        margin-top: 24px;
        background: #161b2255;
    }

    /* Toggle */
    .stToggle label { color: #c9d1d9 !important; }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin: 6px 0 !important;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #58a6ff !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #161b22 !important;
        border: 1px dashed #30363d !important;
        border-radius: 8px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = ActiveAgent()
if "pending_scan" not in st.session_state:
    st.session_state.pending_scan = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

agent = st.session_state.agent

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ CodeGuard AI")

    if DEMO_MODE:
        st.markdown('<div class="demo-banner">🔑 <b>Demo Mode</b><br>Add <code>ANTHROPIC_API_KEY</code> to <code>.env</code> for real Claude scanning.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#58a6ff;font-family:monospace;font-size:0.85rem">● LIVE — Claude AI</span>')

    st.divider()

    # Claude features
    st.markdown("**Claude Features**")
    st.markdown("""
    <span class="feature-pill">🔧 Tool Use</span>
    <span class="feature-pill">👁️ Vision</span>
    <span class="feature-pill">⚡ Caching</span>
    <span class="feature-pill">💬 Multi-turn</span>
    <span class="feature-pill">🌊 Streaming</span>
    <span class="feature-pill">🧠 Thinking</span>
    """, unsafe_allow_html=True)

    st.divider()

    # Scan options
    st.markdown("**Scan Options**")
    deep_scan = st.toggle(
        "🧠 Deep Scan (Extended Thinking)",
        value=False,
        help="Claude reasons deeply before reporting. More thorough, slightly slower."
    )
    stream_output = st.toggle("🌊 Stream output", value=True)

    st.divider()

    # Image upload
    st.markdown("**📸 Scan Code Screenshot**")
    uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        st.image(uploaded, use_column_width=True)
        if st.button("🔍 Scan Image", type="primary", use_container_width=True):
            st.session_state.pending_scan = {
                "prompt": "Scan all the code visible in this image for security vulnerabilities. Identify every issue, assign severity, and provide fixes.",
                "image_data": encode_image(uploaded),
                "deep": deep_scan,
                "stream": False,
            }
            st.rerun()

    st.divider()

    # Quick examples
    st.markdown("**⚡ Quick Examples**")
    EXAMPLES = [
        ("SQL Injection", 'query = "SELECT * FROM users WHERE id = " + user_id\ndb.execute(query)'),
        ("Hardcoded Secrets", 'API_KEY = "sk-1234567890abcdef"\npassword = "admin123"'),
        ("XSS + eval()", 'document.getElementById("out").innerHTML = userInput;\neval(userInput);'),
        ("Insecure Functions", 'import pickle\ndata = pickle.loads(user_data)\nos.system("rm -rf " + path)'),
        ("Swift Vulnerabilities", 'let apiKey = "sk-abc123secretkey"\nUserDefaults.standard.set(password, forKey: "userPassword")\nNSLog("Token: \\(authToken)")\nlet query = "SELECT * FROM users WHERE id = \\(userId)"'),
    ]
    for label, code in EXAMPLES:
        if st.button(f"{label}", use_container_width=True):
            st.session_state.pending_scan = {
                "prompt": f"Scan this code for security vulnerabilities:\n\n```\n{code}\n```",
                "image_data": None,
                "deep": deep_scan,
                "stream": stream_output,
                "code_preview": code,
            }
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown("# 🛡️ CodeGuard AI")
    st.markdown('<p style="color:#8b949e;margin-top:-12px">AI-powered code vulnerability scanner — paste code or upload a screenshot</p>', unsafe_allow_html=True)
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    if DEMO_MODE:
        st.markdown('<div class="badge-demo">⚠ Demo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-live">🛡 Live</div>', unsafe_allow_html=True)

st.divider()

# ── Code input ────────────────────────────────────────────────────────────────
code_input = st.text_area(
    "code_area",
    height=220,
    placeholder="# Paste any code here — Python, JavaScript, PHP, Java, SQL...\n\nquery = 'SELECT * FROM users WHERE name = ' + username\nAPI_KEY = 'sk-hardcoded-key-1234'\neval(userInput)",
    label_visibility="collapsed",
)

col_lang, col_scan, col_deep = st.columns([2, 3, 2])
with col_lang:
    language = st.selectbox(
        "lang",
        ["Auto Detect", "Swift", "Python", "JavaScript", "PHP", "Java", "Go", "Ruby", "SQL", "Kotlin"],
        label_visibility="collapsed",
    )
with col_scan:
    scan_clicked = st.button(
        "🔍  Scan for Vulnerabilities",
        type="primary",
        use_container_width=True,
        disabled=not code_input.strip(),
    )
with col_deep:
    quick_deep = st.toggle("🧠 Deep", value=False, key="inline_deep")

if scan_clicked and code_input.strip():
    st.session_state.pending_scan = {
        "prompt": f"Scan this {language} code for security vulnerabilities. Run all relevant scanning tools and report every issue found.\n\n```{language.lower()}\n{code_input}\n```",
        "image_data": None,
        "deep": quick_deep,
        "stream": stream_output,
        "code_preview": code_input,
    }
    st.rerun()

# ── Process pending scan ──────────────────────────────────────────────────────
if st.session_state.pending_scan:
    scan = st.session_state.pending_scan
    st.session_state.pending_scan = None

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    st.markdown("---")
    st.markdown("### 🔎 Scanning...")

    with st.container():
        st.markdown('<div class="scan-output">', unsafe_allow_html=True)

        if scan.get("stream") and not scan["image_data"] and not scan["deep"]:
            result = st.write_stream(agent.stream_chat(scan["prompt"], history))
        else:
            label = "🧠 Deep scanning with extended thinking..." if scan["deep"] else "⚙️ Running vulnerability scanners..."
            with st.spinner(label):
                result = agent.chat(scan["prompt"], history, image_data=scan.get("image_data"), deep_analysis=scan["deep"])
            st.markdown(result)

        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": scan["prompt"]})
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.session_state.last_result = result

# ── Follow-up chat ────────────────────────────────────────────────────────────
if st.session_state.last_result:
    st.divider()
    st.markdown("### 💬 Ask a follow-up")
    st.caption("Ask Claude to explain a vulnerability, show a fix, or scan something else.")

    if prompt := st.chat_input("e.g. Show me the fixed version of the SQL injection..."):
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🛡️"):
            followup = st.write_stream(agent.stream_chat(prompt, history))

        st.session_state.messages.append({"role": "assistant", "content": followup})
        st.rerun()

    # Show prior follow-up exchanges
    followups = [m for m in st.session_state.messages if not (
        m["role"] == "user" and ("Scan this" in m["content"] or "Scan all" in m["content"])
    )][2:]  # skip first user+assistant (the scan itself)

    for msg in followups:
        with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

# ── Welcome screen ────────────────────────────────────────────────────────────
elif not st.session_state.pending_scan:
    st.markdown("""
    <div class="welcome-box">
        <div style="font-size:3.5rem;margin-bottom:12px">🛡️</div>
        <h3 style="color:#c9d1d9 !important;margin-bottom:8px">Paste code above or try an example</h3>
        <p style="color:#8b949e;max-width:480px;margin:0 auto">
            CodeGuard AI scans for SQL injection, XSS, hardcoded secrets,<br>
            insecure functions, and authentication flaws — in any language.
        </p>
        <br>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <span style="background:#1a0a0a;border:1px solid #ff4444;border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#ff4444">🔴 SQL Injection</span>
            <span style="background:#1a110a;border:1px solid #ff8800;border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#ff8800">🟠 XSS</span>
            <span style="background:#1a0a0a;border:1px solid #ff4444;border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#ff4444">🔴 Hardcoded Secrets</span>
            <span style="background:#1a110a;border:1px solid #ff8800;border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#ff8800">🟠 Insecure Functions</span>
            <span style="background:#1a1a0a;border:1px solid #ffcc00;border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#ffcc00">🟡 Auth Flaws</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
