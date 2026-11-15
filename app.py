import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Avengers Assemble | Lunar Outpost 3D",
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
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
iframe {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 99999 !important;
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; font-family: 'Segoe UI', system-ui, sans-serif; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: #020617; color: #f8fafc; touch-action: none; }

  #app-shell { position: relative; width: 100%; height: 100%; overflow: hidden; background: #020617; }
  #bg-space-canvas { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }

  .screen {
    position: absolute; inset: 0; z-index: 10;
    display: none; flex-direction: column; align-items: center; justify-content: center;
    padding: 14px; overflow-y: auto; touch-action: pan-y;
  }
  .screen.active { display: flex; }

  .glass-panel {
    background: rgba(9, 13, 31, 0.9);
    backdrop-filter: blur(12px);
    border: 2.5px solid #eab308;
    border-radius: 22px;
    box-shadow: 0 0 45px rgba(56, 189, 248, 0.25), 0 18px 40px rgba(0, 0, 0, 0.82);
  }

  .loader-wrap {
    width: 680px; max-width: 95%; padding: 28px 30px; text-align: center;
    background: rgba(9, 13, 31, 0.88); border: 2.5px solid #38bdf8;
    border-radius: 24px; box-shadow: 0 0 60px rgba(56, 189, 248, 0.3);
  }
  .orbit-ring {
    width: 88px; height: 88px; margin: 0 auto 14px auto;
    border-radius: 50%; border: 4px solid rgba(56, 189, 248, 0.2);
    border-top-color: #fde047; border-right-color: #38bdf8;
    display: flex; align-items: center; justify-content: center;
    font-size: 38px; animation: spinOrbit 1.4s linear infinite;
  }
  .orbit-ring span { animation: spinReverse 1.4s linear infinite; display: inline-block; }
  @keyframes spinOrbit { to { transform: rotate(360deg); } }
  @keyframes spinReverse { to { transform: rotate(-360deg); } }

  .load-title {
    font-size: clamp(24px, 4.5vw, 38px); font-weight: 900; letter-spacing: 2px;
    background: linear-gradient(90deg, #fde047, #38bdf8, #f43f5e);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .load-bar-bg {
    width: 100%; height: 13px; background: #0f172a; border: 2px solid #38bdf8;
    border-radius: 999px; overflow: hidden; margin: 16px 0 8px 0;
  }
  .load-bar-fill {
    height: 100%; width: 0%;
    background: linear-gradient(90deg, #ef4444, #eab308, #38bdf8);
    transition: width 0.08s linear;
  }
  .science-backdrop-card {
    margin-top: 18px; padding: 14px 18px; border-radius: 16px;
    background: linear-gradient(145deg, rgba(30, 27, 75, 0.92), rgba(15, 23, 42, 0.92));
    border: 2px solid rgba(253, 224, 71, 0.7); text-align: left;
  }
  .science-tag { font-size: 11px; font-weight: 900; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; }
  .science-fact-txt { font-size: clamp(12.5px, 2.2vw, 14.5px); color: #f8fafc; margin-top: 5px; line-height: 1.48; font-weight: 600; }

  .create-card { width: 540px; max-width: 95%; padding: 28px 30px; text-align: center; }
  .game-logo-title {
    font-size: clamp(28px, 5vw, 40px); font-weight: 900; color: #fde047; letter-spacing: 1.5px;
    text-shadow: 0 0 24px rgba(253, 224, 71, 0.45);
  }
  .game-logo-sub {
    font-size: 13px; color: #7dd3fc; font-weight: 800; letter-spacing: 2px;
    text-transform: uppercase; margin: 6px 0 22px 0;
  }
  .menu-btn {
    width: 100%; padding: 14px 18px; margin-bottom: 11px;
    border-radius: 15px; font-size: 15px; font-weight: 900; cursor: pointer;
    border: 2.5px solid #fde047; color: #ffffff;
    background: linear-gradient(90deg, #dc2626 0%, #2563eb 100%);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6); transition: transform 0.15s, box-shadow 0.15s;
  }
  .menu-btn:hover { transform: translateY(-2px); box-shadow: 0 0 22px rgba(56, 189, 248, 0.7); }
  .menu-btn.secondary { background: linear-gradient(145deg, #1e293b, #0f172a); border-color: #38bdf8; }
  .menu-btn.multi { background: linear-gradient(145deg, #3b0764, #1e1b4b); border-color: #c084fc; }
  #multi-notice {
    display: none; margin-top: 8px; padding: 11px 14px; border-radius: 12px;
    background: rgba(127, 29, 29, 0.92); border: 2px solid #fca5a5;
    color: #fef08a; font-weight: 800; font-size: 13px;
  }

  .age-panel { width: 1140px; max-width: 97%; max-height: 96%; overflow-y: auto; padding: 16px 20px; }
  .age-top-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
  .age-input-group {
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8;
    border-radius: 14px; padding: 8px 14px;
  }
  .age-input-group label { font-size: 14px; font-weight: 900; color: #fde047; }
  .age-input-group input {
    width: 96px; padding: 7px 10px; border-radius: 10px;
    border: 2px solid #fde047; background: #020617; color: #ffffff;
    font-size: 16px; font-weight: 900; text-align: center; outline: none;
  }
  #age-feedback { font-size: 12.5px; font-weight: 800; color: #93c5fd; }
  .vault-badge {
    background: linear-gradient(145deg, #422006, #1e1b4b);
    border: 2.5px solid #fde047; border-radius: 14px; padding: 8px 16px;
    font-size: 15px; font-weight: 900; color: #fde047;
  }
  .hero-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin: 10px 0 12px 0; }
  @media (max-width: 980px) { .hero-grid { grid-template-columns: repeat(4, 1fr); } }
  @media (max-width: 580px) { .hero-grid { grid-template-columns: repeat(2, 1fr); } }
  .hero-card {
    background: linear-gradient(155deg, #0f172a, #1e1b4b);
    border: 2.5px solid #334155; border-radius: 15px; padding: 8px 6px;
    text-align: center; cursor: pointer; transition: transform 0.15s, border-color 0.15s;
  }
  .hero-card:hover { transform: translateY(-2px); border-color: #38bdf8; }
  .hero-card.selected {
    border-color: #fde047; box-shadow: 0 0 20px rgba(253, 224, 71, 0.75);
    background: linear-gradient(155deg, #1e1b4b, #172554);
  }
  .hero-card.locked { opacity: 0.8; border-color: #475569; }
  .hero-name { font-weight: 900; font-size: 12.5px; color: #fde047; margin-top: 2px; }
  .hero-perk { font-size: 10px; color: #86efac; font-weight: 700; margin-top: 3px; line-height: 1.25; }
  .hero-status { margin-top: 5px; padding: 3px 5px; border-radius: 8px; font-size: 10px; font-weight: 900; }
  .status-unlocked { background: rgba(22, 163, 74, 0.25); color: #86efac; border: 1px solid #4ade80; }
  .status-locked { background: rgba(127, 29, 29, 0.55); color: #fde047; border: 1px solid #f87171; }
  #hero-msg { min-height: 20px; text-align: center; font-size: 13px; font-weight: 800; color: #fca5a5; margin-bottom: 8px; }
  .continue-btn {
    width: 320px; max-width: 100%; padding: 12px 22px; border-radius: 14px;
    font-size: 15px; font-weight: 900; cursor: pointer;
    border: 2.5px solid #fde047; color: #ffffff;
    background: linear-gradient(90deg, #16a34a, #0284c7); display: block; margin: 0 auto;
  }
  .continue-btn:disabled { background: #1e293b; border-color: #475569; color: #64748b; cursor: not-allowed; }

  .inst-panel { width: 1040px; max-width: 97%; max-height: 96%; overflow-y: auto; padding: 20px 24px; text-align: center; }
  .inst-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0 18px 0; }
  @media (max-width: 860px) { .inst-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 500px) { .inst-grid { grid-template-columns: 1fr; } }
  .inst-box { background: linear-gradient(155deg, #1e293b, #0f172a); border: 2px solid #38bdf8; border-radius: 15px; padding: 13px 12px; }
  .inst-box h3 { color: #fde047; font-size: 14px; margin: 5px 0; }
  .inst-box p { color: #e2e8f0; font-size: 12px; line-height: 1.42; }

  #screen-game { padding: 0; overflow: hidden; touch-action: none; }
  #game-root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #020617; outline: none; touch-action: none; }
  #canvas-container { position: absolute; inset: 0; width: 100%; height: 100%; touch-action: none; }

  #game-sidebar {
    position: absolute; top: 0; left: 0; bottom: 0; width: 268px; max-width: 84vw; z-index: 45;
    background: linear-gradient(180deg, rgba(7, 11, 24, 0.98), rgba(15, 23, 42, 0.98));
    border-right: 3px solid #eab308; padding: 14px 12px;
    transform: translateX(-100%); transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
    display: flex; flex-direction: column; gap: 7px; overflow-y: auto;
    box-shadow: 12px 0 36px rgba(0, 0, 0, 0.85);
  }
  #game-sidebar.open { transform: translateX(0); }
  .sb-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1.5px solid #334155; }
  .sb-stat { background: #0f172a; border: 1.5px solid #38bdf8; border-radius: 11px; padding: 8px 10px; font-size: 12px; line-height: 1.48; }
  .sb-btn {
    width: 100%; padding: 9px 11px; border-radius: 10px; text-align: left;
    font-size: 12px; font-weight: 800; color: #ffffff; cursor: pointer;
    background: linear-gradient(90deg, #1e293b, #1e1b4b); border: 1.5px solid #38bdf8;
  }
  .sb-btn:hover { border-color: #fde047; background: #1d4ed8; }
  .sb-btn.danger { background: linear-gradient(90deg, #7f1d1d, #991b1b); border-color: #fca5a5; }

  .top-hud {
    position: absolute; top: 6px; left: 6px; right: 6px;
    display: grid; grid-template-columns: 0.48fr 0.92fr 0.88fr 0.88fr 0.88fr 0.88fr 1.25fr;
    gap: 5px; pointer-events: none; z-index: 12;
  }
  .hud-card {
    background: rgba(9, 13, 31, 0.86); backdrop-filter: blur(8px);
    border: 1.8px solid rgba(234, 179, 8, 0.78); border-radius: 10px;
    padding: 4px 7px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6); pointer-events: auto;
  }
  .sidebar-toggle-btn {
    width: 100%; height: 100%; background: linear-gradient(145deg, #1d4ed8, #1e1b4b);
    border: 2px solid #fde047; border-radius: 10px; color: #fde047;
    font-size: 11px; font-weight: 900; cursor: pointer; pointer-events: auto;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px;
  }
  .hud-row { display: flex; justify-content: space-between; align-items: center; }
  .hud-lbl { font-size: 9.5px; font-weight: 800; color: #93c5fd; text-transform: uppercase; display: flex; align-items: center; gap: 3px; }
  .hud-val { font-size: 14.5px; font-weight: 900; color: #ffffff; }
  .hud-sub { font-size: 9px; font-weight: 800; color: #cbd5e1; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-bg { width: 100%; height: 5px; background: rgba(2, 6, 23, 0.92); border-radius: 99px; overflow: hidden; margin-top: 2px; }
  .bar-fill { height: 100%; width: 90%; transition: width 0.18s ease; border-radius: 99px; }

  .qchip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 13px; height: 13px; border-radius: 50%;
    background: rgba(56, 189, 248, 0.25); border: 1px solid #38bdf8;
    color: #7dd3fc; font-size: 9px; font-weight: 900; cursor: pointer;
  }

  .ticker-bar {
    position: absolute; top: 64px; left: 6px; right: 6px;
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(6px);
    border: 1.5px solid #38bdf8; border-radius: 9px; padding: 3.5px 10px;
    z-index: 12; font-size: 11px; font-weight: 800;
  }
  #status-msg { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .nasa-badge-btn {
    background: rgba(14, 165, 233, 0.22); border: 1px solid #38bdf8; color: #7dd3fc;
    border-radius: 999px; padding: 2px 8px; font-size: 10px; font-weight: 900; cursor: pointer; white-space: nowrap;
  }

  #minimap-wrap {
    position: absolute; top: 96px; left: 8px; z-index: 16;
    background: rgba(2, 6, 23, 0.84); border: 1.8px solid #38bdf8; border-radius: 12px;
    padding: 4px; text-align: center;
  }
  #minimap { display: block; border-radius: 7px; background: #0b1120; }

  #zoom-bar {
    position: absolute; top: 96px; right: 8px; z-index: 16;
    display: flex; flex-direction: column; gap: 4px;
    background: rgba(2, 6, 23, 0.82); border: 1.5px solid #38bdf8; border-radius: 11px; padding: 4px;
  }
  .zbtn {
    background: #1e293b; border: 1.2px solid #7dd3fc; color: #fde047;
    border-radius: 7px; padding: 4px 7px; font-size: 11px; font-weight: 900; cursor: pointer;
  }
  .zbtn:hover { background: #1d4ed8; }

  #flare-alarm {
    position: absolute; top: 228px; left: 8px;
    background: linear-gradient(90deg, rgba(185, 28, 28, 0.95), rgba(127, 29, 29, 0.95));
    border: 2px solid #fde047; border-radius: 11px; padding: 6px 10px;
    z-index: 22; display: none; width: 235px;
    box-shadow: 0 0 22px rgba(239, 68, 68, 0.85); animation: pulseRed 0.75s infinite alternate;
  }
  @keyframes pulseRed { from { transform: scale(1); } to { transform: scale(1.03); } }

  #comic-toast {
    position: absolute; top: 98px; right: 56px; width: 230px;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(30, 27, 75, 0.96));
    border: 2.5px solid #fde047; border-radius: 14px; padding: 7px 10px;
    z-index: 25; display: none; text-align: center;
    box-shadow: 0 0 24px rgba(253, 224, 71, 0.5);
  }

  #unlock-banner {
    position: absolute; top: 98px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(90deg, #ca8a04, #16a34a);
    border: 2px solid #fef08a; border-radius: 999px; padding: 6px 16px;
    font-size: 12px; font-weight: 900; color: #ffffff; z-index: 35; display: none;
    white-space: nowrap; max-width: 90%; overflow: hidden; text-overflow: ellipsis;
  }

  #pad-progress-wrap {
    position: absolute; top: 134px; left: 50%; transform: translateX(-50%);
    background: rgba(2, 6, 23, 0.92); border: 2px solid #4ade80; border-radius: 999px;
    padding: 5px 14px; display: none; align-items: center; gap: 8px; z-index: 20;
  }
  #pad-progress-bar-bg { width: 110px; height: 8px; background: #1e293b; border-radius: 99px; overflow: hidden; }
  #pad-progress-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #4ade80, #fde047); }

  #joy-wrap {
    position: absolute; bottom: 104px; left: 14px; z-index: 24;
    display: none; flex-direction: column; align-items: center; gap: 3px;
  }
  #joy-wrap.visible { display: flex; }
  #joy-base {
    width: 112px; height: 112px; border-radius: 50%;
    background: radial-gradient(circle, rgba(15, 23, 42, 0.72), rgba(30, 58, 138, 0.45));
    border: 2.5px solid rgba(56, 189, 248, 0.85);
    position: relative; touch-action: none;
    box-shadow: 0 0 22px rgba(56, 189, 248, 0.35);
  }
  #joy-knob {
    width: 46px; height: 46px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #fde047, #ea580c);
    border: 2.5px solid #ffffff;
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
    pointer-events: none;
  }
  .joy-hint { font-size: 9.5px; font-weight: 900; color: #7dd3fc; text-shadow: 0 1px 4px #000; }

  #mobile-quick-pad {
    position: absolute; bottom: 104px; right: 12px; z-index: 24;
    display: none; flex-direction: column; gap: 6px;
  }
  #mobile-quick-pad.visible { display: flex; }
  .mq-btn {
    width: 60px; height: 46px; border-radius: 13px;
    background: rgba(15, 23, 42, 0.88); border: 2px solid #fde047;
    color: #fff; font-size: 11px; font-weight: 900; cursor: pointer;
    box-shadow: 0 4px 14px rgba(0,0,0,0.65);
  }

  .bottom-dock {
    position: absolute; bottom: 6px; left: 6px; right: 6px;
    display: grid; grid-template-columns: 1.38fr 1.25fr 1.55fr;
    gap: 6px; z-index: 15;
  }
  .dock-panel {
    background: rgba(9, 13, 31, 0.9); backdrop-filter: blur(8px);
    border: 1.5px solid rgba(56, 189, 248, 0.6); border-radius: 11px; padding: 5px 7px;
  }
  .dock-title { font-size: 9.5px; font-weight: 900; color: #fde047; text-transform: uppercase; margin-bottom: 4px; display: flex; justify-content: space-between; }
  .btn-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
  .btn-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; }
  .btn-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
  .btn-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }

  .gbtn {
    background: linear-gradient(145deg, #1d4ed8, #312e81);
    color: #ffffff; border: 1.3px solid #7dd3fc; border-radius: 7px;
    padding: 4.5px 3px; font-size: 10px; font-weight: 800; cursor: pointer; text-align: center;
    line-height: 1.15;
  }
  .gbtn:hover { border-color: #fde047; }
  .gbtn-green { background: linear-gradient(145deg, #15803d, #047857); border-color: #86efac; }
  .gbtn-red { background: linear-gradient(145deg, #b91c1c, #991b1b); border-color: #fca5a5; }
  .gbtn-gold { background: linear-gradient(145deg, #ca8a04, #b45309); border-color: #fef08a; }
  .gbtn-cyan { background: linear-gradient(145deg, #0369a1, #1e3a8a); border-color: #38bdf8; }
  .gbtn-purple { background: linear-gradient(145deg, #7e22ce, #4c1d95); border-color: #d8b4fe; }
  .kbadge {
    display: inline-block; background: rgba(2, 6, 23, 0.78); color: #fde047;
    border: 1px solid rgba(253, 224, 71, 0.65); border-radius: 4px;
    padding: 0 3px; font-size: 8.5px; font-weight: 900; margin-left: 2px;
  }

  .modal-backdrop {
    position: absolute; inset: 0; z-index: 60;
    background: rgba(2, 6, 23, 0.9); backdrop-filter: blur(8px);
    display: none; align-items: center; justify-content: center; padding: 12px;
  }
  .modal-box {
    background: linear-gradient(160deg, #0f172a, #1e1b4b);
    border: 2.5px solid #38bdf8; border-radius: 18px; padding: 16px 20px;
    width: 660px; max-width: 97%; max-height: 92%; overflow-y: auto;
  }
  .choice-btn {
    width: 100%; text-align: left; background: rgba(30, 41, 59, 0.95);
    border: 2px solid #eab308; border-radius: 12px; padding: 10px 12px;
    color: #fff; cursor: pointer; margin-top: 8px;
  }
  .choice-btn:hover { background: rgba(30, 58, 138, 0.95); border-color: #38bdf8; }

  #glossary-pop {
    position: absolute; top: 96px; left: 50%; transform: translateX(-50%);
    width: 390px; max-width: 92%;
    background: rgba(15, 23, 42, 0.98); border: 2.5px solid #38bdf8; border-radius: 15px;
    padding: 11px 14px; z-index: 50; display: none;
  }
  .slider-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 8px 0; }
  .slider-item { background: #020617; border: 1px solid #334155; border-radius: 9px; padding: 7px 9px; font-size: 11.5px; }
  .slider-item input { width: 100%; margin-top: 3px; }

  @media (max-width: 820px) {
    .top-hud { grid-template-columns: 0.6fr repeat(3, 1fr); row-gap: 4px; }
    .hud-sub { display: none; }
    .ticker-bar { top: 98px; font-size: 10px; }
    #minimap-wrap { top: 128px; }
    #minimap { width: 92px; height: 80px; }
    #zoom-bar { top: 128px; }
    #flare-alarm { top: 230px; width: 195px; }
    .bottom-dock { grid-template-columns: 1fr; gap: 4px; }
    .dock-panel.hide-sm-panel { display: none; }
    .kbadge { display: none; }
    #joy-wrap { bottom: 88px; left: 10px; }
    #mobile-quick-pad { bottom: 88px; right: 10px; }
  }
</style>
</head>
<body>
<div id="app-shell">
  <canvas id="bg-space-canvas"></canvas>

  <div id="screen-loader" class="screen active">
    <div class="loader-wrap">
      <div class="orbit-ring"><span>🌕</span></div>
      <div class="load-title">AVENGERS ASSEMBLE</div>
      <div style="font-size:12px;color:#93c5fd;font-weight:800;margin-top:4px;letter-spacing:1.2px;">SHACKLETON CRATER 3D LUNAR OUTPOST</div>
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
      <div style="font-size:50px;margin-bottom:4px;">🛡️🌕🚀</div>
      <div class="game-logo-title">AVENGERS ASSEMBLE</div>
      <div class="game-logo-sub">3D Lunar Survival Expedition</div>
      <button class="menu-btn" onclick="goToAgePage()">🚀 CREATE &amp; PLAY MISSION</button>
      <button class="menu-btn secondary" id="create-music-btn" onclick="toggleMusic()">🎵 MUSIC: ON</button>
      <button class="menu-btn multi" onclick="clickMultiplayer()">👥 MULTIPLAYER</button>
      <div id="multi-notice">🚧 Multiplayer Mode is Currently Unavailable! Enjoy Single-Player 3D Lunar Survival.</div>
    </div>
  </div>

  <div id="screen-age" class="screen">
    <div class="glass-panel age-panel">
      <div style="text-align:center;margin-bottom:10px;">
        <h2 style="color:#fde047;font-size:clamp(18px, 3vw, 24px);font-weight:900;">🦸 COMMANDER AGE &amp; HERO SELECTION</h2>
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
      <h2 style="color:#fde047;font-size:clamp(20px, 3vw, 26px);font-weight:900;">📖 MISSION BRIEFING &amp; CONTROLS</h2>
      <p id="inst-hero-line" style="color:#7dd3fc;font-size:13.5px;font-weight:800;margin-top:5px;"></p>
      <div class="inst-grid">
        <div class="inst-box">
          <div style="font-size:28px;">🕹️</div>
          <h3>1. Laptop &amp; Mobile</h3>
          <p><b>Laptop:</b> WASD/Arrows to move, <b>Space</b> jump, <b>Z/X</b> or wheel to zoom out to the whole Moon!<br><b>Phone:</b> Use the glowing thumb <b>Joystick Handle</b> &amp; pinch to zoom!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:28px;">⌨️</div>
          <h3>2. Fast Keyboard Keys</h3>
          <p><b>Q</b> Shield • <b>E</b> Airlock • <b>1–6</b> Auto-Run Stations • <b>R</b> Rover • <b>N</b> Next Sol • <b>F G H J K</b> Earth Radio • <b>M</b> Menu • <b>V</b> Music!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:28px;">🚨</div>
          <h3>3. NASA Solar Flares</h3>
          <p>Keep Shield <b>OFF</b> when calm to charge Power. When a <b>DONKI Solar Flare</b> hits: Run Inside, press <b>E</b> to Seal Airlock, and press <b>Q</b> for Shield!</p>
        </div>
        <div class="inst-box">
          <div style="font-size:28px;">🪙</div>
          <h3>4. Unlock Elite Heroes</h3>
          <p>Explore the huge lunar surface to gather Coins, farm CSA crops, mine Ice, and drill Science! Earn <b>1080+ Vault Coins</b> to unlock elite Avengers!</p>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
        <button class="menu-btn secondary" style="width:180px;margin:0;" onclick="goToAgePage()">⬅️ Back</button>
        <button class="menu-btn" style="width:300px;margin:0;" onclick="launchGameScreen()">🚀 LAUNCH 3D MOON MISSION</button>
      </div>
    </div>
  </div>

  <div id="screen-game" class="screen">
    <div id="game-root" tabindex="0">
      <div id="canvas-container"></div>

      <div id="game-sidebar">
        <div class="sb-header">
          <span style="font-weight:900;color:#fde047;font-size:15px;">🛡️ AVENGERS MENU</span>
          <button onclick="toggleSidebar()" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 10px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <div class="sb-stat">
          <div><b>Hero:</b> <span id="sb-hero" style="color:#fde047;"></span></div>
          <div><b>Mode:</b> <span id="sb-mode" style="color:#7dd3fc;"></span></div>
          <div><b>Vault Coins:</b> <span id="sb-coins" style="color:#fde047;font-weight:900;">40</span> 🪙</div>
          <div><b>Trophies:</b> <span id="sb-wins" style="color:#4ade80;font-weight:900;">0</span> 🏆</div>
        </div>
        <button class="sb-btn" onclick="sidebarChangeAgeHero()">🦸 Change Age &amp; Hero</button>
        <button class="sb-btn" onclick="sidebarGoInstructions()">📖 Instructions &amp; Shortcut Keys</button>
        <button class="sb-btn" onclick="openMathLab()">📈 Engineering Graphs &amp; Math Lab</button>
        <button class="sb-btn" onclick="openNasaModal()">🛰️ NASA &amp; Partner Data Log</button>
        <button class="sb-btn" onclick="toggleJoystick()">🕹️ Toggle Mobile Joystick Handle</button>
        <button class="sb-btn" id="sb-music-btn" onclick="toggleMusic()">🎵 Music: ON</button>
        <button class="sb-btn" onclick="restartCurrentRun()">🔄 Restart Current Mission</button>
        <button class="sb-btn danger" onclick="quitAndResetGame()">🚪 Quit Game &amp; Reset Vault</button>
      </div>

      <div class="top-hud">
        <button class="sidebar-toggle-btn" onclick="toggleSidebar()" title="Menu (M)">
          <span style="font-size:16px;line-height:1;">☰</span>
          <span>MENU <span class="kbadge">M</span></span>
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
            <span class="hud-lbl">⚡ Pwr <span class="qchip" onclick="openGlossary('POWER')">?</span></span>
            <span class="hud-val" id="ui-pwr">95%</span>
          </div>
          <div class="bar-bg"><div id="bar-pwr" class="bar-fill" style="width:95%;background:#facc15;"></div></div>
          <div class="hud-sub" id="sub-pwr">☀️ Charging</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">🫁 O₂ <span class="qchip" onclick="openGlossary('OXYGEN')">?</span></span>
            <span class="hud-val" id="ui-ox">95%</span>
          </div>
          <div class="bar-bg"><div id="bar-ox" class="bar-fill" style="width:95%;background:#38bdf8;"></div></div>
          <div class="hud-sub" id="sub-ox">🔒 Sealed</div>
        </div>
        <div class="hud-card">
          <div class="hud-row">
            <span class="hud-lbl">🍽️ Food <span class="qchip" onclick="openGlossary('FOOD')">?</span></span>
            <span class="hud-val" id="ui-food">90%</span>
          </div>
          <div class="bar-bg"><div id="bar-food" class="bar-fill" style="width:90%;background:#4ade80;"></div></div>
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
            <span class="hud-val" style="font-size:13.5px;"><span id="ui-coins" style="color:#fde047;">40</span> | <span id="ui-sci" style="color:#d8b4fe;">0</span></span>
          </div>
          <div style="display:flex;gap:3px;margin-top:3px;">
            <button class="gbtn" id="hud-music-btn" style="flex:1;padding:2.5px;font-size:9.5px;" onclick="toggleMusic()">🔊 V</button>
            <button class="gbtn gbtn-cyan" style="flex:1;padding:2.5px;font-size:9.5px;" onclick="toggleJoystick()" title="Joystick Handle">🕹️ Pad</button>
          </div>
        </div>
      </div>

      <div class="ticker-bar">
        <span id="status-msg">🚀 Touchdown at Shackleton Crater! Explore the expanded Moon &amp; collect Vault Coins!</span>
        <button class="nasa-badge-btn" id="nasa-feed-btn" onclick="openNasaModal()">🛰️ NASA DONKI</button>
      </div>

      <div id="minimap-wrap">
        <div style="font-size:8.5px;font-weight:900;color:#7dd3fc;margin-bottom:2px;">📡 LUNAR RADAR</div>
        <canvas id="minimap" width="116" height="100"></canvas>
      </div>

      <div id="zoom-bar">
        <button class="zbtn" onclick="adjustZoom(-0.45)" title="Zoom In (X)">➕ <span class="kbadge">X</span></button>
        <button class="zbtn" onclick="adjustZoom(0.45)" title="Zoom Out (Z)">➖ <span class="kbadge">Z</span></button>
        <button class="zbtn" onclick="toggleFullMoonView()" title="Whole Moon View (C)">🌕 <span class="kbadge">C</span></button>
      </div>

      <div id="flare-alarm">
        <div style="font-size:11.5px;font-weight:900;color:#fde047;" id="flare-alarm-title">🚨 NASA DONKI FLARE!</div>
        <div style="font-size:10.5px;color:#fff;margin-top:2px;" id="flare-alarm-desc">Inside + Seal Airlock (E) + Shield (Q)!</div>
      </div>

      <div id="unlock-banner"></div>

      <div id="pad-progress-wrap">
        <span id="pad-progress-label" style="font-size:11.5px;font-weight:900;color:#4ade80;">⚡ Working...</span>
        <div id="pad-progress-bar-bg"><div id="pad-progress-bar"></div></div>
      </div>

      <div id="comic-toast">
        <div id="comic-badge" style="font-size:30px;line-height:1.1;">🛡️⚡</div>
        <div id="comic-title" style="font-size:12px;font-weight:900;color:#fde047;margin-top:2px;">SHIELD ONLINE!</div>
        <div id="comic-body" style="font-size:10.5px;color:#e2e8f0;margin-top:2px;">Blocking radiation!</div>
      </div>

      <div id="glossary-pop">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span id="gl-title" style="font-weight:900;color:#fde047;font-size:13.5px;">Science Decoder</span>
          <button onclick="closeGlossary()" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:2px 8px;font-weight:900;cursor:pointer;">✕</button>
        </div>
        <p id="gl-body" style="font-size:12px;color:#e2e8f0;margin:6px 0 0 0;line-height:1.42;"></p>
      </div>

      <div id="joy-wrap">
        <div id="joy-base"><div id="joy-knob"></div></div>
        <div class="joy-hint">MOVE HANDLE</div>
      </div>

      <div id="mobile-quick-pad">
        <button class="mq-btn" style="border-color:#38bdf8;" onclick="triggerJump()">⬆️<br>JUMP</button>
        <button class="mq-btn" style="border-color:#ef4444;" onclick="toggleShield()">🛡️<br>SHIELD</button>
        <button class="mq-btn" style="border-color:#4ade80;" onclick="toggleDoor()">🔒<br>DOOR</button>
      </div>

      <div class="bottom-dock">
        <div class="dock-panel">
          <div class="dock-title"><span>🏃 Auto-Run Stations</span><span style="color:#7dd3fc;">WASD / Arrows + Space</span></div>
          <div class="btn-grid-4" style="margin-bottom:4px;">
            <button class="gbtn gbtn-gold" onclick="autoRunTo('SOLAR')">☀️ Solar<span class="kbadge">1</span></button>
            <button class="gbtn gbtn-cyan" onclick="autoRunTo('ICE')">🧊 Ice<span class="kbadge">2</span></button>
            <button class="gbtn gbtn-purple" onclick="autoRunTo('SCIENCE')">🔬 Sci<span class="kbadge">3</span></button>
            <button class="gbtn gbtn-green" onclick="autoRunTo('FARM')">🌱 Farm<span class="kbadge">4</span></button>
          </div>
          <div class="btn-grid-3">
            <button class="gbtn" onclick="autoRunTo('PANTRY')">🍽️ Pantry<span class="kbadge">5</span></button>
            <button class="gbtn gbtn-red" onclick="autoRunTo('SHIELD')">🛡️ Console<span class="kbadge">6</span></button>
            <button class="gbtn" onclick="triggerJump()">⬆️ Jump<span class="kbadge">SPC</span></button>
          </div>
        </div>

        <div class="dock-panel hide-sm-panel">
          <div class="dock-title"><span>⚙️ Outpost Systems</span><span id="zone-badge" style="color:#4ade80;">📍 INSIDE BASE</span></div>
          <div class="btn-grid-2" style="margin-bottom:4px;">
            <button class="gbtn gbtn-red" id="btn-shield" onclick="toggleShield()">🛡️ Shield: OFF<span class="kbadge">Q</span></button>
            <button class="gbtn gbtn-green" id="btn-door" onclick="toggleDoor()">🔒 Airlock: SEALED<span class="kbadge">E</span></button>
          </div>
          <div class="btn-grid-2">
            <button class="gbtn gbtn-gold" onclick="deployRoverScan()">🚙 Rover<span class="kbadge">R</span></button>
            <button class="gbtn gbtn-cyan" onclick="advanceSolEarly()">🌙 Next Sol<span class="kbadge">N</span></button>
          </div>
        </div>

        <div class="dock-panel hide-sm-panel">
          <div class="dock-title"><span>📡 Earth HQ Radio <span class="qchip" onclick="openGlossary('DELAY')">?</span></span><span style="color:#7dd3fc;">384,400 km • 2.6s</span></div>
          <div class="btn-grid-5" style="margin-bottom:4px;">
            <button class="gbtn" onclick="callEarth(1)">⚡+30%<br><span class="kbadge">F</span></button>
            <button class="gbtn gbtn-cyan" onclick="callEarth(2)">🫁+30%<br><span class="kbadge">G</span></button>
            <button class="gbtn gbtn-green" onclick="callEarth(3)">🍅+30%<br><span class="kbadge">H</span></button>
            <button class="gbtn gbtn-red" onclick="callEarth(4)">❤️+30%<br><span class="kbadge">J</span></button>
            <button class="gbtn gbtn-gold" onclick="callEarth(5)">☀️Clr<br><span class="kbadge">K</span></button>
          </div>
          <div id="radio-log" style="font-size:9.8px;color:#fde047;font-weight:800;text-align:center;">
            15 🪙 per drop (Dr. Strange: 10 🪙 &amp; 1.0s)
          </div>
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
          <div id="debrief-icon" style="font-size:36px;">🏆</div>
          <h2 id="debrief-title" style="color:#fde047;font-size:20px;margin:3px 0;"></h2>
          <div id="debrief-rank" style="font-size:12.5px;font-weight:900;color:#4ade80;margin-bottom:4px;"></div>
          <p id="debrief-sub" style="font-size:12px;color:#cbd5e1;margin-bottom:6px;"></p>
          <canvas id="debrief-chart" width="600" height="135" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:11px;margin:5px 0;"></canvas>
          <div id="debrief-lesson" style="background:rgba(14,165,233,0.15);border:1.5px solid #38bdf8;border-radius:10px;padding:8px 11px;font-size:11.5px;color:#e0f2fe;text-align:left;line-height:1.4;margin-bottom:10px;"></div>
          <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
            <button class="menu-btn secondary" style="width:210px;margin:0;padding:10px;" onclick="debriefChangeHero()">🦸 Switch Hero (<span id="deb-vault">40</span> 🪙)</button>
            <button class="menu-btn" style="width:200px;margin:0;padding:10px;" onclick="restartCurrentRun()">🔄 Play Again</button>
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
          <canvas id="math-chart" width="600" height="165" style="width:100%;background:#020617;border:1.5px solid #334155;border-radius:11px;"></canvas>
          <div id="math-summary" style="margin-top:7px;font-size:11.5px;color:#93c5fd;font-weight:700;"></div>
        </div>
      </div>

      <div id="nasa-modal" class="modal-backdrop">
        <div class="modal-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;">
            <h3 style="color:#fde047;">🛰️ NASA &amp; Space Agency Partner Data</h3>
            <button onclick="closeModal('nasa-modal')" style="background:#ef4444;color:#fff;border:none;border-radius:8px;padding:4px 12px;font-weight:900;cursor:pointer;">Close ✕</button>
          </div>
          <div id="nasa-data-body" style="font-size:12px;line-height:1.52;color:#e2e8f0;"></div>
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
    key: "IRON", name: "Iron Man", unlockCoins: 1080,
    perk: "⚡ 2x Solar Charge & Jet Jumps",
    suit: "#dc2626", accent: "#facc15", eyes: "#38bdf8",
    head: "<rect x='30' y='18' width='60' height='54' rx='18' fill='#b91c1c' stroke='#facc15' stroke-width='3'/><polygon points='38,22 82,22 76,58 44,58' fill='#facc15'/><rect x='40' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/><rect x='66' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/>"
  },
  {
    key: "THOR", name: "Thor Odinson", unlockCoins: 1120,
    perk: "🔨 60% less Solar Flare Radiation",
    suit: "#475569", accent: "#ef4444", eyes: "#38bdf8",
    head: "<path d='M 24 58 Q 28 14 60 16 Q 92 14 96 58 L 86 34 Q 60 24 34 34 Z' fill='#facc15'/><path d='M 20 42 L 10 22 L 26 32 Z' fill='#cbd5e1'/><path d='M 100 42 L 110 22 L 94 32 Z' fill='#cbd5e1'/>"
  },
  {
    key: "STRANGE", name: "Dr. Strange", unlockCoins: 1160,
    perk: "⏳ 1.0s Radio Delay & 10 🪙 Drops",
    suit: "#1e3a8a", accent: "#dc2626", eyes: "#4ade80",
    head: "<path d='M 28 46 Q 30 16 60 16 Q 90 16 92 46 L 84 32 Q 60 22 36 32 Z' fill='#1e293b'/><path d='M 26 42 L 34 42' stroke='#e2e8f0' stroke-width='4'/><path d='M 86 42 L 94 42' stroke='#e2e8f0' stroke-width='4'/>"
  },
  {
    key: "WANDA", name: "Wanda Maximoff", unlockCoins: 1200,
    perk: "🔮 2x Crop Growth & +6% O₂ Bonus",
    suit: "#991b1b", accent: "#f43f5e", eyes: "#ef4444",
    head: "<path d='M 22 60 Q 26 16 60 16 Q 94 16 98 60 L 86 34 Q 60 24 34 34 Z' fill='#7c2d12'/><polygon points='42,38 50,18 60,30 70,18 78,38' fill='#ef4444' stroke='#fca5a5' stroke-width='1.5'/>"
  },
  {
    key: "LOKI", name: "Loki", unlockCoins: 1250,
    perk: "🐍 2x Vault Coins & +50% Science",
    suit: "#15803d", accent: "#eab308", eyes: "#22c55e",
    head: "<path d='M 22 58 Q 24 18 60 18 Q 96 18 98 58 Z' fill='#0f172a'/><path d='M 34 40 Q 60 50 86 40 L 82 28 Q 60 38 38 28 Z' fill='#eab308' stroke='#fef08a' stroke-width='1.5'/><path d='M 40 32 Q 22 6 44 4 Q 34 18 46 30 Z' fill='#eab308'/><path d='M 80 32 Q 98 6 76 4 Q 86 18 74 30 Z' fill='#eab308'/>"
  }
];

const LOAD_FACTS = [
  "Shackleton Crater at the Moon's South Pole has sunlit rims for solar power right next to shadowed craters filled with water-ice (H₂O) that can be split into breathable Oxygen!",
  "Even traveling at the speed of light (300,000 km/s), a radio message from a Lunar Outpost to Earth HQ and back takes 2.56 seconds across 384,400 km!",
  "Lunar gravity is only 1/6th of Earth's gravity—astronauts can leap six times higher on the Moon while electrostatic lunar dust clings to spacesuits and solar panels!",
  "NASA RadLab measurements show lunar surface radiation averages 0.42 mSv per Sol—over 50 times higher than a normal day on Earth!"
];

const GLOSSARY = {
  SOL: { title: "📅 What is a Lunar Sol?", body: "A Sol is one survival day-cycle on an off-world outpost. Survive all 7 Sols at Shackleton Crater while balancing Power, Oxygen, Food, and Radiation!" },
  POWER: { title: "⚡ Solar Power vs. Shielding", body: "Solar panels charge your batteries in calm skies unless covered in lunar dust. Raising the Radiation Shield protects against solar flares while drawing steady battery power." },
  OXYGEN: { title: "🫁 Airlock & Ice Electrolysis", body: "The Moon has no air. Leaving the Airlock Door open leaks Oxygen into space. Mine Shackleton Crater ice (H₂O) and split it with electricity to produce fresh O₂!" },
  FOOD: { title: "🌱 CSA 4-Crop Hydroponics", body: "Inspired by the Canadian Space Agency Deep Space Food Toolkit and NASA OSDR (OSD-767), your greenhouse grows Tomatoes, Lettuce, Radishes, and Potatoes without soil." },
  RAD: { title: "☢️ Radiation Dose (mSv)", body: "mSv (millisievert) measures radiation exposure. NASA RadLab BLEO sets lunar baseline around 0.42 mSv/Sol, spiking during unshielded NASA DONKI solar storms." },
  DELAY: { title: "📡 2.6-Second Light Delay", body: "Earth is 384,400 km away. Radio waves travel at light speed, creating a real 2.56-second round-trip delay when calling Earth Mission Control!" }
};

let session = {
  screen: "LOADER",
  age: null,
  ageTier: "10-12 Commander",
  heroKey: "CAP",
  vaultCoins: 40,
  unlocked: ["CAP", "WIDOW"],
  wins: 0,
  musicOn: true,
  joystickVisible: ("ontouchstart" in window) || (navigator.maxTouchPoints > 0) || (window.innerWidth <= 820)
};

function getHero(key) { return HEROES.find(h => h.key === (key || session.heroKey)) || HEROES[0]; }

function getDiff() {
  if (session.ageTier.includes("7-9")) return { drain: 0.48, solSecs: 30, flareWarn: 9.5, flareDur: 8.0, flareDmg: 4.0, flareGap: 16 };
  if (session.ageTier.includes("13+")) return { drain: 0.78, solSecs: 26, flareWarn: 7.5, flareDur: 9.5, flareDmg: 7.5, flareGap: 12 };
  return { drain: 0.62, solSecs: 28, flareWarn: 8.5, flareDur: 8.5, flareDmg: 5.5, flareGap: 14 };
}

let audioCtx = null, masterGain = null, musicTimer = null, musicBeat = 0;

const CHORDS = [
  { bass: 73.42, pad: [146.83, 220.00, 293.66, 349.23], lead: [587.33, 0, 523.25, 587.33, 659.25, 0, 587.33, 440.00] },
  { bass: 58.27, pad: [116.54, 174.61, 233.08, 293.66], lead: [466.16, 0, 523.25, 587.33, 700.00, 0, 659.25, 587.33] },
  { bass: 87.31, pad: [174.61, 220.00, 261.63, 349.23], lead: [698.46, 0, 659.25, 587.33, 523.25, 0, 587.33, 659.25] },
  { bass: 65.41, pad: [130.81, 196.00, 261.63, 329.63], lead: [523.25, 0, 587.33, 659.25, 783.99, 0, 659.25, 523.25] }
];

function ensureAudio() {
  if (!audioCtx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) {
      audioCtx = new AC();
      masterGain = audioCtx.createGain();
      masterGain.gain.value = 0.85;
      masterGain.connect(audioCtx.destination);
    }
  }
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
}

function playSynthVoice(freq, dur, type, vol, cutoff=1800, attack=0.02) {
  if (!session.musicOn || !freq) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const filt = audioCtx.createBiquadFilter();
    const g = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    filt.type = "lowpass";
    filt.frequency.setValueAtTime(cutoff, now);
    g.gain.setValueAtTime(0.0001, now);
    g.gain.linearRampToValueAtTime(vol, now + attack);
    g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.connect(filt); filt.connect(g); g.connect(masterGain);
    osc.start(now); osc.stop(now + dur + 0.02);
  } catch(e) {}
}

function playKick() {
  if (!session.musicOn) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(115, now);
    osc.frequency.exponentialRampToValueAtTime(36, now + 0.14);
    g.gain.setValueAtTime(0.065, now);
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.16);
    osc.connect(g); g.connect(masterGain);
    osc.start(now); osc.stop(now + 0.17);
  } catch(e) {}
}

function startHeroicSoundtrack() {
  clearInterval(musicTimer);
  musicTimer = setInterval(() => {
    if (!session.musicOn || session.screen === "LOADER") return;
    const bar = Math.floor(musicBeat / 8) % CHORDS.length;
    const step = musicBeat % 8;
    const ch = CHORDS[bar];

    if (step === 0) {
      ch.pad.forEach(n => playSynthVoice(n, 2.35, "sawtooth", 0.015, 720, 0.25));
    }
    if (step % 2 === 0) {
      playSynthVoice(ch.bass, 0.42, "triangle", 0.05, 360, 0.01);
    }
    if (step === 0 || step === 4 || step === 6) {
      playKick();
    }
    const leadNote = ch.lead[step];
    if (leadNote > 0) {
      playSynthVoice(leadNote, 0.38, "triangle", 0.028, 2200, 0.015);
    }
    musicBeat++;
  }, 290);
}

function playSfx(freq, dur=0.14, type="sine", vol=0.075, slideTo=null) {
  if (!session.musicOn) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const now = audioCtx.currentTime;
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, now);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, now + dur);
    g.gain.setValueAtTime(vol, now);
    g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    o.connect(g); g.connect(masterGain);
    o.start(now); o.stop(now + dur + 0.02);
  } catch(e) {}
}

function syncMusicButtons() {
  const lbl = session.musicOn ? "🎵 MUSIC: ON" : "🔇 MUSIC: OFF";
  document.getElementById("create-music-btn").innerText = lbl;
  document.getElementById("sb-music-btn").innerText = lbl;
  document.getElementById("hud-music-btn").innerText = session.musicOn ? "🔊 V" : "🔇 V";
}

function toggleMusic() {
  ensureAudio();
  session.musicOn = !session.musicOn;
  syncMusicButtons();
  if (session.musicOn) {
    playSfx(523.25, 0.18, "triangle", 0.08, 784);
    startHeroicSoundtrack();
  }
}

function syncJoystickVisibility() {
  document.getElementById("joy-wrap").classList.toggle("visible", session.joystickVisible);
  document.getElementById("mobile-quick-pad").classList.toggle("visible", session.joystickVisible);
}
function toggleJoystick() {
  session.joystickVisible = !session.joystickVisible;
  syncJoystickVisibility();
  playSfx(560, 0.1, "triangle", 0.06);
}

let joyX = 0, joyY = 0, joyPointerId = null;
const joyBase = document.getElementById("joy-base");
const joyKnob = document.getElementById("joy-knob");

function updateJoystickFromClient(cx, cy) {
  const rect = joyBase.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const maxR = rect.width * 0.38;
  let dx = cx - centerX;
  let dy = cy - centerY;
  const dist = Math.hypot(dx, dy);
  if (dist > maxR) {
    dx = (dx / dist) * maxR;
    dy = (dy / dist) * maxR;
  }
  joyKnob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
  joyX = dx / maxR;
  joyY = dy / maxR;
}

joyBase.addEventListener("pointerdown", e => {
  e.preventDefault();
  ensureAudio();
  joyPointerId = e.pointerId;
  joyBase.setPointerCapture(e.pointerId);
  updateJoystickFromClient(e.clientX, e.clientY);
});
joyBase.addEventListener("pointermove", e => {
  if (e.pointerId !== joyPointerId) return;
  e.preventDefault();
  updateJoystickFromClient(e.clientX, e.clientY);
});
function releaseJoystick(e) {
  if (e.pointerId !== joyPointerId) return;
  joyPointerId = null;
  joyX = 0; joyY = 0;
  joyKnob.style.transform = "translate(-50%, -50%)";
}
joyBase.addEventListener("pointerup", releaseJoystick);
joyBase.addEventListener("pointercancel", releaseJoystick);

const bgCanvas = document.getElementById("bg-space-canvas");
const bgCtx = bgCanvas.getContext("2d");
let bgStars = [];
function initBgStars() {
  bgCanvas.width = window.innerWidth || 1200;
  bgCanvas.height = window.innerHeight || 800;
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
  bgCtx.ellipse(w * 0.5, h + 110, w * 0.72, 210, 0, Math.PI, 0);
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
  document.getElementById("load-fact").innerText = LOAD_FACTS[Math.floor(Math.random() * LOAD_FACTS.length)];
  const steps = [
    "Connecting to NASA DONKI Space Weather Feed...",
    "Mapping Expanded Shackleton Crater Terrain...",
    "Loading 3D Avengers Lunar Suits & Hardware...",
    "Preparing CSA 4-Crop Hydroponic Greenhouse...",
    "Avengers Assemble — Ready for Launch!"
  ];
  const startT = performance.now();
  const duration = 5000;
  function tickLoader(now) {
    const elapsed = now - startT;
    const pct = Math.min(100, (elapsed / duration) * 100);
    document.getElementById("load-bar-fill").style.width = pct + "%";
    document.getElementById("load-pct").innerText = Math.floor(pct) + "%";
    document.getElementById("load-status").innerText = steps[Math.min(steps.length - 1, Math.floor((pct / 100) * steps.length))];
    if (elapsed < duration) requestAnimationFrame(tickLoader);
    else goToCreatePage();
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
    b.innerText = `🔓 NEW AVENGER UNLOCKED: ${newlyUnlocked.join(", ").toUpperCase()}!`;
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
      <rect x="0" y="0" width="120" height="140" rx="14" fill="rgba(2,6,23,0.8)"/>
      <text x="60" y="64" text-anchor="middle" fill="#fde047" font-size="26">🔒</text>
      <text x="60" y="94" text-anchor="middle" fill="#ffffff" font-size="11.5" font-weight="bold">${h.unlockCoins} 🪙</text>
    `;
    card.innerHTML = `
      <svg width="80" height="92" viewBox="0 0 120 140">
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
  startHeroicSoundtrack();
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

const WORLD_LIMIT_X = 48;
const WORLD_LIMIT_Z = 44;

const STATIONS = {
  SOLAR:   { x: -18.0, z: 8.5,   r: 3.4, label: "☀️ Scrubbing Solar Dust...", color: 0xfacc15, tag: "☀️ SOLAR ARRAY" },
  ICE:     { x: -15.5, z: -14.0, r: 3.4, label: "🧊 Mining Crater Ice (+O₂, -⚡)...", color: 0x38bdf8, tag: "🧊 ICE CRATER" },
  SCIENCE: { x: 16.5,  z: 14.5,  r: 3.4, label: "🔬 Drilling Lunar Core (-O₂, +Sci)...", color: 0xd8b4fe, tag: "🔬 EVA SCIENCE" },
  FARM:    { x: 17.5,  z: -4.0,  r: 3.6, label: "🌱 Harvesting CSA Crops...", color: 0x4ade80, tag: "🌱 CSA FARM" },
  PANTRY:  { x: 2.3,   z: -1.2,  r: 2.2, label: "🍽️ Stocking Pantry Table...", color: 0xf472b6, tag: "🍽️ PANTRY" },
  SHIELD:  { x: -2.4,  z: -1.4,  r: 2.1, label: "🛡️ Shield Console", color: 0x60a5fa, tag: "🛡️ SHIELD" }
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
    power: 96,
    oxygen: 96,
    food: 92,
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
    crops: [100, 100, 75, 100],
    autoTarget: null,
    activePad: null,
    padProgress: 0,
    shieldPadLatched: false,
    roverCooldown: 0,
    radioBusy: false,
    radioBeamTimer: 0,
    camZoom: 1.0,
    fullMoonMode: false,
    dilemmasShown: {}
  };
  telemetryLog = [{ sol: 1, pwr: 96, ox: 96, hp: 100 }];
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
  for (let i = 0; i < 6500; i++) {
    const shade = 75 + Math.floor(Math.random() * 55);
    ctx.fillStyle = `rgb(${shade},${shade+6},${shade+16})`;
    ctx.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
  }
  for (let i = 0; i < 50; i++) {
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
  tex.repeat.set(12, 12);
  return tex;
}

function makeFloatingLabel(text, borderHex) {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 64;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "rgba(9,13,31,0.88)";
  ctx.strokeStyle = borderHex;
  ctx.lineWidth = 5;
  ctx.beginPath(); ctx.roundRect(6, 8, 244, 48, 14); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#ffffff";
  ctx.font = "900 20px Segoe UI, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(text, 128, 40);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true }));
  sprite.scale.set(5.4, 1.35, 1);
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
  const w = container.clientWidth || window.innerWidth;
  const h = container.clientHeight || window.innerHeight;

  heroPos = new THREE.Vector3(0, 0, 1.5);
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  scene.fog = new THREE.FogExp2(0x04091a, 0.0042);

  camera = new THREE.PerspectiveCamera(52, w / h, 0.1, 480);
  camera.position.set(0, 15, 22);

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  clock = new THREE.Clock();

  scene.add(new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.72));
  dirLight = new THREE.DirectionalLight(0xfff7ed, 1.55);
  dirLight.position.set(-48, 52, 28);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(1024, 1024);
  const d = 52;
  dirLight.shadow.camera.left = -d; dirLight.shadow.camera.right = d;
  dirLight.shadow.camera.top = d; dirLight.shadow.camera.bottom = -d;
  scene.add(dirLight);

  beaconLight = new THREE.PointLight(0x38bdf8, 1.2, 18);
  beaconLight.position.set(0, 4.5, 0);
  scene.add(beaconLight);

  const starGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(2000 * 3);
  const starCol = new Float32Array(2000 * 3);
  for (let i = 0; i < 2000; i++) {
    const r = 130 + Math.random() * 140;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(Math.random() * 1.6 - 0.8);
    starPos[i*3] = r * Math.sin(phi) * Math.cos(theta);
    starPos[i*3+1] = r * Math.cos(phi);
    starPos[i*3+2] = r * Math.sin(phi) * Math.sin(theta);
    starCol[i*3] = Math.random() > 0.7 ? 1.0 : 0.82;
    starCol[i*3+1] = 0.92;
    starCol[i*3+2] = 1.0;
  }
  starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute("color", new THREE.BufferAttribute(starCol, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ size: 0.75, vertexColors: true })));

  shootingStar = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.24, 5.2), new THREE.MeshBasicMaterial({ color: 0xbae6fd }));
  shootingStar.position.set(-70, 48, -80);
  scene.add(shootingStar);

  sunMesh = new THREE.Mesh(new THREE.SphereGeometry(8.5, 24, 24), new THREE.MeshBasicMaterial({ color: 0xfde047 }));
  sunMesh.position.set(-85, 58, -78);
  scene.add(sunMesh);
  sunGlow = new THREE.Mesh(new THREE.SphereGeometry(12.5, 24, 24), new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.26, depthWrite: false }));
  sunGlow.position.copy(sunMesh.position);
  scene.add(sunGlow);

  earthGroup = new THREE.Group();
  earthGroup.position.set(68, 52, -88);
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(8.5, 28, 28), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.5 })));
  const landMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8 });
  [[-3.0, 2.2, 7.2, 3.2], [3.5, -1.4, 6.8, 2.8], [0.4, 4.8, -6.2, 3.0], [-4.2, -3.2, -5.6, 2.6]].forEach(c => {
    const patch = new THREE.Mesh(new THREE.SphereGeometry(c[3], 12, 12), landMat);
    patch.position.set(c[0], c[1], c[2]); patch.scale.set(1, 0.8, 0.5);
    earthGroup.add(patch);
  });
  earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(9.2, 24, 24), new THREE.MeshBasicMaterial({ color: 0x60a5fa, transparent: true, opacity: 0.18, depthWrite: false })));
  scene.add(earthGroup);

  const lunarTex = makeLunarTexture();
  const moonDiskGeo = new THREE.CircleGeometry(68, 64);
  moonDiskGeo.rotateX(-Math.PI / 2);
  const ground = new THREE.Mesh(
    moonDiskGeo,
    new THREE.MeshStandardMaterial({ map: lunarTex, roughness: 0.94, metalness: 0.05 })
  );
  ground.receiveShadow = true;
  scene.add(ground);

  const moonSphereBody = new THREE.Mesh(
    new THREE.SphereGeometry(72, 40, 28),
    new THREE.MeshStandardMaterial({ map: lunarTex, color: 0x475569, roughness: 0.96 })
  );
  moonSphereBody.position.set(0, -24.5, 0);
  scene.add(moonSphereBody);

  const rimRing = new THREE.Mesh(
    new THREE.TorusGeometry(56, 2.2, 10, 48),
    new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.95 })
  );
  rimRing.rotation.x = Math.PI / 2;
  rimRing.position.y = 0.6;
  scene.add(rimRing);

  const rockMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 });
  [
    [-32, 22], [-36, -18], [34, 24], [38, -22], [10, 34], [-14, -36],
    [28, -32], [-26, 30], [42, 4], [-42, -4], [0, -40], [22, 32], [-30, -30], [36, 12]
  ].forEach(([rx, rz]) => {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.4 + Math.random() * 1.9, 0), rockMat);
    rock.position.set(rx, 0.7, rz); rock.rotation.set(Math.random(), Math.random(), 0);
    rock.castShadow = true; rock.receiveShadow = true;
    scene.add(rock);
  });

  function addCraterRing(cx, cz, rad) {
    const cr = new THREE.Mesh(
      new THREE.TorusGeometry(rad, 0.55, 8, 24),
      new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 })
    );
    cr.rotation.x = Math.PI / 2; cr.position.set(cx, 0.15, cz);
    scene.add(cr);
  }
  addCraterRing(-32, -26, 6.5);
  addCraterRing(32, -26, 7.2);
  addCraterRing(-34, 26, 5.8);
  addCraterRing(30, 28, 6.2);
  addCraterRing(0, -32, 5.0);

  function addPath(x1, z1, x2, z2, col) {
    const len = Math.hypot(x2 - x1, z2 - z1);
    const p = new THREE.Mesh(new THREE.PlaneGeometry(len, 1.25), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.28, depthWrite: false }));
    p.rotation.x = -Math.PI / 2;
    p.rotation.z = -Math.atan2(z2 - z1, x2 - x1);
    p.position.set((x1 + x2) / 2, 0.04, (z1 + z2) / 2);
    scene.add(p);
  }
  addPath(0, 6.2, STATIONS.SOLAR.x, STATIONS.SOLAR.z, 0xfacc15);
  addPath(0, 6.2, STATIONS.ICE.x, STATIONS.ICE.z, 0x38bdf8);
  addPath(0, 6.2, STATIONS.SCIENCE.x, STATIONS.SCIENCE.z, 0xd8b4fe);
  addPath(5.5, -1.5, STATIONS.FARM.x, STATIONS.FARM.z, 0x4ade80);

  const habFloor = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.2, 0.22, 32), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.45, metalness: 0.4 }));
  habFloor.position.set(0, 0.11, 0); habFloor.receiveShadow = true;
  scene.add(habFloor);

  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.0, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.5),
    new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.16, roughness: 0.1, side: THREE.DoubleSide, depthWrite: false })
  ));
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.06, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.5),
    new THREE.MeshBasicMaterial({ color: 0xe2e8f0, wireframe: true, transparent: true, opacity: 0.34, depthWrite: false })
  ));
  const habLbl = makeFloatingLabel("🏠 ARTEMIS HABITAT", "#38bdf8");
  habLbl.position.set(0, 7.4, 0);
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
    new THREE.CylinderGeometry(0.22, 0.55, beamDir.length(), 10),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85, depthWrite: false })
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
    new THREE.SphereGeometry(8.0, 28, 18, 0, Math.PI * 2, 0, Math.PI * 0.52),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false })
  );
  shieldWireMesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(8.18, 2),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, wireframe: true, transparent: true, opacity: 0.42, depthWrite: false })
  );
  shieldDomeMesh.visible = false; shieldWireMesh.visible = false;
  scene.add(shieldDomeMesh, shieldWireMesh);

  for (let i = 0; i < 4; i++) {
    const px = STATIONS.SOLAR.x - 3.3 + i * 2.2, pz = STATIONS.SOLAR.z - 1.2 + (i % 2) * 2.0;
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 1.8, 8), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
    pole.position.set(px, 0.9, pz); scene.add(pole);
    const panel = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.12, 2.4), new THREE.MeshStandardMaterial({ color: 0x1d4ed8, emissive: 0x1e3a8a, emissiveIntensity: 0.35, metalness: 0.6 }));
    panel.position.set(px, 1.9, pz); panel.rotation.x = 0.32; panel.castShadow = true; scene.add(panel);
    const dust = new THREE.Mesh(new THREE.BoxGeometry(1.92, 0.14, 2.42), new THREE.MeshStandardMaterial({ color: 0xa16207, transparent: true, opacity: 0.88 }));
    dust.position.set(px, 1.95, pz); dust.rotation.x = 0.32; dust.visible = false; scene.add(dust);
    solarDustMeshes.push(dust);
  }
  const sLbl = makeFloatingLabel("☀️ SOLAR ARRAY [1]", "#facc15"); sLbl.position.set(STATIONS.SOLAR.x, 4.6, STATIONS.SOLAR.z); scene.add(sLbl);

  const iceMat = new THREE.MeshStandardMaterial({ color: 0x7dd3fc, emissive: 0x0284c7, emissiveIntensity: 0.65, roughness: 0.15 });
  [[0, 0, 1.9], [1.4, -0.8, 1.25], [-1.3, 0.6, 1.4], [0.2, 1.4, 1.0]].forEach(([ox, oz, h]) => {
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.6, h, 6), iceMat);
    c.position.set(STATIONS.ICE.x + ox, h / 2 - 0.1, STATIONS.ICE.z + oz); c.castShadow = true; scene.add(c);
  });
  const iLbl = makeFloatingLabel("🧊 CRATER ICE [2]", "#38bdf8"); iLbl.position.set(STATIONS.ICE.x, 4.1, STATIONS.ICE.z); scene.add(iLbl);

  const sciBase = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 2.1, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x3b0764, metalness: 0.5 }));
  sciBase.position.set(STATIONS.SCIENCE.x, 0.18, STATIONS.SCIENCE.z); scene.add(sciBase);
  const drillTower = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.34, 2.8, 8), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.7 }));
  drillTower.position.set(STATIONS.SCIENCE.x, 1.5, STATIONS.SCIENCE.z); drillTower.castShadow = true; scene.add(drillTower);
  drillCrystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.7, 0), new THREE.MeshStandardMaterial({ color: 0xd8b4fe, emissive: 0xa855f7, emissiveIntensity: 0.8 }));
  drillCrystal.position.set(STATIONS.SCIENCE.x, 3.3, STATIONS.SCIENCE.z); scene.add(drillCrystal);
  const sciLbl = makeFloatingLabel("🔬 EVA SCIENCE [3]", "#d8b4fe"); sciLbl.position.set(STATIONS.SCIENCE.x, 4.9, STATIONS.SCIENCE.z); scene.add(sciLbl);

  const ghDome = new THREE.Mesh(new THREE.SphereGeometry(4.6, 20, 14, 0, Math.PI * 2, 0, Math.PI * 0.5), new THREE.MeshStandardMaterial({ color: 0x4ade80, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false }));
  ghDome.position.set(STATIONS.FARM.x, 0, STATIONS.FARM.z); scene.add(ghDome);
  const ghWire = new THREE.Mesh(new THREE.SphereGeometry(4.66, 10, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), new THREE.MeshBasicMaterial({ color: 0x86efac, wireframe: true, transparent: true, opacity: 0.36, depthWrite: false }));
  ghWire.position.set(STATIONS.FARM.x, 0, STATIONS.FARM.z); scene.add(ghWire);
  const gLbl = makeFloatingLabel("🌱 CSA FARM [4]", "#4ade80"); gLbl.position.set(STATIONS.FARM.x, 5.5, STATIONS.FARM.z); scene.add(gLbl);

  const cropColors = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  [[-1.3, -1.1], [1.3, -1.1], [-1.3, 1.1], [1.3, 1.1]].forEach(([ox, oz], idx) => {
    const bed = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.35, 1.4), new THREE.MeshStandardMaterial({ color: 0x451a03 }));
    bed.position.set(STATIONS.FARM.x + ox, 0.18, STATIONS.FARM.z + oz); scene.add(bed);
    const plant = new THREE.Group(); plant.position.set(STATIONS.FARM.x + ox, 0.4, STATIONS.FARM.z + oz);
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
      new THREE.MeshBasicMaterial({ color: st.color, side: THREE.DoubleSide, transparent: true, opacity: 0.8, depthWrite: false })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(st.x, 0.08, st.z);
    scene.add(ring);
    padRings[key] = ring;
  });

  roverGroup = new THREE.Group();
  const rBody = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.65, 1.3), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.4 }));
  rBody.position.y = 0.62; rBody.castShadow = true; roverGroup.add(rBody);
  const wMat = new THREE.MeshStandardMaterial({ color: 0x0f172a });
  [[-0.75, 0.7], [0.75, 0.7], [-0.75, -0.7], [0.75, -0.7]].forEach(([wx, wz]) => {
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.25, 12), wMat);
    wh.rotation.x = Math.PI / 2; wh.position.set(wx, 0.34, wz); roverGroup.add(wh);
  });
  roverGroup.position.set(0, 0, 22);
  scene.add(roverGroup);

  const coinPositions = [
    [-9, 12], [8, 12], [-22, -2], [25, 8], [-6, -18], [12, -16],
    [-28, 16], [28, -16], [-32, -8], [34, 2], [0, 26], [0, -26],
    [-18, 28], [20, 28], [-24, -28], [24, -28], [-38, 8], [38, -8]
  ];
  coinPositions.forEach(([cx, cz]) => {
    const coin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.62, 0.62, 0.18, 16),
      new THREE.MeshStandardMaterial({ color: 0xfacc15, emissive: 0xca8a04, emissiveIntensity: 0.75, metalness: 0.7 })
    );
    coin.rotation.x = Math.PI / 2; coin.position.set(cx, 1.15, cz);
    coin.userData = { active: true, respawn: 0 };
    scene.add(coin); coinOrbs.push(coin);
  });

  const fpGeo = new THREE.BufferGeometry();
  const fpPos = new Float32Array(360 * 3);
  for (let i = 0; i < 360; i++) {
    fpPos[i*3] = (Math.random() - 0.5) * 95;
    fpPos[i*3+1] = Math.random() * 34;
    fpPos[i*3+2] = (Math.random() - 0.5) * 95;
  }
  fpGeo.setAttribute("position", new THREE.BufferAttribute(fpPos, 3));
  flareParticles = new THREE.Points(fpGeo, new THREE.PointsMaterial({ color: 0xff4500, size: 0.55, transparent: true, opacity: 0.92 }));
  flareParticles.visible = false;
  scene.add(flareParticles);

  buildHero3D();
  threeReady = true;
  setupCanvasZoomGestures();
  animate3D();
}

