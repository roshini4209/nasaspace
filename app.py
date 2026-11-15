import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Avengers Assemble | Moon & Mars 3D",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
header[data-testid="stHeader"], footer, #MainMenu, section[data-testid="stSidebar"], div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
    display: none !important;
}
html, body, .stApp {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    overflow: hidden !important;
    background: #020617 !important;
}
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
iframe {
    position: fixed !important; top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important; height: 100dvh !important;
    border: none !important; margin: 0 !important; padding: 0 !important; z-index: 99999 !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_nasa_data():
    flr = {"id": "2024-05-14T16:46-FLR-001", "class": "X8.7", "source": "ARCHIVED NASA DONKI", "live": False}
    cme = {"id": "2024-05-14T17:12-CME-001", "speed": 1240, "source": "ARCHIVED NASA DONKI", "live": False}
    try:
        r1 = requests.get("https://api.nasa.gov/DONKI/FLR?api_key=DEMO_KEY", timeout=4)
        if r1.status_code == 200 and isinstance(r1.json(), list) and len(r1.json()) > 0:
            lt = r1.json()[-1]
            flr = {"id": lt.get("flrID", "LIVE-FLR"), "class": lt.get("classType", "M2.4"), "source": "LIVE NASA DONKI API", "live": True}
    except Exception:
        pass
    try:
        r2 = requests.get("https://api.nasa.gov/DONKI/CME?api_key=DEMO_KEY", timeout=4)
        if r2.status_code == 200 and isinstance(r2.json(), list) and len(r2.json()) > 0:
            lt = r2.json()[-1]
            an = lt.get("cmeAnalyses") or []
            spd = an[0].get("speed", 780) if an else 780
            cme = {"id": lt.get("activityID", "LIVE-CME"), "speed": int(spd) if spd else 780, "source": "LIVE NASA DONKI API", "live": True}
    except Exception:
        pass
    return {"flr": flr, "cme": cme}

nasa_payload = fetch_nasa_data()

APP_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; font-family: 'Segoe UI', system-ui, sans-serif; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #020617; color: #f8fafc; touch-action: none; }
  #app-shell { position: relative; width: 100%; height: 100%; overflow: hidden; background: #020617; }
  #bg-space-canvas { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }

  .screen {
    position: absolute; inset: 0; z-index: 10;
    display: none; flex-direction: column; align-items: center; justify-content: center;
    padding: 12px; overflow-y: auto; touch-action: pan-y;
  }
  .screen.active { display: flex; }
  .glass-panel {
    background: rgba(9, 13, 31, 0.92); backdrop-filter: blur(12px);
    border: 2.5px solid #eab308; border-radius: 22px;
    box-shadow: 0 0 46px rgba(56, 189, 248, 0.25), 0 18px 40px rgba(0, 0, 0, 0.85);
  }

  .loader-wrap {
    width: 680px; max-width: 95%; padding: 28px 30px; text-align: center;
    background: rgba(9, 13, 31, 0.9); border: 2.5px solid #38bdf8; border-radius: 24px;
  }
  .orbit-ring {
    width: 86px; height: 86px; margin: 0 auto 12px auto; border-radius: 50%;
    border: 4px solid rgba(56, 189, 248, 0.22); border-top-color: #fde047; border-right-color: #f97316;
    display: flex; align-items: center; justify-content: center; font-size: 38px;
    animation: spinO 1.4s linear infinite;
  }
  .orbit-ring span { animation: spinR 1.4s linear infinite; display: inline-block; }
  @keyframes spinO { to { transform: rotate(360deg); } }
  @keyframes spinR { to { transform: rotate(-360deg); } }
  .load-title {
    font-size: clamp(26px, 5vw, 40px); font-weight: 900; letter-spacing: 2px;
    background: linear-gradient(90deg, #fde047, #38bdf8, #f97316, #f43f5e);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .load-bar-bg { width: 100%; height: 13px; background: #0f172a; border: 2px solid #38bdf8; border-radius: 999px; overflow: hidden; margin: 15px 0 8px 0; }
  .load-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #ef4444, #eab308, #38bdf8); transition: width 0.08s linear; }
  .science-card {
    margin-top: 16px; padding: 13px 16px; border-radius: 15px; text-align: left;
    background: linear-gradient(145deg, rgba(30, 27, 75, 0.92), rgba(15, 23, 42, 0.92));
    border: 2px solid rgba(253, 224, 71, 0.72);
  }

  .create-card { width: 640px; max-width: 96%; max-height: 96%; overflow-y: auto; padding: 22px 26px; text-align: center; }
  .game-logo-title { font-size: clamp(26px, 5vw, 40px); font-weight: 900; color: #fde047; letter-spacing: 1.5px; text-shadow: 0 0 22px rgba(253, 224, 71, 0.45); }
  .game-logo-sub { font-size: 12px; color: #7dd3fc; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin: 4px 0 16px 0; }
  .planet-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 11px; margin-bottom: 14px; }
  @media (max-width: 560px) { .planet-grid { grid-template-columns: 1fr; } }
  .planet-card {
    background: linear-gradient(150deg, #0f172a, #1e1b4b); border: 2.5px solid #334155;
    border-radius: 15px; padding: 12px; cursor: pointer; text-align: left; transition: 0.16s;
  }
  .planet-card.active-moon { border-color: #38bdf8; box-shadow: 0 0 22px rgba(56, 189, 248, 0.55); background: linear-gradient(150deg, #0c1f3d, #1e293b); }
  .planet-card.active-mars { border-color: #f97316; box-shadow: 0 0 22px rgba(249, 115, 22, 0.55); background: linear-gradient(150deg, #3b1208, #1e1b4b); }
  .planet-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
  .planet-name { font-size: 15.5px; font-weight: 900; color: #fde047; }
  .planet-pill { font-size: 9.5px; font-weight: 900; padding: 2px 7px; border-radius: 999px; background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #7dd3fc; }
  .planet-specs { font-size: 11px; color: #cbd5e1; line-height: 1.42; font-weight: 600; }

  .menu-btn {
    width: 100%; padding: 13px 16px; margin-bottom: 9px; border-radius: 14px;
    font-size: 14.5px; font-weight: 900; cursor: pointer; border: 2.5px solid #fde047; color: #fff;
    background: linear-gradient(90deg, #dc2626 0%, #2563eb 100%); box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6);
  }
  .menu-btn:hover { transform: translateY(-1px); box-shadow: 0 0 20px rgba(56, 189, 248, 0.7); }
  .menu-btn.secondary { background: linear-gradient(145deg, #1e293b, #0f172a); border-color: #38bdf8; }
  .menu-btn.multi { background: linear-gradient(145deg, #3b0764, #1e1b4b); border-color: #c084fc; }
  .menu-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  #multi-notice { display: none; margin-top: 6px; padding: 9px 12px; border-radius: 11px; background: rgba(127, 29, 29, 0.92); border: 2px solid #fca5a5; color: #fef08a; font-weight: 800; font-size: 12px; }

  .age-panel { width: 1140px; max-width: 97%; max-height: 96%; overflow-y: auto; padding: 15px 18px; }
  .age-top-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
  .age-input-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; background: #0f172a; border: 2px solid #38bdf8; border-radius: 13px; padding: 7px 13px; }
  .age-input-group label { font-size: 14px; font-weight: 900; color: #fde047; }
  .age-input-group input { width: 92px; padding: 6px 9px; border-radius: 9px; border: 2px solid #fde047; background: #020617; color: #fff; font-size: 16px; font-weight: 900; text-align: center; outline: none; }
  .vault-badge { background: linear-gradient(145deg, #422006, #1e1b4b); border: 2.5px solid #fde047; border-radius: 13px; padding: 8px 15px; font-size: 15px; font-weight: 900; color: #fde047; }
  .hero-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin: 10px 0; }
  @media (max-width: 980px) { .hero-grid { grid-template-columns: repeat(4, 1fr); } }
  @media (max-width: 580px) { .hero-grid { grid-template-columns: repeat(2, 1fr); } }
  .hero-card { background: linear-gradient(155deg, #0f172a, #1e1b4b); border: 2.5px solid #334155; border-radius: 14px; padding: 8px 6px; text-align: center; cursor: pointer; transition: 0.15s; }
  .hero-card.selected { border-color: #fde047; box-shadow: 0 0 18px rgba(253, 224, 71, 0.75); background: linear-gradient(155deg, #1e1b4b, #172554); }
  .hero-card.locked { opacity: 0.85; border-color: #475569; }
  .hero-card.can-buy { opacity: 1; border-color: #4ade80; box-shadow: 0 0 14px rgba(74, 222, 128, 0.55); }
  .hero-name { font-weight: 900; font-size: 12px; color: #fde047; margin-top: 2px; }
  .hero-shield-tag { font-size: 9.2px; color: #7dd3fc; font-weight: 800; margin-top: 2px; }
  .hero-perk { font-size: 9.8px; color: #86efac; font-weight: 700; margin-top: 2px; line-height: 1.22; }
  .hero-status { margin-top: 5px; padding: 3px 4px; border-radius: 7px; font-size: 9.8px; font-weight: 900; }
  .st-ok { background: rgba(22, 163, 74, 0.25); color: #86efac; border: 1px solid #4ade80; }
  .st-buy { background: linear-gradient(90deg, #16a34a, #ca8a04); color: #fff; border: 1px solid #fef08a; }
  .st-lock { background: rgba(127, 29, 29, 0.55); color: #fde047; border: 1px solid #f87171; }
  #hero-msg { min-height: 20px; text-align: center; font-size: 13px; font-weight: 800; color: #fde047; margin-bottom: 8px; }
  .continue-btn { width: 320px; max-width: 100%; padding: 12px 20px; border-radius: 13px; font-size: 15px; font-weight: 900; cursor: pointer; border: 2.5px solid #fde047; color: #fff; background: linear-gradient(90deg, #16a34a, #0284c7); display: block; margin: 0 auto; }
  .continue-btn:disabled { background: #1e293b; border-color: #475569; color: #64748b; cursor: not-allowed; }

  .inst-panel { width: 1040px; max-width: 97%; max-height: 96%; overflow-y: auto; padding: 20px 22px; text-align: center; }
  .inst-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0 18px 0; }
  @media (max-width: 860px) { .inst-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 500px) { .inst-grid { grid-template-columns: 1fr; } }
  .inst-box { background: linear-gradient(155deg, #1e293b, #0f172a); border: 2px solid #38bdf8; border-radius: 14px; padding: 12px; }
  .inst-box h3 { color: #fde047; font-size: 13.5px; margin: 5px 0; }
  .inst-box p { color: #e2e8f0; font-size: 11.8px; line-height: 1.4; }

  #screen-game { padding: 0; overflow: hidden; touch-action: none; }
  #game-root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #020617; outline: none; touch-action: none; }
  #canvas-container { position: absolute; inset: 0; width: 100%; height: 100%; touch-action: none; }

  #game-sidebar {
    position: absolute; top: 0; left: 0; bottom: 0; width: 270px; max-width: 84vw; z-index: 45;
    background: linear-gradient(180deg, rgba(7, 11, 24, 0.98), rgba(15, 23, 42, 0.98));
    border-right: 3px solid #eab308; padding: 13px 12px;
    transform: translateX(-100%); transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
    display: flex; flex-direction: column; gap: 6px; overflow-y: auto;
  }
  #game-sidebar.open { transform: translateX(0); }
  .sb-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 7px; border-bottom: 1.5px solid #334155; }
  .sb-stat { background: #0f172a; border: 1.5px solid #38bdf8; border-radius: 10px; padding: 7px 10px; font-size: 11.8px; line-height: 1.45; }
  .sb-btn { width: 100%; padding: 8.5px 10px; border-radius: 9px; text-align: left; font-size: 11.8px; font-weight: 800; color: #fff; cursor: pointer; background: linear-gradient(90deg, #1e293b, #1e1b4b); border: 1.5px solid #38bdf8; }
  .sb-btn:hover { border-color: #fde047; background: #1d4ed8; }
  .sb-btn.danger { background: linear-gradient(90deg, #7f1d1d, #991b1b); border-color: #fca5a5; }

  .top-hud {
    position: absolute; top: 5px; left: 5px; right: 5px;
    display: grid; grid-template-columns: 0.72fr 0.98fr 0.85fr 0.85fr 0.85fr 0.85fr 1.25fr;
    gap: 5px; pointer-events: none; z-index: 12;
  }
  .hud-card {
    background: rgba(9, 13, 31, 0.86); backdrop-filter: blur(8px);
    border: 1.8px solid rgba(234, 179, 8, 0.78); border-radius: 10px;
    padding: 4px 6px; pointer-events: auto;
  }
  .top-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; pointer-events: auto; }
  .top-act-btn {
    background: linear-gradient(145deg, #1d4ed8, #1e1b4b); border: 1.8px solid #fde047;
    border-radius: 10px; color: #fde047; font-size: 10px; font-weight: 900; cursor: pointer;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px;
  }
  .hud-row { display: flex; justify-content: space-between; align-items: center; }
  .hud-lbl { font-size: 9.2px; font-weight: 800; color: #93c5fd; text-transform: uppercase; display: flex; align-items: center; gap: 2px; }
  .hud-val { font-size: 14px; font-weight: 900; color: #fff; }
  .hud-sub { font-size: 8.8px; font-weight: 800; color: #cbd5e1; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-bg { width: 100%; height: 5px; background: rgba(2, 6, 23, 0.92); border-radius: 99px; overflow: hidden; margin-top: 2px; }
  .bar-fill { height: 100%; width: 90%; transition: width 0.18s ease; border-radius: 99px; }
  .qchip { display: inline-flex; align-items: center; justify-content: center; width: 13px; height: 13px; border-radius: 50%; background: rgba(56, 189, 248, 0.25); border: 1px solid #38bdf8; color: #7dd3fc; font-size: 8.5px; font-weight: 900; cursor: pointer; }

  .ticker-bar {
    position: absolute; top: 61px; left: 5px; right: 5px;
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    background: rgba(15, 23, 42, 0.86); border: 1.5px solid #38bdf8; border-radius: 9px;
    padding: 3px 10px; z-index: 12; font-size: 10.8px; font-weight: 800;
  }
  #status-msg { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .nasa-badge-btn { background: rgba(14, 165, 233, 0.22); border: 1px solid #38bdf8; color: #7dd3fc; border-radius: 999px; padding: 2px 8px; font-size: 9.8px; font-weight: 900; cursor: pointer; white-space: nowrap; }

  #minimap-wrap { position: absolute; top: 92px; left: 7px; z-index: 16; background: rgba(2, 6, 23, 0.84); border: 1.8px solid #38bdf8; border-radius: 11px; padding: 4px; text-align: center; }
  #minimap { display: block; border-radius: 7px; background: #0b1120; }

  #right-tools {
    position: absolute; top: 92px; right: 7px; z-index: 16;
    display: flex; flex-direction: column; gap: 4px;
    background: rgba(2, 6, 23, 0.84); border: 1.5px solid #38bdf8; border-radius: 11px; padding: 4px;
  }
  .zbtn { background: #1e293b; border: 1.2px solid #7dd3fc; color: #fde047; border-radius: 7px; padding: 4px 6px; font-size: 10.5px; font-weight: 900; cursor: pointer; white-space: nowrap; }
  .zbtn:hover { background: #1d4ed8; }
  .zbtn.fun { border-color: #f472b6; color: #fbcfe8; }

  #flare-alarm {
    position: absolute; top: 222px; left: 7px; width: 238px; display: none; z-index: 22;
    background: linear-gradient(90deg, rgba(185, 28, 28, 0.95), rgba(127, 29, 29, 0.95));
    border: 2px solid #fde047; border-radius: 11px; padding: 6px 10px;
    animation: pulseRed 0.75s infinite alternate;
  }
  @keyframes pulseRed { from { transform: scale(1); } to { transform: scale(1.03); } }
  #comic-toast {
    position: absolute; top: 94px; right: 86px; width: 230px; display: none; z-index: 25; text-align: center;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(30, 27, 75, 0.96));
    border: 2.5px solid #fde047; border-radius: 13px; padding: 7px 9px;
  }
  #unlock-banner {
    position: absolute; top: 94px; left: 50%; transform: translateX(-50%); display: none; z-index: 35;
    background: linear-gradient(90deg, #ca8a04, #16a34a); border: 2px solid #fef08a; border-radius: 999px;
    padding: 5px 15px; font-size: 11.5px; font-weight: 900; color: #fff; white-space: nowrap;
  }
  #pad-progress-wrap {
    position: absolute; top: 128px; left: 50%; transform: translateX(-50%); display: none; align-items: center; gap: 8px; z-index: 20;
    background: rgba(2, 6, 23, 0.92); border: 2px solid #4ade80; border-radius: 999px; padding: 5px 13px;
  }
  #pad-progress-bar-bg { width: 105px; height: 8px; background: #1e293b; border-radius: 99px; overflow: hidden; }
  #pad-progress-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #4ade80, #fde047); }

  #joy-wrap { position: absolute; bottom: 102px; left: 12px; z-index: 24; display: none; flex-direction: column; align-items: center; gap: 3px; }
  #joy-wrap.visible { display: flex; }
  #joy-base { width: 108px; height: 108px; border-radius: 50%; background: radial-gradient(circle, rgba(15, 23, 42, 0.72), rgba(30, 58, 138, 0.45)); border: 2.5px solid rgba(56, 189, 248, 0.85); position: relative; touch-action: none; }
  #joy-knob { width: 44px; height: 44px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #fde047, #ea580c); border: 2.5px solid #fff; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; }

  #mobile-quick-pad { position: absolute; bottom: 102px; right: 10px; z-index: 24; display: none; flex-direction: column; gap: 5px; }
  #mobile-quick-pad.visible { display: flex; }
  .mq-btn { width: 62px; height: 42px; border-radius: 11px; background: rgba(15, 23, 42, 0.9); border: 2px solid #fde047; color: #fff; font-size: 10px; font-weight: 900; cursor: pointer; }

  .bottom-dock {
    position: absolute; bottom: 5px; left: 5px; right: 5px;
    display: grid; grid-template-columns: 1.45fr 1.25fr 1.5fr; gap: 5px; z-index: 15;
  }
  .dock-panel { background: rgba(9, 13, 31, 0.9); backdrop-filter: blur(8px); border: 1.5px solid rgba(56, 189, 248, 0.6); border-radius: 11px; padding: 5px 6px; }
  .dock-title { font-size: 9.2px; font-weight: 900; color: #fde047; text-transform: uppercase; margin-bottom: 3.5px; display: flex; justify-content: space-between; }
  .btn-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
  .btn-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3.5px; }
  .btn-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
  .gbtn { background: linear-gradient(145deg, #1d4ed8, #312e81); color: #fff; border: 1.2px solid #7dd3fc; border-radius: 7px; padding: 4px 2px; font-size: 9.8px; font-weight: 800; cursor: pointer; text-align: center; line-height: 1.15; }
  .gbtn:hover { border-color: #fde047; }
  .gbtn-green { background: linear-gradient(145deg, #15803d, #047857); border-color: #86efac; }
  .gbtn-red { background: linear-gradient(145deg, #b91c1c, #991b1b); border-color: #fca5a5; }
  .gbtn-gold { background: linear-gradient(145deg, #ca8a04, #b45309); border-color: #fef08a; }
  .gbtn-cyan { background: linear-gradient(145deg, #0369a1, #1e3a8a); border-color: #38bdf8; }
  .gbtn-purple { background: linear-gradient(145deg, #7e22ce, #4c1d95); border-color: #d8b4fe; }
  .kbadge { display: inline-block; background: rgba(2, 6, 23, 0.8); color: #fde047; border: 1px solid rgba(253, 224, 71, 0.6); border-radius: 4px; padding: 0 3px; font-size: 8px; font-weight: 900; margin-left: 2px; }

  .modal-backdrop { position: absolute; inset: 0; z-index: 60; background: rgba(2, 6, 23, 0.88); backdrop-filter: blur(8px); display: none; align-items: center; justify-content: center; padding: 12px; }
  .modal-box { background: linear-gradient(160deg, #0f172a, #1e1b4b); border: 2.5px solid #38bdf8; border-radius: 18px; padding: 16px 20px; width: 650px; max-width: 97%; max-height: 92%; overflow-y: auto; }
  .choice-btn { width: 100%; text-align: left; background: rgba(30, 41, 59, 0.95); border: 2px solid #eab308; border-radius: 11px; padding: 9px 12px; color: #fff; cursor: pointer; margin-top: 8px; }
  #glossary-pop { position: absolute; top: 94px; left: 50%; transform: translateX(-50%); width: 380px; max-width: 92%; background: rgba(15, 23, 42, 0.98); border: 2.5px solid #38bdf8; border-radius: 14px; padding: 11px 14px; z-index: 50; display: none; }
  .slider-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 8px 0; }
  .slider-item { background: #020617; border: 1px solid #334155; border-radius: 9px; padding: 7px 9px; font-size: 11.5px; }
  .slider-item input { width: 100%; margin-top: 3px; }

  @media (max-width: 820px) {
    .top-hud { grid-template-columns: 0.85fr repeat(3, 1fr); row-gap: 4px; }
    .hud-sub { display: none; }
    .ticker-bar { top: 96px; font-size: 9.8px; }
    #minimap-wrap { top: 124px; }
    #minimap { width: 88px; height: 76px; }
    #right-tools { top: 124px; }
    #flare-alarm { top: 222px; width: 190px; }
    .bottom-dock { grid-template-columns: 1fr; }
    .dock-panel.hide-sm { display: none; }
    .kbadge { display: none; }
    #joy-wrap { bottom: 86px; left: 10px; }
    #mobile-quick-pad { bottom: 86px; right: 10px; }
  }
</style>
</head>
<body>
<div id="app-shell">
  <canvas id="bg-space-canvas"></canvas>

  <div id="screen-loader" class="screen active">
    <div class="loader-wrap">
      <div class="orbit-ring"><span>🪐</span></div>
      <div class="load-title">AVENGERS ASSEMBLE</div>
      <div style="font-size:12px;color:#93c5fd;font-weight:800;margin-top:4px;letter-spacing:1.3px;">MOON &amp; MARS 3D SURVIVAL COMMAND</div>
      <div class="load-bar-bg"><div id="load-bar-fill" class="load-bar-fill"></div></div>
      <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:900;color:#fde047;">
        <span id="load-status">Initializing Deep Space Telemetry...</span>
        <span id="load-pct">0%</span>
      </div>
      <div class="science-card">
        <div style="font-size:11px;font-weight:900;color:#38bdf8;letter-spacing:1px;">🛰️ REAL NASA DEEP SPACE SCIENCE FACT</div>
        <div id="load-fact" style="font-size:14px;color:#f8fafc;margin-top:5px;line-height:1.45;font-weight:600;"></div>
      </div>
    </div>
  </div>

  <div id="screen-create" class="screen">
    <div class="glass-panel create-card">
      <div style="font-size:44px;margin-bottom:2px;">🛡️🌕🔴</div>
      <div class="game-logo-title">AVENGERS ASSEMBLE</div>
      <div class="game-logo-sub">Select Mission Planet &amp; Settings</div>
      <div class="planet-grid">
        <div id="card-planet-MOON" class="planet-card active-moon" onclick="selectPlanet('MOON')">
          <div class="planet-head"><span class="planet-name">🌕 MOON</span><span class="planet-pill">Shackleton Crater</span></div>
          <div class="planet-specs">• <b>Gravity:</b> 1/6G High Jumps<br>• <b>Solar:</b> 100% Sunlight (1,361 W/m²)<br>• <b>Radiation:</b> 0.42 mSv/Sol • Fierce Flares<br>• <b>Comms:</b> 2.6s Delay • Crater Ice O₂</div>
        </div>
        <div id="card-planet-MARS" class="planet-card" onclick="selectPlanet('MARS')">
          <div class="planet-head"><span class="planet-name">🔴 MARS</span><span class="planet-pill" style="border-color:#f97316;color:#fdba74;background:rgba(249,115,22,0.2);">Jezero Crater</span></div>
          <div class="planet-specs">• <b>Gravity:</b> 3/8G Crisp Jumps<br>• <b>Solar:</b> 43% Sunlight (590 W/m²)<br>• <b>Radiation:</b> 0.67 mSv/Sol • Heavy Dust<br>• <b>Comms:</b> 6.5s Delay • MOXIE CO₂→O₂</div>
        </div>
      </div>
      <button class="menu-btn" id="btn-start-world" onclick="goToAgePage()">🚀 LAUNCH MOON MISSION</button>
      <div class="menu-row-2">
        <button class="menu-btn secondary" id="create-music-btn" onclick="toggleMusic()">🎵 MUSIC: ON</button>
        <button class="menu-btn multi" onclick="clickMultiplayer()">👥 MULTIPLAYER</button>
      </div>
      <div id="multi-notice">🚧 Multiplayer Mode is Currently Unavailable! Enjoy Single-Player 3D Survival.</div>
    </div>
  </div>

  <div id="screen-age" class="screen">
    <div class="glass-panel age-panel">
      <h2 style="text-align:center;color:#fde047;font-size:clamp(18px,3vw,23px);font-weight:900;margin-bottom:10px;">🦸 COMMANDER AGE &amp; HERO SELECTION</h2>
      <div class="age-top-row">
        <div class="age-input-group">
          <label for="age-input">🎂 Enter Your Age:</label>
          <input type="number" id="age-input" min="1" max="100" placeholder="Age" oninput="validateAgePage()">
          <span id="age-feedback" style="font-size:12.5px;font-weight:800;color:#93c5fd;">Enter age (1–100) to continue</span>
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
      <h2 style="color:#fde047;font-size:clamp(20px,3vw,25px);font-weight:900;">📖 MISSION BRIEFING &amp; CONTROLS</h2>
      <p id="inst-hero-line" style="color:#7dd3fc;font-size:13px;font-weight:800;margin-top:4px;"></p>
      <div class="inst-grid">
        <div class="inst-box">
          <div style="font-size:26px;">🚙</div>
          <h3>1. Drive 3D Rover</h3>
          <p>Press <b>B</b> (or tap <b>Drive</b>) to hop into your 6-wheel Explorer Rover! Use <b>WASD / Joystick</b> to steer realistically across craters and grab coins fast!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:26px;">☕💃🪑</div>
          <h3>2. Fun Emotes &amp; Pause</h3>
          <p>Press <b>T</b> Drink Coffee, <b>Y</b> Dance, <b>U</b> Sit in Commander Chair, <b>Space</b> Jump, and <b>P</b> anytime to Pause your 10-minute Sol!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:26px;">🛡️🚨</div>
          <h3>3. Hero Shields &amp; Flares</h3>
          <p>Each 10-min Sol has <b>2 random NASA DONKI Solar Flares</b>. Rush inside, press <b>E</b> to Seal Airlock, and press <b>Q</b> for your hero's unique 3D Shield!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:26px;">⌨️🪙</div>
          <h3>4. Keys &amp; Vault Shop</h3>
          <p><b>1–6</b> Auto-Run • <b>R</b> Scan • <b>F–K</b> Earth Radio • <b>Z/X/C</b> Zoom. Earn <b>1000+ Vault Coins</b> and spend them in the Hero Locker to unlock elite Avengers!</p>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
        <button class="menu-btn secondary" style="width:170px;margin:0;" onclick="goToAgePage()">⬅️ Back</button>
        <button class="menu-btn" style="width:300px;margin:0;" id="btn-launch-final" onclick="launchGameScreen()">🚀 LAUNCH 3D MISSION</button>
      </div>
    </div>
  </div>

  <div id="screen-game" class="screen">
    <div id="game-root" tabindex="0">
      <div id="canvas-container"></div>

      <div id="game-sidebar">
        <div class="sb-header">
          <span style="font-weight:900;color:#fde047;font-size:14.5px;">🛡️ AVENGERS MENU</span>
          <button onclick="toggleSidebar()" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:3px 9px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <div class="sb-stat">
          <div><b>World:</b> <span id="sb-world" style="color:#f97316;font-weight:900;">MOON</span></div>
          <div><b>Hero:</b> <span id="sb-hero" style="color:#fde047;"></span></div>
          <div><b>Mode:</b> <span id="sb-mode" style="color:#7dd3fc;"></span></div>
          <div><b>Vault Coins:</b> <span id="sb-coins" style="color:#fde047;font-weight:900;">40</span> 🪙</div>
          <div><b>Trophies:</b> <span id="sb-wins" style="color:#4ade80;font-weight:900;">0</span> 🏆</div>
        </div>
        <button class="sb-btn" onclick="sidebarChangeAgeHero()">🦸 Change Age &amp; Hero</button>
        <button class="sb-btn" onclick="sidebarChangePlanet()">🪐 Switch Moon / Mars</button>
        <button class="sb-btn" onclick="sidebarGoInstructions()">📖 Instructions &amp; Keys</button>
        <button class="sb-btn" onclick="openMathLab()">📈 Engineering Graphs &amp; Math Lab</button>
        <button class="sb-btn" onclick="openNasaModal()">🛰️ NASA &amp; Partner Data Log</button>
        <button class="sb-btn" onclick="toggleJoystick()">🕹️ Toggle Mobile Joystick Handle</button>
        <button class="sb-btn" id="sb-music-btn" onclick="toggleMusic()">🎵 Music: ON</button>
        <button class="sb-btn" onclick="restartCurrentRun()">🔄 Restart Current Mission</button>
        <button class="sb-btn danger" onclick="quitAndResetGame()">🚪 Quit Game &amp; Reset Vault</button>
      </div>

      <div class="top-hud">
        <div class="top-actions">
          <button class="top-act-btn" onclick="toggleSidebar()"><span>☰</span><span>MENU</span></button>
          <button class="top-act-btn" id="btn-pause-hud" style="border-color:#38bdf8;color:#7dd3fc;" onclick="togglePause()"><span>⏸️</span><span>PAUSE</span></button>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">📅 Sol <span class="qchip" onclick="openGlossary('SOL')">?</span></span>
            <span class="hud-val" id="ui-sol">1/7</span>
          </div>
          <div class="bar-bg"><div id="bar-sol" class="bar-fill" style="width:0%;background:#a855f7;"></div></div>
          <div class="hud-sub" id="ui-weather">⏱️ 10:00 • Calm</div>
        </div>
        <div class="hud-card">
          <div class="hud-row"><span class="hud-lbl">⚡ Pwr <span class="qchip" onclick="openGlossary('POWER')">?</span></span><span class="hud-val" id="ui-pwr">96%</span></div>
          <div class="bar-bg"><div id="bar-pwr" class="bar-fill" style="width:96%;background:#facc15;"></div></div>
          <div class="hud-sub" id="sub-pwr">☀️ Charging</div>
        </div>
        <div class="hud-card">
          <div class="hud-row"><span class="hud-lbl">🫁 O₂ <span class="qchip" onclick="openGlossary('OXYGEN')">?</span></span><span class="hud-val" id="ui-ox">96%</span></div>
          <div class="bar-bg"><div id="bar-ox" class="bar-fill" style="width:96%;background:#38bdf8;"></div></div>
          <div class="hud-sub" id="sub-ox">🔒 Sealed</div>
        </div>
        <div class="hud-card">
          <div class="hud-row"><span class="hud-lbl">🍽️ Food <span class="qchip" onclick="openGlossary('FOOD')">?</span></span><span class="hud-val" id="ui-food">92%</span></div>
          <div class="bar-bg"><div id="bar-food" class="bar-fill" style="width:92%;background:#4ade80;"></div></div>
          <div class="hud-sub" id="sub-basket">🧺 0/4</div>
        </div>
        <div class="hud-card">
          <div class="hud-row"><span class="hud-lbl">❤️ HP <span class="qchip" onclick="openGlossary('RAD')">?</span></span><span class="hud-val" id="ui-hp">100%</span></div>
          <div class="bar-bg"><div id="bar-hp" class="bar-fill" style="width:100%;background:#f43f5e;"></div></div>
          <div class="hud-sub" id="sub-rad">☢️ 0.42 mSv</div>
        </div>
        <div class="hud-card" style="border-color:#38bdf8;">
          <div class="hud-row">
            <span class="hud-lbl">🪙 Vault / 🔬</span>
            <span class="hud-val" style="font-size:13px;"><span id="ui-coins" style="color:#fde047;">40</span> | <span id="ui-sci" style="color:#d8b4fe;">0</span></span>
          </div>
          <div style="display:flex;gap:3px;margin-top:3px;">
            <button class="gbtn" id="hud-music-btn" style="flex:1;padding:2.5px;font-size:9px;" onclick="toggleMusic()">🔊 V</button>
            <button class="gbtn gbtn-cyan" style="flex:1;padding:2.5px;font-size:9px;" onclick="toggleJoystick()">🕹️ Pad</button>
          </div>
        </div>
      </div>

      <div class="ticker-bar">
        <span id="status-msg">🚀 Touchdown! Press B to drive your 3D Rover, P to Pause, T/Y/U for Fun Emotes!</span>
        <button class="nasa-badge-btn" id="nasa-feed-btn" onclick="openNasaModal()">🛰️ NASA DONKI</button>
      </div>

      <div id="minimap-wrap">
        <div id="radar-title" style="font-size:8.5px;font-weight:900;color:#7dd3fc;margin-bottom:2px;">📡 SHACKLETON RADAR</div>
        <canvas id="minimap" width="112" height="96"></canvas>
      </div>

      <div id="right-tools">
        <button class="zbtn" onclick="adjustZoom(-0.45)">➕ <span class="kbadge">X</span></button>
        <button class="zbtn" onclick="adjustZoom(0.45)">➖ <span class="kbadge">Z</span></button>
        <button class="zbtn" id="btn-whole-planet" onclick="toggleFullPlanetView()">🌕 <span class="kbadge">C</span></button>
        <button class="zbtn fun" onclick="triggerEmote('COFFEE')">☕ <span class="kbadge">T</span></button>
        <button class="zbtn fun" onclick="triggerEmote('DANCE')">💃 <span class="kbadge">Y</span></button>
        <button class="zbtn fun" onclick="triggerEmote('SIT')">🪑 <span class="kbadge">U</span></button>
      </div>

      <div id="flare-alarm">
        <div style="font-size:11.5px;font-weight:900;color:#fde047;" id="flare-alarm-title">🚨 NASA DONKI FLARE!</div>
        <div style="font-size:10.5px;color:#fff;margin-top:2px;" id="flare-alarm-desc">Inside + Door(E) + Shield(Q)!</div>
      </div>

      <div id="unlock-banner"></div>
      <div id="pad-progress-wrap">
        <span id="pad-progress-label" style="font-size:11px;font-weight:900;color:#4ade80;">⚡ Working...</span>
        <div id="pad-progress-bar-bg"><div id="pad-progress-bar"></div></div>
      </div>
      <div id="comic-toast">
        <div id="comic-badge" style="font-size:28px;line-height:1.1;">🛡️</div>
        <div id="comic-title" style="font-size:11.5px;font-weight:900;color:#fde047;margin-top:2px;"></div>
        <div id="comic-body" style="font-size:10px;color:#e2e8f0;margin-top:2px;"></div>
      </div>
      <div id="glossary-pop">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span id="gl-title" style="font-weight:900;color:#fde047;font-size:13px;"></span>
          <button onclick="closeGlossary()" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:2px 8px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <p id="gl-body" style="font-size:11.8px;color:#e2e8f0;margin:6px 0 0 0;line-height:1.4;"></p>
      </div>

      <div id="joy-wrap">
        <div id="joy-base"><div id="joy-knob"></div></div>
        <div style="font-size:9px;font-weight:900;color:#7dd3fc;">MOVE / STEER</div>
      </div>
      <div id="mobile-quick-pad">
        <button class="mq-btn" style="border-color:#facc15;" id="mq-drive" onclick="toggleDriveRover()">🚙<br>DRIVE</button>
        <button class="mq-btn" style="border-color:#38bdf8;" onclick="triggerJump()">⬆️<br>JUMP</button>
        <button class="mq-btn" style="border-color:#ef4444;" onclick="toggleShield()">🛡️<br>SHIELD</button>
        <button class="mq-btn" style="border-color:#4ade80;" onclick="toggleDoor()">🔒<br>DOOR</button>
      </div>

      <div class="bottom-dock">
        <div class="dock-panel">
          <div class="dock-title"><span>🏃 Stations &amp; Rover</span><span style="color:#7dd3fc;">WASD + B Drive + SPC Jump</span></div>
          <div class="btn-grid-4" style="margin-bottom:4px;">
            <button class="gbtn gbtn-gold" onclick="autoRunTo('SOLAR')">☀️ Solar<span class="kbadge">1</span></button>
            <button class="gbtn gbtn-cyan" id="btn-station-o2" onclick="autoRunTo('O2GEN')">🧊 Ice<span class="kbadge">2</span></button>
            <button class="gbtn gbtn-purple" onclick="autoRunTo('SCIENCE')">🔬 Sci<span class="kbadge">3</span></button>
            <button class="gbtn gbtn-green" onclick="autoRunTo('FARM')">🌱 Farm<span class="kbadge">4</span></button>
          </div>
          <div class="btn-grid-4">
            <button class="gbtn" onclick="autoRunTo('PANTRY')">🍽️ Pantry<span class="kbadge">5</span></button>
            <button class="gbtn gbtn-red" onclick="autoRunTo('SHIELD')">🛡️ Cons<span class="kbadge">6</span></button>
            <button class="gbtn gbtn-gold" id="btn-drive-dock" onclick="toggleDriveRover()">🚙 Drive<span class="kbadge">B</span></button>
            <button class="gbtn" id="btn-jump-dock" onclick="triggerJump()">⬆️ Jump<span class="kbadge">SPC</span></button>
          </div>
        </div>

        <div class="dock-panel hide-sm">
          <div class="dock-title"><span>⚙️ Outpost Systems</span><span id="zone-badge" style="color:#4ade80;">📍 INSIDE BASE</span></div>
          <div class="btn-grid-2" style="margin-bottom:4px;">
            <button class="gbtn gbtn-red" id="btn-shield" onclick="toggleShield()">🛡️ Shield: OFF<span class="kbadge">Q</span></button>
            <button class="gbtn gbtn-green" id="btn-door" onclick="toggleDoor()">🔒 Airlock: SEALED<span class="kbadge">E</span></button>
          </div>
          <div class="btn-grid-2">
            <button class="gbtn gbtn-gold" onclick="deployRoverScan()">📡 Scan<span class="kbadge">R</span></button>
            <button class="gbtn gbtn-cyan" onclick="advanceSolEarly()">🌙 Next Sol<span class="kbadge">N</span></button>
          </div>
        </div>

        <div class="dock-panel hide-sm">
          <div class="dock-title"><span>📡 Earth HQ Radio <span class="qchip" onclick="openGlossary('DELAY')">?</span></span><span id="comms-dist-lbl" style="color:#7dd3fc;">384,400 km • 2.6s</span></div>
          <div class="btn-grid-5" style="margin-bottom:4px;">
            <button class="gbtn" onclick="callEarth(1)">⚡+30%<br><span class="kbadge">F</span></button>
            <button class="gbtn gbtn-cyan" onclick="callEarth(2)">🫁+30%<br><span class="kbadge">G</span></button>
            <button class="gbtn gbtn-green" onclick="callEarth(3)">🍅+30%<br><span class="kbadge">H</span></button>
            <button class="gbtn gbtn-red" onclick="callEarth(4)">❤️+30%<br><span class="kbadge">J</span></button>
            <button class="gbtn gbtn-gold" onclick="callEarth(5)">☀️Clr<br><span class="kbadge">K</span></button>
          </div>
          <div id="radio-log" style="font-size:9.6px;color:#fde047;font-weight:800;text-align:center;">
            15 🪙 per drop (Dr. Strange: 10 🪙 &amp; faster link)
          </div>
        </div>
      </div>

      <div id="pause-modal" class="modal-backdrop">
        <div class="modal-box" style="width:420px;text-align:center;border-color:#fde047;">
          <div style="font-size:40px;">⏸️</div>
          <h2 style="color:#fde047;margin:6px 0 4px 0;">MISSION PAUSED</h2>
          <p style="font-size:12.5px;color:#cbd5e1;margin-bottom:16px;">All Sol clocks, solar flares &amp; resource drains are frozen.</p>
          <button class="menu-btn" onclick="togglePause()">▶️ RESUME MISSION (P)</button>
          <button class="menu-btn secondary" onclick="pauseToHero()">🦸 Change Age / Buy Hero</button>
          <button class="menu-btn secondary" onclick="restartCurrentRun()">🔄 Restart Mission</button>
          <button class="menu-btn" style="background:linear-gradient(90deg,#7f1d1d,#991b1b);border-color:#fca5a5;" onclick="quitAndResetGame()">🚪 Quit &amp; Reset Vault</button>
        </div>
      </div>

      <div id="dilemma-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:#dc2626;color:#fff;font-size:10.5px;font-weight:900;padding:3px 9px;border-radius:999px;">⚖️ NASA ENGINEERING DILEMMA</span>
            <span id="dil-sol" style="color:#7dd3fc;font-size:12px;font-weight:900;">SOL 2</span>
          </div>
          <h3 id="dil-title" style="margin:9px 0 5px 0;color:#fde047;font-size:18px;"></h3>
          <p id="dil-desc" style="margin:0 0 8px 0;font-size:12.5px;color:#e2e8f0;line-height:1.45;"></p>
          <div id="dil-choices"></div>
        </div>
      </div>

      <div id="debrief-modal" class="modal-backdrop">
        <div class="modal-box" style="text-align:center;border-color:#fde047;">
          <div id="debrief-icon" style="font-size:34px;">🏆</div>
          <h2 id="debrief-title" style="color:#fde047;font-size:19px;margin:3px 0;"></h2>
          <div id="debrief-rank" style="font-size:12px;font-weight:900;color:#4ade80;margin-bottom:4px;"></div>
          <p id="debrief-sub" style="font-size:11.8px;color:#cbd5e1;margin-bottom:6px;"></p>
          <canvas id="debrief-chart" width="600" height="130" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:10px;margin:4px 0;"></canvas>
          <div id="debrief-lesson" style="background:rgba(14,165,233,0.15);border:1.5px solid #38bdf8;border-radius:10px;padding:8px 11px;font-size:11.5px;color:#e0f2fe;text-align:left;line-height:1.4;margin-bottom:10px;"></div>
          <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
            <button class="menu-btn secondary" style="width:210px;margin:0;padding:10px;" onclick="debriefChangeHero()">🦸 Switch Hero (<span id="deb-vault">40</span> 🪙)</button>
            <button class="menu-btn" style="width:190px;margin:0;padding:10px;" onclick="restartCurrentRun()">🔄 Play Again</button>
          </div>
        </div>
      </div>

      <div id="math-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="color:#fde047;" id="math-title">📈 Engineering Trade-Off Lab</h3>
            <button onclick="closeModal('math-modal')" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 12px;font-weight:900;cursor:pointer;">Close ✕</button>
          </div>
          <div class="slider-grid">
            <div class="slider-item">🛡️ Shield Duty: <b id="sl-sh-v">35%</b><input type="range" id="sl-sh" min="0" max="100" value="35" oninput="updateMathLab()"></div>
            <div class="slider-item">🌱 Grow-Lights: <b id="sl-fm-v">50%</b><input type="range" id="sl-fm" min="10" max="100" value="50" oninput="updateMathLab()"></div>
            <div class="slider-item">🔬 EVA Science: <b id="sl-ev-v">2 hrs</b><input type="range" id="sl-ev" min="0" max="6" value="2" oninput="updateMathLab()"></div>
            <div class="slider-item">🌪️ Dust Loss: <b id="sl-ds-v">15%</b><input type="range" id="sl-ds" min="0" max="65" value="15" oninput="updateMathLab()"></div>
          </div>
          <canvas id="math-chart" width="600" height="160" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:10px;"></canvas>
          <div id="math-summary" style="margin-top:7px;font-size:11.5px;color:#93c5fd;font-weight:700;"></div>
        </div>
      </div>

      <div id="nasa-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="color:#fde047;">🛰️ NASA &amp; Space Agency Partner Data</h3>
            <button onclick="closeModal('nasa-modal')" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 12px;font-weight:900;cursor:pointer;">Close ✕</button>
          </div>
          <div id="nasa-data-body" style="font-size:12px;line-height:1.5;color:#e2e8f0;"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
        onerror="var s=document.createElement('script');s.src='https://unpkg.com/three@0.128.0/build/three.min.js';document.head.appendChild(s);"></script>

<script>
const NASA = __NASA_JSON__;
const SOL_SECONDS = 600;
const WORLD_RADIUS = 64;

const PLANETS = {
  MOON: {
    key: "MOON", name: "Moon", site: "Shackleton Crater", icon: "🌕",
    gravity: 11.2, jumpVel: 7.5, solarChargeMult: 1.0, solarIrradiance: "1,361 W/m² (100%)",
    radBaseline: 0.42, flareDmgMult: 1.05, dustChance: 0.50, dustPowerLoss: 0.14,
    commsDelayMs: 2600, commsLabel: "384,400 km • 2.6s",
    o2Short: "🧊 Ice", o2Tag: "🧊 CRATER ICE [2]", o2Work: "🧊 Electrolysis: Crater Ice → O₂..."
  },
  MARS: {
    key: "MARS", name: "Mars", site: "Jezero Crater", icon: "🔴",
    gravity: 19.2, jumpVel: 8.6, solarChargeMult: 0.45, solarIrradiance: "590 W/m² (43%)",
    radBaseline: 0.67, flareDmgMult: 0.85, dustChance: 0.88, dustPowerLoss: 0.28,
    commsDelayMs: 6500, commsLabel: "225M km • 12m [6.5s]",
    o2Short: "⚙️ MOXIE", o2Tag: "⚙️ MOXIE O₂ [2]", o2Work: "⚙️ MOXIE Converting CO₂ → O₂..."
  }
};

const HEROES = [
  { key: "CAP", name: "Captain America", unlockCoins: 0, perk: "🛡️ Shield drains 50% less Power", shieldName: "Vibranium Star Shield", domeColor: 0x2563eb, wireColor: 0xef4444, auraColor: 0x60a5fa, suit: "#1d4ed8", accent: "#dc2626", trim: "#f8fafc", eyes: "#38bdf8", skin: "#f5cba7", head: "<path d='M 24 50 A 36 36 0 0 1 96 50 Z' fill='#1d4ed8' stroke='#fff' stroke-width='2'/><text x='60' y='38' text-anchor='middle' fill='#fff' font-size='18' font-weight='900'>A</text>" },
  { key: "WIDOW", name: "Natasha Romanoff", unlockCoins: 0, perk: "🕷️ +25% Speed & 40% less O₂", shieldName: "Widow's Bite Barrier", domeColor: 0x0ea5e9, wireColor: 0xf43f5e, auraColor: 0x38bdf8, suit: "#111827", accent: "#ef4444", trim: "#38bdf8", eyes: "#22c55e", skin: "#fbdcc4", head: "<path d='M 24 58 Q 26 14 60 16 Q 94 14 96 58 L 88 34 Q 60 22 32 34 Z' fill='#b91c1c'/><circle cx='24' cy='52' r='9' fill='#b91c1c'/><circle cx='96' cy='52' r='9' fill='#b91c1c'/>" },
  { key: "IRON", name: "Iron Man", unlockCoins: 1000, perk: "⚡ 2x Solar Charge & Jet Jumps", shieldName: "Mk-85 Nano Shield", domeColor: 0x38bdf8, wireColor: 0xfacc15, auraColor: 0x7dd3fc, suit: "#b91c1c", accent: "#facc15", trim: "#38bdf8", eyes: "#7dd3fc", skin: "#facc15", head: "<rect x='30' y='18' width='60' height='54' rx='18' fill='#b91c1c' stroke='#facc15' stroke-width='3'/><polygon points='38,22 82,22 76,58 44,58' fill='#facc15'/><rect x='40' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/><rect x='66' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/>" },
  { key: "THOR", name: "Thor Odinson", unlockCoins: 1100, perk: "🔨 60% less Flare Radiation", shieldName: "Mjolnir Lightning Aegis", domeColor: 0x38bdf8, wireColor: 0xe0f2fe, auraColor: 0x93c5fd, suit: "#334155", accent: "#dc2626", trim: "#cbd5e1", eyes: "#7dd3fc", skin: "#f5cba7", head: "<path d='M 24 58 Q 28 14 60 16 Q 92 14 96 58 L 86 34 Q 60 24 34 34 Z' fill='#facc15'/><path d='M 20 42 L 10 22 L 26 32 Z' fill='#cbd5e1'/><path d='M 100 42 L 110 22 L 94 32 Z' fill='#cbd5e1'/>" },
  { key: "STRANGE", name: "Dr. Strange", unlockCoins: 1200, perk: "⏳ Fast Radio & 10 🪙 Drops", shieldName: "Eldritch Tao Mandala", domeColor: 0xf97316, wireColor: 0xfde047, auraColor: 0xfb923c, suit: "#1e3a8a", accent: "#dc2626", trim: "#facc15", eyes: "#4ade80", skin: "#f5cba7", head: "<path d='M 28 46 Q 30 16 60 16 Q 90 16 92 46 L 84 32 Q 60 22 36 32 Z' fill='#1e293b'/><path d='M 26 42 L 34 42' stroke='#e2e8f0' stroke-width='4'/><path d='M 86 42 L 94 42' stroke='#e2e8f0' stroke-width='4'/>" },
  { key: "WANDA", name: "Wanda Maximoff", unlockCoins: 1300, perk: "🔮 2x Crop Growth & +6% O₂", shieldName: "Scarlet Chaos Hex", domeColor: 0xdc2626, wireColor: 0xfb7185, auraColor: 0xef4444, suit: "#7f1d1d", accent: "#ef4444", trim: "#fda4af", eyes: "#ef4444", skin: "#fbdcc4", head: "<path d='M 22 60 Q 26 16 60 16 Q 94 16 98 60 L 86 34 Q 60 24 34 34 Z' fill='#7c2d12'/><polygon points='42,38 50,18 60,30 70,18 78,38' fill='#ef4444' stroke='#fca5a5' stroke-width='1.5'/>" },
  { key: "LOKI", name: "Loki", unlockCoins: 1400, perk: "🐍 2x Vault Coins & +50% Sci", shieldName: "Horned Crown Ward", domeColor: 0x16a34a, wireColor: 0xfacc15, auraColor: 0x4ade80, suit: "#14532d", accent: "#eab308", trim: "#22c55e", eyes: "#4ade80", skin: "#f5cba7", head: "<path d='M 22 58 Q 24 18 60 18 Q 96 18 98 58 Z' fill='#0f172a'/><path d='M 34 40 Q 60 50 86 40 L 82 28 Q 60 38 38 28 Z' fill='#eab308'/><path d='M 40 32 Q 22 6 44 4 Q 34 18 46 30 Z' fill='#eab308'/><path d='M 80 32 Q 98 6 76 4 Q 86 18 74 30 Z' fill='#eab308'/>" }
];

const LOAD_FACTS = [
  "On Mars, sunlight is only 43% as strong as on the Moon (590 vs. 1,361 W/m²), and NASA's Perseverance MOXIE proved Martian CO₂ can be turned into breathable Oxygen!",
  "Shackleton Crater at the Moon's South Pole has sunlit rims for solar power right next to permanently shadowed water-ice craters!",
  "NASA Curiosity RAD measured ~0.67 mSv/day of radiation on Mars, while NASA RadLab/CRaTER places lunar surface baselines near 0.42 mSv/Sol!",
  "Radio signals travel at light speed: Moon-to-Earth round-trip takes 2.56 seconds (384,400 km), while Mars-to-Earth takes 6 to 44 minutes!"
];

const GLOSSARY = {
  SOL: { title: "📅 10-Minute Endurance Sol", body: "A Sol is one survival day-cycle! Each Sol runs 10 full minutes with 2 random NASA DONKI solar flares so you can explore in your 3D Rover, farm crops, and master real space survival." },
  POWER: { title: "⚡ Solar Power & Planet Climate", body: "Moon gets 100% sunlight (1,361 W/m²). Mars gets only 43% sunlight (590 W/m²) and frequent dust storms—so timing your Shield (Q) is critical!" },
  OXYGEN: { title: "🫁 Ice Electrolysis vs. Mars MOXIE", body: "Moon bases mine Shackleton water-ice (H₂O) for O₂. Mars bases run MOXIE to split Martian CO₂ into pure Oxygen! Keep your Airlock (E) sealed when inside." },
  FOOD: { title: "🌱 CSA 4-Crop Hydroponics", body: "Inspired by the CSA Deep Space Food Toolkit & NASA OSDR (OSD-767), your dome grows Tomatoes, Lettuce, Radishes & Potatoes without soil." },
  RAD: { title: "☢️ Radiation Dose (mSv)", body: "mSv measures radiation exposure (NASA RadLab & Curiosity RAD). Baseline is 0.42 mSv/Sol on Moon and 0.67 mSv/Sol on Mars—spiking during solar flares!" },
  DELAY: { title: "📡 Light-Speed Radio Delay", body: "Earth HQ is 384,400 km from the Moon (2.6s delay) and up to 400M km from Mars (simulated as a 6.5s delay in-game)!" }
};

let session = {
  screen: "LOADER", planet: "MOON", age: null, ageTier: "10-12 Commander",
  heroKey: "CAP", vaultCoins: 40, unlocked: ["CAP", "WIDOW"], wins: 0, musicOn: true,
  joystickVisible: ("ontouchstart" in window) || (navigator.maxTouchPoints > 0) || (window.innerWidth <= 820)
};

function getHero(k) { return HEROES.find(h => h.key === (k || session.heroKey)) || HEROES[0]; }
function getPlanet() { return PLANETS[session.planet] || PLANETS.MOON; }
function getDiff() {
  if (session.ageTier.includes("7-9")) return { drain: 0.24, flareWarn: 10.0, flareDur: 10.0, flareDmg: 3.2 };
  if (session.ageTier.includes("13+")) return { drain: 0.42, flareWarn: 7.5, flareDur: 12.0, flareDmg: 6.2 };
  return { drain: 0.32, flareWarn: 8.5, flareDur: 11.0, flareDmg: 4.6 };
}

function selectPlanet(pKey) {
  ensureAudio(); session.planet = pKey;
  playSfx(pKey === "MARS" ? 392 : 523.25, 0.16, "triangle", 0.08, pKey === "MARS" ? 587 : 659);
  document.getElementById("card-planet-MOON").className = "planet-card" + (pKey === "MOON" ? " active-moon" : "");
  document.getElementById("card-planet-MARS").className = "planet-card" + (pKey === "MARS" ? " active-mars" : "");
  document.getElementById("btn-start-world").innerText = pKey === "MARS" ? "🚀 LAUNCH MARS EXPEDITION (JEZERO)" : "🚀 LAUNCH MOON MISSION (SHACKLETON)";
}

let audioCtx = null, masterGain = null, musicTimer = null, musicBeat = 0;
const CHORDS = [
  { bass: 73.42, pad: [146.83, 220.00, 293.66, 349.23], lead: [587.33, 0, 523.25, 587.33, 659.25, 0, 587.33, 440.00] },
  { bass: 58.27, pad: [116.54, 174.61, 233.08, 293.66], lead: [466.16, 0, 523.25, 587.33, 698.46, 0, 659.25, 587.33] },
  { bass: 87.31, pad: [174.61, 220.00, 261.63, 349.23], lead: [698.46, 0, 659.25, 587.33, 523.25, 0, 587.33, 659.25] },
  { bass: 65.41, pad: [130.81, 196.00, 261.63, 329.63], lead: [523.25, 0, 587.33, 659.25, 783.99, 0, 659.25, 523.25] }
];

function ensureAudio() {
  if (!audioCtx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) { audioCtx = new AC(); masterGain = audioCtx.createGain(); masterGain.gain.value = 0.85; masterGain.connect(audioCtx.destination); }
  }
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
}
function playSynthVoice(freq, dur, type, vol, cutoff=1800, attack=0.02) {
  if (!session.musicOn || !freq) return;
  try {
    ensureAudio(); if (!audioCtx) return;
    const now = audioCtx.currentTime, osc = audioCtx.createOscillator(), filt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
    osc.type = type; osc.frequency.setValueAtTime(freq, now);
    filt.type = "lowpass"; filt.frequency.setValueAtTime(cutoff, now);
    g.gain.setValueAtTime(0.0001, now); g.gain.linearRampToValueAtTime(vol, now + attack); g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.connect(filt); filt.connect(g); g.connect(masterGain); osc.start(now); osc.stop(now + dur + 0.02);
  } catch(e) {}
}
function playKick() {
  if (!session.musicOn) return;
  try {
    ensureAudio(); if (!audioCtx) return;
    const now = audioCtx.currentTime, osc = audioCtx.createOscillator(), g = audioCtx.createGain();
    osc.type = "sine"; osc.frequency.setValueAtTime(112, now); osc.frequency.exponentialRampToValueAtTime(34, now + 0.14);
    g.gain.setValueAtTime(0.058, now); g.gain.exponentialRampToValueAtTime(0.0001, now + 0.16);
    osc.connect(g); g.connect(masterGain); osc.start(now); osc.stop(now + 0.17);
  } catch(e) {}
}
function startHeroicSoundtrack() {
  clearInterval(musicTimer);
  musicTimer = setInterval(() => {
    if (!session.musicOn || session.screen === "LOADER" || state.userPaused) return;
    const bar = Math.floor(musicBeat / 8) % CHORDS.length, step = musicBeat % 8, ch = CHORDS[bar];
    const p = session.planet === "MARS" ? 0.94 : 1.0;
    if (step === 0) ch.pad.forEach(n => playSynthVoice(n * p, 2.3, "sawtooth", 0.013, 720, 0.24));
    if (step % 2 === 0) playSynthVoice(ch.bass * p, 0.4, "triangle", 0.045, 360, 0.01);
    if (step === 0 || step === 4 || step === 6) playKick();
    if (ch.lead[step] > 0) playSynthVoice(ch.lead[step] * p, 0.36, "triangle", 0.024, 2200, 0.015);
    musicBeat++;
  }, 290);
}
function playSfx(freq, dur=0.14, type="sine", vol=0.075, slideTo=null) {
  if (!session.musicOn) return;
  try {
    ensureAudio(); if (!audioCtx) return;
    const now = audioCtx.currentTime, o = audioCtx.createOscillator(), g = audioCtx.createGain();
    o.type = type; o.frequency.setValueAtTime(freq, now);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, now + dur);
    g.gain.setValueAtTime(vol, now); g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    o.connect(g); g.connect(masterGain); o.start(now); o.stop(now + dur + 0.02);
  } catch(e) {}
}
function syncMusicButtons() {
  const lbl = session.musicOn ? "🎵 MUSIC: ON" : "🔇 MUSIC: OFF";
  document.getElementById("create-music-btn").innerText = lbl;
  document.getElementById("sb-music-btn").innerText = lbl;
  document.getElementById("hud-music-btn").innerText = session.musicOn ? "🔊 V" : "🔇 V";
}
function toggleMusic() { ensureAudio(); session.musicOn = !session.musicOn; syncMusicButtons(); if (session.musicOn) { playSfx(523, 0.18, "triangle", 0.08, 784); startHeroicSoundtrack(); } }

function syncJoystickVisibility() {
  document.getElementById("joy-wrap").classList.toggle("visible", session.joystickVisible);
  document.getElementById("mobile-quick-pad").classList.toggle("visible", session.joystickVisible);
}
function toggleJoystick() { session.joystickVisible = !session.joystickVisible; syncJoystickVisibility(); playSfx(560, 0.1, "triangle", 0.06); }

let joyX = 0, joyY = 0, joyPointerId = null;
const joyBase = document.getElementById("joy-base"), joyKnob = document.getElementById("joy-knob");
function updateJoy(cx, cy) {
  const rect = joyBase.getBoundingClientRect(), maxR = rect.width * 0.38;
  let dx = cx - (rect.left + rect.width / 2), dy = cy - (rect.top + rect.height / 2);
  const d = Math.hypot(dx, dy);
  if (d > maxR) { dx = (dx / d) * maxR; dy = (dy / d) * maxR; }
  joyKnob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
  joyX = dx / maxR; joyY = dy / maxR;
}
joyBase.addEventListener("pointerdown", e => { e.preventDefault(); ensureAudio(); joyPointerId = e.pointerId; joyBase.setPointerCapture(e.pointerId); updateJoy(e.clientX, e.clientY); });
joyBase.addEventListener("pointermove", e => { if (e.pointerId === joyPointerId) { e.preventDefault(); updateJoy(e.clientX, e.clientY); } });
function relJoy(e) { if (e.pointerId === joyPointerId) { joyPointerId = null; joyX = 0; joyY = 0; joyKnob.style.transform = "translate(-50%, -50%)"; } }
joyBase.addEventListener("pointerup", relJoy); joyBase.addEventListener("pointercancel", relJoy);

const bgCanvas = document.getElementById("bg-space-canvas"), bgCtx = bgCanvas.getContext("2d");
let bgStars = [];
function initBgStars() {
  bgCanvas.width = window.innerWidth || 1200; bgCanvas.height = window.innerHeight || 800;
  bgStars = Array.from({ length: 160 }, () => ({ x: Math.random() * bgCanvas.width, y: Math.random() * bgCanvas.height, r: 0.6 + Math.random() * 1.8, s: 0.15 + Math.random() * 0.45, p: Math.random() * 6.28 }));
}
initBgStars();
function drawBgSpace(ts) {
  requestAnimationFrame(drawBgSpace);
  if (session.screen === "GAME") return;
  const w = bgCanvas.width, h = bgCanvas.height, grd = bgCtx.createRadialGradient(w * 0.5, h * 0.15, 20, w * 0.5, h * 0.5, w * 0.85);
  grd.addColorStop(0, "#1e1b4b"); grd.addColorStop(0.55, "#090d1f"); grd.addColorStop(1, "#020617");
  bgCtx.fillStyle = grd; bgCtx.fillRect(0, 0, w, h);
  bgStars.forEach(st => { bgCtx.fillStyle = `rgba(224,242,254,${0.45 + 0.55 * Math.sin(ts * 0.002 * st.s + st.p)})`; bgCtx.beginPath(); bgCtx.arc(st.x, st.y, st.r, 0, 6.28); bgCtx.fill(); });
  bgCtx.fillStyle = "rgba(100,116,139,0.22)"; bgCtx.beginPath(); bgCtx.ellipse(w * 0.5, h + 110, w * 0.72, 210, 0, Math.PI, 0); bgCtx.fill();
}
requestAnimationFrame(drawBgSpace);

function showScreen(id) { document.querySelectorAll(".screen").forEach(s => s.classList.remove("active")); document.getElementById(id).classList.add("active"); }

function startFiveSecondLoader() {
  session.screen = "LOADER"; showScreen("screen-loader");
  document.getElementById("load-fact").innerText = LOAD_FACTS[Math.floor(Math.random() * LOAD_FACTS.length)];
  const steps = ["Connecting to NASA DONKI Space Weather...", "Loading 3D Explorer Rover & Habitat...", "Forging Hero Shields & Space Suits...", "Calibrating 10-Minute Sol Clocks...", "Avengers Assemble — Ready!"];
  const t0 = performance.now();
  function tick(now) {
    const pct = Math.min(100, ((now - t0) / 5000) * 100);
    document.getElementById("load-bar-fill").style.width = pct + "%";
    document.getElementById("load-pct").innerText = Math.floor(pct) + "%";
    document.getElementById("load-status").innerText = steps[Math.min(steps.length - 1, Math.floor((pct / 100) * steps.length))];
    if (pct < 100) requestAnimationFrame(tick); else goToCreatePage();
  }
  requestAnimationFrame(tick);
}

function goToCreatePage() {
  session.screen = "CREATE"; state.paused = true;
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("multi-notice").style.display = "none";
  selectPlanet(session.planet); syncMusicButtons(); showScreen("screen-create");
}
function clickMultiplayer() { ensureAudio(); playSfx(240, 0.18, "sawtooth", 0.06); document.getElementById("multi-notice").style.display = "block"; }

let notifiedAffordable = {};
function addVaultCoins(amount) {
  if (amount <= 0) return;
  session.vaultCoins += amount;
  syncVaultDisplays();
  if (session.screen === "GAME") {
    HEROES.forEach(h => {
      if (!session.unlocked.includes(h.key) && session.vaultCoins >= h.unlockCoins && !notifiedAffordable[h.key]) {
        notifiedAffordable[h.key] = true;
        const b = document.getElementById("unlock-banner");
        b.innerText = `🪙 ${h.unlockCoins} COINS REACHED! Open MENU → Change Hero to buy ${h.name.toUpperCase()}!`;
        b.style.display = "block";
        playSfx(587, 0.28, "triangle", 0.1, 1174);
        clearTimeout(b._t); b._t = setTimeout(() => { b.style.display = "none"; }, 4200);
      }
    });
  }
}

function syncVaultDisplays() {
  const v = Math.floor(session.vaultCoins);
  document.getElementById("age-vault-coins").innerText = v;
  document.getElementById("ui-coins").innerText = v;
  document.getElementById("sb-coins").innerText = v;
  document.getElementById("deb-vault").innerText = v;
  document.getElementById("sb-wins").innerText = session.wins;
}

function renderHeroGrid() {
  syncVaultDisplays();
  const grid = document.getElementById("hero-grid");
  grid.innerHTML = "";
  HEROES.forEach(h => {
    const unlocked = session.unlocked.includes(h.key);
    const canBuy = !unlocked && session.vaultCoins >= h.unlockCoins;
    const selected = session.heroKey === h.key;
    const card = document.createElement("div");
    card.className = "hero-card" + (selected ? " selected" : "") + (canBuy ? " can-buy" : (!unlocked ? " locked" : ""));
    const lockSvg = unlocked ? "" : `<rect x="0" y="0" width="120" height="140" rx="14" fill="rgba(2,6,23,0.78)"/><text x="60" y="64" text-anchor="middle" fill="#fde047" font-size="26">${canBuy ? "🔓" : "🔒"}</text><text x="60" y="94" text-anchor="middle" fill="#ffffff" font-size="11.5" font-weight="bold">${h.unlockCoins} 🪙</text>`;
    const stClass = unlocked ? "st-ok" : (canBuy ? "st-buy" : "st-lock");
    const stText = unlocked ? (selected ? "✅ SELECTED" : "🔓 UNLOCKED") : (canBuy ? `🪙 BUY (-${h.unlockCoins})` : `🔒 ${Math.floor(session.vaultCoins)}/${h.unlockCoins} 🪙`);
    card.innerHTML = `
      <svg width="76" height="88" viewBox="0 0 120 140">
        <circle cx="60" cy="52" r="36" fill="#f8fafc" stroke="${h.suit}" stroke-width="4"/><circle cx="60" cy="53" r="22" fill="#ffedd5"/>
        <ellipse cx="51" cy="52" rx="4.5" ry="5.5" fill="${h.eyes}"/><circle cx="49.5" cy="50" r="1.8" fill="#fff"/>
        <ellipse cx="69" cy="52" rx="4.5" ry="5.5" fill="${h.eyes}"/><circle cx="67.5" cy="50" r="1.8" fill="#fff"/>
        <path d="M 54 62 Q 60 67 66 62" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        ${h.head}<rect x="32" y="88" width="56" height="44" rx="14" fill="${h.suit}" stroke="${h.accent}" stroke-width="3.5"/>
        <circle cx="60" cy="108" r="7" fill="#38bdf8" stroke="#fff" stroke-width="1.5"/>${lockSvg}
      </svg>
      <div class="hero-name">${h.name}</div>
      <div class="hero-shield-tag">✨ ${h.shieldName}</div>
      <div class="hero-perk">${h.perk}</div>
      <div class="hero-status ${stClass}">${stText}</div>
    `;
    card.onclick = () => {
      ensureAudio();
      if (unlocked) {
        session.heroKey = h.key;
        document.getElementById("hero-msg").innerText = `✅ Selected ${h.name}!`;
        playSfx(640, 0.12, "triangle", 0.07);
        renderHeroGrid(); validateAgePage();
      } else if (session.vaultCoins >= h.unlockCoins) {
        session.vaultCoins -= h.unlockCoins;
        session.unlocked.push(h.key);
        session.heroKey = h.key;
        playSfx(523, 0.24, "triangle", 0.1, 1046);
        document.getElementById("hero-msg").innerText = `🎉 Unlocked ${h.name}! (-${h.unlockCoins} 🪙 deducted from Vault — Remaining: ${Math.floor(session.vaultCoins)} 🪙)`;
        renderHeroGrid(); validateAgePage();
      } else {
        const need = Math.ceil(h.unlockCoins - session.vaultCoins);
        document.getElementById("hero-msg").innerText = `❌ Need ${need} more Vault Coins to unlock ${h.name}!`;
        playSfx(210, 0.16, "sawtooth", 0.07);
      }
    };
    grid.appendChild(card);
  });
}

function validateAgePage() {
  const num = parseInt(document.getElementById("age-input").value.trim(), 10);
  const fb = document.getElementById("age-feedback"), btn = document.getElementById("btn-to-inst");
  if (isNaN(num) || num < 1 || num > 100) {
    session.age = null; fb.style.color = "#fca5a5"; fb.innerText = "👉 Enter valid age (1–100) to continue"; btn.disabled = true;
  } else {
    session.age = num;
    session.ageTier = num <= 9 ? "7-9 Cadet" : (num <= 12 ? "10-12 Commander" : "13+ Mission Planner");
    fb.style.color = "#86efac"; fb.innerText = `✅ ${session.ageTier} Mode Ready`; btn.disabled = false;
  }
}

function goToAgePage() {
  ensureAudio(); startHeroicSoundtrack(); state.paused = true; session.screen = "AGE";
  document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("pause-modal").style.display = "none";
  document.getElementById("hero-msg").innerText = "";
  if (session.age) document.getElementById("age-input").value = session.age;
  renderHeroGrid(); validateAgePage(); showScreen("screen-age");
}

function goToInstructions() {
  if (!session.age) return;
  ensureAudio(); playSfx(523, 0.14, "triangle", 0.08); session.screen = "INSTRUCTIONS";
  const h = getHero(), pl = getPlanet();
  document.getElementById("inst-hero-line").innerText = `${pl.icon} ${pl.name} (${pl.site}) • ${h.name} • ${session.ageTier} • 10-Min Sols`;
  document.getElementById("btn-launch-final").innerText = `🚀 LAUNCH 3D ${pl.name.toUpperCase()} MISSION`;
  showScreen("screen-instructions");
}

const STATIONS = {
  SOLAR:   { x: -21.0, z: 10.5,  r: 3.8, label: "☀️ Scrubbing Solar Dust...", color: 0xfacc15, tag: "☀️ SOLAR ARRAY" },
  O2GEN:   { x: -18.5, z: -17.5, r: 3.8, label: "🧊 Generating Oxygen...", color: 0x38bdf8, tag: "🧊 O₂ STATION" },
  SCIENCE: { x: 19.5,  z: 17.5,  r: 3.8, label: "🔬 Drilling Core Sample (-O₂, +Sci)...", color: 0xd8b4fe, tag: "🔬 EVA SCIENCE" },
  FARM:    { x: 21.0,  z: -5.0,  r: 4.0, label: "🌱 Harvesting CSA Crops...", color: 0x4ade80, tag: "🌱 CSA FARM" },
  PANTRY:  { x: 2.3,   z: -1.2,  r: 2.2, label: "🍽️ Stocking Pantry Table...", color: 0xf472b6, tag: "🍽️ PANTRY" },
  SHIELD:  { x: -2.4,  z: -1.4,  r: 2.1, label: "🛡️ Shield Console", color: 0x60a5fa, tag: "🛡️ SHIELD" }
};

let state = { started: false, paused: true, userPaused: false, ended: false };
let telemetryLog = [], lastShieldToggleMs = 0;

function makeSolFlares() {
  const f1 = 45 + Math.random() * 210;
  const f2 = 315 + Math.random() * 215;
  return [f1, f2];
}

function resetMissionState() {
  const pl = getPlanet();
  state = {
    started: true, paused: false, userPaused: false, ended: false,
    sol: 1, solClock: 0, flareSchedule: makeSolFlares(), flaresTriggered: 0,
    power: 96, oxygen: 96, food: 92, hp: 100, rad: pl.radBaseline, science: 0,
    doorSealed: true, shieldOn: false, dusty: false,
    flarePhase: "CALM", flareTimer: 0,
    basket: [], pantryCount: 3, crops: [100, 100, 75, 100],
    autoTarget: null, activePad: null, padProgress: 0, shieldPadLatched: false,
    driving: false, roverSpeed: 0, roverSteer: 0,
    emote: null, emoteTimer: 0,
    roverCooldown: 0, radioBusy: false, radioBeamTimer: 0,
    camZoom: 1.0, fullPlanetMode: false, dilemmasShown: {}
  };
  telemetryLog = [{ sol: 1, pwr: 96, ox: 96, hp: 100 }];
}

let threeReady = false, scene, camera, renderer, clock, worldGroup;
let heroGroup, heroBodyRig, heroLimbs = {}, heroBasketGroup, heroShieldFX, heroCoffeeMug, heroAuraRings = [], heroLightning = [];
let sunMesh, sunGlow, dirLight, hemiLight, beaconLight, earthGroup, radioBeamMesh, commsDishHead, scoutDrone, droneRotor, landerStrobe;
let shieldDomeMesh, shieldWireMesh, shieldRingMesh, airlockDoorMesh, airlockGlowMat;
let solarDustMeshes = [], cropMeshes = [], pantryFoodGroup, drillCrystal;
let playerRover, roverWheels = [], roverFrontPivots = [], roverPos = null, roverRotY = 0;
let coinOrbs = [], flareParticles, fxParticles = [], shootingStar, padRings = {};
let heroPos = null, heroVelY = 0, heroRotY = 0, wasInside = true, footstepTimer = 0, runCycle = 0;
const keys = {};

function makeLunarTexture() {
  const c = document.createElement("canvas"); c.width = 512; c.height = 512;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#6b7280"; ctx.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 6500; i++) {
    const v = 80 + Math.floor(Math.random() * 52);
    ctx.fillStyle = `rgb(${v},${v + 6},${v + 16})`;
    ctx.fillRect(Math.random() * 512, Math.random() * 512, 2.2, 2.2);
  }
  for (let i = 0; i < 50; i++) {
    const x = Math.random() * 512, y = Math.random() * 512, r = 6 + Math.random() * 26;
    const g = ctx.createRadialGradient(x, y, r * 0.2, x, y, r);
    g.addColorStop(0, "rgba(30,41,59,0.55)"); g.addColorStop(0.75, "rgba(100,116,139,0.18)"); g.addColorStop(1, "rgba(226,232,240,0.34)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, 6.28); ctx.fill();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(14, 14);
  return tex;
}

function makeCapShieldTexture() {
  const c = document.createElement("canvas"); c.width = 256; c.height = 256;
  const ctx = c.getContext("2d"), cx = 128, cy = 128;
  [[124, "#dc2626"], [98, "#f8fafc"], [72, "#dc2626"], [48, "#1d4ed8"]].forEach(([r, col]) => { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 6.28); ctx.fill(); });
  ctx.fillStyle = "#fff"; ctx.beginPath();
  for (let i = 0; i < 5; i++) {
    const a1 = -Math.PI / 2 + (i * 2 * Math.PI) / 5, a2 = a1 + Math.PI / 5;
    if (i === 0) ctx.moveTo(cx + Math.cos(a1) * 38, cy + Math.sin(a1) * 38); else ctx.lineTo(cx + Math.cos(a1) * 38, cy + Math.sin(a1) * 38);
    ctx.lineTo(cx + Math.cos(a2) * 16, cy + Math.sin(a2) * 16);
  }
  ctx.closePath(); ctx.fill(); return new THREE.CanvasTexture(c);
}

function makeMandalaTexture() {
  const c = document.createElement("canvas"); c.width = 256; c.height = 256;
  const ctx = c.getContext("2d");
  ctx.strokeStyle = "#f97316"; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(128, 128, 114, 0, 6.28); ctx.stroke();
  ctx.strokeStyle = "#fde047"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(128, 128, 86, 0, 6.28); ctx.stroke();
  for (let i = 0; i < 2; i++) { ctx.save(); ctx.translate(128, 128); ctx.rotate(i * Math.PI / 4); ctx.strokeRect(-70, -70, 140, 140); ctx.restore(); }
  return new THREE.CanvasTexture(c);
}

function makeFloatingLabel(text, borderHex) {
  const c = document.createElement("canvas"); c.width = 280; c.height = 64;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "rgba(9,13,31,0.88)"; ctx.strokeStyle = borderHex; ctx.lineWidth = 5;
  ctx.beginPath(); ctx.roundRect(6, 8, 268, 48, 14); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#fff"; ctx.font = "900 19px Segoe UI, sans-serif"; ctx.textAlign = "center"; ctx.fillText(text, 140, 40);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  sp.scale.set(5.8, 1.35, 1); return sp;
}

function buildHero3D() {
  if (heroGroup) scene.remove(heroGroup);
  heroAuraRings = []; heroLightning = [];
  const h = getHero();
  heroGroup = new THREE.Group(); heroBodyRig = new THREE.Group(); heroGroup.add(heroBodyRig);

  const shadowBlob = new THREE.Mesh(new THREE.CircleGeometry(0.82, 20), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.42, depthWrite: false }));
  shadowBlob.rotation.x = -Math.PI / 2; shadowBlob.position.y = 0.05; heroGroup.add(shadowBlob);

  const suitMat = new THREE.MeshStandardMaterial({ color: h.suit, roughness: 0.32, metalness: 0.35 });
  const accMat  = new THREE.MeshStandardMaterial({ color: h.accent, roughness: 0.28, metalness: 0.45 });
  const trimMat = new THREE.MeshStandardMaterial({ color: h.trim, roughness: 0.25, metalness: 0.6 });
  const skinMat = new THREE.MeshStandardMaterial({ color: h.skin, roughness: 0.55 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.5 });

  const chest = new THREE.Mesh(new THREE.BoxGeometry(0.96, 0.82, 0.54), suitMat); chest.position.y = 1.82; chest.castShadow = true; heroBodyRig.add(chest);
  const waist = new THREE.Mesh(new THREE.BoxGeometry(0.76, 0.38, 0.44), accMat); waist.position.y = 1.26; heroBodyRig.add(waist);
  const belt = new THREE.Mesh(new THREE.BoxGeometry(0.84, 0.14, 0.5), darkMat); belt.position.y = 1.12; heroBodyRig.add(belt);
  const buckle = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.16, 0.54), trimMat); buckle.position.y = 1.12; heroBodyRig.add(buckle);
  [-0.56, 0.56].forEach(sx => { const p = new THREE.Mesh(new THREE.SphereGeometry(0.25, 12, 12), accMat); p.position.set(sx, 2.12, 0); heroBodyRig.add(p); });
  const emblem = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.08, 16), new THREE.MeshBasicMaterial({ color: h.auraColor }));
  emblem.rotation.x = Math.PI / 2; emblem.position.set(0, 1.88, 0.29); heroBodyRig.add(emblem);

  const headGrp = new THREE.Group(); headGrp.position.y = 2.66;
  headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.38, 18, 18), h.key === "IRON" ? accMat : skinMat));
  headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.49, 16, 14), new THREE.MeshStandardMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.22, roughness: 0.1, depthWrite: false })));
  [-0.13, 0.13].forEach(ex => { const e = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.06, 0.06), new THREE.MeshBasicMaterial({ color: h.eyes })); e.position.set(ex, 0.04, 0.35); headGrp.add(e); });

  if (h.key === "CAP") headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.41, 14, 12, 0, 6.28, 0, Math.PI * 0.58), suitMat));
  else if (h.key === "IRON") { const fp = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.44, 0.14), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.85 })); fp.position.set(0, 0, 0.32); headGrp.add(fp); }
  else if (h.key === "LOKI") {
    const cr = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.06, 8, 18), new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.9 }));
    cr.rotation.x = Math.PI / 2; cr.position.y = 0.24; headGrp.add(cr);
    [-0.24, 0.24].forEach(hx => { const hn = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.72, 10), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.9 })); hn.position.set(hx, 0.62, 0.16); hn.rotation.z = hx > 0 ? -0.35 : 0.35; hn.rotation.x = 0.38; headGrp.add(hn); });
  } else if (h.key === "WANDA") { const ti = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.42, 4), accMat); ti.position.set(0, 0.36, 0.22); headGrp.add(ti); }
  else if (h.key === "THOR") headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.42, 14, 12, 0, 6.28, 0, Math.PI * 0.62), new THREE.MeshStandardMaterial({ color: 0xfacc15 })));
  else if (h.key === "WIDOW") headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.42, 14, 12, 0, 6.28, 0, Math.PI * 0.66), new THREE.MeshStandardMaterial({ color: 0xb91c1c })));
  else headGrp.add(new THREE.Mesh(new THREE.SphereGeometry(0.41, 14, 12, 0, 6.28, 0, Math.PI * 0.55), darkMat));
  heroBodyRig.add(headGrp);

  if (["THOR", "STRANGE", "LOKI", "WANDA"].includes(h.key)) {
    const cape = new THREE.Mesh(new THREE.BoxGeometry(0.95, 1.55, 0.06), new THREE.MeshStandardMaterial({ color: h.key === "LOKI" ? 0x15803d : 0xdc2626 }));
    cape.position.set(0, 1.38, -0.35); cape.rotation.x = 0.2; heroLimbs.cape = cape; heroBodyRig.add(cape);
  } else heroLimbs.cape = null;

  function makeLimb(x, y, m1, m2, isLeg) {
    const p = new THREE.Group(); p.position.set(x, y, 0);
    const u = new THREE.Mesh(new THREE.CylinderGeometry(isLeg ? 0.16 : 0.13, isLeg ? 0.14 : 0.11, isLeg ? 0.52 : 0.44, 10), m1);
    u.position.y = isLeg ? -0.26 : -0.22; p.add(u);
    const j = new THREE.Group(); j.position.y = isLeg ? -0.52 : -0.44;
    const l = new THREE.Mesh(new THREE.CylinderGeometry(isLeg ? 0.13 : 0.11, isLeg ? 0.12 : 0.10, isLeg ? 0.50 : 0.40, 10), m2);
    l.position.y = isLeg ? -0.25 : -0.20; j.add(l);
    if (isLeg) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.18, 0.42), darkMat); b.position.set(0, -0.50, 0.07); j.add(b); }
    p.add(j); p.userData.lower = j; heroBodyRig.add(p); return p;
  }
  heroLimbs.lArm = makeLimb(-0.60, 2.08, suitMat, accMat, false);
  heroLimbs.rArm = makeLimb(0.60, 2.08, suitMat, accMat, false);
  heroLimbs.lLeg = makeLimb(-0.24, 1.08, suitMat, darkMat, true);
  heroLimbs.rLeg = makeLimb(0.24, 1.08, suitMat, darkMat, true);

  heroCoffeeMug = new THREE.Group();
  const mug = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.11, 0.24, 12), new THREE.MeshStandardMaterial({ color: 0xf8fafc, emissive: 0x38bdf8, emissiveIntensity: 0.25 }));
  const cof = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.04, 12), new THREE.MeshBasicMaterial({ color: 0x78350f }));
  cof.position.y = 0.11; heroCoffeeMug.add(mug, cof);
  heroCoffeeMug.position.set(0, -0.42, 0.18); heroCoffeeMug.visible = false;
  heroLimbs.rArm.userData.lower.add(heroCoffeeMug);

  if (h.key === "CAP") {
    const sh = new THREE.Mesh(new THREE.CylinderGeometry(0.54, 0.54, 0.08, 24), [new THREE.MeshStandardMaterial({ color: 0xdc2626 }), new THREE.MeshStandardMaterial({ map: makeCapShieldTexture() }), new THREE.MeshStandardMaterial({ color: 0x94a3b8 })]);
    sh.rotation.z = Math.PI / 2; sh.position.set(-0.18, -0.30, 0.14); heroLimbs.lArm.userData.lower.add(sh);
  } else if (h.key === "THOR") {
    const mj = new THREE.Group();
    mj.add(new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.05, 0.55, 8), new THREE.MeshStandardMaterial({ color: 0x78350f })));
    const hm = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.26, 0.46), new THREE.MeshStandardMaterial({ color: 0xcbd5e1, metalness: 0.9 }));
    hm.position.y = 0.28; mj.add(hm); mj.rotation.x = Math.PI / 2; mj.position.set(0, -0.36, 0.22); heroLimbs.rArm.userData.lower.add(mj);
  }

  heroShieldFX = new THREE.Group(); heroShieldFX.position.set(0, 1.65, 0);
  if (h.key === "CAP") {
    const gs = new THREE.Mesh(new THREE.CylinderGeometry(1.38, 1.38, 0.1, 28), [new THREE.MeshBasicMaterial({ color: 0xef4444 }), new THREE.MeshBasicMaterial({ map: makeCapShieldTexture(), transparent: true, opacity: 0.92, depthWrite: false }), new THREE.MeshBasicMaterial({ map: makeCapShieldTexture(), transparent: true, opacity: 0.85, depthWrite: false })]);
    gs.rotation.x = Math.PI / 2; gs.position.set(0, 0.15, 1.05);
    const hr = new THREE.Mesh(new THREE.TorusGeometry(1.62, 0.05, 10, 32), new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.8, depthWrite: false }));
    hr.position.set(0, 0.15, 1.05); heroShieldFX.add(gs, hr); heroAuraRings.push(hr);
  } else if (h.key === "THOR") {
    const piv = new THREE.Group();
    const hm = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.36, 0.62), new THREE.MeshStandardMaterial({ color: 0xe0f2fe, emissive: 0x38bdf8, emissiveIntensity: 0.9 }));
    hm.position.set(1.65, 0.25, 0); piv.add(hm); heroShieldFX.add(piv); heroAuraRings.push(piv);
    for (let i = 0; i < 5; i++) {
      const b = new THREE.Mesh(new THREE.TorusGeometry(1.55, 0.04, 6, 18), new THREE.MeshBasicMaterial({ color: i % 2 ? 0xffffff : 0x7dd3fc, transparent: true, opacity: 0.85, depthWrite: false }));
      b.rotation.set(i * 0.6, i * 0.9, 0); heroShieldFX.add(b); heroLightning.push(b);
    }
  } else if (h.key === "LOKI") {
    const ch = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.07, 10, 30), new THREE.MeshBasicMaterial({ color: 0xeab308, depthWrite: false }));
    ch.rotation.x = Math.PI / 2; ch.position.y = 1.4;
    const gw = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 2.5, 8, 1, true), new THREE.MeshBasicMaterial({ color: 0x22c55e, wireframe: true, transparent: true, opacity: 0.72, depthWrite: false }));
    heroShieldFX.add(ch, gw); heroAuraRings.push(ch, gw);
  } else if (h.key === "STRANGE") {
    const mt = makeMandalaTexture();
    [1.15, -1.15].forEach(z => { const d = new THREE.Mesh(new THREE.PlaneGeometry(2.7, 2.7), new THREE.MeshBasicMaterial({ map: mt, transparent: true, opacity: 0.92, side: THREE.DoubleSide, depthWrite: false })); d.position.set(0, 0.1, z); heroShieldFX.add(d); heroAuraRings.push(d); });
  } else if (h.key === "WANDA") {
    const hx = new THREE.Mesh(new THREE.IcosahedronGeometry(1.65, 1), new THREE.MeshBasicMaterial({ color: 0xef4444, wireframe: true, transparent: true, opacity: 0.8, depthWrite: false }));
    heroShieldFX.add(hx); heroAuraRings.push(hx);
  } else if (h.key === "IRON") {
    const np = new THREE.Mesh(new THREE.CircleGeometry(1.45, 6), new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.52, side: THREE.DoubleSide, depthWrite: false })); np.position.set(0, 0.15, 1.15);
    const ne = new THREE.Mesh(new THREE.RingGeometry(1.36, 1.5, 6), new THREE.MeshBasicMaterial({ color: 0xfacc15, side: THREE.DoubleSide, depthWrite: false })); ne.position.set(0, 0.15, 1.16);
    heroShieldFX.add(np, ne); heroAuraRings.push(ne);
  } else {
    const r1 = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.06, 10, 26), new THREE.MeshBasicMaterial({ color: 0x38bdf8, depthWrite: false })); r1.rotation.x = Math.PI / 2;
    heroShieldFX.add(r1); heroAuraRings.push(r1);
  }
  heroShieldFX.visible = state.shieldOn; heroGroup.add(heroShieldFX);

  heroBasketGroup = new THREE.Group(); heroBasketGroup.position.set(0, 1.7, -0.58); heroBodyRig.add(heroBasketGroup);
  heroGroup.position.copy(heroPos); scene.add(heroGroup);
  refreshBasketVisuals();

  if (shieldDomeMesh) {
    shieldDomeMesh.material.color.setHex(h.domeColor);
    shieldWireMesh.material.color.setHex(h.wireColor);
    shieldRingMesh.material.color.setHex(h.auraColor);
  }
}

