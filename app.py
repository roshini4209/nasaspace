import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Avengers Lunar Outpost 3D",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
header[data-testid="stHeader"], footer, #MainMenu, section[data-testid="stSidebar"] {
    display: none !important;
}
.stApp {
    background: #020617 !important;
    overflow: hidden !important;
}
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
iframe {
    display: block !important;
    border: none !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_nasa_data():
    flr = {
        "id": "2024-05-14T16:46:00-FLR-001",
        "class": "X8.7",
        "peak": "2024-05-14T16:51Z",
        "source": "ARCHIVED NASA DONKI DATASET",
        "live": False
    }
    cme = {
        "id": "2024-05-14T17:12:00-CME-001",
        "speed": 1240,
        "source": "ARCHIVED NASA DONKI DATASET",
        "live": False
    }
    try:
        r1 = requests.get("https://api.nasa.gov/DONKI/FLR?api_key=DEMO_KEY", timeout=4)
        if r1.status_code == 200:
            arr = r1.json()
            if isinstance(arr, list) and len(arr) > 0:
                latest = arr[-1]
                flr = {
                    "id": latest.get("flrID", "LIVE-DONKI-FLR"),
                    "class": latest.get("classType", "M2.4"),
                    "peak": latest.get("peakTime", "Live Feed"),
                    "source": "LIVE NASA DONKI FLR API",
                    "live": True
                }
    except Exception:
        pass
    try:
        r2 = requests.get("https://api.nasa.gov/DONKI/CME?api_key=DEMO_KEY", timeout=4)
        if r2.status_code == 200:
            arr = r2.json()
            if isinstance(arr, list) and len(arr) > 0:
                latest = arr[-1]
                analyses = latest.get("cmeAnalyses") or []
                spd = analyses[0].get("speed", 780) if analyses else 780
                cme = {
                    "id": latest.get("activityID", "LIVE-DONKI-CME"),
                    "speed": int(spd) if spd else 780,
                    "source": "LIVE NASA DONKI CME API",
                    "live": True
                }
    except Exception:
        pass
    return {"flr": flr, "cme": cme}

nasa_payload = fetch_nasa_data()

APP_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; font-family: 'Segoe UI', system-ui, sans-serif; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #020617; color: #f8fafc; }

  #app-shell { position: relative; width: 100%; height: 860px; overflow: hidden; background: #020617; }
  #bg-space-canvas { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }

  .screen {
    position: absolute; inset: 0; z-index: 10;
    display: none; flex-direction: column; align-items: center; justify-content: center;
    padding: 20px; overflow-y: auto;
  }
  .screen.active { display: flex; }

  .glass-panel {
    background: rgba(9, 13, 31, 0.88);
    backdrop-filter: blur(12px);
    border: 2.5px solid #eab308;
    border-radius: 22px;
    box-shadow: 0 0 45px rgba(56, 189, 248, 0.25), 0 18px 40px rgba(0, 0, 0, 0.8);
  }

  #screen-loader { text-align: center; }
  .loader-wrap {
    width: 680px; max-width: 94%; padding: 34px 36px;
    background: rgba(9, 13, 31, 0.86);
    border: 2.5px solid #38bdf8;
    border-radius: 24px;
    box-shadow: 0 0 60px rgba(56, 189, 248, 0.3);
  }
  .orbit-ring {
    width: 96px; height: 96px; margin: 0 auto 16px auto;
    border-radius: 50%; border: 4px solid rgba(56, 189, 248, 0.2);
    border-top-color: #fde047; border-right-color: #38bdf8;
    display: flex; align-items: center; justify-content: center;
    font-size: 42px; animation: spinOrbit 1.4s linear infinite;
  }
  .orbit-ring span { animation: spinReverse 1.4s linear infinite; display: inline-block; }
  @keyframes spinOrbit { to { transform: rotate(360deg); } }
  @keyframes spinReverse { to { transform: rotate(-360deg); } }

  .load-title {
    font-size: 30px; font-weight: 900; letter-spacing: 1.5px;
    background: linear-gradient(90deg, #fde047, #38bdf8, #f43f5e);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .load-bar-bg {
    width: 100%; height: 14px; background: #0f172a; border: 2px solid #38bdf8;
    border-radius: 999px; overflow: hidden; margin: 18px 0 8px 0;
  }
  .load-bar-fill {
    height: 100%; width: 0%;
    background: linear-gradient(90deg, #ef4444, #eab308, #38bdf8);
    transition: width 0.08s linear;
  }
  .science-backdrop-card {
    margin-top: 22px; padding: 16px 20px; border-radius: 16px;
    background: linear-gradient(145deg, rgba(30, 27, 75, 0.92), rgba(15, 23, 42, 0.92));
    border: 2px solid rgba(253, 224, 71, 0.7); text-align: left;
  }
  .science-tag { font-size: 11px; font-weight: 900; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; }
  .science-fact-txt { font-size: 14.5px; color: #f8fafc; margin-top: 6px; line-height: 1.5; font-weight: 600; }

  .create-card {
    width: 560px; max-width: 94%; padding: 34px 36px; text-align: center;
  }
  .game-logo-title {
    font-size: 36px; font-weight: 900; color: #fde047; letter-spacing: 1px;
    text-shadow: 0 0 24px rgba(253, 224, 71, 0.45);
  }
  .game-logo-sub {
    font-size: 13.5px; color: #7dd3fc; font-weight: 800; letter-spacing: 2px;
    text-transform: uppercase; margin: 6px 0 26px 0;
  }
  .menu-btn {
    width: 100%; padding: 15px 20px; margin-bottom: 12px;
    border-radius: 16px; font-size: 16px; font-weight: 900; cursor: pointer;
    border: 2.5px solid #fde047; color: #ffffff;
    background: linear-gradient(90deg, #dc2626 0%, #2563eb 100%);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
    transition: transform 0.16s, box-shadow 0.16s;
  }
  .menu-btn:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 0 24px rgba(56, 189, 248, 0.7); }
  .menu-btn.secondary {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-color: #38bdf8;
  }
  .menu-btn.multi {
    background: linear-gradient(145deg, #3b0764, #1e1b4b);
    border-color: #c084fc;
  }
  #multi-notice {
    display: none; margin-top: 10px; padding: 12px 16px; border-radius: 12px;
    background: rgba(127, 29, 29, 0.92); border: 2px solid #fca5a5;
    color: #fef08a; font-weight: 800; font-size: 13.5px;
  }

  .age-panel {
    width: 1120px; max-width: 97%; padding: 20px 24px;
  }
  .age-top-row {
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 14px; margin-bottom: 16px;
  }
  .age-input-group {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8;
    border-radius: 14px; padding: 10px 16px;
  }
  .age-input-group label { font-size: 15px; font-weight: 900; color: #fde047; }
  .age-input-group input {
    width: 110px; padding: 8px 12px; border-radius: 10px;
    border: 2px solid #fde047; background: #020617; color: #ffffff;
    font-size: 17px; font-weight: 900; text-align: center; outline: none;
  }
  #age-feedback { font-size: 13px; font-weight: 800; color: #93c5fd; }
  .vault-badge {
    background: linear-gradient(145deg, #422006, #1e1b4b);
    border: 2.5px solid #fde047; border-radius: 14px; padding: 10px 20px;
    font-size: 16px; font-weight: 900; color: #fde047;
    box-shadow: 0 0 18px rgba(253, 224, 71, 0.25);
  }
  .hero-grid {
    display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin: 12px 0 14px 0;
  }
  @media (max-width: 1020px) { .hero-grid { grid-template-columns: repeat(4, 1fr); } }
  .hero-card {
    background: linear-gradient(155deg, #0f172a, #1e1b4b);
    border: 2.5px solid #334155; border-radius: 16px; padding: 9px 7px;
    text-align: center; cursor: pointer; position: relative;
    transition: transform 0.16s, border-color 0.16s, box-shadow 0.16s;
  }
  .hero-card:hover { transform: translateY(-3px); border-color: #38bdf8; }
  .hero-card.selected {
    border-color: #fde047;
    box-shadow: 0 0 22px rgba(253, 224, 71, 0.75);
    background: linear-gradient(155deg, #1e1b4b, #172554);
  }
  .hero-card.locked { opacity: 0.78; border-color: #475569; }
  .hero-name { font-weight: 900; font-size: 13px; color: #fde047; margin-top: 2px; }
  .hero-perk { font-size: 10.5px; color: #86efac; font-weight: 700; margin-top: 4px; line-height: 1.25; }
  .hero-status {
    margin-top: 6px; padding: 4px 6px; border-radius: 8px;
    font-size: 10.5px; font-weight: 900;
  }
  .status-unlocked { background: rgba(22, 163, 74, 0.25); color: #86efac; border: 1px solid #4ade80; }
  .status-locked { background: rgba(127, 29, 29, 0.55); color: #fde047; border: 1px solid #f87171; }
  #hero-msg {
    min-height: 22px; text-align: center; font-size: 13.5px; font-weight: 800;
    color: #fca5a5; margin-bottom: 10px;
  }
  .continue-btn {
    width: 340px; max-width: 100%; padding: 14px 24px; border-radius: 14px;
    font-size: 16px; font-weight: 900; cursor: pointer;
    border: 2.5px solid #fde047; color: #ffffff;
    background: linear-gradient(90deg, #16a34a, #0284c7);
    display: block; margin: 0 auto; transition: 0.18s;
  }
  .continue-btn:disabled {
    background: #1e293b; border-color: #475569; color: #64748b; cursor: not-allowed;
    box-shadow: none; transform: none;
  }

  .inst-panel { width: 1040px; max-width: 96%; padding: 26px 28px; text-align: center; }
  .inst-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0 22px 0; }
  @media (max-width: 900px) { .inst-grid { grid-template-columns: repeat(2, 1fr); } }
  .inst-box {
    background: linear-gradient(155deg, #1e293b, #0f172a);
    border: 2px solid #38bdf8; border-radius: 16px; padding: 16px 14px; text-align: center;
  }
  .inst-box h3 { color: #fde047; font-size: 15px; margin: 6px 0; }
  .inst-box p { color: #e2e8f0; font-size: 12.5px; line-height: 1.45; }

  #screen-game { padding: 0; }
  #game-root {
    position: relative; width: 100%; height: 860px; overflow: hidden;
    background: #020617; outline: none;
  }
  #canvas-container { position: absolute; inset: 0; width: 100%; height: 100%; }

  #game-sidebar {
    position: absolute; top: 0; left: 0; bottom: 0; width: 270px; z-index: 45;
    background: linear-gradient(180deg, rgba(7, 11, 24, 0.97), rgba(15, 23, 42, 0.97));
    border-right: 3px solid #eab308; padding: 16px 14px;
    transform: translateX(-100%); transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
    display: flex; flex-direction: column; gap: 8px; overflow-y: auto;
    box-shadow: 12px 0 36px rgba(0, 0, 0, 0.85);
  }
  #game-sidebar.open { transform: translateX(0); }
  .sb-header {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 10px; border-bottom: 1.5px solid #334155;
  }
  .sb-stat {
    background: #0f172a; border: 1.5px solid #38bdf8; border-radius: 12px;
    padding: 9px 12px; font-size: 12.5px; line-height: 1.5;
  }
  .sb-btn {
    width: 100%; padding: 10px 12px; border-radius: 11px; text-align: left;
    font-size: 12.5px; font-weight: 800; color: #ffffff; cursor: pointer;
    background: linear-gradient(90deg, #1e293b, #1e1b4b);
    border: 1.5px solid #38bdf8; transition: 0.15s;
  }
  .sb-btn:hover { border-color: #fde047; background: #1d4ed8; }
  .sb-btn.danger { background: linear-gradient(90deg, #7f1d1d, #991b1b); border-color: #fca5a5; }

  .top-hud {
    position: absolute; top: 8px; left: 8px; right: 8px;
    display: grid; grid-template-columns: 0.52fr 1fr 0.92fr 0.92fr 0.92fr 0.92fr 1.15fr;
    gap: 6px; pointer-events: none; z-index: 12;
  }
  .hud-card {
    background: rgba(9, 13, 31, 0.86); backdrop-filter: blur(8px);
    border: 2px solid rgba(234, 179, 8, 0.78); border-radius: 12px;
    padding: 5px 8px; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.65);
    pointer-events: auto;
  }
  .sidebar-toggle-btn {
    width: 100%; height: 100%; background: linear-gradient(145deg, #1d4ed8, #1e1b4b);
    border: 2px solid #fde047; border-radius: 12px; color: #fde047;
    font-size: 12px; font-weight: 900; cursor: pointer; pointer-events: auto;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px;
  }
  .sidebar-toggle-btn:hover { box-shadow: 0 0 14px rgba(253, 224, 71, 0.7); }
  .hud-row { display: flex; justify-content: space-between; align-items: center; }
  .hud-lbl { font-size: 10px; font-weight: 800; color: #93c5fd; text-transform: uppercase; display: flex; align-items: center; gap: 3px; }
  .hud-val { font-size: 16px; font-weight: 900; color: #ffffff; }
  .hud-sub { font-size: 9.8px; font-weight: 800; color: #cbd5e1; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-bg { width: 100%; height: 6px; background: rgba(2, 6, 23, 0.92); border-radius: 99px; overflow: hidden; margin-top: 3px; }
  .bar-fill { height: 100%; width: 90%; transition: width 0.18s ease; border-radius: 99px; }

  .qchip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 14px; height: 14px; border-radius: 50%;
    background: rgba(56, 189, 248, 0.25); border: 1px solid #38bdf8;
    color: #7dd3fc; font-size: 9.5px; font-weight: 900; cursor: pointer;
  }

  .ticker-bar {
    position: absolute; top: 76px; left: 8px; right: 8px;
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
    background: rgba(15, 23, 42, 0.86); backdrop-filter: blur(6px);
    border: 1.5px solid #38bdf8; border-radius: 10px; padding: 5px 12px;
    z-index: 12; font-size: 12px; font-weight: 800;
  }
  .nasa-badge-btn {
    background: rgba(14, 165, 233, 0.22); border: 1px solid #38bdf8; color: #7dd3fc;
    border-radius: 999px; padding: 2px 10px; font-size: 10.5px; font-weight: 900; cursor: pointer;
  }

  #minimap-wrap {
    position: absolute; top: 114px; left: 10px; z-index: 16;
    background: rgba(2, 6, 23, 0.84); border: 2px solid #38bdf8; border-radius: 14px;
    padding: 5px; text-align: center;
  }
  #minimap { display: block; border-radius: 8px; background: #0b1120; }

  #flare-alarm {
    position: absolute; top: 266px; left: 10px;
    background: linear-gradient(90deg, rgba(185, 28, 28, 0.95), rgba(127, 29, 29, 0.95));
    border: 2.5px solid #fde047; border-radius: 12px; padding: 7px 12px;
    z-index: 22; display: none; width: 255px;
    box-shadow: 0 0 25px rgba(239, 68, 68, 0.85);
    animation: pulseRed 0.75s infinite alternate;
  }
  @keyframes pulseRed { from { transform: scale(1); } to { transform: scale(1.03); } }

  #comic-toast {
    position: absolute; top: 114px; right: 12px; width: 260px;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(30, 27, 75, 0.96));
    border: 3px solid #fde047; border-radius: 16px; padding: 9px 12px;
    z-index: 25; display: none; text-align: center;
    box-shadow: 0 0 28px rgba(253, 224, 71, 0.55);
  }

  #unlock-banner {
    position: absolute; top: 118px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(90deg, #ca8a04, #16a34a);
    border: 2.5px solid #fef08a; border-radius: 999px; padding: 8px 22px;
    font-size: 13.5px; font-weight: 900; color: #ffffff; z-index: 35;
    display: none; box-shadow: 0 0 28px rgba(250, 204, 21, 0.85);
  }

  #pad-progress-wrap {
    position: absolute; top: 160px; left: 50%; transform: translateX(-50%);
    background: rgba(2, 6, 23, 0.92); border: 2px solid #4ade80; border-radius: 999px;
    padding: 6px 16px; display: none; align-items: center; gap: 10px; z-index: 20;
  }
  #pad-progress-bar-bg { width: 125px; height: 9px; background: #1e293b; border-radius: 99px; overflow: hidden; }
  #pad-progress-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #4ade80, #fde047); }

  .bottom-dock {
    position: absolute; bottom: 8px; left: 8px; right: 8px;
    display: grid; grid-template-columns: 1.35fr 1.3fr 1.55fr;
    gap: 8px; z-index: 15;
  }
  .dock-panel {
    background: rgba(9, 13, 31, 0.89); backdrop-filter: blur(8px);
    border: 1.5px solid rgba(56, 189, 248, 0.6); border-radius: 13px; padding: 7px 9px;
  }
  .dock-title { font-size: 10.5px; font-weight: 900; color: #fde047; text-transform: uppercase; margin-bottom: 5px; display: flex; justify-content: space-between; }
  .btn-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
  .btn-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
  .btn-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
  .btn-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }

  .gbtn {
    background: linear-gradient(145deg, #1d4ed8, #312e81);
    color: #ffffff; border: 1.5px solid #7dd3fc; border-radius: 8px;
    padding: 5.5px 4px; font-size: 10.8px; font-weight: 800; cursor: pointer; text-align: center;
  }
  .gbtn:hover { border-color: #fde047; transform: translateY(-1px); }
  .gbtn-green { background: linear-gradient(145deg, #15803d, #047857); border-color: #86efac; }
  .gbtn-red { background: linear-gradient(145deg, #b91c1c, #991b1b); border-color: #fca5a5; }
  .gbtn-gold { background: linear-gradient(145deg, #ca8a04, #b45309); border-color: #fef08a; }
  .gbtn-cyan { background: linear-gradient(145deg, #0369a1, #1e3a8a); border-color: #38bdf8; }
  .gbtn-purple { background: linear-gradient(145deg, #7e22ce, #4c1d95); border-color: #d8b4fe; }

  .modal-backdrop {
    position: absolute; inset: 0; z-index: 60;
    background: rgba(2, 6, 23, 0.9); backdrop-filter: blur(8px);
    display: none; align-items: center; justify-content: center; padding: 16px;
  }
  .modal-box {
    background: linear-gradient(160deg, #0f172a, #1e1b4b);
    border: 3px solid #38bdf8; border-radius: 20px; padding: 20px 24px;
    width: 680px; max-width: 96%; max-height: 92%; overflow-y: auto;
  }
  .choice-btn {
    width: 100%; text-align: left; background: rgba(30, 41, 59, 0.95);
    border: 2px solid #eab308; border-radius: 12px; padding: 11px 14px;
    color: #fff; cursor: pointer; margin-top: 9px;
  }
  .choice-btn:hover { background: rgba(30, 58, 138, 0.95); border-color: #38bdf8; }

  #glossary-pop {
    position: absolute; top: 116px; left: 50%; transform: translateX(-50%);
    width: 400px; max-width: 90%;
    background: rgba(15, 23, 42, 0.98); border: 2.5px solid #38bdf8; border-radius: 16px;
    padding: 12px 16px; z-index: 50; display: none;
  }
  .slider-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0; }
  .slider-item { background: #020617; border: 1px solid #334155; border-radius: 10px; padding: 8px 10px; font-size: 12px; }
  .slider-item input { width: 100%; margin-top: 4px; }
</style>
</head>
<body>
<div id="app-shell">
  <canvas id="bg-space-canvas"></canvas>

  <div id="screen-loader" class="screen active">
    <div class="loader-wrap">
      <div class="orbit-ring"><span>🌕</span></div>
      <div class="load-title">AVENGERS LUNAR OUTPOST 3D</div>
      <div style="font-size:12.5px;color:#93c5fd;font-weight:800;margin-top:4px;letter-spacing:1px;">INITIALIZING SHACKLETON CRATER TELEMETRY...</div>
      <div class="load-bar-bg"><div id="load-bar-fill" class="load-bar-fill"></div></div>
      <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:900;color:#fde047;">
        <span id="load-status">Calibrating 1/6G Lunar Physics...</span>
        <span id="load-pct">0%</span>
      </div>
      <div class="science-backdrop-card">
        <div class="science-tag">🛰️ REAL LUNAR SPACE SCIENCE FACT</div>
        <div id="load-fact" class="science-fact-txt"></div>
      </div>
    </div>
  </div>

  <div id="screen-create" class="screen">
    <div class="glass-panel create-card">
      <div style="font-size:52px;margin-bottom:6px;">🛡️🌕🚀</div>
      <div class="game-logo-title">AVENGERS LUNAR OUTPOST</div>
      <div class="game-logo-sub">3D Shackleton Crater Survival</div>
      <button class="menu-btn" onclick="goToAgePage()">🚀 CREATE &amp; PLAY MISSION</button>
      <button class="menu-btn secondary" id="create-music-btn" onclick="toggleMusic()">🎵 MUSIC: ON</button>
      <button class="menu-btn multi" onclick="clickMultiplayer()">👥 MULTIPLAYER</button>
      <div id="multi-notice">🚧 Multiplayer Mode is Currently Unavailable! Enjoy Single-Player 3D Lunar Survival.</div>
    </div>
  </div>

  <div id="screen-age" class="screen">
    <div class="glass-panel age-panel">
      <div style="text-align:center;margin-bottom:12px;">
        <h2 style="color:#fde047;font-size:24px;font-weight:900;">🦸 COMMANDER AGE &amp; HERO SELECTION</h2>
      </div>
      <div class="age-top-row">
        <div class="age-input-group">
          <label for="age-input">🎂 Enter Your Age:</label>
          <input type="number" id="age-input" min="1" max="100" placeholder="Age" oninput="validateAgePage()">
          <span id="age-feedback">Enter your age (1–100) to unlock mission briefing</span>
        </div>
        <div class="vault-badge">🪙 VAULT COINS: <span id="age-vault-coins">40</span></div>
      </div>
      <div id="hero-grid" class="hero-grid"></div>
      <div id="hero-msg"></div>
      <button id="btn-to-inst" class="continue-btn" disabled onclick="goToInstructions()">CONTINUE TO INSTRUCTIONS ➡️</button>
    </div>
  </div>

  <div id="screen-instructions" class="screen">
    <div class="glass-panel inst-panel">
      <h2 style="color:#fde047;font-size:26px;font-weight:900;">📖 MISSION BRIEFING &amp; CONTROLS</h2>
      <p id="inst-hero-line" style="color:#7dd3fc;font-size:14px;font-weight:800;margin-top:6px;"></p>
      <div class="inst-grid">
        <div class="inst-box">
          <div style="font-size:32px;">🕹️</div>
          <h3>1. Explore 3D Moon</h3>
          <p>Use <b>W A S D / Arrow Keys</b> and <b>SPACE</b> for 1/6G lunar jumps, or tap the <b>Auto-Run buttons</b>. Stand on glowing pads to auto-work!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:32px;">🚨</div>
          <h3>2. NASA Solar Flares</h3>
          <p>Keep Shield <b>OFF</b> during calm skies to charge batteries. When a <b>DONKI Solar Flare</b> hits: Run Inside, <b>Seal Airlock</b>, and <b>Raise Shield</b>!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:32px;">🌱</div>
          <h3>3. Farm, Ice &amp; Science</h3>
          <p>Harvest 4 CSA crops to stock your Pantry, mine Crater Ice for O₂ (-Power), and drill <b>EVA Core Samples</b> (+Science, -O₂).</p>
        </div>
        <div class="inst-box">
          <div style="font-size:32px;">🪙</div>
          <h3>4. Grow Vault Coins</h3>
          <p>Every coin earned on the Moon goes straight into your <b>Vault</b> and unlocks elite Avengers! Open the Game Sidebar anytime to switch heroes.</p>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:14px;flex-wrap:wrap;">
        <button class="menu-btn secondary" style="width:200px;margin:0;" onclick="goToAgePage()">⬅️ Back</button>
        <button class="menu-btn" style="width:320px;margin:0;" onclick="launchGameScreen()">🚀 LAUNCH 3D MOON MISSION</button>
      </div>
    </div>
  </div>

  <div id="screen-game" class="screen">
    <div id="game-root" tabindex="0">
      <div id="canvas-container"></div>

      <div id="game-sidebar">
        <div class="sb-header">
          <span style="font-weight:900;color:#fde047;font-size:15px;">🛡️ COMMAND MENU</span>
          <button onclick="toggleSidebar()" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 10px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <div class="sb-stat">
          <div><b>Hero:</b> <span id="sb-hero" style="color:#fde047;"></span></div>
          <div><b>Mode:</b> <span id="sb-mode" style="color:#7dd3fc;"></span></div>
          <div><b>Vault Coins:</b> <span id="sb-coins" style="color:#fde047;font-weight:900;">40</span> 🪙</div>
          <div><b>Trophies:</b> <span id="sb-wins" style="color:#4ade80;font-weight:900;">0</span> 🏆</div>
        </div>
        <button class="sb-btn" onclick="sidebarChangeAgeHero()">🦸 Change Age &amp; Hero</button>
        <button class="sb-btn" onclick="sidebarGoInstructions()">📖 Mission Instructions</button>
        <button class="sb-btn" onclick="openMathLab()">📈 Engineering Graphs &amp; Math Lab</button>
        <button class="sb-btn" onclick="openNasaModal()">🛰️ NASA &amp; Partner Data Log</button>
        <button class="sb-btn" id="sb-music-btn" onclick="toggleMusic()">🎵 Music: ON</button>
        <button class="sb-btn" onclick="restartCurrentRun()">🔄 Restart Current Mission</button>
        <button class="sb-btn danger" onclick="quitAndResetGame()">🚪 Quit Game &amp; Reset Vault</button>
      </div>

      <div class="top-hud">
        <button class="sidebar-toggle-btn" onclick="toggleSidebar()">
          <span style="font-size:18px;line-height:1;">☰</span>
          <span>MENU</span>
        </button>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">📅 Sol <span class="qchip" onclick="openGlossary('SOL')">?</span></span>
            <span class="hud-val" id="ui-sol">1 / 7</span>
          </div>
          <div class="bar-bg"><div id="bar-sol" class="bar-fill" style="width:0%;background:#a855f7;"></div></div>
          <div class="hud-sub" id="ui-weather">☀️ Calm Sky</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">⚡ Power <span class="qchip" onclick="openGlossary('POWER')">?</span></span>
            <span class="hud-val" id="ui-pwr">92%</span>
          </div>
          <div class="bar-bg"><div id="bar-pwr" class="bar-fill" style="width:92%;background:#facc15;"></div></div>
          <div class="hud-sub" id="sub-pwr">☀️ Charging</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">🫁 O₂ <span class="qchip" onclick="openGlossary('OXYGEN')">?</span></span>
            <span class="hud-val" id="ui-ox">92%</span>
          </div>
          <div class="bar-bg"><div id="bar-ox" class="bar-fill" style="width:92%;background:#38bdf8;"></div></div>
          <div class="hud-sub" id="sub-ox">🔒 Sealed</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">🍽️ Food <span class="qchip" onclick="openGlossary('FOOD')">?</span></span>
            <span class="hud-val" id="ui-food">86%</span>
          </div>
          <div class="bar-bg"><div id="bar-food" class="bar-fill" style="width:86%;background:#4ade80;"></div></div>
          <div class="hud-sub" id="sub-basket">🧺 0/4</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">❤️ HP <span class="qchip" onclick="openGlossary('RAD')">?</span></span>
            <span class="hud-val" id="ui-hp">100%</span>
          </div>
          <div class="bar-bg"><div id="bar-hp" class="bar-fill" style="width:100%;background:#f43f5e;"></div></div>
          <div class="hud-sub" id="sub-rad">☢️ 0.42 mSv</div>
        </div>
        <div class="hud-card" style="border-color:#38bdf8;">
          <div class="hud-row">
            <span class="hud-lbl">🪙 Vault / 🔬</span>
            <span class="hud-val" style="font-size:14px;"><span id="ui-coins" style="color:#fde047;">40</span> | <span id="ui-sci" style="color:#d8b4fe;">0</span></span>
          </div>
          <div style="display:flex;gap:4px;margin-top:5px;">
            <button class="gbtn" id="hud-music-btn" style="flex:1;padding:3px;font-size:10px;" onclick="toggleMusic()">🔊 Music</button>
            <button class="gbtn gbtn-gold" style="flex:1;padding:3px;font-size:10px;" onclick="toggleCameraMode()">🎥 Cam</button>
          </div>
        </div>
      </div>

      <div class="ticker-bar">
        <span id="status-msg">🚀 Touchdown at Shackleton Crater! Collect Moon Coins to grow your Vault!</span>
        <button class="nasa-badge-btn" id="nasa-feed-btn" onclick="openNasaModal()">🛰️ NASA DONKI Telemetry</button>
      </div>

      <div id="minimap-wrap">
        <div style="font-size:9.5px;font-weight:900;color:#7dd3fc;margin-bottom:3px;">📡 SHACKLETON RADAR</div>
        <canvas id="minimap" width="128" height="110"></canvas>
      </div>

      <div id="flare-alarm">
        <div style="font-size:12.5px;font-weight:900;color:#fde047;" id="flare-alarm-title">🚨 NASA DONKI FLARE!</div>
        <div style="font-size:11px;color:#fff;margin-top:2px;" id="flare-alarm-desc">Run inside, Seal Airlock &amp; Raise Shield!</div>
      </div>

      <div id="unlock-banner"></div>

      <div id="pad-progress-wrap">
        <span id="pad-progress-label" style="font-size:12px;font-weight:900;color:#4ade80;">⚡ Working...</span>
        <div id="pad-progress-bar-bg"><div id="pad-progress-bar"></div></div>
      </div>

      <div id="comic-toast">
        <div id="comic-badge" style="font-size:34px;line-height:1.1;">🛡️⚡</div>
        <div id="comic-title" style="font-size:13px;font-weight:900;color:#fde047;margin-top:3px;">SHIELD ONLINE!</div>
        <div id="comic-body" style="font-size:11px;color:#e2e8f0;margin-top:2px;">Blocking radiation!</div>
      </div>

      <div id="glossary-pop">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span id="gl-title" style="font-weight:900;color:#fde047;font-size:14px;">Science Decoder</span>
          <button onclick="closeGlossary()" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:2px 8px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <p id="gl-body" style="font-size:12.5px;color:#e2e8f0;margin:7px 0 0 0;line-height:1.45;"></p>
      </div>

      <div class="bottom-dock">
        <div class="dock-panel">
          <div class="dock-title"><span>🏃 Auto-Run Stations</span><span style="color:#7dd3fc;">WASD / Arrows + Space</span></div>
          <div class="btn-grid-4" style="margin-bottom:5px;">
            <button class="gbtn gbtn-gold" onclick="autoRunTo('SOLAR')">☀️ Solar</button>
            <button class="gbtn gbtn-cyan" onclick="autoRunTo('ICE')">🧊 Ice</button>
            <button class="gbtn gbtn-purple" onclick="autoRunTo('SCIENCE')">🔬 Science</button>
            <button class="gbtn gbtn-green" onclick="autoRunTo('FARM')">🌱 Farm</button>
          </div>
          <div class="btn-grid-3">
            <button class="gbtn" onclick="autoRunTo('PANTRY')">🍽️ Pantry</button>
            <button class="gbtn gbtn-red" onclick="autoRunTo('SHIELD')">🛡️ Console</button>
            <button class="gbtn" onclick="triggerJump()">⬆️ 1/6G Jump</button>
          </div>
        </div>

        <div class="dock-panel">
          <div class="dock-title"><span>⚙️ Outpost Systems</span><span id="zone-badge" style="color:#4ade80;">📍 INSIDE BASE</span></div>
          <div class="btn-grid-2" style="margin-bottom:5px;">
            <button class="gbtn gbtn-red" id="btn-shield" onclick="toggleShield()">🛡️ Shield: OFF</button>
            <button class="gbtn gbtn-green" id="btn-door" onclick="toggleDoor()">🔒 Airlock: SEALED</button>
          </div>
          <div class="btn-grid-2">
            <button class="gbtn gbtn-gold" onclick="deployRoverScan()">🚙 Rover (+Coins)</button>
            <button class="gbtn gbtn-cyan" onclick="advanceSolEarly()">🌙 Next Sol</button>
          </div>
        </div>

        <div class="dock-panel">
          <div class="dock-title"><span>📡 Earth HQ Radio <span class="qchip" onclick="openGlossary('DELAY')">?</span></span><span style="color:#7dd3fc;">384,400 km • 2.6s</span></div>
          <div class="btn-grid-5" style="margin-bottom:5px;">
            <button class="gbtn" onclick="callEarth(1)">⚡<br>+30%</button>
            <button class="gbtn gbtn-cyan" onclick="callEarth(2)">🫁<br>+30%</button>
            <button class="gbtn gbtn-green" onclick="callEarth(3)">🍅<br>+30%</button>
            <button class="gbtn gbtn-red" onclick="callEarth(4)">❤️<br>+30%</button>
            <button class="gbtn gbtn-gold" onclick="callEarth(5)">☀️<br>Clear</button>
          </div>
          <div id="radio-log" style="font-size:10.3px;color:#fde047;font-weight:800;text-align:center;">
            15 🪙 per drop (Dr. Strange: 10 🪙 &amp; 1.0s delay)
          </div>
        </div>
      </div>

      <div id="dilemma-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:#dc2626;color:#fff;font-size:11px;font-weight:900;padding:3px 10px;border-radius:999px;">⚖️ NASA ENGINEERING DILEMMA</span>
            <span id="dil-sol" style="color:#7dd3fc;font-size:12px;font-weight:900;">SOL 2</span>
          </div>
          <h3 id="dil-title" style="margin:10px 0 6px 0;color:#fde047;font-size:19px;"></h3>
          <p id="dil-desc" style="margin:0 0 8px 0;font-size:13px;color:#e2e8f0;line-height:1.45;"></p>
          <div id="dil-choices"></div>
        </div>
      </div>

      <div id="debrief-modal" class="modal-backdrop">
        <div class="modal-box" style="text-align:center;border-color:#fde047;">
          <div id="debrief-icon" style="font-size:38px;">🏆</div>
          <h2 id="debrief-title" style="color:#fde047;font-size:21px;margin:4px 0;"></h2>
          <div id="debrief-rank" style="font-size:13px;font-weight:900;color:#4ade80;margin-bottom:4px;"></div>
          <p id="debrief-sub" style="font-size:12.5px;color:#cbd5e1;margin-bottom:6px;"></p>
          <canvas id="debrief-chart" width="600" height="145" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:12px;margin:6px 0;"></canvas>
          <div id="debrief-lesson" style="background:rgba(14,165,233,0.15);border:1.5px solid #38bdf8;border-radius:10px;padding:9px 12px;font-size:12px;color:#e0f2fe;text-align:left;line-height:1.4;margin-bottom:12px;"></div>
          <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
            <button class="menu-btn secondary" style="width:220px;margin:0;padding:11px;" onclick="debriefChangeHero()">🦸 Switch Hero (Vault: <span id="deb-vault">40</span> 🪙)</button>
            <button class="menu-btn" style="width:220px;margin:0;padding:11px;" onclick="restartCurrentRun()">🔄 Play Again</button>
          </div>
        </div>
      </div>

      <div id="math-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="color:#fde047;">📈 Engineering Trade-Off Math Lab</h3>
            <button onclick="closeModal('math-modal')" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 12px;font-weight:900;cursor:pointer;">Close ✕</button>
          </div>
          <div class="slider-grid">
            <div class="slider-item">🛡️ Shield Duty: <b id="sl-sh-v">35%</b><input type="range" id="sl-sh" min="0" max="100" value="35" oninput="updateMathLab()"></div>
            <div class="slider-item">🌱 Grow-Lights: <b id="sl-fm-v">50%</b><input type="range" id="sl-fm" min="10" max="100" value="50" oninput="updateMathLab()"></div>
            <div class="slider-item">🔬 EVA Science: <b id="sl-ev-v">2 hrs</b><input type="range" id="sl-ev" min="0" max="6" value="2" oninput="updateMathLab()"></div>
            <div class="slider-item">🌪️ Solar Dust: <b id="sl-ds-v">15%</b><input type="range" id="sl-ds" min="0" max="60" value="15" oninput="updateMathLab()"></div>
          </div>
          <canvas id="math-chart" width="600" height="175" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:12px;"></canvas>
          <div id="math-summary" style="margin-top:8px;font-size:12px;color:#93c5fd;font-weight:700;"></div>
        </div>
      </div>

      <div id="nasa-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <h3 style="color:#fde047;">🛰️ NASA &amp; Space Agency Partner Data</h3>
            <button onclick="closeModal('nasa-modal')" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 12px;font-weight:900;cursor:pointer;">Close ✕</button>
          </div>
          <div id="nasa-data-body" style="font-size:12.5px;line-height:1.55;color:#e2e8f0;"></div>
        </div>
      </div>

    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
        onerror="var s=document.createElement('script');s.src='https://unpkg.com/three@0.128.0/build/three.min.js';document.head.appendChild(s);"></script>

<script>
const NASA = __NASA_JSON__;

const HEROES = [
  {
    key: "CAP", name: "Captain America", unlockCoins: 0,
    perk: "🛡️ Shield drains 50% less Power",
    suit: "#1d4ed8", accent: "#ef4444", eyes: "#38bdf8",
    head: "<path d='M 24 50 A 36 36 0 0 1 96 50 Z' fill='#1d4ed8' stroke='#ffffff' stroke-width='2'/><text x='60' y='38' text-anchor='middle' fill='#ffffff' font-size='18' font-weight='900'>A</text>"
  },
  {
    key: "WIDOW", name: "Natasha Romanoff", unlockCoins: 0,
    perk: "🕷️ +25% Speed & 40% less O₂ use",
    suit: "#1e293b", accent: "#ef4444", eyes: "#22c55e",
    head: "<path d='M 24 58 Q 26 14 60 16 Q 94 14 96 58 L 88 34 Q 60 22 32 34 Z' fill='#b91c1c'/><circle cx='24' cy='52' r='9' fill='#b91c1c'/><circle cx='96' cy='52' r='9' fill='#b91c1c'/>"
  },
  {
    key: "IRON", name: "Iron Man", unlockCoins: 80,
    perk: "⚡ 2x Solar Charge & Jet Jumps",
    suit: "#dc2626", accent: "#facc15", eyes: "#38bdf8",
    head: "<rect x='30' y='18' width='60' height='54' rx='18' fill='#b91c1c' stroke='#facc15' stroke-width='3'/><polygon points='38,22 82,22 76,58 44,58' fill='#facc15'/><rect x='40' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/><rect x='66' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/>"
  },
  {
    key: "THOR", name: "Thor Odinson", unlockCoins: 120,
    perk: "🔨 60% less Solar Flare Radiation",
    suit: "#475569", accent: "#ef4444", eyes: "#38bdf8",
    head: "<path d='M 24 58 Q 28 14 60 16 Q 92 14 96 58 L 86 34 Q 60 24 34 34 Z' fill='#facc15'/><path d='M 20 42 L 10 22 L 26 32 Z' fill='#cbd5e1'/><path d='M 100 42 L 110 22 L 94 32 Z' fill='#cbd5e1'/>"
  },
  {
    key: "STRANGE", name: "Dr. Strange", unlockCoins: 160,
    perk: "⏳ 1.0s Radio Delay & 10 🪙 Drops",
    suit: "#1e3a8a", accent: "#dc2626", eyes: "#4ade80",
    head: "<path d='M 28 46 Q 30 16 60 16 Q 90 16 92 46 L 84 32 Q 60 22 36 32 Z' fill='#1e293b'/><path d='M 26 42 L 34 42' stroke='#e2e8f0' stroke-width='4'/><path d='M 86 42 L 94 42' stroke='#e2e8f0' stroke-width='4'/>"
  },
  {
    key: "WANDA", name: "Wanda Maximoff", unlockCoins: 200,
    perk: "🔮 2x Crop Growth & +6% O₂ Bonus",
    suit: "#991b1b", accent: "#f43f5e", eyes: "#ef4444",
    head: "<path d='M 22 60 Q 26 16 60 16 Q 94 16 98 60 L 86 34 Q 60 24 34 34 Z' fill='#7c2d12'/><polygon points='42,38 50,18 60,30 70,18 78,38' fill='#ef4444' stroke='#fca5a5' stroke-width='1.5'/>"
  },
  {
    key: "LOKI", name: "Loki", unlockCoins: 250,
    perk: "🐍 2x Vault Coins & +50% Science",
    suit: "#15803d", accent: "#eab308", eyes: "#22c55e",
    head: "<path d='M 22 58 Q 24 18 60 18 Q 96 18 98 58 Z' fill='#0f172a'/><path d='M 34 40 Q 60 50 86 40 L 82 28 Q 60 38 38 28 Z' fill='#eab308' stroke='#fef08a' stroke-width='1.5'/><path d='M 40 32 Q 22 6 44 4 Q 34 18 46 30 Z' fill='#eab308'/><path d='M 80 32 Q 98 6 76 4 Q 86 18 74 30 Z' fill='#eab308'/>"
  }
];

const LOAD_FACTS = [
  "Shackleton Crater at the Moon's South Pole has sunlit rims for solar power right next to permanently shadowed craters filled with water-ice (H₂O) that can be split into breathable Oxygen!",
  "Even traveling at the speed of light (300,000 km/s), a radio message from a Lunar Outpost to Earth HQ and back takes 2.56 seconds across 384,400 km!",
  "Lunar gravity is only 1/6th of Earth's gravity—an astronaut can leap six times higher on the Moon, while abrasive electrostatic lunar dust clings to spacesuits and solar panels!",
  "NASA RadLab data shows lunar astronauts experience roughly 0.42 mSv of cosmic radiation per Sol—over 50 times higher than a normal day at sea level on Earth!"
];

const GLOSSARY = {
  SOL: { title: "📅 What is a Lunar Sol?", body: "A Sol is one survival day-cycle on an off-world outpost. Survive all 7 Sols at Shackleton Crater while balancing Power, Oxygen, Food, and Radiation!" },
  POWER: { title: "⚡ Solar Power vs. Shielding", body: "Solar panels charge your batteries in calm skies, unless coated in lunar dust. Raising the Vibranium Radiation Shield protects you from solar flares but rapidly drains battery power!" },
  OXYGEN: { title: "🫁 Airlock & Ice Electrolysis", body: "The Moon has no air. Leaving the Airlock Door open leaks Oxygen into space. Mine Shackleton Crater ice (H₂O) and split it with electricity to create fresh O₂!" },
  FOOD: { title: "🌱 CSA 4-Crop Hydroponics", body: "Inspired by the Canadian Space Agency Deep Space Food Toolkit and NASA OSDR (OSD-767), your greenhouse grows Tomatoes, Lettuce, Radishes, and Potatoes without soil." },
  RAD: { title: "☢️ Radiation Dose (mSv)", body: "mSv (millisievert) measures radiation exposure. NASA RadLab BLEO sets lunar baseline around 0.42 mSv/Sol, spiking steeply during unshielded NASA DONKI solar storms." },
  DELAY: { title: "📡 2.6-Second Light Delay", body: "Earth is 384,400 km away. Radio waves travel at the speed of light, creating a real 2.56-second round-trip delay when calling Earth Mission Control!" }
};

let session = {
  screen: "LOADER",
  age: null,
  ageTier: "10-12 Commander",
  heroKey: "CAP",
  vaultCoins: 40,
  unlocked: ["CAP", "WIDOW"],
  wins: 0,
  musicOn: true
};

function getHero(key) {
  return HEROES.find(h => h.key === (key || session.heroKey)) || HEROES[0];
}

function getDiff() {
  if (session.ageTier.includes("7-9")) return { drain: 0.72, solSecs: 26, flareWarn: 9.0, flareDur: 8.0, flareDmg: 5.5, flareGap: 14 };
  if (session.ageTier.includes("13+")) return { drain: 1.22, solSecs: 22, flareWarn: 6.5, flareDur: 10.5, flareDmg: 10.0, flareGap: 10 };
  return { drain: 1.0, solSecs: 24, flareWarn: 7.5, flareDur: 9.0, flareDmg: 8.0, flareGap: 12 };
}

let audioCtx = null, bgmInterval = null, bgmIdx = 0;
const bgmNotes = [220, 261.63, 329.63, 392.0, 440.0, 392.0, 329.63, 293.66];

function ensureAudio() {
  if (!audioCtx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) audioCtx = new AC();
  }
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
}

function playSfx(freq, dur=0.14, type="sine", vol=0.08, slideTo=null) {
  if (!session.musicOn) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, audioCtx.currentTime);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, audioCtx.currentTime + dur);
    g.gain.setValueAtTime(vol, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
    o.connect(g); g.connect(audioCtx.destination);
    o.start(); o.stop(audioCtx.currentTime + dur);
  } catch(e) {}
}

function startBgmLoop() {
  clearInterval(bgmInterval);
  bgmInterval = setInterval(() => {
    if (session.musicOn && session.screen !== "LOADER") {
      playSfx(bgmNotes[bgmIdx % bgmNotes.length], 0.16, "sine", 0.015);
      bgmIdx++;
    }
  }, 620);
}

function syncMusicButtons() {
  const lbl = session.musicOn ? "🎵 MUSIC: ON" : "🔇 MUSIC: OFF";
  document.getElementById("create-music-btn").innerText = lbl;
  document.getElementById("sb-music-btn").innerText = lbl;
  document.getElementById("hud-music-btn").innerText = session.musicOn ? "🔊 Music" : "🔇 Muted";
}

function toggleMusic() {
  ensureAudio();
  session.musicOn = !session.musicOn;
  syncMusicButtons();
  if (session.musicOn) {
    playSfx(523.25, 0.18, "triangle", 0.08, 784);
    startBgmLoop();
  }
}

const bgCanvas = document.getElementById("bg-space-canvas");
const bgCtx = bgCanvas.getContext("2d");
let bgStars = [];
function initBgStars() {
  bgCanvas.width = bgCanvas.clientWidth || 1200;
  bgCanvas.height = bgCanvas.clientHeight || 860;
  bgStars = [];
  for (let i = 0; i < 160; i++) {
    bgStars.push({
      x: Math.random() * bgCanvas.width,
      y: Math.random() * bgCanvas.height,
      r: 0.6 + Math.random() * 1.8,
      s: 0.15 + Math.random() * 0.45,
      p: Math.random() * Math.PI * 2
    });
  }
}
initBgStars();
function drawBgSpace(ts) {
  requestAnimationFrame(drawBgSpace);
  if (session.screen === "GAME") return;
  const w = bgCanvas.width, h = bgCanvas.height;
  const grd = bgCtx.createRadialGradient(w * 0.5, h * 0.15, 20, w * 0.5, h * 0.5, w * 0.85);
  grd.addColorStop(0, "#1e1b4b");
  grd.addColorStop(0.55, "#090d1f");
  grd.addColorStop(1, "#020617");
  bgCtx.fillStyle = grd;
  bgCtx.fillRect(0, 0, w, h);

  bgStars.forEach(st => {
    const a = 0.45 + 0.55 * Math.sin(ts * 0.002 * st.s + st.p);
    bgCtx.fillStyle = `rgba(224,242,254,${a})`;
    bgCtx.beginPath(); bgCtx.arc(st.x, st.y, st.r, 0, Math.PI * 2); bgCtx.fill();
  });

  bgCtx.fillStyle = "rgba(100,116,139,0.22)";
  bgCtx.beginPath();
  bgCtx.ellipse(w * 0.5, h + 120, w * 0.72, 220, 0, Math.PI, 0);
  bgCtx.fill();
}
requestAnimationFrame(drawBgSpace);

function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

function startFiveSecondLoader() {
  session.screen = "LOADER";
  showScreen("screen-loader");
  const fact = LOAD_FACTS[Math.floor(Math.random() * LOAD_FACTS.length)];
  document.getElementById("load-fact").innerText = fact;

  const steps = [
    "Connecting to NASA DONKI Space Weather Feed...",
    "Mapping Shackleton Crater Water-Ice Deposits...",
    "Loading 3D Avengers Lunar Suits & Hardware...",
    "Preparing CSA 4-Crop Hydroponic Greenhouse...",
    "Ready for Lunar Launch!"
  ];
  const startT = performance.now();
  const duration = 5000;

  function tickLoader(now) {
    const elapsed = now - startT;
    const pct = Math.min(100, (elapsed / duration) * 100);
    document.getElementById("load-bar-fill").style.width = pct + "%";
    document.getElementById("load-pct").innerText = Math.floor(pct) + "%";
    const sIdx = Math.min(steps.length - 1, Math.floor((pct / 100) * steps.length));
    document.getElementById("load-status").innerText = steps[sIdx];
    if (elapsed < duration) {
      requestAnimationFrame(tickLoader);
    } else {
      goToCreatePage();
    }
  }
  requestAnimationFrame(tickLoader);
}

function goToCreatePage() {
  session.screen = "CREATE";
  document.getElementById("multi-notice").style.display = "none";
  syncMusicButtons();
  showScreen("screen-create");
}

function clickMultiplayer() {
  ensureAudio();
  playSfx(240, 0.18, "sawtooth", 0.06);
  document.getElementById("multi-notice").style.display = "block";
}

function checkHeroUnlocks(showToastInGame=false) {
  let newlyUnlocked = [];
  HEROES.forEach(h => {
    if (!session.unlocked.includes(h.key) && session.vaultCoins >= h.unlockCoins) {
      session.unlocked.push(h.key);
      newlyUnlocked.push(h.name);
    }
  });
  if (showToastInGame && newlyUnlocked.length > 0) {
    const b = document.getElementById("unlock-banner");
    b.innerText = `🔓 NEW AVENGER UNLOCKED: ${newlyUnlocked.join(", ").toUpperCase()}! Open MENU → Change Age & Hero!`;
    b.style.display = "block";
    playSfx(587, 0.28, "triangle", 0.1, 1174);
    clearTimeout(b._t);
    b._t = setTimeout(() => { b.style.display = "none"; }, 4200);
  }
}

function addVaultCoins(amount) {
  if (amount <= 0) return;
  session.vaultCoins += amount;
  checkHeroUnlocks(session.screen === "GAME");
  syncVaultDisplays();
}

function syncVaultDisplays() {
  document.getElementById("age-vault-coins").innerText = Math.floor(session.vaultCoins);
  document.getElementById("ui-coins").innerText = Math.floor(session.vaultCoins);
  document.getElementById("sb-coins").innerText = Math.floor(session.vaultCoins);
  document.getElementById("deb-vault").innerText = Math.floor(session.vaultCoins);
  document.getElementById("sb-wins").innerText = session.wins;
}

function renderHeroGrid() {
  checkHeroUnlocks(false);
  syncVaultDisplays();
  const grid = document.getElementById("hero-grid");
  grid.innerHTML = "";
  HEROES.forEach(h => {
    const unlocked = session.unlocked.includes(h.key);
    const selected = session.heroKey === h.key;
    const card = document.createElement("div");
    card.className = "hero-card" + (selected ? " selected" : "") + (!unlocked ? " locked" : "");
    const lockSvg = unlocked ? "" : `
      <rect x="0" y="0" width="120" height="140" rx="14" fill="rgba(2,6,23,0.78)"/>
      <text x="60" y="68" text-anchor="middle" fill="#fde047" font-size="28">🔒</text>
      <text x="60" y="96" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="bold">${h.unlockCoins} 🪙</text>
    `;
    card.innerHTML = `
      <svg width="86" height="98" viewBox="0 0 120 140">
        <circle cx="60" cy="52" r="36" fill="#f8fafc" stroke="${h.suit}" stroke-width="4"/>
        <circle cx="60" cy="53" r="22" fill="#ffedd5"/>
        <ellipse cx="51" cy="52" rx="4.5" ry="5.5" fill="${h.eyes}"/><circle cx="49.5" cy="50" r="1.8" fill="#fff"/>
        <ellipse cx="69" cy="52" rx="4.5" ry="5.5" fill="${h.eyes}"/><circle cx="67.5" cy="50" r="1.8" fill="#fff"/>
        <path d="M 54 62 Q 60 67 66 62" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        ${h.head}
        <rect x="32" y="88" width="56" height="44" rx="14" fill="${h.suit}" stroke="${h.accent}" stroke-width="3.5"/>
        <circle cx="60" cy="108" r="7" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5"/>
        ${lockSvg}
      </svg>
      <div class="hero-name">${h.name}</div>
      <div class="hero-perk">${h.perk}</div>
      <div class="hero-status ${unlocked ? 'status-unlocked' : 'status-locked'}">
        ${unlocked ? (selected ? '✅ SELECTED' : '🔓 UNLOCKED') : `🔒 ${Math.floor(session.vaultCoins)} / ${h.unlockCoins} 🪙`}
      </div>
    `;
    card.onclick = () => {
      ensureAudio();
      if (unlocked) {
        session.heroKey = h.key;
        document.getElementById("hero-msg").innerText = "";
        playSfx(640, 0.12, "triangle", 0.07);
        renderHeroGrid();
        validateAgePage();
      } else {
        const needed = Math.max(0, h.unlockCoins - Math.floor(session.vaultCoins));
        document.getElementById("hero-msg").innerText = `❌ ${h.name} is locked! Collect ${needed} more Vault Coins on the Moon to unlock!`;
        playSfx(210, 0.16, "sawtooth", 0.07);
      }
    };
    grid.appendChild(card);
  });
}

function validateAgePage() {
  const raw = document.getElementById("age-input").value.trim();
  const fb = document.getElementById("age-feedback");
  const btn = document.getElementById("btn-to-inst");
  const num = parseInt(raw, 10);
  if (!raw || isNaN(num) || num < 1 || num > 100) {
    session.age = null;
    fb.style.color = "#fca5a5";
    fb.innerText = "👉 Please enter a valid age (1–100) to continue";
    btn.disabled = true;
  } else {
    session.age = num;
    if (num <= 9) session.ageTier = "7-9 Cadet";
    else if (num <= 12) session.ageTier = "10-12 Commander";
    else session.ageTier = "13+ Mission Planner";
    fb.style.color = "#86efac";
    fb.innerText = `✅ ${session.ageTier} Mode Ready`;
    btn.disabled = false;
  }
}

function goToAgePage() {
  ensureAudio();
  startBgmLoop();
  state.paused = true;
  session.screen = "AGE";
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("hero-msg").innerText = "";
  if (session.age) document.getElementById("age-input").value = session.age;
  renderHeroGrid();
  validateAgePage();
  showScreen("screen-age");
}

function goToInstructions() {
  if (!session.age) return;
  ensureAudio();
  playSfx(523, 0.14, "triangle", 0.08);
  session.screen = "INSTRUCTIONS";
  const h = getHero();
  document.getElementById("inst-hero-line").innerText = `Commander: ${h.name}  •  ${session.ageTier} Mode  •  Vault: ${Math.floor(session.vaultCoins)} 🪙`;
  showScreen("screen-instructions");
}

const STATIONS = {
  SOLAR:   { x: -13.5, z: 5.5,  r: 3.1, label: "☀️ Scrubbing Solar Dust...", color: 0xfacc15, tag: "☀️ SOLAR ARRAY" },
  ICE:     { x: -10.0, z: -8.5, r: 3.0, label: "🧊 Mining Crater Ice (+O₂, -⚡)...", color: 0x38bdf8, tag: "🧊 ICE CRATER" },
  SCIENCE: { x: 9.5,   z: 9.0,  r: 3.0, label: "🔬 Drilling Lunar Core (-O₂, +Sci)...", color: 0xd8b4fe, tag: "🔬 EVA SCIENCE" },
  FARM:    { x: 12.2,  z: -2.0, r: 3.3, label: "🌱 Harvesting CSA Crops...", color: 0x4ade80, tag: "🌱 CSA FARM" },
  PANTRY:  { x: 2.3,   z: -1.2, r: 2.2, label: "🍽️ Stocking Pantry Table...", color: 0xf472b6, tag: "🍽️ PANTRY" },
  SHIELD:  { x: -2.4,  z: -1.4, r: 2.2, label: "🛡️ Shield Console", color: 0x60a5fa, tag: "🛡️ SHIELD" }
};

let state = { started: false, paused: true, ended: false };
let telemetryLog = [];

function resetMissionState() {
  const diff = getDiff();
  state = {
    started: true,
    paused: false,
    ended: false,
    sol: 1,
    solClock: 0,
    power: 92,
    oxygen: 92,
    food: 86,
    hp: 100,
    rad: 0.42,
    science: 0,
    doorSealed: true,
    shieldOn: false,
    dusty: false,
    flarePhase: "CALM",
    flareTimer: diff.flareGap,
    basket: [],
    pantryCount: 3,
    crops: [100, 100, 70, 100],
    autoTarget: null,
    activePad: null,
    padProgress: 0,
    roverCooldown: 0,
    radioBusy: false,
    radioBeamTimer: 0,
    camWide: false,
    dilemmasShown: {}
  };
  telemetryLog = [{ sol: 1, pwr: 92, ox: 92, hp: 100 }];
}

let threeReady = false;
let scene, camera, renderer, clock;
let heroGroup, heroLimbs = {}, heroBasketGroup;
let sunMesh, sunGlow, dirLight, beaconLight, earthGroup, radioBeamMesh;
let shieldDomeMesh, shieldWireMesh, airlockDoorMesh, airlockGlowMat;
let solarDustMeshes = [], cropMeshes = [], pantryFoodGroup, roverGroup, drillCrystal;
let coinOrbs = [], flareParticles, fxParticles = [], shootingStar;
let padRings = {};
let heroPos = null, heroVelY = 0, heroRotY = 0, wasInside = true, footstepTimer = 0;
const keys = {};

function makeLunarTexture() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 512;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#64748b";
  ctx.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 6000; i++) {
    const shade = 75 + Math.floor(Math.random() * 55);
    ctx.fillStyle = `rgb(${shade},${shade+6},${shade+16})`;
    ctx.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
  }
  for (let i = 0; i < 45; i++) {
    const x = Math.random() * 512, y = Math.random() * 512, r = 6 + Math.random() * 26;
    const grad = ctx.createRadialGradient(x, y, r * 0.2, x, y, r);
    grad.addColorStop(0, "rgba(30,41,59,0.55)");
    grad.addColorStop(0.75, "rgba(100,116,139,0.2)");
    grad.addColorStop(1, "rgba(203,213,225,0.35)");
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(6, 6);
  return tex;
}

function makeFloatingLabel(text, borderHex) {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 64;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "rgba(9,13,31,0.86)";
  ctx.strokeStyle = borderHex;
  ctx.lineWidth = 5;
  ctx.beginPath(); ctx.roundRect(6, 8, 244, 48, 14); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#ffffff";
  ctx.font = "900 21px Segoe UI, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(text, 128, 40);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true }));
  sprite.scale.set(4.8, 1.2, 1);
  return sprite;
}

function buildHero3D() {
  if (heroGroup) scene.remove(heroGroup);
  const h = getHero();
  heroGroup = new THREE.Group();
  const suitMat = new THREE.MeshStandardMaterial({ color: h.suit, roughness: 0.35, metalness: 0.25 });
  const accMat  = new THREE.MeshStandardMaterial({ color: h.accent, roughness: 0.3, metalness: 0.35 });
  const whiteMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.25 });

  const torso = new THREE.Mesh(new THREE.BoxGeometry(0.95, 1.15, 0.6), suitMat);
  torso.position.y = 1.45; torso.castShadow = true; heroGroup.add(torso);

  const emblem = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.08, 16), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
  emblem.rotation.x = Math.PI / 2; emblem.position.set(0, 1.55, 0.31); heroGroup.add(emblem);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.54, 18, 18), whiteMat);
  head.position.y = 2.42; head.castShadow = true; heroGroup.add(head);

  const visor = new THREE.Mesh(
    new THREE.SphereGeometry(0.45, 16, 12, -Math.PI * 0.35, Math.PI * 0.7, Math.PI * 0.25, Math.PI * 0.42),
    new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1, metalness: 0.8 })
  );
  visor.position.set(0, 2.42, 0.15); heroGroup.add(visor);

  const eyeMat = new THREE.MeshBasicMaterial({ color: h.eyes });
  [-0.16, 0.16].forEach(ex => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), eyeMat);
    eye.position.set(ex, 2.44, 0.52); heroGroup.add(eye);
  });

  if (h.key === "CAP") {
    const shield = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.1, 20), accMat);
    shield.rotation.x = Math.PI / 2; shield.position.set(0, 1.5, -0.38); heroGroup.add(shield);
  } else if (h.key === "LOKI") {
    const hornMat = new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.8, roughness: 0.2 });
    [-0.3, 0.3].forEach(hx => {
      const horn = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.65, 8), hornMat);
      horn.position.set(hx, 3.05, 0.1); horn.rotation.z = hx > 0 ? -0.35 : 0.35; heroGroup.add(horn);
    });
  } else if (h.key === "THOR" || h.key === "STRANGE") {
    const cape = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.35, 0.08), accMat);
    cape.position.set(0, 1.25, -0.36); cape.rotation.x = 0.18; heroGroup.add(cape);
  } else if (h.key === "WANDA") {
    const crown = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.07, 8, 16), accMat);
    crown.rotation.x = Math.PI / 2; crown.position.set(0, 2.86, 0.05); heroGroup.add(crown);
  }

  const limbGeo = new THREE.BoxGeometry(0.28, 0.85, 0.28);
  heroLimbs.lArm = new THREE.Mesh(limbGeo, accMat); heroLimbs.lArm.position.set(-0.66, 1.4, 0);
  heroLimbs.rArm = new THREE.Mesh(limbGeo, accMat); heroLimbs.rArm.position.set(0.66, 1.4, 0);
  heroLimbs.lLeg = new THREE.Mesh(limbGeo, suitMat); heroLimbs.lLeg.position.set(-0.26, 0.45, 0);
  heroLimbs.rLeg = new THREE.Mesh(limbGeo, suitMat); heroLimbs.rLeg.position.set(0.26, 0.45, 0);
  heroGroup.add(heroLimbs.lArm, heroLimbs.rArm, heroLimbs.lLeg, heroLimbs.rLeg);

  heroBasketGroup = new THREE.Group(); heroBasketGroup.position.set(0, 1.5, -0.65);
  heroGroup.add(heroBasketGroup);

  heroGroup.position.copy(heroPos);
  scene.add(heroGroup);
  refreshBasketVisuals();
}

function init3D() {
  if (threeReady) return;
  const container = document.getElementById("canvas-container");
  const w = container.clientWidth || window.innerWidth || 1200;
  const h = container.clientHeight || 860;

  heroPos = new THREE.Vector3(0, 0, 1.5);
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  scene.fog = new THREE.FogExp2(0x04091a, 0.013);

  camera = new THREE.PerspectiveCamera(52, w / h, 0.1, 260);
  camera.position.set(0, 14, 21);

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  clock = new THREE.Clock();

  scene.add(new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.65));
  dirLight = new THREE.DirectionalLight(0xfff7ed, 1.5);
  dirLight.position.set(-28, 32, 16);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(1024, 1024);
  const d = 28;
  dirLight.shadow.camera.left = -d; dirLight.shadow.camera.right = d;
  dirLight.shadow.camera.top = d; dirLight.shadow.camera.bottom = -d;
  scene.add(dirLight);

  beaconLight = new THREE.PointLight(0x38bdf8, 1.2, 14);
  beaconLight.position.set(0, 4.5, 0);
  scene.add(beaconLight);

  const starGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(1400 * 3);
  const starCol = new Float32Array(1400 * 3);
  for (let i = 0; i < 1400; i++) {
    const r = 75 + Math.random() * 75;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(Math.random() * 0.85 + 0.12);
    starPos[i*3] = r * Math.sin(phi) * Math.cos(theta);
    starPos[i*3+1] = Math.abs(r * Math.cos(phi)) + 6;
    starPos[i*3+2] = r * Math.sin(phi) * Math.sin(theta);
    starCol[i*3] = Math.random() > 0.7 ? 1.0 : 0.8;
    starCol[i*3+1] = 0.9;
    starCol[i*3+2] = 1.0;
  }
  starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute("color", new THREE.BufferAttribute(starCol, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ size: 0.55, vertexColors: true })));

  shootingStar = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 3.8), new THREE.MeshBasicMaterial({ color: 0xbae6fd }));
  shootingStar.position.set(-40, 32, -50);
  scene.add(shootingStar);

  sunMesh = new THREE.Mesh(new THREE.SphereGeometry(5.2, 24, 24), new THREE.MeshBasicMaterial({ color: 0xfde047 }));
  sunMesh.position.set(-42, 34, -38);
  scene.add(sunMesh);
  sunGlow = new THREE.Mesh(new THREE.SphereGeometry(7.8, 24, 24), new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.28 }));
  sunGlow.position.copy(sunMesh.position);
  scene.add(sunGlow);

  earthGroup = new THREE.Group();
  earthGroup.position.set(34, 30, -45);
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(4.8, 28, 28), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.5 })));
  const landMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8 });
  [[-1.8, 1.4, 4.1, 1.9], [2.1, -0.8, 3.9, 1.6], [0.2, 2.8, -3.5, 1.8], [-2.5, -1.9, -3.2, 1.5]].forEach(c => {
    const patch = new THREE.Mesh(new THREE.SphereGeometry(c[3], 12, 12), landMat);
    patch.position.set(c[0], c[1], c[2]); patch.scale.set(1, 0.8, 0.5);
    earthGroup.add(patch);
  });
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(5.2, 24, 24), new THREE.MeshBasicMaterial({ color: 0x60a5fa, transparent: true, opacity: 0.18 })));
  scene.add(earthGroup);

  const groundGeo = new THREE.PlaneGeometry(115, 115, 52, 52);
  groundGeo.rotateX(-Math.PI / 2);
  const posAttr = groundGeo.attributes.position;
  for (let i = 0; i < posAttr.count; i++) {
    const x = posAttr.getX(i), z = posAttr.getZ(i);
    const dist = Math.hypot(x, z);
    let y = 0;
    if (dist > 20) y = Math.sin(x * 0.18) * Math.cos(z * 0.18) * 1.5 + (dist - 20) * 0.13;
    else if (Math.hypot(x + 10.0, z + 8.5) < 3.5) y = -0.35;
    posAttr.setY(i, y);
  }
  groundGeo.computeVertexNormals();
  const ground = new THREE.Mesh(groundGeo, new THREE.MeshStandardMaterial({ map: makeLunarTexture(), roughness: 0.95, metalness: 0.04 }));
  ground.receiveShadow = true;
  scene.add(ground);

  const rockMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 });
  [[-20, 12], [-18, -14], [19, 11], [21, -12], [5, 16], [-6, -18], [15, -15], [-2, 17]].forEach(([rx, rz]) => {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.0 + Math.random() * 1.3, 0), rockMat);
    rock.position.set(rx, 0.45, rz); rock.rotation.set(Math.random(), Math.random(), 0);
    rock.castShadow = true; rock.receiveShadow = true;
    scene.add(rock);
  });

  function addPath(x1, z1, x2, z2, col) {
    const len = Math.hypot(x2 - x1, z2 - z1);
    const p = new THREE.Mesh(new THREE.PlaneGeometry(len, 1.05), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.24 }));
    p.rotation.x = -Math.PI / 2;
    p.rotation.z = -Math.atan2(z2 - z1, x2 - x1);
    p.position.set((x1 + x2) / 2, 0.03, (z1 + z2) / 2);
    scene.add(p);
  }
  addPath(0, 6.2, -13.5, 5.5, 0xfacc15);
  addPath(0, 6.2, -10.0, -8.5, 0x38bdf8);
  addPath(0, 6.2, 9.5, 9.0, 0xd8b4fe);
  addPath(5.5, -1.5, 12.2, -2.0, 0x4ade80);

  const habFloor = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.2, 0.22, 32), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.45, metalness: 0.4 }));
  habFloor.position.set(0, 0.11, 0); habFloor.receiveShadow = true;
  scene.add(habFloor);

  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.0, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.5),
    new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.16, roughness: 0.1, side: THREE.DoubleSide })
  ));
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.05, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.5),
    new THREE.MeshBasicMaterial({ color: 0xe2e8f0, wireframe: true, transparent: true, opacity: 0.34 })
  ));

  const habLbl = makeFloatingLabel("🏠 ARTEMIS HABITAT", "#38bdf8");
  habLbl.position.set(0, 7.2, 0);
  scene.add(habLbl);

  const airlockFrame = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.8, 1.4), new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 }));
  airlockFrame.position.set(0, 1.4, 6.0); airlockFrame.castShadow = true;
  scene.add(airlockFrame);

  airlockGlowMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x16a34a, emissiveIntensity: 0.7 });
  airlockDoorMesh = new THREE.Mesh(new THREE.BoxGeometry(2.3, 2.3, 0.35), airlockGlowMat);
  airlockDoorMesh.position.set(0, 1.25, 6.0);
  scene.add(airlockDoorMesh);

  const beamDir = new THREE.Vector3().subVectors(earthGroup.position, new THREE.Vector3(0, 6.8, 0));
  radioBeamMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(0.16, 0.45, beamDir.length(), 10),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85 })
  );
  radioBeamMesh.position.copy(new THREE.Vector3(0, 6.8, 0)).add(beamDir.clone().multiplyScalar(0.5));
  radioBeamMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), beamDir.clone().normalize());
  radioBeamMesh.visible = false;
  scene.add(radioBeamMesh);

  const tableTop = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.25, 1.4), new THREE.MeshStandardMaterial({ color: 0xb45309 }));
  tableTop.position.set(2.3, 1.0, -1.2); tableTop.castShadow = true;
  scene.add(tableTop);
  pantryFoodGroup = new THREE.Group(); pantryFoodGroup.position.set(2.3, 1.25, -1.2);
  scene.add(pantryFoodGroup);
  refreshPantryVisuals();

  const consoleDesk = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 1.1), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, emissive: 0x1d4ed8, emissiveIntensity: 0.45 }));
  consoleDesk.position.set(-2.4, 0.6, -1.4);
  scene.add(consoleDesk);

  shieldDomeMesh = new THREE.Mesh(
    new THREE.SphereGeometry(7.9, 28, 18, 0, Math.PI * 2, 0, Math.PI * 0.52),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.25, side: THREE.DoubleSide })
  );
  shieldWireMesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(7.95, 2),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, wireframe: true, transparent: true, opacity: 0.48 })
  );
  shieldDomeMesh.visible = false; shieldWireMesh.visible = false;
  scene.add(shieldDomeMesh, shieldWireMesh);

  for (let i = 0; i < 3; i++) {
    const px = -15.5 + i * 2.2, pz = 4.2 + (i % 2) * 1.8;
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 1.8, 8), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
    pole.position.set(px, 0.9, pz); scene.add(pole);
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.12, 2.4), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, emissive: 0x1e3a8a, emissiveIntensity: 0.35, metalness: 0.6 }));
    panel.position.set(px, 1.9, pz); panel.rotation.x = 0.32; panel.castShadow = true; scene.add(panel);
    const dust = new THREE.Mesh(new THREE.BoxGeometry(1.92, 0.14, 2.42), new THREE.MeshStandardMaterial({ color: 0xa16207, transparent: true, opacity: 0.88 }));
    dust.position.set(px, 1.95, pz); dust.rotation.x = 0.32; dust.visible = false; scene.add(dust);
    solarDustMeshes.push(dust);
  }
  const sLbl = makeFloatingLabel("☀️ SOLAR ARRAY", "#facc15"); sLbl.position.set(-13.5, 4.3, 5.5); scene.add(sLbl);

  const iceMat = new THREE.MeshStandardMaterial({ color: 0x7dd3fc, emissive: 0x0284c7, emissiveIntensity: 0.65, roughness: 0.15 });
  [[-10.0, -8.5, 1.7], [-8.8, -9.2, 1.15], [-11.2, -8.0, 1.25], [-9.9, -7.2, 0.95]].forEach(([ix, iz, h]) => {
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.55, h, 6), iceMat);
    c.position.set(ix, h / 2 - 0.2, iz); c.castShadow = true; scene.add(c);
  });
  const iLbl = makeFloatingLabel("🧊 CRATER ICE (+O₂)", "#38bdf8"); iLbl.position.set(-10.0, 3.6, -8.5); scene.add(iLbl);

  const sciBase = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.9, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x3b0764, metalness: 0.5 }));
  sciBase.position.set(9.5, 0.18, 9.0); scene.add(sciBase);
  const drillTower = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.32, 2.6, 8), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.7 }));
  drillTower.position.set(9.5, 1.4, 9.0); drillTower.castShadow = true; scene.add(drillTower);
  drillCrystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.65, 0), new THREE.MeshStandardMaterial({ color: 0xd8b4fe, emissive: 0xa855f7, emissiveIntensity: 0.8 }));
  drillCrystal.position.set(9.5, 3.1, 9.0); scene.add(drillCrystal);
  const sciLbl = makeFloatingLabel("🔬 EVA SCIENCE (-O₂)", "#d8b4fe"); sciLbl.position.set(9.5, 4.6, 9.0); scene.add(sciLbl);

  const ghDome = new THREE.Mesh(new THREE.SphereGeometry(4.4, 20, 14, 0, Math.PI * 2, 0, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: 0x4ade80, transparent: true, opacity: 0.18, side: THREE.DoubleSide }));
  ghDome.position.set(12.2, 0, -2.0); scene.add(ghDome);
  const ghWire = new THREE.Mesh(new THREE.SphereGeometry(4.45, 10, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), new THREE.MeshBasicMaterial({ color: 0x86efac, wireframe: true, transparent: true, opacity: 0.36 }));
  ghWire.position.set(12.2, 0, -2.0); scene.add(ghWire);
  const gLbl = makeFloatingLabel("🌱 CSA GREENHOUSE", "#4ade80"); gLbl.position.set(12.2, 5.2, -2.0); scene.add(gLbl);

  const cropColors = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  [[-1.3, -1.1], [1.3, -1.1], [-1.3, 1.1], [1.3, 1.1]].forEach(([ox, oz], idx) => {
    const bed = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.35, 1.4), new THREE.MeshStandardMaterial({ color: 0x451a03 }));
    bed.position.set(12.2 + ox, 0.18, -2.0 + oz); scene.add(bed);
    const plant = new THREE.Group(); plant.position.set(12.2 + ox, 0.4, -2.0 + oz);
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, 0.8, 6), new THREE.MeshStandardMaterial({ color: 0x16a34a }));
    stem.position.y = 0.4;
    const fruit = new THREE.Mesh(new THREE.SphereGeometry(0.36, 12, 12), new THREE.MeshStandardMaterial({ color: cropColors[idx], emissive: cropColors[idx], emissiveIntensity: 0.35 }));
    fruit.position.y = 0.9;
    plant.add(stem, fruit); scene.add(plant);
    cropMeshes.push(plant);
  });

  Object.entries(STATIONS).forEach(([key, st]) => {
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(st.r * 0.65, st.r * 0.85, 32),
      new THREE.MeshBasicMaterial({ color: st.color, side: THREE.DoubleSide, transparent: true, opacity: 0.8 })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(st.x, 0.08, st.z);
    scene.add(ring);
    padRings[key] = ring;
  });

  roverGroup = new THREE.Group();
  const rBody = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.6, 1.2), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.4 }));
  rBody.position.y = 0.6; rBody.castShadow = true; roverGroup.add(rBody);
  const wMat = new THREE.MeshStandardMaterial({ color: 0x0f172a });
  [[-0.7, 0.65], [0.7, 0.65], [-0.7, -0.65], [0.7, -0.65]].forEach(([wx, wz]) => {
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.25, 12), wMat);
    wh.rotation.x = Math.PI / 2; wh.position.set(wx, 0.32, wz); roverGroup.add(wh);
  });
  roverGroup.position.set(0, 0, 12.5);
  scene.add(roverGroup);

  [[-7, 9.5], [4.5, 10.5], [-14.5, -2.5], [15.5, 5.5], [-3, -11.5], [6.5, -9.5]].forEach(([cx, cz]) => {
    const coin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.58, 0.58, 0.16, 16),
      new THREE.MeshStandardMaterial({ color: 0xfacc15, emissive: 0xca8a04, emissiveIntensity: 0.72, metalness: 0.7 })
    );
    coin.rotation.x = Math.PI / 2; coin.position.set(cx, 1.1, cz);
    coin.userData = { active: true, respawn: 0 };
    scene.add(coin); coinOrbs.push(coin);
  });

  const fpGeo = new THREE.BufferGeometry();
  const fpPos = new Float32Array(280 * 3);
  for (let i = 0; i < 280; i++) {
    fpPos[i*3] = (Math.random() - 0.5) * 46;
    fpPos[i*3+1] = Math.random() * 24;
    fpPos[i*3+2] = (Math.random() - 0.5) * 46;
  }
  fpGeo.setAttribute("position", new THREE.BufferAttribute(fpPos, 3));
  flareParticles = new THREE.Points(fpGeo, new THREE.PointsMaterial({ color: 0xff4500, size: 0.48, transparent: true, opacity: 0.92 }));
  flareParticles.visible = false;
  scene.add(flareParticles);

  buildHero3D();
  threeReady = true;
  animate3D();
}

