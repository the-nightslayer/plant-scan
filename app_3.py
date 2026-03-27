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
import streamlit.components.v1 as components

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌿 PlantScan AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

def render_site_logo() -> None:
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
          <span class="leaf-item l2">🌿</span>
          <span class="leaf-item l3">🍂</span>
          <span class="leaf-item l4">🍃</span>
          <span class="leaf-item l5">🍂</span>
          <span class="leaf-item l6">🌱</span>
          <span class="leaf-item l7">🍂</span>
          <span class="leaf-item l8">🍃</span>
          <span class="leaf-item l9">🌿</span>
          <span class="leaf-item l10">🍃</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_leaf_confetti() -> None:
    """
    Renders a full-screen leaf confetti burst using st.components.v1.html,
    which reliably executes JavaScript in Streamlit (unlike st.markdown scripts).
    The iframe is sized to 0px so it takes no visual space.
    """
    confetti_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; }
  body { overflow: hidden; background: transparent; }
  .leaf {
    position: fixed;
    top: -60px;
    font-size: 1.8rem;
    pointer-events: none;
    animation: leafDrop linear forwards;
    z-index: 99999;
  }
  @keyframes leafDrop {
    0%   { opacity: 1;   transform: translateY(0px)    translateX(0px)   rotate(0deg);   }
    80%  { opacity: 1; }
    100% { opacity: 0;   transform: translateY(105vh)  translateX(var(--sway)) rotate(720deg); }
  }
</style>
</head>
<body>
<script>
  (function () {
    const emojis = ['🍃','🌿','🍂','🌱','🍀'];
    const count  = 90;

    for (let i = 0; i < count; i++) {
      const el       = document.createElement('div');
      el.className   = 'leaf';
      el.textContent = emojis[Math.floor(Math.random() * emojis.length)];

      const left     = Math.random() * 100;
      const size     = 1.2 + Math.random() * 1.8;
      const duration = 3.5 + Math.random() * 4;
      const delay    = Math.random() * 2.5;
      const sway     = (Math.random() * 180 - 90).toFixed(0) + 'px';

      el.style.cssText = `
        left: ${left}vw;
        font-size: ${size}rem;
        --sway: ${sway};
        animation-name: leafDrop;
        animation-duration: ${duration}s;
        animation-delay: ${delay}s;
      `;
      document.body.appendChild(el);
    }

    // Clean up after all animations finish
    setTimeout(() => document.body.innerHTML = '', 9000);
  })();