function init3DEngineOnce() {
  if (threeReady) return;
  const cont = document.getElementById("canvas-container");
  const w = cont.clientWidth || window.innerWidth, h = cont.clientHeight || window.innerHeight;
  heroPos = new THREE.Vector3(0, 0, 1.5);
  roverPos = new THREE.Vector3(0, 0, 11.5);
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  scene.fog = new THREE.FogExp2(0x050b1f, 0.0022);

  camera = new THREE.PerspectiveCamera(52, w / h, 0.1, 600);
  camera.position.set(0, 15, 22);

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(w, h); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  cont.appendChild(renderer.domElement);

  clock = new THREE.Clock();
  hemiLight = new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.8); scene.add(hemiLight);
  dirLight = new THREE.DirectionalLight(0xfff8eb, 1.55); dirLight.position.set(-55, 58, 32); dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(1024, 1024); const d = 64;
  dirLight.shadow.camera.left = -d; dirLight.shadow.camera.right = d; dirLight.shadow.camera.top = d; dirLight.shadow.camera.bottom = -d;
  scene.add(dirLight);
  beaconLight = new THREE.PointLight(0x38bdf8, 1.2, 18); beaconLight.position.set(0, 4.5, 0); scene.add(beaconLight);

  worldGroup = new THREE.Group(); scene.add(worldGroup);
  threeReady = true;
  setupCanvasZoomGestures();
  animate3D();
}

