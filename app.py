import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import time

# ==========================================
# 1. PAGE CONFIG & DARK SPACE GAME STYLING
# ==========================================
st.set_page_config(
    page_title="Lunar Hero: 2D Cartoon Outpost Simulator",
    page_icon="🧑‍🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 100%) !important;
    color: #ffffff !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] {
    background-color: #090d16 !important;
    border-right: 2px solid #38bdf8 !important;
}
div[data-testid="stMetric"] {
    background: #1e293b !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 14px !important;
    padding: 12px !important;
}
.stButton>button {
    background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 2px solid #7dd3fc !important;
    border-radius: 12px !important;
    padding: 12px 18px !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    width: 100%;
}
.stButton>button:hover {
    border-color: #fde047 !important;
    box-shadow: 0 0 15px rgba(253, 224, 71, 0.7) !important;
}
.card-box {
    background: #1e293b;
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZE SESSION STATE
# ==========================================
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.player_name = "Leo"
    st.session_state.avatar = "BOY"  # BOY or GIRL
    st.session_state.age = 9

# ==========================================
# 3. SCREEN 0: AVATAR (BOY/GIRL) & AGE PICKER
# ==========================================
if not st.session_state.started:
    st.markdown("<h1 style='text-align:center;'>🌕 LUNAR HERO: ARTEMIS OUTPOST</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.2rem;'>Pick your Cartoon Astronaut Avatar & Age to Start Your Mission!</p>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2.4, 1])
    with col_center:
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        name_in = st.text_input("✏️ Enter Your Astronaut Name:", value="Commander Leo")
        age_in = st.slider("🎂 Select Your Age (7 to 12) — Adjusts Game Speed & Difficulty!", 7, 12, 9)

        if age_in <= 9:
            st.info("🌟 **Junior Cadet Mode (Ages 7–9):** Slower battery drain, helpful hints during Solar Flares, and easy-to-read space tips!")
        else:
            st.warning("🚀 **Mission Commander Mode (Ages 10–12):** Faster solar storms, lunar dust hazards, and stricter NASA power trade-offs!")

        st.subheader("🧑‍🚀 Choose Your Cartoon Character:")
        av_col1, av_col2 = st.columns(2)

        # Render pure cartoon SVG previews using components.html so they never break
        with av_col1:
            components.html("""
            <div style="background:#0f172a;border:3px solid #38bdf8;border-radius:16px;padding:10px;text-align:center;font-family:sans-serif;color:white;">
                <svg width="130" height="150" viewBox="0 0 120 140">
                    <circle cx="60" cy="52" r="36" fill="#e2e8f0" stroke="#38bdf8" stroke-width="4"/>
                    <rect x="32" y="28" width="56" height="44" rx="18" fill="#1e293b"/>
                    <!-- Spiky Boy Hair -->
                    <path d="M 35 35 L 45 18 L 55 30 L 65 16 L 75 30 L 85 22 L 85 38 Z" fill="#f59e0b"/>
                    <!-- Cartoon Face -->
                    <circle cx="60" cy="52" r="18" fill="#fed7aa"/>
                    <circle cx="53" cy="49" r="3" fill="#0f172a"/>
                    <circle cx="67" cy="49" r="3" fill="#0f172a"/>
                    <path d="M 54 58 Q 60 64 66 58" stroke="#0f172a" stroke-width="2.5" fill="none"/>
                    <!-- Spacesuit Body -->
                    <rect x="34" y="86" width="52" height="46" rx="12" fill="#f8fafc" stroke="#38bdf8" stroke-width="3"/>
                    <rect x="46" y="98" width="28" height="18" rx="4" fill="#0284c7"/>
                </svg>
                <div style="font-weight:bold;font-size:16px;margin-top:4px;">👦 Boy Astronaut (Leo)</div>
            </div>
            """, height=205)
            if st.button("👦 Play as Boy Astronaut"):
                st.session_state.player_name = name_in
                st.session_state.age = age_in
                st.session_state.avatar = "BOY"
                st.session_state.started = True
                st.rerun()

        with av_col2:
            components.html("""
            <div style="background:#0f172a;border:3px solid #ec4899;border-radius:16px;padding:10px;text-align:center;font-family:sans-serif;color:white;">
                <svg width="130" height="150" viewBox="0 0 120 140">
                    <!-- Twin Ponytails -->
                    <circle cx="20" cy="52" r="12" fill="#a855f7"/>
                    <circle cx="100" cy="52" r="12" fill="#a855f7"/>
                    <circle cx="60" cy="52" r="36" fill="#e2e8f0" stroke="#ec4899" stroke-width="4"/>
                    <rect x="32" y="28" width="56" height="44" rx="18" fill="#1e293b"/>
                    <!-- Girl Hair Bangs -->
                    <path d="M 34 40 Q 60 20 86 40" stroke="#a855f7" stroke-width="10" fill="none"/>
                    <!-- Cartoon Face -->
                    <circle cx="60" cy="52" r="18" fill="#fed7aa"/>
                    <circle cx="53" cy="49" r="3" fill="#0f172a"/>
                    <circle cx="67" cy="49" r="3" fill="#0f172a"/>
                    <path d="M 54 58 Q 60 64 66 58" stroke="#e11d48" stroke-width="2.5" fill="none"/>
                    <!-- Spacesuit Body -->
                    <rect x="34" y="86" width="52" height="46" rx="12" fill="#f8fafc" stroke="#ec4899" stroke-width="3"/>
                    <rect x="46" y="98" width="28" height="18" rx="4" fill="#db2777"/>
                </svg>
                <div style="font-weight:bold;font-size:16px;margin-top:4px;">👧 Girl Astronaut (Maya)</div>
            </div>
            """, height=205)
            if st.button("👧 Play as Girl Astronaut"):
                st.session_state.player_name = name_in
                st.session_state.age = age_in
                st.session_state.avatar = "GIRL"
                st.session_state.started = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown(f"### {'👦' if st.session_state.avatar=='BOY' else '👧'} {st.session_state.player_name}")
    st.caption(f"Age: {st.session_state.age} | {'Cadet Mode (7-9)' if st.session_state.age<=9 else 'Commander Mode (10-12)'}")
    st.markdown("---")
    page = st.radio(
        "🧭 **GAME MENU:**",
        [
            "🎮 1. Live 2D Lunar Outpost Game",
            "📊 2. Telemetry Graphs & Math Lab",
            "🛰️ 3. Real NASA Science Guide"
        ]
    )
    st.markdown("---")
    if st.button("🔄 Change Avatar / Age"):
        st.session_state.started = False
        st.rerun()

# ==========================================
# PAGE 1: PURE 2D INTERACTIVE CARTOON SIMULATION
# ==========================================
if page == "🎮 1. Live 2D Lunar Outpost Game":
    drain_rate = 8 if st.session_state.age <= 9 else 13
    avatar_type = st.session_state.avatar
    player_name = st.session_state.player_name

    # Pure HTML5/SVG/JS 2D Cartoon Game Engine inside components.html (Immune to white markdown bug!)
    game_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }}
        body {{ margin: 0; padding: 10px; background: #060b19; color: #ffffff; }}
        
        /* Top Resource HUD Bars */
        .hud {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-bottom: 10px;
        }}
        .hud-card {{
            background: #1e293b;
            border: 2px solid #38bdf8;
            border-radius: 12px;
            padding: 8px 12px;
            text-align: center;
        }}
        .hud-title {{ font-size: 13px; color: #93c5fd; font-weight: bold; }}
        .hud-val {{ font-size: 22px; font-weight: 900; margin: 2px 0; }}
        .bar-bg {{ width: 100%; height: 10px; background: #0f172a; border-radius: 6px; overflow: hidden; }}
        .bar-fill {{ height: 100%; transition: width 0.35s ease; }}

        /* Story / Alert Ticker */
        .ticker {{
            background: #1e293b;
            border: 2px solid #fde047;
            border-radius: 12px;
            padding: 10px 16px;
            margin-bottom: 10px;
            font-size: 15px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .flare-mode {{
            background: linear-gradient(90deg, #7f1d1d, #991b1b);
            border-color: #fde047;
            animation: flash 1.2s infinite;
        }}
        @keyframes flash {{
            0%, 100% {{ box-shadow: 0 0 8px #ef4444; }}
            50% {{ box-shadow: 0 0 22px #fde047; }}
        }}

        /* 2D Cartoon World Viewport */
        .world-box {{
            border: 3px solid #38bdf8;
            border-radius: 16px;
            overflow: hidden;
            background: #020617;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        }}

        /* Smooth Character Walking Animation */
        #astronaut {{
            transition: transform 0.65s cubic-bezier(0.25, 1, 0.5, 1);
        }}

        /* Interactive Control Deck */
        .controls {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 12px;
        }}
        .ctrl-col {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 10px;
        }}
        .ctrl-col h4 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #7dd3fc;
            text-align: center;
        }}
        button.game-btn {{
            width: 100%;
            background: linear-gradient(90deg, #0284c7, #2563eb);
            color: white;
            border: 2px solid #7dd3fc;
            border-radius: 10px;
            padding: 9px 10px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 6px;
            transition: 0.15s;
        }}
        button.game-btn:hover {{
            transform: translateY(-2px);
            border-color: #fde047;
            box-shadow: 0 0 12px rgba(253, 224, 71, 0.6);
        }}
        button.next-sol-btn {{
            background: linear-gradient(90deg, #16a34a, #059669);
            border-color: #86efac;
            font-size: 15px;
            padding: 14px;
        }}
    </style>
    </head>
    <body>

    <!-- TOP TELEMETRY HUD -->
    <div class="hud">
        <div class="hud-card">
            <div class="hud-title">📅 LUNAR SOL (DAY)</div>
            <div class="hud-val" id="sol-val">1 / 7</div>
            <div style="font-size:11px;color:#cbd5e1;">Comms Delay: 1.3s</div>
        </div>
        <div class="hud-card">
            <div class="hud-title">⚡ BATTERY POWER</div>
            <div class="hud-val" id="pwr-val">90%</div>
            <div class="bar-bg"><div id="pwr-bar" class="bar-fill" style="width:90%;background:#facc15;"></div></div>
        </div>
        <div class="hud-card">
            <div class="hud-title">🫁 OXYGEN (AIR)</div>
            <div class="hud-val" id="ox-val">90%</div>
            <div class="bar-bg"><div id="ox-bar" class="bar-fill" style="width:90%;background:#38bdf8;"></div></div>
        </div>
        <div class="hud-card">
            <div class="hud-title">🍅 SPACE FOOD</div>
            <div class="hud-val" id="food-val">90%</div>
            <div class="bar-bg"><div id="food-bar" class="bar-fill" style="width:90%;background:#4ade80;"></div></div>
        </div>
        <div class="hud-card">
            <div class="hud-title">❤️ CREW HEALTH</div>
            <div class="hud-val" id="hp-val">100%</div>
            <div class="bar-bg"><div id="hp-bar" class="bar-fill" style="width:100%;background:#f43f5e;"></div></div>
        </div>
    </div>

    <!-- MISSION ALERT BANNER -->
    <div id="alert-box" class="ticker flare-mode">
        <span id="story-text">🚨 NASA DONKI SOLAR FLARE INCOMING! You are OUTSIDE! 1) Raise Shield (-25% Power), 2) Run Inside Outpost, 3) Close Door!</span>
        <span id="rad-badge" style="background:#0f172a;padding:4px 10px;border-radius:8px;font-size:12px;color:#fde047;">☢️ Dose: 0.42 mSv</span>
    </div>

    <!-- 2D CARTOON LUNAR OUTPOST SCENE -->
    <div class="world-box">
        <svg id="game-svg" viewBox="0 0 960 350" width="100%" height="340">
            <defs>
                <linearGradient id="skyNormal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#020617"/>
                    <stop offset="100%" stop-color="#0f172a"/>
                </linearGradient>
                <linearGradient id="skyFlare" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#450a0a"/>
                    <stop offset="100%" stop-color="#1e1b4b"/>
                </linearGradient>
                <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#fef08a"/>
                    <stop offset="60%" stop-color="#f97316"/>
                    <stop offset="100%" stop-color="rgba(239,68,68,0)"/>
                </radialGradient>
            </defs>

            <!-- Dynamic Sky Background -->
            <rect id="sky-rect" width="960" height="275" fill="url(#skyFlare)" />

            <!-- Stars & Earth in the Lunar Sky -->
            <circle cx="50" cy="40" r="2" fill="#ffffff"/>
            <circle cx="240" cy="25" r="2.5" fill="#ffffff"/>
            <circle cx="480" cy="35" r="2" fill="#ffffff"/>
            <circle cx="720" cy="28" r="2.5" fill="#ffffff"/>
            <circle cx="910" cy="50" r="2" fill="#ffffff"/>
            <!-- Cartoon Earth in Distance -->
            <circle cx="870" cy="60" r="26" fill="#2563eb" stroke="#93c5fd" stroke-width="2"/>
            <path d="M 855 50 Q 870 45 878 58 Q 865 72 855 65 Z" fill="#22c55e"/>
            <text x="838" y="100" fill="#93c5fd" font-size="11" font-weight="bold">🌍 EARTH (1.3s)</text>

            <!-- SUN & SOLAR FLARE RAYS (NASA DONKI) -->
            <g id="sun-group">
                <circle cx="105" cy="70" r="58" fill="url(#sunGlow)" />
                <circle cx="105" cy="70" r="32" fill="#fde047" />
                <!-- Animated Solar Flare Bolts -->
                <g id="flare-rays" style="display:block;">
                    <path d="M 155 80 L 290 135 L 275 148 L 430 195" stroke="#fde047" stroke-width="5" fill="none" stroke-dasharray="10,5"/>
                    <path d="M 145 105 L 260 165 L 250 180 L 390 230" stroke="#ef4444" stroke-width="4" fill="none"/>
                    <text x="175" y="48" fill="#fde047" font-size="16" font-weight="bold">⚡ NASA DONKI SOLAR FLARE STORM! ⚡</text>
                </g>
            </g>

            <!-- CRATER MOUNTAINS IN BACKGROUND -->
            <polygon points="0,275 120,195 260,275" fill="#1e293b"/>
            <polygon points="210,275 360,180 520,275" fill="#334155"/>
            <polygon points="620,275 790,190 960,275" fill="#1e293b"/>

            <!-- LUNAR SURFACE GROUND -->
            <rect x="0" y="275" width="960" height="75" fill="#64748b"/>
            <ellipse cx="140" cy="315" rx="55" ry="10" fill="#475569"/>
            <ellipse cx="520" cy="325" rx="80" ry="12" fill="#475569"/>
            <ellipse cx="830" cy="315" rx="60" ry="10" fill="#475569"/>

            <!-- ACTIVE RADIATION SHIELD FORCE-FIELD DOME -->
            <g id="shield-dome" style="display:none;">
                <path d="M 355 275 A 255 215 0 0 1 885 275" fill="rgba(56, 189, 248, 0.20)" stroke="#38bdf8" stroke-width="6" stroke-dasharray="14,6"/>
                <text x="485" y="95" fill="#38bdf8" font-size="16" font-weight="bold">🛡️ WATER-WALL RADIATION SHIELD ON (-25% POWER)</text>
            </g>

            <!-- STATION 1: OUTSIDE SOLAR ARRAYS (X = 180) -->
            <g transform="translate(95, 175)">
                <!-- Support Pole -->
                <rect x="68" y="55" width="12" height="45" fill="#cbd5e1"/>
                <rect x="45" y="92" width="58" height="10" rx="4" fill="#94a3b8"/>
                <!-- Tilted Solar Panel Wing -->
                <rect id="solar-panel-rect" x="0" y="10" width="148" height="48" rx="6" fill="#2563eb" stroke="#93c5fd" stroke-width="3"/>
                <line x1="37" y1="10" x2="37" y2="58" stroke="#93c5fd" stroke-width="1.5"/>
                <line x1="74" y1="10" x2="74" y2="58" stroke="#93c5fd" stroke-width="1.5"/>
                <line x1="111" y1="10" x2="111" y2="58" stroke="#93c5fd" stroke-width="1.5"/>
                <line x1="0" y1="34" x2="148" y2="34" stroke="#93c5fd" stroke-width="1.5"/>
                <text id="solar-label" x="8" y="0" fill="#fde047" font-size="13" font-weight="bold">☀️ SOLAR ARRAY (CLEAN)</text>
            </g>

            <!-- STATION 2: ARTEMIS HABITAT DOME & AIRLOCK DOOR (X = 520) -->
            <g>
                <!-- Outer Dome Structure -->
                <path d="M 390 275 A 135 125 0 0 1 660 275 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="5"/>
                <!-- Interior Cutaway Window -->
                <path d="M 445 270 A 80 75 0 0 1 625 270 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="3"/>
                <!-- O2 Life Support Tanks Inside -->
                <rect x="565" y="220" width="20" height="45" rx="6" fill="#38bdf8"/>
                <rect x="590" y="220" width="20" height="45" rx="6" fill="#38bdf8"/>
                <text x="562" y="214" fill="#7dd3fc" font-size="10" font-weight="bold">O₂ TANKS</text>

                <!-- AIRLOCK CORRIDOR & DOOR ON LEFT SIDE -->
                <rect x="385" y="195" width="52" height="80" rx="6" fill="#334155" stroke="#cbd5e1" stroke-width="3"/>
                <!-- Door Panel (Changes Red when Open, Green when Closed) -->
                <rect id="airlock-door" x="393" y="203" width="36" height="70" rx="4" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
                <text id="door-status-txt" x="365" y="185" fill="#f87171" font-size="13" font-weight="bold">🔓 DOOR OPEN</text>
                <text x="475" y="140" fill="#ffffff" font-size="14" font-weight="bold">🏠 ARTEMIS OUTPOST</text>
            </g>

            <!-- STATION 3: CSA HYDROPONIC GREENHOUSE DOME (X = 775) -->
            <g>
                <path d="M 685 275 A 90 85 0 0 1 865 275 Z" fill="rgba(6, 78, 59, 0.9)" stroke="#4ade80" stroke-width="4"/>
                <!-- Purple LED Grow Bar -->
                <rect x="730" y="212" width="90" height="7" rx="3" fill="#e879f9"/>
                <!-- Hydroponic Tomato Plants -->
                <circle cx="745" cy="255" r="10" fill="#22c55e"/>
                <circle cx="745" cy="252" r="5" fill="#ef4444"/>
                <circle cx="775" cy="255" r="10" fill="#22c55e"/>
                <circle cx="775" cy="252" r="5" fill="#ef4444"/>
                <circle cx="805" cy="255" r="10" fill="#22c55e"/>
                <circle cx="805" cy="252" r="5" fill="#ef4444"/>
                <text x="712" y="178" fill="#4ade80" font-size="13" font-weight="bold">🌱 CSA GREENHOUSE</text>
            </g>

            <!-- ========================================== -->
            <!-- CARTOON ASTRONAUT CHARACTER (MOVES SMOOTHLY) -->
            <!-- ========================================== -->
            <g id="astronaut" transform="translate(215, 200)">
                <!-- Floating Speech/Status Bubble Above Head -->
                <rect x="-65" y="-42" width="130" height="22" rx="8" fill="#0284c7" stroke="#ffffff" stroke-width="1.5"/>
                <text id="astro-bubble" x="0" y="-27" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="bold">{player_name} (Outside)</text>

                <!-- Backpack (PLSS Life Support) -->
                <rect x="-22" y="22" width="44" height="36" rx="8" fill="#cbd5e1" stroke="#475569" stroke-width="2"/>

                <!-- Girl Ponytails (Only displayed if GIRL avatar selected) -->
                <g style="display:{'block' if avatar_type=='GIRL' else 'none'};">
                    <circle cx="-26" cy="4" r="9" fill="#a855f7"/>
                    <circle cx="26" cy="4" r="9" fill="#a855f7"/>
                </g>

                <!-- Spacesuit Helmet -->
                <circle cx="0" cy="4" r="22" fill="#ffffff" stroke="{'38bdf8' if avatar_type=='BOY' else '#ec4899'}" stroke-width="3.5"/>
                <!-- Helmet Visor Glass -->
                <rect x="-15" y="-10" width="30" height="22" rx="10" fill="#1e293b"/>
                <!-- Cartoon Hair Inside Helmet -->
                <path d="M -12 -6 Q 0 -15 12 -6" stroke="{'#f59e0b' if avatar_type=='BOY' else '#a855f7'}" stroke-width="5" fill="none"/>
                <!-- Cartoon Face & Smile Inside Visor -->
                <circle cx="0" cy="2" r="10" fill="#fed7aa"/>
                <circle cx="-4" cy="0" r="1.8" fill="#0f172a"/>
                <circle cx="4" cy="0" r="1.8" fill="#0f172a"/>
                <path d="M -4 5 Q 0 9 4 5" stroke="#0f172a" stroke-width="1.8" fill="none"/>

                <!-- Spacesuit Torso -->
                <rect x="-16" y="25" width="32" height="32" rx="9" fill="#ffffff" stroke="#38bdf8" stroke-width="2.5"/>
                <!-- Chest Control Patch -->
                <rect x="-9" y="32" width="18" height="12" rx="3" fill="#0284c7"/>

                <!-- Cartoon Arms -->
                <line x1="-16" y1="32" x2="-28" y2="45" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/>
                <line x1="16" y1="32" x2="28" y2="45" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/>

                <!-- Cartoon Legs & Moon Boots -->
                <line x1="-8" y1="57" x2="-10" y2="73" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>
                <line x1="8" y1="57" x2="10" y2="73" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>
                <rect x="-15" y="70" width="12" height="7" rx="3" fill="#334155"/>
                <rect x="3" y="70" width="12" height="7" rx="3" fill="#334155"/>
            </g>
        </svg>
    </div>

    <!-- INTERACTIVE GAME BUTTONS -->
    <div class="controls">
        <!-- Column 1: Movement & Door -->
        <div class="ctrl-col">
            <h4>🏃 1. MOVE & AIRLOCK</h4>
            <button class="game-btn" onclick="walkOutside()">🌑 Walk Outside to Solar</button>
            <button class="game-btn" onclick="runInside()">🏠 Run Inside Outpost</button>
            <button class="game-btn" id="door-btn" onclick="toggleDoor()">🔒 Close Airlock Door</button>
        </div>

        <!-- Column 2: Solar Flare & Shield Trade-Off -->
        <div class="ctrl-col">
            <h4>🛡️ 2. SOLAR SHIELD & DUST</h4>
            <button class="game-btn" id="shield-btn" onclick="toggleShield()">🛡️ Raise Shield (-25% ⚡)</button>
            <button class="game-btn" onclick="sweepDust()">🧹 Sweep Solar Dust (+25% ⚡)</button>
        </div>

        <!-- Column 3: Food & Oxygen Trade-Off -->
        <div class="ctrl-col">
            <h4>🌱 3. FOOD & OXYGEN</h4>
            <button class="game-btn" onclick="growFood()">🍅 Grow Space Food (-15% ⚡)</button>
            <button class="game-btn" onclick="makeOxygen()">🫁 Melt Ice for O₂ (-15% ⚡)</button>
        </div>

        <!-- Column 4: Next Sol Turn -->
        <div class="ctrl-col">
            <h4>🌙 4. ADVANCE MISSION</h4>
            <button class="game-btn next-sol-btn" onclick="nextSol()">🚀 FINISH SOL & SIMULATE NIGHT</button>
            <button class="game-btn" style="background:#475569;border-color:#94a3b8;" onclick="resetSim()">🔄 Play Again (Reset)</button>
        </div>
    </div>

    <script>
        let sol = 1;
        let power = 90;
        let oxygen = 90;
        let food = 90;
        let health = 100;
        let radDose = 0.42;
        let pos = "OUTSIDE"; // OUTSIDE, INSIDE, FARM
        let doorClosed = false;
        let shieldOn = false;
        let flareActive = true;
        let dustyPanels = false;
        let gameOver = false;
        const drainRate = {drain_rate};
        const playerName = "{player_name}";

        function updateUI(msg) {{
            document.getElementById("sol-val").innerText = sol + " / 7";
            document.getElementById("pwr-val").innerText = power + "%";
            document.getElementById("ox-val").innerText = oxygen + "%";
            document.getElementById("food-val").innerText = food + "%";
            document.getElementById("hp-val").innerText = health + "%";

            document.getElementById("pwr-bar").style.width = power + "%";
            document.getElementById("ox-bar").style.width = oxygen + "%";
            document.getElementById("food-bar").style.width = food + "%";
            document.getElementById("hp-bar").style.width = health + "%";

            document.getElementById("rad-badge").innerText = "☢️ Dose: " + radDose.toFixed(2) + " mSv";
            if (msg) document.getElementById("story-text").innerText = msg;

            // Move Cartoon Astronaut Smoothly
            const astro = document.getElementById("astronaut");
            const bubble = document.getElementById("astro-bubble");
            if (pos === "OUTSIDE") {{
                astro.setAttribute("transform", "translate(215, 200)");
                bubble.textContent = playerName + " (Outside)";
            }} else if (pos === "INSIDE") {{
                astro.setAttribute("transform", "translate(515, 200)");
                bubble.textContent = playerName + " (Inside Safe)";
            }} else {{
                astro.setAttribute("transform", "translate(765, 200)");
                bubble.textContent = playerName + " (Farming)";
            }}

            // Door Visual
            const doorRect = document.getElementById("airlock-door");
            const doorTxt = document.getElementById("door-status-txt");
            const doorBtn = document.getElementById("door-btn");
            if (doorClosed) {{
                doorRect.setAttribute("fill", "#22c55e");
                doorTxt.textContent = "🔒 DOOR CLOSED";
                doorTxt.setAttribute("fill", "#4ade80");
                doorBtn.innerText = "🔓 Open Airlock Door";
            }} else {{
                doorRect.setAttribute("fill", "#ef4444");
                doorTxt.textContent = "🔓 DOOR OPEN";
                doorTxt.setAttribute("fill", "#f87171");
                doorBtn.innerText = "🔒 Close Airlock Door";
            }}

            // Shield Dome Visual
            const dome = document.getElementById("shield-dome");
            const sBtn = document.getElementById("shield-btn");
            if (shieldOn) {{
                dome.style.display = "block";
                sBtn.innerText = "🟢 Turn OFF Shield (+15% ⚡)";
            }} else {{
                dome.style.display = "none";
                sBtn.innerText = "🛡️ Raise Shield (-25% ⚡)";
            }}

            // Solar Flare Visual
            const rays = document.getElementById("flare-rays");
            const sky = document.getElementById("sky-rect");
            const alertBox = document.getElementById("alert-box");
            if (flareActive) {{
                rays.style.display = "block";
                sky.setAttribute("fill", "url(#skyFlare)");
                alertBox.classList.add("flare-mode");
            }} else {{
                rays.style.display = "none";
                sky.setAttribute("fill", "url(#skyNormal)");
                alertBox.classList.remove("flare-mode");
            }}

            // Dusty Solar Panel Visual
            const pRect = document.getElementById("solar-panel-rect");
            const pLbl = document.getElementById("solar-label");
            if (dustyPanels) {{
                pRect.setAttribute("fill", "#854d0e");
                pLbl.textContent = "🌪️ DUSTY SOLAR PANELS!";
            }} else {{
                pRect.setAttribute("fill", "#2563eb");
                pLbl.textContent = "☀️ SOLAR ARRAY (CLEAN)";
            }}
        }}

        function walkOutside() {{
            if (gameOver) return;
            pos = "OUTSIDE";
            doorClosed = false;
            updateUI("🧑‍🚀 You opened the Airlock Door and walked OUTSIDE to the Solar Panels!");
        }}

        function runInside() {{
            if (gameOver) return;
            pos = "INSIDE";
            updateUI("🏠 You ran INSIDE the Outpost! Now click 'Close Airlock Door' to seal the habitat!");
        }}

        function toggleDoor() {{
            if (gameOver) return;
            if (pos === "OUTSIDE" && !doorClosed) {{
                updateUI("❗ Run INSIDE the Outpost first before locking the Airlock Door!");
                return;
            }}
            doorClosed = !doorClosed;
            updateUI(doorClosed ? "🔒 Airlock Door CLOSED and sealed! Oxygen and crew are protected." : "🔓 Airlock Door OPENED.");
        }}

        function toggleShield() {{
            if (gameOver) return;
            if (!shieldOn) {{
                if (power < 25) {{
                    updateUI("⚠️ Not enough Battery Power to raise the shield! Walk outside and sweep solar panels!");
                    return;
                }}
                shieldOn = true;
                power = Math.max(0, power - 25);
                updateUI("🛡️ RADIATION SHIELD RAISED! Watch the blue dome protect the base—Battery Power dropped by -25%!");
            }} else {{
                shieldOn = false;
                power = Math.min(100, power + 15);
                updateUI("⚪ Shield turned OFF. You saved +15% Battery Power, but watch out for Solar Flares!");
            }}
        }}

        function sweepDust() {{
            if (gameOver) return;
            if (pos !== "OUTSIDE") {{
                updateUI("❗ Walk OUTSIDE to the Solar Panels first so your astronaut can sweep the moon dust!");
                return;
            }}
            dustyPanels = false;
            power = Math.min(100, power + 25);
            oxygen = Math.max(0, oxygen - 10);
            updateUI("🧹 You swept the sticky moon dust off the solar panels! +25% Power, but breathing outside used -10% Oxygen!");
        }}

        function growFood() {{
            if (gameOver) return;
            if (power < 15) {{
                updateUI("⚠️ Too little Battery Power to run the CSA Greenhouse LED lights!");
                return;
            }}
            pos = "FARM";
            power = Math.max(0, power - 15);
            food = Math.min(100, food + 25);
            oxygen = Math.min(100, oxygen + 5);
            updateUI("🍅 You walked to the CSA Greenhouse! Grown +25% Space Tomatoes & +5% Plant O₂ (Cost: -15% Power)!");
        }}

        function makeOxygen() {{
            if (gameOver) return;
            if (power < 15) {{
                updateUI("⚠️ Not enough Battery Power to melt crater water-ice into oxygen!");
                return;
            }}
            pos = "INSIDE";
            power = Math.max(0, power - 15);
            oxygen = Math.min(100, oxygen + 25);
            updateUI("🫁 You melted lunar crater ice into fresh air! +25% Oxygen (Cost: -15% Power)!");
        }}

        function nextSol() {{
            if (gameOver) return;
            oxygen = Math.max(0, oxygen - drainRate);
            food = Math.max(0, food - drainRate);
            let solarGain = dustyPanels ? 8 : 20;
            power = Math.min(100, power + solarGain);

            let report = "";
            if (flareActive) {{
                if (pos === "OUTSIDE") {{
                    health = Math.max(0, health - 35);
                    radDose += 2.10;
                    report = "🚨 OUCH! You stayed OUTSIDE during a NASA DONKI Solar Flare! (-35% Health!) ";
                }} else if (!doorClosed) {{
                    health = Math.max(0, health - 15);
                    oxygen = Math.max(0, oxygen - 20);
                    radDose += 1.15;
                    report = "⚠️ You ran inside, but left the Airlock Door OPEN! (-15% Health, -20% O₂!) ";
                }} else if (!shieldOn) {{
                    health = Math.max(0, health - 20);
                    radDose += 1.40;
                    report = "⚠️ Door was closed, but Radiation Shield was OFF! (-20% Health!) ";
                }} else {{
                    radDose += 0.20;
                    report = "🛡️ PERFECT! Shield ON, Inside Outpost, and Door CLOSED! Zero flare damage! ";
                }}
            }} else {{
                radDose += 0.42;
                if (!doorClosed) {{
                    oxygen = Math.max(0, oxygen - 15);
                    report = "🔓 Door was left open overnight (-15% Oxygen)! ";
                }} else {{
                    report = "✨ Safe lunar night! ";
                }}
            }}

            if (power <= 0 || oxygen <= 0 || food <= 0 || health <= 0) {{
                gameOver = true;
                updateUI("💥 MISSION FAILED ON SOL " + sol + "! " + report + "Click 'Play Again (Reset)' to try a better trade-off strategy!");
                return;
            }}

            sol += 1;
            if (sol > 7) {{
                gameOver = true;
                updateUI("🏆 VICTORY! You survived all 7 Lunar Sols and mastered NASA Outpost Trade-Offs! Click 'Play Again' for a new run!");
                return;
            }}

            // Roll Next Sol Random NASA Event
            let roll = Math.random();
            if (roll < 0.50) {{
                flareActive = true;
                shieldOn = false;
                report += "| ⚡ NEW NASA DONKI SOLAR FLARE! Raise Shield, Run Inside & Close Door!";
            }} else if (roll < 0.80) {{
                flareActive = false;
                dustyPanels = true;
                report += "| 🌪️ MOON DUST STORM coated the solar panels! Walk outside to sweep them!";
            }} else {{
                flareActive = false;
                report += "| ☀️ CALM SPACE WEATHER! Great day to save power and grow food!";
            }}
            updateUI(report);
        }}

        function resetSim() {{
            sol = 1; power = 90; oxygen = 90; food = 90; health = 100; radDose = 0.42;
            pos = "OUTSIDE"; doorClosed = false; shieldOn = false; flareActive = true; dustyPanels = false; gameOver = false;
            updateUI("🚨 NEW MISSION STARTED! Solar Flare incoming—Raise Shield, Run Inside, and Close the Door!");
        }}
    </script>
    </body>
    </html>
    """
    components.html(game_html, height=760, scrolling=False)

# ==========================================
# PAGE 2: TELEMETRY GRAPHS & MATH LAB
# ==========================================
elif page == "📊 2. Telemetry Graphs & Math Lab":
    st.title("📊 Lunar Outpost Engineering Trade-Off Graphs & Math")
    st.write("Here is the real NASA math behind every action your cartoon astronaut takes on the Moon!")

    # Sample comparison chart showing Shielded vs Unshielded trade-offs
    df_sim = pd.DataFrame({
        "Sol": [1, 2, 3, 4, 5, 6, 7],
        "Power with Shield ON (%)": [90, 65, 60, 55, 50, 48, 45],
        "Crew Health with Shield ON (%)": [100, 100, 100, 98, 98, 96, 95],
        "Crew Health with Shield OFF (%)": [100, 65, 45, 25, 10, 0, 0]
    }).set_index("Sol")
    st.subheader("📈 Why Trade-Offs Matter: Shield ON (Drains Power) vs. Shield OFF (Loses Health)")
    st.line_chart(df_sim)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class='card-box'>
        <h4>⚡ 1. Solar Shield vs. Battery Power Equation</h4>
        <p>When a <b>NASA DONKI Solar Flare</b> erupts, high-energy protons race toward the Moon:</p>
        <ul>
            <li><b>Raising Water-Wall Shield:</b> Immediately costs <b>-25% Battery Power</b>, leaving less energy for growing food.</li>
            <li><b>Staying Outside Unshielded:</b> Costs <b>-35% Astronaut Health</b> and spikes radiation by <b>+2.10 mSv</b>!</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='card-box'>
        <h4>🌱 2. CSA Greenhouse & Oxygen Loop</h4>
        <p>Based on the <b>Canadian Space Agency (CSA) Lunar Food Toolkit</b> and <b>NASA OSDR Study OSD-767</b>:</p>
        <ul>
            <li><b>LED Grow Lamps:</b> Cost <b>-15% Battery Power</b> per harvest.</li>
            <li><b>Reward:</b> Produces <b>+25% Space Tomatoes</b> and <b>+5% bonus Oxygen</b> through photosynthesis!</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE 3: REAL NASA SCIENCE GUIDE
# ==========================================
elif page == "🛰️ 3. Real NASA Science Guide":
    st.title("🛰️ Real NASA & Space Agency Datasets Powering This Game")
    st.markdown("""
    <div class='card-box'>
    <h4>☀️ NASA DONKI (Space Weather Database)</h4>
    <p>Tracks real-time Solar Flares (FLR) and Coronal Mass Ejections (CME) via NASA's Moon-to-Mars Space Weather Analysis Office (<code>https://api.nasa.gov/DONKI/FLR</code>).</p>
    </div>
    <div class='card-box'>
    <h4>☢️ NASA RadLab & Open Science Data Repository (OSDR)</h4>
    <p>Baseline lunar surface radiation (~0.42 mSv/Sol) comes from <b>NASA RadLab BLEO</b>. Biological health effects are grounded in <b>OSD-137</b> (muscle/bone loss), <b>OSD-984</b> (galactic cosmic radiation impact on skeletal muscle), and <b>OSD-767</b> (spaceflight tomato crop stress).</p>
    </div>
    <div class='card-box'>
    <h4>🌱 Canadian Space Agency (CSA) Lunar Food Production Toolkit</h4>
    <p>Models how hydroponic greenhouses at the Lunar South Pole turn electrical power and water into fresh astronaut nutrition and oxygen.</p>
    </div>
    """, unsafe_allow_html=True)