function resize3D() {
  if (!threeReady) return;
  const container = document.getElementById("canvas-container");
  const w = container.clientWidth || window.innerWidth;
  const h = container.clientHeight || 860;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}
window.addEventListener("resize", () => { initBgStars(); resize3D(); });

function refreshBasketVisuals() {
  if (!heroBasketGroup) return;
  while (heroBasketGroup.children.length) heroBasketGroup.remove(heroBasketGroup.children[0]);
  if (!state.basket || state.basket.length === 0) return;
  heroBasketGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.45, 0.5), new THREE.MeshStandardMaterial({ color: 0x92400e })));
  const colMap = { "🍅": 0xef4444, "🥬": 0x22c55e, "🥕": 0xf97316, "🥔": 0xeab308 };
  state.basket.forEach((icon, i) => {
    const v = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), new THREE.MeshStandardMaterial({ color: colMap[icon] || 0x4ade80, emissive: colMap[icon] || 0x4ade80, emissiveIntensity: 0.35 }));
    v.position.set((i % 2 - 0.5) * 0.3, 0.3 + Math.floor(i / 2) * 0.28, 0);
    heroBasketGroup.add(v);
  });
}

function refreshPantryVisuals() {
  if (!pantryFoodGroup) return;
  while (pantryFoodGroup.children.length) pantryFoodGroup.remove(pantryFoodGroup.children[0]);
  const cols = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  for (let i = 0; i < Math.min(6, state.pantryCount || 0); i++) {
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 10), new THREE.MeshStandardMaterial({ color: cols[i % 4] }));
    f.position.set(-0.75 + (i % 3) * 0.75, 0.1, i >= 3 ? 0.35 : -0.35);
    pantryFoodGroup.add(f);
  }
}