function buildWorld3D() {
  const pl = getPlanet(), h = getHero();
  while (worldGroup.children.length > 0) worldGroup.remove(worldGroup.children[0]);
  solarDustMeshes = []; cropMeshes = []; coinOrbs = []; fxParticles = []; padRings = {};
  roverWheels = []; roverFrontPivots = [];
  scene.background = new THREE.Color(0x020617);
  scene.fog = new THREE.FogExp2(0x050b1f, 0.0022);

  const starGeo = new THREE.BufferGeometry(), sPos = new Float32Array(2000 * 3);
  for (let i = 0; i < 2000; i++) {
    const r = 150 + Math.random() * 150, th = Math.random() * 6.28, ph = Math.acos(Math.random() * 1.6 - 0.8);
    sPos[i*3] = r * Math.sin(ph) * Math.cos(th); sPos[i*3+1] = r * Math.cos(ph); sPos[i*3+2] = r * Math.sin(ph) * Math.sin(th);
  }
  starGeo.setAttribute("position", new THREE.BufferAttribute(sPos, 3));
  worldGroup.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0xe0f2fe, size: 0.8 })));

  shootingStar = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.24, 5.5), new THREE.MeshBasicMaterial({ color: 0xbae6fd }));
  shootingStar.position.set(-80, 50, -85); worldGroup.add(shootingStar);

  sunMesh = new THREE.Mesh(new THREE.SphereGeometry(9.0, 24, 24), new THREE.MeshBasicMaterial({ color: 0xfde047 }));
  sunMesh.position.set(-92, 62, -85); worldGroup.add(sunMesh);
  sunGlow = new THREE.Mesh(new THREE.SphereGeometry(13.5, 24, 24), new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.26, depthWrite: false }));
  sunGlow.position.copy(sunMesh.position); worldGroup.add(sunGlow);

  earthGroup = new THREE.Group(); earthGroup.position.set(74, 55, -94);
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(9.0, 24, 24), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, emissive: 0x1e40af, emissiveIntensity: 0.3 })));
  const lm = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8 });
  [[-3.2, 2.4, 7.6, 3.4], [3.6, -1.5, 7.2, 2.9], [0.4, 5.0, -6.5, 3.1]].forEach(c => { const p = new THREE.Mesh(new THREE.SphereGeometry(c[3], 12, 12), lm); p.position.set(c[0], c[1], c[2]); p.scale.set(1, 0.8, 0.5); earthGroup.add(p); });
  worldGroup.add(earthGroup);

  const lunarTex = makeLunarTexture();
  const diskGeo = new THREE.CircleGeometry(82, 64); diskGeo.rotateX(-Math.PI / 2);
  const ground = new THREE.Mesh(diskGeo, new THREE.MeshStandardMaterial({ map: lunarTex, roughness: 0.94, metalness: 0.04 }));
  ground.receiveShadow = true; worldGroup.add(ground);

  const body = new THREE.Mesh(new THREE.SphereGeometry(86, 40, 28), new THREE.MeshStandardMaterial({ map: lunarTex, color: 0x475569, roughness: 0.96 }));
  body.position.set(0, -28, 0); worldGroup.add(body);

  const rim = new THREE.Mesh(new THREE.TorusGeometry(69, 2.8, 10, 54), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.95 }));
  rim.rotation.x = Math.PI / 2; rim.position.y = 0.8; worldGroup.add(rim);

  const rockMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 });
  [[-38, 28], [-44, -22], [40, 30], [45, -26], [12, 42], [-18, -44], [34, -38], [-32, 36], [50, 6], [-50, -6], [0, -48], [26, 40], [-36, -38], [44, 16]].forEach(([rx, rz]) => {
    const rk = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6 + Math.random() * 2.1, 0), rockMat);
    rk.position.set(rx, 0.8, rz); rk.rotation.y = Math.random() * 6; rk.castShadow = true; worldGroup.add(rk);
  });
  [[-38, -32, 7.5], [38, -32, 8.2], [-40, 32, 6.8], [36, 34, 7.2]].forEach(([cx, cz, rad]) => {
    const cr = new THREE.Mesh(new THREE.TorusGeometry(rad, 0.65, 8, 24), rockMat); cr.rotation.x = Math.PI / 2; cr.position.set(cx, 0.16, cz); worldGroup.add(cr);
  });

  function addPath(x1, z1, x2, z2, col) {
    const p = new THREE.Mesh(new THREE.PlaneGeometry(Math.hypot(x2 - x1, z2 - z1), 1.35), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.28, depthWrite: false }));
    p.rotation.x = -Math.PI / 2; p.rotation.z = -Math.atan2(z2 - z1, x2 - x1); p.position.set((x1 + x2) / 2, 0.04, (z1 + z2) / 2); worldGroup.add(p);
  }
  addPath(0, 6.2, STATIONS.SOLAR.x, STATIONS.SOLAR.z, 0xfacc15);
  addPath(0, 6.2, STATIONS.O2GEN.x, STATIONS.O2GEN.z, 0x38bdf8);
  addPath(0, 6.2, STATIONS.SCIENCE.x, STATIONS.SCIENCE.z, 0xd8b4fe);
  addPath(5.5, -1.5, STATIONS.FARM.x, STATIONS.FARM.z, 0x4ade80);

  const lander = new THREE.Group(); lander.position.set(0, 0, -34);
  lander.add(new THREE.Mesh(new THREE.CylinderGeometry(5.5, 6.2, 0.35, 16), new THREE.MeshStandardMaterial({ color: 0x334155 })));
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 2.2, 7.5, 16), new THREE.MeshStandardMaterial({ color: 0xf8fafc, metalness: 0.4 })); fus.position.y = 5; lander.add(fus);
  const nose = new THREE.Mesh(new THREE.ConeGeometry(1.5, 2.8, 16), new THREE.MeshStandardMaterial({ color: pl.key === "MARS" ? 0xf97316 : 0x2563eb })); nose.position.y = 10.1; lander.add(nose);
  landerStrobe = new THREE.Mesh(new THREE.SphereGeometry(0.32, 10, 10), new THREE.MeshBasicMaterial({ color: 0xef4444 })); landerStrobe.position.y = 11.7; lander.add(landerStrobe);
  const lLbl = makeFloatingLabel(pl.key === "MARS" ? "🚀 ARES LANDER" : "🚀 ARTEMIS LANDER", "#facc15"); lLbl.position.set(0, 13.4, 0); lander.add(lLbl);
  worldGroup.add(lander);

  const dishTower = new THREE.Group(); dishTower.position.set(-34, 0, -4);
  const tp = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.55, 6.2, 10), new THREE.MeshStandardMaterial({ color: 0xcbd5e1 })); tp.position.y = 3.1; dishTower.add(tp);
  commsDishHead = new THREE.Mesh(new THREE.ConeGeometry(2.6, 1.3, 18, 1, true), new THREE.MeshStandardMaterial({ color: 0xf8fafc, side: THREE.DoubleSide })); commsDishHead.position.y = 6.6; commsDishHead.rotation.x = -0.9; dishTower.add(commsDishHead);
  worldGroup.add(dishTower);

  scoutDrone = new THREE.Group();
  scoutDrone.add(new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.65, 1.1), new THREE.MeshStandardMaterial({ color: 0xfacc15 })));
  droneRotor = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.08, 0.25), new THREE.MeshBasicMaterial({ color: 0x38bdf8 })); droneRotor.position.y = 0.55; scoutDrone.add(droneRotor);
  scoutDrone.position.set(16, 6.8, 0); worldGroup.add(scoutDrone);

  const habFloor = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.2, 0.22, 32), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.45 }));
  habFloor.position.set(0, 0.11, 0); habFloor.receiveShadow = true; worldGroup.add(habFloor);
  worldGroup.add(new THREE.Mesh(new THREE.SphereGeometry(6.0, 24, 16, 0, 6.28, 0, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false })));
  worldGroup.add(new THREE.Mesh(new THREE.SphereGeometry(6.06, 12, 8, 0, 6.28, 0, Math.PI * 0.5), new THREE.MeshBasicMaterial({ color: 0xe2e8f0, wireframe: true, transparent: true, opacity: 0.34, depthWrite: false })));
  const habLbl = makeFloatingLabel(pl.key === "MARS" ? "🏠 ARES HABITAT" : "🏠 ARTEMIS HABITAT", "#38bdf8"); habLbl.position.set(0, 7.5, 0); worldGroup.add(habLbl);

  const chair = new THREE.Group(); chair.position.set(-0.2, 0.22, -2.8);
  const cMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.4 }), cMetal = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 });
  const cBase = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.65, 0.12, 12), cMetal); cBase.position.y = 0.06;
  const cStem = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.65, 10), cMetal); cStem.position.y = 0.42;
  const cSeat = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.18, 1.05), cMat); cSeat.position.y = 0.78;
  const cBack = new THREE.Mesh(new THREE.BoxGeometry(1.15, 1.25, 0.18), cMat); cBack.position.set(0, 1.45, -0.45);
  [-0.58, 0.58].forEach(ax => { const ar = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.12, 0.9), cMetal); ar.position.set(ax, 1.12, 0); chair.add(ar); });
  chair.add(cBase, cStem, cSeat, cBack);
  worldGroup.add(chair);

  const airFrame = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.8, 1.4), new THREE.MeshStandardMaterial({ color: 0x334155 })); airFrame.position.set(0, 1.4, 6.0); worldGroup.add(airFrame);
  airlockGlowMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x16a34a, emissiveIntensity: 0.7 });
  airlockDoorMesh = new THREE.Mesh(new THREE.BoxGeometry(2.3, 2.3, 0.35), airlockGlowMat); airlockDoorMesh.position.set(0, 1.25, 6.0); worldGroup.add(airlockDoorMesh);

  const bDir = new THREE.Vector3().subVectors(earthGroup.position, new THREE.Vector3(0, 6.8, 0));
  radioBeamMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.6, bDir.length(), 10), new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85, depthWrite: false }));
  radioBeamMesh.position.copy(new THREE.Vector3(0, 6.8, 0)).add(bDir.clone().multiplyScalar(0.5));
  radioBeamMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), bDir.clone().normalize());
  radioBeamMesh.visible = false; worldGroup.add(radioBeamMesh);

  const tableTop = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.25, 1.4), new THREE.MeshStandardMaterial({ color: 0xb45309 })); tableTop.position.set(2.3, 1.0, -1.2); worldGroup.add(tableTop);
  pantryFoodGroup = new THREE.Group(); pantryFoodGroup.position.set(2.3, 1.25, -1.2); worldGroup.add(pantryFoodGroup); refreshPantryVisuals();
  const cDesk = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 1.1), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, emissive: 0x1d4ed8, emissiveIntensity: 0.45 })); cDesk.position.set(-2.4, 0.6, -1.4); worldGroup.add(cDesk);

  shieldDomeMesh = new THREE.Mesh(new THREE.SphereGeometry(8.0, 28, 18, 0, 6.28, 0, Math.PI * 0.52), new THREE.MeshBasicMaterial({ color: h.domeColor, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false }));
  shieldWireMesh = new THREE.Mesh(new THREE.IcosahedronGeometry(8.22, 2), new THREE.MeshBasicMaterial({ color: h.wireColor, wireframe: true, transparent: true, opacity: 0.44, depthWrite: false }));
  shieldRingMesh = new THREE.Mesh(new THREE.TorusGeometry(8.28, 0.14, 10, 48), new THREE.MeshBasicMaterial({ color: h.auraColor, transparent: true, opacity: 0.82, depthWrite: false }));
  shieldRingMesh.rotation.x = Math.PI / 2; shieldRingMesh.position.y = 0.45;
  shieldDomeMesh.visible = false; shieldWireMesh.visible = false; shieldRingMesh.visible = false;
  worldGroup.add(shieldDomeMesh, shieldWireMesh, shieldRingMesh);

  for (let i = 0; i < 4; i++) {
    const px = STATIONS.SOLAR.x - 3.3 + i * 2.2, pz = STATIONS.SOLAR.z - 1.2 + (i % 2) * 2.0;
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 1.8, 8), new THREE.MeshStandardMaterial({ color: 0x94a3b8 })); pole.position.set(px, 0.9, pz); worldGroup.add(pole);
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.12, 2.4), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, emissive: 0x1e3a8a, emissiveIntensity: 0.35, metalness: 0.6 })); panel.position.set(px, 1.9, pz); panel.rotation.x = 0.32; worldGroup.add(panel);
    const dust = new THREE.Mesh(new THREE.BoxGeometry(1.92, 0.14, 2.42), new THREE.MeshStandardMaterial({ color: 0xa16207, transparent: true, opacity: 0.9 })); dust.position.set(px, 1.95, pz); dust.rotation.x = 0.32; dust.visible = false; worldGroup.add(dust); solarDustMeshes.push(dust);
  }
  const sLbl = makeFloatingLabel("☀️ SOLAR ARRAY [1]", "#facc15"); sLbl.position.set(STATIONS.SOLAR.x, 4.7, STATIONS.SOLAR.z); worldGroup.add(sLbl);

  const iceMat = new THREE.MeshStandardMaterial({ color: 0x7dd3fc, emissive: 0x0284c7, emissiveIntensity: 0.65 });
  [[0, 0, 2.0], [1.5, -0.9, 1.3], [-1.4, 0.7, 1.5], [0.2, 1.5, 1.1]].forEach(([ox, oz, ht]) => { const c = new THREE.Mesh(new THREE.ConeGeometry(0.65, ht, 6), iceMat); c.position.set(STATIONS.O2GEN.x + ox, ht / 2 - 0.1, STATIONS.O2GEN.z + oz); worldGroup.add(c); });
  const iLbl = makeFloatingLabel(pl.o2Tag, "#38bdf8"); iLbl.position.set(STATIONS.O2GEN.x, 4.3, STATIONS.O2GEN.z); worldGroup.add(iLbl);

  const sciBase = new THREE.Mesh(new THREE.CylinderGeometry(1.9, 2.2, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x3b0764 })); sciBase.position.set(STATIONS.SCIENCE.x, 0.18, STATIONS.SCIENCE.z); worldGroup.add(sciBase);
  const dTow = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.34, 2.9, 8), new THREE.MeshStandardMaterial({ color: 0xe2e8f0 })); dTow.position.set(STATIONS.SCIENCE.x, 1.55, STATIONS.SCIENCE.z); worldGroup.add(dTow);
  drillCrystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.74, 0), new THREE.MeshStandardMaterial({ color: 0xd8b4fe, emissive: 0xa855f7, emissiveIntensity: 0.85 })); drillCrystal.position.set(STATIONS.SCIENCE.x, 3.45, STATIONS.SCIENCE.z); worldGroup.add(drillCrystal);
  const sciLbl = makeFloatingLabel("🔬 EVA SCIENCE [3]", "#d8b4fe"); sciLbl.position.set(STATIONS.SCIENCE.x, 5.1, STATIONS.SCIENCE.z); worldGroup.add(sciLbl);

  const ghDome = new THREE.Mesh(new THREE.SphereGeometry(4.8, 20, 14, 0, 6.28, 0, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: 0x4ade80, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false })); ghDome.position.set(STATIONS.FARM.x, 0, STATIONS.FARM.z); worldGroup.add(ghDome);
  const ghWire = new THREE.Mesh(new THREE.SphereGeometry(4.86, 10, 8, 0, 6.28, 0, Math.PI * 0.5), new THREE.MeshBasicMaterial({ color: 0x86efac, wireframe: true, transparent: true, opacity: 0.36, depthWrite: false })); ghWire.position.set(STATIONS.FARM.x, 0, STATIONS.FARM.z); worldGroup.add(ghWire);
  const gLbl = makeFloatingLabel("🌱 CSA FARM [4]", "#4ade80"); gLbl.position.set(STATIONS.FARM.x, 5.7, STATIONS.FARM.z); worldGroup.add(gLbl);

  const cropCols = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  [[-1.3, -1.1], [1.3, -1.1], [-1.3, 1.1], [1.3, 1.1]].forEach(([ox, oz], idx) => {
    const bed = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.35, 1.4), new THREE.MeshStandardMaterial({ color: 0x451a03 })); bed.position.set(STATIONS.FARM.x + ox, 0.18, STATIONS.FARM.z + oz); worldGroup.add(bed);
    const plant = new THREE.Group(); plant.position.set(STATIONS.FARM.x + ox, 0.4, STATIONS.FARM.z + oz);
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, 0.8, 6), new THREE.MeshStandardMaterial({ color: 0x16a34a })); stem.position.y = 0.4;
    const fruit = new THREE.Mesh(new THREE.SphereGeometry(0.36, 12, 12), new THREE.MeshStandardMaterial({ color: cropCols[idx], emissive: cropCols[idx], emissiveIntensity: 0.35 })); fruit.position.y = 0.9;
    plant.add(stem, fruit); worldGroup.add(plant); cropMeshes.push(plant);
  });

  Object.entries(STATIONS).forEach(([k, st]) => {
    const ring = new THREE.Mesh(new THREE.RingGeometry(st.r * 0.65, st.r * 0.85, 32), new THREE.MeshBasicMaterial({ color: st.color, side: THREE.DoubleSide, transparent: true, opacity: 0.8, depthWrite: false }));
    ring.rotation.x = -Math.PI / 2; ring.position.set(st.x, 0.08, st.z); worldGroup.add(ring); padRings[k] = ring;
  });

  playerRover = new THREE.Group();
  const rvChassis = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.68, 3.8), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.45, roughness: 0.3 }));
  rvChassis.position.y = 0.82; rvChassis.castShadow = true; playerRover.add(rvChassis);
  const rvNose = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.48, 0.9), new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.6 }));
  rvNose.position.set(0, 0.9, 1.95); playerRover.add(rvNose);
  const rvSeat = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.9, 0.25), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
  rvSeat.position.set(0, 1.45, -0.55); playerRover.add(rvSeat);
  const rvRoll = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.08, 8, 20, Math.PI), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.8 }));
  rvRoll.position.set(0, 1.15, -0.65); playerRover.add(rvRoll);
  const rvDash = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.5, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
  rvDash.position.set(0, 1.32, 0.95); playerRover.add(rvDash);
  const steerWheel = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.05, 8, 16), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
  steerWheel.position.set(0, 1.55, 0.72); steerWheel.rotation.x = 0.5; playerRover.add(steerWheel);
  [-0.75, 0.75].forEach(lx => {
    const hl = new THREE.Mesh(new THREE.SphereGeometry(0.18, 10, 10), new THREE.MeshBasicMaterial({ color: 0xe0f2fe }));
    hl.position.set(lx, 0.95, 2.42); playerRover.add(hl);
    const tl = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.16, 0.1), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
    tl.position.set(lx, 0.92, -1.92); playerRover.add(tl);
  });
  const wMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.85 }), hubMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.8 });
  [[-1.32, 1.35, true], [1.32, 1.35, true], [-1.32, 0.0, false], [1.32, 0.0, false], [-1.32, -1.35, false], [1.32, -1.35, false]].forEach(([wx, wz, isFront]) => {
    const piv = new THREE.Group(); piv.position.set(wx, 0.52, wz);
    const wheel = new THREE.Group();
    const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.42, 16), wMat); tire.rotation.z = Math.PI / 2;
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.46, 10), hubMat); hub.rotation.z = Math.PI / 2;
    wheel.add(tire, hub); piv.add(wheel); playerRover.add(piv);
    roverWheels.push(wheel); if (isFront) roverFrontPivots.push(piv);
  });
  const rvLbl = makeFloatingLabel("🚙 EXPLORER ROVER [B]", "#facc15"); rvLbl.position.set(0, 3.2, 0); playerRover.add(rvLbl);
  roverPos.set(0, 0, 11.5); roverRotY = Math.PI / 2;
  playerRover.position.copy(roverPos); playerRover.rotation.y = roverRotY;
  worldGroup.add(playerRover);

  [[-11, 14], [10, 14], [-28, -2], [30, 10], [-8, -22], [14, -20], [-34, 20], [34, -20], [-40, -10], [42, 4], [0, 32], [0, -24], [-22, 34], [24, 34], [-30, -34], [30, -34], [-46, 10], [46, -10], [0, 46], [-48, -28]].forEach(([cx, cz]) => {
    const coin = new THREE.Mesh(new THREE.CylinderGeometry(0.66, 0.66, 0.18, 16), new THREE.MeshStandardMaterial({ color: 0xfacc15, emissive: 0xca8a04, emissiveIntensity: 0.78, metalness: 0.72 }));
    coin.rotation.x = Math.PI / 2; coin.position.set(cx, 1.2, cz); coin.userData = { active: true, respawn: 0 };
    worldGroup.add(coin); coinOrbs.push(coin);
  });

  const fpGeo = new THREE.BufferGeometry(), fpPos = new Float32Array(380 * 3);
  for (let i = 0; i < 380; i++) { fpPos[i*3] = (Math.random() - 0.5) * 120; fpPos[i*3+1] = Math.random() * 38; fpPos[i*3+2] = (Math.random() - 0.5) * 120; }
  fpGeo.setAttribute("position", new THREE.BufferAttribute(fpPos, 3));
  flareParticles = new THREE.Points(fpGeo, new THREE.PointsMaterial({ color: 0xff4500, size: 0.58, transparent: true, opacity: 0.92 }));
  flareParticles.visible = false; worldGroup.add(flareParticles);
}