function adjustZoom(delta) {
  state.fullMoonMode = false;
  state.camZoom = Math.max(0.65, Math.min(4.6, state.camZoom + delta));
  playSfx(520, 0.06, "sine", 0.04);
}

function toggleFullMoonView() {
  state.fullMoonMode = !state.fullMoonMode;
  state.camZoom = state.fullMoonMode ? 4.4 : 1.0;
  playSfx(state.fullMoonMode ? 440 : 660, 0.12, "triangle", 0.06);
  setStatus(state.fullMoonMode ? "🌕 Whole Moon Orbital View! Press C or ➕ to zoom back to your Avenger." : "🎥 Returned to third-person Avenger camera.");
}

function setupCanvasZoomGestures() {
  const cont = document.getElementById("canvas-container");
  cont.addEventListener("wheel", e => {
    if (session.screen !== "GAME") return;
    e.preventDefault();
    adjustZoom(e.deltaY > 0 ? 0.25 : -0.25);
  }, { passive: false });

  let pinchStartDist = null;
  cont.addEventListener("touchstart", e => {
    if (e.touches.length === 2) {
      pinchStartDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
    }
  }, { passive: true });
  cont.addEventListener("touchmove", e => {
    if (e.touches.length === 2 && pinchStartDist) {
      const dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      const diff = (pinchStartDist - dist) * 0.008;
      state.fullMoonMode = false;
      state.camZoom = Math.max(0.65, Math.min(4.6, state.camZoom + diff));
      pinchStartDist = dist;
    }
  }, { passive: true });
  cont.addEventListener("touchend", () => { pinchStartDist = null; }, { passive: true });
}