function spawnFxPuff(x, y, z, colorHex=0xcbd5e1, size=0.4) {
  if (!threeReady) return;
  const puff = new THREE.Mesh(
    new THREE.SphereGeometry(size, 8, 8),
    new THREE.MeshBasicMaterial({ color: colorHex, transparent: true, opacity: 0.75 })
  );
  puff.position.set(x, y, z);
  puff.userData = { life: 0.45 };
  scene.add(puff);
  fxParticles.push(puff);
}

function launchGameScreen() {
  ensureAudio();
  startBgmLoop();
  session.screen = "GAME";
  showScreen("screen-game");
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("debrief-modal").style.display = "none";
  document.getElementById("dilemma-modal").style.display = "none";
  document.getElementById("math-modal").style.display = "none";
  document.getElementById("nasa-modal").style.display = "none";
  document.getElementById("flare-alarm").style.display = "none";

  resetMissionState();
  const h = getHero();
  document.getElementById("sb-hero").innerText = h.name;
  document.getElementById("sb-mode").innerText = session.ageTier;
  document.getElementById("nasa-feed-btn").innerText =
    NASA.flr.live ? `🟢 LIVE DONKI ${NASA.flr.class}` : `🟡 ARCHIVED DONKI ${NASA.flr.class}`;
  syncMusicButtons();
  syncVaultDisplays();

  function boot3D() {
    if (typeof THREE !== "undefined") {
      init3D();
      resize3D();
      heroPos.set(0, 0, 1.5);
      wasInside = true;
      buildHero3D();
      refreshPantryVisuals();
      updateHUD();
      drawMinimap();
      playSfx(440, 0.25, "triangle", 0.09, 880);
      setStatus(`🚀 Mission Live as ${h.name}! Every coin earned on the Moon adds directly to your Vault!`);
      document.getElementById("game-root").focus();
    } else {
      setTimeout(boot3D, 120);
    }
  }
  boot3D();
}