function adjustZoom(delta) { state.fullPlanetMode = false; state.camZoom = Math.max(0.65, Math.min(5.0, state.camZoom + delta)); playSfx(520, 0.06, "sine", 0.04); }
function toggleFullPlanetView() {
  state.fullPlanetMode = !state.fullPlanetMode; state.camZoom = state.fullPlanetMode ? 4.8 : 1.0;
  playSfx(state.fullPlanetMode ? 440 : 660, 0.12, "triangle", 0.06);
  setStatus(state.fullPlanetMode ? `${getPlanet().icon} Whole ${getPlanet().name} View! Press C or ➕ to zoom back.` : "🎥 Returned to Avenger camera.");
}
function setupCanvasZoomGestures() {
  const cont = document.getElementById("canvas-container");
  cont.addEventListener("wheel", e => { if (session.screen === "GAME") { e.preventDefault(); adjustZoom(e.deltaY > 0 ? 0.28 : -0.28); } }, { passive: false });
  let pd = null;
  cont.addEventListener("touchstart", e => { if (e.touches.length === 2) pd = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY); }, { passive: true });
  cont.addEventListener("touchmove", e => { if (e.touches.length === 2 && pd) { const d = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY); state.fullPlanetMode = false; state.camZoom = Math.max(0.65, Math.min(5.0, state.camZoom + (pd - d) * 0.009)); pd = d; } }, { passive: true });
  cont.addEventListener("touchend", () => { pd = null; }, { passive: true });
}
function resize3D() { if (!threeReady) return; const c = document.getElementById("canvas-container"), w = c.clientWidth || window.innerWidth, h = c.clientHeight || window.innerHeight; camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); }
window.addEventListener("resize", () => { initBgStars(); resize3D(); });

