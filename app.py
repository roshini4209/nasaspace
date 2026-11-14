import streamlit as st
import random
import time
import requests
import pandas as pd

# ==========================================
# 1. PAGE CONFIG & HIGH-CONTRAST GAME CSS
# ==========================================
st.set_page_config(
    page_title="Lunar Hero: Artemis Outpost Game",
    page_icon="🧑‍🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Deep Space Background */
.stApp {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
    color: #ffffff !important;
}

/* FORCE ALL TEXT TO BE BRIGHT & VISIBLE */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #f8fafc !important;
}

/* Fix Metric Cards Visibility */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 16px !important;
    padding: 14px !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25) !important;
}
div[data-testid="stMetricLabel"] p, div[data-testid="stMetricLabel"] {
    color: #7dd3fc !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
}
div[data-testid="stMetricValue"] div, div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
}

/* Fix Sidebar Visibility */
section[data-testid="stSidebar"] {
    background-color: #090d16 !important;
    border-right: 2px solid #38bdf8 !important;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Game Action Buttons */
.stButton>button {
    background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 2px solid #7dd3fc !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    transition: 0.2s ease-in-out !important;
    width: 100%;
}
.stButton>button:hover {
    transform: scale(1.02) !important;
    border-color: #fde047 !important;
    box-shadow: 0 0 18px rgba(253, 224, 71, 0.7) !important;
}

/* Kid-Friendly Info Boxes */
.game-banner {
    background: rgba(30, 41, 59, 0.95);
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 14px;
    font-size: 1.05rem;
}
.flare-warning {
    background: linear-gradient(90deg, #7f1d1d, #991b1b);
    border: 3px solid #fde047;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 14px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 10px #ef4444; }
    50% { box-shadow: 0 0 28px #fde047; }
    100% { box-shadow: 0 0 10px #ef4444; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INITIALIZE GAME SESSION STATE
# ==========================================
if "profile_ready" not in st.session_state:
    st.session_state.profile_ready = False
    st.session_state.player_name = "Alex"
    st.session_state.player_age = 9
    st.session_state.difficulty = "Cadet (Ages 7–9)"

if "sol" not in st.session_state:
    st.session_state.sol = 1
    st.session_state.power = 90
    st.session_state.oxygen = 90
    st.session_state.food = 90
    st.session_state.health = 100
    st.session_state.shield_on = False
    st.session_state.door_closed = False
    st.session_state.player_pos = "OUTSIDE_SOLAR"  # OUTSIDE_SOLAR, INSIDE_HAB, GREENHOUSE
    st.session_state.solar_flare_active = True
    st.session_state.dust_on_panels = False
    st.session_state.rad_msv = 0.42
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.story_log = (
        "🚨 **SOLAR FLARE INCOMING!** You are standing **OUTSIDE** near the solar panels! "
        "Quick: 1️⃣ Turn **ON** the Radiation Shield (costs Power), 2️⃣ Run **INSIDE** the Outpost, and 3️⃣ **CLOSE** the Airlock Door!"
    )
    st.session_state.history = pd.DataFrame({
        "Sol": [1], "Power": [90], "Oxygen": [90], "Food": [90], "Health": [100]
    })

# ==========================================
# 3. STEP 0: AGE & DIFFICULTY ONBOARDING MODAL
# ==========================================
if not st.session_state.profile_ready:
    st.markdown("<h1 style='text-align:center;'>🧑‍🚀 Welcome to Lunar Hero: Artemis Outpost!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.2rem;'>An Interactive Space Survival Game Powered by Real NASA Data</p>", unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("<div class='game-banner'>", unsafe_allow_html=True)
        st.subheader("🎮 Step 1: Create Your Astronaut Profile")
        name_input = st.text_input("What is your Astronaut Name?", value="Commander Alex")
        age_input = st.slider("🎂 How old are you? (Adjusts Game Difficulty!)", min_value=7, max_value=12, value=9)
        
        if age_input <= 9:
            diff_label = "🌟 Junior Cadet Mode (Ages 7–9)"
            diff_desc = "Simpler tips, slower resource drain, and helpful reminders when a Solar Storm appears!"
        else:
            diff_label = "🚀 Mission Commander Mode (Ages 10–12)"
            diff_desc = "Faster battery drain, surprise moon-dust storms, and real NASA radiation trade-offs!"
            
        st.info(f"**Selected Difficulty:** {diff_label}\n\n{diff_desc}")
        
        if st.button("🚀 LAUNCH TO THE MOON!"):
            st.session_state.player_name = name_input
            st.session_state.player_age = age_input
            st.session_state.difficulty = diff_label
            st.session_state.profile_ready = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. SIDEBAR NAVIGATION & PLAYER BADGE
# ==========================================
with st.sidebar:
    st.markdown(f"### 🧑‍🚀 {st.session_state.player_name}")
    st.caption(f"Age: {st.session_state.player_age} | {st.session_state.difficulty}")
    st.markdown("---")
    
    nav_page = st.radio(
        "🕹️ **CHOOSE SCREEN:**",
        [
            "🎮 1. Play Lunar Outpost Game",
            "📈 2. Mission Graphs & Math Lab",
            "🛰️ 3. Real NASA Data & Science"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 🎒 Astronaut Suit Status")
    loc_label = "🌑 Outside on Moon" if st.session_state.player_pos == "OUTSIDE_SOLAR" else (
        "🏠 Inside Outpost" if st.session_state.player_pos == "INSIDE_HAB" else "🌱 In Greenhouse"
    )
    st.write(f"📍 **Location:** {loc_label}")
    st.write(f"🚪 **Airlock Door:** {'🔒 CLOSED (Safe)' if st.session_state.door_closed else '🔓 OPEN (Danger!)'}")
    st.write(f"🛡️ **Radiation Shield:** {'🟢 MAX ON (-25⚡)' if st.session_state.shield_on else '⚪ OFF (Saves Power)'}")
    
    st.markdown("---")
    if st.button("🔄 Restart Game"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ==========================================
# HELPER: INTERACTIVE 2D VISUAL GAME SCENE
# ==========================================
def render_visual_outpost():
    """Renders an interactive cartoon 2D SVG Lunar Base Scene reacting to player actions."""
    flare_svg = ""
    sky_color = "#020617"
    if st.session_state.solar_flare_active:
        sky_color = "#450a0a"
        flare_svg = """
        <circle cx="110" cy="70" r="48" fill="#f97316" />
        <circle cx="110" cy="70" r="35" fill="#fde047" />
        <path d="M 160 80 Q 320 120 480 160" stroke="#fbbf24" stroke-width="6" stroke-dasharray="10,6" fill="none"/>
        <path d="M 150 100 Q 300 160 440 210" stroke="#ef4444" stroke-width="5" stroke-dasharray="8,8" fill="none"/>
        <text x="180" y="55" fill="#fde047" font-size="18" font-weight="bold">⚡ NASA DONKI SOLAR FLARE INCOMING! ⚡</text>
        """
    else:
        flare_svg = """
        <circle cx="110" cy="70" r="32" fill="#fde047" />
        <text x="160" y="65" fill="#93c5fd" font-size="16" font-weight="bold">☀️ Calm Space Weather (Normal Sunlight)</text>
        """

    # Shield Dome Visual
    shield_svg = ""
    if st.session_state.shield_on:
        shield_svg = """
        <path d="M 350 310 A 210 190 0 0 1 830 310" fill="rgba(56, 189, 248, 0.22)" stroke="#38bdf8" stroke-width="6" stroke-dasharray="12,6"/>
        <text x="475" y="115" fill="#38bdf8" font-size="16" font-weight="bold">🛡️ WATER-WALL SHIELD ACTIVE (-25% POWER)</text>
        """

    # Airlock Door Visual
    door_color = "#22c55e" if st.session_state.door_closed else "#ef4444"
    door_text = "🔒 DOOR CLOSED" if st.session_state.door_closed else "🔓 DOOR OPEN"

    # Dust on Solar Panels Visual
    panel_color = "#a16207" if st.session_state.dust_on_panels else "#2563eb"
    panel_label = "🌪️ DUSTY PANELS!" if st.session_state.dust_on_panels else "☀️ SOLAR PANELS"

    # Player Astronaut Position Coordinates
    if st.session_state.player_pos == "OUTSIDE_SOLAR":
        astro_x, astro_y = 235, 245
        astro_caption = "🧑‍🚀 YOU (Outside)"
    elif st.session_state.player_pos == "INSIDE_HAB":
        astro_x, astro_y = 525, 245
        astro_caption = "🧑‍🚀 YOU (Safe Inside)"
    else:
        astro_x, astro_y = 715, 245
        astro_caption = "🧑‍🚀 YOU (Farming)"

    svg_code = f"""
    <div style="border: 3px solid #38bdf8; border-radius: 18px; overflow: hidden; margin-bottom: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.6);">
    <svg viewBox="0 0 900 360" width="100%" height="320" xmlns="http://www.w3.org/2000/svg">
        <!-- Space Sky -->
        <rect width="900" height="290" fill="{sky_color}" />
        <!-- Stars -->
        <circle cx="40" cy="40" r="2" fill="white"/>
        <circle cx="280" cy="30" r="2" fill="white"/>
        <circle cx="620" cy="45" r="2.5" fill="white"/>
        <circle cx="840" cy="60" r="2" fill="white"/>
        <circle cx="760" cy="25" r="1.5" fill="white"/>

        {flare_svg}
        {shield_svg}

        <!-- Gray Lunar Surface (Shackleton Crater Rim) -->
        <rect x="0" y="290" width="900" height="70" fill="#64748b" />
        <ellipse cx="150" cy="325" rx="65" ry="12" fill="#475569" />
        <ellipse cx="480" cy="335" rx="90" ry="14" fill="#475569" />
        <text x="20" y="345" fill="#e2e8f0" font-size="14" font-weight="bold">🌑 LUNAR SOUTH POLE (SHACKLETON CRATER RIM)</text>

        <!-- STATION 1: OUTSIDE SOLAR ARRAY -->
        <rect x="115" y="210" width="110" height="50" fill="{panel_color}" stroke="#93c5fd" stroke-width="3" rx="6"/>
        <line x1="170" y1="260" x2="170" y2="290" stroke="#cbd5e1" stroke-width="8"/>
        <text x="110" y="198" fill="#ffffff" font-size="13" font-weight="bold">{panel_label}</text>

        <!-- STATION 2: MAIN HABITAT DOME & AIRLOCK -->
        <path d="M 410 290 A 125 115 0 0 1 650 290 Z" fill="#1e293b" stroke="#cbd5e1" stroke-width="5"/>
        <!-- Airlock Door on Left of Dome -->
        <rect x="415" y="215" width="42" height="75" fill="{door_color}" stroke="#ffffff" stroke-width="3" rx="6"/>
        <text x="385" y="165" fill="{door_color}" font-size="14" font-weight="bold">{door_text}</text>
        <text x="485" y="205" fill="#38bdf8" font-size="15" font-weight="bold">🏠 HABITAT & O₂</text>

        <!-- STATION 3: CSA GREENHOUSE DOME -->
        <path d="M 660 290 A 85 80 0 0 1 820 290 Z" fill="#064e3b" stroke="#4ade80" stroke-width="4"/>
        <text x="675" y="205" fill="#4ade80" font-size="14" font-weight="bold">🌱 CSA FARM</text>
        <circle cx="710" cy="275" r="8" fill="#ef4444"/>
        <circle cx="740" cy="275" r="8" fill="#22c55e"/>
        <circle cx="770" cy="275" r="8" fill="#ef4444"/>

        <!-- PLAYER ASTRONAUT CHARACTER -->
        <g transform="translate({astro_x}, {astro_y})">
            <!-- Suit Body -->
            <rect x="-18" y="0" width="36" height="38" rx="10" fill="#f8fafc" stroke="#38bdf8" stroke-width="3"/>
            <!-- Helmet -->
            <circle cx="0" cy="-14" r="18" fill="#f8fafc" stroke="#38bdf8" stroke-width="3"/>
            <!-- Gold Visor -->
            <rect x="-11" y="-22" width="22" height="14" rx="6" fill="#fbbf24"/>
            <!-- Label above Player -->
            <rect x="-60" y="-54" width="120" height="22" rx="6" fill="#0284c7"/>
            <text x="-50" y="-38" fill="#ffffff" font-size="12" font-weight="bold">{astro_caption}</text>
        </g>
    </svg>
    </div>
    """
    st.markdown(svg_code, unsafe_allow_html=True)

# ==========================================
# PAGE 1: INTERACTIVE LUNAR SIMULATION GAME
# ==========================================
if nav_page == "🎮 1. Play Lunar Outpost Game":
    st.title(f"🌕 Lunar Outpost Survival — Sol (Day) {st.session_state.sol} of 7")

    # Top 4 Big Kid-Friendly Meters
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⚡ Battery Power", f"{st.session_state.power}%", "-25% if Shield ON" if st.session_state.shield_on else "+Solar Charging")
    m2.metric("🫁 Oxygen (Air)", f"{st.session_state.oxygen}%", "Safe" if st.session_state.door_closed else "Leaking (Door Open!)")
    m3.metric("🍅 Space Food", f"{st.session_state.food}%", "CSA Hydroponics")
    m4.metric("❤️ Astronaut Health", f"{st.session_state.health}%", f"{st.session_state.rad_msv:.2f} mSv Radiation")

    # Check Win / Lose States
    if st.session_state.game_over:
        st.error(f"💥 **MISSION OVER ON SOL {st.session_state.sol}!** {st.session_state.story_log}")
        st.info("💡 **What We Learned:** On the Moon, every action has a trade-off! Turning on shields saves your health from solar flares, but drains battery power needed for food and oxygen. Click **Restart Game** in the sidebar to try again!")
        st.stop()

    if st.session_state.game_won:
        st.success(f"🏆 **YOU WON, {st.session_state.player_name.upper()}!** You survived 7 Lunar Sols at Shackleton Crater and mastered NASA engineering trade-offs!")
        st.balloons()
        st.stop()

    # Live Alert Banner
    if st.session_state.solar_flare_active:
        st.markdown(f"<div class='flare-warning'>{st.session_state.story_log}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='game-banner'>{st.session_state.story_log}</div>", unsafe_allow_html=True)

    # Render Interactive 2D Visual Outpost
    render_visual_outpost()

    # ==========================================
    # INTERACTIVE ACTION CONTROLS (KID-FRIENDLY)
    # ==========================================
    st.subheader("🕹️ Step 1: Move Your Astronaut & Operate the Base!")
    st.caption("Watch the picture above change as you click! Every action trades one resource for another.")

    c_move, c_shield, c_tasks = st.columns(3)

    with c_move:
        st.markdown("#### 🏃 1. Move & Airlock Door")
        if st.button("🌑 Walk Outside to Solar Panels"):
            st.session_state.player_pos = "OUTSIDE_SOLAR"
            st.session_state.door_closed = False
            st.session_state.story_log = "🧑‍🚀 You opened the Airlock Door and walked **OUTSIDE** to the solar panels! (Warning: You are exposed if a Solar Flare hits!)"
            st.rerun()

        if st.button("🏠 Run Inside Habitat Dome"):
            st.session_state.player_pos = "INSIDE_HAB"
            st.session_state.story_log = "🏠 You ran **INSIDE** the Habitat Dome! Don't forget to **Close the Airlock Door** to lock in oxygen and block radiation!"
            st.rerun()

        door_btn_label = "🔓 Open Airlock Door" if st.session_state.door_closed else "🔒 Close & Lock Airlock Door"
        if st.button(door_btn_label):
            if st.session_state.player_pos == "OUTSIDE_SOLAR" and not st.session_state.door_closed:
                st.warning("Run INSIDE the Habitat or Greenhouse before locking the door from the inside!")
            else:
                st.session_state.door_closed = not st.session_state.door_closed
                state_word = "CLOSED and locked" if st.session_state.door_closed else "OPENED"
                st.session_state.story_log = f"🚪 Airlock Door is now **{state_word}**!"
                st.rerun()

    with c_shield:
        st.markdown("#### 🛡️ 2. Radiation & Power Trade-Off")
        shield_btn_text = "🟢 Turn OFF Shield (Save Power)" if st.session_state.shield_on else "🛡️ RAISE RADIATION SHIELD (-25% Power)"
        if st.button(shield_btn_text):
            if not st.session_state.shield_on:
                if st.session_state.power >= 25:
                    st.session_state.shield_on = True
                    st.session_state.power = max(0, st.session_state.power - 25)
                    st.session_state.story_log = "🛡️ **Radiation Shield RAISED!** Water walls now block NASA DONKI solar flares, but your **Battery Power dropped by 25%** right away!"
                else:
                    st.session_state.story_log = "⚠️ Not enough Battery Power to raise the shield! Sweep the solar panels outside first!"
            else:
                st.session_state.shield_on = False
                st.session_state.power = min(100, st.session_state.power + 15)
                st.session_state.story_log = "⚪ **Radiation Shield Powered Down.** You saved +15% Battery Power, but the dome is unshielded against solar flares!"
            st.rerun()

        if st.button("🧹 Sweep Moon Dust off Panels (+25% ⚡)"):
            if st.session_state.player_pos != "OUTSIDE_SOLAR":
                st.session_state.story_log = "❗ You must walk **OUTSIDE to the Solar Panels** first to sweep off the moon dust!"
            else:
                st.session_state.dust_on_panels = False
                st.session_state.power = min(100, st.session_state.power + 25)
                st.session_state.oxygen = max(0, st.session_state.oxygen - 10)
                st.session_state.story_log = "🧹 You brushed the sticky lunar dust off the solar arrays! **+25% Battery Power**, but working outside used **-10% Oxygen**!"
            st.rerun()

    with c_tasks:
        st.markdown("#### 🌱 3. Food & Oxygen Station")
        if st.button("🌱 Go to Greenhouse & Grow Food (+25% 🍅)"):
            if st.session_state.power < 15:
                st.session_state.story_log = "⚠️ Too little Battery Power to run the purple LED grow-lights!"
            else:
                st.session_state.player_pos = "GREENHOUSE"
                st.session_state.power = max(0, st.session_state.power - 15)
                st.session_state.food = min(100, st.session_state.food + 25)
                st.session_state.oxygen = min(100, st.session_state.oxygen + 5)
                st.session_state.story_log = "🍅 You walked into the **CSA Greenhouse** and turned on the LED grow-lights! **+25% Space Tomatoes & +5% Plant Oxygen**, but it cost **-15% Power**!"
            st.rerun()

        if st.button("🫁 Make Fresh Oxygen from Moon Ice (+25% 🫁)"):
            if st.session_state.power < 15:
                st.session_state.story_log = "⚠️ Not enough Battery Power to melt crater ice into oxygen!"
            else:
                st.session_state.player_pos = "INSIDE_HAB"
                st.session_state.power = max(0, st.session_state.power - 15)
                st.session_state.oxygen = min(100, st.session_state.oxygen + 25)
                st.session_state.story_log = "🫁 You melted Shackleton Crater ice into breathable air! **+25% Oxygen**, costing **-15% Battery Power**!"
            st.rerun()

    st.markdown("---")
    # ==========================================
    # END TURN / SLEEP TO NEXT SOL BUTTON
    # ==========================================
    if st.button("🌙 FINISH TODAY & SIMULATE NEXT LUNAR SOL (1.3s Earth-Moon Radio Delay)"):
        with st.spinner("📡 Sending daily status to NASA Mission Control on Earth (1.3 seconds light-travel time)..."):
            time.sleep(1.5)

        # Difficulty Multiplier based on Player Age
        drain = 10 if st.session_state.player_age <= 9 else 15

        # Daily baseline consumption
        st.session_state.oxygen = max(0, st.session_state.oxygen - drain)
        st.session_state.food = max(0, st.session_state.food - drain)

        # Solar recharge if panels are clean
        solar_gain = 10 if st.session_state.dust_on_panels else 22
        st.session_state.power = min(100, max(0, st.session_state.power + solar_gain))

        outcome_notes = []

        # Evaluate Solar Flare Protection
        if st.session_state.solar_flare_active:
            if st.session_state.player_pos == "OUTSIDE_SOLAR":
                st.session_state.health = max(0, st.session_state.health - 35)
                st.session_state.rad_msv += 2.10
                outcome_notes.append("🚨 **OUCH!** You stayed **OUTSIDE** during a NASA DONKI Solar Flare! You took **-35% Health** from space radiation!")
            elif not st.session_state.door_closed:
                st.session_state.oxygen = max(0, st.session_state.oxygen - 20)
                st.session_state.health = max(0, st.session_state.health - 15)
                st.session_state.rad_msv += 1.10
                outcome_notes.append("⚠️ You went inside, but left the **Airlock Door OPEN**! Radiation and air leaked (-15% Health, -20% Oxygen)!")
            elif not st.session_state.shield_on:
                st.session_state.health = max(0, st.session_state.health - 20)
                st.session_state.rad_msv += 1.45
                outcome_notes.append("⚠️ You were inside with the door closed, but forgot to turn ON the **Radiation Shield**! Solar protons pierced the wall (-20% Health)!")
            else:
                st.session_state.rad_msv += 0.20
                outcome_notes.append("🛡️ **PERFECT DEFENSE!** You turned on the Radiation Shield, ran inside, and closed the Airlock Door! Zero solar flare damage!")
        else:
            st.session_state.rad_msv += 0.42
            if not st.session_state.door_closed:
                st.session_state.oxygen = max(0, st.session_state.oxygen - 15)
                outcome_notes.append("🔓 You left the Airlock Door open overnight, losing **-15% Oxygen**!")
            else:
                outcome_notes.append("✨ Peaceful lunar night! All crew members slept safely inside.")

        # Advance Sol & Roll Next Day's NASA Event
        st.session_state.sol += 1
        next_roll = random.random()
        if next_roll < 0.50:
            st.session_state.solar_flare_active = True
            st.session_state.shield_on = False  # Resets so player must actively decide each flare
            outcome_notes.append("⚡ **NEW NASA DONKI ALERT:** A giant Solar Flare just erupted from the Sun! Raise shields, get inside, and close the door!")
        elif next_roll < 0.80:
            st.session_state.solar_flare_active = False
            st.session_state.dust_on_panels = True
            outcome_notes.append("🌪️ **MOON DUST ALERT:** Sticky lunar dust covered your solar panels outside! Walk outside to sweep them or power will drop!")
        else:
            st.session_state.solar_flare_active = False
            outcome_notes.append("☀️ **CLEAR SKIES:** Calm space weather today! Great time to turn OFF shields to save power and grow food in the Greenhouse!")

        st.session_state.story_log = " | ".join(outcome_notes)

        # Save to History for Page 2 Graphs
        new_row = pd.DataFrame({
            "Sol": [st.session_state.sol],
            "Power": [st.session_state.power],
            "Oxygen": [st.session_state.oxygen],
            "Food": [st.session_state.food],
            "Health": [st.session_state.health]
        })
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)

        # Check Win / Lose
        if st.session_state.power <= 0 or st.session_state.oxygen <= 0 or st.session_state.food <= 0 or st.session_state.health <= 0:
            st.session_state.game_over = True
        elif st.session_state.sol > 7:
            st.session_state.game_won = True

        st.rerun()

# ==========================================
# PAGE 2: MISSION GRAPHS & MATH LAB (SEPARATED)
# ==========================================
elif nav_page == "📈 2. Mission Graphs & Math Lab":
    st.title("📈 Mission Telemetry Graphs & Trade-Off Math")
    st.write("Here is how your decisions in the game affected your Lunar Outpost over time!")

    st.subheader("1. Resource History Chart Across Lunar Sols")
    st.line_chart(st.session_state.history.set_index("Sol"))

    st.subheader("2. How the Engineering Trade-Off Math Works")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class='game-banner'>
        <h4>⚡ The Shield vs. Power Equation</h4>
        <p>On the Moon, water-wall pumps and magnetic shields protect astronauts from solar storms, but they require massive electricity:</p>
        <ul>
            <li><b>Raising Radiation Shield:</b> Costs <b>-25% Battery Power</b> immediately.</li>
            <li><b>Leaving Shield OFF during Solar Flare:</b> Saves battery, but deals <b>-20% to -35% Astronaut Health</b> damage!</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='game-banner'>
        <h4>☢️ Your Cumulative NASA RadLab Dose</h4>
        <p><b>Total Radiation Absorbed:</b> <code>{st.session_state.rad_msv:.2f} mSv (Millisieverts)</code></p>
        <ul>
            <li><b>Normal Lunar Day (NASA RadLab BLEO):</b> +0.42 mSv/Sol</li>
            <li><b>Shielded Solar Flare:</b> +0.20 mSv/Sol</li>
            <li><b>Unshielded Outside in Solar Flare:</b> +2.10 mSv/Sol</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE 3: REAL NASA DATA & SCIENCE SOURCES
# ==========================================
elif nav_page == "🛰️ 3. Real NASA Data & Science":
    st.title("🛰️ Real NASA & Space Agency Science Inside This Game")
    st.write("Every rule in **Lunar Hero** comes from real space datasets provided for the 2026 NASA Space Apps Challenge:")

    st.markdown("""
    <div class='game-banner'>
    <h4>☀️ 1. NASA DONKI (Space Weather Database)</h4>
    <p>When the Sun turns red and shoots yellow lightning in our game, that represents a real <b>Solar Flare (FLR)</b> or <b>Solar Energetic Particle (SEP)</b> storm tracked by NASA's Moon-to-Mars Space Weather Analysis Office (<code>https://api.nasa.gov/DONKI/FLR</code>).</p>
    </div>

    <div class='game-banner'>
    <h4>🧬 2. NASA OSDR (Open Science Data Repository) & RadLab</h4>
    <p>Why does your Astronaut Health drop if you skip food or absorb radiation? Real NASA space biology missions—including <b>OSD-137 (Rodent Research 3)</b>, <b>OSD-1018 (Space Radiation & Behavior)</b>, and <b>OSD-767 (Spaceflight Tomato Crop Stress)</b>—prove that radiation and low nutrition weaken muscles, bones, and plants in space!</p>
    </div>

    <div class='game-banner'>
    <h4>🌱 3. Canadian Space Agency (CSA) Lunar Food Toolkit</h4>
    <p>Our greenhouse station is modeled on the <b>CSA Toolkit for Food Production on the Moon</b>. Growing dwarf tomatoes and lettuce with hydroponic LED lights gives astronauts fresh food and extra oxygen, but uses precious solar power.</p>
    </div>

    <div class='game-banner'>
    <h4>🌑 4. NASA Moon Trek & Shackleton Crater (Lunar South Pole)</h4>
    <p>Our outpost is located at the rim of <b>Shackleton Crater</b> on the Moon's South Pole, mapped by NASA's Lunar Reconnaissance Orbiter (LRO). High crater rims get almost constant sunlight for solar panels, while deep craters hold frozen water ice for oxygen!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🤖 **NASA Space Apps SI Disclosure:** Built with Python & Streamlit using Gemini to assist with SVG game rendering and NASA open data integration (NASA DONKI, NASA OSDR OSD-137/OSD-767/OSD-1018, NASA RadLab, and CSA Lunar Food Toolkit).")