function toggleSidebar() {
  const sb = document.getElementById("game-sidebar");
  sb.classList.toggle("open");
  syncVaultDisplays();
}

function sidebarChangeAgeHero() {
  goToAgePage();
}

function sidebarGoInstructions() {
  state.paused = true;
  document.getElementById("game-sidebar").classList.remove("open");
  goToInstructions();
}

function restartCurrentRun() {
  launchGameScreen();
}

function debriefChangeHero() {
  document.getElementById("debrief-modal").style.display = "none";
  goToAgePage();
}

function quitAndResetGame() {
  state.paused = true;
  state.ended = true;
  session.age = null;
  session.ageTier = "10-12 Commander";
  session.heroKey = "CAP";
  session.vaultCoins = 40;
  session.unlocked = ["CAP", "WIDOW"];
  session.wins = 0;
  document.getElementById("age-input").value = "";
  document.getElementById("game-sidebar").classList.remove("open");
  startFiveSecondLoader();
}

function openGlossary(key) {
  const g = GLOSSARY[key] || GLOSSARY.SOL;
  document.getElementById("gl-title").innerText = g.title;
  document.getElementById("gl-body").innerText = g.body;
  document.getElementById("glossary-pop").style.display = "block";
  playSfx(620, 0.1, "sine", 0.06);
}
function closeGlossary() { document.getElementById("glossary-pop").style.display = "none"; }

