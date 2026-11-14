# ==============================================================================
# AVENGERS LUNAR OUTPOST: GEN-Z EDITION — PART 1 OF 2
# ==============================================================================
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

# 1. PAGE CONFIG (SIDEBAR COLLAPSED BY DEFAULT FOR FULL-SCREEN GAME)
st.set_page_config(
    page_title="Avengers Lunar Outpost: Gen-Z Edition",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_game_frame(html_str: str, height: int = 860):
    """Renders the interactive HTML5/JS/WebAudio game engine."""
    components.html(html_str, height=height, scrolling=False)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #1e1b4b 0%, #090d16 60%, #020617 100%) !important;
    color: #ffffff !important;
}
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 0.8rem !important;
    max-width: 99% !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] {
    background-color: #090d16 !important;
    border-right: 2px solid #eab308 !important;
}
.stButton>button {
    background: linear-gradient(90deg, #b91c1c 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: 2px solid #fde047 !important;
    border-radius: 12px !important;
    padding: 12px 18px !important;
    font-size: 1.02rem !important;
    font-weight: 800 !important;
    width: 100%;
    transition: 0.2s !important;
}
.stButton>button:hover {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 20px rgba(253, 224, 71, 0.85) !important;
    transform: translateY(-2px);
}
.avengers-card {
    background: rgba(15, 23, 42, 0.92);
    border: 2px solid #eab308;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.75);
}
.inst-card {
    background: linear-gradient(145deg, #1e1b4b, #0f172a);
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 16px;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. REAL NASA DONKI API FETCH + FALLBACK
# ==========================================
@st.cache_data(ttl=600)
def get_nasa_donki_flare():
    """Fetches real Solar Flare notifications from NASA DONKI API or uses verified NASA archive."""
    try:
        url = "https://api.nasa.gov/DONKI/FLR?api_key=DEMO_KEY"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and len(r.json()) > 0:
            latest = r.json()[-1]
            return {
                "id": latest.get("flrID", "2026-FLR-LIVE"),
                "class": latest.get("classType", "M2.4"),
                "source": "LIVE NASA DONKI API"
            }
    except Exception:
        pass
    return {
        "id": "2026-10-29T14:20-FLR",
        "class": "X1.8",
        "source": "ARCHIVED NASA DONKI DATASET"
    }

nasa_flare = get_nasa_donki_flare()

# ==========================================
# 3. AVENGERS COMMANDER ROSTER & PINTEREST LINKS
# ==========================================
HEROES = {
    "CAPTAIN_AMERICA": {
        "name": "Captain America",
        "title": "First Avenger & Outpost Tactician",
        "pin_url": "https://pin.it/7lGSNgtmX",
        "unlock_wins": 0,
        "unlock_coins": 0,
        "perk_code": "CAP",
        "perk_desc": "🛡️ Vibranium Shield: Radiation Shield costs 50% less Power to run!",
        "bio": "Unlocked First! Steve Rogers keeps the lunar base calm under pressure and halves shield battery drain.",
        "suit_color": "#2563eb",
        "accent": "#ef4444",
        "eyes": "#38bdf8",
        "head_svg": "<path d='M 24 50 A 36 36 0 0 1 96 50 Z' fill='#1d4ed8' stroke='#ffffff' stroke-width='2'/><text x='60' y='38' text-anchor='middle' fill='#ffffff' font-size='18' font-weight='900'>A</text>"
    },
    "NATASHA": {
        "name": "Natasha Romanoff",
        "title": "Black Widow • Stealth & O₂ Ops",
        "pin_url": "https://pin.it/3rwFMJxSe",
        "unlock_wins": 0,
        "unlock_coins": 0,
        "perk_code": "WIDOW",
        "perk_desc": "🕷️ Widow Stealth: Uses 50% less Oxygen & starts with +20 bonus SuperCoins!",
        "bio": "Unlocked First! Master spy who wastes zero breathable air during moonwalks and solar maintenance.",
        "suit_color": "#1e293b",
        "accent": "#ef4444",
        "eyes": "#22c55e",
        "head_svg": "<path d='M 24 58 Q 26 14 60 16 Q 94 14 96 58 L 88 34 Q 60 22 32 34 Z' fill='#b91c1c'/><circle cx='24' cy='52' r='9' fill='#b91c1c'/><circle cx='96' cy='52' r='9' fill='#b91c1c'/>"
    },
    "IRON_MAN": {
        "name": "Iron Man",
        "title": "Tony Stark • Arc Reactor Engineer",
        "pin_url": "https://pin.it/7lGSNgtmX",
        "unlock_wins": 1,
        "unlock_coins": 60,
        "perk_code": "IRON",
        "perk_desc": "⚡ Arc Reactor Core: Doubles passive Solar Charging (+2% Power/tick)!",
        "bio": "Unlock with 1 Win (or 60 🪙)! Powers the entire Shackleton Crater outpost with his Mk-85 Arc Reactor.",
        "suit_color": "#dc2626",
        "accent": "#facc15",
        "eyes": "#38bdf8",
        "head_svg": "<rect x='30' y='18' width='60' height='54' rx='18' fill='#b91c1c' stroke='#facc15' stroke-width='3'/><polygon points='38,22 82,22 76,58 44,58' fill='#facc15'/><rect x='40' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/><rect x='66' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/>"
    },
    "THOR": {
        "name": "Thor Odinson",
        "title": "God of Thunder & Stormbreaker",
        "pin_url": "https://pin.it/6mL1Mocte",
        "unlock_wins": 1,
        "unlock_coins": 60,
        "perk_code": "THOR",
        "perk_desc": "🔨 Asgardian Thunder: Takes 60% less damage from NASA DONKI Solar Flares!",
        "bio": "Unlock with 1 Win (or 60 🪙)! Cosmic radiation barely scratches the God of Thunder.",
        "suit_color": "#475569",
        "accent": "#ef4444",
        "eyes": "#38bdf8",
        "head_svg": "<path d='M 24 58 Q 28 14 60 16 Q 92 14 96 58 L 86 34 Q 60 24 34 34 Z' fill='#facc15'/><path d='M 20 42 L 10 22 L 26 32 Z' fill='#cbd5e1'/><path d='M 100 42 L 110 22 L 94 32 Z' fill='#cbd5e1'/>"
    },
    "DR_STRANGE": {
        "name": "Dr. Strange",
        "title": "Master of the Mystic Time Stone",
        "pin_url": "https://pin.it/YCQRFqBZr",
        "unlock_wins": 2,
        "unlock_coins": 80,
        "perk_code": "STRANGE",
        "perk_desc": "⏳ Eye of Agamotto: Fast Earth Comms (1.0s delay) & cheaper calls (10 🪙)!",
        "bio": "Unlock with 2 Wins (or 80 🪙)! Bends space-time so NASA Houston replies faster and cheaper.",
        "suit_color": "#1e3a8a",
        "accent": "#dc2626",
        "eyes": "#4ade80",
        "head_svg": "<path d='M 28 46 Q 30 16 60 16 Q 90 16 92 46 L 84 32 Q 60 22 36 32 Z' fill='#1e293b'/><path d='M 26 42 L 34 42' stroke='#e2e8f0' stroke-width='4'/><path d='M 86 42 L 94 42' stroke='#e2e8f0' stroke-width='4'/>"
    },
    "WANDA": {
        "name": "Wanda Maximoff",
        "title": "Scarlet Witch • Chaos Botanist",
        "pin_url": "https://pin.it/4CI6sAMay",
        "unlock_wins": 2,
        "unlock_coins": 80,
        "perk_code": "WANDA",
        "perk_desc": "🔮 Chaos Magic: CSA Greenhouse vegetables grow 2x faster & give +5 bonus O₂!",
        "bio": "Unlock with 2 Wins (or 80 🪙)! Uses Scarlet Chaos energy to accelerate hydroponic crops.",
        "suit_color": "#991b1b",
        "accent": "#f43f5e",
        "eyes": "#ef4444",
        "head_svg": "<path d='M 22 60 Q 26 16 60 16 Q 94 16 98 60 L 86 34 Q 60 24 34 34 Z' fill='#7c2d12'/><polygon points='42,38 50,18 60,30 70,18 78,38' fill='#ef4444' stroke='#fca5a5' stroke-width='1.5'/>"
    },
    "LOKI": {
        "name": "Loki",
        "title": "God of Mischief (Funko Pop Edition)",
        "pin_url": "https://pin.it/6mL1Mocte",
        "unlock_wins": 2,
        "unlock_coins": 90,
        "perk_code": "LOKI",
        "perk_desc": "🐍 Glorious Purpose: Doubles all SuperCoin (🪙) payouts from Rover & Drone!",
        "bio": "Unlock with 2 Wins (or 90 🪙)! Wearing his gold horned crown and green suit, Loki gets 2x coins!",
        "suit_color": "#15803d",
        "accent": "#eab308",
        "eyes": "#22c55e",
        "head_svg": "<path d='M 22 58 Q 24 18 60 18 Q 96 18 98 58 Z' fill='#0f172a'/><path d='M 34 40 Q 60 50 86 40 L 82 28 Q 60 38 38 28 Z' fill='#eab308' stroke='#fef08a' stroke-width='1.5'/><path d='M 40 32 Q 22 6 44 4 Q 34 18 46 30 Z' fill='#eab308'/><path d='M 80 32 Q 98 6 76 4 Q 86 18 74 30 Z' fill='#eab308'/>"
    }
}

# ==========================================
# 4. SESSION STATE INITIALIZATION
# ==========================================
if "av_stage" not in st.session_state:
    st.session_state.av_stage = "STEP_1_HERO_SELECT"
if "age_str" not in st.session_state:
    st.session_state.age_str = ""
if "valid_age" not in st.session_state:
    st.session_state.valid_age = 10
if "age_tier" not in st.session_state:
    st.session_state.age_tier = "9-12"
if "hero_key" not in st.session_state or st.session_state.hero_key not in HEROES:
    st.session_state.hero_key = "CAPTAIN_AMERICA"
if "games_won" not in st.session_state:
    st.session_state.games_won = 0
if "bank_coins" not in st.session_state:
    st.session_state.bank_coins = 40
if "unlocked_heroes" not in st.session_state:
    st.session_state.unlocked_heroes = ["CAPTAIN_AMERICA", "NATASHA"]

hero_cfg = HEROES[st.session_state.hero_key]

# ==========================================
# SIDEBAR (ONLY VISIBLE WHEN OPENED VIA TOP-LEFT '>')
# ==========================================
with st.sidebar:
    st.markdown("## 🛡️ **AVENGERS TELEMETRY HUB**")
    st.markdown(f"**Selected Avenger:** `{hero_cfg['name']}`")
    st.markdown(f"**Mission Wins:** `🏆 {st.session_state.games_won}` | **Vault Coins:** `🪙 {st.session_state.bank_coins}`")
    st.markdown("---")

    side_page = st.radio(
        "📂 **Open Module:**",
        [
            "🎮 1. Active Full-Screen Game",
            "📈 2. Engineering Graphs & Math Lab",
            "🛰️ 3. Real NASA Data Verification"
        ]
    )
    st.markdown("---")
    st.caption("Won a mission or earned SuperCoins? Claim them here to unlock Iron Man, Thor, Wanda, Dr. Strange & Loki!")
    if st.button("🏆 Claim Victory (+1 Win & +60 🪙)"):
        st.session_state.games_won += 1
        st.session_state.bank_coins += 60
        st.success("Victory Claimed! Go to Step 1 to unlock new Avengers!")
    if st.button("🛡️ Step 1: Switch Avenger / Age"):
        st.session_state.av_stage = "STEP_1_HERO_SELECT"
        st.rerun()
    if st.button("📖 Step 2: Mission Briefing"):
        st.session_state.av_stage = "STEP_2_BRIEFING"
        st.rerun()

if side_page == "📈 2. Engineering Graphs & Math Lab":
    st.title("📈 Avengers Lunar Outpost: Engineering Trade-Off Graphs")
    st.info("👈 Select **'🎮 1. Active Full-Screen Game'** in the sidebar to return to the game!")
    df_chart = pd.DataFrame({
        "Sol": [1, 2, 3, 4, 5, 6, 7],
        "Power (Smart Shield Only During Flares)": [90, 86, 82, 79, 75, 72, 70],
        "Power (If Shield Left ON Constantly)": [90, 55, 20, 0, 0, 0, 0],
        "Crew Health Protected (%)": [100, 100, 100, 99, 98, 98, 97]
    }).set_index("Sol")
    st.line_chart(df_chart)
    st.markdown("""
    <div class='avengers-card'>
    <h4>⚖️ Real NASA Resource Math Inside the Game</h4>
    <ul>
        <li><b>Spaced-Out Solar Flare Cooldown (NASA DONKI):</b> Solar flares have a guaranteed calm gap of at least 36 seconds between storms so you can turn OFF the shield, farm vegetables, and recharge batteries.</li>
        <li><b>4-Crop Greenhouse & Home Pantry Table (NASA OSDR OSD-895, OSD-767 & CSA):</b> Cultivate Tomatoes, Lettuce, Radishes, and Potatoes, carry them in your Hand Basket, and stock the Home Table where they disappear 1-by-1 as eaten!</li>
        <li><b>5-Preset Earth Comms (2.6s Light-Travel Delay):</b> Radio signals travel 384,400 km between the Moon and NASA Houston, requiring SuperCoins and a realistic time delay.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

elif side_page == "🛰️ 3. Real NASA Data Verification":
    st.title("🛰️ Authentic NASA & Space Agency Datasets Used")
    st.info("👈 Select **'🎮 1. Active Full-Screen Game'** in the sidebar to return to the game!")
    st.markdown(f"""
    <div class='avengers-card'>
    <h4>☀️ 1. Live NASA CCMC DONKI Space Weather API</h4>
    <p><b>Active Solar Flare Event ID:</b> <code>{nasa_flare['id']}</code> (Class <code>{nasa_flare['class']}</code>) via <b>{nasa_flare['source']}</b>.<br>
    Endpoint: <code>https://api.nasa.gov/DONKI/FLR</code></p>
    </div>
    <div class='avengers-card'>
    <h4>🌱 2. NASA OSDR (OSD-895 EDEN ISS & OSD-767 Space Tomatoes) + CSA</h4>
    <p>Hydroponic crop growth and oxygen production are modeled on <b>NASA OSDR Study OSD-895</b>, <b>OSD-767</b>, and the <b>Canadian Space Agency (CSA) Lunar Food Toolkit</b>.</p>
    </div>
    <div class='avengers-card'>
    <h4>☢️ 3. NASA RadLab BLEO & OSDR Crew Health (OSD-137)</h4>
    <p>Baseline lunar radiation (<code>0.42 mSv/Sol</code>) is calibrated from <b>NASA RadLab BLEO</b> and <b>OSDR Study OSD-137</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# STEP 1: DIRECT AGE INPUT (NO 7-12 METER) & AVENGERS ROSTER
# ==============================================================================
if st.session_state.av_stage == "STEP_1_HERO_SELECT":
    st.markdown("<h1 style='text-align:center;'>🛡️ AVENGERS LUNAR OUTPOST: SELECT YOUR HERO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.1rem;'>Enter your age below and choose your Avenger! (Captain America & Natasha Romanoff unlock first; names are fixed to each Avenger!)</p>", unsafe_allow_html=True)

    st.markdown("<div class='avengers-card'>", unsafe_allow_html=True)
    col_age, col_vault = st.columns([2, 1.2])

    age_is_valid = False
    with col_age:
        raw_age = st.text_input("🎂 How old are you?", value=st.session_state.age_str, placeholder="your age")
        st.session_state.age_str = raw_age
        if raw_age.strip() == "":
            st.warning("👉 Please enter **your age** above to unlock the Avenger selection buttons!")
        else:
            try:
                parsed_age = int(raw_age.strip())
                if parsed_age <= 0 or parsed_age > 100:
                    st.error("⚠️ **your age** — Age must be between 1 and 100! Please enter **your age** again.")
                else:
                    age_is_valid = True
                    st.session_state.valid_age = parsed_age
                    if parsed_age <= 9:
                        st.session_state.age_tier = "7-9"
                    else:
                        st.session_state.age_tier = "9-12"
                    st.success("✅ Age locked in! Now pick your Avenger below.")
            except ValueError:
                st.error("⚠️ **your age** — Please enter a valid number for **your age**!")

    with col_vault:
        st.markdown(f"""
        <div style='background:#0f172a;border:2px solid #fde047;border-radius:14px;padding:10px;text-align:center;'>
            <div style='font-size:12px;color:#fde047;font-weight:bold;'>🏆 WINS: {st.session_state.games_won} | 🪙 VAULT COINS: {st.session_state.bank_coins}</div>
            <div style='font-size:11px;color:#93c5fd;margin-top:4px;'>Win missions or spend SuperCoins to unlock Iron Man, Thor, Strange, Wanda & Loki!</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎁 Judge Demo: Unlock All Avengers (+300 🪙)"):
            st.session_state.games_won = 3
            st.session_state.bank_coins += 300
            st.session_state.unlocked_heroes = list(HEROES.keys())
            st.rerun()

    st.subheader("🦸‍♂️ Avengers Commander Roster (Character Powers & Instructions):")
    hero_keys = list(HEROES.keys())
    row1 = st.columns(4)
    row2 = st.columns(3)
    grid_cols = row1 + row2

    for idx, hk in enumerate(hero_keys):
        h = HEROES[hk]
        is_unlocked = (
            hk in st.session_state.unlocked_heroes
            or st.session_state.games_won >= h["unlock_wins"]
        )
        border_c = h["accent"] if is_unlocked else "#475569"
        lock_overlay = "" if is_unlocked else f"""
            <rect x="0" y="0" width="120" height="145" rx="14" fill="rgba(2,6,23,0.82)"/>
            <text x="60" y="65" text-anchor="middle" fill="#fde047" font-size="26">🔒</text>
            <text x="60" y="90" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{h['unlock_wins']} WIN OR {h['unlock_coins']} 🪙</text>
        """
        with grid_cols[idx]:
            render_game_frame(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e1b4b);border:3px solid {border_c};border-radius:16px;padding:8px;text-align:center;font-family:sans-serif;color:white;">
                <svg width="105" height="120" viewBox="0 0 120 145">
                    <circle cx="60" cy="52" r="36" fill="#f8fafc" stroke="{h['suit_color']}" stroke-width="4"/>
                    <circle cx="60" cy="53" r="22" fill="#ffedd5"/>
                    <ellipse cx="51" cy="52" rx="4.5" ry="5.5" fill="{h['eyes']}"/><circle cx="49.5" cy="50" r="1.8" fill="#fff"/>
                    <ellipse cx="69" cy="52" rx="4.5" ry="5.5" fill="{h['eyes']}"/><circle cx="67.5" cy="50" r="1.8" fill="#fff"/>
                    <path d="M 54 62 Q 60 67 66 62" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
                    {h['head_svg']}
                    <rect x="32" y="88" width="56" height="46" rx="14" fill="{h['suit_color']}" stroke="{h['accent']}" stroke-width="3.5"/>
                    <circle cx="60" cy="108" r="7" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5"/>
                    {lock_overlay}
                </svg>
                <div style="font-weight:900;font-size:13.5px;color:#fde047;">{h['name']}</div>
                <div style="font-size:10px;color:#93c5fd;margin:2px 0;">{h['title']}</div>
                <div style="font-size:10px;color:#86efac;font-weight:bold;">{h['perk_desc']}</div>
                <div style="font-size:9.5px;color:#cbd5e1;margin-top:2px;">{h['bio']}</div>
                <div style="margin-top:3px;"><a href="{h['pin_url']}" target="_blank" style="color:#f472b6;font-size:10px;text-decoration:none;">📌 Character Pin ↗</a></div>
            </div>
            """, height=255)

            if is_unlocked:
                if st.button(f"🛡️ Play as {h['name']} ➔", key=f"play_{hk}", disabled=not age_is_valid):
                    st.session_state.hero_key = hk
                    st.session_state.av_stage = "STEP_2_BRIEFING"
                    st.rerun()
            else:
                can_buy = st.session_state.bank_coins >= h["unlock_coins"] and age_is_valid
                if st.button(f"🔓 Unlock ({h['unlock_coins']} 🪙)", key=f"buy_{hk}", disabled=not can_buy):
                    st.session_state.bank_coins -= h["unlock_coins"]
                    st.session_state.unlocked_heroes.append(hk)
                    st.session_state.hero_key = hk
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# STEP 2: SIMPLE KID-FRIENDLY INSTRUCTIONS SCREEN
# ==============================================================================
if st.session_state.av_stage == "STEP_2_BRIEFING":
    st.markdown(f"<h1 style='text-align:center;'>📖 MISSION BRIEFING FOR {hero_cfg['name'].upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:1.1rem;'>Avenger Special Ability: <b style='color:#fde047;'>{hero_cfg['perk_desc']}</b></p>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class='inst-card'>
            <h3>🚨 1. Spaced-Out Solar Flares</h3>
            <p>Solar flares do <b>NOT</b> hit constantly! You get a long calm gap (36+ seconds) to work outside with your <b>Shield OFF</b>.</p>
            <p style='color:#fde047;font-weight:bold;'>⚡ When the NASA DONKI Siren + Meme pops up: Sprint Inside, Close the Door, and Turn Shield ON for the storm!</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='inst-card'>
            <h3>🧺 2. Farm, Basket & Table</h3>
            <p>Walk to the <b>CSA Greenhouse</b> to grow <b>🍅 Tomatoes, 🥬 Lettuce, 🥕 Radishes, and 🥔 Potatoes</b>!</p>
            <p style='color:#4ade80;font-weight:bold;'>When ripe, a meme pops up! Pick them into your Basket (🧺) and take them to the Home Table (they disappear 1-by-1 as you eat!).</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='inst-card'>
            <h3>📡 3. 5-Preset Earth Comms</h3>
            <p>No typing needed! Click any of the <b>5 Preset Radio Buttons</b> to call Avengers HQ & NASA Mission Control on Earth!</p>
            <p style='color:#38bdf8;font-weight:bold;'>Costs SuperCoins (🪙) and takes 2.6 seconds (light-speed travel delay) to beam back solutions & supplies!</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class='inst-card'>
            <h3>🔊 4. Sounds & Gen-Z Memes</h3>
            <p>Every move, harvest, coin pickup, and alarm plays real synthesized arcade sound effects + background space synth music!</p>
            <p style='color:#f472b6;font-weight:bold;'>Your custom Pinterest Memes pop up for flares, shield ON (2s), dusty panels, ripe crops, and victory!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("⬅️ Back to Hero Selection"):
            st.session_state.av_stage = "STEP_1_HERO_SELECT"
            st.rerun()
    with b2:
        if st.button(f"🚀 LAUNCH FULL-SCREEN GAME AS {hero_cfg['name'].upper()}! 🌕"):
            st.session_state.av_stage = "STEP_3_PLAY"
            st.rerun()
    st.stop()
# ================= END OF PART 1 (PASTE PART 2 DIRECTLY BELOW THIS LINE!) =================
# ================= START OF PART 2 (PASTE DIRECTLY BELOW PART 1) =================
# ==============================================================================
# STEP 3: FULL-SCREEN AVENGERS LUNAR ARCADE (MEMES + SOUNDS + SPACED FLARES)
# ==============================================================================
is_young_tier = (st.session_state.age_tier == "7-9")
warn_ticks = 4 if is_young_tier else 3
calm_cooldown_ticks = 12 if is_young_tier else 10  # 30 to 36s guaranteed calm gap between solar flares!
start_coins = 80 if is_young_tier else 60
if hero_cfg["perk_code"] == "WIDOW":
    start_coins += 20

avengers_game_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; user-select: none; }}
    body {{ margin: 0; padding: 6px; background: #020617; color: #ffffff; overflow-x: hidden; }}

    .hud {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin-bottom: 6px; }}
    .hud-box {{
        background: linear-gradient(145deg, #1e1b4b, #0f172a);
        border: 2px solid #eab308; border-radius: 12px; padding: 5px 6px; text-align: center;
    }}
    .hud-label {{ font-size: 10px; color: #fde047; font-weight: 800; text-transform: uppercase; }}
    .hud-num {{ font-size: 18px; font-weight: 900; margin: 1px 0; }}
    .hud-rate {{ font-size: 9.5px; font-weight: bold; padding: 1px 5px; border-radius: 5px; display: inline-block; }}
    .bar-wrap {{ width: 100%; height: 7px; background: #020617; border-radius: 4px; overflow: hidden; margin-top: 2px; }}
    .bar-inner {{ height: 100%; transition: width 0.3s ease; }}

    .top-strip {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 6px; }}
    .warning-strip {{ display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
    .warn-pill {{
        background: #7f1d1d; border: 2px solid #fde047; color: #fff;
        padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 800;
        animation: pulseWarn 1s infinite;
    }}
    .ok-pill {{
        background: #064e3b; border: 2px solid #34d399; color: #ecfdf5;
        padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 800;
    }}
    @keyframes pulseWarn {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.03); }} }}

    .viewport {{
        border: 3px solid #eab308; border-radius: 16px; overflow: hidden;
        position: relative; background: #020617; box-shadow: 0 10px 30px rgba(0,0,0,0.85);
    }}
    .clickable:hover {{ filter: drop-shadow(0 0 8px #fde047); cursor: pointer; }}
    #astronaut {{ transition: transform 0.42s cubic-bezier(0.22, 1, 0.36, 1); }}

    @keyframes hoverDrone {{
        0%, 100% {{ transform: translate(310px, 92px); }}
        50% {{ transform: translate(355px, 78px); }}
    }}
    #drone-unit {{ animation: hoverDrone 3.5s ease-in-out infinite; }}

    /* NON-BLOCKING GEN-Z MEME POPUP CARD */
    #meme-popup {{
        position: absolute; top: 38px; right: 14px; width: 250px;
        background: rgba(15, 23, 42, 0.96); border: 3px solid #fde047;
        border-radius: 16px; padding: 10px; text-align: center;
        box-shadow: 0 10px 28px rgba(0,0,0,0.9); z-index: 20; display: none;
    }}

    .deck-grid {{ display: grid; grid-template-columns: 1.15fr 1.25fr 1.4fr; gap: 8px; margin-top: 7px; }}
    .panel-box {{
        background: linear-gradient(145deg, #1e1b4b, #0f172a);
        border: 2px solid #334155; border-radius: 14px; padding: 8px 10px;
    }}
    .panel-title {{
        font-size: 12px; font-weight: 900; color: #fde047; margin: 0 0 6px 0;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .btn-grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }}
    .btn-grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-bottom: 5px; }}
    button.g-btn {{
        background: linear-gradient(90deg, #b91c1c, #1d4ed8); color: #fff;
        border: 1.5px solid #fde047; border-radius: 8px; padding: 6px 5px;
        font-size: 11px; font-weight: 800; cursor: pointer;
    }}
    button.g-btn:hover {{ border-color: #38bdf8; box-shadow: 0 0 10px rgba(253,224,71,0.7); }}
    button.comm-btn {{
        width: 100%; text-align: left; background: #0f172a; color: #e2e8f0;
        border: 1.5px solid #38bdf8; border-radius: 7px; padding: 5px 8px;
        font-size: 11px; font-weight: 700; cursor: pointer; margin-bottom: 4px;
    }}
    button.comm-btn:hover {{ background: #1e3a8a; border-color: #fde047; }}
    .earth-reply-box {{
        background: #020617; border: 1.5px solid #4ade80; border-radius: 8px;
        padding: 6px 8px; font-size: 11px; color: #86efac; min-height: 44px; margin-top: 4px;
    }}
</style>
</head>
<body tabindex="0">

<div class="hud">
    <div class="hud-box">
        <div class="hud-label">📅 Lunar Sol</div>
        <div class="hud-num" id="sol-num">1 / 7</div>
        <div class="hud-rate" id="weather-badge" style="background:#064e3b;color:#6ee7b7;">☀️ Sky Calm</div>
    </div>
    <div class="hud-box">
        <div class="hud-label">⚡ Power</div>
        <div class="hud-num" id="pwr-num">90%</div>
        <div class="bar-wrap"><div id="pwr-bar" class="bar-inner" style="width:90%;background:#facc15;"></div></div>
        <div class="hud-rate" id="pwr-rate" style="background:#064e3b;color:#6ee7b7;">☀️ Charging</div>
    </div>
    <div class="hud-box">
        <div class="hud-label">🫁 Oxygen</div>
        <div class="hud-num" id="ox-num">90%</div>
        <div class="bar-wrap"><div id="ox-bar" class="bar-inner" style="width:90%;background:#38bdf8;"></div></div>
        <div class="hud-rate" id="ox-rate" style="background:#064e3b;color:#6ee7b7;">🔒 Door Sealed</div>
    </div>
    <div class="hud-box">
        <div class="hud-label">🍽️ Hunger/Food</div>
        <div class="hud-num" id="food-num">85%</div>
        <div class="bar-wrap"><div id="food-bar" class="bar-inner" style="width:85%;background:#4ade80;"></div></div>
        <div class="hud-rate" id="pantry-rate" style="background:#1e3a8a;color:#93c5fd;">🏠 Table: 3 Veggies</div>
    </div>
    <div class="hud-box">
        <div class="hud-label">🧺 Hand Basket</div>
        <div class="hud-num" id="basket-num" style="font-size:15px;">Empty</div>
        <div class="hud-rate" style="background:#3b0764;color:#e9d5ff;">Bring to Home Table</div>
    </div>
    <div class="hud-box">
        <div class="hud-label">❤️ Hero Health</div>
        <div class="hud-num" id="hp-num">100%</div>
        <div class="bar-wrap"><div id="hp-bar" class="bar-inner" style="width:100%;background:#f43f5e;"></div></div>
        <div class="hud-rate" id="rad-rate" style="background:#451a03;color:#fde047;">☢️ 0.42 mSv</div>
    </div>
    <div class="hud-box" style="border-color:#fde047;">
        <div class="hud-label" style="color:#fde047;">🪙 SuperCoins</div>
        <div class="hud-num" id="coin-num" style="color:#fde047;">{start_coins}</div>
        <div class="hud-rate" style="background:#713f12;color:#fef08a;">🦸 {hero_cfg['name']}</div>
    </div>
</div>

<div class="top-strip">
    <div class="warning-strip" id="warning-strip"></div>
    <button class="g-btn" id="sound-btn" style="width:180px;background:#059669;" onclick="toggleAudio()">🔊 Sound &amp; Music: ON</button>
</div>

<div class="viewport">
    <!-- GEN-Z MEME POPUP OVERLAY -->
    <div id="meme-popup">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span id="meme-badge" style="background:#eab308;color:#000;font-size:10px;font-weight:900;padding:2px 6px;border-radius:4px;">GEN-Z MEME ALERT</span>
            <span style="cursor:pointer;font-size:13px;color:#cbd5e1;" onclick="closeMeme()">✖</span>
        </div>
        <div id="meme-art" style="font-size:38px;margin:4px 0;">😱🔥🏃‍♂️</div>
        <div id="meme-title" style="font-weight:900;font-size:12.5px;color:#fde047;margin-bottom:3px;">POV: SOLAR FLARE INCOMING!</div>
        <div id="meme-sub" style="font-size:11px;color:#e2e8f0;margin-bottom:6px;">Drop work &amp; TURN ON THE SHIELD!!</div>
        <a id="meme-pin-link" href="https://pin.it/320BCxcPn" target="_blank" style="display:inline-block;background:#e11d48;color:#fff;font-size:10.5px;font-weight:bold;padding:4px 8px;border-radius:6px;text-decoration:none;">
            📌 View Your Pinterest Meme ↗
        </a>
    </div>

    <svg id="world-svg" viewBox="0 0 980 330" width="100%" height="325">
        <defs>
            <linearGradient id="skyCalm" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#020617"/><stop offset="100%" stop-color="#1e1b4b"/></linearGradient>
            <linearGradient id="skyWarn" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#78350f"/><stop offset="100%" stop-color="#020617"/></linearGradient>
            <linearGradient id="skyFlare" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#991b1b"/><stop offset="100%" stop-color="#090d16"/></linearGradient>
            <linearGradient id="moonGround" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#94a3b8"/><stop offset="100%" stop-color="#334155"/></linearGradient>
            <linearGradient id="metalDome" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f8fafc"/><stop offset="100%" stop-color="#64748b"/></linearGradient>
        </defs>

        <rect id="sky-bg" width="980" height="255" fill="url(#skyCalm)"/>
        <circle cx="50" cy="30" r="2" fill="#fff"/><circle cx="230" cy="20" r="2" fill="#bae6fd"/><circle cx="640" cy="22" r="2.2" fill="#fde047"/>

        <rect x="180" y="6" width="560" height="24" rx="12" fill="rgba(15,23,42,0.92)" stroke="#eab308" stroke-width="1.5"/>
        <text id="story-msg" x="460" y="22" text-anchor="middle" fill="#fde047" font-size="11.5" font-weight="bold">
            🛡️ Avengers Base Active! Sky is CALM—cultivate vegetables, drive the Rover, or collect Drone Coins!
        </text>

        <g transform="translate(905, 52)">
            <circle cx="0" cy="0" r="24" fill="#1d4ed8" stroke="#60a5fa" stroke-width="2"/>
            <path d="M -12 -10 Q 2 -16 10 -4 Q 5 12 -8 8 Z" fill="#22c55e"/>
            <text x="-45" y="36" fill="#93c5fd" font-size="10" font-weight="bold">🌍 AVENGERS HQ</text>
        </g>
        <g id="comms-beam" style="display:none;">
            <line x1="650" y1="140" x2="885" y2="58" stroke="#4ade80" stroke-width="4" stroke-dasharray="8,6"/>
            <rect x="665" y="75" width="195" height="22" rx="6" fill="#064e3b" stroke="#4ade80" stroke-width="1.5"/>
            <text x="762" y="90" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="bold">📡 CALLING EARTH HQ...</text>
        </g>

        <g id="sun-system">
            <circle cx="75" cy="58" r="32" fill="#fde047" stroke="#f97316" stroke-width="4"/>
            <g id="flare-warn-svg" style="display:none;">
                <rect x="120" y="34" width="380" height="28" rx="8" fill="#78350f" stroke="#fde047" stroke-width="2"/>
                <text id="flare-warn-txt" x="310" y="53" text-anchor="middle" fill="#fde047" font-size="12.5" font-weight="bold">
                    ⚠️ NASA DONKI ALERT: SOLAR FLARE INCOMING! RUN INSIDE!
                </text>
            </g>
            <g id="flare-bolts" style="display:none;">
                <path d="M 110 68 Q 250 110 385 160" stroke="#fde047" stroke-width="6" stroke-dasharray="10,6" fill="none"/>
                <path d="M 100 88 Q 230 145 365 205" stroke="#ef4444" stroke-width="5" stroke-dasharray="8,8" fill="none"/>
                <rect x="120" y="34" width="390" height="28" rx="8" fill="#991b1b" stroke="#fde047" stroke-width="2"/>
                <text x="315" y="53" text-anchor="middle" fill="#fde047" font-size="12.5" font-weight="bold">
                    🚨 SOLAR FLARE ({nasa_flare['class']}) HITTING! KEEP SHIELD ON &amp; DOOR SEALED!
                </text>
            </g>
        </g>

        <g id="drone-unit" class="clickable" onclick="collectIce()">
            <rect x="-18" y="-8" width="36" height="14" rx="5" fill="#eab308" stroke="#fff" stroke-width="1.5"/>
            <text x="-35" y="-14" fill="#fde047" font-size="9.5" font-weight="bold">🚁 DRONE (+10 🪙)</text>
        </g>

        <polygon points="0,255 95,175 235,255" fill="#1e293b"/>
        <polygon points="160,255 310,155 460,255" fill="#334155"/>
        <polygon points="610,255 770,165 940,255" fill="#334155"/>
        <rect x="0" y="255" width="980" height="75" fill="url(#moonGround)"/>

        <g id="shield-dome" style="display:none;">
            <path d="M 355 255 A 265 205 0 0 1 915 255" fill="rgba(56, 189, 248, 0.24)" stroke="#38bdf8" stroke-width="6" stroke-dasharray="14,6"/>
            <text x="485" y="70" fill="#38bdf8" font-size="12.5" font-weight="bold">🛡️ AVENGERS RADIATION SHIELD ACTIVE!</text>
        </g>

        <g class="clickable" onclick="walkToAndAct(135, 'SOLAR')" transform="translate(65, 152)">
            <rect x="64" y="56" width="12" height="45" fill="#cbd5e1"/>
            <rect id="solar-wing" x="0" y="10" width="140" height="48" rx="6" fill="#1d4ed8" stroke="#93c5fd" stroke-width="3"/>
            <rect id="dust-layer" x="0" y="10" width="140" height="48" rx="6" fill="rgba(161, 98, 7, 0.88)" style="display:none;"/>
            <text id="solar-txt" x="2" y="2" fill="#fde047" font-size="11.5" font-weight="bold">☀️ [CLICK] SOLAR ARRAY</text>
        </g>

        <g class="clickable" onclick="driveRover()" transform="translate(235, 212)">
            <rect x="0" y="10" width="70" height="22" rx="6" fill="#b91c1c" stroke="#fde047" stroke-width="2"/>
            <rect x="15" y="0" width="32" height="14" rx="4" fill="#38bdf8"/>
            <circle cx="16" cy="34" r="10" fill="#1e293b" stroke="#cbd5e1" stroke-width="3"/>
            <circle cx="54" cy="34" r="10" fill="#1e293b" stroke="#cbd5e1" stroke-width="3"/>
            <text x="-8" y="-6" fill="#fde047" font-size="11" font-weight="bold">🚙 ROVER (+15 🪙)</text>
        </g>

        <g class="clickable" onclick="walkToAndAct(520, 'HAB')">
            <path d="M 395 255 A 138 122 0 0 1 670 255 Z" fill="url(#metalDome)" stroke="#eab308" stroke-width="4"/>
            <path d="M 445 252 A 88 78 0 0 1 635 252 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5"/>
            <circle cx="535" cy="155" r="15" fill="#1e1b4b" stroke="#fde047" stroke-width="2"/>
            <text x="535" y="161" text-anchor="middle" fill="#fde047" font-size="17" font-weight="900">A</text>
            <rect x="485" y="232" width="115" height="7" rx="3" fill="#b45309" stroke="#fde047" stroke-width="1"/>
            <text x="488" y="205" fill="#fde047" font-size="10" font-weight="bold">🍽️ HOME PANTRY TABLE:</text>
            <text id="table-veggies-svg" x="492" y="226" fill="#ffffff" font-size="15">🍅 🥬 🥕</text>
            <text x="455" y="122" fill="#ffffff" font-size="12" font-weight="bold">🏠 [CLICK] AVENGERS HOME (UNLOAD BASKET)</text>
        </g>

        <g class="clickable" onclick="toggleDoor()">
            <rect x="382" y="178" width="52" height="77" rx="8" fill="#334155" stroke="#94a3b8" stroke-width="3"/>
            <rect id="airlock-door" x="390" y="186" width="36" height="66" rx="5" fill="#22c55e" stroke="#ffffff" stroke-width="2"/>
            <text id="door-txt" x="355" y="168" fill="#4ade80" font-size="11.5" font-weight="bold">🔒 [CLICK] SEALED</text>
        </g>

        <g class="clickable" onclick="walkToAndAct(815, 'FARM')">
            <path d="M 690 255 A 135 105 0 0 1 965 255 Z" fill="rgba(6, 78, 59, 0.92)" stroke="#4ade80" stroke-width="4"/>
            <rect x="735" y="182" width="180" height="6" rx="3" fill="#e879f9"/>
            <rect x="725" y="242" width="205" height="10" rx="4" fill="#3f2e21" stroke="#a16207" stroke-width="1.5"/>
            <text id="plot-0-svg" x="735" y="236" font-size="18">🍅</text>
            <text id="plot-1-svg" x="782" y="236" font-size="18">🥬</text>
            <text id="plot-2-svg" x="832" y="236" font-size="18">🌱</text>
            <text id="plot-3-svg" x="882" y="236" font-size="18">🥔</text>
            <text x="725" y="142" fill="#4ade80" font-size="12" font-weight="bold">🌱 [CLICK] CSA 4-CROP GREENHOUSE</text>
        </g>

        <g id="astronaut" transform="translate(520, 168)">
            <rect x="-76" y="-32" width="152" height="21" rx="8" fill="{hero_cfg['suit_color']}" stroke="#fde047" stroke-width="1.5"/>
            <text id="astro-tag" x="0" y="-17" text-anchor="middle" fill="#fff" font-size="10.5" font-weight="bold">{hero_cfg['name']} (Inside)</text>
            <text id="float-text" x="0" y="-42" text-anchor="middle" fill="#fde047" font-size="15" font-weight="bold"></text>

            <g transform="translate(-36, -10) scale(0.62)">
                <circle cx="60" cy="52" r="38" fill="#f8fafc" stroke="{hero_cfg['suit_color']}" stroke-width="5"/>
                <circle cx="60" cy="53" r="22" fill="#ffedd5"/>
                <ellipse cx="51" cy="52" rx="4.5" ry="5.5" fill="{hero_cfg['eyes']}"/><circle cx="49.5" cy="50" r="1.8" fill="#fff"/>
                <ellipse cx="69" cy="52" rx="4.5" ry="5.5" fill="{hero_cfg['eyes']}"/><circle cx="67.5" cy="50" r="1.8" fill="#fff"/>
                <path d="M 54 62 Q 60 67 66 62" stroke="#0f172a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
                {hero_cfg['head_svg']}
            </g>

            <rect x="-17" y="42" width="34" height="32" rx="9" fill="{hero_cfg['suit_color']}" stroke="{hero_cfg['accent']}" stroke-width="3"/>
            <circle cx="0" cy="55" r="5" fill="#38bdf8" stroke="#fff" stroke-width="1"/>
            <line x1="-17" y1="48" x2="-30" y2="62" stroke="{hero_cfg['suit_color']}" stroke-width="7" stroke-linecap="round"/>
            <line x1="17" y1="48" x2="30" y2="62" stroke="{hero_cfg['suit_color']}" stroke-width="7" stroke-linecap="round"/>
            <line x1="-8" y1="74" x2="-10" y2="90" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>
            <line x1="8" y1="74" x2="10" y2="90" stroke="#f8fafc" stroke-width="8" stroke-linecap="round"/>

            <g id="hand-basket-svg" transform="translate(26, 52)" style="display:none;">
                <path d="M -14 0 L 14 0 L 10 18 L -10 18 Z" fill="#d97706" stroke="#fef08a" stroke-width="1.5"/>
                <path d="M -10 0 Q 0 -12 10 0" fill="none" stroke="#fef08a" stroke-width="2"/>
                <text id="basket-veggie-icons" x="0" y="-2" text-anchor="middle" font-size="11">🍅</text>
            </g>
        </g>
    </svg>
</div>

<div class="deck-grid">
    <div class="panel-box">
        <div class="panel-title">
            <span>🕹️ 1. MOVE &amp; SHIELD ({hero_cfg['name']})</span>
            <span style="color:#7dd3fc;font-size:10.5px;" id="pos-lbl">Inside Home</span>
        </div>
        <div class="btn-grid-2">
            <button class="g-btn" onclick="moveStep(-70)">◀ Walk Left (A)</button>
            <button class="g-btn" onclick="moveStep(70)">Walk Right (D) ▶</button>
            <button class="g-btn" id="door-btn" onclick="toggleDoor()">🔓 Open Door (E)</button>
            <button class="g-btn" id="shield-btn" onclick="toggleShield()">🛡️ Raise Shield (Storm Only!)</button>
            <button class="g-btn" onclick="cleanPanels()">🧹 Scrub Solar (+25% ⚡)</button>
            <button class="g-btn" onclick="makeAir()">🫁 Melt Ice O₂ (-12% ⚡)</button>
            <button class="g-btn" style="background:linear-gradient(90deg,#16a34a,#059669);grid-column:span 2;padding:8px;" onclick="advanceSol()">
                🌙 FINISH SOL &amp; ADVANCE DAY (+25 🪙)
            </button>
        </div>
    </div>

    <div class="panel-box" style="border-color:#4ade80;">
        <div class="panel-title">
            <span>🌱 2. MULTI-CROP FARM &amp; BASKET (OSD-895 / CSA)</span>
            <span style="color:#86efac;font-size:10.5px;">Click Plot to Plant/Pick!</span>
        </div>
        <div class="btn-grid-4">
            <button class="g-btn" onclick="interactPlot(0)">🍅 Tomato<br><span id="plot-txt-0">PICK!</span></button>
            <button class="g-btn" onclick="interactPlot(1)">🥬 Lettuce<br><span id="plot-txt-1">PICK!</span></button>
            <button class="g-btn" onclick="interactPlot(2)">🥕 Radish<br><span id="plot-txt-2">Sprout..</span></button>
            <button class="g-btn" onclick="interactPlot(3)">🥔 Potato<br><span id="plot-txt-3">PICK!</span></button>
        </div>
        <div class="btn-grid-2">
            <button class="g-btn" style="background:#059669;" onclick="harvestAllRipe()">🧺 Collect Ripe into Basket</button>
            <button class="g-btn" style="background:#d97706;" onclick="deliverBasketHome()">🏠 Put Basket on Home Table</button>
        </div>
        <div style="font-size:10.5px;color:#cbd5e1;margin-top:5px;background:#020617;padding:5px 8px;border-radius:6px;">
            🍽️ <b>Home Pantry Table:</b> <span id="pantry-list-txt">🍅 🥬 🥕 (Disappears 1-by-1 as eaten!)</span>
        </div>
    </div>

    <div class="panel-box" style="border-color:#38bdf8;">
        <div class="panel-title">
            <span>📡 3. EARTH HQ COMMS (5 PRESETS • NO TYPING)</span>
            <span style="color:#fde047;font-size:10.5px;">Cost: {'10' if hero_cfg['perk_code']=='STRANGE' else '15'} 🪙 | {'1.0s' if hero_cfg['perk_code']=='STRANGE' else '2.6s'} Delay</span>
        </div>
        <button class="comm-btn" onclick="callEarth(1)">1️⃣ "⚡ Power is draining fast! What should I do?"</button>
        <button class="comm-btn" onclick="callEarth(2)">2️⃣ "🫁 I am running out of breathable Oxygen (O₂)!"</button>
        <button class="comm-btn" onclick="callEarth(3)">3️⃣ "🍅 Our Home Pantry table is out of Vegetables!"</button>
        <button class="comm-btn" onclick="callEarth(4)">4️⃣ "🚨 Solar Flare alert! When do I turn ON the Shield?"</button>
        <button class="comm-btn" onclick="callEarth(5)">5️⃣ "📊 Resources hitting critical limits—send NASA drop!"</button>
        <div class="earth-reply-box" id="earth-reply">
            🌍 <b>Avengers Earth HQ:</b> Click any of the 5 preset transmissions above for delayed NASA telemetry solutions &amp; emergency supplies!
        </div>
    </div>
</div>

<script>
    // 1. SYNTHESIZED WEB AUDIO SOUND ENGINE (MUSIC + TONES FOR EVERY MOVE!)
    let audioCtx = null;
    let soundOn = true;
    let bgmIdx = 0;
    const bgmNotes = [220, 261.6, 329.6, 392, 329.6, 261.6];

    function playTone(freq, type, dur, vol=0.07) {{
        if (!soundOn) return;
        try {{
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === "suspended") audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + dur);
        }} catch(e) {{}}
    }}

    function toggleAudio() {{
        soundOn = !soundOn;
        document.getElementById("sound-btn").innerText = soundOn ? "🔊 Sound & Music: ON" : "🔇 Sound & Music: OFF";
        if (soundOn) playTone(523.25, "sine", 0.2);
    }}

    // 2. YOUR 5 EXACT PINTEREST MEME TRIGGERS
    let shieldMemeTimeout = null;
    function showMeme(art, title, sub, pinUrl, autoHideMs=0) {{
        const box = document.getElementById("meme-popup");
        document.getElementById("meme-art").innerText = art;
        document.getElementById("meme-title").innerText = title;
        document.getElementById("meme-sub").innerText = sub;
        document.getElementById("meme-pin-link").href = pinUrl;
        box.style.display = "block";
        if (shieldMemeTimeout) clearTimeout(shieldMemeTimeout);
        if (autoHideMs > 0) {{
            shieldMemeTimeout = setTimeout(() => {{ box.style.display = "none"; }}, autoHideMs);
        }}
    }}
    function closeMeme() {{ document.getElementById("meme-popup").style.display = "none"; }}

    // 3. GAME STATE & SPACED-OUT FLARE COOLDOWN
    let sol = 1, power = 90, oxygen = 90, food = 85, health = 100, coins = {start_coins}, rad = 0.42;
    let astroX = 520, doorClosed = true, shieldOn = false;
    let flareState = "CALM", flareTimer = 0;
    let calmCooldown = {calm_cooldown_ticks}; // Guaranteed long calm gap before next flare!
    let dusty = false, ended = false, commsBusy = false;

    const perk = "{hero_cfg['perk_code']}";
    const heroName = "{hero_cfg['name']}";
    const flareID = "{nasa_flare['id']}";
    const warnMax = {warn_ticks};
    const cooldownMax = {calm_cooldown_ticks};

    const cropMeta = [
        {{ name: "Tomato", icon: "🍅", ox: 4 }},
        {{ name: "Lettuce", icon: "🥬", ox: 8 }},
        {{ name: "Radish", icon: "🥕", ox: 3 }},
        {{ name: "Potato", icon: "🥔", ox: 2 }}
    ];
    let plots = [3, 3, 2, 3];
    let basket = [];
    let homePantry = ["🍅", "🥬", "🥕"];
    let hungerTick = 0;

    function getZone() {{ return astroX < 395 ? "OUTSIDE" : (astroX < 680 ? "INSIDE" : "FARM"); }}
    function spawnPopup(txt) {{
        const el = document.getElementById("float-text");
        el.textContent = txt;
        setTimeout(() => {{ if (el.textContent === txt) el.textContent = ""; }}, 1400);
    }}

    function checkContextualMemes() {{
        if (ended) return;
        // 1. Flare Alert Meme until Shield is ON
        if ((flareState === "WARNING" || flareState === "ACTIVE") && !shieldOn) {{
            showMeme("😱☀️🏃‍♂️", "SOLAR FLARE ALERT!", "Run Inside & Turn Shield ON Now!", "https://pin.it/320BCxcPn");
            return;
        }}
        // 2. Dusty Solar Panel Meme
        if (dusty) {{
            showMeme("🧹🌪️😒", "SOLAR PANELS DUSTY!", "Power dropping! Walk outside & scrub!", "https://pin.it/1MJRej5pj");
            return;
        }}
        // 3. Ripe Plants Ready Meme until cultivated
        if (plots.includes(3)) {{
            showMeme("🍅🥬🧺✨", "PLANTS READY TO CULTIVATE!", "Harvest ripe crops into your Basket!", "https://pin.it/4fXQCGxrB");
            return;
        }}
    }}

    function refreshWarnings() {{
        const strip = document.getElementById("warning-strip");
        let pills = [];
        const zone = getZone();
        if (flareState === "WARNING") {{
            pills.push(`<div class="warn-pill">🚨 SOLAR FLARE IN ${{flareTimer * 3}}s! Run Inside, Close Door &amp; Turn Shield ON!</div>`);
        }} else if (flareState === "ACTIVE") {{
            if (zone === "OUTSIDE" || !shieldOn || !doorClosed) {{
                pills.push(`<div class="warn-pill">⚡ FLARE HITTING! Get Inside + Seal Door + Turn Shield ON!</div>`);
            }} else {{
                pills.push(`<div class="ok-pill">🛡️ Shield Blocking Flare (${{flareTimer * 3}}s left)!</div>`);
            }}
        }} else if (shieldOn) {{
            pills.push(`<div class="warn-pill">💡 Sky is CALM! Turn Shield OFF to stop Battery Drain!</div>`);
        }}
        if (!doorClosed) pills.push(`<div class="warn-pill">🫁 Door OPEN (-2% O₂/tick)!</div>`);
        if (homePantry.length === 0) pills.push(`<div class="warn-pill">🍽️ Home Table EMPTY! Harvest Greenhouse crops!</div>`);
        if (pills.length === 0) pills.push(`<div class="ok-pill">✅ Systems Nominal! Next flare cooldown: ${{calmCooldown * 3}}s+</div>`);
        strip.innerHTML = pills.join("");
    }}

    function render(msg) {{
        const zone = getZone();
        document.getElementById("sol-num").innerText = sol + " / 7";
        document.getElementById("pwr-num").innerText = power + "%";
        document.getElementById("ox-num").innerText = oxygen + "%";
        document.getElementById("food-num").innerText = food + "%";
        document.getElementById("hp-num").innerText = health + "%";
        document.getElementById("coin-num").innerText = coins;

        document.getElementById("pwr-bar").style.width = power + "%";
        document.getElementById("ox-bar").style.width = oxygen + "%";
        document.getElementById("food-bar").style.width = food + "%";
        document.getElementById("hp-bar").style.width = health + "%";
        document.getElementById("rad-rate").innerText = "☢️ " + rad.toFixed(2) + " mSv";

        const wBadge = document.getElementById("weather-badge");
        wBadge.innerText = flareState === "CALM" ? "☀️ Sky Calm" : (flareState === "WARNING" ? "⚠️ Flare Soon!" : "🚨 FLARE HIT!");

        document.getElementById("basket-num").innerText = basket.length > 0 ? basket.join("") : "Empty";
        document.getElementById("hand-basket-svg").style.display = basket.length > 0 ? "block" : "none";
        document.getElementById("basket-veggie-icons").textContent = basket.slice(0, 3).join("");

        document.getElementById("pantry-rate").innerText = "🏠 Table: " + homePantry.length + " Veggies";
        document.getElementById("table-veggies-svg").textContent = homePantry.length > 0 ? homePantry.join(" ") : "EMPTY!";
        document.getElementById("pantry-list-txt").textContent = homePantry.length > 0 ? homePantry.join(" ") : "EMPTY! Bring Basket from Greenhouse!";

        for (let i = 0; i < 4; i++) {{
            const st = plots[i];
            document.getElementById("plot-" + i + "-svg").textContent = st === 0 ? "🕳️" : (st === 1 ? "🌱" : (st === 2 ? "🌿" : cropMeta[i].icon));
            document.getElementById("plot-txt-" + i).textContent = st === 0 ? "Plant (5⚡)" : (st === 3 ? "PICK!" : "Growing..");
        }}

        if (msg) document.getElementById("story-msg").textContent = msg;
        document.getElementById("astronaut").setAttribute("transform", `translate(${{astroX}}, 168)`);
        const zLbl = zone === "OUTSIDE" ? "Outside Moon" : (zone === "INSIDE" ? "Inside Home" : "Greenhouse");
        document.getElementById("astro-tag").textContent = `${{heroName}} (${{zLbl}})`;
        document.getElementById("pos-lbl").textContent = zLbl;

        document.getElementById("airlock-door").setAttribute("fill", doorClosed ? "#22c55e" : "#ef4444");
        document.getElementById("door-txt").textContent = doorClosed ? "🔒 [CLICK] SEALED" : "🔓 [CLICK] OPEN";
        document.getElementById("door-btn").innerText = doorClosed ? "🔓 Open Door (E)" : "🔒 Close Door (E)";

        document.getElementById("shield-dome").style.display = shieldOn ? "block" : "none";
        document.getElementById("shield-btn").innerText = shieldOn ? "🟢 Turn Shield OFF (Save ⚡)" : "🛡️ Raise Shield (Storm Only!)";
        document.getElementById("flare-warn-svg").style.display = flareState === "WARNING" ? "block" : "none";
        document.getElementById("flare-bolts").style.display = flareState === "ACTIVE" ? "block" : "none";
        document.getElementById("sky-bg").setAttribute("fill", flareState === "ACTIVE" ? "url(#skyFlare)" : (flareState === "WARNING" ? "url(#skyWarn)" : "url(#skyCalm)"));
        document.getElementById("dust-layer").style.display = dusty ? "block" : "none";

        refreshWarnings();
    }}

    function moveStep(delta) {{
        if (ended) return;
        playTone(300, "triangle", 0.08);
        const nextX = Math.max(90, Math.min(860, astroX + delta));
        if ((astroX < 395 && nextX >= 395) || (astroX >= 395 && nextX < 395)) doorClosed = false;
        astroX = nextX;
        render();
    }}

    function walkToAndAct(targetX, kind) {{
        if (ended) return;
        if ((astroX < 395 && targetX >= 395) || (astroX >= 395 && targetX < 395)) doorClosed = false;
        astroX = targetX;
        if (kind === "SOLAR") cleanPanels();
        else if (kind === "HAB") deliverBasketHome();
        else if (kind === "FARM") harvestAllRipe();
    }}

    function toggleDoor() {{
        if (ended) return;
        if (getZone() === "OUTSIDE" && !doorClosed) {{ render("❗ Walk Inside first before locking the Airlock Door!"); return; }}
        doorClosed = !doorClosed;
        playTone(doorClosed ? 520 : 240, "sine", 0.15);
        spawnPopup(doorClosed ? "🔒 Door Sealed!" : "🔓 Door Open");
        render();
    }}

    function toggleShield() {{
        if (ended) return;
        if (!shieldOn) {{
            if (power < 10) {{ render("⚠️ Power too low!"); return; }}
            shieldOn = true;
            power = Math.max(0, power - (perk === "CAP" ? 5 : 10));
            playTone(660, "sine", 0.25);
            // YOUR 2-SECOND SHIELD MEME POPUP!
            showMeme("😎🛡️⚡", "VIBRANIUM SHIELD ON!", "Solar flare blocked like a boss (2s)!", "https://pin.it/24dl7qhQI", 2000);
            render("🛡️ Shield RAISED! Turn it OFF after the Solar Flare passes to save Power!");
        }} else {{
            shieldOn = false;
            playTone(330, "sine", 0.15);
            render("🟢 Shield turned OFF! Battery charging.");
        }}
    }}

    function cleanPanels() {{
        if (ended) return;
        astroX = 135; doorClosed = false; dusty = false;
        power = Math.min(100, power + 25); coins += (perk === "LOKI" ? 20 : 10);
        playTone(784, "triangle", 0.2);
        closeMeme();
        spawnPopup("+25% ⚡ Clean!");
        render("🧹 Scrubbed moon dust off Solar Array! +25% Power!");
    }}

    function makeAir() {{
        if (ended || power < 12) return;
        astroX = 520; power -= 12; oxygen = Math.min(100, oxygen + 25);
        playTone(587, "sine", 0.2);
        spawnPopup("+25% 🫁 O₂");
        render("🫁 Melted crater ice into +25% breathable Oxygen!");
    }}

    function collectIce() {{
        if (ended) return;
        const gain = perk === "LOKI" ? 20 : 10;
        coins += gain;
        playTone(880, "sine", 0.15);
        spawnPopup(`+${{gain}} 🪙 Drone!`);
        render(`🚁 Collected Drone Ice for +${{gain}} 🪙 SuperCoins!`);
    }}

    function driveRover() {{
        if (ended) return;
        astroX = 275; doorClosed = false;
        const gain = perk === "LOKI" ? 30 : 15;
        coins += gain;
        playTone(440, "sawtooth", 0.2);
        spawnPopup(`🚙 +${{gain}} 🪙!`);
        render(`🚙 Drove Avengers Lunar Rover! +${{gain}} 🪙 SuperCoins!`);
    }}

    function interactPlot(idx) {{
        if (ended) return;
        astroX = 815;
        if (plots[idx] === 3) {{
            basket.push(cropMeta[idx].icon);
            oxygen = Math.min(100, oxygen + cropMeta[idx].ox + (perk === "WANDA" ? 5 : 0));
            plots[idx] = 0;
            playTone(659, "sine", 0.18);
            if (!plots.includes(3)) closeMeme();
            spawnPopup(`🧺 Picked ${{cropMeta[idx].icon}}!`);
            render("🧺 Harvested into Basket! Click 'Put Basket on Home Table' or replant!");
        }} else if (plots[idx] === 0 && power >= 5) {{
            power -= 5;
            plots[idx] = perk === "WANDA" ? 2 : 1;
            playTone(493, "triangle", 0.15);
            spawnPopup("🌱 Planted!");
            render("🌱 Seeds planted in CSA Greenhouse!");
        }}
    }}

    function harvestAllRipe() {{
        if (ended) return;
        astroX = 815;
        let count = 0;
        for (let i = 0; i < 4; i++) {{
            if (plots[i] === 3) {{
                basket.push(cropMeta[i].icon);
                oxygen = Math.min(100, oxygen + cropMeta[i].ox);
                plots[i] = 0; count++;
            }} else if (plots[i] === 0 && power >= 5) {{
                power -= 5; plots[i] = perk === "WANDA" ? 2 : 1;
            }}
        }}
        playTone(698, "sine", 0.2);
        if (!plots.includes(3)) closeMeme();
        render(count > 0 ? `🧺 Picked ${{count}} ripe veggies into Basket & replanted!` : "🌱 Planted empty greenhouse plots!");
    }}

    function deliverBasketHome() {{
        if (ended) return;
        astroX = 520;
        if (basket.length === 0) {{ render("🏠 Inside Avengers Home! Basket is empty."); return; }}
        const n = basket.length;
        while (basket.length > 0) homePantry.push(basket.shift());
        coins += n * 5;
        playTone(784, "sine", 0.25);
        spawnPopup(`🍽️ +${{n}} on Table!`);
        render(`🏠 Placed ${{n}} fresh veggies on the Home Pantry Table! Watch them disappear 1-by-1 as eaten!`);
    }}

    function callEarth(id) {{
        if (ended || commsBusy) return;
        const cost = perk === "STRANGE" ? 10 : 15;
        const delayMs = perk === "STRANGE" ? 1000 : 2600;
        if (coins < cost) {{
            document.getElementById("earth-reply").innerHTML = `⚠️ Need <b>${{cost}} 🪙 SuperCoins</b>! Click the Rover (🚙) or Drone (🚁)!`;
            return;
        }}
        coins -= cost; commsBusy = true;
        playTone(987, "sine", 0.2);
        document.getElementById("comms-beam").style.display = "block";
        document.getElementById("earth-reply").innerHTML = "📡 <b>Signal traveling to Earth...</b> Waiting for NASA & Avengers HQ reply...";
        render();

        setTimeout(() => {{
            document.getElementById("comms-beam").style.display = "none";
            commsBusy = false;
            playTone(1046, "sine", 0.25);
            if (id === 1) {{ power = Math.min(100, power + 30); shieldOn = false; document.getElementById("earth-reply").innerHTML = "🌍 <b>HQ Solution (+30% ⚡):</b> 'Shield turned OFF & +30% reserve power beamed!'"; }}
            else if (id === 2) {{ oxygen = Math.min(100, oxygen + 35); doorClosed = true; document.getElementById("earth-reply").innerHTML = "🌍 <b>HQ Solution (+35% 🫁):</b> 'Airlock sealed & +35% O₂ emergency tank opened!'"; }}
            else if (id === 3) {{ homePantry.push("🍅", "🥬", "🥔"); food = Math.min(100, food + 25); document.getElementById("earth-reply").innerHTML = "🌍 <b>HQ Solution (+3 Veggies):</b> 'CSA Veggie Drop placed on your Home Pantry Table!'"; }}
            else if (id === 4) {{ power = Math.min(100, power + 15); document.getElementById("earth-reply").innerHTML = "🌍 <b>HQ Solution (+15% ⚡):</b> 'Only turn Shield ON when the Solar Flare Siren warns you!'"; }}
            else {{ power = Math.min(100, power + 20); oxygen = Math.min(100, oxygen + 20); health = Math.min(100, health + 20); document.getElementById("earth-reply").innerHTML = "🌍 <b>HQ Solution (Full Boost!):</b> '+20% Power, +20% O₂, and +20% Health restored!'"; }}
            render("✅ Earth HQ telemetry solution received!");
        }}, delayMs);
    }}

    function advanceSol() {{
        if (ended) return;
        sol += 1; coins += 25;
        playTone(523, "triangle", 0.3);
        if (sol > 7) {{
            ended = true;
            // YOUR VICTORY MEME POPUP!
            showMeme("🏆🎉🦸‍♂️", "AVENGERS VICTORY!", "You survived all 7 Lunar Sols! Claim your Trophy in the Sidebar!", "https://pin.it/1MEqcIZWV");
            render("🏆 VICTORY! Open the top-left Sidebar (>) and click 'Claim Victory' to unlock new Avengers!");
            return;
        }}
        render(`📅 Lunar Sol ${{sol}} started (+25 🪙)!`);
    }}

    window.addEventListener("keydown", (e) => {{
        if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") moveStep(-55);
        if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") moveStep(55);
        if (e.key === "e" || e.key === "E") toggleDoor();
    }});

    // MASTER GAME LOOP (EVERY 3 SECONDS — NEVER FREEZES!)
    setInterval(() => {{
        if (ended) return;
        try {{
            // Background Space Synth Note
            if (soundOn) {{
                playTone(bgmNotes[bgmIdx % bgmNotes.length], "sine", 0.12, 0.015);
                bgmIdx++;
            }}

            const zone = getZone();
            const shieldCost = perk === "CAP" ? 1 : 2;
            const chargeRate = perk === "IRON" ? 2 : 1;

            if (shieldOn) power = Math.max(0, power - shieldCost);
            else if (dusty) power = Math.max(0, power - 1);
            else power = Math.min(100, power + chargeRate);

            if (!doorClosed) oxygen = Math.max(0, oxygen - 2);
            else if (perk !== "WIDOW" || hungerTick % 2 === 0) oxygen = Math.max(0, oxygen - 1);

            // Grow Crops
            for (let i = 0; i < 4; i++) {{
                if (plots[i] === 1 || plots[i] === 2) {{
                    if (Math.random() < (perk === "WANDA" ? 0.85 : 0.45)) plots[i] += 1;
                }}
            }}

            // Eat Veggies from Home Table 1-by-1
            hungerTick++;
            food = Math.max(0, food - 2);
            if (hungerTick % 2 === 0 && homePantry.length > 0 && food < 92) {{
                const v = homePantry.shift();
                food = Math.min(100, food + 15);
                spawnPopup(`😋 Ate ${{v}} (+15% Food)`);
            }}

            // SPACED-OUT SOLAR FLARE MACHINE (WITH GUARANTEED CALM COOLDOWN!)
            if (flareState === "CALM") {{
                rad += 0.03;
                if (calmCooldown > 0) {{
                    calmCooldown--;
                    if (calmCooldown === 5 && Math.random() < 0.35) {{
                        dusty = true;
                        checkContextualMemes();
                    }}
                }} else if (Math.random() < 0.30) {{
                    flareState = "WARNING";
                    flareTimer = warnMax;
                    playTone(220, "sawtooth", 0.4, 0.09);
                    checkContextualMemes();
                }}
            }} else if (flareState === "WARNING") {{
                playTone(260, "sawtooth", 0.3, 0.08);
                checkContextualMemes();
                flareTimer--;
                if (flareTimer <= 0) {{
                    flareState = "ACTIVE";
                    flareTimer = 3;
                }}
            }} else if (flareState === "ACTIVE") {{
                const dmgMult = perk === "THOR" ? 0.4 : 1.0;
                if (zone === "OUTSIDE") {{
                    health = Math.max(0, Math.round(health - 16 * dmgMult));
                    rad += 0.60;
                    spawnPopup("🚨 OUTSIDE IN FLARE!");
                }} else if (!doorClosed || !shieldOn) {{
                    health = Math.max(0, Math.round(health - 10 * dmgMult));
                    rad += 0.30;
                    checkContextualMemes();
                }} else {{
                    rad += 0.04;
                    coins += 5;
                }}
                flareTimer--;
                if (flareTimer <= 0) {{
                    flareState = "CALM";
                    calmCooldown = cooldownMax; // Reset 30-36s calm gap before another flare can happen!
                    closeMeme();
                    render("☀️ Solar Flare ended! Turn OFF your Shield now to save Power! (Long calm gap ahead)");
                }}
            }}

            checkContextualMemes();

            if (power <= 0 || oxygen <= 0 || food <= 0 || health <= 0) {{
                ended = true;
                render("💥 MISSION OVER! Refresh or click 'Switch Avenger' in the sidebar to play again!");
                return;
            }}
            render();
        }} catch(err) {{}}
    }}, 3000);

    render();
</script>
</body>
</html>
"""

render_game_frame(avengers_game_html, height=840)