function refreshBasketVisuals() {
  if (!heroBasketGroup) return;
  while (heroBasketGroup.children.length) heroBasketGroup.remove(heroBasketGroup.children[0]);
  if (!state.basket || state.basket.length === 0) return;
  heroBasketGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.45, 0.5), new THREE.MeshStandardMaterial({ color: 0x92400e })));
  const cm = { "🍅": 0xef4444, "🥬": 0x22c55e, "🥕": 0xf97316, "🥔": 0xeab308 };
  state.basket.forEach((ic, i) => { const v = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), new THREE.MeshStandardMaterial({ color: cm[ic] || 0x4ade80 })); v.position.set((i % 2 - 0.5) * 0.3, 0.3 + Math.floor(i / 2) * 0.28, 0); heroBasketGroup.add(v); });
}
function refreshPantryVisuals() {
  if (!pantryFoodGroup) return;
  while (pantryFoodGroup.children.length) pantryFoodGroup.remove(pantryFoodGroup.children[0]);
  const cols = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  for (let i = 0; i < Math.min(6, state.pantryCount || 0); i++) { const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 10), new THREE.MeshStandardMaterial({ color: cols[i % 4] })); f.position.set(-0.75 + (i % 3) * 0.75, 0.1, i >= 3 ? 0.35 : -0.35); pantryFoodGroup.add(f); }
}
function spawnFxPuff(x, y, z, col=0xcbd5e1, sz=0.4) {
  if (!threeReady) return;
  const p = new THREE.Mesh(new THREE.SphereGeometry(sz, 8, 8), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.72, depthWrite: false }));
  p.position.set(x, y, z); p.userData = { life: 0.42 }; worldGroup.add(p); fxParticles.push(p);
}