function openMathLab() {
  state.paused = true;
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("math-modal").style.display = "flex";
  updateMathLab();
}
function openNasaModal() {
  state.paused = true;
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("nasa-data-body").innerHTML = `
    <p><b>☀️ NASA DONKI Solar Flare Feed:</b> <code>${NASA.flr.id}</code> (Class <code>${NASA.flr.class}</code>) — <b>${NASA.flr.source}</b></p>
    <p style="margin-top:8px;"><b>🌊 NASA DONKI CME Feed:</b> <code>${NASA.cme.id}</code> (Speed <code>${NASA.cme.speed} km/s</code>) — <b>${NASA.cme.source}</b></p>
    <p style="margin-top:8px;"><b>☢️ NASA RadLab BLEO &amp; OSDR (OSD-137, OSD-767, OSD-895):</b> Lunar surface baseline radiation calibrated at <code>0.42 mSv/Sol</code>, paired with spaceflight crop biology models.</p>
    <p style="margin-top:8px;"><b>🤝 Partner Space Agencies:</b> Canadian Space Agency (CSA) Deep Space Food Toolkit (4-crop hydroponics), ISRO Chandrayaan-3 South Pole regolith &amp; water-ice research, and ESA lunar communications delay physics (<code>2.56s</code> round-trip across 384,400 km).</p>
  `;
  document.getElementById("nasa-modal").style.display = "flex";
}
function closeModal(id) {
  document.getElementById(id).style.display = "none";
  if (!state.ended && document.getElementById("dilemma-modal").style.display !== "flex") {
    state.paused = false;
  }
  document.getElementById("game-root").focus();
}

