"""
╔══════════════════════════════════════════════════════════════════╗
║          AI TUTOR  —  Smart Learning Platform                   ║
║  Professional Streamlit Dashboard with animations & API calls   ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────
import streamlit as st
import requests
import time
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Tutor — Smart Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# STYLING  (Custom CSS — glassmorphism + animations + theme)
# ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
/* ── Google Font ──────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root & Global ────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App Background — animated gradient ───────────────────────── */
.stApp {
    background: linear-gradient(-45deg, #0a0a1a, #0d1b3e, #1a0a2e, #0a1628, #070d1f, #12002e);
    background-size: 400% 400%;
    animation: gradientBG 14s ease infinite;
    min-height: 100vh;
    overflow-x: hidden;
}

@keyframes gradientBG {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
}

/* ── Floating Stars Background ─────────────────────────────────── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 30% 60%, rgba(200,180,255,0.5) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 50% 10%, rgba(255,255,255,0.7) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 80%, rgba(180,200,255,0.5) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 85% 30%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 20% 85%, rgba(200,180,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 60% 45%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 92% 65%, rgba(255,200,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 40% 92%, rgba(180,255,200,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 5%,  rgba(255,255,255,0.6) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
    animation: starTwinkle 4s ease-in-out infinite alternate;
}

@keyframes starTwinkle {
    0%   { opacity: 0.4; }
    100% { opacity: 1;   }
}

/* ── Page fade-in on load ─────────────────────────────────────── */
.main .block-container {
    animation: pageFadeIn 0.7s ease-in-out;
    padding-top: 2rem;
}

@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0);    }
}

/* ── Sidebar ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 30, 0.95) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(99, 89, 255, 0.25);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── Nav buttons in sidebar ──────────────────────────────────── */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 12px 16px;
    margin: 4px 0;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #a0aec0;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    text-align: left;
    transition: all 0.25s ease;
    text-decoration: none;
}

.nav-btn:hover, .nav-btn.active {
    background: linear-gradient(90deg, rgba(99,89,255,0.25), rgba(139,92,246,0.15));
    color: #c4b5fd;
    padding-left: 22px;
    border-left: 3px solid #8b5cf6;
}

/* ── Glassmorphism cards ─────────────────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
    animation: cardFadeIn 0.5s ease-in-out;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative;
    overflow: hidden;
}

/* Shimmer sweep on cards */
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
    animation: shimmerSweep 4s ease-in-out infinite;
    pointer-events: none;
}

@keyframes shimmerSweep {
    0%   { left: -100%; }
    60%  { left: 150%;  }
    100% { left: 150%;  }
}

.glass-card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 20px 60px rgba(99,89,255,0.3), 0 0 30px rgba(139,92,246,0.15),
                inset 0 1px 0 rgba(255,255,255,0.15);
    border-color: rgba(139,92,246,0.4);
}

@keyframes cardFadeIn {
    from { opacity: 0; transform: scale(0.97) translateY(10px); }
    to   { opacity: 1; transform: scale(1)    translateY(0);    }
}

/* ── Stat cards ──────────────────────────────────────────────── */
.stat-card {
    background: linear-gradient(135deg, rgba(99,89,255,0.2), rgba(139,92,246,0.1));
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    animation: cardFadeIn 0.6s ease, statPulse 3s ease-in-out infinite;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    overflow: hidden;
}

@keyframes statPulse {
    0%, 100% { box-shadow: 0 4px 20px rgba(99,89,255,0.15); }
    50%       { box-shadow: 0 4px 30px rgba(139,92,246,0.4); }
}

.stat-card:hover {
    transform: scale(1.06) translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,89,255,0.5);
    border-color: #c4b5fd;
}

.stat-number {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #c4b5fd, #f0abfc, #818cf8);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbowShift 4s linear infinite;
}

.stat-label {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Page title ───────────────────────────────────────────────── */
.page-title {
    font-size: 34px;
    font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #c4b5fd, #f0abfc, #818cf8);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
    animation: rainbowShift 3s linear infinite;
}

@keyframes rainbowShift {
    0%   { background-position: 0%   center; }
    100% { background-position: 200% center; }
}

.page-subtitle {
    font-size: 15px;
    color: #64748b;
    margin-bottom: 24px;
}

/* ── Section header ───────────────────────────────────────────── */
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #c4b5fd;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(139,92,246,0.3);
}

/* ── Chat bubbles ─────────────────────────────────────────────── */
.chat-wrapper {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 6px;
    scrollbar-width: thin;
    scrollbar-color: #4f46e5 transparent;
}

.user-bubble {
    display: flex;
    justify-content: flex-end;
    margin: 10px 0;
    animation: slideFromRight 0.35s ease;
}

.user-bubble-inner {
    max-width: 72%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(79,70,229,0.4);
}

.bot-bubble {
    display: flex;
    justify-content: flex-start;
    margin: 10px 0;
    animation: slideFromLeft 0.35s ease;
}

.bot-bubble-inner {
    max-width: 72%;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e2e8f0;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    font-size: 14px;
    line-height: 1.6;
}

.bubble-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    margin: 0 8px;
}

.user-avatar { background: #4f46e5; }
.bot-avatar  { background: rgba(99,89,255,0.2); border: 1px solid rgba(139,92,246,0.4); }

@keyframes slideFromRight {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0);    }
}

@keyframes slideFromLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to   { opacity: 1; transform: translateX(0);     }
}

/* ── Typing dots animation ────────────────────────────────────── */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 14px 18px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px 18px 18px 4px;
    width: fit-content;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: #818cf8;
    border-radius: 50%;
    animation: typingBounce 1.2s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
    0%, 60%, 100% { transform: translateY(0);   opacity: 0.4; }
    30%            { transform: translateY(-8px); opacity: 1;   }
}

/* ── Animated submit button ───────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #9333ea) !important;
    background-size: 200% auto !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 28px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(79,70,229,0.4), 0 0 0 0 rgba(139,92,246,0.5) !important;
    letter-spacing: 0.5px !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 0; height: 0;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.4s ease, height 0.4s ease, opacity 0.4s ease;
    opacity: 0;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 12px 35px rgba(79,70,229,0.65), 0 0 20px rgba(139,92,246,0.3) !important;
    background-position: right center !important;
}

.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ── Text inputs ─────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    border-radius: 10px !important;
    color: #000000 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

/* Chat input black text */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    color: #000000 !important;
    background: rgba(255,255,255,0.92) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,89,255,0.15) !important;
}

/* ── File uploader ───────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(139,92,246,0.4) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    background: rgba(79,70,229,0.05) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #818cf8 !important;
    background: rgba(79,70,229,0.1) !important;
}

/* ── Success / Error alerts ───────────────────────────────────── */
.success-alert {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.4);
    border-left: 4px solid #10b981;
    border-radius: 10px;
    padding: 14px 18px;
    color: #6ee7b7;
    font-size: 14px;
    animation: cardFadeIn 0.4s ease;
}

.error-alert {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.4);
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 14px 18px;
    color: #fca5a5;
    font-size: 14px;
    animation: cardFadeIn 0.4s ease;
}

.info-alert {
    background: rgba(99,89,255,0.1);
    border: 1px solid rgba(99,89,255,0.3);
    border-left: 4px solid #818cf8;
    border-radius: 10px;
    padding: 14px 18px;
    color: #c4b5fd;
    font-size: 14px;
    animation: cardFadeIn 0.4s ease;
}

/* ── Response card ────────────────────────────────────────────── */
.response-card {
    background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(139,92,246,0.08));
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 20px 24px;
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.75;
    animation: cardFadeIn 0.4s ease;
}

/* ── Progress bar ─────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #f0abfc) !important;
    border-radius: 6px !important;
}

/* ── Selectbox / Radio ────────────────────────────────────────── */
.stSelectbox > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    border-radius: 10px !important;
}

/* ── Dividers ─────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    margin: 20px 0 !important;
}

/* ── Scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 3px; }

/* ── Badge ────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.badge-purple { background: rgba(139,92,246,0.2); color: #c4b5fd; }
.badge-green  { background: rgba(16,185,129,0.15); color: #6ee7b7; }
.badge-red    { background: rgba(239,68,68,0.15);   color: #fca5a5; }

/* ── Logo row ─────────────────────────────────────────────────── */
.logo-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}

.logo-icon {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 15px rgba(79,70,229,0.4);
}

.logo-text {
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(90deg, #c4b5fd, #f0abfc, #818cf8, #c4b5fd);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: rainbowShift 5s linear infinite;
}
.logo-sub  { font-size: 11px; color: #64748b; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; }

/* ── Pulse animation for status dot ──────────────────────────── */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #10b981;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1);   box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
    50%       { opacity: 0.8; transform: scale(1.1); box-shadow: 0 0 0 5px rgba(16,185,129,0); }
}

/* ── Chart containers ────────────────────────────────────────── */
.chart-label {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 6px;
    font-weight: 500;
}

.chart-bar-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
    margin-bottom: 14px;
}

.chart-bar-fill {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #4f46e5, #c4b5fd);
    animation: barGrow 1s ease-out;
}

@keyframes barGrow {
    from { width: 0%; }
}

/* ── Settings toggle ─────────────────────────────────────────── */
.stCheckbox span[data-baseweb="checkbox"] {
    background-color: rgba(79,70,229,0.2) !important;
    border-color: rgba(139,92,246,0.4) !important;
}

/* ── Metric labels ───────────────────────────────────────────── */
[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
}

[data-testid="stMetricValue"] {
    color: #c4b5fd !important;
    font-weight: 700 !important;
}

/* ── Footer ──────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #334155;
    font-size: 12px;
    padding: 20px 0 8px;
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "page": "Home Dashboard",
        "messages": [],
        "api_status": None,
        "last_response": None,
        "uploaded_files": [],
        "settings": {
            "api_url": "http://localhost:8001",
            "model": "gpt-4o",
            "temperature": 0.7,
            "theme": "Dark",
            "auto_scroll": True,
            "typing_animation": True,
        },
        "stats": {
            "queries_sent": 0,
            "files_uploaded": 0,
            "sessions": 1,
        },
        "quiz_data": [],
        "quiz_active": False,
        "quiz_index": 0,
        "quiz_score": 0,
        "quiz_feedback": None,
        "quiz_finished": False,
        "quiz_topic": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# ─────────────────────────────────────────────────────────────────
# API FUNCTIONS
# ─────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8001"

def call_backend_api(user_input: str) -> dict:
    """
    Send user input to the backend /chat/ endpoint.
    Endpoint: POST {BACKEND_URL}/chat/
    """
    url = f"{BACKEND_URL}/chat/"
    try:
        response = requests.post(
            url,
            json={
                "query": user_input,
                "session_id": "user1",
                "top_k": None,
                "use_reranker": True
            },
            timeout=180,
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"❌ Cannot reach backend at **{url}**. Make sure the API server is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "⏱️ Request timed out. The backend took too long to respond."}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"🔴 HTTP error: `{e.response.status_code}` — {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Unexpected error: {str(e)}"}


# ─────────────────────────────────────────────────────────────────
# PRIMARY CHAT FUNCTION  (used by Chat Interface)
# ─────────────────────────────────────────────────────────────────


def ask_ai(question: str, session_id: str = "user1") -> dict:
    """
    Send a chat query to the backend /chat/ endpoint using JSON body.
    Endpoint: POST {BACKEND_URL}/chat/
    """
    url = f"{BACKEND_URL}/chat/"
    try:
        response = requests.post(
            url,
            json={
                "query": question,
                "session_id": session_id,
                "top_k": None,
                "use_reranker": True
            },
            timeout=180,
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"❌ Cannot reach backend at **{url}**. Make sure the API server is running on port 8000."}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "⏱️ Request timed out. The backend took too long to respond."}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"🔴 HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Unexpected error: {str(e)}"}


def upload_file_to_backend(file) -> dict:
    """Upload a PDF/file to the backend /ingest/upload endpoint."""
    endpoint = f"{BACKEND_URL}/ingest/upload"
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(endpoint, files=files, timeout=300)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"❌ Cannot reach backend at **{endpoint}**. Make sure the API server is running on port 8000."}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"🔴 HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Upload failed: {str(e)}"}


def ingest_text_to_backend(text_content: str, source_name: str = "pasted_text") -> dict:
    """Ingest raw text via POST /ingest/text."""
    endpoint = f"{BACKEND_URL}/ingest/text"
    try:
        response = requests.post(
            endpoint,
            json={"text": text_content, "source_name": source_name},
            timeout=300,
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"❌ Cannot reach backend at **{endpoint}**."}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"🔴 HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Ingest failed: {str(e)}"}


def generate_quiz(topic: str = "", context: str = "", num_questions: int = 5) -> dict:
    """Generate a quiz via POST /generate-quiz/."""
    endpoint = f"{BACKEND_URL}/generate-quiz/"
    try:
        payload = {"num_questions": num_questions}
        if topic:
            payload["topic"] = topic
        if context:
            payload["context"] = context
        response = requests.post(endpoint, json=payload, timeout=180)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": f"❌ Cannot reach backend at **{endpoint}**."}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"🔴 HTTP {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"status": "error", "message": f"⚠️ Quiz generation failed: {str(e)}"}


def get_ingest_stats() -> dict:
    """Fetch vector DB stats via GET /ingest/stats."""
    endpoint = f"{BACKEND_URL}/ingest/stats"
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_backend_health() -> bool:
    """Ping GET /health and return True if online."""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("🏠", "Home Dashboard"),
    ("📂", "Upload Data"),
    ("💬", "Chat Interface"),
    ("📝", "Interactive Quiz"),
    ("📊", "Results"),
    ("⚙️", "Settings"),
]

with st.sidebar:
    # Logo
    st.markdown("""
    <div class="logo-row">
        <div class="logo-icon">🎓</div>
        <div>
            <div class="logo-text">AI Tutor</div>
            <div class="logo-sub">Smart Learning Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:11px;color:#475569;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)

    for icon, label in NAV_ITEMS:
        is_active = st.session_state.page == label
        active_class = "nav-btn active" if is_active else "nav-btn"
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()

    st.markdown("---")

    # Backend status
    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        if st.button("🔄", key="refresh_health", help="Check backend status"):
            st.session_state.api_status = check_backend_health()
            st.rerun()
    with col_s2:
        if st.session_state.api_status is True:
            st.markdown('<div style="font-size:13px;color:#6ee7b7;padding-top:5px;"><span class="status-dot"></span>API Online</div>', unsafe_allow_html=True)
        elif st.session_state.api_status is False:
            st.markdown('<div style="font-size:13px;color:#fca5a5;padding-top:5px;">🔴 API Offline</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:13px;color:#64748b;padding-top:5px;">⚪ Status unknown</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div style="font-size:11px;color:#475569;text-align:center;">{datetime.now().strftime("%a, %d %b %Y %H:%M")}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;color:#5b4d8a;text-align:center;margin-top:4px;">✨ Powered by AI • Study Smarter</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HELPER UI COMPONENTS
# ─────────────────────────────────────────────────────────────────

def show_success(msg: str):
    st.markdown(f'<div class="success-alert">✅ {msg}</div>', unsafe_allow_html=True)

def show_error(msg: str):
    st.markdown(f'<div class="error-alert">{msg}</div>', unsafe_allow_html=True)

def show_info(msg: str):
    st.markdown(f'<div class="info-alert">ℹ️ {msg}</div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE 1 — HOME DASHBOARD
# ─────────────────────────────────────────────────────────────────

def page_home():
    page_header("🏠 Home Dashboard", "Welcome back! Your AI learning platform is ready.")

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    stats = st.session_state.stats

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['queries_sent']}</div>
            <div class="stat-label">💬 Queries Sent</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['files_uploaded']}</div>
            <div class="stat-label">📂 Files Uploaded</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['sessions']}</div>
            <div class="stat-label">🔁 Sessions</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.messages)//2}</div>
            <div class="stat-label">🧠 Conversations</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main content columns
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🚀 Quick Actions")
        q1, q2 = st.columns(2)
        with q1:
            if st.button("💬  Start Chatting", key="home_chat", use_container_width=True):
                st.session_state.page = "Chat Interface"
                st.rerun()
            if st.button("📂  Upload Document", key="home_upload", use_container_width=True):
                st.session_state.page = "Upload Data"
                st.rerun()
        with q2:
            if st.button("📊  View Results", key="home_results", use_container_width=True):
                st.session_state.page = "Results"
                st.rerun()
            if st.button("⚙️  Settings", key="home_settings", use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        section("📈 Activity Overview")
        topics = [("Algebra", 82), ("Physics", 65), ("History", 47), ("Chemistry", 90), ("Literature", 38)]
        for topic, pct in topics:
            st.markdown(f'<div class="chart-label">{topic} <span style="float:right;color:#818cf8;font-weight:600;">{pct}%</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-bar-bg"><div class="chart-bar-fill" style="width:{pct}%;"></div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("📌 Recent Activity")
        activities = [
            ("💬", "Asked about derivatives", "2m ago"),
            ("📂", "Uploaded Physics Notes.pdf", "15m ago"),
            ("🧠", "Generated quiz on history", "1h ago"),
            ("✅", "Completed session #7", "3h ago"),
        ]
        for icon, label, time_ago in activities:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:22px;">{icon}</div>
                <div style="flex:1;">
                    <div style="font-size:13px;color:#e2e8f0;font-weight:500;">{label}</div>
                    <div style="font-size:11px;color:#475569;margin-top:2px;">{time_ago}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🔌 System Status")
        api_url = st.session_state.settings["api_url"]
        st.markdown(f'<div style="font-size:13px;color:#94a3b8;margin-bottom:8px;">Backend: <code style="color:#c4b5fd;">{api_url}</code></div>', unsafe_allow_html=True)
        if st.button("🔄 Check API Health", key="home_health", use_container_width=True):
            with st.spinner("Pinging backend..."):
                ok = check_backend_health()
                st.session_state.api_status = ok
            if ok:
                show_success("Backend is online and reachable!")
            else:
                show_error(f"Cannot reach backend at `{api_url}`. Start Member 1's server.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick send from dashboard
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section("⚡ Quick Query")
    quick_q = st.text_input("Quick Query", placeholder="Ask a quick question to the AI…", key="home_quick_q", label_visibility="collapsed")
    if st.button("Send Query →", key="home_send"):
        if quick_q.strip():
            with st.spinner(""):
                st.markdown("""
                <div class="bot-bubble" style="margin:12px 0;">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
                result = call_backend_api(quick_q)
            if result["status"] == "success":
                answer = result["data"].get("answer", result["data"].get("response", str(result["data"])))
                st.markdown(f'<div class="response-card">🤖 {answer}</div>', unsafe_allow_html=True)
                st.session_state.stats["queries_sent"] += 1
            else:
                show_error(result["message"])
        else:
            show_info("Please type a question first.")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE 2 — UPLOAD DATA
# ─────────────────────────────────────────────────────────────────

def page_upload():
    page_header("📂 Upload Data", "Upload study materials for the AI Tutor to analyze.")

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("📎 File Upload")
        uploaded = st.file_uploader(
            "Drag & drop files here, or click to browse",
            type=["pdf", "txt", "docx", "png", "jpg", "csv", "json"],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed",
        )

        if uploaded:
            st.markdown("<br>", unsafe_allow_html=True)
            for f in uploaded:
                size_kb = len(f.getvalue()) / 1024
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                            background:rgba(79,70,229,0.08);border:1px solid rgba(139,92,246,0.25);
                            border-radius:10px;margin-bottom:8px;">
                    <span style="font-size:20px;">📄</span>
                    <div style="flex:1;">
                        <div style="color:#e2e8f0;font-size:13px;font-weight:600;">{f.name}</div>
                        <div style="color:#64748b;font-size:11px;">{f.type} • {size_kb:.1f} KB</div>
                    </div>
                    <span class="badge badge-purple">Ready</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀  Upload to Backend", key="upload_btn", use_container_width=True):
                progress = st.progress(0, text="Uploading…")
                all_ok = True
                for i, f in enumerate(uploaded):
                    progress.progress((i + 1) / len(uploaded), text=f"Uploading {f.name}…")
                    result = upload_file_to_backend(f)
                    if result["status"] == "success":
                        st.session_state.uploaded_files.append(f.name)
                        st.session_state.stats["files_uploaded"] += 1
                    else:
                        show_error(result["message"])
                        all_ok = False
                    time.sleep(0.3)
                progress.empty()
                if all_ok:
                    show_success(f"Successfully uploaded {len(uploaded)} file(s) to the backend!")

        st.markdown('</div>', unsafe_allow_html=True)

        # Manual text input
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("✍️ Paste Text Content")
        text_content = st.text_area(
            "Study Material",
            placeholder="Paste lecture notes, textbook excerpts, or any study material here…",
            height=180,
            key="paste_text",
            label_visibility="collapsed",
        )
        if st.button("Submit Text →", key="submit_text"):
            if text_content.strip():
                with st.spinner("Ingesting text into backend..."):
                    result = ingest_text_to_backend(text_content, source_name="pasted_text")
                if result["status"] == "success":
                    show_success("Text content ingested into the RAG pipeline successfully!")
                    st.session_state.stats["files_uploaded"] += 1
                else:
                    show_error(result["message"])
            else:
                show_info("Please paste some text content first.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("📋 Upload History")
        if st.session_state.uploaded_files:
            for fname in reversed(st.session_state.uploaded_files[-10:]):
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:9px 0;
                            border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span>📄</span>
                    <span style="color:#c4b5fd;font-size:13px;">{fname}</span>
                    <span class="badge badge-green" style="margin-left:auto;">✓ Done</span>
                </div>""", unsafe_allow_html=True)
        else:
            show_info("No files uploaded yet in this session.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("ℹ️ Supported Formats")
        formats = [
            ("📄", "PDF", "Study notes, textbooks"),
            ("📝", "TXT / DOCX", "Plain text, Word docs"),
            ("🖼️", "PNG / JPG", "Diagrams, images"),
            ("📊", "CSV / JSON", "Structured data"),
        ]
        for icon, fmt, desc in formats:
            st.markdown(f"""
            <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;">
                <span style="font-size:18px;">{icon}</span>
                <div>
                    <div style="color:#c4b5fd;font-size:13px;font-weight:600;">{fmt}</div>
                    <div style="color:#64748b;font-size:11px;">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE 3 — CHAT INTERFACE
# ─────────────────────────────────────────────────────────────────

def page_chat():
    page_header("💬 Chat Interface", "Have a conversation with your AI Tutor.")

    # Chat history display
    st.markdown('<div class="glass-card" style="padding:20px;">', unsafe_allow_html=True)
    section("🗨️ Conversation")

    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#475569;">
            <div style="font-size:48px;margin-bottom:12px;">🤖</div>
            <div style="font-size:16px;font-weight:600;color:#94a3b8;margin-bottom:6px;">AI Tutor is ready!</div>
            <div style="font-size:13px;">Ask me anything about your study materials.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-bubble">
                    <div class="user-bubble-inner">{msg["content"]}</div>
                    <div class="bubble-avatar user-avatar">👤</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-bubble">
                    <div class="bubble-avatar bot-avatar">🤖</div>
                    <div class="bot-bubble-inner">{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input row
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    inp_col, btn_col, clr_col = st.columns([8, 1.5, 1.5])
    with inp_col:
        user_msg = st.text_input(
            "Chat Message",
            placeholder="Ask your AI Tutor anything…",
            key="chat_input",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send ➤", key="chat_send", use_container_width=True)
    with clr_col:
        if st.button("🗑️ Clear", key="chat_clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Suggested prompts
    st.markdown('<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">', unsafe_allow_html=True)
    suggestions = ["Explain this concept", "Give me a quiz", "Summarize notes", "Solve this problem"]
    s_cols = st.columns(len(suggestions))
    for i, (col, sug) in enumerate(zip(s_cols, suggestions)):
        with col:
            if st.button(f"💡 {sug}", key=f"sug_{i}", use_container_width=True):
                user_msg = sug
                send = True
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Send logic  — uses ask_ai() → POST /chat/?query=...&session_id=user1
    if send and user_msg and user_msg.strip():
        st.session_state.messages.append({"role": "user", "content": user_msg})
        st.session_state.stats["queries_sent"] += 1

        # Show typing animation while waiting for AI response
        with st.spinner("🤖 AI Tutor is thinking…"):
            result = ask_ai(user_msg)

        if result["status"] == "success":
            data = result["data"]
            # Accept various response field names from the backend
            answer = (
                data.get("response")
                or data.get("answer")
                or data.get("message")
                or data.get("reply")
                or str(data)
            )
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            # Graceful error — still shown inside chat so the user knows what happened
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ {result['message']}"
            })

        st.rerun()


# ─────────────────────────────────────────────────────────────────
# PAGE 3.5 — INTERACTIVE QUIZ
# ─────────────────────────────────────────────────────────────────

def page_quiz():
    page_header("📝 Interactive Quiz", "Test your knowledge based on your study materials.")

    if not st.session_state.quiz_active and not st.session_state.quiz_finished:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🎯 Quiz Configuration")
        topic = st.text_input("Quiz Topic", value=st.session_state.quiz_topic, placeholder="e.g. Vision Transformers, Newton's Laws...")
        num_q = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

        if st.button("🚀 Generate Quiz", use_container_width=True):
            if not topic.strip():
                show_error("Please enter a topic first.")
            else:
                with st.spinner("Analyzing documents and crafting questions..."):
                    result = generate_quiz(topic=topic, num_questions=num_q)
                
                if result["status"] == "success":
                    questions = result["data"].get("questions", [])
                    if questions and len(questions) > 0:
                        # Check if it's the "No context found" dummy question
                        if "could not find enough information" in questions[0].get("question", ""):
                             show_error(questions[0]["question"])
                        else:
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_active = True
                            st.session_state.quiz_index = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_feedback = None
                            st.session_state.quiz_topic = topic
                            st.rerun()
                    else:
                        show_error("Could not generate questions for this topic. Try something mentioned in your uploads.")
                else:
                    show_error(result["message"])
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.quiz_active:
        q_idx = st.session_state.quiz_index
        questions = st.session_state.quiz_data
        total_q = len(questions)
        q = questions[q_idx]

        # Progress
        progress_pct = (q_idx) / total_q
        st.markdown(f'<div style="color:#94a3b8;font-size:12px;margin-bottom:5px;">Question {q_idx + 1} of {total_q}</div>', unsafe_allow_html=True)
        st.progress(progress_pct)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:18px;font-weight:700;color:#c4b5fd;margin-bottom:20px;">{q["question"]}</div>', unsafe_allow_html=True)

        options = q.get("options", [])
        selected = st.radio("Choose the correct answer:", options, key=f"q_{q_idx}", index=None)

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Submit Answer", use_container_width=True, disabled=st.session_state.quiz_feedback is not None):
                if selected:
                    selected_letter = selected[0] if selected else ""
                    correct_letter = q["answer"]
                    
                    if selected_letter == correct_letter:
                        st.session_state.quiz_feedback = {"type": "success", "msg": "Correct! Excellent work."}
                        st.session_state.quiz_score += 1
                    else:
                        st.session_state.quiz_feedback = {"type": "error", "msg": f"Actually, the correct answer was {correct_letter}."}
                    st.rerun()
                else:
                    st.warning("Please select an option first.")

        if st.session_state.quiz_feedback:
            if st.session_state.quiz_feedback["type"] == "success":
                show_success(st.session_state.quiz_feedback["msg"])
            else:
                show_error(st.session_state.quiz_feedback["msg"])
            
            if q.get("hint"):
                st.info(f"💡 {q['hint']}")

            with col2:
                if q_idx + 1 < total_q:
                    if st.button("Next Question →", use_container_width=True):
                        st.session_state.quiz_index += 1
                        st.session_state.quiz_feedback = None
                        st.rerun()
                else:
                    if st.button("Finish Quiz 🏁", use_container_width=True):
                        st.session_state.quiz_active = False
                        st.session_state.quiz_finished = True
                        st.session_state.quiz_feedback = None
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.quiz_finished:
        st.markdown('<div class="glass-card" style="text-align:center;padding:40px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:60px;">🏆</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-title">Quiz Completed!</div>', unsafe_allow_html=True)
        
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_data)
        pct = (score / total) * 100 if total > 0 else 0
        
        st.markdown(f"""
        <div style="margin:20px 0;">
            <div style="font-size:48px;font-weight:800;color:#c4b5fd;">{score} / {total}</div>
            <div style="font-size:18px;color:#94a3b8;">Your Score: {pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

        if pct >= 80:
            show_success("Amazing! You have mastered this topic.")
        elif pct >= 50:
            show_info("Good job! A bit more review and you'll be an expert.")
        else:
            show_error("Keep studying! Try reviewing the documents again.")

        if st.button("🔄 Restart Quiz", use_container_width=True):
            st.session_state.quiz_finished = False
            st.session_state.quiz_active = False
            st.session_state.quiz_data = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE 4 — RESULTS VISUALIZATION
# ─────────────────────────────────────────────────────────────────

def page_results():
    page_header("📊 Results", "Visualize AI Tutor responses and analytics.")

    # Last response card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section("🔍 Latest API Response")

    if st.session_state.last_response:
        st.markdown(f'<div class="response-card">{st.session_state.last_response}</div>', unsafe_allow_html=True)
    elif st.session_state.messages:
        # Show last assistant message
        last_bot = [m for m in st.session_state.messages if m["role"] == "assistant"]
        if last_bot:
            st.markdown(f'<div class="response-card">🤖 {last_bot[-1]["content"]}</div>', unsafe_allow_html=True)
        else:
            show_info("No assistant responses yet. Start chatting!")
    else:
        show_info("No responses yet. Use the Chat Interface to get started.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics row
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("📨 Total Queries", st.session_state.stats["queries_sent"], delta="+1 today")
    with col_b:
        st.metric("💬 Messages", len(st.session_state.messages), delta=None)
    with col_c:
        st.metric("📂 Files Processed", st.session_state.stats["files_uploaded"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history export
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("💾 Conversation History")

        if st.session_state.messages:
            history_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="⬇️ Export Chat as JSON",
                data=history_json,
                file_name=f"ai_tutor_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="export_json",
                use_container_width=True,
            )
            # Preview
            st.markdown("<br>", unsafe_allow_html=True)
            for msg in st.session_state.messages[-6:]:
                role_color = "#818cf8" if msg["role"] == "user" else "#6ee7b7"
                role_label = "You" if msg["role"] == "user" else "AI"
                st.markdown(f"""
                <div style="padding:8px 14px;margin-bottom:6px;
                            border-left:3px solid {role_color};
                            background:rgba(255,255,255,0.04);
                            border-radius:0 8px 8px 0;">
                    <span style="color:{role_color};font-size:11px;font-weight:700;text-transform:uppercase;">{role_label}</span>
                    <div style="color:#e2e8f0;font-size:13px;margin-top:3px;">{msg["content"][:120]}{"…" if len(msg["content"]) > 120 else ""}</div>
                </div>""", unsafe_allow_html=True)
        else:
            show_info("No conversation history yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("📈 Session Statistics")

        total = len(st.session_state.messages)
        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        bot_count = total - user_count

        stats_data = [
            ("🙍 User messages", user_count, "#818cf8"),
            ("🤖 AI responses", bot_count, "#c4b5fd"),
            ("📂 Files uploaded", st.session_state.stats["files_uploaded"], "#6ee7b7"),
            ("🔁 API calls", st.session_state.stats["queries_sent"], "#f0abfc"),
        ]

        for label, count, color in stats_data:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:#94a3b8;font-size:13px;">{label}</span>
                <span style="color:{color};font-weight:700;font-size:16px;">{count}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️ Clear All Data", key="clear_all", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.session_state.stats = {"queries_sent": 0, "files_uploaded": 0, "sessions": st.session_state.stats["sessions"]}
            show_success("All session data cleared.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE 5 — SETTINGS
# ─────────────────────────────────────────────────────────────────

def page_settings():
    page_header("⚙️ Settings", "Configure the AI Tutor platform.")

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🔌 API Configuration")

        new_url = st.text_input(
            "Backend URL",
            value=st.session_state.settings["api_url"],
            placeholder="http://localhost:8001",
            key="settings_url",
        )
        new_model = st.selectbox(
            "AI Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "claude-3-opus", "gemini-pro"],
            index=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "claude-3-opus", "gemini-pro"].index(
                st.session_state.settings["model"]
            ),
            key="settings_model",
        )
        new_temp = st.slider(
            "Temperature (creativity)",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.settings["temperature"],
            step=0.05,
            key="settings_temp",
        )

        if st.button("💾 Save API Settings", key="save_api", use_container_width=True):
            st.session_state.settings["api_url"] = new_url
            st.session_state.settings["model"] = new_model
            st.session_state.settings["temperature"] = new_temp
            show_success("API settings saved successfully!")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🎨 Display Preferences")

        new_auto_scroll = st.checkbox("Auto-scroll chat to bottom", value=st.session_state.settings["auto_scroll"], key="s_scroll")
        new_typing = st.checkbox("Show typing animation", value=st.session_state.settings["typing_animation"], key="s_typing")

        if st.button("💾 Save Display Settings", key="save_display", use_container_width=True):
            st.session_state.settings["auto_scroll"] = new_auto_scroll
            st.session_state.settings["typing_animation"] = new_typing
            show_success("Display settings saved!")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("📋 Current Configuration")

        cfg_items = [
            ("Backend URL", st.session_state.settings["api_url"]),
            ("Model", st.session_state.settings["model"]),
            ("Temperature", str(st.session_state.settings["temperature"])),
            ("Auto-scroll", "Yes" if st.session_state.settings["auto_scroll"] else "No"),
            ("Typing animation", "Yes" if st.session_state.settings["typing_animation"] else "No"),
        ]

        for key, val in cfg_items:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:9px 0;
                        border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:#64748b;font-size:13px;">{key}</span>
                <span style="color:#c4b5fd;font-size:13px;font-weight:600;">{val}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("🧪 API Test")

        test_payload = st.text_input("Test input", value="Hello, can you hear me?", key="test_input")
        if st.button("🚀 Send Test Request", key="test_api", use_container_width=True):
            with st.spinner("Sending test request..."):
                result = call_backend_api(test_payload)
            if result["status"] == "success":
                show_success("API is responding correctly!")
                st.json(result["data"])
            else:
                show_error(result["message"])

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section("ℹ️ About")
        st.markdown("""
        <div style="color:#94a3b8;font-size:13px;line-height:1.8;">
            <div>🎓 <strong style="color:#c4b5fd;">AI Tutor Platform</strong></div>
            <div style="color:#64748b;margin-top:4px;">Version 1.0.0</div>
            <div style="margin-top:12px;">Frontend by <strong style="color:#818cf8;">Member 2</strong></div>
            <div>Backend by <strong style="color:#6ee7b7;">Member 1</strong></div>
            <div style="margin-top:12px;">Built with <strong style="color:#c4b5fd;">Streamlit</strong> + REST API</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ROUTER — Show the selected page
# ─────────────────────────────────────────────────────────────────

page = st.session_state.page

if page == "Home Dashboard":
    page_home()
elif page == "Upload Data":
    page_upload()
elif page == "Chat Interface":
    page_chat()
elif page == "Interactive Quiz":
    page_quiz()
elif page == "Results":
    page_results()
elif page == "Settings":
    page_settings()


# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer">🎓 AI Tutor Platform &nbsp;•&nbsp; Powered by AI &nbsp;•&nbsp; Learn Smarter, Not Harder ✨</div>',
    unsafe_allow_html=True,
)