function launchGameScreen() {
  ensureAudio(); startHeroicSoundtrack(); session.screen = "GAME"; showScreen("screen-game");
  ["game-sidebar"].forEach(id => document.getElementById(id).classList.remove("open"));
  ["pause-modal", "debrief-modal", "dilemma-modal", "math-modal", "nasa-modal", "flare-alarm"].forEach(id => document.getElementById(id).style.display = "none");

  resetMissionState();
  const h = getHero(), pl = getPlanet();
  document.getElementById("sb-world").innerText = `${pl.icon} ${pl.name} (${pl.site})`;
  document.getElementById("sb-hero").innerText = h.name;
  document.getElementById("sb-mode").innerText = session.ageTier;
  document.getElementById("radar-title").innerText = `📡 ${pl.site.toUpperCase()}`;
  document.getElementById("btn-whole-planet").innerHTML = `${pl.icon} <span class="kbadge">C</span>`;
  document.getElementById("btn-station-o2").innerHTML = `${pl.o2Short}<span class="kbadge">2</span>`;
  document.getElementById("btn-jump-dock").innerHTML = (pl.key === "MARS" ? "⬆️ 3/8G" : "⬆️ 1/6G") + '<span class="kbadge">SPC</span>';
  document.getElementById("comms-dist-lbl").innerText = pl.commsLabel;
  document.getElementById("nasa-feed-btn").innerText = NASA.flr.live ? `🟢 LIVE DONKI ${NASA.flr.class}` : `🟡 ARCHIVED DONKI ${NASA.flr.class}`;
  STATIONS.O2GEN.label = pl.o2Work; STATIONS.O2GEN.tag = pl.o2Tag;
  syncMusicButtons(); syncJoystickVisibility(); syncVaultDisplays(); updateDriveButtons();

  function boot3D() {
    if (typeof THREE !== "undefined") {
      init3DEngineOnce(); resize3D();
      heroPos.set(0, 0, 1.5); wasInside = true;
      buildWorld3D(); buildHero3D(); updateHUD(); drawMinimap();
      playSfx(440, 0.25, "triangle", 0.09, 880);
      setStatus(`🚀 ${pl.icon} Touchdown at ${pl.site}! Press B to drive Rover, P to Pause, T/Y/U for Coffee, Dance & Chair!`);
      document.getElementById("game-root").focus();
    } else setTimeout(boot3D, 120);
  }
  boot3D();
}

function togglePause() {
  if (session.screen !== "GAME" || state.ended) return;
  state.userPaused = !state.userPaused;
  document.getElementById("pause-modal").style.display = state.userPaused ? "flex" : "none";
  document.getElementById("btn-pause-hud").innerHTML = state.userPaused ? "<span>▶️</span><span>PLAY</span>" : "<span>⏸️</span><span>PAUSE</span>";
  playSfx(state.userPaused ? 330 : 523, 0.14, "triangle", 0.07);
  if (!state.userPaused) document.getElementById("game-root").focus();
}
function pauseToHero() { state.userPaused = false; goToAgePage(); }
function toggleSidebar() { document.getElementById("game-sidebar").classList.toggle("open"); syncVaultDisplays(); }
function sidebarChangeAgeHero() { goToAgePage(); }
function sidebarChangePlanet() { goToCreatePage(); }
function sidebarGoInstructions() { state.paused = true; document.getElementById("game-sidebar").classList.remove("open"); goToInstructions(); }
function restartCurrentRun() { launchGameScreen(); }
function debriefChangeHero() { document.getElementById("debrief-modal").style.display = "none"; goToAgePage(); }
function quitAndResetGame() {
  state.paused = true; state.ended = true;
  session.age = null; session.heroKey = "CAP"; session.vaultCoins = 40; session.unlocked = ["CAP", "WIDOW"]; session.wins = 0; notifiedAffordable = {};
  document.getElementById("age-input").value = ""; document.getElementById("game-sidebar").classList.remove("open");
  startFiveSecondLoader();
}

function updateDriveButtons() {
  document.getElementById("btn-drive-dock").innerHTML = (state.driving ? "🚶 Exit" : "🚙 Drive") + '<span class="kbadge">B</span>';
  document.getElementById("mq-drive").innerHTML = state.driving ? "🚶<br>EXIT" : "🚙<br>DRIVE";
}

function toggleDriveRover() {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  state.emote = null; if (heroCoffeeMug) heroCoffeeMug.visible = false;
  if (!state.driving) {
    state.driving = true; state.autoTarget = null; state.roverSpeed = 0; state.roverSteer = 0;
    if (isInsideHabitat() && state.doorSealed) state.doorSealed = false;
    heroPos.copy(roverPos);
    playSfx(180, 0.26, "sawtooth", 0.08, 420);
    showComic("🚙💨", "ROVER ENGINE ON!", "Drive with W/S (Throttle/Brake) & A/D (Steer)! Press B to exit.", 2200);
    setStatus("🚙 Driving 6-Wheel Explorer Rover! Collect coins & visit stations at high speed! Press B to exit.");
  } else {
    state.driving = false; state.roverSpeed = 0;
    heroPos.set(roverPos.x + Math.cos(roverRotY) * 2.8, 0, roverPos.z - Math.sin(roverRotY) * 2.8);
    playSfx(360, 0.16, "triangle", 0.07, 220);
    setStatus("🚶 Exited Explorer Rover! On foot.");
  }
  updateDriveButtons(); updateHUD();
  document.getElementById("game-root").focus();
}

function triggerEmote(type) {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  if (state.driving) toggleDriveRover();
  state.autoTarget = null;
  if (type === "SIT" && state.emote === "SIT") {
    state.emote = null; setStatus("🚶 Stood up from Commander Chair!"); return;
  }
  state.emote = type;
  if (type === "COFFEE") {
    state.emoteTimer = 3.8;
    if (heroCoffeeMug) heroCoffeeMug.visible = true;
    state.hp = Math.min(100, state.hp + 3);
    playSfx(520, 0.18, "sine", 0.07, 720);
    showComic("☕🚀", "SPACE COFFEE BREAK!", `${getHero().name} sips zero-G espresso (+3% Crew Morale HP)!`, 2000);
    setStatus("☕ Drinking hot space coffee! Morale boosted (+3% HP).");
  } else if (type === "DANCE") {
    state.emoteTimer = 5.5;
    if (heroCoffeeMug) heroCoffeeMug.visible = false;
    playSfx(587, 0.15, "triangle", 0.08, 880);
    setStatus(`💃 ${getHero().name} is grooving in low gravity! Move anytime to stop.`);
  } else if (type === "SIT") {
    state.emoteTimer = 9999;
    if (heroCoffeeMug) heroCoffeeMug.visible = false;
    heroPos.set(-0.2, 0, -2.55); heroRotY = 0;
    playSfx(420, 0.14, "sine", 0.07, 520);
    showComic("🪑😌", "COMMANDER CHAIR", "Relaxing inside the Habitat! Move or press U to stand up.", 2000);
    setStatus("🪑 Sitting in the Habitat Commander Chair! Press U or move to stand up.");
  }
  updateHUD();
}

function openGlossary(k) { const g = GLOSSARY[k] || GLOSSARY.SOL; document.getElementById("gl-title").innerText = g.title; document.getElementById("gl-body").innerText = g.body; document.getElementById("glossary-pop").style.display = "block"; playSfx(620, 0.1, "sine", 0.06); }
function closeGlossary() { document.getElementById("glossary-pop").style.display = "none"; }
function openMathLab() { state.paused = true; document.getElementById("game-sidebar").classList.remove("open"); document.getElementById("math-title").innerText = `📈 ${getPlanet().name} Trade-Off Lab`; document.getElementById("math-modal").style.display = "flex"; updateMathLab(); }
function openNasaModal() {
  state.paused = true; const pl = getPlanet(); document.getElementById("game-sidebar").classList.remove("open");
  document.getElementById("nasa-data-body").innerHTML = `
    <p><b>${pl.icon} Site:</b> ${pl.name} (${pl.site}) | Sunlight: <code>${pl.solarIrradiance}</code> | Radiation: <code>${pl.radBaseline} mSv/Sol</code></p>
    <p style="margin-top:7px;"><b>☀️ NASA DONKI FLR:</b> <code>${NASA.flr.id}</code> (Class <code>${NASA.flr.class}</code>) — <b>${NASA.flr.source}</b></p>
    <p style="margin-top:7px;"><b>🌊 NASA DONKI CME:</b> <code>${NASA.cme.id}</code> (Speed <code>${NASA.cme.speed} km/s</code>) — <b>${NASA.cme.source}</b></p>
    <p style="margin-top:7px;"><b>☢️ NASA RadLab BLEO, Curiosity RAD &amp; OSDR (OSD-137, OSD-767, OSD-895):</b> Calibrates lunar (0.42 mSv/Sol) &amp; Martian (0.67 mSv/Sol) radiation and hydroponic crop biology.</p>
    <p style="margin-top:7px;"><b>🤝 Partners:</b> CSA Deep Space Food Toolkit, ISRO Chandrayaan-3 South Pole water-ice research, NASA Perseverance MOXIE, ESA lunar comms.</p>`;
  document.getElementById("nasa-modal").style.display = "flex";
}
function closeModal(id) { document.getElementById(id).style.display = "none"; if (!state.ended && document.getElementById("dilemma-modal").style.display !== "flex") state.paused = false; document.getElementById("game-root").focus(); }