function updateMathLab() {
  const sh = Number(document.getElementById("sl-sh").value);
  const fm = Number(document.getElementById("sl-fm").value);
  const ev = Number(document.getElementById("sl-ev").value);
  const ds = Number(document.getElementById("sl-ds").value);
  document.getElementById("sl-sh-v").innerText = sh + "%";
  document.getElementById("sl-fm-v").innerText = fm + "%";
  document.getElementById("sl-ev-v").innerText = ev + " hrs";
  document.getElementById("sl-ds-v").innerText = ds + "%";

  const pts = [];
  let p = 92, o = 92, r = 0.42;
  for (let s = 1; s <= 7; s++) {
    const solarIn = 32 * (1 - ds / 100);
    p = Math.max(0, Math.min(100, p + solarIn - (sh * 0.34 + fm * 0.15 + ev * 1.5 + 4)));
    o = Math.max(0, Math.min(100, o + fm * 0.14 - (8 + ev * 2.4)));
    r += 0.42 + ev * 0.08 + ((s === 3 || s === 6) ? 1.8 * (1 - sh / 100) : 0);
    pts.push({ p, o, r });
  }
  const c = document.getElementById("math-chart");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  for (let y = 25; y <= 155; y += 32.5) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif";
  ctx.fillText("100%", 6, 28); ctx.fillText("50%", 12, 93); ctx.fillText("0%", 18, 158);
  function plot(k, col) {
    ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath();
    pts.forEach((pt, idx) => {
      const x = 45 + (idx / 6) * 525;
      const y = 155 - (pt[k] / 100) * 130;
      if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
  plot("p", "#facc15"); plot("o", "#38bdf8");
  ctx.fillStyle = "#facc15"; ctx.fillText("■ Projected Power %", 350, 16);
  ctx.fillStyle = "#38bdf8"; ctx.fillText("■ Projected Oxygen %", 475, 16);
  const last = pts[6];
  document.getElementById("math-summary").innerText =
    `Projected Sol 7 Status: Power ${Math.round(last.p)}% | Oxygen ${Math.round(last.o)}% | Cumulative Crew Radiation ${last.r.toFixed(2)} mSv`;
}

const DILEMMAS = {
  2: {
    title: "🔬 Deep Crater Discovery: Oxygen vs. Research!",
    desc: "Orbital radar spotted ancient lunar volcanic glass and frozen water-ice deeper inside Shackleton Crater! Drilling takes heavy EVA exertion.",
    choices: [
      {
        label: "A) Run Deep EVA Core Drill",
        tradeoff: "Cost: -16% 🫁 O₂ & +0.25 mSv  |  Reward: +300 🔬 Science & +35 🪙 Vault Coins",
        apply: () => { state.oxygen = Math.max(5, state.oxygen - 16); state.rad += 0.25; state.science += 300; addVaultCoins(35); setStatus("🔬 Deep EVA succeeded! +300 Science & +35 Vault Coins (-16% O₂)!"); }
      },
      {
        label: "B) Send Autonomous Rover Camera Instead",
        tradeoff: "Cost: -12% ⚡ Power  |  Reward: +110 🔬 Science & +15 🪙 Vault Coins",
        apply: () => { state.power = Math.max(5, state.power - 12); state.science += 110; addVaultCoins(15); setStatus("🚙 Rover scan saved Oxygen! +110 Science & +15 Vault Coins (-12% Power)."); }
      }
    ]
  },
  4: {
    title: `🌊 NASA DONKI CME Alert (${NASA.cme.speed} km/s): Shield vs. Greenhouse!`,
    desc: `NASA DONKI logged Coronal Mass Ejection ${NASA.cme.id}! Peak power cannot max out both magnetic shielding and CSA Greenhouse grow-lights tonight.`,
    choices: [
      {
        label: "A) Reinforce Magnetic Dome Shielding",
        tradeoff: "Cost: -20% ⚡ Power & -10% 🍽️ Food  |  Reward: Blocks CME & +25 🪙 Vault Coins",
        apply: () => { state.power = Math.max(5, state.power - 20); state.food = Math.max(8, state.food - 10); state.science += 100; addVaultCoins(25); state.flarePhase = "CALM"; state.flareTimer = 14; setStatus("🛡️ CME deflected! +25 Vault Coins (-20% Power)."); }
      },
      {
        label: "B) Prioritize CSA Greenhouse Grow-Lights",
        tradeoff: "Cost: +0.95 mSv & -14% ❤️ HP  |  Reward: +22% 🍽️ Food, +15% 🫁 O₂ & +20 🪙",
        apply: () => { state.rad += 0.95; state.hp = Math.max(10, state.hp - 14); state.food = Math.min(100, state.food + 22); state.oxygen = Math.min(100, state.oxygen + 15); addVaultCoins(20); setStatus("🌱 Greenhouse thrived (+22% Food), crew absorbed CME radiation!"); }
      }
    ]
  },
  6: {
    title: "📡 Micrometeoroid Hit Solar Inverter — Comms Delay Choice!",
    desc: "A space rock cracked an inverter outside! Earth HQ is 384,400 km away (2.6s light delay). How will you respond?",
    choices: [
      {
        label: "A) Rush Outside for Manual EVA Patch",
        tradeoff: "Cost: -14% 🫁 O₂ & +0.20 mSv  |  Reward: +15% ⚡ Power, +180 🔬 & +30 🪙",
        apply: () => { state.oxygen = Math.max(5, state.oxygen - 14); state.rad += 0.20; state.power = Math.min(100, state.power + 15); state.science += 180; addVaultCoins(30); setStatus("🛠️ Bold EVA repair restored +15% Power & +30 Vault Coins!"); }
      },
      {
        label: "B) Wait for Earth HQ Remote Software Reroute",
        tradeoff: "Cost: -16% ⚡ Power drained while waiting  |  Reward: Zero Risk & +25 🪙 Vault Coins",
        apply: () => { state.power = Math.max(5, state.power - 16); addVaultCoins(25); setStatus("📡 Earth HQ rerouted power safely! +25 Vault Coins."); }
      }
    ]
  }
};

function triggerDilemma(solNum) {
  const d = DILEMMAS[solNum];
  if (!d) return;
  state.paused = true;
  playSfx(392, 0.25, "triangle", 0.09, 523);
  document.getElementById("dil-sol").innerText = `LUNAR SOL ${solNum}`;
  document.getElementById("dil-title").innerText = d.title;
  document.getElementById("dil-desc").innerText = d.desc;
  const wrap = document.getElementById("dil-choices");
  wrap.innerHTML = "";
  d.choices.forEach(ch => {
    const btn = document.createElement("button");
    btn.className = "choice-btn";
    btn.innerHTML = `<div style="font-size:13.5px;font-weight:900;color:#fde047;">${ch.label}</div>
                     <div style="font-size:11.5px;color:#93c5fd;margin-top:3px;font-weight:700;">${ch.tradeoff}</div>`;
    btn.onclick = () => {
      ch.apply();
      state.paused = false;
      document.getElementById("dilemma-modal").style.display = "none";
      playSfx(660, 0.18, "sine", 0.08, 880);
      updateHUD();
      document.getElementById("game-root").focus();
    };
    wrap.appendChild(btn);
  });
  document.getElementById("dilemma-modal").style.display = "flex";
}

function showComic(badge, title, body, ms=2400) {
  const el = document.getElementById("comic-toast");
  document.getElementById("comic-badge").innerText = badge;
  document.getElementById("comic-title").innerText = title;
  document.getElementById("comic-body").innerText = body;
  el.style.display = "block";
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.style.display = "none"; }, ms);
}
function setStatus(msg) { document.getElementById("status-msg").innerText = msg; }
function isInsideHabitat() { return heroPos ? Math.hypot(heroPos.x, heroPos.z) < 5.9 : true; }

function autoRunTo(stationKey) {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  const st = STATIONS[stationKey];
  if (!st) return;
  state.autoTarget = new THREE.Vector3(st.x, 0, st.z);
  playSfx(480, 0.1, "triangle", 0.06);
  setStatus(`🏃 Auto-running to ${st.tag}...`);
  document.getElementById("game-root").focus();
}

function triggerJump() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  if (heroPos.y <= 0.02) {
    heroVelY = (session.heroKey === "IRON") ? 8.4 : 6.5;
    playSfx(260, 0.22, "sine", 0.08, 540);
    spawnFxPuff(heroPos.x, 0.3, heroPos.z, 0x38bdf8, 0.45);
  }
}

function toggleCameraMode() { state.camWide = !state.camWide; playSfx(520, 0.08, "sine", 0.05); }

function toggleDoor() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  if (!isInsideHabitat() && !state.doorSealed) {
    setStatus("⚠️ Run inside the Habitat Dome first before sealing the Airlock Door!");
    playSfx(200, 0.15, "sawtooth", 0.06);
    return;
  }
  state.doorSealed = !state.doorSealed;
  playSfx(state.doorSealed ? 660 : 320, 0.16, "square", 0.07);
  setStatus(state.doorSealed ? "🔒 Airlock Door SEALED! Cabin Oxygen locked in." : "🔓 Airlock Door OPENED — seal when back inside!");
  updateHUD();
}