</script>
</body>
</html>
"""
    # height=0 hides the iframe visually; the fixed-position leaves escape the iframe
    # in most browsers when allow="same-origin" is set via srcdoc rendering.
    # We use a generous height so the confetti iframe JS actually runs.
    components.html(confetti_html, height=0, scrolling=False)


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --green-deep:  #1b4332;
  --green-mid:   #2d6a4f;
  --green-light: #52b788;
  --green-pale:  #b7e4c7;
  --bark:        #8b5e3c;
  --soil:        #5c3d2e;
  --moss:        #6a994e;
  --card-bg:     rgba(255,252,245,0.90);
  --shadow:      0 8px 32px rgba(27,67,50,0.18);
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  color: #111111 !important;
}

.stApp {
  background-color: #dff0d8 !important;
  background-image:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='340' viewBox='0 0 1200 340'%3E%3Cdefs%3E%3ClinearGradient id='sky' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0' stop-color='%23c8eac0'/%3E%3Cstop offset='1' stop-color='%23dff0d8'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1200' height='340' fill='url(%23sky)'/%3E%3Cellipse cx='60' cy='310' rx='28' ry='80' fill='%23b2d8a0' opacity='0.4'/%3E%3Cellipse cx='60' cy='230' rx='22' ry='55' fill='%23a0c890' opacity='0.4'/%3E%3Cellipse cx='150' cy='310' rx='30' ry='90' fill='%23a8d498' opacity='0.38'/%3E%3Cellipse cx='150' cy='215' rx='24' ry='60' fill='%2398c088' opacity='0.38'/%3E%3Cellipse cx='260' cy='310' rx='26' ry='78' fill='%23b8dca8' opacity='0.40'/%3E%3Cellipse cx='260' cy='226' rx='20' ry='54' fill='%23a8cc98' opacity='0.40'/%3E%3Cellipse cx='370' cy='310' rx='32' ry='95' fill='%23a0cc90' opacity='0.36'/%3E%3Cellipse cx='370' cy='208' rx='26' ry='65' fill='%2390bc80' opacity='0.36'/%3E%3Cellipse cx='490' cy='310' rx='28' ry='84' fill='%23b0d8a0' opacity='0.38'/%3E%3Cellipse cx='490' cy='220' rx='22' ry='58' fill='%23a0c890' opacity='0.38'/%3E%3Cellipse cx='600' cy='310' rx='30' ry='88' fill='%23a8d098' opacity='0.36'/%3E%3Cellipse cx='600' cy='215' rx='24' ry='62' fill='%2398c088' opacity='0.36'/%3E%3Cellipse cx='710' cy='310' rx='26' ry='80' fill='%23b4dca4' opacity='0.38'/%3E%3Cellipse cx='710' cy='223' rx='20' ry='54' fill='%23a4cc94' opacity='0.38'/%3E%3Cellipse cx='820' cy='310' rx='34' ry='98' fill='%239ec88e' opacity='0.36'/%3E%3Cellipse cx='820' cy='205' rx='27' ry='68' fill='%238eb87e' opacity='0.36'/%3E%3Cellipse cx='930' cy='310' rx='28' ry='86' fill='%23acd49c' opacity='0.38'/%3E%3Cellipse cx='930' cy='218' rx='22' ry='56' fill='%239cc48c' opacity='0.38'/%3E%3Cellipse cx='1040' cy='310' rx='30' ry='90' fill='%23b0d8a0' opacity='0.36'/%3E%3Cellipse cx='1040' cy='212' rx='24' ry='63' fill='%23a0c890' opacity='0.36'/%3E%3Cellipse cx='1140' cy='310' rx='28' ry='82' fill='%23a8d098' opacity='0.40'/%3E%3Cellipse cx='1140' cy='222' rx='20' ry='54' fill='%2398c088' opacity='0.40'/%3E%3Crect x='18' y='190' width='14' height='150' fill='%23795548' opacity='0.65'/%3E%3Cellipse cx='25' cy='188' rx='40' ry='80' fill='%232d6a4f' opacity='0.72'/%3E%3Cellipse cx='8' cy='168' rx='28' ry='56' fill='%23388e5a' opacity='0.62'/%3E%3Cellipse cx='44' cy='174' rx='26' ry='50' fill='%23256044' opacity='0.58'/%3E%3Crect x='108' y='220' width='12' height='120' fill='%236d4c41' opacity='0.62'/%3E%3Cellipse cx='114' cy='218' rx='34' ry='68' fill='%231b5e3b' opacity='0.68'/%3E%3Cellipse cx='98' cy='200' rx='24' ry='48' fill='%23317a50' opacity='0.60'/%3E%3Cellipse cx='132' cy='207' rx='22' ry='45' fill='%23215535' opacity='0.55'/%3E%3Crect x='1168' y='185' width='14' height='155' fill='%23795548' opacity='0.65'/%3E%3Cellipse cx='1175' cy='183' rx='40' ry='80' fill='%232d6a4f' opacity='0.72'/%3E%3Cellipse cx='1157' cy='163' rx='28' ry='56' fill='%23388e5a' opacity='0.62'/%3E%3Cellipse cx='1194' cy='170' rx='26' ry='50' fill='%23256044' opacity='0.58'/%3E%3Crect x='1075' y='215' width='12' height='125' fill='%236d4c41' opacity='0.62'/%3E%3Cellipse cx='1081' cy='212' rx='34' ry='68' fill='%231b5e3b' opacity='0.68'/%3E%3Cellipse cx='1064' cy='194' rx='24' ry='48' fill='%23317a50' opacity='0.60'/%3E%3Cellipse cx='1098' cy='202' rx='22' ry='45' fill='%23215535' opacity='0.55'/%3E%3Crect x='0' y='305' width='1200' height='35' fill='%2352b788' opacity='0.25'/%3E%3C/svg%3E") !important;
  background-repeat: repeat-x !important;
  background-position: bottom !important;
  background-size: 1200px 340px !important;
  min-height: 100vh;
  overflow-x: hidden;
}

.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 5px;
  background: linear-gradient(90deg,
    #1b4332 0%, #2d6a4f 20%, #52b788 40%,
    #6a994e 60%, #2d6a4f 80%, #1b4332 100%);
  z-index: 9999;
}

.leaf-layer {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 2; overflow: hidden;
}
.leaf-item {
  position: fixed; top: -12vh; z-index: 2;
  pointer-events: none; font-size: 1.5rem; opacity: 0.80;
  animation-name: leafFall, leafSway;
  animation-timing-function: linear, ease-in-out;
  animation-iteration-count: infinite, infinite;
  animation-direction: normal, alternate;
  filter: drop-shadow(0 2px 4px rgba(27,67,50,0.2));
}
@keyframes leafFall {
  0%   { transform: translateY(0)     rotate(0deg);   opacity: 0.80; }
  100% { transform: translateY(120vh) rotate(360deg); opacity: 0.90; }
}
@keyframes leafSway {
  0%   { margin-left: -12px; }
  100% { margin-left:  28px; }
}
.l1  { left:  5%; animation-duration: 11s,  3.1s; animation-delay: 0s,    0s;    }
.l2  { left: 13%; animation-duration: 14s,  2.8s; animation-delay: 1.0s,  0.3s;  }
.l3  { left: 22%; animation-duration: 12s,  3.2s; animation-delay: 2.1s,  0.8s;  }
.l4  { left: 33%; animation-duration: 15s,  2.9s; animation-delay: 0.7s,  0.2s;  }
.l5  { left: 45%; animation-duration: 13s,  3.0s; animation-delay: 1.8s,  0.5s;  }
.l6  { left: 57%; animation-duration: 16s,  3.3s; animation-delay: 2.8s,  0.7s;  }
.l7  { left: 68%; animation-duration: 12.5s,2.7s; animation-delay: 0.4s,  0.4s;  }
.l8  { left: 78%; animation-duration: 14.5s,3.1s; animation-delay: 1.5s,  0.6s;  }
.l9  { left: 87%; animation-duration: 11.5s,2.9s; animation-delay: 3.2s,  0.9s;  }
.l10 { left: 95%; animation-duration: 13.5s,3.4s; animation-delay: 0.9s,  0.1s;  }

.main-title {
  font-family: 'Playfair Display', serif !important;
  font-size: 2.8rem !important;
  color: #1b4332 !important;
  text-align: center;
  margin-bottom: 0 !important;
  text-shadow: 0 2px 8px rgba(27,67,50,0.12);
  position: relative; z-index: 3;
}
.sub-title {
  text-align: center;
  font-size: 1rem;
  color: #2d6a4f !important;
  margin-bottom: 1.8rem;
  position: relative; z-index: 3;
  font-style: italic;
}

/* ── Cozy Upload zone ── */
.upload-wrapper {
  max-width: 500px;
  margin: 0 auto 2rem auto;
  position: relative; z-index: 3;
}
.upload-wrapper [data-testid="stFileUploader"] {
  background: linear-gradient(135deg,
    rgba(27,67,50,0.85) 0%,
    rgba(45,106,79,0.90) 100%) !important;
  border: 3px dashed #52b788 !important;
  border-radius: 24px !important;
  padding: 1.5rem !important;
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.1);
  transition: all 0.3s ease;
}
.upload-wrapper [data-testid="stFileUploader"]:hover {
  border-color: #b7e4c7 !important;
  transform: scale(1.01);
}

.upload-wrapper [data-testid="stFileUploader"] *,
.upload-wrapper [data-testid="stFileUploader"] p,
.upload-wrapper [data-testid="stFileUploader"] span,
.upload-wrapper [data-testid="stFileUploader"] small,
.upload-wrapper [data-testid="stFileUploader"] div,
.upload-wrapper [data-testid="stFileUploader"] label,
.upload-wrapper [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"],
.upload-wrapper [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] * {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}

.upload-wrapper [data-testid="stFileUploader"] svg {
  fill: #b7e4c7 !important;
  stroke: #b7e4c7 !important;
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
  color: #fff !important; border: none !important;
  border-radius: 12px !important; font-size: 1rem !important;
  font-weight: 600 !important; padding: 0.65rem 1.4rem !important;
  box-shadow: 0 4px 18px rgba(27,67,50,0.30) !important;
  transition: transform .15s, box-shadow .15s !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(27,67,50,0.40) !important;
}

.section-card {
  background: var(--card-bg);
  border-radius: 18px;
  padding: 1.2rem 1rem 0.8rem;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(178,220,194,0.65);
  text-align: center;
  margin-bottom: 1rem;
  color: #111111 !important;
  position: relative; z-index: 1;
  background-image: radial-gradient(ellipse at 90% 10%, rgba(82,183,136,0.08) 0%, transparent 60%);
}
.section-card * { color: #111111 !important; }

.section-icon   { font-size: 2rem;  margin-bottom: 0.25rem; }
.section-header {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem; color: #1b4332;
  font-weight: 700; margin-bottom: 0.55rem;
}

.status-pill {
  display: inline-block; color: #fff !important;
  border-radius: 999px; padding: 0.22rem 1rem;
  font-weight: 600; font-size: 0.9rem;
  margin-bottom: 0.45rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.14);
}

.mini-badge {
  display: inline-block;
  background: rgba(82,183,136,0.16);
  border: 1px solid #b7e4c7;
  border-radius: 8px;
  padding: 0.18rem 0.65rem;
  font-size: 0.82rem; color: #111111;
  margin: 0.22rem 0.08rem;
}

.fun-fact {
  background: linear-gradient(120deg, #d8f3dc, #b7e4c7);
  border-left: 5px solid #2d6a4f;
  border-radius: 12px;
  padding: 0.85rem 1.2rem;
  margin-top: 1.4rem;
  font-size: 0.95rem; color: #111111;
  box-shadow: 0 3px 12px rgba(27,67,50,0.10);
  position: relative; z-index: 3;
}

.plant-name {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.85rem !important;
  color: #1b4332 !important;
  margin-bottom: 0 !important;
}
.confidence { color: #2d6a4f !important; font-size: 0.88rem; margin-bottom: 0.7rem; }

.badge {
  display: inline-block; padding: 0.18rem 0.7rem;
  border-radius: 999px; color: #fff !important;
  font-size: 0.8rem; margin-bottom: 0.25rem;
}

/* ── Sidebar: force black text everywhere ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #f0f7ee 0%, #e8f5e9 100%) !important;
  border-right: 2px solid rgba(45,106,79,0.18) !important;
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] summary,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
  color: #111111 !important;
  -webkit-text-fill-color: #111111 !important;
}

/* Expander header text specifically */
section[data-testid="stSidebar"] details > summary,
section[data-testid="stSidebar"] details > summary *,
section[data-testid="stSidebar"] .streamlit-expanderHeader,
section[data-testid="stSidebar"] .streamlit-expanderHeader * {
  color: #111111 !important;
  -webkit-text-fill-color: #111111 !important;
}

/* st.caption inside sidebar */
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stCaption * {
  color: #444444 !important;
  -webkit-text-fill-color: #444444 !important;
}

/* st.info inside sidebar */
section[data-testid="stSidebar"] .stAlert,
section[data-testid="stSidebar"] .stAlert * {
  color: #111111 !important;
  -webkit-text-fill-color: #111111 !important;
}

.sidebar-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.15rem;
  color: #1b4332 !important;
  -webkit-text-fill-color: #1b4332 !important;
  font-weight: 700; margin-bottom: 0.7rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid #52b788;
}

.vine-divider {
  text-align: center;
  font-size: 1.4rem;
  margin: 0.2rem 0 1rem 0;
  letter-spacing: 0.4rem;
  opacity: 0.6;
  position: relative; z-index: 3;
}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_ID          = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
DATA_DIR          = Path(os.getenv("PLANTSCAN_DATA_DIR", "data"))
HISTORY_FILE      = DATA_DIR / "history.json"
MAX_HISTORY_ITEMS = int(os.getenv("PLANTSCAN_MAX_HISTORY", "100"))

def get_api_key() -> str:
    key = ""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
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
            "id":         str(uuid.uuid4()),
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M"),
            "plant_name": plant_name,
            "result":     result,
            "image":      image_b64,
        },
    )
    save_history(history)

def image_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()

def extract_json_object(text: str) -> str:
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    start = t.find("{")
    end   = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1]
    return t

def analyse_plant(client: Groq, b64: str) -> Dict[str, Any]:
    prompt = (
        "You are an expert botanist and garden advisor. "
        "Analyse the plant in this image and respond ONLY with valid JSON "
        "(no markdown, no extra text) using exactly this structure:\n"
        '{\n'
        ' "plant_name": "Common name (Scientific name)",\n'
        ' "confidence": "High / Medium / Low",\n'
        ' "description": "2-3 sentence overview.",\n'
        ' "health_status": "Healthy / Stressed / Diseased / Unknown",\n'
        ' "health_tips": ["Tip 1","Tip 2","Tip 3"],\n'
        ' "garden_suitability": "Excellent / Good / Fair / Poor",\n'
        ' "garden_notes": "2-3 sentences about garden value.",\n'
        ' "invasive_risk": "None / Low / Medium / High",\n'
        ' "bee_impact": "Positive / Neutral / Negative",\n'
        ' "bee_details": "2-3 sentences about pollinator interaction.",\n'
        ' "bloom_season": "Spring / Summer / Autumn / Winter / Year-round / N/A",\n'
        ' "fun_fact": "One interesting fact."\n'
        '}'
    )
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": [
            {"type": "text",      "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]}],
        max_tokens=1024, temperature=0.3,
    )
    raw       = (resp.choices[0].message.content or "").strip()
    extracted = extract_json_object(raw)
    parsed    = json.loads(extracted)
    return parsed

STATUS_COLOR = {"Healthy": "#4caf50", "Stressed": "#ff9800", "Diseased": "#f44336", "Unknown": "#9e9e9e"}
IMPACT_COLOR = {"Positive": "#4caf50", "Neutral":  "#2196f3", "Negative": "#f44336"}
SUIT_COLOR   = {"Excellent": "#4caf50", "Good": "#8bc34a",    "Fair": "#ff9800",     "Poor":  "#f44336"}

# ── API Check ─────────────────────────────────────────────────────────────────
API_KEY = get_api_key()
if not API_KEY:
    st.error("⚠️ `GROQ_API_KEY` not found.")
    st.stop()
client = get_groq_client(API_KEY)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_site_logo()
    st.markdown('<div class="sidebar-title">📜 Scan History</div>', unsafe_allow_html=True)
    history = load_history()
    if not history:
        st.info("No scans yet.")
    else:
        for e in history[:10]:
            with st.expander(f"🌱 {e['plant_name']}"):
                if e.get("image"):
                    st.image(base64.b64decode(e["image"]), width=120)
                st.caption(e["timestamp"])

# ── Main UI ───────────────────────────────────────────────────────────────────
render_falling_leaves()
st.markdown('<h1 class="main-title">🌿 PlantScan AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="vine-divider">🌿 ❧ 🌿</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert botanical analysis from a simple photo</p>', unsafe_allow_html=True)

# Centered cozy upload area
col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_mid:
    st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload a plant photo",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.image(img, use_container_width=True)
        scan_btn = st.button("🔬 Analyse Plant", use_container_width=True, type="primary")

    if scan_btn:
        with st.spinner("Identifying plant..."):
            b64    = image_to_b64(img)
            result = analyse_plant(client, b64)
            add_to_history(result.get("plant_name", "Unknown"), result, b64)

        # ── Leaf confetti via components.html (reliable JS execution) ──
        render_leaf_confetti()

        st.markdown("---")
        st.markdown(f'<h2 class="plant-name">🌿 {result.get("plant_name")}</h2>', unsafe_allow_html=True)
        st.write(result.get("description"))

        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            h = result.get("health_status")
            st.markdown(
                f'<div class="section-card">🩺<br><b>Health</b><br>'
                f'<div class="status-pill" style="background:{STATUS_COLOR.get(h, "#9e9e9e")}">{h}</div></div>',
                unsafe_allow_html=True,
            )
            for tip in result.get("health_tips", []):
                st.write(f"• {tip}")
        with res_c2:
            s = result.get("garden_suitability")
            st.markdown(
                f'<div class="section-card">🌻<br><b>Garden</b><br>'
                f'<div class="status-pill" style="background:{SUIT_COLOR.get(s, "#9e9e9e")}">{s}</div></div>',
                unsafe_allow_html=True,
            )
            st.caption(result.get("garden_notes"))
        with res_c3:
            b = result.get("bee_impact")
            st.markdown(
                f'<div class="section-card">🐝<br><b>Pollinators</b><br>'
                f'<div class="status-pill" style="background:{IMPACT_COLOR.get(b, "#9e9e9e")}">{b}</div></div>',
                unsafe_allow_html=True,
            )
            st.caption(result.get("bee_details"))

        if result.get("fun_fact"):
            st.markdown(
                f'<div class="fun-fact">💡 <b>Did you know?</b> {result["fun_fact"]}</div>',
                unsafe_allow_html=True,
            )