function updateMathLab() {
  const pl = getPlanet(), sh = +document.getElementById("sl-sh").value, fm = +document.getElementById("sl-fm").value, ev = +document.getElementById("sl-ev").value, ds = +document.getElementById("sl-ds").value;
  document.getElementById("sl-sh-v").innerText = sh + "%"; document.getElementById("sl-fm-v").innerText = fm + "%"; document.getElementById("sl-ev-v").innerText = ev + " hrs"; document.getElementById("sl-ds-v").innerText = ds + "%";
  const pts = []; let p = 96, o = 96, r = pl.radBaseline;
  for (let s = 1; s <= 7; s++) {
    p = Math.max(0, Math.min(100, p + 34 * pl.solarChargeMult * (1 - ds / 100) - (sh * 0.28 + fm * 0.13 + ev * 1.3 + 3.5)));
    o = Math.max(0, Math.min(100, o + fm * 0.14 - (7.2 + ev * 2.1)));
    r += pl.radBaseline + ev * 0.08 + ((s === 3 || s === 6) ? 1.8 * pl.flareDmgMult * (1 - sh / 100) : 0);
    pts.push({ p, o, r });
  }
  const c = document.getElementById("math-chart"), ctx = c.getContext("2d"); ctx.clearRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1; for (let y = 24; y <= 144; y += 30) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif"; ctx.fillText("100%", 6, 27); ctx.fillText("50%", 12, 87); ctx.fillText("0%", 18, 147);
  function plot(k, col) { ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath(); pts.forEach((pt, i) => { const x = 45 + (i / 6) * 525, y = 144 - (pt[k] / 100) * 120; if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke(); }
  plot("p", "#facc15"); plot("o", "#38bdf8");
  document.getElementById("math-summary").innerText = `${pl.name} Sol 7 Projection: Power ${Math.round(pts[6].p)}% | O₂ ${Math.round(pts[6].o)}% | Radiation ${pts[6].r.toFixed(2)} mSv`;
}

function getDilemma(sol) {
  const pl = getPlanet();
  if (sol === 2) return { title: `🔬 ${pl.site} Discovery: O₂ vs. Science!`, desc: `Orbital scans spotted ancient mineral ice deposits deeper in ${pl.site}. Heavy EVA drilling costs extra Oxygen.`, choices: [
    { label: "A) Run Deep EVA Core Drill", tradeoff: "-12% O₂ & +0.20 mSv | +300 Science & +90 🪙", apply: () => { state.oxygen = Math.max(8, state.oxygen - 12); state.rad += 0.2; state.science += 300; addVaultCoins(90); setStatus("🔬 Deep EVA succeeded! +90 Vault Coins!"); } },
    { label: "B) Send Scout Drone Instead", tradeoff: "-9% Power | +130 Science & +45 🪙", apply: () => { state.power = Math.max(8, state.power - 9); state.science += 130; addVaultCoins(45); setStatus("🚁 Drone saved O₂! +45 Vault Coins!"); } }
  ]};
  if (sol === 4) return { title: `🌊 NASA DONKI CME (${NASA.cme.speed} km/s): Shield vs. Farm!`, desc: `Coronal Mass Ejection ${NASA.cme.id} incoming! Peak power cannot max both shielding and CSA Greenhouse lights.`, choices: [
    { label: "A) Reinforce Outpost Shielding", tradeoff: "-14% Power & -8% Food | Blocks CME & +80 🪙", apply: () => { state.power = Math.max(8, state.power - 14); state.food = Math.max(10, state.food - 8); state.science += 120; addVaultCoins(80); setStatus("🛡️ CME deflected! +80 Vault Coins!"); } },
    { label: "B) Prioritize Greenhouse Grow-Lights", tradeoff: "+0.75 mSv & -10% HP | +22% Food, +15% O₂ & +60 🪙", apply: () => { state.rad += 0.75; state.hp = Math.max(12, state.hp - 10); state.food = Math.min(100, state.food + 22); state.oxygen = Math.min(100, state.oxygen + 15); addVaultCoins(60); setStatus("🌱 Greenhouse thrived (+22% Food)!"); } }
  ]};
  if (sol === 6) return { title: "📡 Solar Bus Damaged — Earth Comms Delay!", desc: `Waiting for Earth HQ diagnostics across ${pl.commsLabel} drains power.`, choices: [
    { label: "A) Manual EVA Patch Outside", tradeoff: "-10% O₂ & +0.16 mSv | +18% Power & +90 🪙", apply: () => { state.oxygen = Math.max(8, state.oxygen - 10); state.rad += 0.16; state.power = Math.min(100, state.power + 18); state.science += 180; addVaultCoins(90); setStatus("🛠️ EVA patch restored +18% Power & +90 Vault Coins!"); } },
    { label: "B) Wait for Earth HQ Software Reroute", tradeoff: "-12% Power | Zero Crew Risk & +65 🪙", apply: () => { state.power = Math.max(8, state.power - 12); addVaultCoins(65); setStatus("📡 Earth HQ rerouted power safely! +65 Vault Coins!"); } }
  ]};
  return null;
}

function triggerDilemma(sol) {
  const d = getDilemma(sol); if (!d) return;
  state.paused = true; playSfx(392, 0.25, "triangle", 0.09, 523);
  document.getElementById("dil-sol").innerText = `${getPlanet().name.toUpperCase()} SOL ${sol}`;
  document.getElementById("dil-title").innerText = d.title; document.getElementById("dil-desc").innerText = d.desc;
  const w = document.getElementById("dil-choices"); w.innerHTML = "";
  d.choices.forEach(ch => {
    const b = document.createElement("button"); b.className = "choice-btn";
    b.innerHTML = `<div style="font-size:13px;font-weight:900;color:#fde047;">${ch.label}</div><div style="font-size:11px;color:#93c5fd;margin-top:3px;">${ch.tradeoff}</div>`;
    b.onclick = () => { ch.apply(); state.paused = false; document.getElementById("dilemma-modal").style.display = "none"; playSfx(660, 0.18, "sine", 0.08, 880); updateHUD(); document.getElementById("game-root").focus(); };
    w.appendChild(b);
  });
  document.getElementById("dilemma-modal").style.display = "flex";
}

function showComic(badge, title, body, ms=2200) {
  const el = document.getElementById("comic-toast");
  document.getElementById("comic-badge").innerText = badge; document.getElementById("comic-title").innerText = title; document.getElementById("comic-body").innerText = body;
  el.style.display = "block"; clearTimeout(el._t); el._t = setTimeout(() => { el.style.display = "none"; }, ms);
}
function setStatus(m) { document.getElementById("status-msg").innerText = m; }
function isInsideHabitat() { return heroPos ? Math.hypot(heroPos.x, heroPos.z) < 5.9 : true; }

function autoRunTo(k) {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  if (state.driving && (k === "PANTRY" || k === "SHIELD")) toggleDriveRover();
  state.emote = null; if (heroCoffeeMug) heroCoffeeMug.visible = false;
  const st = STATIONS[k]; if (!st) return;
  state.autoTarget = new THREE.Vector3(st.x, 0, st.z); playSfx(480, 0.1, "triangle", 0.06);
  setStatus(`🏃 Heading to ${st.tag}...`); document.getElementById("game-root").focus();
}

function triggerJump() {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused || state.driving) return;
  state.emote = null; if (heroCoffeeMug) heroCoffeeMug.visible = false;
  if (heroPos && heroPos.y <= 0.02) {
    const pl = getPlanet();
    heroVelY = (session.heroKey === "IRON") ? pl.jumpVel * 1.28 : pl.jumpVel;
    playSfx(260, 0.22, "sine", 0.08, 540); spawnFxPuff(heroPos.x, 0.3, heroPos.z, 0x38bdf8, 0.45);
  }
}

function toggleDoor() {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  if (!isInsideHabitat() && !state.doorSealed) { setStatus("⚠️ Get inside the Habitat Dome first before sealing Airlock!"); playSfx(200, 0.15, "sawtooth", 0.06); return; }
  state.doorSealed = !state.doorSealed; playSfx(state.doorSealed ? 660 : 320, 0.16, "square", 0.07);
  setStatus(state.doorSealed ? "🔒 Airlock SEALED! Oxygen safe." : "🔓 Airlock OPEN — press E to seal when inside."); updateHUD();
}

function toggleShield() {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  const now = performance.now(); if (now - lastShieldToggleMs < 280) return; lastShieldToggleMs = now;
  if (!state.shieldOn && state.power < 6) { setStatus("⚠️ Battery too low for Shield! Press 1 for Solar or F for Earth drop."); playSfx(180, 0.2, "sawtooth", 0.08); return; }
  const h = getHero(); state.shieldOn = !state.shieldOn; if (heroShieldFX) heroShieldFX.visible = state.shieldOn;
  if (state.shieldOn) {
    const cost = (session.heroKey === "CAP") ? 3 : 6; state.power = Math.max(0, state.power - cost);
    playSfx(320, 0.28, "sawtooth", 0.075, 760); showComic("🛡️⚡", `${h.shieldName.toUpperCase()} ON!`, "Press Q to turn OFF after flare passes.");
    setStatus(`🛡️ ${h.shieldName} ON (-${cost}% startup Power)!`);
  } else { playSfx(540, 0.18, "sine", 0.07, 260); setStatus(`🟢 ${h.shieldName} OFF — batteries recharging.`); }
  updateHUD();
}

function deployRoverScan() {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused) return;
  if (state.roverCooldown > 0) { setStatus(`📡 Scanner recharging (${Math.ceil(state.roverCooldown)}s)...`); return; }
  if (state.power < 4) { setStatus("⚠️ Need 4% Power to scan!"); return; }
  state.power = Math.max(0, state.power - 4);
  const g = (session.heroKey === "LOKI") ? 90 : 45; addVaultCoins(g); state.science += 55; state.roverCooldown = 9;
  playSfx(740, 0.22, "triangle", 0.08, 980); showComic("📡🪙", "MINERAL SCAN!", `+${g} Vault Coins & +55 Science (-4% Power)!`, 1900);
}