function toggleShield() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  if (!state.shieldOn && state.power < 8) {
    setStatus("⚠️ Battery Power too low for Vibranium Shield! Scrub Solar Array or call Earth HQ!");
    playSfx(180, 0.2, "sawtooth", 0.08);
    return;
  }
  state.shieldOn = !state.shieldOn;
  if (state.shieldOn) {
    const cost = (session.heroKey === "CAP") ? 5 : 10;
    state.power = Math.max(0, state.power - cost);
    playSfx(320, 0.3, "sawtooth", 0.08, 760);
    showComic("🛡️⚡", "VIBRANIUM SHIELD ON!", "Blocking NASA DONKI radiation! Turn OFF after storm to save Power.");
    setStatus(`🛡️ Shield RAISED (-${cost}% startup Power)! Turn OFF after the flare passes.`);
  } else {
    playSfx(540, 0.18, "sine", 0.07, 260);
    setStatus("🟢 Shield turned OFF! Solar panels are recharging battery power.");
  }
  updateHUD();
}

function deployRoverScan() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  if (state.roverCooldown > 0) { setStatus(`🚙 Rover recharging... ready in ${Math.ceil(state.roverCooldown)}s.`); return; }
  if (state.power < 6) { setStatus("⚠️ Need 6% Power for a Lunar Rover scan!"); return; }
  state.power = Math.max(0, state.power - 6);
  const gain = (session.heroKey === "LOKI") ? 45 : 22;
  addVaultCoins(gain);
  state.science += 45;
  state.roverCooldown = 10;
  playSfx(740, 0.22, "triangle", 0.08, 980);
  showComic("🚙🪙", "ROVER SCAN COMPLETE!", `+${gain} Vault Coins & +45 Science (-6% Power)!`, 2000);
  setStatus(`🚙 Rover mapped crater rim: +${gain} 🪙 added to Vault (-6% Power)!`);
}