function resize3D() {
  if (!threeReady) return;
  const container = document.getElementById("canvas-container");
  const w = container.clientWidth || window.innerWidth;
  const h = container.clientHeight || window.innerHeight;
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
    new THREE.MeshBasicMaterial({ color: colorHex, transparent: true, opacity: 0.75, depthWrite: false })
  );
  puff.position.set(x, y, z);
  puff.userData = { life: 0.42 };
  scene.add(puff);
  fxParticles.push(puff);
}

function launchGameScreen() {
  ensureAudio();
  startHeroicSoundtrack();
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
  syncJoystickVisibility();
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
      setStatus(`🚀 Mission Live as ${h.name}! Use WASD/Joystick, Q=Shield, E=Airlock, 1-6=Stations, C=Whole Moon!`);
      document.getElementById("game-root").focus();
    } else {
      setTimeout(boot3D, 120);
    }
  }
  boot3D();
}

function toggleSidebar() {
  document.getElementById("game-sidebar").classList.toggle("open");
  syncVaultDisplays();
}
function sidebarChangeAgeHero() { goToAgePage(); }
function sidebarGoInstructions() { state.paused = true; document.getElementById("game-sidebar").classList.remove("open"); goToInstructions(); }
function restartCurrentRun() { launchGameScreen(); }
function debriefChangeHero() { document.getElementById("debrief-modal").style.display = "none"; goToAgePage(); }

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
  if (!state.ended && document.getElementById("dilemma-modal").style.display !== "flex") state.paused = false;
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
  let p = 96, o = 96, r = 0.42;
  for (let s = 1; s <= 7; s++) {
    const solarIn = 32 * (1 - ds / 100);
    p = Math.max(0, Math.min(100, p + solarIn - (sh * 0.30 + fm * 0.14 + ev * 1.4 + 4)));
    o = Math.max(0, Math.min(100, o + fm * 0.14 - (7.5 + ev * 2.2)));
    r += 0.42 + ev * 0.08 + ((s === 3 || s === 6) ? 1.8 * (1 - sh / 100) : 0);
    pts.push({ p, o, r });
  }
  const c = document.getElementById("math-chart");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  for (let y = 24; y <= 146; y += 30.5) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif";
  ctx.fillText("100%", 6, 27); ctx.fillText("50%", 12, 88); ctx.fillText("0%", 18, 149);
  function plot(k, col) {
    ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath();
    pts.forEach((pt, idx) => {
      const x = 45 + (idx / 6) * 525;
      const y = 146 - (pt[k] / 100) * 122;
      if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
  plot("p", "#facc15"); plot("o", "#38bdf8");
  ctx.fillStyle = "#facc15"; ctx.fillText("■ Projected Power %", 350, 15);
  ctx.fillStyle = "#38bdf8"; ctx.fillText("■ Projected Oxygen %", 475, 15);
  const last = pts[6];
  document.getElementById("math-summary").innerText =
    `Projected Sol 7 Status: Power ${Math.round(last.p)}% | Oxygen ${Math.round(last.o)}% | Cumulative Radiation ${last.r.toFixed(2)} mSv`;
}

const DILEMMAS = {
  2: {
    title: "🔬 Deep Crater Discovery: Oxygen vs. Research!",
    desc: "Orbital radar spotted ancient volcanic glass and frozen water-ice deeper inside Shackleton Crater! Drilling takes heavy EVA exertion.",
    choices: [
      {
        label: "A) Run Deep EVA Core Drill",
        tradeoff: "Cost: -12% 🫁 O₂ & +0.20 mSv  |  Reward: +300 🔬 Science & +60 🪙 Vault Coins",
        apply: () => { state.oxygen = Math.max(8, state.oxygen - 12); state.rad += 0.20; state.science += 300; addVaultCoins(60); setStatus("🔬 Deep EVA succeeded! +300 Science & +60 Vault Coins!"); }
      },
      {
        label: "B) Send Autonomous Rover Camera Instead",
        tradeoff: "Cost: -9% ⚡ Power  |  Reward: +120 🔬 Science & +30 🪙 Vault Coins",
        apply: () => { state.power = Math.max(8, state.power - 9); state.science += 120; addVaultCoins(30); setStatus("🚙 Rover scan saved Oxygen! +120 Science & +30 Vault Coins."); }
      }
    ]
  },
  4: {
    title: `🌊 NASA DONKI CME Alert (${NASA.cme.speed} km/s): Shield vs. Greenhouse!`,
    desc: `NASA DONKI logged Coronal Mass Ejection ${NASA.cme.id}! Peak power cannot max out both magnetic shielding and CSA Greenhouse grow-lights tonight.`,
    choices: [
      {
        label: "A) Reinforce Magnetic Dome Shielding",
        tradeoff: "Cost: -14% ⚡ Power & -8% 🍽️ Food  |  Reward: Blocks CME & +50 🪙 Vault Coins",
        apply: () => { state.power = Math.max(8, state.power - 14); state.food = Math.max(10, state.food - 8); state.science += 100; addVaultCoins(50); state.flarePhase = "CALM"; state.flareTimer = 15; setStatus("🛡️ CME deflected! +50 Vault Coins."); }
      },
      {
        label: "B) Prioritize CSA Greenhouse Grow-Lights",
        tradeoff: "Cost: +0.75 mSv & -10% ❤️ HP  |  Reward: +22% 🍽️ Food, +15% 🫁 O₂ & +40 🪙",
        apply: () => { state.rad += 0.75; state.hp = Math.max(12, state.hp - 10); state.food = Math.min(100, state.food + 22); state.oxygen = Math.min(100, state.oxygen + 15); addVaultCoins(40); setStatus("🌱 Greenhouse thrived (+22% Food)!"); }
      }
    ]
  },
  6: {
    title: "📡 Micrometeoroid Hit Solar Inverter — Comms Delay Choice!",
    desc: "A tiny space rock cracked an inverter outside! Earth HQ is 384,400 km away (2.6s light delay). How will you respond?",
    choices: [
      {
        label: "A) Rush Outside for Manual EVA Patch",
        tradeoff: "Cost: -10% 🫁 O₂ & +0.16 mSv  |  Reward: +18% ⚡ Power, +180 🔬 & +60 🪙",
        apply: () => { state.oxygen = Math.max(8, state.oxygen - 10); state.rad += 0.16; state.power = Math.min(100, state.power + 18); state.science += 180; addVaultCoins(60); setStatus("🛠️ EVA repair restored +18% Power & +60 Vault Coins!"); }
      },
      {
        label: "B) Wait for Earth HQ Remote Software Reroute",
        tradeoff: "Cost: -12% ⚡ Power drained while waiting  |  Reward: Zero Risk & +45 🪙 Vault Coins",
        apply: () => { state.power = Math.max(8, state.power - 12); addVaultCoins(45); setStatus("📡 Earth HQ rerouted power safely! +45 Vault Coins."); }
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
    btn.innerHTML = `<div style="font-size:13px;font-weight:900;color:#fde047;">${ch.label}</div>
                     <div style="font-size:11px;color:#93c5fd;margin-top:3px;font-weight:700;">${ch.tradeoff}</div>`;
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

function showComic(badge, title, body, ms=2200) {
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
  if (heroPos && heroPos.y <= 0.02) {
    heroVelY = (session.heroKey === "IRON") ? 8.8 : 6.8;
    playSfx(260, 0.22, "sine", 0.08, 540);
    spawnFxPuff(heroPos.x, 0.3, heroPos.z, 0x38bdf8, 0.45);
  }
}

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
  if (!state.shieldOn && state.power < 6) {
    setStatus("⚠️ Battery Power too low for Vibranium Shield! Scrub Solar Array [1] or call Earth HQ [F]!");
    playSfx(180, 0.2, "sawtooth", 0.08);
    return;
  }
  state.shieldOn = !state.shieldOn;
  if (state.shieldOn) {
    const cost = (session.heroKey === "CAP") ? 3 : 6;
    state.power = Math.max(0, state.power - cost);
    playSfx(320, 0.28, "sawtooth", 0.075, 760);
    showComic("🛡️⚡", "VIBRANIUM SHIELD ON!", "Blocking NASA DONKI radiation! Press Q to turn OFF after storm.");
    setStatus(`🛡️ Shield RAISED (-${cost}% startup Power)! Press Q to turn OFF after the flare.`);
  } else {
    playSfx(540, 0.18, "sine", 0.07, 260);
    setStatus("🟢 Shield turned OFF! Solar arrays are recharging battery power.");
  }
  updateHUD();
}

function deployRoverScan() {
  if (session.screen !== "GAME" || state.ended || state.paused) return;
  if (state.roverCooldown > 0) { setStatus(`🚙 Rover recharging... ready in ${Math.ceil(state.roverCooldown)}s.`); return; }
  if (state.power < 4) { setStatus("⚠️ Need 4% Power for a Lunar Rover scan!"); return; }
  state.power = Math.max(0, state.power - 4);
  const gain = (session.heroKey === "LOKI") ? 70 : 35;
  addVaultCoins(gain);
  state.science += 50;
  state.roverCooldown = 9;
  playSfx(740, 0.22, "triangle", 0.08, 980);
  showComic("🚙🪙", "ROVER SCAN COMPLETE!", `+${gain} Vault Coins & +50 Science (-4% Power)!`, 2000);
  setStatus(`🚙 Rover mapped crater rim: +${gain} 🪙 added to Vault!`);
}

function callEarth(preset) {
  if (session.screen !== "GAME" || state.ended || state.paused || state.radioBusy) return;
  const cost = (session.heroKey === "STRANGE") ? 10 : 15;
  const delayMs = (session.heroKey === "STRANGE") ? 1000 : 2600;
  if (session.vaultCoins < cost) {
    document.getElementById("radio-log").innerText = `⚠️ Need ${cost} 🪙! Grab spinning Moon Coins or press R for Rover!`;
    playSfx(210, 0.15, "sawtooth", 0.06);
    return;
  }
  session.vaultCoins -= cost;
  syncVaultDisplays();
  state.radioBusy = true;
  state.radioBeamTimer = delayMs / 1000;
  playSfx(440, 0.15, "sine", 0.08, 880);
  document.getElementById("radio-log").innerText = `📡 Signal beamed 384,400 km to Earth HQ... (${(delayMs / 1000).toFixed(1)}s delay)`;

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
    state.power = Math.min(100, state.power + 28);
    const g = 22 * coinMult;
    addVaultCoins(g);
    playSfx(784, 0.2, "triangle", 0.09, 1046);
    showComic("🧹☀️", "SOLAR ARRAY CLEAN!", `+28% Power & +${g} 🪙 Vault Coins!`, 1900);
    setStatus(`🧹 Swept lunar dust off Solar Array! +${g} 🪙 added to Vault.`);
  } else if (key === "ICE") {
    if (state.power < 7) { setStatus("⚠️ Need at least 7% ⚡ Power to run Ice Electrolysis!"); return; }
    state.power = Math.max(0, state.power - 7);
    state.oxygen = Math.min(100, state.oxygen + 30);
    const g = 18 * coinMult;
    addVaultCoins(g);
    playSfx(620, 0.22, "sine", 0.08, 920);
    showComic("🧊🫁", "ICE ELECTROLYSIS!", `+30% O₂ & +${g} 🪙 Vault Coins (-7% Power)!`, 1900);
    setStatus(`🫁 Melted Crater Ice (+30% O₂) & earned +${g} 🪙 Vault Coins!`);
  } else if (key === "SCIENCE") {
    if (state.oxygen < 14 || state.power < 7) {
      setStatus("⚠️ Too risky! Need ≥14% 🫁 O₂ & ≥7% ⚡ Power for EVA Core Drilling!");
      playSfx(200, 0.2, "sawtooth", 0.08);
      return;
    }
    const sciGain = (session.heroKey === "LOKI") ? 300 : 200;
    const g = 40 * coinMult;
    state.oxygen = Math.max(0, state.oxygen - 10);
    state.power = Math.max(0, state.power - 5);
    state.rad += 0.14;
    state.science += sciGain;
    addVaultCoins(g);
    playSfx(520, 0.25, "sawtooth", 0.07, 1040);
    spawnFxPuff(STATIONS.SCIENCE.x, 1.5, STATIONS.SCIENCE.z, 0xd8b4fe, 0.65);
    showComic("🔬🌕", "CORE SAMPLE DRILLED!", `+${sciGain} Science & +${g} 🪙 Vault Coins (-10% O₂)!`, 2200);
    setStatus(`🔬 Drilled regolith core (+${sciGain} Science, +${g} 🪙 Vault Coins)!`);
  } else if (key === "FARM") {
    const icons = ["🍅", "🥬", "🥕", "🥔"];
    let picked = 0;
    for (let i = 0; i < 4; i++) {
      if (state.crops[i] >= 95 && state.basket.length < 4) {
        state.basket.push(icons[i]); state.crops[i] = 5;
        state.power = Math.max(0, state.power - 1.5);
        state.oxygen = Math.min(100, state.oxygen + (session.heroKey === "WANDA" ? 6 : 2.5));
        picked++;
      }
    }
    if (picked > 0) {
      refreshBasketVisuals();
      playSfx(698, 0.18, "sine", 0.09, 987);
      showComic("🧺🍅🥬", "CSA HARVEST!", `Picked ${picked} fresh crops! Press 5 to Stock Pantry!`, 1900);
      setStatus(`🧺 Harvested ${picked} CSA crops into your Basket! Press 5 to run to Pantry.`);
    } else if (state.basket.length >= 4) {
      setStatus("🧺 Basket full (4/4)! Press 5 to run to the Pantry Table inside!");
    } else {
      setStatus("🌱 Space veggies still growing under hydroponic LEDs...");
    }
  } else if (key === "PANTRY") {
    if (state.basket.length === 0) { setStatus("🧺 Basket empty! Press 4 to harvest ripe crops in CSA Farm."); return; }
    const n = state.basket.length;
    state.basket = [];
    state.pantryCount = Math.min(6, state.pantryCount + n);
    state.food = Math.min(100, state.food + n * 15);
    const g = n * 18 * coinMult;
    addVaultCoins(g);
    state.science += n * 25;
    refreshBasketVisuals(); refreshPantryVisuals();
    playSfx(880, 0.25, "triangle", 0.09, 1320);
    showComic("🍽️✨", "PANTRY STOCKED!", `+${n*15}% Food & +${g} 🪙 Vault Coins!`, 1900);
    setStatus(`🍽️ Stocked Pantry Table! +${g} 🪙 added to your Vault.`);
  } else if (key === "SHIELD") {
    if (!state.shieldPadLatched) {
      state.shieldPadLatched = true;
      toggleShield();
    }
  }
}

function drawMinimap() {
  const c = document.getElementById("minimap");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  if (!heroPos) return;
  const mx = x => (x + WORLD_LIMIT_X + 4) / ((WORLD_LIMIT_X + 4) * 2) * c.width;
  const mz = z => (z + WORLD_LIMIT_Z + 4) / ((WORLD_LIMIT_Z + 4) * 2) * c.height;

  ctx.strokeStyle = "rgba(148,163,184,0.35)"; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(c.width / 2, c.height / 2, c.height * 0.46, 0, Math.PI * 2); ctx.stroke();

  ctx.strokeStyle = "rgba(56,189,248,0.75)"; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(mx(0), mz(0), 8, 0, Math.PI * 2); ctx.stroke();

  const stCols = { SOLAR: "#facc15", ICE: "#38bdf8", SCIENCE: "#d8b4fe", FARM: "#4ade80", PANTRY: "#f472b6", SHIELD: "#60a5fa" };
  Object.entries(STATIONS).forEach(([k, st]) => {
    ctx.fillStyle = stCols[k];
    ctx.beginPath(); ctx.arc(mx(st.x), mz(st.z), 3.4, 0, Math.PI * 2); ctx.fill();
  });

  ctx.fillStyle = "#fef08a";
  coinOrbs.forEach(co => {
    if (co.userData.active) ctx.fillRect(mx(co.position.x) - 1.2, mz(co.position.z) - 1.2, 2.4, 2.4);
  });

  ctx.fillStyle = "#ffffff";
  ctx.beginPath(); ctx.arc(mx(heroPos.x), mz(heroPos.z), 4.2, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 1.8; ctx.stroke();
}

function animate3D() {
  requestAnimationFrame(animate3D);
  if (session.screen !== "GAME") return;
  const dt = Math.min(0.05, clock.getDelta());
  const t = clock.elapsedTime;
  const diff = getDiff();

  earthGroup.rotation.y += dt * 0.08;
  drillCrystal.rotation.y += dt * 1.8;
  drillCrystal.position.y = 3.3 + Math.sin(t * 2.5) * 0.22;

  roverGroup.position.x = Math.sin(t * 0.26) * 24;
  roverGroup.rotation.y = Math.cos(t * 0.26) > 0 ? Math.PI / 2 : -Math.PI / 2;

  shootingStar.position.x += dt * 36;
  shootingStar.position.y -= dt * 7;
  if (shootingStar.position.x > 110) {
    shootingStar.position.set(-90 - Math.random() * 40, 38 + Math.random() * 20, -75 - Math.random() * 35);
  }

  Object.values(padRings).forEach((ring, idx) => {
    const s = 1 + Math.sin(t * 3.5 + idx) * 0.06;
    ring.scale.set(s, s, 1);
  });

  shieldDomeMesh.visible = state.shieldOn;
  shieldWireMesh.visible = state.shieldOn;
  if (state.shieldOn) shieldWireMesh.rotation.y += dt * 0.22;

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
    sunMesh.scale.setScalar(1.26 + Math.sin(t * 10) * 0.07);
    sunMesh.material.color.setHex(0xf97316);
    scene.fog.color.setHex(0x2a0a0a);
    beaconLight.color.setHex(0xef4444);
    beaconLight.intensity = 1.2 + Math.sin(t * 12) * 1.1;
    flareParticles.visible = false;
  } else if (state.flarePhase === "ACTIVE") {
    sunMesh.scale.setScalar(1.52);
    sunMesh.material.color.setHex(0xef4444);
    scene.fog.color.setHex(0x450a0a);
    beaconLight.color.setHex(0xef4444);
    beaconLight.intensity = 2.2 + Math.sin(t * 16) * 1.2;
    flareParticles.visible = true;
    const arr = flareParticles.geometry.attributes.position.array;
    for (let i = 1; i < arr.length; i += 3) { arr[i] -= dt * 21; if (arr[i] < 0) arr[i] = 34; }
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

    if (Math.hypot(joyX, joyY) > 0.12) {
      moveX += joyX;
      moveZ += joyY;
    }

    if (Math.hypot(moveX, moveZ) > 0.08) {
      state.autoTarget = null;
    } else if (state.autoTarget) {
      const dx = state.autoTarget.x - heroPos.x, dz = state.autoTarget.z - heroPos.z;
      const dist = Math.hypot(dx, dz);
      if (dist < 0.5) state.autoTarget = null;
      else { moveX = dx / dist; moveZ = dz / dist; }
    }

    const runSpeed = (session.heroKey === "WIDOW") ? 13.8 : 11.2;
    const mag = Math.hypot(moveX, moveZ);
    if (mag > 0.08) {
      const clampMag = Math.min(1, mag);
      moveX = (moveX / mag) * clampMag;
      moveZ = (moveZ / mag) * clampMag;
      heroPos.x = Math.max(-WORLD_LIMIT_X, Math.min(WORLD_LIMIT_X, heroPos.x + moveX * runSpeed * dt));
      heroPos.z = Math.max(-WORLD_LIMIT_Z, Math.min(WORLD_LIMIT_Z, heroPos.z + moveZ * runSpeed * dt));
      const rDist = Math.hypot(heroPos.x, heroPos.z);
      if (rDist > 52) {
        heroPos.x = (heroPos.x / rDist) * 52;
        heroPos.z = (heroPos.z / rDist) * 52;
      }
      const desiredRot = Math.atan2(moveX, moveZ);
      heroRotY += Math.atan2(Math.sin(desiredRot - heroRotY), Math.cos(desiredRot - heroRotY)) * Math.min(1, dt * 12);

      heroLimbs.lLeg.rotation.x = Math.sin(t * 15) * 0.72;
      heroLimbs.rLeg.rotation.x = -Math.sin(t * 15) * 0.72;
      heroLimbs.lArm.rotation.x = -Math.sin(t * 15) * 0.62;
      heroLimbs.rArm.rotation.x = Math.sin(t * 15) * 0.62;

      footstepTimer -= dt;
      if (footstepTimer <= 0 && heroPos.y <= 0.05) {
        footstepTimer = 0.25;
        spawnFxPuff(heroPos.x, 0.12, heroPos.z, 0x94a3b8, 0.22);
      }
    } else {
      heroLimbs.lLeg.rotation.x *= 0.85; heroLimbs.rLeg.rotation.x *= 0.85;
      heroLimbs.lArm.rotation.x *= 0.85; heroLimbs.rArm.rotation.x *= 0.85;
    }

    heroPos.y += heroVelY * dt;
    if (heroPos.y > 0) {
      heroVelY -= 11.2 * dt;
      if (Math.random() < 0.45) spawnFxPuff(heroPos.x, heroPos.y + 0.3, heroPos.z, 0x38bdf8, 0.16);
    } else { heroPos.y = 0; heroVelY = 0; }
    heroGroup.position.copy(heroPos);
    heroGroup.rotation.y = heroRotY;

    const nowInside = isInsideHabitat();
    if (wasInside && !nowInside && state.doorSealed) {
      state.doorSealed = false;
      playSfx(310, 0.14, "square", 0.06);
      setStatus("🌑 Stepped outside onto Lunar Plains! Press E to seal Airlock when back inside.");
    }
    wasInside = nowInside;

    coinOrbs.forEach(c => {
      if (c.userData.active) {
        c.rotation.z += dt * 3.0;
        c.position.y = 1.1 + Math.sin(t * 3 + c.position.x) * 0.22;
        if (Math.hypot(heroPos.x - c.position.x, heroPos.z - c.position.z) < 1.6) {
          c.userData.active = false; c.visible = false; c.userData.respawn = 12;
          const gain = (session.heroKey === "LOKI") ? 50 : 25;
          addVaultCoins(gain);
          playSfx(987, 0.16, "sine", 0.085, 1318);
          spawnFxPuff(c.position.x, 1.1, c.position.z, 0xfde047, 0.58);
          setStatus(`🪙 Picked up Lunar Coin Orb (+${gain} 🪙 added directly to Vault)!`);
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
      if (state.activePad !== stoodPad) {
        state.activePad = stoodPad;
        state.padProgress = 0;
        if (stoodPad !== "SHIELD") state.shieldPadLatched = false;
      }
      if (stoodPad === "SHIELD" && state.shieldPadLatched) {
        progWrap.style.display = "none";
      } else {
        state.padProgress += dt * 1.25;
        progWrap.style.display = "flex";
        document.getElementById("pad-progress-label").innerText = STATIONS[stoodPad].label;
        document.getElementById("pad-progress-bar").style.width = Math.min(100, Math.max(0, state.padProgress * 100)) + "%";
        if (state.padProgress >= 1.0) {
          completePadAction(stoodPad);
          state.padProgress = -0.75;
        }
      }
    } else {
      state.activePad = null;
      state.padProgress = 0;
      state.shieldPadLatched = false;
      progWrap.style.display = "none";
    }

    const growSpeed = (session.heroKey === "WANDA") ? 8.0 : 4.8;
    for (let i = 0; i < 4; i++) {
      state.crops[i] = Math.min(100, state.crops[i] + growSpeed * dt);
      const s = 0.25 + (state.crops[i] / 100) * 0.95;
      cropMeshes[i].scale.set(s, s, s);
    }

    if (state.roverCooldown > 0) state.roverCooldown -= dt;

    if (state.shieldOn) {
      const sDrain = (session.heroKey === "CAP" ? 0.72 : 1.45) * diff.drain;
      state.power = Math.max(0, state.power - sDrain * dt);
      if (state.power <= 0.1) { state.shieldOn = false; setStatus("⚡ Battery hit 0%! Shield offline!"); }
    } else if (state.dusty) {
      state.power = Math.max(0, state.power - 0.35 * diff.drain * dt);
    } else {
      state.power = Math.min(100, state.power + ((session.heroKey === "IRON") ? 4.2 : 2.3) * dt);
    }

    let oxLoss = (state.doorSealed ? 0.32 : 1.25) * diff.drain;
    if (session.heroKey === "WIDOW") oxLoss *= 0.6;
    state.oxygen = Math.max(0, state.oxygen - oxLoss * dt);
    state.food = Math.max(0, state.food - 0.28 * diff.drain * dt);

    state.flareTimer -= dt;
    if (state.flarePhase === "CALM" && state.flareTimer <= 0) {
      state.flarePhase = "WARN"; state.flareTimer = diff.flareWarn;
      playSfx(240, 0.45, "sawtooth", 0.08, 460);
      document.getElementById("flare-alarm").style.display = "block";
      document.getElementById("flare-alarm-title").innerText = `🚨 NASA DONKI ${NASA.flr.class} FLARE!`;
      showComic("🚨☀️🔥", "SOLAR FLARE INCOMING!", `DONKI ${NASA.flr.class} storm hits in ${Math.ceil(diff.flareWarn)}s! Press E & Q inside!`, 2800);
    } else if (state.flarePhase === "WARN") {
      document.getElementById("flare-alarm-desc").innerText = `Impact in ${Math.max(0, state.flareTimer).toFixed(1)}s! Inside + Door(E) + Shield(Q)`;
      if (state.flareTimer <= 0) { state.flarePhase = "ACTIVE"; state.flareTimer = diff.flareDur; playSfx(180, 0.5, "sawtooth", 0.095, 120); }
    } else if (state.flarePhase === "ACTIVE") {
      document.getElementById("flare-alarm-title").innerText = `☢️ STORM HITTING (${Math.ceil(state.flareTimer)}s)`;
      const safe = nowInside && state.doorSealed && state.shieldOn;
      if (!safe) {
        state.hp = Math.max(0, state.hp - diff.flareDmg * (session.heroKey === "THOR" ? 0.4 : 1.0) * dt);
        state.rad += 0.22 * dt;
        document.getElementById("flare-alarm-desc").innerText = "⚠️ RADIATION HIT! Inside + Door(E) + Shield(Q)!";
      } else {
        state.rad += 0.012 * dt;
        document.getElementById("flare-alarm-desc").innerText = "🛡️ 100% PROTECTED BY SHIELD!";
      }
      if (state.flareTimer <= 0) {
        state.flarePhase = "CALM"; state.flareTimer = diff.flareGap + Math.random() * 5;
        document.getElementById("flare-alarm").style.display = "none";
        if (Math.random() < 0.6) { state.dusty = true; showComic("🌪️☀️", "PANELS DUSTY!", "Press 1 to sweep moon dust off solar panels!", 2300); }
        else showComic("☀️✅", "FLARE PASSED!", "Press Q to turn Shield OFF and recharge!", 2200);
        setStatus("☀️ Solar Flare cleared! Press Q to turn Shield OFF and recharge batteries.");
      }
    } else {
      state.rad += 0.012 * dt;
    }

    state.solClock += dt;
    if (state.solClock >= diff.solSecs) {
      state.solClock = 0; state.sol += 1;
      telemetryLog.push({ sol: state.sol, pwr: Math.round(state.power), ox: Math.round(state.oxygen), hp: Math.round(state.hp) });

      if (state.sol > 7) {
        endMission(true, "WIN");
      } else {
        const bonus = (session.heroKey === "LOKI") ? 70 : 35;
        addVaultCoins(bonus);
        state.science += 50;
        if (state.pantryCount > 0) { state.pantryCount--; refreshPantryVisuals(); }
        playSfx(523, 0.2, "triangle", 0.09, 784);
        if (DILEMMAS[state.sol] && !state.dilemmasShown[state.sol]) {
          state.dilemmasShown[state.sol] = true;
          triggerDilemma(state.sol);
        } else {
          showComic("🌙🏆", `LUNAR SOL ${state.sol} OF 7`, `+${bonus} 🪙 Vault Coins & +50 🔬 Science!`, 2000);
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

  const z = state.camZoom;
  const followRatio = state.fullMoonMode ? 0.08 : Math.max(0.15, 0.92 - (z - 1) * 0.22);
  const desiredCam = new THREE.Vector3(
    heroPos.x * followRatio,
    13.5 * z,
    heroPos.z * followRatio + 18.5 * z
  );
  camera.position.lerp(desiredCam, Math.min(1, dt * 4.5));
  camera.lookAt(heroPos.x * followRatio, state.fullMoonMode ? -2.0 : 1.4, heroPos.z * followRatio);

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

  document.getElementById("btn-shield").innerHTML = (state.shieldOn ? "🛡️ Shield: ON" : "🛡️ Shield: OFF") + '<span class="kbadge">Q</span>';
  document.getElementById("btn-door").innerHTML = (state.doorSealed ? "🔒 Airlock: SEALED" : "🔓 Airlock: OPEN") + '<span class="kbadge">E</span>';
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
    addVaultCoins(150);
    playSfx(523, 0.25, "triangle", 0.1, 1046);
    const rank = state.science >= 1100 ? "💎 CHIEF NASA MISSION PLANNER" : (state.science >= 700 ? "🥇 SHACKLETON COMMANDER" : "🥈 ARTEMIS SPECIALIST");
    document.getElementById("debrief-icon").innerText = "🏆🦸‍♂️🌕";
    document.getElementById("debrief-title").innerText = "7-SOL MISSION ACCOMPLISHED!";
    document.getElementById("debrief-rank").innerText = `${rank} • +150 🪙 Victory Vault Bonus!`;
    document.getElementById("debrief-sub").innerText = `${h.name} survived 7 Sols | Science: ${state.science} | Dose: ${state.rad.toFixed(2)} mSv | Vault: ${Math.floor(session.vaultCoins)} 🪙`;
    document.getElementById("debrief-lesson").innerHTML =
      `<b>🛰️ Engineering Takeaway:</b> You balanced Power, Oxygen, CSA Food, EVA Science, and <b>NASA DONKI ${NASA.flr.class}</b> space weather across 7 Sols! Keep collecting Vault Coins to unlock Iron Man, Thor, Dr. Strange, Wanda &amp; Loki!`;
  } else {
    playSfx(220, 0.45, "sawtooth", 0.09, 110);
    document.getElementById("debrief-icon").innerText = "🛠️📡";
    document.getElementById("debrief-title").innerText = `MISSION DEBRIEF — SOL ${state.sol} OF 7`;
    document.getElementById("debrief-rank").innerText = `Science Logged: ${state.science} pts • Vault Coins Kept: ${Math.floor(session.vaultCoins)} 🪙`;
    const lessons = {
      POWER: "⚡ <b>Power Budget Depleted:</b> Turn Shield OFF (Q) after solar flares pass and press 1 to scrub dusty solar panels!",
      OXYGEN: "🫁 <b>Oxygen Depleted:</b> Press E to seal the Airlock when back inside and press 2 to mine Shackleton Crater ice (H₂O → O₂)!",
      FOOD: "🍽️ <b>Pantry Empty:</b> Press 4 to harvest CSA crops and press 5 to stock your Pantry Table!",
      RADIATION: "☢️ <b>Solar Flare Exposure:</b> When the NASA DONKI siren sounds, get inside, Seal Airlock (E), and Raise Shield (Q)!"
    };
    document.getElementById("debrief-sub").innerText = `Resource limit reached: ${cause}. All Vault Coins earned are safely banked!`;
    document.getElementById("debrief-lesson").innerHTML = lessons[cause] || lessons.POWER;
  }

  const c = document.getElementById("debrief-chart");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  for (let y = 22; y <= 122; y += 25) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif";
  ctx.fillText("100%", 6, 25); ctx.fillText("50%", 12, 75); ctx.fillText("0%", 18, 125);
  const pts = telemetryLog.length > 1 ? telemetryLog : [...telemetryLog, { sol: state.sol + 0.5, pwr: state.power, ox: state.oxygen, hp: state.hp }];
  function plotSeries(k, col) {
    ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.beginPath();
    pts.forEach((p, idx) => {
      const x = 45 + (idx / Math.max(1, pts.length - 1)) * 525;
      const y = 122 - (Math.max(0, Math.min(100, p[k])) / 100) * 100;
      if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
  plotSeries("pwr", "#facc15"); plotSeries("ox", "#38bdf8"); plotSeries("hp", "#f43f5e");
  ctx.fillStyle = "#facc15"; ctx.fillText("■ Power", 410, 14);
  ctx.fillStyle = "#38bdf8"; ctx.fillText("■ Oxygen", 470, 14);
  ctx.fillStyle = "#f43f5e"; ctx.fillText("■ Crew HP", 535, 14);
  syncVaultDisplays();
}

window.addEventListener("keydown", e => {
  if (session.screen !== "GAME") return;
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) e.preventDefault();
  keys[e.code] = true;
  if (e.repeat) return;

  switch (e.code) {
    case "Space": triggerJump(); break;
    case "KeyQ": toggleShield(); break;
    case "KeyE": toggleDoor(); break;
    case "Digit1": autoRunTo("SOLAR"); break;
    case "Digit2": autoRunTo("ICE"); break;
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
    case "KeyC": toggleFullMoonView(); break;
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