function callEarth(preset) {
  if (session.screen !== "GAME" || state.ended || state.paused || state.userPaused || state.radioBusy) return;
  const pl = getPlanet(), cost = (session.heroKey === "STRANGE") ? 10 : 15, delayMs = (session.heroKey === "STRANGE") ? Math.round(pl.commsDelayMs * 0.42) : pl.commsDelayMs;
  if (session.vaultCoins < cost) { document.getElementById("radio-log").innerText = `⚠️ Need ${cost} 🪙! Drive Rover to collect Coins!`; playSfx(210, 0.15, "sawtooth", 0.06); return; }
  session.vaultCoins -= cost; syncVaultDisplays(); state.radioBusy = true; state.radioBeamTimer = delayMs / 1000;
  playSfx(440, 0.15, "sine", 0.08, 880);
  document.getElementById("radio-log").innerText = `📡 Signal beamed (${(delayMs / 1000).toFixed(1)}s light delay)...`;
  setTimeout(() => {
    state.radioBusy = false; if (state.ended) return; playSfx(880, 0.25, "triangle", 0.09, 1180);
    if (preset === 1) { state.power = Math.min(100, state.power + 32); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Battery Pod landed (+32% ⚡)!"; }
    else if (preset === 2) { state.oxygen = Math.min(100, state.oxygen + 32); document.getElementById("radio-log").innerText = "🌍 Earth HQ: O₂ Tank landed (+32% 🫁)!"; }
    else if (preset === 3) { state.food = Math.min(100, state.food + 32); state.pantryCount = Math.min(6, state.pantryCount + 2); refreshPantryVisuals(); document.getElementById("radio-log").innerText = "🌍 Earth HQ: CSA Rations (+32% 🍽️)!"; }
    else if (preset === 4) { state.hp = Math.min(100, state.hp + 32); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Nano-Medkit (+32% ❤️)!"; }
    else { state.flarePhase = "CALM"; document.getElementById("flare-alarm").style.display = "none"; document.getElementById("radio-log").innerText = "🌍 DONKI Forecast: Solar storm cleared!"; }
    updateHUD();
  }, delayMs);
}

function advanceSolEarly() { if (session.screen === "GAME" && !state.ended && !state.paused && !state.userPaused) { state.solClock = SOL_SECONDS - 0.08; playSfx(523, 0.2, "triangle", 0.08); } }

function completePadAction(k) {
  const mult = (session.heroKey === "LOKI") ? 2 : 1, pl = getPlanet();
  if (k === "SOLAR") { state.dusty = false; state.power = Math.min(100, state.power + (pl.key === "MARS" ? 22 : 28)); const g = 35 * mult; addVaultCoins(g); playSfx(784, 0.2, "triangle", 0.09, 1046); showComic("🧹☀️", "SOLAR CLEAN!", `+Power & +${g} 🪙 Vault Coins!`, 1800); }
  else if (k === "O2GEN") { if (state.power < 7) { setStatus("⚠️ Need 7% Power!"); return; } state.power -= 7; state.oxygen = Math.min(100, state.oxygen + 30); const g = 30 * mult; addVaultCoins(g); playSfx(620, 0.22, "sine", 0.08, 920); showComic("🫁✨", pl.key === "MARS" ? "MOXIE CO₂→O₂!" : "ICE → O₂!", `+30% O₂ & +${g} 🪙 (-7% ⚡)!`, 1800); }
  else if (k === "SCIENCE") { if (state.oxygen < 14 || state.power < 7) { setStatus("⚠️ Need ≥14% O₂ & ≥7% ⚡!"); return; } state.oxygen -= 10; state.power -= 5; state.rad += 0.14; const sc = session.heroKey === "LOKI" ? 300 : 200, g = 60 * mult; state.science += sc; addVaultCoins(g); playSfx(520, 0.25, "sawtooth", 0.07, 1040); spawnFxPuff(STATIONS.SCIENCE.x, 1.5, STATIONS.SCIENCE.z, 0xd8b4fe, 0.68); showComic("🔬🪐", "CORE DRILLED!", `+${sc} Sci & +${g} 🪙 (-10% O₂)!`, 2000); }
  else if (k === "FARM") {
    const ic = ["🍅", "🥬", "🥕", "🥔"]; let pk = 0;
    for (let i = 0; i < 4; i++) if (state.crops[i] >= 95 && state.basket.length < 4) { state.basket.push(ic[i]); state.crops[i] = 5; state.power = Math.max(0, state.power - 1.5); state.oxygen = Math.min(100, state.oxygen + (session.heroKey === "WANDA" ? 6 : 2.5)); pk++; }
    if (pk > 0) { refreshBasketVisuals(); playSfx(698, 0.18, "sine", 0.09, 987); showComic("🧺🍅", "CSA HARVEST!", `Picked ${pk} crops! Stock Pantry [5]!`, 1800); }
    else setStatus(state.basket.length >= 4 ? "🧺 Basket full (4/4)! Press 5 to Stock Pantry!" : "🌱 Crops still growing...");
  } else if (k === "PANTRY") {
    if (state.basket.length === 0) { setStatus("🧺 Basket empty! Press 4 to visit CSA Farm."); return; }
    const n = state.basket.length; state.basket = []; state.pantryCount = Math.min(6, state.pantryCount + n); state.food = Math.min(100, state.food + n * 15);
    const g = n * 25 * mult; addVaultCoins(g); state.science += n * 25; refreshBasketVisuals(); refreshPantryVisuals();
    playSfx(880, 0.25, "triangle", 0.09, 1320); showComic("🍽️✨", "PANTRY STOCKED!", `+${n * 15}% Food & +${g} 🪙!`, 1800);
  } else if (k === "SHIELD") { if (!state.shieldPadLatched) { state.shieldPadLatched = true; toggleShield(); } }
}

function drawMinimap() {
  const c = document.getElementById("minimap"), ctx = c.getContext("2d"); ctx.clearRect(0, 0, c.width, c.height);
  if (!heroPos) return;
  const mx = x => (x + WORLD_RADIUS + 4) / ((WORLD_RADIUS + 4) * 2) * c.width, mz = z => (z + WORLD_RADIUS + 4) / ((WORLD_RADIUS + 4) * 2) * c.height;
  ctx.strokeStyle = "rgba(148,163,184,0.38)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(c.width / 2, c.height / 2, c.height * 0.46, 0, 6.28); ctx.stroke();
  ctx.strokeStyle = "rgba(56,189,248,0.8)"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(mx(0), mz(0), 6.5, 0, 6.28); ctx.stroke();
  const sc = { SOLAR: "#facc15", O2GEN: "#38bdf8", SCIENCE: "#d8b4fe", FARM: "#4ade80", PANTRY: "#f472b6", SHIELD: "#60a5fa" };
  Object.entries(STATIONS).forEach(([k, st]) => { ctx.fillStyle = sc[k]; ctx.beginPath(); ctx.arc(mx(st.x), mz(st.z), 3.1, 0, 6.28); ctx.fill(); });
  ctx.fillStyle = "#fef08a"; coinOrbs.forEach(co => { if (co.userData.active) ctx.fillRect(mx(co.position.x) - 1, mz(co.position.z) - 1, 2.2, 2.2); });
  if (roverPos) { ctx.fillStyle = "#f97316"; ctx.fillRect(mx(roverPos.x) - 3, mz(roverPos.z) - 2, 6, 4); }
  ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(mx(heroPos.x), mz(heroPos.z), 3.8, 0, 6.28); ctx.fill(); ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 1.6; ctx.stroke();
}

function animate3D() {
  requestAnimationFrame(animate3D);
  if (session.screen !== "GAME" || !heroPos) return;
  try {
    const dt = Math.min(0.05, clock.getDelta()), t = clock.elapsedTime, diff = getDiff(), pl = getPlanet();

    earthGroup.rotation.y += dt * 0.08;
    drillCrystal.rotation.y += dt * 1.8; drillCrystal.position.y = 3.45 + Math.sin(t * 2.5) * 0.22;
    commsDishHead.rotation.y = Math.sin(t * 0.35) * 0.6;
    landerStrobe.material.color.setHex(Math.sin(t * 6) > 0 ? 0xef4444 : 0x450a0a);
    scoutDrone.position.set(Math.cos(t * 0.45) * 26, 6.8 + Math.sin(t * 2.6) * 0.65, Math.sin(t * 0.45) * 20);
    droneRotor.rotation.y += dt * 22;
    shootingStar.position.x += dt * 38; shootingStar.position.y -= dt * 7;
    if (shootingStar.position.x > 130) shootingStar.position.set(-100 - Math.random() * 45, 42 + Math.random() * 20, -85 - Math.random() * 35);

    Object.values(padRings).forEach((ring, i) => { const s = 1 + Math.sin(t * 3.5 + i) * 0.06; ring.scale.set(s, s, 1); });

    shieldDomeMesh.visible = state.shieldOn; shieldWireMesh.visible = state.shieldOn; shieldRingMesh.visible = state.shieldOn;
    if (heroShieldFX) heroShieldFX.visible = state.shieldOn;
    if (state.shieldOn) {
      shieldWireMesh.rotation.y += dt * 0.24;
      heroAuraRings.forEach((r, i) => { if (session.heroKey === "STRANGE") r.rotation.z += dt * (i % 2 ? -2.4 : 2.4); else r.rotation.y += dt * (i % 2 ? -2.4 : 3.2); });
      heroLightning.forEach((b, i) => { b.rotation.x += dt * (2.5 + i * 0.4); b.rotation.y += dt * (3.0 - i * 0.3); });
    }

    const dY = state.doorSealed ? 1.25 : 3.35;
    airlockDoorMesh.position.y += (dY - airlockDoorMesh.position.y) * Math.min(1, dt * 8);
    airlockGlowMat.color.setHex(state.doorSealed ? 0x22c55e : 0xef4444);
    airlockGlowMat.emissive.setHex(state.doorSealed ? 0x16a34a : 0xb91c1c);
    solarDustMeshes.forEach(m => { m.visible = state.dusty; });

    if (state.radioBeamTimer > 0) { state.radioBeamTimer -= dt; radioBeamMesh.visible = true; radioBeamMesh.material.opacity = 0.55 + Math.sin(t * 25) * 0.3; }
    else radioBeamMesh.visible = false;

    if (state.flarePhase === "WARN") {
      sunMesh.scale.setScalar(1.26 + Math.sin(t * 10) * 0.07); sunMesh.material.color.setHex(0xf97316);
      scene.fog.color.setHex(0x2d0a0a); beaconLight.color.setHex(0xef4444); beaconLight.intensity = 1.2 + Math.sin(t * 12) * 1.1; flareParticles.visible = false;
    } else if (state.flarePhase === "ACTIVE") {
      sunMesh.scale.setScalar(1.52); sunMesh.material.color.setHex(0xef4444);
      scene.fog.color.setHex(0x4a0b0b); beaconLight.color.setHex(0xef4444); beaconLight.intensity = 2.2 + Math.sin(t * 16) * 1.2; flareParticles.visible = true;
      const arr = flareParticles.geometry.attributes.position.array;
      for (let i = 1; i < arr.length; i += 3) { arr[i] -= dt * 22; if (arr[i] < 0) arr[i] = 38; }
      flareParticles.geometry.attributes.position.needsUpdate = true;
    } else {
      sunMesh.scale.setScalar(1.0); sunMesh.material.color.setHex(0xfde047);
      scene.fog.color.setHex(0x050b1f); beaconLight.color.setHex(0x38bdf8); beaconLight.intensity = 1.1; flareParticles.visible = false;
    }

    for (let i = fxParticles.length - 1; i >= 0; i--) {
      const p = fxParticles[i]; p.userData.life -= dt; p.position.y += dt * 0.9; p.scale.addScalar(dt * 1.4); p.material.opacity = Math.max(0, p.userData.life * 1.5);
      if (p.userData.life <= 0) { worldGroup.remove(p); fxParticles.splice(i, 1); }
    }

    if (state.started && !state.ended && !state.paused && !state.userPaused) {
      let inX = 0, inZ = 0;
      if (keys["KeyW"] || keys["ArrowUp"]) inZ -= 1;
      if (keys["KeyS"] || keys["ArrowDown"]) inZ += 1;
      if (keys["KeyA"] || keys["ArrowLeft"]) inX -= 1;
      if (keys["KeyD"] || keys["ArrowRight"]) inX += 1;
      if (Math.hypot(joyX, joyY) > 0.12) { inX += joyX; inZ += joyY; }

      if (Math.hypot(inX, inZ) > 0.1) {
        state.autoTarget = null;
        if (state.emote) { state.emote = null; if (heroCoffeeMug) heroCoffeeMug.visible = false; }
      }

      if (state.driving) {
        let throttle = -inZ, steerInput = -inX;
        if (state.autoTarget) {
          const dx = state.autoTarget.x - roverPos.x, dz = state.autoTarget.z - roverPos.z, dist = Math.hypot(dx, dz);
          if (dist < 2.2) { state.autoTarget = null; throttle = 0; }
          else {
            const desA = Math.atan2(dx, dz);
            const diffA = Math.atan2(Math.sin(desA - roverRotY), Math.cos(desA - roverRotY));
            steerInput = Math.max(-1, Math.min(1, diffA * 2.2));
            throttle = Math.abs(diffA) > 1.2 ? 0.35 : 0.95;
          }
        }
        const accel = 24, maxSpd = 24, revMax = -10;
        if (Math.abs(throttle) > 0.08) state.roverSpeed = Math.max(revMax, Math.min(maxSpd, state.roverSpeed + throttle * accel * dt));
        else state.roverSpeed *= Math.pow(0.08, dt);

        state.roverSteer += (steerInput * 0.55 - state.roverSteer) * Math.min(1, dt * 10);
        const turnFactor = Math.abs(state.roverSpeed) > 0.4 ? (state.roverSpeed >= 0 ? 1 : -1) * Math.min(1, Math.abs(state.roverSpeed) / 7) : 0.35;
        roverRotY += state.roverSteer * 3.0 * turnFactor * dt;

        let nx = roverPos.x + Math.sin(roverRotY) * state.roverSpeed * dt;
        let nz = roverPos.z + Math.cos(roverRotY) * state.roverSpeed * dt;
        const rHab = Math.hypot(nx, nz);
        if (rHab < 7.2) { nx = (nx / (rHab || 1)) * 7.2; nz = (nz / (rHab || 1)) * 7.2; state.roverSpeed *= 0.3; }
        const rLim = Math.hypot(nx, nz);
        if (rLim > WORLD_RADIUS) { nx = (nx / rLim) * WORLD_RADIUS; nz = (nz / rLim) * WORLD_RADIUS; state.roverSpeed *= 0.5; }
        roverPos.set(nx, 0, nz);

        playerRover.position.copy(roverPos);
        playerRover.position.y = Math.abs(Math.sin(t * 14)) * Math.min(0.08, Math.abs(state.roverSpeed) * 0.004);
        playerRover.rotation.y = roverRotY;
        playerRover.rotation.z = -state.roverSteer * Math.min(0.12, Math.abs(state.roverSpeed) * 0.006);
        roverFrontPivots.forEach(p => { p.rotation.y = state.roverSteer; });
        roverWheels.forEach(w => { w.rotation.x += state.roverSpeed * dt * 1.9; });

        heroPos.set(roverPos.x, 0.55, roverPos.z);
        heroRotY = roverRotY;
        heroGroup.position.copy(heroPos); heroGroup.rotation.y = heroRotY;
        heroBodyRig.rotation.x = 0; heroBodyRig.position.y = 0;
        heroLimbs.lLeg.rotation.x = -1.4; heroLimbs.rLeg.rotation.x = -1.4;
        heroLimbs.lLeg.userData.lower.rotation.x = 1.35; heroLimbs.rLeg.userData.lower.rotation.x = 1.35;
        heroLimbs.lArm.rotation.x = -1.05; heroLimbs.rArm.rotation.x = -1.05;
        heroLimbs.lArm.userData.lower.rotation.x = -0.3; heroLimbs.rArm.userData.lower.rotation.x = -0.3;

        if (Math.abs(state.roverSpeed) > 3 && Math.random() < 0.45) {
          spawnFxPuff(roverPos.x - Math.sin(roverRotY) * 1.8, 0.25, roverPos.z - Math.cos(roverRotY) * 1.8, 0x94a3b8, 0.34);
        }
      } else {
        let mx = inX, mz = inZ;
        if (Math.hypot(mx, mz) <= 0.08 && state.autoTarget) {
          const dx = state.autoTarget.x - heroPos.x, dz = state.autoTarget.z - heroPos.z, dist = Math.hypot(dx, dz);
          if (dist < 0.5) state.autoTarget = null; else { mx = dx / dist; mz = dz / dist; }
        }
        const runSpd = (session.heroKey === "WIDOW") ? 14.5 : 11.8, mag = Math.hypot(mx, mz);
        if (mag > 0.08) {
          const cm = Math.min(1, mag); mx = (mx / mag) * cm; mz = (mz / mag) * cm;
          heroPos.x += mx * runSpd * dt; heroPos.z += mz * runSpd * dt;
          const rDist = Math.hypot(heroPos.x, heroPos.z);
          if (rDist > WORLD_RADIUS) { heroPos.x = (heroPos.x / rDist) * WORLD_RADIUS; heroPos.z = (heroPos.z / rDist) * WORLD_RADIUS; }
          const desR = Math.atan2(mx, mz);
          heroRotY += Math.atan2(Math.sin(desR - heroRotY), Math.cos(desR - heroRotY)) * Math.min(1, dt * 13);

          runCycle += dt * 15.5; const sw = Math.sin(runCycle);
          heroBodyRig.rotation.x = 0.14; heroBodyRig.position.y = Math.abs(Math.cos(runCycle)) * 0.16;
          heroLimbs.lLeg.rotation.x = sw * 0.85; heroLimbs.rLeg.rotation.x = -sw * 0.85;
          heroLimbs.lLeg.userData.lower.rotation.x = Math.max(0, -sw) * 0.95; heroLimbs.rLeg.userData.lower.rotation.x = Math.max(0, sw) * 0.95;
          heroLimbs.lArm.rotation.x = (state.shieldOn && session.heroKey === "CAP") ? -1.15 : -sw * 0.72;
          heroLimbs.rArm.rotation.x = sw * 0.72;
          heroLimbs.lArm.userData.lower.rotation.x = -0.55; heroLimbs.rArm.userData.lower.rotation.x = -0.55;
          if (heroLimbs.cape) heroLimbs.cape.rotation.x = 0.42 + Math.sin(runCycle * 2) * 0.08;
          footstepTimer -= dt;
          if (footstepTimer <= 0 && heroPos.y <= 0.05) { footstepTimer = 0.24; spawnFxPuff(heroPos.x, 0.12, heroPos.z, 0x94a3b8, 0.22); }
        } else if (state.emote) {
          state.emoteTimer -= dt;
          if (state.emoteTimer <= 0) { state.emote = null; if (heroCoffeeMug) heroCoffeeMug.visible = false; }
          else if (state.emote === "COFFEE") {
            heroBodyRig.rotation.x = 0; heroBodyRig.position.y = Math.sin(t * 3) * 0.03;
            heroLimbs.rArm.rotation.x = -1.6 + Math.sin(t * 4) * 0.25; heroLimbs.rArm.userData.lower.rotation.x = -1.2;
            heroLimbs.lArm.rotation.x = 0; heroLimbs.lLeg.rotation.x = 0; heroLimbs.rLeg.rotation.x = 0;
            if (Math.random() < 0.25) spawnFxPuff(heroPos.x, 2.75, heroPos.z, 0xf8fafc, 0.14);
          } else if (state.emote === "DANCE") {
            heroRotY += dt * 2.8;
            heroBodyRig.position.y = Math.abs(Math.sin(t * 10)) * 0.28;
            heroLimbs.lArm.rotation.x = -2.4 + Math.sin(t * 12) * 0.6;
            heroLimbs.rArm.rotation.x = -2.4 - Math.sin(t * 12) * 0.6;
            heroLimbs.lLeg.rotation.x = Math.sin(t * 10) * 0.55;
            heroLimbs.rLeg.rotation.x = -Math.sin(t * 10) * 0.55;
          } else if (state.emote === "SIT") {
            heroPos.set(-0.2, 0.16, -2.55); heroRotY = 0;
            heroBodyRig.rotation.x = 0; heroBodyRig.position.y = 0;
            heroLimbs.lLeg.rotation.x = -1.52; heroLimbs.rLeg.rotation.x = -1.52;
            heroLimbs.lLeg.userData.lower.rotation.x = 1.48; heroLimbs.rLeg.userData.lower.rotation.x = 1.48;
            heroLimbs.lArm.rotation.x = -0.65; heroLimbs.rArm.rotation.x = -0.65;
            heroLimbs.lArm.userData.lower.rotation.x = -0.5; heroLimbs.rArm.userData.lower.rotation.x = -0.5;
          }
        } else {
          heroBodyRig.rotation.x *= 0.82; heroBodyRig.position.y = Math.sin(t * 2.8) * 0.035;
          heroLimbs.lLeg.rotation.x *= 0.82; heroLimbs.rLeg.rotation.x *= 0.82;
          heroLimbs.lLeg.userData.lower.rotation.x *= 0.82; heroLimbs.rLeg.userData.lower.rotation.x *= 0.82;
          heroLimbs.lArm.rotation.x += (((state.shieldOn && session.heroKey === "CAP") ? -1.2 : 0) - heroLimbs.lArm.rotation.x) * 0.18;
          heroLimbs.rArm.rotation.x *= 0.82; heroLimbs.lArm.userData.lower.rotation.x *= 0.82; heroLimbs.rArm.userData.lower.rotation.x *= 0.82;
          if (heroLimbs.cape) heroLimbs.cape.rotation.x = 0.18 + Math.sin(t * 3) * 0.04;
        }

        if (state.emote !== "SIT") {
          heroPos.y += heroVelY * dt;
          if (heroPos.y > 0) { heroVelY -= pl.gravity * dt; if (Math.random() < 0.45) spawnFxPuff(heroPos.x, heroPos.y + 0.3, heroPos.z, 0x38bdf8, 0.16); }
          else { heroPos.y = 0; heroVelY = 0; }
        }
        heroGroup.position.copy(heroPos); heroGroup.rotation.y = heroRotY;
      }

      const nowIn = isInsideHabitat();
      if (wasInside && !nowIn && state.doorSealed) { state.doorSealed = false; playSfx(310, 0.14, "square", 0.06); }
      wasInside = nowIn;

      const pickupR = state.driving ? 2.9 : 1.7;
      coinOrbs.forEach(c => {
        if (c.userData.active) {
          c.rotation.z += dt * 3; c.position.y = 1.15 + Math.sin(t * 3 + c.position.x) * 0.22;
          if (Math.hypot(heroPos.x - c.position.x, heroPos.z - c.position.z) < pickupR) {
            c.userData.active = false; c.visible = false; c.userData.respawn = 12;
            const g = (session.heroKey === "LOKI") ? 90 : 45; addVaultCoins(g);
            playSfx(987, 0.16, "sine", 0.085, 1318); spawnFxPuff(c.position.x, 1.15, c.position.z, 0xfde047, 0.58);
            setStatus(`🪙 Picked up Coin Orb (+${g} 🪙 added to Vault)!`);
          }
        } else { c.userData.respawn -= dt; if (c.userData.respawn <= 0) { c.userData.active = true; c.visible = true; } }
      });

      let stoodPad = null;
      for (const [k, st] of Object.entries(STATIONS)) {
        if (Math.hypot(heroPos.x - st.x, heroPos.z - st.z) < (state.driving ? st.r + 1.2 : st.r)) { stoodPad = k; break; }
      }
      const pw = document.getElementById("pad-progress-wrap");
      if (stoodPad) {
        if (state.activePad !== stoodPad) { state.activePad = stoodPad; state.padProgress = 0; if (stoodPad !== "SHIELD") state.shieldPadLatched = false; }
        if (stoodPad === "SHIELD" && state.shieldPadLatched) pw.style.display = "none";
        else {
          state.padProgress += dt * 1.25; pw.style.display = "flex";
          document.getElementById("pad-progress-label").innerText = STATIONS[stoodPad].label;
          document.getElementById("pad-progress-bar").style.width = Math.min(100, Math.max(0, state.padProgress * 100)) + "%";
          if (state.padProgress >= 1.0) { completePadAction(stoodPad); state.padProgress = -0.75; }
        }
      } else { state.activePad = null; state.padProgress = 0; state.shieldPadLatched = false; pw.style.display = "none"; }

      const growSpd = (session.heroKey === "WANDA") ? 5.5 : 3.0;
      for (let i = 0; i < 4; i++) { state.crops[i] = Math.min(100, state.crops[i] + growSpd * dt); const s = 0.25 + (state.crops[i] / 100) * 0.95; cropMeshes[i].scale.set(s, s, s); }
      if (state.roverCooldown > 0) state.roverCooldown -= dt;

      if (state.shieldOn) {
        state.power = Math.max(0, state.power - (session.heroKey === "CAP" ? 0.45 : 0.9) * diff.drain * dt);
        if (state.power <= 0.1) { state.shieldOn = false; setStatus("⚡ Battery hit 0%! Shield offline!"); }
      } else if (state.dusty) {
        state.power = Math.max(0, state.power - pl.dustPowerLoss * diff.drain * dt);
      } else {
        state.power = Math.min(100, state.power + ((session.heroKey === "IRON") ? 3.2 : 1.8) * pl.solarChargeMult * dt);
      }

      let oxLoss = (state.doorSealed ? 0.15 : 0.65) * diff.drain;
      if (session.heroKey === "WIDOW") oxLoss *= 0.6;
      state.oxygen = Math.max(0, state.oxygen - oxLoss * dt);
      state.food = Math.max(0, state.food - 0.12 * diff.drain * dt);

      if (state.flarePhase === "CALM" && state.flaresTriggered < 2 && state.solClock >= state.flareSchedule[state.flaresTriggered]) {
        state.flaresTriggered += 1;
        state.flarePhase = "WARN"; state.flareTimer = diff.flareWarn;
        playSfx(240, 0.45, "sawtooth", 0.08, 460);
        document.getElementById("flare-alarm").style.display = "block";
        document.getElementById("flare-alarm-title").innerText = `🚨 DONKI ${NASA.flr.class} FLARE (${state.flaresTriggered}/2)!`;
        showComic("🚨☀️🔥", `SOLAR FLARE ${state.flaresTriggered} OF 2!`, `DONKI ${NASA.flr.class} hits in ${Math.ceil(diff.flareWarn)}s! Get Inside + E + Q!`, 2800);
      } else if (state.flarePhase === "WARN") {
        state.flareTimer -= dt;
        document.getElementById("flare-alarm-desc").innerText = `Impact in ${Math.max(0, state.flareTimer).toFixed(1)}s! Inside + Door(E) + Shield(Q)`;
        if (state.flareTimer <= 0) { state.flarePhase = "ACTIVE"; state.flareTimer = diff.flareDur; playSfx(180, 0.5, "sawtooth", 0.095, 120); }
      } else if (state.flarePhase === "ACTIVE") {
        state.flareTimer -= dt;
        document.getElementById("flare-alarm-title").innerText = `☢️ STORM HITTING (${Math.ceil(state.flareTimer)}s)`;
        const safe = nowIn && state.doorSealed && state.shieldOn;
        if (!safe) {
          state.hp = Math.max(0, state.hp - diff.flareDmg * pl.flareDmgMult * (session.heroKey === "THOR" ? 0.4 : 1.0) * dt);
          state.rad += 0.20 * pl.flareDmgMult * dt;
          document.getElementById("flare-alarm-desc").innerText = "⚠️ RADIATION HIT! Inside + Door(E) + Shield(Q)!";
        } else {
          state.rad += 0.008 * dt;
          document.getElementById("flare-alarm-desc").innerText = `🛡️ PROTECTED BY ${getHero().shieldName.toUpperCase()}!`;
        }
        if (state.flareTimer <= 0) {
          state.flarePhase = "CALM"; document.getElementById("flare-alarm").style.display = "none";
          if (Math.random() < pl.dustChance) { state.dusty = true; showComic("🌪️☀️", "SOLAR PANELS DUSTY!", "Press 1 to sweep dust off solar panels!", 2300); }
          else showComic("☀️✅", "FLARE PASSED!", "Press Q to turn Shield OFF and recharge!", 2200);
        }
      } else {
        state.rad += (pl.radBaseline / SOL_SECONDS) * dt;
      }

      state.solClock += dt;
      if (state.solClock >= SOL_SECONDS) {
        state.solClock = 0; state.sol += 1;
        state.flareSchedule = makeSolFlares(); state.flaresTriggered = 0;
        telemetryLog.push({ sol: state.sol, pwr: Math.round(state.power), ox: Math.round(state.oxygen), hp: Math.round(state.hp) });
        if (state.sol > 7) endMission(true, "WIN");
        else {
          const bon = (session.heroKey === "LOKI") ? 140 : 70; addVaultCoins(bon); state.science += 60;
          if (state.pantryCount > 0) { state.pantryCount--; refreshPantryVisuals(); }
          playSfx(523, 0.2, "triangle", 0.09, 784);
          if (getDilemma(state.sol) && !state.dilemmasShown[state.sol]) { state.dilemmasShown[state.sol] = true; triggerDilemma(state.sol); }
          else showComic(pl.icon + "🏆", `${pl.name.toUpperCase()} SOL ${state.sol} OF 7`, `+${bon} 🪙 Vault Coins!`, 2100);
        }
      }

      if (state.power <= 0) endMission(false, "POWER");
      else if (state.oxygen <= 0) endMission(false, "OXYGEN");
      else if (state.food <= 0) endMission(false, "FOOD");
      else if (state.hp <= 0) endMission(false, "RADIATION");

      updateHUD(); drawMinimap();
    }

    const z = state.camZoom, fr = state.fullPlanetMode ? 0.06 : Math.max(0.14, 0.92 - (z - 1) * 0.2);
    const camOff = state.driving && !state.fullPlanetMode ? 22.0 : 19.5;
    camera.position.lerp(new THREE.Vector3(heroPos.x * fr, 14.0 * z, heroPos.z * fr + camOff * z), Math.min(1, dt * 4.5));
    camera.lookAt(heroPos.x * fr, state.fullPlanetMode ? -3.0 : 1.5, heroPos.z * fr);
    renderer.render(scene, camera);
  } catch(err) { console.error(err); }
}

function updateHUD() {
  const pl = getPlanet();
  const rem = Math.max(0, Math.ceil(SOL_SECONDS - state.solClock));
  const mm = String(Math.floor(rem / 60)).padStart(2, "0"), ss = String(rem % 60).padStart(2, "0");
  document.getElementById("ui-sol").innerText = Math.min(7, state.sol) + "/7";
  document.getElementById("bar-sol").style.width = Math.min(100, (state.solClock / SOL_SECONDS) * 100) + "%";
  document.getElementById("ui-weather").innerText = state.flarePhase === "ACTIVE" ? `☢️ ${NASA.flr.class} STORM` : (state.flarePhase === "WARN" ? "🚨 FLARE WARN" : `⏱️ ${mm}:${ss} • ${state.dusty ? "Dusty" : "Calm"}`);

  document.getElementById("ui-pwr").innerText = Math.round(state.power) + "%"; document.getElementById("bar-pwr").style.width = state.power + "%";
  document.getElementById("sub-pwr").innerText = state.shieldOn ? "🛡️ Draining" : (state.dusty ? "🌪️ Dusty" : `☀️ ${pl.key === "MARS" ? "43% Sun" : "Charging"}`);
  document.getElementById("ui-ox").innerText = Math.round(state.oxygen) + "%"; document.getElementById("bar-ox").style.width = state.oxygen + "%";
  document.getElementById("sub-ox").innerText = state.doorSealed ? "🔒 Sealed" : "🔓 Open (-O₂)";
  document.getElementById("ui-food").innerText = Math.round(state.food) + "%"; document.getElementById("bar-food").style.width = state.food + "%";
  document.getElementById("sub-basket").innerText = `🧺 ${state.basket.length}/4 ${state.basket.join("")}`;
  document.getElementById("ui-hp").innerText = Math.round(state.hp) + "%"; document.getElementById("bar-hp").style.width = state.hp + "%";
  document.getElementById("sub-rad").innerText = `☢️ ${state.rad.toFixed(2)} mSv`;
  document.getElementById("ui-sci").innerText = state.science; syncVaultDisplays();

  document.getElementById("btn-shield").innerHTML = (state.shieldOn ? "🛡️ Shield: ON" : "🛡️ Shield: OFF") + '<span class="kbadge">Q</span>';
  document.getElementById("btn-door").innerHTML = (state.doorSealed ? "🔒 Airlock: SEALED" : "🔓 Airlock: OPEN") + '<span class="kbadge">E</span>';
  document.getElementById("zone-badge").innerText = state.driving ? "🚙 DRIVING ROVER" : (isInsideHabitat() ? "📍 INSIDE BASE" : `${pl.icon} ON ${pl.name.toUpperCase()}`);
}

function endMission(won, cause) {
  state.ended = true;
  ["flare-alarm", "dilemma-modal", "pause-modal"].forEach(id => document.getElementById(id).style.display = "none");
  document.getElementById("debrief-modal").style.display = "flex";
  const h = getHero(), pl = getPlanet();
  if (won) {
    session.wins += 1; addVaultCoins(300); playSfx(523, 0.25, "triangle", 0.1, 1046);
    document.getElementById("debrief-icon").innerText = `🏆🦸‍♂️${pl.icon}`;
    document.getElementById("debrief-title").innerText = `7-SOL ${pl.name.toUpperCase()} VICTORY!`;
    document.getElementById("debrief-rank").innerText = `+300 🪙 Victory Vault Bonus! Science: ${state.science}`;
    document.getElementById("debrief-sub").innerText = `${h.name} survived 7 Sols at ${pl.site} | Dose: ${state.rad.toFixed(2)} mSv`;
    document.getElementById("debrief-lesson").innerHTML = `<b>🛰️ Takeaway:</b> You balanced ${pl.name}'s sunlight (${pl.solarIrradiance}), ${pl.radBaseline} mSv/Sol radiation, and ${pl.commsLabel} radio delay across 7 Sols!`;
  } else {
    playSfx(220, 0.45, "sawtooth", 0.09, 110);
    document.getElementById("debrief-icon").innerText = "🛠️📡";
    document.getElementById("debrief-title").innerText = `${pl.name.toUpperCase()} DEBRIEF — SOL ${state.sol}/7`;
    document.getElementById("debrief-rank").innerText = `Science: ${state.science} • Vault Coins Kept: ${Math.floor(session.vaultCoins)} 🪙`;
    const L = { POWER: `⚡ Power Depleted on ${pl.name}! Turn Shield OFF (Q) after flares & clean Solar [1].`, OXYGEN: `🫁 O₂ Depleted! Seal Airlock (E) & visit ${pl.o2Short} [2].`, FOOD: "🍽️ Pantry Empty! Harvest Farm [4] & Stock Pantry [5].", RADIATION: `☢️ Solar Flare Hit! Rush inside, Door (E) & ${h.shieldName} (Q)!` };
    document.getElementById("debrief-sub").innerText = `Constraint reached: ${cause}. All Vault Coins earned stay banked!`;
    document.getElementById("debrief-lesson").innerHTML = L[cause] || L.POWER;
  }
  const c = document.getElementById("debrief-chart"), ctx = c.getContext("2d"); ctx.clearRect(0, 0, c.width, c.height);
  const pts = telemetryLog.length > 1 ? telemetryLog : [...telemetryLog, { sol: state.sol + 0.5, pwr: state.power, ox: state.oxygen, hp: state.hp }];
  function plS(k, col) { ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath(); pts.forEach((p, i) => { const x = 45 + (i / Math.max(1, pts.length - 1)) * 525, y = 118 - (Math.max(0, Math.min(100, p[k])) / 100) * 96; if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke(); }
  plS("pwr", "#facc15"); plS("ox", "#38bdf8"); plS("hp", "#f43f5e");
  syncVaultDisplays();
}

window.addEventListener("keydown", e => {
  if (session.screen !== "GAME") return;
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) e.preventDefault();
  keys[e.code] = true;
  if (e.repeat) return;
  switch (e.code) {
    case "KeyP": togglePause(); break;
    case "KeyB": toggleDriveRover(); break;
    case "Space": triggerJump(); break;
    case "KeyQ": toggleShield(); break;
    case "KeyE": toggleDoor(); break;
    case "KeyT": triggerEmote("COFFEE"); break;
    case "KeyY": triggerEmote("DANCE"); break;
    case "KeyU": triggerEmote("SIT"); break;
    case "Digit1": autoRunTo("SOLAR"); break;
    case "Digit2": autoRunTo("O2GEN"); break;
    case "Digit3": autoRunTo("SCIENCE"); break;
    case "Digit4": autoRunTo("FARM"); break;
    case "Digit5": autoRunTo("PANTRY"); break;
    case "Digit6": autoRunTo("SHIELD"); break;
    case "KeyR": deployRoverScan(); break;
    case "KeyN": advanceSolEarly(); break;
    case "KeyF": callEarth(1); break;
    case "KeyG": callEarth(2); break;
    case "KeyH": callEarth(3); break;
    case "KeyJ": callEarth(4); break;
    case "KeyK": callEarth(5); break;
    case "KeyZ": case "Minus": adjustZoom(0.45); break;
    case "KeyX": case "Equal": adjustZoom(-0.45); break;
    case "KeyC": toggleFullPlanetView(); break;
    case "KeyM": case "Escape": toggleSidebar(); break;
    case "KeyV": toggleMusic(); break;
  }
});
window.addEventListener("keyup", e => { keys[e.code] = false; });

startFiveSecondLoader();
</script>
</body>
</html>
"""

components.html(APP_HTML.replace("__NASA_JSON__", json.dumps(nasa_payload)), height=860, scrolling=False)