function callEarth(preset) {
  if (session.screen !== "GAME" || state.ended || state.paused || state.radioBusy) return;
  const cost = (session.heroKey === "STRANGE") ? 10 : 15;
  const delayMs = (session.heroKey === "STRANGE") ? 1000 : 2600;
  if (session.vaultCoins < cost) {
    document.getElementById("radio-log").innerText = `⚠️ Need ${cost} 🪙! Grab spinning Moon Coins or run Rover Scan!`;
    playSfx(210, 0.15, "sawtooth", 0.06);
    return;
  }
  session.vaultCoins -= cost;
  syncVaultDisplays();
  state.radioBusy = true;
  state.radioBeamTimer = delayMs / 1000;
  playSfx(440, 0.15, "sine", 0.08, 880);
  document.getElementById("radio-log").innerText = `📡 Signal traveling 384,400 km to Earth HQ... (${(delayMs / 1000).toFixed(1)}s light delay)`;

  setTimeout(() => {
    state.radioBusy = false;
    if (state.ended) return;
    playSfx(880, 0.25, "triangle", 0.09, 1180);
    if (preset === 1) { state.power = Math.min(100, state.power + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Arc Battery Pod landed (+30% ⚡)!"; }
    else if (preset === 2) { state.oxygen = Math.min(100, state.oxygen + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Emergency O₂ Tank delivered (+30% 🫁)!"; }
    else if (preset === 3) { state.food = Math.min(100, state.food + 30); state.pantryCount = Math.min(6, state.pantryCount + 2); refreshPantryVisuals(); document.getElementById("radio-log").innerText = "🌍 Earth HQ: CSA Hydroponic Ration Drop (+30% 🍽️)!"; }
    else if (preset === 4) { state.hp = Math.min(100, state.hp + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Nano-Medkit restored +30% ❤️ HP!"; }
    else { state.flarePhase = "CALM"; state.flareTimer = getDiff().flareGap; document.getElementById("flare-alarm").style.display = "none"; document.getElementById("radio-log").innerText = "🌍 NASA DONKI Forecast: Solar storm cleared!"; }
    updateHUD();
  }, delayMs);
}

function advanceSolEarly() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  state.solClock = getDiff().solSecs - 0.08;
  playSfx(523, 0.2, "triangle", 0.08);
}

function completePadAction(key) {
  const coinMult = (session.heroKey === "LOKI") ? 2 : 1;
  if (key === "SOLAR") {
    state.dusty = false;
    state.power = Math.min(100, state.power + 24);
    const g = 14 * coinMult;
    addVaultCoins(g);
    playSfx(784, 0.2, "triangle", 0.09, 1046);
    showComic("🧹☀️", "SOLAR ARRAY CLEAN!", `+24% Power & +${g} 🪙 Vault Coins!`, 2000);
    setStatus(`🧹 Swept lunar dust off Solar Array! +${g} 🪙 added to Vault.`);
  } else if (key === "ICE") {
    if (state.power < 10) { setStatus("⚠️ Need at least 10% ⚡ Power to run Ice Electrolysis!"); return; }
    state.power = Math.max(0, state.power - 10);
    state.oxygen = Math.min(100, state.oxygen + 26);
    const g = 10 * coinMult;
    addVaultCoins(g);
    playSfx(620, 0.22, "sine", 0.08, 920);
    showComic("🧊🫁", "ICE ELECTROLYSIS!", `+26% O₂ & +${g} 🪙 Vault Coins (-10% Power)!`, 2000);
    setStatus(`🫁 Melted Crater Ice (+26% O₂) & earned +${g} 🪙 Vault Coins!`);
  } else if (key === "SCIENCE") {
    if (state.oxygen < 18 || state.power < 10) {
      setStatus("⚠️ Too risky! Need ≥18% 🫁 O₂ & ≥10% ⚡ Power for EVA Core Drilling!");
      playSfx(200, 0.2, "sawtooth", 0.08);
      return;
    }
    const sciGain = (session.heroKey === "LOKI") ? 300 : 200;
    const g = 24 * coinMult;
    state.oxygen = Math.max(0, state.oxygen - 14);
    state.power = Math.max(0, state.power - 8);
    state.rad += 0.18;
    state.science += sciGain;
    addVaultCoins(g);
    playSfx(520, 0.25, "sawtooth", 0.07, 1040);
    spawnFxPuff(9.5, 1.5, 9.0, 0xd8b4fe, 0.65);
    showComic("🔬🌕", "CORE SAMPLE DRILLED!", `+${sciGain} Science & +${g} 🪙 Vault Coins (-14% O₂)!`, 2400);
    setStatus(`🔬 Drilled regolith core (+${sciGain} Science, +${g} 🪙 Vault Coins) at -14% O₂!`);
  } else if (key === "FARM") {
    const icons = ["🍅", "🥬", "🥕", "🥔"];
    let picked = 0;
    for (let i = 0; i < 4; i++) {
      if (state.crops[i] >= 95 && state.basket.length < 4) {
        state.basket.push(icons[i]); state.crops[i] = 5;
        state.power = Math.max(0, state.power - 2);
        state.oxygen = Math.min(100, state.oxygen + (session.heroKey === "WANDA" ? 6 : 2));
        picked++;
      }
    }
    if (picked > 0) {
      refreshBasketVisuals();
      playSfx(698, 0.18, "sine", 0.09, 987);
      showComic("🧺🍅🥬", "CSA HARVEST!", `Picked ${picked} fresh crops! Run to the Pantry Table inside!`, 2100);
      setStatus(`🧺 Harvested ${picked} CSA crops into your Basket! Stock the Pantry Table.`);
    } else if (state.basket.length >= 4) {
      setStatus("🧺 Basket full (4/4)! Run to the Pantry Table inside!");
    } else {
      setStatus("🌱 Space veggies still growing under hydroponic LEDs...");
    }
  } else if (key === "PANTRY") {
    if (state.basket.length === 0) { setStatus("🧺 Basket empty! Visit the CSA Greenhouse to harvest ripe crops."); return; }
    const n = state.basket.length;
    state.basket = [];
    state.pantryCount = Math.min(6, state.pantryCount + n);
    state.food = Math.min(100, state.food + n * 13);
    const g = n * 10 * coinMult;
    addVaultCoins(g);
    state.science += n * 25;
    refreshBasketVisuals(); refreshPantryVisuals();
    playSfx(880, 0.25, "triangle", 0.09, 1320);
    showComic("🍽️✨", "PANTRY STOCKED!", `+${n*13}% Food & +${g} 🪙 Vault Coins!`, 2100);
    setStatus(`🍽️ Stocked Pantry Table! +${g} 🪙 added to your Vault.`);
  } else if (key === "SHIELD") {
    toggleShield();
  }
}

function drawMinimap() {
  const c = document.getElementById("minimap");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  if (!heroPos) return;
  const mx = x => (x + 22) / 44 * c.width;
  const mz = z => (z + 18) / 36 * c.height;

  ctx.strokeStyle = "rgba(56,189,248,0.65)"; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(mx(0), mz(0), 17, 0, Math.PI * 2); ctx.stroke();

  const stCols = { SOLAR: "#facc15", ICE: "#38bdf8", SCIENCE: "#d8b4fe", FARM: "#4ade80", PANTRY: "#f472b6", SHIELD: "#60a5fa" };
  Object.entries(STATIONS).forEach(([k, st]) => {
    ctx.fillStyle = stCols[k];
    ctx.beginPath(); ctx.arc(mx(st.x), mz(st.z), 4.2, 0, Math.PI * 2); ctx.fill();
  });

  ctx.fillStyle = "#fef08a";
  coinOrbs.forEach(co => {
    if (co.userData.active) ctx.fillRect(mx(co.position.x) - 1.5, mz(co.position.z) - 1.5, 3, 3);
  });

  ctx.fillStyle = "#ffffff";
  ctx.beginPath(); ctx.arc(mx(heroPos.x), mz(heroPos.z), 4.8, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 2; ctx.stroke();
}

function animate3D() {
  requestAnimationFrame(animate3D);
  if (session.screen !== "GAME") return;
  const dt = Math.min(0.05, clock.getDelta());
  const t = clock.elapsedTime;
  const diff = getDiff();

  earthGroup.rotation.y += dt * 0.08;
  drillCrystal.rotation.y += dt * 1.8;
  drillCrystal.position.y = 3.1 + Math.sin(t * 2.5) * 0.2;

  roverGroup.position.x = Math.sin(t * 0.35) * 8.5;
  roverGroup.rotation.y = Math.cos(t * 0.35) > 0 ? Math.PI / 2 : -Math.PI / 2;

  shootingStar.position.x += dt * 28;
  shootingStar.position.y -= dt * 6;
  if (shootingStar.position.x > 65) {
    shootingStar.position.set(-55 - Math.random() * 30, 26 + Math.random() * 14, -45 - Math.random() * 20);
  }

  Object.values(padRings).forEach((ring, idx) => {
    const s = 1 + Math.sin(t * 3.5 + idx) * 0.06;
    ring.scale.set(s, s, 1);
  });

  shieldDomeMesh.visible = state.shieldOn;
  shieldWireMesh.visible = state.shieldOn;
  if (state.shieldOn) shieldWireMesh.rotation.y += dt * 0.25;

  const targetDoorY = state.doorSealed ? 1.25 : 3.35;
  airlockDoorMesh.position.y += (targetDoorY - airlockDoorMesh.position.y) * Math.min(1, dt * 8);
  airlockGlowMat.color.setHex(state.doorSealed ? 0x22c55e : 0xef4444);
  airlockGlowMat.emissive.setHex(state.doorSealed ? 0x16a34a : 0xb91c1c);
  solarDustMeshes.forEach(m => { m.visible = state.dusty; });

  if (state.radioBeamTimer > 0) {
    state.radioBeamTimer -= dt;
    radioBeamMesh.visible = true;
    radioBeamMesh.material.opacity = 0.55 + Math.sin(t * 25) * 0.3;
  } else {
    radioBeamMesh.visible = false;
  }

  if (state.flarePhase === "WARN") {
    sunMesh.scale.setScalar(1.28 + Math.sin(t * 10) * 0.08);
    sunMesh.material.color.setHex(0xf97316);
    scene.fog.color.setHex(0x2a0a0a);
    beaconLight.color.setHex(0xef4444);
    beaconLight.intensity = 1.2 + Math.sin(t * 12) * 1.1;
    flareParticles.visible = false;
  } else if (state.flarePhase === "ACTIVE") {
    sunMesh.scale.setScalar(1.58);
    sunMesh.material.color.setHex(0xef4444);
    scene.fog.color.setHex(0x450a0a);
    beaconLight.color.setHex(0xef4444);
    beaconLight.intensity = 2.2 + Math.sin(t * 16) * 1.2;
    flareParticles.visible = true;
    const arr = flareParticles.geometry.attributes.position.array;
    for (let i = 1; i < arr.length; i += 3) { arr[i] -= dt * 19; if (arr[i] < 0) arr[i] = 24; }
    flareParticles.geometry.attributes.position.needsUpdate = true;
  } else {
    sunMesh.scale.setScalar(1.0);
    sunMesh.material.color.setHex(0xfde047);
    scene.fog.color.setHex(0x04091a);
    beaconLight.color.setHex(0x38bdf8);
    beaconLight.intensity = 1.1;
    flareParticles.visible = false;
  }

  for (let i = fxParticles.length - 1; i >= 0; i--) {
    const p = fxParticles[i];
    p.userData.life -= dt;
    p.position.y += dt * 0.9;
    p.scale.addScalar(dt * 1.5);
    p.material.opacity = Math.max(0, p.userData.life * 1.5);
    if (p.userData.life <= 0) { scene.remove(p); fxParticles.splice(i, 1); }
  }

  if (state.started && !state.ended && !state.paused) {
    let moveX = 0, moveZ = 0;
    if (keys["KeyW"] || keys["ArrowUp"])    moveZ -= 1;
    if (keys["KeyS"] || keys["ArrowDown"])  moveZ += 1;
    if (keys["KeyA"] || keys["ArrowLeft"])  moveX -= 1;
    if (keys["KeyD"] || keys["ArrowRight"]) moveX += 1;

    if (moveX !== 0 || moveZ !== 0) state.autoTarget = null;
    else if (state.autoTarget) {
      const dx = state.autoTarget.x - heroPos.x, dz = state.autoTarget.z - heroPos.z;
      const dist = Math.hypot(dx, dz);
      if (dist < 0.45) state.autoTarget = null;
      else { moveX = dx / dist; moveZ = dz / dist; }
    }

    const runSpeed = (session.heroKey === "WIDOW") ? 10.6 : 8.5;
    if (Math.hypot(moveX, moveZ) > 0.05) {
      const len = Math.hypot(moveX, moveZ); moveX /= len; moveZ /= len;
      heroPos.x = Math.max(-21, Math.min(21, heroPos.x + moveX * runSpeed * dt));
      heroPos.z = Math.max(-17, Math.min(17, heroPos.z + moveZ * runSpeed * dt));
      const desiredRot = Math.atan2(moveX, moveZ);
      heroRotY += Math.atan2(Math.sin(desiredRot - heroRotY), Math.cos(desiredRot - heroRotY)) * Math.min(1, dt * 12);

      heroLimbs.lLeg.rotation.x = Math.sin(t * 14) * 0.7;
      heroLimbs.rLeg.rotation.x = -Math.sin(t * 14) * 0.7;
      heroLimbs.lArm.rotation.x = -Math.sin(t * 14) * 0.6;
      heroLimbs.rArm.rotation.x = Math.sin(t * 14) * 0.6;

      footstepTimer -= dt;
      if (footstepTimer <= 0 && heroPos.y <= 0.05) {
        footstepTimer = 0.28;
        spawnFxPuff(heroPos.x, 0.12, heroPos.z, 0x94a3b8, 0.22);
      }
    } else {
      heroLimbs.lLeg.rotation.x *= 0.85; heroLimbs.rLeg.rotation.x *= 0.85;
      heroLimbs.lArm.rotation.x *= 0.85; heroLimbs.rArm.rotation.x *= 0.85;
    }

    heroPos.y += heroVelY * dt;
    if (heroPos.y > 0) {
      heroVelY -= 11.4 * dt;
      if (Math.random() < 0.45) spawnFxPuff(heroPos.x, heroPos.y + 0.3, heroPos.z, 0x38bdf8, 0.16);
    } else { heroPos.y = 0; heroVelY = 0; }
    heroGroup.position.copy(heroPos);
    heroGroup.rotation.y = heroRotY;

    const nowInside = isInsideHabitat();
    if (wasInside && !nowInside && state.doorSealed) {
      state.doorSealed = false;
      playSfx(310, 0.14, "square", 0.06);
      setStatus("🌑 Stepped outside onto Shackleton Crater! Seal Airlock when back inside!");
    }
    wasInside = nowInside;

    coinOrbs.forEach(c => {
      if (c.userData.active) {
        c.rotation.z += dt * 3.0;
        c.position.y = 1.0 + Math.sin(t * 3 + c.position.x) * 0.22;
        if (Math.hypot(heroPos.x - c.position.x, heroPos.z - c.position.z) < 1.45) {
          c.userData.active = false; c.visible = false; c.userData.respawn = 14;
          const gain = (session.heroKey === "LOKI") ? 30 : 15;
          addVaultCoins(gain);
          playSfx(987, 0.16, "sine", 0.09, 1318);
          spawnFxPuff(c.position.x, 1.1, c.position.z, 0xfde047, 0.55);
          setStatus(`🪙 Picked up Moon Coin Orb (+${gain} 🪙 added directly to Vault)!`);
        }
      } else {
        c.userData.respawn -= dt;
        if (c.userData.respawn <= 0) { c.userData.active = true; c.visible = true; }
      }
    });

    let stoodPad = null;
    for (const [key, st] of Object.entries(STATIONS)) {
      if (Math.hypot(heroPos.x - st.x, heroPos.z - st.z) < st.r) { stoodPad = key; break; }
    }
    const progWrap = document.getElementById("pad-progress-wrap");
    if (stoodPad) {
      if (state.activePad !== stoodPad) { state.activePad = stoodPad; state.padProgress = 0; }
      state.padProgress += dt * 1.15;
      progWrap.style.display = "flex";
      document.getElementById("pad-progress-label").innerText = STATIONS[stoodPad].label;
      document.getElementById("pad-progress-bar").style.width = Math.min(100, Math.max(0, state.padProgress * 100)) + "%";
      if (state.padProgress >= 1.0) { completePadAction(stoodPad); state.padProgress = -0.65; }
    } else {
      state.activePad = null; state.padProgress = 0; progWrap.style.display = "none";
    }

    const growSpeed = (session.heroKey === "WANDA") ? 7.5 : 4.2;
    for (let i = 0; i < 4; i++) {
      state.crops[i] = Math.min(100, state.crops[i] + growSpeed * dt);
      const s = 0.25 + (state.crops[i] / 100) * 0.95;
      cropMeshes[i].scale.set(s, s, s);
    }

    if (state.roverCooldown > 0) state.roverCooldown -= dt;

    if (state.shieldOn) {
      const sDrain = (session.heroKey === "CAP" ? 1.45 : 2.95) * diff.drain;
      state.power = Math.max(0, state.power - sDrain * dt);
      if (state.power <= 0.1) { state.shieldOn = false; setStatus("⚡ Battery hit 0%! Shield collapsed!"); }
    } else if (state.dusty) {
      state.power = Math.max(0, state.power - 0.8 * diff.drain * dt);
    } else {
      state.power = Math.min(100, state.power + ((session.heroKey === "IRON") ? 2.6 : 1.35) * dt);
    }

    let oxLoss = (state.doorSealed ? 0.62 : 2.3) * diff.drain;
    if (session.heroKey === "WIDOW") oxLoss *= 0.6;
    state.oxygen = Math.max(0, state.oxygen - oxLoss * dt);
    state.food = Math.max(0, state.food - 0.52 * diff.drain * dt);

    state.flareTimer -= dt;
    if (state.flarePhase === "CALM" && state.flareTimer <= 0) {
      state.flarePhase = "WARN"; state.flareTimer = diff.flareWarn;
      playSfx(240, 0.45, "sawtooth", 0.09, 460);
      document.getElementById("flare-alarm").style.display = "block";
      document.getElementById("flare-alarm-title").innerText = `🚨 NASA DONKI ${NASA.flr.class} FLARE!`;
      showComic("🚨☀️🔥", "SOLAR FLARE INCOMING!", `NASA DONKI ${NASA.flr.class} storm hits in ${Math.ceil(diff.flareWarn)}s!`, 3000);
    } else if (state.flarePhase === "WARN") {
      document.getElementById("flare-alarm-desc").innerText = `Impact in ${Math.max(0, state.flareTimer).toFixed(1)}s! Inside + Sealed + Shield ON!`;
      if (state.flareTimer <= 0) { state.flarePhase = "ACTIVE"; state.flareTimer = diff.flareDur; playSfx(180, 0.5, "sawtooth", 0.11, 120); }
    } else if (state.flarePhase === "ACTIVE") {
      document.getElementById("flare-alarm-title").innerText = `☢️ STORM HITTING (${Math.ceil(state.flareTimer)}s)`;
      const safe = nowInside && state.doorSealed && state.shieldOn;
      if (!safe) {
        state.hp = Math.max(0, state.hp - diff.flareDmg * (session.heroKey === "THOR" ? 0.4 : 1.0) * dt);
        state.rad += 0.25 * dt;
        document.getElementById("flare-alarm-desc").innerText = "⚠️ RADIATION HIT! Inside + Seal Door + Shield ON!";
      } else {
        state.rad += 0.015 * dt;
        document.getElementById("flare-alarm-desc").innerText = "🛡️ 100% PROTECTED BY SHIELD!";
      }
      if (state.flareTimer <= 0) {
        state.flarePhase = "CALM"; state.flareTimer = diff.flareGap + Math.random() * 5;
        document.getElementById("flare-alarm").style.display = "none";
        if (Math.random() < 0.65) { state.dusty = true; showComic("🌪️☀️", "PANELS DUSTY!", "Storm cleared, moon dust coated your solar panels!", 2400); }
        else showComic("☀️✅", "FLARE PASSED!", "Lower Shield now to recharge battery!", 2300);
        setStatus("☀️ Solar Flare cleared! Turn Shield OFF to recharge batteries.");
      }
    } else {
      state.rad += 0.015 * dt;
    }

    state.solClock += dt;
    if (state.solClock >= diff.solSecs) {
      state.solClock = 0; state.sol += 1;
      telemetryLog.push({ sol: state.sol, pwr: Math.round(state.power), ox: Math.round(state.oxygen), hp: Math.round(state.hp) });

      if (state.sol > 7) {
        endMission(true, "WIN");
      } else {
        const bonus = (session.heroKey === "LOKI") ? 40 : 20;
        addVaultCoins(bonus);
        state.science += 50;
        if (state.pantryCount > 0) { state.pantryCount--; refreshPantryVisuals(); }
        playSfx(523, 0.2, "triangle", 0.09, 784);
        if (DILEMMAS[state.sol] && !state.dilemmasShown[state.sol]) {
          state.dilemmasShown[state.sol] = true;
          triggerDilemma(state.sol);
        } else {
          showComic("🌙🏆", `LUNAR SOL ${state.sol} OF 7`, `+${bonus} 🪙 Vault Coins & +50 🔬 Science!`, 2100);
        }
      }
    }

    if (state.power <= 0) endMission(false, "POWER");
    else if (state.oxygen <= 0) endMission(false, "OXYGEN");
    else if (state.food <= 0) endMission(false, "FOOD");
    else if (state.hp <= 0) endMission(false, "RADIATION");

    updateHUD();
    drawMinimap();
  }

  const camOffset = state.camWide ? new THREE.Vector3(0, 21, 27) : new THREE.Vector3(0, 12.8, 16.8);
  camera.position.lerp(new THREE.Vector3(heroPos.x * 0.62 + camOffset.x, camOffset.y, heroPos.z * 0.52 + camOffset.z), Math.min(1, dt * 4.5));
  camera.lookAt(heroPos.x * 0.48, 1.4, heroPos.z * 0.42);

  renderer.render(scene, camera);
}

function updateHUD() {
  const diff = getDiff();
  document.getElementById("ui-sol").innerText = Math.min(7, state.sol) + " / 7";
  document.getElementById("bar-sol").style.width = Math.min(100, (state.solClock / diff.solSecs) * 100) + "%";
  document.getElementById("ui-weather").innerText =
    state.flarePhase === "ACTIVE" ? `☢️ ${NASA.flr.class} STORM` :
    (state.flarePhase === "WARN" ? "🚨 FLARE WARN" : (state.dusty ? "🌪️ Dusty" : "☀️ Calm Sky"));

  document.getElementById("ui-pwr").innerText = Math.round(state.power) + "%";
  document.getElementById("bar-pwr").style.width = state.power + "%";
  document.getElementById("sub-pwr").innerText = state.shieldOn ? "🛡️ Draining" : (state.dusty ? "🌪️ Dusty" : "☀️ Charging");

  document.getElementById("ui-ox").innerText = Math.round(state.oxygen) + "%";
  document.getElementById("bar-ox").style.width = state.oxygen + "%";
  document.getElementById("sub-ox").innerText = state.doorSealed ? "🔒 Sealed" : "🔓 Open (-O₂)";

  document.getElementById("ui-food").innerText = Math.round(state.food) + "%";
  document.getElementById("bar-food").style.width = state.food + "%";
  document.getElementById("sub-basket").innerText = `🧺 ${state.basket.length}/4 ${state.basket.join("")}`;

  document.getElementById("ui-hp").innerText = Math.round(state.hp) + "%";
  document.getElementById("bar-hp").style.width = state.hp + "%";
  document.getElementById("sub-rad").innerText = `☢️ ${state.rad.toFixed(2)} mSv`;

  document.getElementById("ui-sci").innerText = state.science;
  syncVaultDisplays();

  document.getElementById("btn-shield").innerText = state.shieldOn ? "🛡️ Shield: ON" : "🛡️ Shield: OFF";
  document.getElementById("btn-door").innerText = state.doorSealed ? "🔒 Airlock: SEALED" : "🔓 Airlock: OPEN";
  document.getElementById("zone-badge").innerText = isInsideHabitat() ? "📍 INSIDE BASE" : "🌑 OUTSIDE MOON";
}

function endMission(won, cause) {
  state.ended = true;
  document.getElementById("flare-alarm").style.display = "none";
  document.getElementById("dilemma-modal").style.display = "none";
  document.getElementById("debrief-modal").style.display = "flex";
  const h = getHero();

  if (won) {
    session.wins += 1;
    addVaultCoins(60);
    playSfx(523, 0.25, "triangle", 0.1, 1046);
    const rank = state.science >= 1100 ? "💎 CHIEF NASA MISSION PLANNER" : (state.science >= 700 ? "🥇 SHACKLETON COMMANDER" : "🥈 ARTEMIS SPECIALIST");
    document.getElementById("debrief-icon").innerText = "🏆🦸‍♂️🌕";
    document.getElementById("debrief-title").innerText = "7-SOL MISSION ACCOMPLISHED!";
    document.getElementById("debrief-rank").innerText = `${rank} • +60 🪙 Victory Vault Bonus!`;
    document.getElementById("debrief-sub").innerText = `${h.name} survived 7 Sols | Science: ${state.science} | Dose: ${state.rad.toFixed(2)} mSv | Vault: ${Math.floor(session.vaultCoins)} 🪙`;
    document.getElementById("debrief-lesson").innerHTML =
      `<b>🛰️ Engineering Takeaway:</b> You balanced Power, Oxygen, CSA Food, EVA Science, and <b>NASA DONKI ${NASA.flr.class}</b> space weather across 7 Sols! Click <b>Switch Hero</b> to play with any newly unlocked Avengers!`;
  } else {
    playSfx(220, 0.45, "sawtooth", 0.09, 110);
    document.getElementById("debrief-icon").innerText = "🛠️📡";
    document.getElementById("debrief-title").innerText = `MISSION DEBRIEF — SOL ${state.sol} OF 7`;
    document.getElementById("debrief-rank").innerText = `Science Logged: ${state.science} pts • Vault Coins Kept: ${Math.floor(session.vaultCoins)} 🪙`;
    const lessons = {
      POWER: "⚡ <b>Power Budget Depleted:</b> Leaving the Shield ON during calm skies or letting lunar dust coat solar panels drains batteries fast.",
      OXYGEN: "🫁 <b>Oxygen Depleted:</b> Seal the Airlock Door when back inside and mine Shackleton Crater ice (H₂O → O₂) before running heavy EVA science drills!",
      FOOD: "🍽️ <b>Pantry Empty:</b> Harvest Tomatoes, Lettuce, Radishes & Potatoes in the CSA Greenhouse and stock your Pantry Table!",
      RADIATION: "☢️ <b>Solar Flare Exposure:</b> When the NASA DONKI siren sounds, rush inside the Habitat, Seal the Airlock, and Raise the Shield!"
    };
    document.getElementById("debrief-sub").innerText = `Resource limit reached: ${cause}. All Vault Coins earned on this run are safely banked!`;
    document.getElementById("debrief-lesson").innerHTML = lessons[cause] || lessons.POWER;
  }

  const c = document.getElementById("debrief-chart");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  for (let y = 24; y <= 130; y += 26.5) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif";
  ctx.fillText("100%", 6, 27); ctx.fillText("50%", 12, 80); ctx.fillText("0%", 18, 133);
  const pts = telemetryLog.length > 1 ? telemetryLog : [...telemetryLog, { sol: state.sol + 0.5, pwr: state.power, ox: state.oxygen, hp: state.hp }];
  function plotSeries(k, col) {
    ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath();
    pts.forEach((p, idx) => {
      const x = 45 + (idx / Math.max(1, pts.length - 1)) * 525;
      const y = 130 - (Math.max(0, Math.min(100, p[k])) / 100) * 106;
      if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
  plotSeries("pwr", "#facc15"); plotSeries("ox", "#38bdf8"); plotSeries("hp", "#f43f5e");
  ctx.fillStyle = "#facc15"; ctx.fillText("■ Power", 410, 15);
  ctx.fillStyle = "#38bdf8"; ctx.fillText("■ Oxygen", 470, 15);
  ctx.fillStyle = "#f43f5e"; ctx.fillText("■ Crew HP", 535, 15);
  syncVaultDisplays();
}

window.addEventListener("keydown", e => {
  if (session.screen !== "GAME") return;
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) e.preventDefault();
  keys[e.code] = true;
  if (e.code === "Space") triggerJump();
  if (e.code === "KeyE") toggleDoor();
  if (e.code === "KeyQ") toggleShield();
});
window.addEventListener("keyup", e => { keys[e.code] = false; });

startFiveSecondLoader();
</script>
</body>
</html>
"""

components.html(APP_HTML.replace("__NASA_JSON__", json.dumps(nasa_payload)), height=865, scrolling=False)
