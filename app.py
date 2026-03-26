import streamlit as st
import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import uuid
from groq import Groq
from PIL import Image
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌿 PlantScan AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_site_logo() -> None:
    """
    Optional: show Thomas More logo if you add it to the project.
    Place one of these files:
    - assets/tomasmore-logo.png
    - assets/tomasmore-logo.jpg
    - assets/tomasmore-logo.webp
    """
    candidates = [
        Path("assets/tomasmore-logo.png"),
        Path("assets/tomasmore-logo.jpg"),
        Path("assets/tomasmore-logo.webp"),
    ]
    for p in candidates:
        if p.exists():
            st.sidebar.image(str(p), use_container_width=True)
            return


def render_falling_leaves() -> None:
    st.markdown(
        """
        <div class="leaf-layer" aria-hidden="true">
          <span class="leaf-item l1">🍃</span>
          <span class="leaf-item l2">🍃</span>
          <span class="leaf-item l3">🍂</span>
          <span class="leaf-item l4">🍃</span>
          <span class="leaf-item l5">🍂</span>
          <span class="leaf-item l6">🍃</span>
          <span class="leaf-item l7">🍂</span>
          <span class="leaf-item l8">🍃</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── CSS + Falling Leaves (all inline) ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --green-deep:  #1b4332;
  --green-mid:   #2d6a4f;
  --green-light: #52b788;
  --green-pale:  #b7e4c7;
  --card-bg:     rgba(255,255,255,0.84);
  --shadow:      0 8px 32px rgba(27,67,50,0.18);
}
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  color: #111111 !important;
}
.stApp p,
.stApp li,
.stApp span,
.stApp label,
.stApp small,
.stApp div[data-testid="stMarkdownContainer"],
.stApp div[data-testid="stMarkdownContainer"] * {
  color: #111111 !important;
}
.stApp {
  background: #ffffff !important;
  min-height: 100vh;
  overflow-x: hidden;
}
/* falling leaves (works without JS) */
.leaf-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;
}
.leaf-item {
  position: fixed;
  top: -12vh;
  z-index: 2;
  pointer-events: none;
  font-size: 1.6rem;
  opacity: 0.85;
  animation-name: leafFall, leafSway;
  animation-timing-function: linear, ease-in-out;
  animation-iteration-count: infinite, infinite;
  animation-direction: normal, alternate;
}
@keyframes leafFall {
  0%   { transform: translateY(0) rotate(0deg); opacity: 0.85; }
  100% { transform: translateY(120vh) rotate(360deg); opacity: 0.95; }
}
@keyframes leafSway {
  0%   { margin-left: -10px; }
  100% { margin-left: 26px; }
}
.l1 { left: 6%;  animation-duration: 11s, 3.1s; animation-delay: 0s, 0s; }
.l2 { left: 17%; animation-duration: 14s, 2.8s; animation-delay: 1.1s, 0.3s; }
.l3 { left: 29%; animation-duration: 12s, 3.2s; animation-delay: 2.2s, 0.8s; }
.l4 { left: 41%; animation-duration: 15s, 2.9s; animation-delay: 0.8s, 0.2s; }
.l5 { left: 55%; animation-duration: 13s, 3.0s; animation-delay: 1.9s, 0.5s; }
.l6 { left: 69%; animation-duration: 16s, 3.3s; animation-delay: 2.9s, 0.7s; }
.l7 { left: 82%; animation-duration: 12.5s, 2.7s; animation-delay: 0.5s, 0.4s; }
.l8 { left: 93%; animation-duration: 14.5s, 3.1s; animation-delay: 1.6s, 0.6s; }
.main-title {
  font-family: 'Playfair Display', serif !important;
  font-size: 2.8rem !important;
  color: #111111 !important;
  text-align: center;
  margin-bottom: 0 !important;
  text-shadow: none;
  position: relative; z-index: 3;
}
.sub-title {
  text-align: center;
  font-size: 1rem;
  color: #111111 !important;
  margin-bottom: 1.8rem;
  position: relative; z-index: 3;
}
.upload-wrapper {
  max-width: 460px;
  margin: 0 auto 1.4rem auto;
  position: relative; z-index: 3;
}
.upload-wrapper [data-testid="stFileUploader"] {
  background: var(--card-bg) !important;
  border: 2px dashed #52b788 !important;
  border-radius: 14px !important;
  padding: 0.6rem 1rem !important;
  backdrop-filter: blur(6px);
  box-shadow: var(--shadow);
}
.upload-wrapper [data-testid="stFileUploader"] section { padding: 0.5rem !important; }
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
  color: #fff !important; border: none !important;
  border-radius: 12px !important; font-size: 1rem !important;
  font-weight: 600 !important; padding: 0.65rem 1.4rem !important;
  box-shadow: 0 4px 18px rgba(27,67,50,0.3) !important;
  transition: transform .15s, box-shadow .15s !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(27,67,50,0.4) !important;
}
.section-card {
  background: var(--card-bg); border-radius: 18px;
  padding: 1.2rem 1rem 0.8rem; box-shadow: var(--shadow);
  backdrop-filter: blur(8px); border: 1px solid rgba(178,220,194,0.55);
  text-align: center; margin-bottom: 1rem; color: #111111 !important;
  position: relative; z-index: 1;
}
.section-card * { color: #111111 !important; }
.section-icon  { font-size: 2rem; margin-bottom: 0.25rem; }
.section-header {
  font-family: 'Playfair Display', serif; font-size: 1.1rem;
  color: #111111; font-weight: 700; margin-bottom: 0.55rem;
}
.status-pill {
  display: inline-block; color: #fff; border-radius: 999px;
  padding: 0.22rem 1rem; font-weight: 600; font-size: 0.9rem;
  margin-bottom: 0.45rem; box-shadow: 0 2px 8px rgba(0,0,0,0.14);
}
.mini-badge {
  display: inline-block; background: rgba(82,183,136,0.16);
  border: 1px solid #b7e4c7; border-radius: 8px;
  padding: 0.18rem 0.65rem; font-size: 0.82rem;
  color: #111111; margin: 0.22rem 0.08rem;
}
.fun-fact {
  background: linear-gradient(120deg, #d8f3dc, #b7e4c7);
  border-left: 5px solid #2d6a4f; border-radius: 12px;
  padding: 0.85rem 1.2rem; margin-top: 1.4rem;
  font-size: 0.95rem; color: #111111;
  box-shadow: 0 3px 12px rgba(27,67,50,0.1);
  position: relative; z-index: 3;
}
.plant-name {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.85rem !important; color: #111111 !important; margin-bottom: 0 !important;
}
.confidence { color: #111111 !important; font-size: 0.88rem; margin-bottom: 0.7rem; }
.badge {
  display: inline-block; padding: 0.18rem 0.7rem;
  border-radius: 999px; color: #fff; font-size: 0.8rem; margin-bottom: 0.25rem;
}
.status-pill,
.status-pill *,
.badge,
.badge * {
  color: #ffffff !important;
}
/* Keep generated result text in section columns readable on white background */
div[data-testid="column"] p,
div[data-testid="column"] li,
div[data-testid="column"] blockquote,
div[data-testid="column"] label,
div[data-testid="column"] [data-testid="stMarkdownContainer"] {
  color: #111111 !important;
}
section[data-testid="stSidebar"] {
  background: #ffffff !important;
  border-right: 1px solid rgba(45,106,79,0.12) !important;
}
/* Sidebar expand/collapse arrow button */
button[kind="header"][aria-label*="sidebar"],
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
div[data-testid="stSidebarCollapsedControl"] button {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
button[kind="header"][aria-label*="sidebar"] svg,
button[data-testid="collapsedControl"] svg,
button[data-testid="baseButton-headerNoPadding"] svg,
div[data-testid="stSidebarCollapsedControl"] button svg {
  fill: #ffffff !important;
  stroke: #ffffff !important;
  color: #ffffff !important;
}
button[kind="header"][aria-label*="sidebar"] svg *,
button[data-testid="collapsedControl"] svg *,
button[data-testid="baseButton-headerNoPadding"] svg *,
div[data-testid="stSidebarCollapsedControl"] button svg * {
  fill: #ffffff !important;
  stroke: #ffffff !important;
  color: #ffffff !important;
}
.sidebar-title {
  font-family: 'Playfair Display', serif; font-size: 1.15rem;
  color: #111111; font-weight: 700; margin-bottom: 0.7rem;
  padding-bottom: 0.35rem; border-bottom: 2px solid #b7e4c7;
}
[data-testid="stExpander"] {
  background: rgba(255,255,255,0.72) !important;
  border-radius: 10px !important; border: 1px solid #b7e4c7 !important;
  margin-bottom: 0.45rem !important;
}
hr { border-color: #b7e4c7 !important; margin: 1.4rem 0 !important; }
.block-container { position: relative !important; z-index: 3 !important; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_ID = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
DATA_DIR = Path(os.getenv("PLANTSCAN_DATA_DIR", "data"))
HISTORY_FILE = DATA_DIR / "history.json"
MAX_HISTORY_ITEMS = int(os.getenv("PLANTSCAN_MAX_HISTORY", "100"))


def get_api_key() -> str:
    key = ""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")  # type: ignore[attr-defined]
    except Exception:
        key = ""
    if not key:
        key = os.getenv("GROQ_API_KEY", "")
    return key.strip()


@st.cache_resource
def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> List[Dict[str, Any]]:
    ensure_data_dir()
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    ensure_data_dir()
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history[:MAX_HISTORY_ITEMS], f, ensure_ascii=False, indent=2)


def add_to_history(plant_name: str, result: Dict[str, Any], image_b64: str) -> None:
    history = load_history()
    history.insert(
        0,
        {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "plant_name": plant_name,
            "result": result,
            "image": image_b64,
        },
    )
    save_history(history)


def image_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def extract_json_object(text: str) -> str:
    """
    Try hard to extract a single JSON object from model output.
    Handles fenced code blocks and extra leading/trailing text.
    """
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1]
    return t


def analyse_plant(client: Groq, b64: str) -> Dict[str, Any]:
    prompt = (
        "You are an expert botanist and garden advisor. "
        "Analyse the plant in this image and respond ONLY with valid JSON "
        "(no markdown, no extra text) using exactly this structure:\n"
        '{\n'
        '  "plant_name": "Common name (Scientific name)",\n'
        '  "confidence": "High / Medium / Low",\n'
        '  "description": "2-3 sentence overview.",\n'
        '  "health_status": "Healthy / Stressed / Diseased / Unknown",\n'
        '  "health_tips": ["Tip 1","Tip 2","Tip 3"],\n'
        '  "garden_suitability": "Excellent / Good / Fair / Poor",\n'
        '  "garden_notes": "2-3 sentences about garden value.",\n'
        '  "invasive_risk": "None / Low / Medium / High",\n'
        '  "bee_impact": "Positive / Neutral / Negative",\n'
        '  "bee_details": "2-3 sentences about pollinator interaction.",\n'
        '  "bloom_season": "Spring / Summer / Autumn / Winter / Year-round / N/A",\n'
        '  "fun_fact": "One interesting fact."\n'
        '}'
    )
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role":"user","content":[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}},
        ]}],
        max_tokens=1024, temperature=0.3,
    )
    raw = (resp.choices[0].message.content or "").strip()
    extracted = extract_json_object(raw)
    try:
        parsed = json.loads(extracted)
    except json.JSONDecodeError as ex:
        raise ValueError(f"Model returned invalid JSON: {ex}") from ex
    if not isinstance(parsed, dict):
        raise ValueError("Model JSON must be an object.")
    return parsed

STATUS_COLOR = {"Healthy":"#4caf50","Stressed":"#ff9800","Diseased":"#f44336","Unknown":"#9e9e9e"}
IMPACT_COLOR = {"Positive":"#4caf50","Neutral":"#2196f3","Negative":"#f44336"}
SUIT_COLOR   = {"Excellent":"#4caf50","Good":"#8bc34a","Fair":"#ff9800","Poor":"#f44336"}


def badge(label: str, value: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{label}: <strong>{value}</strong></span>'

# ── Groq client init ──────────────────────────────────────────────────────────
API_KEY = get_api_key()
if not API_KEY:
    st.error(
        "⚠️ `GROQ_API_KEY` not found. Add it to Streamlit secrets (recommended for Cloud) "
        "or set it as an environment variable."
    )
    st.stop()
client = get_groq_client(API_KEY)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_site_logo()
    st.markdown('<div class="sidebar-title">📜 Scan History</div>', unsafe_allow_html=True)
    sq = st.text_input("🔍 Search history", placeholder="e.g. Rose, Oak…")
    history = load_history()
    sq_norm = (sq or "").strip().lower()
    if sq_norm:
        filtered = [
            h
            for h in history
            if sq_norm in str(h.get("plant_name", "")).lower()
            or sq_norm in str(h.get("timestamp", "")).lower()
        ]
    else:
        filtered = history

    if not filtered:
        st.info("No scans yet – upload a plant photo!")
    else:
        for e in filtered[:30]:
            with st.expander(f"🌱 {e['plant_name']}  ·  {e['timestamp']}"):
                if e.get("image"):
                    st.image(base64.b64decode(e["image"]), width=120)
                r = e.get("result", {}) or {}
                if isinstance(r, dict):
                    hcol = STATUS_COLOR.get(r.get("health_status", "Unknown"), "#9e9e9e")
                    st.markdown(
                        badge("Health", str(r.get("health_status", "?")), hcol),
                        unsafe_allow_html=True,
                    )
                    desc = str(r.get("description", ""))
                    st.caption((desc[:120] + "…") if len(desc) > 120 else desc)
                else:
                    st.caption("History entry is corrupted (result is not a JSON object).")

    with st.expander("⚙️ History tools", expanded=False):
        st.caption("On Streamlit Cloud, files are not guaranteed to persist across restarts.")
        st.download_button(
            "⬇️ Download history.json",
            data=json.dumps(history, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="history.json",
            mime="application/json",
            use_container_width=True,
        )

# ── Main ──────────────────────────────────────────────────────────────────────
render_falling_leaves()
st.markdown('<h1 class="main-title">🌿 PlantScan AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload a photo of any plant and get an instant expert analysis</p>', unsafe_allow_html=True)

st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
uploaded = st.file_uploader("Drop or click to upload a plant photo", type=["jpg","jpeg","png","webp"], label_visibility="visible")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col_img, col_btn = st.columns([1,2])
    with col_img:
        st.image(img, width=210, caption="Your plant")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        scan_btn = st.button("🔬 Scan Plant", use_container_width=True, type="primary")

    if scan_btn:
        with st.spinner("Analysing your plant… 🌱"):
            b64 = image_to_b64(img)
            try:
                result = analyse_plant(client, b64)
            except Exception as ex:
                st.error(f"Analysis failed: {ex}")
                st.stop()

        add_to_history(result.get("plant_name","Unknown"), result, b64)
        # Trigger celebration immediately after a successful analysis.
        st.balloons()

        st.markdown("---")
        st.markdown(f'<h2 class="plant-name">🌿 {result.get("plant_name","Unknown plant")}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p class="confidence">Identification confidence: <strong>{result.get("confidence","?")}</strong></p>', unsafe_allow_html=True)
        st.markdown(f'> {result.get("description","")}')

        c1, c2, c3 = st.columns(3, gap="medium")

        with c1:
            health = result.get("health_status","Unknown")
            hcol = STATUS_COLOR.get(health,"#9e9e9e")
            st.markdown(f'<div class="section-card"><div class="section-icon">🩺</div><div class="section-header">Plant Health</div><div class="status-pill" style="background:{hcol}">{health}</div></div>', unsafe_allow_html=True)
            for t in result.get("health_tips",[]):
                st.markdown(f"- {t}")

        with c2:
            suit = result.get("garden_suitability","?")
            scol = SUIT_COLOR.get(suit,"#9e9e9e")
            st.markdown(f'<div class="section-card"><div class="section-icon">🌻</div><div class="section-header">Garden Profile</div><div class="status-pill" style="background:{scol}">Suitability: {suit}</div></div>', unsafe_allow_html=True)
            st.markdown(result.get("garden_notes",""))
            st.markdown(f'<div class="mini-badge">⚠️ Invasive risk: {result.get("invasive_risk","?")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="mini-badge">🌸 Bloom: {result.get("bloom_season","?")}</div>', unsafe_allow_html=True)

        with c3:
            bee = result.get("bee_impact","?")
            bcol = IMPACT_COLOR.get(bee,"#9e9e9e")
            st.markdown(f'<div class="section-card"><div class="section-icon">🐝</div><div class="section-header">Bee & Pollinator Impact</div><div class="status-pill" style="background:{bcol}">{bee}</div></div>', unsafe_allow_html=True)
            st.markdown(result.get("bee_details",""))

        if result.get("fun_fact"):
            st.markdown(f'<div class="fun-fact">💡 <strong>Fun fact:</strong> {result["fun_fact"]}</div>', unsafe_allow_html=True)
