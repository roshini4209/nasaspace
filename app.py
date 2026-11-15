# ==============================================================================
# AVENGERS LUNAR OUTPOST 3D: ARTEMIS SURVIVAL — CHALLENGE-MAXED ELITE (app.py)
# Unified Single-File Streamlit + Three.js WebGL + WebAudio + Live NASA APIs
# ==============================================================================
import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

st.set_page_config(
    page_title="Avengers Lunar Outpost 3D | NASA Space Apps 2026",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. HIGH-CONTRAST SPACE UI STYLING
# ==============================================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #17153b 0%, #090d1f 55%, #020617 100%) !important;
    color: #f8fafc !important;
}
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 0.6rem !important;
    max-width: 98% !important;
}
h1, h2, h3, h4, h5, h6, p, span, div, label, li {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b18 0%, #0f172a 100%) !important;
    border-right: 2px solid #eab308 !important;
}
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: #0f172a !important;
    color: #fde047 !important;
    border: 2px solid #38bdf8 !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
}
.stButton > button {
    background: linear-gradient(90deg, #dc2626 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 2px solid #fde047 !important;
    border-radius: 14px !important;
    padding: 10px 16px !important;
    font-size: 0.95rem !important;
    font-weight: 900 !important;
    width: 100%;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.5) !important;
}
.stButton > button:hover {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.75) !important;
    transform: translateY(-2px);
}
.stButton > button:disabled {
    background: #1e293b !important;
    border-color: #475569 !important;
    color: #94a3b8 !important;
    opacity: 0.65 !important;
}
.elite-card {
    background: rgba(15, 23, 42, 0.92);
    border: 2px solid #eab308;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.75);
}
.brief-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 2px solid #38bdf8;
    border-radius: 16px;
    padding: 16px;
    height: 100%;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}
.nasa-pill {
    display: inline-block;
    background: rgba(14, 165, 233, 0.18);
    border: 1.5px solid #38bdf8;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.84rem;
    font-weight: 800;
    color: #7dd3fc !important;
    margin-bottom: 8px;
}
.live-pill {
    display: inline-block;
    background: rgba(22, 163, 74, 0.22);
    border: 1.5px solid #4ade80;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 800;
    color: #86efac !important;
}
.arch-pill {
    display: inline-block;
    background: rgba(202, 138, 4, 0.22);
    border: 1.5px solid #facc15;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 800;
    color: #fef08a !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LIVE NASA OPEN DATA FEEDS (DONKI FLR + CME + EPIC) WITH TRANSPARENT FALLBACK
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_nasa_donki():
    """Fetches real Solar Flare (FLR) & Coronal Mass Ejection (CME) data from NASA DONKI API."""
    flr_result = {
        "id": "2024-05-14T16:46:00-FLR-001",
        "class": "X8.7",
        "peak": "2024-05-14T16:51Z",
        "source": "ARCHIVED NASA DONKI DATASET (Verified Historical Event)",
        "is_live": False
    }
    cme_result = {
        "id": "2024-05-14T17:12:00-CME-001",
        "speed": 1240,
        "note": "Fast coronal mass ejection recorded in NASA DONKI archive.",
        "source": "ARCHIVED NASA DONKI DATASET",
        "is_live": False
    }
    try:
        r_flr = requests.get("https://api.nasa.gov/DONKI/FLR?api_key=DEMO_KEY", timeout=4)
        if r_flr.status_code == 200:
            data = r_flr.json()
            if isinstance(data, list) and len(data) > 0:
                latest = data[-1]
                flr_result = {
                    "id": latest.get("flrID", "LIVE-DONKI-FLR"),
                    "class": latest.get("classType", "M2.4"),
                    "peak": latest.get("peakTime", "Live Telemetry"),
                    "source": "LIVE NASA DONKI FLR API",
                    "is_live": True
                }
    except Exception:
        pass

    try:
        r_cme = requests.get("https://api.nasa.gov/DONKI/CME?api_key=DEMO_KEY", timeout=4)
        if r_cme.status_code == 200:
            data = r_cme.json()
            if isinstance(data, list) and len(data) > 0:
                latest_c = data[-1]
                analyses = latest_c.get("cmeAnalyses") or []
                spd = analyses[0].get("speed", 780) if analyses else 780
                cme_result = {
                    "id": latest_c.get("activityID", "LIVE-DONKI-CME"),
                    "speed": int(spd) if spd else 780,
                    "note": (latest_c.get("note") or "Active solar wind plasma ejection logged by NASA SWRC.")[:160],
                    "source": "LIVE NASA DONKI CME API",
                    "is_live": True
                }
    except Exception:
        pass

    return flr_result, cme_result

@st.cache_data(ttl=1800)
def fetch_nasa_epic():
    """Fetches real DSCOVR EPIC full-disc Earth telemetry metadata from NASA."""
    try:
        r = requests.get("https://api.nasa.gov/EPIC/api/natural/images?api_key=DEMO_KEY", timeout=4)
        if r.status_code == 200:
            items = r.json()
            if isinstance(items, list) and len(items) > 0:
                latest = items[0]
                date_part = latest.get("date", "2026-01-01 00:00:00").split(" ")[0].replace("-", "/")
                img_name = latest.get("image", "")
                img_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date_part}/png/{img_name}.png"
                return {
                    "caption": latest.get("caption", "DSCOVR EPIC Earth full-disc observation from L1 Lagrange point."),
                    "date": latest.get("date", "Latest"),
                    "image_url": img_url,
                    "source": "LIVE NASA EPIC API",
                    "is_live": True
                }
    except Exception:
        pass
    return {
        "caption": "DSCOVR EPIC observes sunlit Earth from the Earth-Sun L1 Lagrange point (~1.5 million km away).",
        "date": "Archived Reference Record",
        "image_url": "",
        "source": "ARCHIVED NASA EPIC METADATA (FALLBACK)",
        "is_live": False
    }

nasa_flare, nasa_cme = fetch_nasa_donki()
nasa_epic = fetch_nasa_epic()

# ==============================================================================
# 3. AVENGERS ROSTER, 3D COSMETICS & GAMEPLAY PERKS
# ==============================================================================
HEROES = {
    "CAPTAIN_AMERICA": {
        "name": "Captain America",
        "title": "First Avenger • Shield Tactician",
        "unlock_wins": 0,
        "unlock_coins": 0,
        "perk_code": "CAP",
        "perk_desc": "🛡️ Vibranium Shield: Shield drains 50% less Power!",
        "suit_color": "#1d4ed8",
        "accent": "#ef4444",
        "eyes": "#38bdf8",
        "head_svg": "<path d='M 24 50 A 36 36 0 0 1 96 50 Z' fill='#1d4ed8' stroke='#ffffff' stroke-width='2'/><text x='60' y='38' text-anchor='middle' fill='#ffffff' font-size='18' font-weight='900'>A</text>"
    },
    "NATASHA": {
        "name": "Natasha Romanoff",
        "title": "Black Widow • Agile EVA Scout",
        "unlock_wins": 0,
        "unlock_coins": 0,
        "perk_code": "WIDOW",
        "perk_desc": "🕷️ Widow Agility: +25% Run Speed, 40% less O₂ use & +20 🪙!",
        "suit_color": "#1e293b",
        "accent": "#ef4444",
        "eyes": "#22c55e",
        "head_svg": "<path d='M 24 58 Q 26 14 60 16 Q 94 14 96 58 L 88 34 Q 60 22 32 34 Z' fill='#b91c1c'/><circle cx='24' cy='52' r='9' fill='#b91c1c'/><circle cx='96' cy='52' r='9' fill='#b91c1c'/>"
    },
    "IRON_MAN": {
        "name": "Iron Man",
        "title": "Tony Stark • Arc Reactor Engineer",
        "unlock_wins": 1,
        "unlock_coins": 60,
        "perk_code": "IRON",
        "perk_desc": "⚡ Arc Reactor: 2x Solar Charging & Jet-Boosted Jumps!",
        "suit_color": "#dc2626",
        "accent": "#facc15",
        "eyes": "#38bdf8",
        "head_svg": "<rect x='30' y='18' width='60' height='54' rx='18' fill='#b91c1c' stroke='#facc15' stroke-width='3'/><polygon points='38,22 82,22 76,58 44,58' fill='#facc15'/><rect x='40' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/><rect x='66' y='40' width='14' height='6' rx='2' fill='#e0f2fe'/>"
    },
    "THOR": {
        "name": "Thor Odinson",
        "title": "God of Thunder • Storm Tank",
        "unlock_wins": 1,
        "unlock_coins": 60,
        "perk_code": "THOR",
        "perk_desc": "🔨 Stormbreaker: Takes 60% less Solar Flare Radiation!",
        "suit_color": "#475569",
        "accent": "#ef4444",
        "eyes": "#38bdf8",
        "head_svg": "<path d='M 24 58 Q 28 14 60 16 Q 92 14 96 58 L 86 34 Q 60 24 34 34 Z' fill='#facc15'/><path d='M 20 42 L 10 22 L 26 32 Z' fill='#cbd5e1'/><path d='M 100 42 L 110 22 L 94 32 Z' fill='#cbd5e1'/>"
    },
    "DR_STRANGE": {
        "name": "Dr. Strange",
        "title": "Master of the Mystic Arts",
        "unlock_wins": 2,
        "unlock_coins": 80,
        "perk_code": "STRANGE",
        "perk_desc": "⏳ Time Stone: 1.0s Earth Radio Delay & cheaper drops!",
        "suit_color": "#1e3a8a",
        "accent": "#dc2626",
        "eyes": "#4ade80",
        "head_svg": "<path d='M 28 46 Q 30 16 60 16 Q 90 16 92 46 L 84 32 Q 60 22 36 32 Z' fill='#1e293b'/><path d='M 26 42 L 34 42' stroke='#e2e8f0' stroke-width='4'/><path d='M 86 42 L 94 42' stroke='#e2e8f0' stroke-width='4'/>"
    },
    "WANDA": {
        "name": "Wanda Maximoff",
        "title": "Scarlet Witch • Chaos Botanist",
        "unlock_wins": 2,
        "unlock_coins": 80,
        "perk_code": "WANDA",
        "perk_desc": "🔮 Chaos Magic: Crops grow 2x faster & add +6% bonus O₂!",
        "suit_color": "#991b1b",
        "accent": "#f43f5e",
        "eyes": "#ef4444",
        "head_svg": "<path d='M 22 60 Q 26 16 60 16 Q 94 16 98 60 L 86 34 Q 60 24 34 34 Z' fill='#7c2d12'/><polygon points='42,38 50,18 60,30 70,18 78,38' fill='#ef4444' stroke='#fca5a5' stroke-width='1.5'/>"
    },
    "LOKI": {
        "name": "Loki",
        "title": "God of Mischief • Coin Master",
        "unlock_wins": 2,
        "unlock_coins": 90,
        "perk_code": "LOKI",
        "perk_desc": "🐍 Glorious Purpose: 2x SuperCoins & +50% EVA Science!",
        "suit_color": "#15803d",
        "accent": "#eab308",
        "eyes": "#22c55e",
        "head_svg": "<path d='M 22 58 Q 24 18 60 18 Q 96 18 98 58 Z' fill='#0f172a'/><path d='M 34 40 Q 60 50 86 40 L 82 28 Q 60 38 38 28 Z' fill='#eab308' stroke='#fef08a' stroke-width='1.5'/><path d='M 40 32 Q 22 6 44 4 Q 34 18 46 30 Z' fill='#eab308'/><path d='M 80 32 Q 98 6 76 4 Q 86 18 74 30 Z' fill='#eab308'/>"
    }
}

SCENARIOS = {
    "STANDARD": {
        "name": "🌕 Standard 7-Sol Artemis Survival",
        "desc": "Balanced NASA DONKI solar flares, dust storms, CSA crop farming, and 3 Mission Dilemmas."
    },
    "STORM_GAUNTLET": {
        "name": "☀️ X-Class Solar Storm Gauntlet",
        "desc": "Frequent intense DONKI flares! Tests rapid shelter runs and battery budgeting."
    },
    "SCIENCE_EXPEDITION": {
        "name": "🔬 Shackleton Science Expedition",
        "desc": "Focus on high-risk EVA core-sample research (trading O₂ for Science Score)!"
    }
}

# ==============================================================================
# 4. SESSION STATE
# ==============================================================================
DEFAULT_STATE = {
    "av_stage": "STEP_1_HERO_SELECT",
    "age_str": "",
    "valid_age": 10,
    "age_tier": "10-12 Commander",
    "scenario_key": "STANDARD",
    "hero_key": "CAPTAIN_AMERICA",
    "games_won": 0,
    "bank_coins": 40,
    "unlocked_heroes": ["CAPTAIN_AMERICA", "NATASHA"],
    "unlock_msg": "",
    "unlock_ok": False,
    "claimed_codes": []
}
for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.hero_key not in HEROES:
    st.session_state.hero_key = "CAPTAIN_AMERICA"

hero_cfg = HEROES[st.session_state.hero_key]

# ==============================================================================
# 5. SIDEBAR NAVIGATION (4 CLEAN MODULES)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🛡️ **ARTEMIS COMMAND HUB**")
    st.markdown(f"**Hero:** `{hero_cfg['name']}`")
    st.markdown(f"**Mode:** `{st.session_state.age_tier}`")
    st.markdown(f"**Vault:** `🏆 {st.session_state.games_won} Wins` | `🪙 {st.session_state.bank_coins}`")
    st.markdown("---")
    side_page = st.radio(
        "📂 **Switch Module:**",
        [
            "🎮 1. 3D Lunar Outpost Game",
            "📈 2. Engineering Trade-Off Lab",
            "🛰️ 3. Live NASA & Partner Data",
            "👩‍🏫 4. Classroom & Parent Guide"
        ]
    )
    st.markdown("---")
    st.markdown("**🏆 Claim 7-Sol Victory Code:**")
    claim_code = st.text_input("Victory Code:", placeholder="e.g. ARTEMIS-WIN-742", label_visibility="collapsed")
    if st.button("🏅 Verify & Claim Trophy"):
        code_clean = claim_code.strip().upper()
        if code_clean.startswith("ARTEMIS-WIN-") and len(code_clean) >= 15:
            if code_clean in st.session_state.claimed_codes:
                st.warning("⚠️ Code already claimed! Complete another 7-Sol run for a new code.")
            else:
                st.session_state.claimed_codes.append(code_clean)
                st.session_state.games_won += 1
                st.session_state.bank_coins += 60
                st.success("🎉 Verified! +1 🏆 Trophy & +60 🪙 SuperCoins added!")
        else:
            st.error("❌ Invalid code! Beat all 7 Lunar Sols in the 3D game to earn a Victory Code.")

    st.markdown("---")
    if st.button("🦸 Step 1: Hero Locker & Scenario"):
        st.session_state.av_stage = "STEP_1_HERO_SELECT"
        st.rerun()
    if st.button("📖 Step 2: Controls & Briefing"):
        st.session_state.av_stage = "STEP_2_BRIEFING"
        st.rerun()

# ==============================================================================
# MODULE 2: ENGINEERING TRADE-OFF MATH LAB & RADIATION COMPARATOR
# ==============================================================================
if side_page == "📈 2. Engineering Trade-Off Lab":
    st.title("📈 Lunar Outpost Engineering & Trade-Off Math Lab")
    st.info("👈 Switch back to **'🎮 1. 3D Lunar Outpost Game'** in the left sidebar anytime to play!")

    st.markdown("""
    <div class='elite-card'>
        <h4>⚖️ Interactive Artemis Resource Simulator ("No Free Lunch")</h4>
        <p>Test how real mission engineers balance <b>Radiation Shielding</b>, <b>Hydroponic Grow Lights</b>, and <b>EVA Research Oxygen</b> across 7 Lunar Sols at Shackleton Crater.</p>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        shield_pct = st.slider("🛡️ Shield Duty (%)", 0, 100, 35)
    with s2:
        farm_pct = st.slider("🌱 CSA Grow-Lights (%)", 10, 100, 50)
    with s3:
        eva_hrs = st.slider("🔬 Daily EVA Science (hrs)", 0, 6, 2)
    with s4:
        dust_pct = st.slider("🌪️ Solar Dust Loss (%)", 0, 60, 15)

    sols = list(range(1, 8))
    pwr_c, ox_c, rad_c, sci_c = [], [], [], []
    p, o, r_tot, sci_tot = 92.0, 92.0, 0.42, 0
    for s_i in sols:
        solar_in = 32.0 * (1.0 - dust_pct / 100.0)
        p = max(0.0, min(100.0, p + solar_in - (shield_pct * 0.34 + farm_pct * 0.15 + eva_hrs * 1.5 + 4.0)))
        o = max(0.0, min(100.0, o + (farm_pct * 0.14) - (8.0 + eva_hrs * 2.4)))
        flare_burst = 1.8 if s_i in (3, 6) else 0.0
        r_tot += 0.42 + (eva_hrs * 0.08) + flare_burst * (1.0 - shield_pct / 100.0)
        sci_tot += eva_hrs * 75
        pwr_c.append(round(p, 1))
        ox_c.append(round(o, 1))
        rad_c.append(round(r_tot, 2))
        sci_c.append(sci_tot)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚡ Power & 🫁 Oxygen Balance (%)")
        st.line_chart(pd.DataFrame({"Sol": sols, "Battery Power (%)": pwr_c, "Oxygen (%)": ox_c}).set_index("Sol"))
    with c2:
        st.subheader("☢️ Cumulative Radiation Dose (mSv) vs Safe Limit")
        st.line_chart(pd.DataFrame({"Sol": sols, "Crew Radiation (mSv)": rad_c, "7-Sol Guideline (mSv)": [4.5]*7}).set_index("Sol"))

    st.subheader("🔎 Real-World Radiation Perspective (What Does mSv Mean?)")
    rad_comp = pd.DataFrame({
        "Exposure Scenario": [
            "1 Day on Earth (Sea Level)",
            "1 Dental X-Ray",
            "1 Lunar Sol (NASA RadLab Baseline)",
            "Your 7-Sol Projected Mission",
            "Unshielded X-Class Solar Flare"
        ],
        "Dose (mSv)": [0.008, 0.01, 0.42, rad_c[-1], 6.5]
    }).set_index("Exposure Scenario")
    st.bar_chart(rad_comp)

    st.markdown(f"""
    <div class='elite-card'>
        <b>🧮 Projected Sol 7 Results:</b> Battery <code>{pwr_c[-1]}%</code> | Oxygen <code>{ox_c[-1]}%</code> | Radiation <code>{rad_c[-1]} mSv</code> | Science Collected <code>{sci_c[-1]} pts</code><br>
        <b>📡 Real Physics Formula:</b> Earth-Moon round-trip radio delay = <code>(2 × 384,400 km) / 299,792 km/s = 2.56 seconds</code>.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# MODULE 3: LIVE NASA & SPACE AGENCY PARTNER DATA VERIFICATION
# ==============================================================================
if side_page == "🛰️ 3. Live NASA & Partner Data":
    st.title("🛰️ Traceable NASA & 2026 Space Agency Partner Data")
    st.info("👈 Switch back to **'🎮 1. 3D Lunar Outpost Game'** in the left sidebar anytime to play!")

    flr_badge = "<span class='live-pill'>🟢 LIVE NASA API CONNECTED</span>" if nasa_flare["is_live"] else "<span class='arch-pill'>🟡 ARCHIVED NASA DATASET (TRANSPARENT FALLBACK)</span>"
    cme_badge = "<span class='live-pill'>🟢 LIVE NASA API CONNECTED</span>" if nasa_cme["is_live"] else "<span class='arch-pill'>🟡 ARCHIVED NASA DATASET (TRANSPARENT FALLBACK)</span>"

    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown(f"""
        <div class='elite-card'>
            {flr_badge}
            <h4>☀️ 1. NASA DONKI Solar Flare Feed (FLR)</h4>
            <p><b>Endpoint:</b> <code>api.nasa.gov/DONKI/FLR</code><br>
            <b>Event ID:</b> <code>{nasa_flare['id']}</code><br>
            <b>Flare Class:</b> <code>{nasa_flare['class']}</code> | <b>Peak:</b> <code>{nasa_flare['peak']}</code><br>
            <b>Source:</b> {nasa_flare['source']}<br>
            <b>Gameplay Link:</b> Sets the live storm intensity and triggers 3D solar particle waves with warning sirens.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_n2:
        st.markdown(f"""
        <div class='elite-card'>
            {cme_badge}
            <h4>🌊 2. NASA DONKI Coronal Mass Ejection Feed (CME)</h4>
            <p><b>Endpoint:</b> <code>api.nasa.gov/DONKI/CME</code><br>
            <b>CME ID:</b> <code>{nasa_cme['id']}</code> | <b>Speed:</b> <code>{nasa_cme['speed']} km/s</code><br>
            <b>Summary:</b> {nasa_cme['note']}<br>
            <b>Gameplay Link:</b> Drives our Sol 4 Mission Control Dilemma (Pre-Charge Magnetic Shielding vs. Grow-Light Power).</p>
        </div>
        """, unsafe_allow_html=True)

    col_n3, col_n4 = st.columns(2)
    with col_n3:
        st.markdown("""
        <div class='elite-card'>
            <h4>☢️ 3. NASA OSDR &amp; RadLab BLEO</h4>
            <p><b>Datasets:</b> <code>NASA RadLab BLEO (celestial_body=Moon)</code>, <code>OSDR OSD-137</code>, <code>OSD-895</code>, <code>OSD-767</code>.<br>
            <b>Gameplay Link:</b> Calibrates lunar surface background radiation at <code>0.42 mSv/Sol</code> and informs EVA exposure limits + spaceflight plant biology.</p>
            <h4>🌍 4. NASA DSCOVR EPIC API</h4>
            <p><b>Status:</b> """ + nasa_epic["source"] + f""" ({nasa_epic['date']})<br>
            {nasa_epic['caption']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_n4:
        st.markdown("""
        <div class='elite-card'>
            <h4>🤝 2026 Space Agency Partner Resources Integrated</h4>
            <ul>
                <li><b>CSA (Canadian Space Agency):</b> Deep Space Food Toolkit inspires our 4-crop hydroponic greenhouse (Tomatoes, Lettuce, Radishes, Potatoes) balancing grow-light electricity against fresh calories &amp; O₂.</li>
                <li><b>ISRO (Indian Space Research Organisation):</b> Chandrayaan-3 Lunar South Pole regolith &amp; thermal/water-ice insights inspire our Shackleton Crater ice-mining &amp; EVA Core-Sample Research Pad.</li>
                <li><b>ESA (European Space Agency):</b> Moonlight lunar communications &amp; inflatable regolith-shielded habitat principles inspire our Earth HQ radio delay and habitat dome trade-offs.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if nasa_epic["is_live"] and nasa_epic["image_url"]:
        st.subheader("🌍 Live View of Earth HQ (NASA DSCOVR EPIC)")
        st.image(nasa_epic["image_url"], caption=f"NASA EPIC ({nasa_epic['date']}): {nasa_epic['caption']}", width=360)

    st.markdown("""
    <div class='elite-card'>
        <h4>🤖 Mandatory NASA Space Apps Challenge Super Intelligence (SI) Disclosure</h4>
        <p>Our team conceived the game concept, lunar survival trade-offs, age-tiered pedagogy, and NASA/partner dataset mappings. We used Gemini as an SI coding collaborator to help build the Python/Streamlit wrapper, Three.js WebGL 3D lunar environment, procedural textures, and Web Audio synthesizer. No NASA logos or flags were modified by SI, and no likeness of minors is included.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# MODULE 4: CLASSROOM, PARENT & OLDER SIBLING GUIDE
# ==============================================================================
if side_page == "👩‍🏫 4. Classroom & Parent Guide":
    st.title("👩‍🏫 Classroom, Parent & Family Mission Guide")
    st.info("👈 Switch back to **'🎮 1. 3D Lunar Outpost Game'** in the left sidebar anytime to play!")

    st.markdown("""
    <div class='elite-card'>
        <h4>🎓 Built for Kids Ages 7–12 — Flexible for Classrooms &amp; Families</h4>
        <p>This guide turns a 5-minute playthrough into an unforgettable STEM lesson about real Artemis mission engineering.</p>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("""
        <div class='brief-card'>
            <h3>🌟 Ages 7–9 (Cadet)</h3>
            <p><b>Focus:</b> Cause &amp; Effect.</p>
            <p>Ask: <i>"What happened to the Oxygen bar when you forgot to close the green Airlock Door?"</i> and <i>"Why did the battery drop faster when the Shield stayed ON?"</i></p>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown("""
        <div class='brief-card'>
            <h3>🚀 Ages 10–12 (Commander)</h3>
            <p><b>Focus:</b> Engineering Trade-Offs.</p>
            <p>Challenge students to beat 7 Sols while scoring over <b>800 Science Points</b>—forcing them to decide when it's safe to spend Oxygen on EVA core drilling.</p>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown("""
        <div class='brief-card'>
            <h3>🏫 Classroom / Older Siblings (13+)</h3>
            <p><b>Focus:</b> Systems Optimization.</p>
            <p>Run the <b>X-Class Storm Gauntlet</b> in 13+ Mode, then compare each student's <b>Debrief Telemetry Graph</b> and total radiation dose (mSv) in Module 2!</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# STEP 1: AGE VERIFICATION, SCENARIO PICKER & AVENGERS 3D HERO LOCKER
# ==============================================================================
if st.session_state.av_stage == "STEP_1_HERO_SELECT":
    live_lbl = f"🟢 LIVE DONKI {nasa_flare['class']}" if nasa_flare["is_live"] else f"🟡 ARCHIVED DONKI {nasa_flare['class']}"
    st.markdown(f"""
    <div style="text-align:center;">
        <span class="nasa-pill">🛰️ {live_lbl} • NASA OSDR &amp; RADLAB • CSA • ISRO • ESA</span>
        <h1 style="margin:2px 0;">🛡️ AVENGERS LUNAR OUTPOST 3D</h1>
        <p style="font-size:1.02rem;color:#cbd5e1 !important;">Balance Power, Oxygen, Radiation Shielding, Food, Comms Delay &amp; EVA Science across 7 Lunar Sols!</p>
    </div>
    """, unsafe_allow_html=True)

    col_age, col_scen, col_vault = st.columns([1.25, 1.35, 1.35])
    age_is_valid = False

    with col_age:
        raw_age = st.text_input("🎂 Commander Age:", value=st.session_state.age_str, placeholder="Type age (e.g. 10)")
        st.session_state.age_str = raw_age
        if raw_age.strip() == "":
            st.warning("👉 Type **your age** to unlock launch!")
        else:
            try:
                parsed_age = int(raw_age.strip())
                if parsed_age <= 0 or parsed_age > 100:
                    st.error("⚠️ Enter an age from 1 to 100!")
                else:
                    age_is_valid = True
                    st.session_state.valid_age = parsed_age
                    if parsed_age <= 9:
                        st.session_state.age_tier = "7-9 Cadet"
                        st.success("🌟 **7–9 Cadet Mode:** Gentle pace + plain-language tips!")
                    elif parsed_age <= 12:
                        st.session_state.age_tier = "10-12 Commander"
                        st.success("🚀 **10–12 Commander Mode:** True Artemis trade-offs!")
                    else:
                        st.session_state.age_tier = "13+ Mission Planner"
                        st.success("🛰️ **13+ Planner Mode:** Hardcore lunar budgeting!")
            except ValueError:
                st.error("⚠️ Type a valid number!")

    with col_scen:
        scen_keys = list(SCENARIOS.keys())
        chosen_scen = st.selectbox(
            "🗺️ Mission Scenario (Replayability):",
            scen_keys,
            index=scen_keys.index(st.session_state.scenario_key),
            format_func=lambda k: SCENARIOS[k]["name"]
        )
        st.session_state.scenario_key = chosen_scen
        st.caption(SCENARIOS[chosen_scen]["desc"])

    with col_vault:
        st.markdown(f"""
        <div style='background:#0f172a;border:2px solid #fde047;border-radius:14px;padding:10px;text-align:center;margin-bottom:6px;'>
            <div style='font-size:14px;color:#fde047 !important;font-weight:900;'>🏆 WINS: {st.session_state.games_won} &nbsp;|&nbsp; 🪙 VAULT: {st.session_state.bank_coins}</div>
            <div style='font-size:11px;color:#93c5fd !important;margin-top:2px;'>Survive 7 Sols &amp; enter Victory Code in Sidebar to unlock Heroes!</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔓 Check Vault & Unlock Next Avenger"):
            locked_list = [k for k in HEROES if k not in st.session_state.unlocked_heroes]
            if not locked_list:
                st.session_state.unlock_ok = True
                st.session_state.unlock_msg = "🎉 All 7 Avengers are already unlocked!"
            else:
                next_k = locked_list[0]
                nh = HEROES[next_k]
                if st.session_state.games_won >= nh["unlock_wins"] and st.session_state.bank_coins >= nh["unlock_coins"]:
                    st.session_state.bank_coins -= nh["unlock_coins"]
                    st.session_state.unlocked_heroes.append(next_k)
                    st.session_state.unlock_ok = True
                    st.session_state.unlock_msg = f"🎉 Unlocked {nh['name']}!"
                else:
                    st.session_state.unlock_ok = False
                    st.session_state.unlock_msg = (
                        f"❌ Insufficient Coins and Trophies! {nh['name']} needs "
                        f"{nh['unlock_wins']} Win(s) & {nh['unlock_coins']} 🪙 "
                        f"(You have {st.session_state.games_won} Wins & {st.session_state.bank_coins} 🪙)."
                    )

    if st.session_state.unlock_msg:
        if st.session_state.unlock_ok:
            st.success(st.session_state.unlock_msg)
        else:
            st.error(st.session_state.unlock_msg)

    st.subheader("🦸‍♂️ Choose Your 3D Avenger Astronaut:")
    hero_keys = list(HEROES.keys())
    grid_cols = st.columns(4) + st.columns(3)

    for idx, hk in enumerate(hero_keys):
        h = HEROES[hk]
        is_unlocked = hk in st.session_state.unlocked_heroes
        border_c = h["accent"] if is_unlocked else "#475569"
        lock_overlay = "" if is_unlocked else f"""
            <rect x="0" y="0" width="120" height="145" rx="14" fill="rgba(2,6,23,0.85)"/>
            <text x="60" y="64" text-anchor="middle" fill="#fde047" font-size="26">🔒</text>
            <text x="60" y="90" text-anchor="middle" fill="#ffffff" font-size="9.5" font-weight="bold">NEED {h['unlock_wins']} WIN &amp; {h['unlock_coins']} 🪙</text>
        """
        with grid_cols[idx]:
            components.html(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e1b4b);border:3px solid {border_c};border-radius:16px;padding:8px;text-align:center;font-family:'Segoe UI',sans-serif;color:white;height:208px;box-sizing:border-box;">
                <svg width="90" height="104" viewBox="0 0 120 145">
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
                <div style="font-size:10.5px;color:#86efac;font-weight:bold;line-height:1.22;">{h['perk_desc']}</div>
            </div>
            """, height=216, scrolling=False)

            if is_unlocked:
                if st.button(f"🚀 Deploy {h['name']}", key=f"play_{hk}", disabled=not age_is_valid):
                    st.session_state.hero_key = hk
                    st.session_state.unlock_msg = ""
                    st.session_state.av_stage = "STEP_2_BRIEFING"
                    st.rerun()
            else:
                if st.button(f"🔒 Unlock {h['name']}", key=f"try_{hk}"):
                    if st.session_state.games_won >= h["unlock_wins"] and st.session_state.bank_coins >= h["unlock_coins"]:
                        st.session_state.bank_coins -= h["unlock_coins"]
                        st.session_state.unlocked_heroes.append(hk)
                        st.session_state.unlock_ok = True
                        st.session_state.unlock_msg = f"🎉 Unlocked {h['name']}!"
                    else:
                        st.session_state.unlock_ok = False
                        st.session_state.unlock_msg = (
                            f"❌ Insufficient Coins and Trophies! {h['name']} needs "
                            f"{h['unlock_wins']} Win(s) & {h['unlock_coins']} 🪙!"
                        )
                    st.rerun()
    st.stop()

# ==============================================================================
# STEP 2: 3D MISSION BRIEFING
# ==============================================================================
if st.session_state.av_stage == "STEP_2_BRIEFING":
    st.markdown(f"<h1 style='text-align:center;'>🌕 BRIEFING: {hero_cfg['name'].upper()}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;font-size:1.05rem;'><b>Scenario:</b> {SCENARIOS[st.session_state.scenario_key]['name']} &nbsp;|&nbsp; "
        f"<b>Perk:</b> <span style='color:#fde047;'>{hero_cfg['perk_desc']}</span></p>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class='brief-card'>
            <h3>🕹️ 1. 3D Moon Roaming</h3>
            <p>Use <b>WASD / Arrows</b>, <b>SPACE</b> (1/6G Jetpack Jump), or tap the <b>Auto-Run buttons</b>. Step onto glowing pads to work automatically!</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='brief-card'>
            <h3>🚨 2. NASA Solar Flares</h3>
            <p>Keep Shield <b>OFF</b> when calm so solar arrays charge. When the <b>NASA DONKI</b> siren sounds: Run Inside, <b>Seal Airlock</b>, and <b>Raise Shield</b>!</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='brief-card'>
            <h3>🔬 3. O₂ vs. Science</h3>
            <p>Visit the new <b>EVA Science Pad</b> to drill lunar core samples (+Science &amp; Coins), but watch your <b>Oxygen</b> &amp; <b>Radiation (mSv)</b>!</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class='brief-card'>
            <h3>⚖️ 4. Mission Dilemmas</h3>
            <p>On Sols 2, 4 &amp; 6, tough <b>NASA Engineering Dilemmas</b> pause the clock. There are no free lunches—every choice teaches real space physics!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("⬅️ Back to Hero Locker"):
            st.session_state.av_stage = "STEP_1_HERO_SELECT"
            st.rerun()
    with b2:
        if st.button(f"🚀 LAUNCH 3D MISSION AS {hero_cfg['name'].upper()}!"):
            st.session_state.av_stage = "STEP_3_PLAY"
            st.rerun()
    st.stop()

# ==============================================================================
# STEP 3: CHALLENGE-MAXED 3D THREE.JS LUNAR SURVIVAL ENGINE
# ==============================================================================
game_config = {
    "heroName": hero_cfg["name"],
    "perk": hero_cfg["perk_code"],
    "suitColor": hero_cfg["suit_color"],
    "accentColor": hero_cfg["accent"],
    "eyeColor": hero_cfg["eyes"],
    "ageTier": st.session_state.age_tier,
    "scenario": st.session_state.scenario_key,
    "flareId": nasa_flare["id"],
    "flareClass": nasa_flare["class"],
    "flareLive": nasa_flare["is_live"],
    "flareSource": nasa_flare["source"],
    "cmeId": nasa_cme["id"],
    "cmeSpeed": nasa_cme["speed"]
}

GAME_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; user-select: none; font-family: 'Segoe UI', system-ui, sans-serif; }
  html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #020617; color: #f8fafc; }

  #game-root { position: relative; width: 100%; height: 830px; overflow: hidden; border: 3px solid #eab308; border-radius: 16px; background: #020617; outline: none; }
  #canvas-container { position: absolute; inset: 0; width: 100%; height: 100%; }

  /* TOP HUD */
  .top-hud {
    position: absolute; top: 8px; left: 8px; right: 8px;
    display: grid; grid-template-columns: 1.05fr 0.95fr 0.95fr 0.95fr 0.95fr 1.15fr;
    gap: 7px; pointer-events: none; z-index: 10;
  }
  .hud-card {
    background: rgba(9, 13, 31, 0.85);
    backdrop-filter: blur(8px);
    border: 2px solid rgba(234, 179, 8, 0.78);
    border-radius: 12px;
    padding: 5px 8px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.65);
    pointer-events: auto;
  }
  .hud-row { display: flex; justify-content: space-between; align-items: center; }
  .hud-lbl { font-size: 10.5px; font-weight: 800; color: #93c5fd; text-transform: uppercase; display: flex; align-items: center; gap: 4px; }
  .hud-val { font-size: 16.5px; font-weight: 900; color: #ffffff; }
  .hud-sub { font-size: 9.8px; font-weight: 800; color: #cbd5e1; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-bg { width: 100%; height: 6.5px; background: rgba(2,6,23,0.92); border-radius: 99px; overflow: hidden; margin-top: 3px; }
  .bar-fill { height: 100%; width: 90%; transition: width 0.18s ease, background 0.18s ease; border-radius: 99px; }

  /* IN-CONTEXT SCIENCE HELP CHIPS (?) */
  .qchip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 15px; height: 15px; border-radius: 50%;
    background: rgba(56, 189, 248, 0.25); border: 1px solid #38bdf8;
    color: #7dd3fc; font-size: 10px; font-weight: 900; cursor: pointer;
  }
  .qchip:hover { background: #38bdf8; color: #020617; }

  /* STATUS & LIVE NASA ATTRIBUTION BAR */
  .ticker-bar {
    position: absolute; top: 78px; left: 8px; right: 8px;
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
    background: rgba(15, 23, 42, 0.86); backdrop-filter: blur(6px);
    border: 1.5px solid #38bdf8; border-radius: 10px; padding: 5px 12px;
    z-index: 10; font-size: 12px; font-weight: 800;
  }
  #status-msg { color: #f8fafc; }
  .nasa-badge-btn {
    background: rgba(14,165,233,0.22); border: 1px solid #38bdf8; color: #7dd3fc;
    border-radius: 999px; padding: 2px 10px; font-size: 10.5px; font-weight: 900; cursor: pointer; white-space: nowrap;
  }
  .nasa-badge-btn:hover { background: #38bdf8; color: #020617; }

  /* TACTICAL 2D RADAR MINIMAP */
  #minimap-wrap {
    position: absolute; top: 118px; left: 10px; z-index: 16;
    background: rgba(2, 6, 23, 0.84); border: 2px solid #38bdf8; border-radius: 14px;
    padding: 5px; box-shadow: 0 6px 20px rgba(0,0,0,0.7); text-align: center;
  }
  #minimap { display: block; border-radius: 8px; background: #0b1120; }

  /* GLOSSARY TOOLTIP CARD */
  #glossary-pop {
    position: absolute; top: 118px; left: 50%; transform: translateX(-50%);
    width: 390px; max-width: 90%;
    background: rgba(15, 23, 42, 0.97); border: 2.5px solid #38bdf8; border-radius: 16px;
    padding: 12px 16px; z-index: 40; display: none;
    box-shadow: 0 0 30px rgba(56,189,248,0.55);
  }

  /* COMIC ALERT POPUP */
  #comic-toast {
    position: absolute; top: 118px; right: 12px; width: 255px;
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,27,75,0.96));
    border: 3px solid #fde047; border-radius: 16px; padding: 9px 12px;
    z-index: 25; display: none; text-align: center;
    box-shadow: 0 0 28px rgba(253, 224, 71, 0.55);
  }

  /* PAD PROGRESS RING */
  #pad-progress-wrap {
    position: absolute; top: 122px; left: 50%; transform: translateX(-50%);
    background: rgba(2, 6, 23, 0.92); border: 2px solid #4ade80; border-radius: 999px;
    padding: 6px 16px; display: none; align-items: center; gap: 10px; z-index: 20;
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.5);
  }
  #pad-progress-bar-bg { width: 125px; height: 9px; background: #1e293b; border-radius: 99px; overflow: hidden; }
  #pad-progress-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #4ade80, #fde047); }

  /* SOLAR FLARE ALARM */
  #flare-alarm {
    position: absolute; top: 274px; left: 10px;
    background: linear-gradient(90deg, rgba(185,28,28,0.95), rgba(127,29,29,0.95));
    border: 2.5px solid #fde047; border-radius: 12px; padding: 7px 12px;
    z-index: 22; display: none; width: 255px;
    box-shadow: 0 0 25px rgba(239, 68, 68, 0.85);
    animation: pulseRed 0.75s infinite alternate;
  }
  @keyframes pulseRed { from { transform: scale(1); } to { transform: scale(1.03); } }

  /* BOTTOM DOCK */
  .bottom-dock {
    position: absolute; bottom: 8px; left: 8px; right: 8px;
    display: grid; grid-template-columns: 1.35fr 1.3fr 1.55fr;
    gap: 8px; z-index: 15;
  }
  .dock-panel {
    background: rgba(9, 13, 31, 0.89);
    backdrop-filter: blur(8px);
    border: 1.5px solid rgba(56, 189, 248, 0.6);
    border-radius: 13px;
    padding: 7px 9px;
  }
  .dock-title { font-size: 10.5px; font-weight: 900; color: #fde047; text-transform: uppercase; margin-bottom: 5px; display: flex; justify-content: space-between; }
  .btn-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
  .btn-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
  .btn-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
  .btn-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }

  .gbtn {
    background: linear-gradient(145deg, #1d4ed8, #312e81);
    color: #ffffff; border: 1.5px solid #7dd3fc; border-radius: 8px;
    padding: 5.5px 4px; font-size: 10.8px; font-weight: 800; cursor: pointer;
    transition: transform 0.1s, box-shadow 0.15s; text-align: center;
  }
  .gbtn:hover { border-color: #fde047; box-shadow: 0 0 12px rgba(253,224,71,0.55); transform: translateY(-1px); }
  .gbtn:active { transform: scale(0.96); }
  .gbtn-green { background: linear-gradient(145deg, #15803d, #047857); border-color: #86efac; }
  .gbtn-red { background: linear-gradient(145deg, #b91c1c, #991b1b); border-color: #fca5a5; }
  .gbtn-gold { background: linear-gradient(145deg, #ca8a04, #b45309); border-color: #fef08a; }
  .gbtn-cyan { background: linear-gradient(145deg, #0369a1, #1e3a8a); border-color: #38bdf8; }
  .gbtn-purple { background: linear-gradient(145deg, #7e22ce, #4c1d95); border-color: #d8b4fe; }

  /* MISSION DILEMMA MODAL (PAUSES GAME FOR REAL TRADE-OFF DECISION) */
  #dilemma-overlay {
    position: absolute; inset: 0; z-index: 55;
    background: rgba(2, 6, 23, 0.88); backdrop-filter: blur(7px);
    display: none; align-items: center; justify-content: center; padding: 16px;
  }
  .dilemma-box {
    background: linear-gradient(160deg, #0f172a, #1e1b4b);
    border: 3px solid #38bdf8; border-radius: 20px; padding: 20px 24px;
    width: 610px; max-width: 96%; box-shadow: 0 0 40px rgba(56,189,248,0.45);
  }
  .choice-btn {
    width: 100%; text-align: left; background: rgba(30, 41, 59, 0.95);
    border: 2px solid #eab308; border-radius: 12px; padding: 11px 14px;
    color: #fff; cursor: pointer; margin-top: 9px; transition: 0.15s;
  }
  .choice-btn:hover { background: rgba(30, 58, 138, 0.95); border-color: #38bdf8; transform: translateX(3px); }

  /* START & DEBRIEF OVERLAYS */
  #start-overlay, #debrief-overlay {
    position: absolute; inset: 0; z-index: 60;
    background: radial-gradient(circle at center, rgba(15,23,42,0.84), rgba(2,6,23,0.95));
    display: flex; align-items: center; justify-content: center; padding: 16px;
  }
  #debrief-overlay { display: none; }
  .modal-card {
    background: linear-gradient(160deg, #0f172a, #1e1b4b);
    border: 3px solid #eab308; border-radius: 22px; padding: 22px 28px;
    width: 650px; max-width: 96%; text-align: center;
    box-shadow: 0 0 45px rgba(56,189,248,0.4);
  }
  .launch-cta {
    margin-top: 14px; background: linear-gradient(90deg, #ef4444, #2563eb);
    border: 2.5px solid #fde047; color: #fff; font-size: 15px; font-weight: 900;
    padding: 12px 26px; border-radius: 14px; cursor: pointer;
    box-shadow: 0 0 20px rgba(253,224,71,0.55);
  }
  .launch-cta:hover { transform: scale(1.03); }
  #debrief-chart {
    width: 100%; height: 150px; background: #020617; border: 1.5px solid #334155;
    border-radius: 12px; margin: 9px 0;
  }
  .victory-code-box {
    background: #064e3b; border: 2px dashed #4ade80; border-radius: 10px;
    padding: 7px 14px; margin: 6px auto; display: inline-block;
    font-size: 15px; font-weight: 900; color: #fef08a; letter-spacing: 1px;
  }
</style>
</head>
<body>
<div id="game-root" tabindex="0">
  <div id="canvas-container"></div>

  <!-- TOP HUD WITH IN-CONTEXT SCIENCE GLOSSARY CHIPS -->
  <div class="top-hud">
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
      <div class="hud-sub" id="sub-pwr">☀️ Solar Charging</div>
    </div>
    <div class="hud-card">
      <div class="hud-row">
        <span class="hud-lbl">🫁 O₂ <span class="qchip" onclick="openGlossary('OXYGEN')">?</span></span>
        <span class="hud-val" id="ui-ox">92%</span>
      </div>
      <div class="bar-bg"><div id="bar-ox" class="bar-fill" style="width:92%;background:#38bdf8;"></div></div>
      <div class="hud-sub" id="sub-ox">🔒 Airlock Sealed</div>
    </div>
    <div class="hud-card">
      <div class="hud-row">
        <span class="hud-lbl">🍽️ Food <span class="qchip" onclick="openGlossary('FOOD')">?</span></span>
        <span class="hud-val" id="ui-food">86%</span>
      </div>
      <div class="bar-bg"><div id="bar-food" class="bar-fill" style="width:86%;background:#4ade80;"></div></div>
      <div class="hud-sub" id="sub-basket">🧺 Basket: 0/4</div>
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
        <span class="hud-lbl">🔬 Sci / 🪙</span>
        <span class="hud-val" style="font-size:14px;"><span id="ui-sci" style="color:#d8b4fe;">0</span> | <span id="ui-coins" style="color:#fde047;">50</span></span>
      </div>
      <div style="display:flex;gap:4px;margin-top:5px;">
        <button class="gbtn" id="btn-sound" style="flex:1;padding:3px;font-size:10px;" onclick="toggleSound()">🔊 SFX</button>
        <button class="gbtn gbtn-gold" style="flex:1;padding:3px;font-size:10px;" onclick="toggleCameraMode()">🎥 Cam</button>
      </div>
    </div>
  </div>

  <!-- STATUS & LIVE NASA ATTRIBUTION -->
  <div class="ticker-bar">
    <span id="status-msg">🛡️ Initializing 3D Shackleton Crater Outpost...</span>
    <button class="nasa-badge-btn" onclick="openGlossary('NASA')" id="nasa-feed-btn">🛰️ NASA DONKI + OSDR Feed</button>
  </div>

  <!-- LIVE TACTICAL 2D RADAR MINIMAP -->
  <div id="minimap-wrap">
    <div style="font-size:9.5px;font-weight:900;color:#7dd3fc;margin-bottom:3px;">📡 SHACKLETON RADAR</div>
    <canvas id="minimap" width="128" height="114"></canvas>
  </div>

  <!-- SOLAR FLARE ALARM -->
  <div id="flare-alarm">
    <div style="font-size:12.5px;font-weight:900;color:#fde047;" id="flare-alarm-title">🚨 NASA DONKI FLARE!</div>
    <div style="font-size:11px;color:#fff;margin-top:2px;" id="flare-alarm-desc">Run inside, Seal Airlock &amp; Raise Shield!</div>
  </div>

  <!-- IN-CONTEXT GLOSSARY POPUP -->
  <div id="glossary-pop">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span id="gl-title" style="font-weight:900;color:#fde047;font-size:14px;">Science Decoder</span>
      <button onclick="closeGlossary()" style="background:#ef4444;color:#fff;border:none;border-radius:6px;padding:2px 8px;font-weight:900;cursor:pointer;">✕</button>
    </div>
    <p id="gl-body" style="font-size:12.5px;color:#e2e8f0;margin:7px 0 0 0;line-height:1.45;"></p>
  </div>

  <!-- PAD PROGRESS -->
  <div id="pad-progress-wrap">
    <span id="pad-progress-label" style="font-size:12px;font-weight:900;color:#4ade80;">⚡ Working...</span>
    <div id="pad-progress-bar-bg"><div id="pad-progress-bar"></div></div>
  </div>

  <!-- COMIC POPUP -->
  <div id="comic-toast">
    <div id="comic-badge" style="font-size:34px;line-height:1.1;">🛡️⚡</div>
    <div id="comic-title" style="font-size:13px;font-weight:900;color:#fde047;margin-top:3px;">SHIELD ONLINE!</div>
    <div id="comic-body" style="font-size:11px;color:#e2e8f0;margin-top:2px;">Vibranium dome blocking radiation!</div>
  </div>

  <!-- BOTTOM CONTROL DOCK -->
  <div class="bottom-dock">
    <div class="dock-panel">
      <div class="dock-title"><span>🏃 Auto-Run to 3D Stations</span><span style="color:#7dd3fc;">WASD / Arrows + Space</span></div>
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
      <div class="dock-title"><span>⚙️ Outpost Controls</span><span id="zone-badge" style="color:#4ade80;">📍 INSIDE BASE</span></div>
      <div class="btn-grid-2" style="margin-bottom:5px;">
        <button class="gbtn gbtn-red" id="btn-shield" onclick="toggleShield()">🛡️ Shield: OFF</button>
        <button class="gbtn gbtn-green" id="btn-door" onclick="toggleDoor()">🔒 Airlock: SEALED</button>
      </div>
      <div class="btn-grid-2">
        <button class="gbtn gbtn-gold" onclick="deployRoverScan()">🚙 Rover Scan</button>
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
        Cost: 15 🪙 per drop (Dr. Strange: 10 🪙 &amp; 1.0s delay!)
      </div>
    </div>
  </div>

  <!-- MISSION DILEMMA MODAL (ZERO FREE LUNCHES!) -->
  <div id="dilemma-overlay">
    <div class="dilemma-box">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="background:#dc2626;color:#fff;font-size:11px;font-weight:900;padding:3px 10px;border-radius:999px;">⚖️ NASA ENGINEERING DILEMMA • CLOCK PAUSED</span>
        <span id="dil-sol" style="color:#7dd3fc;font-size:12px;font-weight:900;">SOL 2</span>
      </div>
      <h3 id="dil-title" style="margin:10px 0 6px 0;color:#fde047;font-size:19px;">Dilemma Title</h3>
      <p id="dil-desc" style="margin:0 0 8px 0;font-size:13px;color:#e2e8f0;line-height:1.45;"></p>
      <div id="dil-choices"></div>
    </div>
  </div>

  <!-- START OVERLAY -->
  <div id="start-overlay">
    <div class="modal-card">
      <div style="font-size:40px;line-height:1;">🌕🛡️🔬</div>
      <h2 style="margin:8px 0 4px 0;color:#fde047;font-size:23px;">AVENGERS LUNAR OUTPOST 3D</h2>
      <div style="font-size:12.5px;color:#7dd3fc;font-weight:800;" id="start-hero-line"></div>
      <p style="font-size:13px;color:#e2e8f0;margin:10px 0;line-height:1.45;">
        Explore Shackleton Crater in 3D! Run onto glowing floor pads to <b>Scrub Solar Dust</b>, <b>Mine Crater Ice</b>, <b>Harvest 4 CSA Space Crops</b>, <b>Stock the Pantry</b>, and <b>Drill EVA Lunar Core Samples</b> (trading O₂ for Science!).<br>
        Tap any <b>?</b> chip anytime to decode real NASA space terms in plain English.
      </p>
      <div id="best-run-line" style="font-size:11.5px;color:#fde047;font-weight:800;margin-bottom:4px;"></div>
      <button class="launch-cta" onclick="startMission()">🚀 LAUNCH 3D MISSION (🔊 AUDIO ON)</button>
    </div>
  </div>

  <!-- DEBRIEF OVERLAY -->
  <div id="debrief-overlay">
    <div class="modal-card">
      <div id="debrief-icon" style="font-size:38px;">🏆</div>
      <h2 id="debrief-title" style="margin:3px 0;color:#fde047;font-size:21px;">MISSION ACCOMPLISHED!</h2>
      <div id="debrief-rank" style="font-size:13px;font-weight:900;color:#4ade80;margin-bottom:3px;"></div>
      <p id="debrief-sub" style="margin:2px 0 6px 0;font-size:12.5px;color:#cbd5e1;"></p>
      <div id="victory-code-wrap" style="display:none;">
        <div class="victory-code-box" id="victory-code-txt">ARTEMIS-WIN-777</div>
        <div style="font-size:10.8px;color:#86efac;margin-bottom:4px;">Paste this code in the left Streamlit Sidebar to bank +1 🏆 Trophy &amp; +60 🪙!</div>
      </div>
      <canvas id="debrief-chart" width="600" height="150"></canvas>
      <div id="debrief-lesson" style="background:rgba(14,165,233,0.15);border:1.5px solid #38bdf8;border-radius:10px;padding:8px 12px;font-size:12px;color:#e0f2fe;text-align:left;line-height:1.4;"></div>
      <button class="launch-cta" style="margin-top:10px;padding:9px 22px;font-size:13.5px;" onclick="restartMission()">🔄 Replay &amp; Beat Your Strategy!</button>
    </div>
  </div>
</div>

<!-- THREE.JS WITH FALLBACK CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
        onerror="var s=document.createElement('script');s.src='https://unpkg.com/three@0.128.0/build/three.min.js';document.head.appendChild(s);"></script>

<script>
const CFG = __GAME_CONFIG_JSON__;

// ============================================================================
// 1. IN-CONTEXT PLAIN-LANGUAGE SCIENCE GLOSSARY
// ============================================================================
const GLOSSARY = {
  SOL: {
    title: "📅 What is a Lunar Sol?",
    body: "A 'Sol' is one survival day-cycle on another world! Here on the sunlit rim of Shackleton Crater (the Moon's South Pole), your mission spans 7 Sols—each bringing new solar weather, food needs, and engineering dilemmas."
  },
  POWER: {
    title: "⚡ Power Budgeting (No Free Lunch!)",
    body: "Sunlight powers your solar arrays, but sharp lunar dust clings to panels and lowers charging. Raising the Vibranium Radiation Shield protects your crew from solar flares, but drains your batteries fast—so timing matters!"
  },
  OXYGEN: {
    title: "🫁 Oxygen, Airlocks & Ice Electrolysis",
    body: "The Moon has no breathable air (it's a vacuum!). Leaving your Airlock Door open leaks precious O₂ into space. You can mine water-ice (H₂O) from shadowed Shackleton Crater and use electricity (electrolysis) to split it into breathable Oxygen!"
  },
  FOOD: {
    title: "🌱 CSA 4-Crop Hydroponic Greenhouse",
    body: "Inspired by the Canadian Space Agency (CSA) Deep Space Food Toolkit and NASA OSDR (OSD-767), your dome grows Tomatoes, Lettuce, Radishes, and Potatoes without soil. Plants also release fresh Oxygen as they grow!"
  },
  RAD: {
    title: "☢️ Radiation Dose (mSv) — NASA RadLab",
    body: "mSv stands for millisievert, which measures space radiation. On Earth we get ~0.008 mSv/day, but on the Moon (NASA RadLab BLEO) astronauts get ~0.42 mSv/Sol—and a NASA DONKI Solar Flare spikes it sharply unless you're inside with Shield ON!"
  },
  DELAY: {
    title: "📡 Why Is There a 2.6-Second Earth Radio Delay?",
    body: "Even at the speed of light (300,000 km/s), a radio message traveling 384,400 km from the Moon to Earth Mission Control and back takes 2.56 seconds! That's why lunar astronauts must think fast and handle emergencies locally."
  },
  NASA: {
    title: "🛰️ Live NASA & Partner Data Powering This Run",
    body: `• Solar Flare Feed: ${CFG.flareId} (Class ${CFG.flareClass}) via ${CFG.flareSource}\n• CME Feed: ${CFG.cmeId} (${CFG.cmeSpeed} km/s)\n• Radiation Baseline: 0.42 mSv/Sol (NASA RadLab BLEO & OSDR OSD-137)\n• Partner Science: CSA Deep Space Food Toolkit, ISRO Chandrayaan-3 South Pole regolith & water-ice, ESA lunar comms.`
  }
};

function openGlossary(key) {
  const g = GLOSSARY[key] || GLOSSARY.NASA;
  document.getElementById("gl-title").innerText = g.title;
  document.getElementById("gl-body").innerText = g.body;
  document.getElementById("glossary-pop").style.display = "block";
  playSfx(620, 0.1, "sine", 0.06);
}
function closeGlossary() {
  document.getElementById("glossary-pop").style.display = "none";
}

// ============================================================================
// 2. MISSION CONTROL DILEMMAS (REAL NASA TRADE-OFFS!)
// ============================================================================
const DILEMMAS = {
  2: {
    title: "🔬 Deep Crater Discovery: Oxygen vs. Research!",
    desc: "ISRO Chandrayaan-3 & NASA orbital maps spotted ancient lunar volcanic glass and frozen water-ice 200m deeper inside Shackleton Crater! Going down takes heavy EVA exertion.",
    choices: [
      {
        label: "A) Run Deep EVA Core Drill",
        tradeoff: "Cost: -16% 🫁 Oxygen & +0.25 mSv Radiation  |  Reward: +300 🔬 Science & +30 🪙",
        apply: () => { state.oxygen = Math.max(5, state.oxygen - 16); state.rad += 0.25; state.science += 300; state.coins += 30; setStatus("🔬 Deep EVA succeeded! +300 Science at the cost of -16% Oxygen!"); }
      },
      {
        label: "B) Send Autonomous Rover Camera Instead",
        tradeoff: "Cost: -12% ⚡ Battery Power  |  Reward: +110 🔬 Science & Zero O₂ Risk",
        apply: () => { state.power = Math.max(5, state.power - 12); state.science += 110; setStatus("🚙 Safe rover scan saved Oxygen! +110 Science (-12% Power)."); }
      }
    ]
  },
  4: {
    title: `🌊 NASA DONKI CME Alert (${CFG.cmeSpeed} km/s): Shield vs. Greenhouse!`,
    desc: `NASA DONKI logged Coronal Mass Ejection ${CFG.cmeId}! You don't have enough peak electricity to max out BOTH magnetic shielding and CSA Greenhouse grow-lights tonight.`,
    choices: [
      {
        label: "A) Reinforce Magnetic Dome Shielding",
        tradeoff: "Cost: -20% ⚡ Power & -10% 🍽️ Food Growth  |  Reward: Blocks CME Radiation & +100 🔬",
        apply: () => { state.power = Math.max(5, state.power - 20); state.food = Math.max(8, state.food - 10); state.science += 100; state.flarePhase = "CALM"; state.flareTimer = 14; setStatus("🛡️ CME deflected! Crew radiation stayed safe, but battery dropped 20%."); }
      },
      {
        label: "B) Prioritize CSA Greenhouse Grow-Lights",
        tradeoff: "Cost: +0.95 mSv Radiation & -14% ❤️ Crew HP  |  Reward: +22% 🍽️ Food & +15% 🫁 O₂",
        apply: () => { state.rad += 0.95; state.hp = Math.max(10, state.hp - 14); state.food = Math.min(100, state.food + 22); state.oxygen = Math.min(100, state.oxygen + 15); setStatus("🌱 Greenhouse thrived (+22% Food), but crew absorbed CME radiation!"); }
      }
    ]
  },
  6: {
    title: "📡 Micrometeoroid Hit Solar Inverter — Comms Delay Choice!",
    desc: "A tiny space rock cracked an inverter outside! Earth HQ is 384,400 km away (2.6s light delay + telemetry diagnostics). How will you respond?",
    choices: [
      {
        label: "A) Rush Outside for Immediate Manual Patch",
        tradeoff: "Cost: -14% 🫁 Oxygen & +0.20 mSv  |  Reward: Instant Fix, +15% ⚡ Power & +180 🔬",
        apply: () => { state.oxygen = Math.max(5, state.oxygen - 14); state.rad += 0.20; state.power = Math.min(100, state.power + 15); state.science += 180; setStatus("🛠️ Bold EVA repair restored +15% Power immediately (-14% O₂)!"); }
      },
      {
        label: "B) Wait for Earth HQ Remote Software Reroute",
        tradeoff: "Cost: -16% ⚡ Power drained while waiting  |  Reward: Zero O₂/Radiation Risk & +25 🪙 Grant",
        apply: () => { state.power = Math.max(5, state.power - 16); state.coins += 25; setStatus("📡 Earth HQ rerouted power safely! Zero crew risk, -16% Power lost during delay."); }
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
  d.choices.forEach((ch, idx) => {
    const btn = document.createElement("button");
    btn.className = "choice-btn";
    btn.innerHTML = `<div style="font-size:13.5px;font-weight:900;color:#fde047;">${ch.label}</div>
                     <div style="font-size:11.5px;color:#93c5fd;margin-top:3px;font-weight:700;">${ch.tradeoff}</div>`;
    btn.onclick = () => {
      ch.apply();
      state.paused = false;
      document.getElementById("dilemma-overlay").style.display = "none";
      playSfx(660, 0.18, "sine", 0.08, 880);
      updateHUD();
      document.getElementById("game-root").focus();
    };
    wrap.appendChild(btn);
  });
  document.getElementById("dilemma-overlay").style.display = "flex";
}

// ============================================================================
// 3. WEB AUDIO SYNTHESIZER
// ============================================================================
let audioCtx = null, soundOn = true, bgmTimer = null, bgmStep = 0;
const bgmScale = [220, 261.63, 329.63, 392.0, 440.0, 392.0, 329.63, 293.66];

function ensureAudio() {
  if (!audioCtx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (AC) audioCtx = new AC();
  }
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
}

function playSfx(freq, dur=0.14, type="sine", vol=0.085, slideTo=null) {
  if (!soundOn) return;
  try {
    ensureAudio();
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, audioCtx.currentTime + dur);
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(); osc.stop(audioCtx.currentTime + dur);
  } catch(e) {}
}

function toggleSound() {
  soundOn = !soundOn;
  document.getElementById("btn-sound").innerText = soundOn ? "🔊 SFX" : "🔇 Mute";
  if (soundOn) playSfx(587, 0.14, "triangle", 0.07);
}

// ============================================================================
// 4. DIFFICULTY & SCENARIO CALIBRATION
// ============================================================================
const baseDiff = CFG.ageTier.includes("7-9")
  ? { drain: 0.72, solSecs: 26, flareWarn: 9.0, flareDur: 8.0, flareDmg: 5.5, flareGap: 14 }
  : (CFG.ageTier.includes("13+")
    ? { drain: 1.25, solSecs: 22, flareWarn: 6.5, flareDur: 10.5, flareDmg: 10.5, flareGap: 10 }
    : { drain: 1.0, solSecs: 24, flareWarn: 7.5, flareDur: 9.0, flareDmg: 8.0, flareGap: 12 });

if (CFG.scenario === "STORM_GAUNTLET") {
  baseDiff.flareGap = 6.5; baseDiff.flareDmg *= 1.25;
} else if (CFG.scenario === "SCIENCE_EXPEDITION") {
  baseDiff.drain *= 1.08;
}
const DIFF = baseDiff;

let state = {};
let telemetryLog = [];

function resetState() {
  state = {
    started: false,
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
    coins: (CFG.perk === "WIDOW") ? 70 : 50,
    doorSealed: true,
    shieldOn: false,
    dusty: false,
    flarePhase: "CALM",
    flareTimer: DIFF.flareGap,
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
resetState();

document.getElementById("start-hero-line").innerText =
  `Commander: ${CFG.heroName} • ${CFG.ageTier} • NASA DONKI ${CFG.flareClass}`;
document.getElementById("nasa-feed-btn").innerText =
  CFG.flareLive ? `🟢 LIVE NASA DONKI ${CFG.flareClass} (Inspect)` : `🟡 ARCHIVED NASA DONKI ${CFG.flareClass} (Inspect)`;

try {
  const best = localStorage.getItem("artemis_best_sci");
  if (best) document.getElementById("best-run-line").innerText = `🏆 Personal Best Science Score: ${best} pts — Can you beat it?`;
} catch(e) {}

// ============================================================================
// 5. THREE.JS 3D OPEN-WORLD LUNAR BASE (PROCEDURAL TEXTURES + SPRITES + FX)
// ============================================================================
let scene, camera, renderer, clock;
let heroGroup, heroLimbs = {}, heroBasketGroup;
let sunMesh, sunGlow, dirLight, beaconLight, earthGroup, radioBeamMesh;
let shieldDomeMesh, shieldWireMesh, airlockDoorMesh, airlockGlowMat;
let solarDustMeshes = [], cropMeshes = [], pantryFoodGroup, roverGroup, drillCrystal;
let coinOrbs = [], flareParticles, fxParticles = [], shootingStar;
let padRings = {};
let heroPos = new THREE.Vector3(0, 0, 1.5);
let heroVelY = 0, heroRotY = 0;
const keys = {};

const STATIONS = {
  SOLAR:   { x: -13.5, z: 5.5,  r: 3.1, label: "☀️ Scrubbing Solar Dust...", color: 0xfacc15, tag: "☀️ SOLAR ARRAY" },
  ICE:     { x: -10.0, z: -8.5, r: 3.0, label: "🧊 Mining Crater Ice (+O₂, -⚡)...", color: 0x38bdf8, tag: "🧊 ICE CRATER" },
  SCIENCE: { x: 9.5,   z: 9.0,  r: 3.0, label: "🔬 Drilling Lunar Core (-O₂, +Sci)...", color: 0xd8b4fe, tag: "🔬 EVA SCIENCE" },
  FARM:    { x: 12.2,  z: -2.0, r: 3.3, label: "🌱 Harvesting CSA Crops...", color: 0x4ade80, tag: "🌱 CSA FARM" },
  PANTRY:  { x: 2.3,   z: -1.2, r: 2.2, label: "🍽️ Stocking Pantry Table...", color: 0xf472b6, tag: "🍽️ PANTRY" },
  SHIELD:  { x: -2.4,  z: -1.4, r: 2.2, label: "🛡️ Shield Console", color: 0x60a5fa, tag: "🛡️ SHIELD" }
};

function makeLunarTexture() {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 512;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#64748b";
  ctx.fillRect(0, 0, 512, 512);
  // Regolith grain
  for (let i = 0; i < 6000; i++) {
    const shade = 75 + Math.floor(Math.random() * 55);
    ctx.fillStyle = `rgb(${shade},${shade+6},${shade+16})`;
    ctx.fillRect(Math.random()*512, Math.random()*512, 2, 2);
  }
  // Micro-craters
  for (let i = 0; i < 45; i++) {
    const x = Math.random()*512, y = Math.random()*512, r = 6 + Math.random()*26;
    const grad = ctx.createRadialGradient(x, y, r*0.2, x, y, r);
    grad.addColorStop(0, "rgba(30,41,59,0.55)");
    grad.addColorStop(0.75, "rgba(100,116,139,0.2)");
    grad.addColorStop(1, "rgba(203,213,225,0.35)");
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill();
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
  ctx.fillStyle = "rgba(9,13,31,0.85)";
  ctx.strokeStyle = borderHex;
  ctx.lineWidth = 5;
  ctx.beginPath(); ctx.roundRect(6, 8, 244, 48, 14); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#ffffff";
  ctx.font = "900 22px Segoe UI, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(text, 128, 40);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true }));
  sprite.scale.set(4.8, 1.2, 1);
  return sprite;
}

function init3D() {
  const container = document.getElementById("canvas-container");
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020617);
  scene.fog = new THREE.FogExp2(0x04091a, 0.013);

  camera = new THREE.PerspectiveCamera(52, container.clientWidth / container.clientHeight, 0.1, 260);
  camera.position.set(0, 14, 21);

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  clock = new THREE.Clock();

  // LIGHTING
  scene.add(new THREE.HemisphereLight(0x93c5fd, 0x1e293b, 0.65));

  dirLight = new THREE.DirectionalLight(0xfff7ed, 1.5);
  dirLight.position.set(-28, 32, 16);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(1024, 1024);
  const d = 28;
  dirLight.shadow.camera.left = -d; dirLight.shadow.camera.right = d;
  dirLight.shadow.camera.top = d; dirLight.shadow.camera.bottom = -d;
  scene.add(dirLight);

  // Emergency Dome Beacon Light
  beaconLight = new THREE.PointLight(0x38bdf8, 1.2, 14);
  beaconLight.position.set(0, 4.5, 0);
  scene.add(beaconLight);

  // STARFIELD + SHOOTING STAR
  const starGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(1400 * 3);
  const starCol = new Float32Array(1400 * 3);
  for (let i = 0; i < 1400; i++) {
    const r = 75 + Math.random() * 75;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(Math.random() * 0.85 + 0.12);
    starPos[i*3]   = r * Math.sin(phi) * Math.cos(theta);
    starPos[i*3+1] = Math.abs(r * Math.cos(phi)) + 6;
    starPos[i*3+2] = r * Math.sin(phi) * Math.sin(theta);
    starCol[i*3]   = Math.random() > 0.7 ? 1.0 : 0.8;
    starCol[i*3+1] = 0.9;
    starCol[i*3+2] = 1.0;
  }
  starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute("color", new THREE.BufferAttribute(starCol, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ size: 0.55, vertexColors: true })));

  shootingStar = new THREE.Mesh(
    new THREE.BoxGeometry(0.18, 0.18, 3.8),
    new THREE.MeshBasicMaterial({ color: 0xbae6fd })
  );
  shootingStar.position.set(-40, 32, -50);
  scene.add(shootingStar);

  // BLAZING 3D SUN
  sunMesh = new THREE.Mesh(new THREE.SphereGeometry(5.2, 24, 24), new THREE.MeshBasicMaterial({ color: 0xfde047 }));
  sunMesh.position.set(-42, 34, -38);
  scene.add(sunMesh);
  sunGlow = new THREE.Mesh(new THREE.SphereGeometry(7.8, 24, 24), new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.28 }));
  sunGlow.position.copy(sunMesh.position);
  scene.add(sunGlow);

  // ROTATING 3D EARTH
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

  // CRATERED LUNAR TERRAIN WITH PROCEDURAL REGOLITH TEXTURE
  const groundGeo = new THREE.PlaneGeometry(115, 115, 52, 52);
  groundGeo.rotateX(-Math.PI / 2);
  const posAttr = groundGeo.attributes.position;
  for (let i = 0; i < posAttr.count; i++) {
    const x = posAttr.getX(i), z = posAttr.getZ(i);
    const dist = Math.hypot(x, z);
    let y = 0;
    if (dist > 20) y = Math.sin(x*0.18)*Math.cos(z*0.18)*1.5 + (dist - 20)*0.13;
    else if (Math.hypot(x + 10.0, z + 8.5) < 3.5) y = -0.35;
    posAttr.setY(i, y);
  }
  groundGeo.computeVertexNormals();
  const ground = new THREE.Mesh(
    groundGeo,
    new THREE.MeshStandardMaterial({ map: makeLunarTexture(), roughness: 0.95, metalness: 0.04 })
  );
  ground.receiveShadow = true;
  scene.add(ground);

  // LUNAR BOULDERS
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.95 });
  [[-20, 12], [-18, -14], [19, 11], [21, -12], [5, 16], [-6, -18], [15, -15], [-2, 17]].forEach(([rx, rz]) => {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.0 + Math.random()*1.3, 0), rockMat);
    rock.position.set(rx, 0.45, rz); rock.rotation.set(Math.random(), Math.random(), 0);
    rock.castShadow = true; rock.receiveShadow = true;
    scene.add(rock);
  });

  // GLOWING PATHWAYS
  function addPath(x1, z1, x2, z2, col) {
    const len = Math.hypot(x2 - x1, z2 - z1);
    const p = new THREE.Mesh(new THREE.PlaneGeometry(len, 1.05), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.24 }));
    p.rotation.x = -Math.PI / 2;
    p.rotation.z = -Math.atan2(z2 - z1, x2 - x1);
    p.position.set((x1 + x2)/2, 0.03, (z1 + z2)/2);
    scene.add(p);
  }
  addPath(0, 6.2, -13.5, 5.5, 0xfacc15);
  addPath(0, 6.2, -10.0, -8.5, 0x38bdf8);
  addPath(0, 6.2, 9.5, 9.0, 0xd8b4fe);
  addPath(5.5, -1.5, 12.2, -2.0, 0x4ade80);

  // CENTRAL ARTEMIS HABITAT DOME
  const habFloor = new THREE.Mesh(new THREE.CylinderGeometry(6.0, 6.2, 0.22, 32), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.45, metalness: 0.4 }));
  habFloor.position.set(0, 0.11, 0); habFloor.receiveShadow = true;
  scene.add(habFloor);

  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.0, 24, 16, 0, Math.PI*2, 0, Math.PI*0.5),
    new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.16, roughness: 0.1, side: THREE.DoubleSide })
  ));
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(6.05, 12, 8, 0, Math.PI*2, 0, Math.PI*0.5),
    new THREE.MeshBasicMaterial({ color: 0xe2e8f0, wireframe: true, transparent: true, opacity: 0.34 })
  ));

  const habLbl = makeFloatingLabel("🏠 ARTEMIS HABITAT", "#38bdf8");
  habLbl.position.set(0, 7.2, 0);
  scene.add(habLbl);

  // AIRLOCK + SLIDING DOOR
  const airlockFrame = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.8, 1.4), new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.5 }));
  airlockFrame.position.set(0, 1.4, 6.0); airlockFrame.castShadow = true;
  scene.add(airlockFrame);

  airlockGlowMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x16a34a, emissiveIntensity: 0.7 });
  airlockDoorMesh = new THREE.Mesh(new THREE.BoxGeometry(2.3, 2.3, 0.35), airlockGlowMat);
  airlockDoorMesh.position.set(0, 1.25, 6.0);
  scene.add(airlockDoorMesh);

  // EARTH HQ LASER BEAM
  const beamDir = new THREE.Vector3().subVectors(earthGroup.position, new THREE.Vector3(0, 6.8, 0));
  radioBeamMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(0.16, 0.45, beamDir.length(), 10),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.85 })
  );
  radioBeamMesh.position.copy(new THREE.Vector3(0, 6.8, 0)).add(beamDir.clone().multiplyScalar(0.5));
  radioBeamMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), beamDir.clone().normalize());
  radioBeamMesh.visible = false;
  scene.add(radioBeamMesh);

  // INSIDE: PANTRY TABLE & SHIELD CONSOLE
  const tableTop = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.25, 1.4), new THREE.MeshStandardMaterial({ color: 0xb45309 }));
  tableTop.position.set(2.3, 1.0, -1.2); tableTop.castShadow = true;
  scene.add(tableTop);
  pantryFoodGroup = new THREE.Group(); pantryFoodGroup.position.set(2.3, 1.25, -1.2);
  scene.add(pantryFoodGroup);
  refreshPantryVisuals();

  const consoleDesk = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 1.1), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, emissive: 0x1d4ed8, emissiveIntensity: 0.45 }));
  consoleDesk.position.set(-2.4, 0.6, -1.4);
  scene.add(consoleDesk);

  // VIBRANIUM SHIELD DOME
  shieldDomeMesh = new THREE.Mesh(
    new THREE.SphereGeometry(7.9, 28, 18, 0, Math.PI*2, 0, Math.PI*0.52),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.25, side: THREE.DoubleSide })
  );
  shieldWireMesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(7.95, 2),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, wireframe: true, transparent: true, opacity: 0.48 })
  );
  shieldDomeMesh.visible = false; shieldWireMesh.visible = false;
  scene.add(shieldDomeMesh, shieldWireMesh);

  // STATION 1: SOLAR ARRAY
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

  // STATION 2: SHACKLETON ICE CRATER
  const iceMat = new THREE.MeshStandardMaterial({ color: 0x7dd3fc, emissive: 0x0284c7, emissiveIntensity: 0.65, roughness: 0.15 });
  [[-10.0, -8.5, 1.7], [-8.8, -9.2, 1.15], [-11.2, -8.0, 1.25], [-9.9, -7.2, 0.95]].forEach(([ix, iz, h]) => {
    const c = new THREE.Mesh(new THREE.ConeGeometry(0.55, h, 6), iceMat);
    c.position.set(ix, h/2 - 0.2, iz); c.castShadow = true; scene.add(c);
  });
  const iLbl = makeFloatingLabel("🧊 CRATER ICE (+O₂)", "#38bdf8"); iLbl.position.set(-10.0, 3.6, -8.5); scene.add(iLbl);

  // STATION 3 (NEW!): EVA SCIENCE CORE-SAMPLE LAB
  const sciBase = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.9, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x3b0764, metalness: 0.5 }));
  sciBase.position.set(9.5, 0.18, 9.0); scene.add(sciBase);
  const drillTower = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.32, 2.6, 8), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.7 }));
  drillTower.position.set(9.5, 1.4, 9.0); drillTower.castShadow = true; scene.add(drillTower);
  drillCrystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.65, 0), new THREE.MeshStandardMaterial({ color: 0xd8b4fe, emissive: 0xa855f7, emissiveIntensity: 0.8 }));
  drillCrystal.position.set(9.5, 3.1, 9.0); scene.add(drillCrystal);
  const sciLbl = makeFloatingLabel("🔬 EVA SCIENCE (-O₂)", "#d8b4fe"); sciLbl.position.set(9.5, 4.6, 9.0); scene.add(sciLbl);

  // STATION 4: CSA 4-CROP HYDROPONIC GREENHOUSE
  const ghDome = new THREE.Mesh(new THREE.SphereGeometry(4.4, 20, 14, 0, Math.PI*2, 0, Math.PI*0.5), new THREE.MeshStandardMaterial({ color: 0x4ade80, transparent: true, opacity: 0.18, side: THREE.DoubleSide }));
  ghDome.position.set(12.2, 0, -2.0); scene.add(ghDome);
  const ghWire = new THREE.Mesh(new THREE.SphereGeometry(4.45, 10, 8, 0, Math.PI*2, 0, Math.PI*0.5), new THREE.MeshBasicMaterial({ color: 0x86efac, wireframe: true, transparent: true, opacity: 0.36 }));
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

  // GLOWING FLOOR PADS
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

  // AUTONOMOUS LUNAR ROVER
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

  // COLLECTIBLE 3D SUPERCOINS
  [[-7, 9.5], [4.5, 10.5], [-14.5, -2.5], [15.5, 5.5], [-3, -11.5], [6.5, -9.5]].forEach(([cx, cz]) => {
    const coin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.55, 0.55, 0.16, 16),
      new THREE.MeshStandardMaterial({ color: 0xfacc15, emissive: 0xca8a04, emissiveIntensity: 0.7, metalness: 0.7 })
    );
    coin.rotation.x = Math.PI / 2; coin.position.set(cx, 1.1, cz);
    coin.userData = { active: true, respawn: 0 };
    scene.add(coin); coinOrbs.push(coin);
  });

  // SOLAR FLARE PARTICLE RAIN
  const fpGeo = new THREE.BufferGeometry();
  const fpPos = new Float32Array(280 * 3);
  for (let i = 0; i < 280; i++) {
    fpPos[i*3] = (Math.random()-0.5)*46; fpPos[i*3+1] = Math.random()*24; fpPos[i*3+2] = (Math.random()-0.5)*46;
  }
  fpGeo.setAttribute("position", new THREE.BufferAttribute(fpPos, 3));
  flareParticles = new THREE.Points(fpGeo, new THREE.PointsMaterial({ color: 0xff4500, size: 0.48, transparent: true, opacity: 0.92 }));
  flareParticles.visible = false;
  scene.add(flareParticles);

  buildHero3D();

  window.addEventListener("resize", () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
}

function buildHero3D() {
  heroGroup = new THREE.Group();
  const suitMat = new THREE.MeshStandardMaterial({ color: CFG.suitColor, roughness: 0.35, metalness: 0.25 });
  const accMat  = new THREE.MeshStandardMaterial({ color: CFG.accentColor, roughness: 0.3, metalness: 0.35 });
  const whiteMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.25 });

  const torso = new THREE.Mesh(new THREE.BoxGeometry(0.95, 1.15, 0.6), suitMat);
  torso.position.y = 1.45; torso.castShadow = true; heroGroup.add(torso);

  const emblem = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.08, 16), new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
  emblem.rotation.x = Math.PI / 2; emblem.position.set(0, 1.55, 0.31); heroGroup.add(emblem);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.54, 18, 18), whiteMat);
  head.position.y = 2.42; head.castShadow = true; heroGroup.add(head);

  const visor = new THREE.Mesh(
    new THREE.SphereGeometry(0.45, 16, 12, -Math.PI*0.35, Math.PI*0.7, Math.PI*0.25, Math.PI*0.42),
    new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1, metalness: 0.8 })
  );
  visor.position.set(0, 2.42, 0.15); heroGroup.add(visor);

  const eyeMat = new THREE.MeshBasicMaterial({ color: CFG.eyeColor });
  [-0.16, 0.16].forEach(ex => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), eyeMat);
    eye.position.set(ex, 2.44, 0.52); heroGroup.add(eye);
  });

  if (CFG.perk === "CAP") {
    const shield = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.1, 20), accMat);
    shield.rotation.x = Math.PI / 2; shield.position.set(0, 1.5, -0.38); heroGroup.add(shield);
  } else if (CFG.perk === "LOKI") {
    const hornMat = new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.8, roughness: 0.2 });
    [-0.3, 0.3].forEach(hx => {
      const horn = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.65, 8), hornMat);
      horn.position.set(hx, 3.05, 0.1); horn.rotation.z = hx > 0 ? -0.35 : 0.35; heroGroup.add(horn);
    });
  } else if (CFG.perk === "THOR" || CFG.perk === "STRANGE") {
    const cape = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.35, 0.08), accMat);
    cape.position.set(0, 1.25, -0.36); cape.rotation.x = 0.18; heroGroup.add(cape);
  } else if (CFG.perk === "WANDA") {
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
}

function refreshBasketVisuals() {
  while (heroBasketGroup.children.length) heroBasketGroup.remove(heroBasketGroup.children[0]);
  if (state.basket.length === 0) return;
  heroBasketGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.45, 0.5), new THREE.MeshStandardMaterial({ color: 0x92400e })));
  const colMap = { "🍅": 0xef4444, "🥬": 0x22c55e, "🥕": 0xf97316, "🥔": 0xeab308 };
  state.basket.forEach((icon, i) => {
    const v = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), new THREE.MeshStandardMaterial({ color: colMap[icon] || 0x4ade80, emissive: colMap[icon] || 0x4ade80, emissiveIntensity: 0.35 }));
    v.position.set((i % 2 - 0.5) * 0.3, 0.3 + Math.floor(i / 2) * 0.28, 0);
    heroBasketGroup.add(v);
  });
}

function refreshPantryVisuals() {
  while (pantryFoodGroup.children.length) pantryFoodGroup.remove(pantryFoodGroup.children[0]);
  const cols = [0xef4444, 0x22c55e, 0xf97316, 0xeab308];
  for (let i = 0; i < Math.min(6, state.pantryCount); i++) {
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 10), new THREE.MeshStandardMaterial({ color: cols[i % 4] }));
    f.position.set(-0.75 + (i % 3) * 0.75, 0.1, i >= 3 ? 0.35 : -0.35);
    pantryFoodGroup.add(f);
  }
}

function spawnFxPuff(x, y, z, colorHex=0xcbd5e1, size=0.4) {
  const puff = new THREE.Mesh(
    new THREE.SphereGeometry(size, 8, 8),
    new THREE.MeshBasicMaterial({ color: colorHex, transparent: true, opacity: 0.75 })
  );
  puff.position.set(x, y, z);
  puff.userData = { life: 0.45 };
  scene.add(puff);
  fxParticles.push(puff);
}

// ============================================================================
// 6. ACTIONS, PAD TRIGGERS & RADIO COMMS
// ============================================================================
function showComic(badge, title, body, ms=2500) {
  const el = document.getElementById("comic-toast");
  document.getElementById("comic-badge").innerText = badge;
  document.getElementById("comic-title").innerText = title;
  document.getElementById("comic-body").innerText = body;
  el.style.display = "block";
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.style.display = "none"; }, ms);
}
function setStatus(msg) { document.getElementById("status-msg").innerText = msg; }
function isInsideHabitat() { return Math.hypot(heroPos.x, heroPos.z) < 5.9; }

function autoRunTo(stationKey) {
  if (!state.started || state.ended || state.paused) return;
  const st = STATIONS[stationKey];
  if (!st) return;
  state.autoTarget = new THREE.Vector3(st.x, 0, st.z);
  playSfx(480, 0.1, "triangle", 0.06);
  setStatus(`🏃 Auto-running to ${st.tag}...`);
  document.getElementById("game-root").focus();
}

function triggerJump() {
  if (!state.started || state.ended || state.paused) return;
  if (heroPos.y <= 0.02) {
    heroVelY = (CFG.perk === "IRON") ? 8.4 : 6.5;
    playSfx(260, 0.22, "sine", 0.08, 540);
    spawnFxPuff(heroPos.x, 0.3, heroPos.z, 0x38bdf8, 0.45);
  }
}

function toggleCameraMode() { state.camWide = !state.camWide; playSfx(520, 0.08, "sine", 0.05); }

function toggleDoor() {
  if (!state.started || state.ended || state.paused) return;
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
  if (!state.started || state.ended || state.paused) return;
  if (!state.shieldOn && state.power < 8) {
    setStatus("⚠️ Battery Power too low for Vibranium Shield! Scrub Solar Array or call Earth HQ!");
    playSfx(180, 0.2, "sawtooth", 0.08);
    return;
  }
  state.shieldOn = !state.shieldOn;
  if (state.shieldOn) {
    const cost = (CFG.perk === "CAP") ? 5 : 10;
    state.power = Math.max(0, state.power - cost);
    playSfx(320, 0.3, "sawtooth", 0.08, 760);
    showComic("🛡️⚡", "VIBRANIUM SHIELD ON!", "Blocking NASA DONKI radiation! Turn OFF after storm to save Power.");
    setStatus(`🛡️ Shield RAISED (-${cost}% startup Power)! Remember to turn OFF after the flare.`);
  } else {
    playSfx(540, 0.18, "sine", 0.07, 260);
    setStatus("🟢 Shield turned OFF! Solar panels are recharging battery power.");
  }
  updateHUD();
}

function deployRoverScan() {
  if (!state.started || state.ended || state.paused) return;
  if (state.roverCooldown > 0) { setStatus(`🚙 Rover recharging... ready in ${Math.ceil(state.roverCooldown)}s.`); return; }
  if (state.power < 6) { setStatus("⚠️ Need 6% Power for a Lunar Rover scan!"); return; }
  state.power = Math.max(0, state.power - 6);
  const gain = (CFG.perk === "LOKI") ? 40 : 20;
  state.coins += gain;
  state.science += 45;
  state.roverCooldown = 11;
  playSfx(740, 0.22, "triangle", 0.08, 980);
  showComic("🚙🪙", "ROVER SCAN COMPLETE!", `+${gain} 🪙 & +45 🔬 Science (-6% Power trade-off)!`, 2000);
  setStatus(`🚙 Rover mapped crater rim: +${gain} 🪙 & +45 Science (-6% Power)!`);
}

function callEarth(preset) {
  if (!state.started || state.ended || state.paused || state.radioBusy) return;
  const cost = (CFG.perk === "STRANGE") ? 10 : 15;
  const delayMs = (CFG.perk === "STRANGE") ? 1000 : 2600;
  if (state.coins < cost) {
    document.getElementById("radio-log").innerText = `⚠️ Need ${cost} 🪙! Grab spinning Moon Coins or run Rover Scan!`;
    playSfx(210, 0.15, "sawtooth", 0.06);
    return;
  }
  state.coins -= cost;
  state.radioBusy = true;
  state.radioBeamTimer = delayMs / 1000;
  playSfx(440, 0.15, "sine", 0.08, 880);
  document.getElementById("radio-log").innerText = `📡 Signal traveling 384,400 km to Earth HQ... (${(delayMs/1000).toFixed(1)}s light delay)`;

  setTimeout(() => {
    state.radioBusy = false;
    if (state.ended) return;
    playSfx(880, 0.25, "triangle", 0.09, 1180);
    if (preset === 1) { state.power = Math.min(100, state.power + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Arc Battery Pod landed (+30% ⚡)!"; }
    else if (preset === 2) { state.oxygen = Math.min(100, state.oxygen + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Emergency O₂ Tank delivered (+30% 🫁)!"; }
    else if (preset === 3) { state.food = Math.min(100, state.food + 30); state.pantryCount = Math.min(6, state.pantryCount + 2); refreshPantryVisuals(); document.getElementById("radio-log").innerText = "🌍 Earth HQ: CSA Hydroponic Ration Drop (+30% 🍽️)!"; }
    else if (preset === 4) { state.hp = Math.min(100, state.hp + 30); document.getElementById("radio-log").innerText = "🌍 Earth HQ: Nano-Medkit restored +30% ❤️ HP!"; }
    else { state.flarePhase = "CALM"; state.flareTimer = DIFF.flareGap; document.getElementById("flare-alarm").style.display = "none"; document.getElementById("radio-log").innerText = "🌍 NASA DONKI Forecast: Solar storm cleared! Safe to lower Shield."; }
    updateHUD();
  }, delayMs);
}

function advanceSolEarly() {
  if (!state.started || state.ended || state.paused) return;
  state.solClock = DIFF.solSecs - 0.08;
  playSfx(523, 0.2, "triangle", 0.08);
}

function completePadAction(key) {
  const coinMult = (CFG.perk === "LOKI") ? 2 : 1;
  if (key === "SOLAR") {
    state.dusty = false;
    state.power = Math.min(100, state.power + 24);
    state.coins += 12 * coinMult;
    playSfx(784, 0.2, "triangle", 0.09, 1046);
    showComic("🧹☀️", "SOLAR ARRAY CLEAN!", `+24% Power & +${12*coinMult} 🪙! Electrostatic lunar dust cleared.`, 2000);
    setStatus("🧹 Swept abrasive lunar dust off Solar Array! Charging restored.");
  } else if (key === "ICE") {
    if (state.power < 10) { setStatus("⚠️ Need at least 10% ⚡ Power to run Shackleton Ice Electrolysis!"); return; }
    state.power = Math.max(0, state.power - 10);
    state.oxygen = Math.min(100, state.oxygen + 26);
    state.coins += 8 * coinMult;
    playSfx(620, 0.22, "sine", 0.08, 920);
    showComic("🧊🫁", "ICE ELECTROLYSIS!", "+26% Oxygen produced (-10% Power trade-off)!", 2000);
    setStatus("🫁 Split Shackleton Crater water-ice (H₂O) into breathable Oxygen (+26% O₂, -10% ⚡)!");
  } else if (key === "SCIENCE") {
    if (state.oxygen < 18 || state.power < 10) {
      setStatus("⚠️ Too risky! Need ≥18% 🫁 Oxygen & ≥10% ⚡ Power for EVA Core-Sample Drilling!");
      playSfx(200, 0.2, "sawtooth", 0.08);
      return;
    }
    const sciGain = (CFG.perk === "LOKI") ? 300 : 200;
    state.oxygen = Math.max(0, state.oxygen - 14);
    state.power = Math.max(0, state.power - 8);
    state.rad += 0.18;
    state.science += sciGain;
    state.coins += 18 * coinMult;
    playSfx(520, 0.25, "sawtooth", 0.07, 1040);
    spawnFxPuff(9.5, 1.5, 9.0, 0xd8b4fe, 0.65);
    showComic("🔬🌕", "CORE SAMPLE DRILLED!", `+${sciGain} Science & +${18*coinMult} 🪙! Trade-off: -14% O₂, -8% ⚡ & +0.18 mSv`, 2400);
    setStatus(`🔬 Extracted Shackleton regolith core (+${sciGain} Science) at the cost of -14% O₂ & -8% Power!`);
  } else if (key === "FARM") {
    const icons = ["🍅", "🥬", "🥕", "🥔"];
    let picked = 0;
    for (let i = 0; i < 4; i++) {
      if (state.crops[i] >= 95 && state.basket.length < 4) {
        state.basket.push(icons[i]); state.crops[i] = 5;
        state.power = Math.max(0, state.power - 2);
        state.oxygen = Math.min(100, state.oxygen + (CFG.perk === "WANDA" ? 6 : 2));
        picked++;
      }
    }
    if (picked > 0) {
      refreshBasketVisuals();
      playSfx(698, 0.18, "sine", 0.09, 987);
      showComic("🧺🍅🥬", "CSA HARVEST!", `Picked ${picked} fresh crops! Run to the Pantry Table inside!`, 2100);
      setStatus(`🧺 Harvested ${picked} CSA crops into your 3D Basket! Carry them to the Pantry Table.`);
    } else if (state.basket.length >= 4) {
      setStatus("🧺 Basket full (4/4)! Run to the Pantry Table inside to stock your food!");
    } else {
      setStatus("🌱 Space veggies still growing under hydroponic LEDs — check back soon!");
    }
  } else if (key === "PANTRY") {
    if (state.basket.length === 0) { setStatus("🧺 Basket empty! Visit the CSA Greenhouse (right) to harvest ripe crops."); return; }
    const n = state.basket.length;
    state.basket = [];
    state.pantryCount = Math.min(6, state.pantryCount + n);
    state.food = Math.min(100, state.food + n * 13);
    state.coins += n * 8 * coinMult;
    state.science += n * 25;
    refreshBasketVisuals(); refreshPantryVisuals();
    playSfx(880, 0.25, "triangle", 0.09, 1320);
    showComic("🍽️✨", "PANTRY STOCKED!", `+${n*13}% Food, +${n*25} Science & +${n*8*coinMult} 🪙!`, 2100);
    setStatus(`🍽️ Stocked Pantry Table with ${n} space veggies! Crew nutrition & botany logs updated.`);
  } else if (key === "SHIELD") {
    toggleShield();
  }
}

// ============================================================================
// 7. 2D TACTICAL RADAR MINIMAP RENDERER
// ============================================================================
function drawMinimap() {
  const c = document.getElementById("minimap");
  const ctx = c.getContext("2d");
  ctx.clearRect(0, 0, c.width, c.height);
  const mx = x => (x + 22) / 44 * c.width;
  const mz = z => (z + 18) / 36 * c.height;

  // Habitat Dome circle
  ctx.strokeStyle = "rgba(56,189,248,0.65)"; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(mx(0), mz(0), 17, 0, Math.PI*2); ctx.stroke();

  // Stations
  const stCols = { SOLAR: "#facc15", ICE: "#38bdf8", SCIENCE: "#d8b4fe", FARM: "#4ade80", PANTRY: "#f472b6", SHIELD: "#60a5fa" };
  Object.entries(STATIONS).forEach(([k, st]) => {
    ctx.fillStyle = stCols[k];
    ctx.beginPath(); ctx.arc(mx(st.x), mz(st.z), 4.2, 0, Math.PI*2); ctx.fill();
  });

  // Active Coins
  ctx.fillStyle = "#fef08a";
  coinOrbs.forEach(co => {
    if (co.userData.active) ctx.fillRect(mx(co.position.x)-1.5, mz(co.position.z)-1.5, 3, 3);
  });

  // Hero pulsing dot
  ctx.fillStyle = "#ffffff";
  ctx.beginPath(); ctx.arc(mx(heroPos.x), mz(heroPos.z), 4.8, 0, Math.PI*2); ctx.fill();
  ctx.strokeStyle = "#ef4444"; ctx.lineWidth = 2; ctx.stroke();
}

// ============================================================================
// 8. MAIN 60 FPS LOOP
// ============================================================================
let wasInside = true, footstepTimer = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(0.05, clock.getDelta());
  const t = clock.elapsedTime;

  earthGroup.rotation.y += dt * 0.08;
  drillCrystal.rotation.y += dt * 1.8;
  drillCrystal.position.y = 3.1 + Math.sin(t * 2.5) * 0.2;

  roverGroup.position.x = Math.sin(t * 0.35) * 8.5;
  roverGroup.rotation.y = Math.cos(t * 0.35) > 0 ? Math.PI / 2 : -Math.PI / 2;

  // Shooting Star
  shootingStar.position.x += dt * 28;
  shootingStar.position.y -= dt * 6;
  if (shootingStar.position.x > 65) {
    shootingStar.position.set(-55 - Math.random()*30, 26 + Math.random()*14, -45 - Math.random()*20);
  }

  // Pulse pads
  Object.values(padRings).forEach((ring, idx) => {
    const s = 1 + Math.sin(t * 3.5 + idx) * 0.06;
    ring.scale.set(s, s, 1);
  });

  // Shield & Airlock visuals
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

  // Solar Flare lighting & red dome alarm beacon
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

  // FX Particles decay
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

    const runSpeed = (CFG.perk === "WIDOW") ? 10.6 : 8.5;
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

    // Low-G lunar jump + jetpack trail
    heroPos.y += heroVelY * dt;
    if (heroPos.y > 0) {
      heroVelY -= 11.4 * dt;
      if (Math.random() < 0.45) spawnFxPuff(heroPos.x, heroPos.y + 0.3, heroPos.z, 0x38bdf8, 0.16);
    } else { heroPos.y = 0; heroVelY = 0; }
    heroGroup.position.copy(heroPos);
    heroGroup.rotation.y = heroRotY;

    // Auto-open Airlock when stepping outside
    const nowInside = isInsideHabitat();
    if (wasInside && !nowInside && state.doorSealed) {
      state.doorSealed = false;
      playSfx(310, 0.14, "square", 0.06);
      setStatus("🌑 Stepped outside onto Shackleton Crater! Seal Airlock when back inside!");
    }
    wasInside = nowInside;

    // Coin pickups
    coinOrbs.forEach(c => {
      if (c.userData.active) {
        c.rotation.z += dt * 3.0;
        c.position.y = 1.0 + Math.sin(t * 3 + c.position.x) * 0.22;
        if (Math.hypot(heroPos.x - c.position.x, heroPos.z - c.position.z) < 1.35) {
          c.userData.active = false; c.visible = false; c.userData.respawn = 18;
          const gain = (CFG.perk === "LOKI") ? 20 : 10;
          state.coins += gain;
          playSfx(987, 0.16, "sine", 0.09, 1318);
          setStatus(`🪙 Collected Lunar SuperCoin Orb (+${gain} 🪙)!`);
        }
      } else {
        c.userData.respawn -= dt;
        if (c.userData.respawn <= 0) { c.userData.active = true; c.visible = true; }
      }
    });

    // Monkey-Mart Auto-Pads
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

    // Crops grow
    const growSpeed = (CFG.perk === "WANDA") ? 7.5 : 4.2;
    for (let i = 0; i < 4; i++) {
      state.crops[i] = Math.min(100, state.crops[i] + growSpeed * dt);
      const s = 0.25 + (state.crops[i] / 100) * 0.95;
      cropMeshes[i].scale.set(s, s, s);
    }

    // Continuous Physics
    if (state.roverCooldown > 0) state.roverCooldown -= dt;

    if (state.shieldOn) {
      const sDrain = (CFG.perk === "CAP" ? 1.45 : 2.95) * DIFF.drain;
      state.power = Math.max(0, state.power - sDrain * dt);
      if (state.power <= 0.1) { state.shieldOn = false; setStatus("⚡ Battery hit 0%! Shield collapsed!"); }
    } else if (state.dusty) {
      state.power = Math.max(0, state.power - 0.8 * DIFF.drain * dt);
    } else {
      state.power = Math.min(100, state.power + ((CFG.perk === "IRON") ? 2.6 : 1.35) * dt);
    }

    let oxLoss = (state.doorSealed ? 0.62 : 2.3) * DIFF.drain;
    if (CFG.perk === "WIDOW") oxLoss *= 0.6;
    state.oxygen = Math.max(0, state.oxygen - oxLoss * dt);
    state.food = Math.max(0, state.food - 0.52 * DIFF.drain * dt);

    // NASA DONKI Solar Flare State Machine
    state.flareTimer -= dt;
    if (state.flarePhase === "CALM" && state.flareTimer <= 0) {
      state.flarePhase = "WARN"; state.flareTimer = DIFF.flareWarn;
      playSfx(240, 0.45, "sawtooth", 0.09, 460);
      document.getElementById("flare-alarm").style.display = "block";
      document.getElementById("flare-alarm-title").innerText = `🚨 NASA DONKI ${CFG.flareClass} FLARE!`;
      showComic("🚨☀️🔥", "SOLAR FLARE INCOMING!", `NASA DONKI ${CFG.flareClass} storm hits in ${Math.ceil(DIFF.flareWarn)}s!`, 3000);
    } else if (state.flarePhase === "WARN") {
      document.getElementById("flare-alarm-desc").innerText = `Impact in ${Math.max(0, state.flareTimer).toFixed(1)}s! Inside + Sealed + Shield ON!`;
      if (state.flareTimer <= 0) { state.flarePhase = "ACTIVE"; state.flareTimer = DIFF.flareDur; playSfx(180, 0.5, "sawtooth", 0.11, 120); }
    } else if (state.flarePhase === "ACTIVE") {
      document.getElementById("flare-alarm-title").innerText = `☢️ STORM HITTING (${Math.ceil(state.flareTimer)}s)`;
      const safe = nowInside && state.doorSealed && state.shieldOn;
      if (!safe) {
        state.hp = Math.max(0, state.hp - DIFF.flareDmg * (CFG.perk === "THOR" ? 0.4 : 1.0) * dt);
        state.rad += 0.25 * dt;
        document.getElementById("flare-alarm-desc").innerText = "⚠️ RADIATION HIT! Inside + Seal Door + Shield ON!";
      } else {
        state.rad += 0.015 * dt;
        document.getElementById("flare-alarm-desc").innerText = "🛡️ 100% PROTECTED BY SHIELD!";
      }
      if (state.flareTimer <= 0) {
        state.flarePhase = "CALM"; state.flareTimer = DIFF.flareGap + Math.random()*5;
        document.getElementById("flare-alarm").style.display = "none";
        if (Math.random() < 0.65) { state.dusty = true; showComic("🌪️☀️", "PANELS DUSTY!", "Storm cleared, but moon dust coated your solar panels!", 2400); }
        else showComic("☀️✅", "FLARE PASSED!", "Lower Shield now to recharge battery!", 2300);
        setStatus("☀️ Solar Flare cleared! Turn Shield OFF to recharge batteries.");
      }
    } else {
      state.rad += 0.015 * dt;
    }

    // 7-Sol Progression + Narrative Dilemmas on Sols 2, 4, 6
    state.solClock += dt;
    if (state.solClock >= DIFF.solSecs) {
      state.solClock = 0; state.sol += 1;
      telemetryLog.push({ sol: state.sol, pwr: Math.round(state.power), ox: Math.round(state.oxygen), hp: Math.round(state.hp) });

      if (state.sol > 7) {
        endMission(true, "WIN");
      } else {
        const bonus = (CFG.perk === "LOKI") ? 30 : 15;
        state.coins += bonus;
        state.science += 50;
        if (state.pantryCount > 0) { state.pantryCount--; refreshPantryVisuals(); }
        playSfx(523, 0.2, "triangle", 0.09, 784);
        if (DILEMMAS[state.sol] && !state.dilemmasShown[state.sol]) {
          state.dilemmasShown[state.sol] = true;
          triggerDilemma(state.sol);
        } else {
          showComic("🌙🏆", `LUNAR SOL ${state.sol} OF 7`, `+${bonus} 🪙 & +50 🔬 Science awarded!`, 2100);
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

  // Third-person camera follow
  const camOffset = state.camWide ? new THREE.Vector3(0, 21, 27) : new THREE.Vector3(0, 12.8, 16.8);
  camera.position.lerp(new THREE.Vector3(heroPos.x*0.62 + camOffset.x, camOffset.y, heroPos.z*0.52 + camOffset.z), Math.min(1, dt * 4.5));
  camera.lookAt(heroPos.x * 0.48, 1.4, heroPos.z * 0.42);

  renderer.render(scene, camera);
}

// ============================================================================
// 9. HUD, DEBRIEF & TELEMETRY CHART
// ============================================================================
function updateHUD() {
  document.getElementById("ui-sol").innerText = Math.min(7, state.sol) + " / 7";
  document.getElementById("bar-sol").style.width = Math.min(100, (state.solClock / DIFF.solSecs) * 100) + "%";
  document.getElementById("ui-weather").innerText =
    state.flarePhase === "ACTIVE" ? `☢️ ${CFG.flareClass} STORM` :
    (state.flarePhase === "WARN" ? "🚨 FLARE WARNING" : (state.dusty ? "🌪️ Panels Dusty" : "☀️ Calm Sky"));

  document.getElementById("ui-pwr").innerText = Math.round(state.power) + "%";
  document.getElementById("bar-pwr").style.width = state.power + "%";
  document.getElementById("sub-pwr").innerText = state.shieldOn ? "🛡️ Shield Draining!" : (state.dusty ? "🌪️ Dusty (-Power)" : "☀️ Solar Charging");

  document.getElementById("ui-ox").innerText = Math.round(state.oxygen) + "%";
  document.getElementById("bar-ox").style.width = state.oxygen + "%";
  document.getElementById("sub-ox").innerText = state.doorSealed ? "🔒 Airlock Sealed" : "🔓 Door Open (-O₂!)";

  document.getElementById("ui-food").innerText = Math.round(state.food) + "%";
  document.getElementById("bar-food").style.width = state.food + "%";
  document.getElementById("sub-basket").innerText = `🧺 Basket: ${state.basket.length}/4 ${state.basket.join("")}`;

  document.getElementById("ui-hp").innerText = Math.round(state.hp) + "%";
  document.getElementById("bar-hp").style.width = state.hp + "%";
  document.getElementById("sub-rad").innerText = `☢️ ${state.rad.toFixed(2)} mSv`;

  document.getElementById("ui-sci").innerText = state.science;
  document.getElementById("ui-coins").innerText = Math.floor(state.coins);

  document.getElementById("btn-shield").innerText = state.shieldOn ? "🛡️ Shield: ON" : "🛡️ Shield: OFF";
  document.getElementById("btn-door").innerText = state.doorSealed ? "🔒 Airlock: SEALED" : "🔓 Airlock: OPEN";
  document.getElementById("zone-badge").innerText = isInsideHabitat() ? "📍 INSIDE BASE" : "🌑 OUTSIDE MOON";
}

function endMission(won, cause) {
  state.ended = true;
  clearInterval(bgmTimer);
  document.getElementById("flare-alarm").style.display = "none";
  document.getElementById("dilemma-overlay").style.display = "none";
  document.getElementById("debrief-overlay").style.display = "flex";

  const codeWrap = document.getElementById("victory-code-wrap");
  if (won) {
    playSfx(523, 0.25, "triangle", 0.1, 1046);
    const rank = state.science >= 1100 ? "💎 CHIEF NASA MISSION PLANNER" : (state.science >= 750 ? "🥇 SHACKLETON COMMANDER" : "🥈 ARTEMIS SPECIALIST");
    const vCode = "ARTEMIS-WIN-" + Math.floor(100 + Math.random() * 899);
    try {
      const prev = Number(localStorage.getItem("artemis_best_sci") || 0);
      if (state.science > prev) localStorage.setItem("artemis_best_sci", String(state.science));
    } catch(e) {}
    document.getElementById("debrief-icon").innerText = "🏆🦸‍♂️🌕";
    document.getElementById("debrief-title").innerText = "7-SOL MISSION ACCOMPLISHED!";
    document.getElementById("debrief-rank").innerText = `RANK EARNED: ${rank} (${state.science} Science Pts)`;
    document.getElementById("debrief-sub").innerText = `Commander ${CFG.heroName} survived 7 Sols | Dose: ${state.rad.toFixed(2)} mSv | Coins: ${Math.floor(state.coins)} 🪙`;
    document.getElementById("victory-code-txt").innerText = vCode;
    codeWrap.style.display = "block";
    document.getElementById("debrief-lesson").innerHTML =
      `<b>🛰️ Real NASA Engineering Takeaway:</b> You balanced Power, Oxygen, CSA Food, EVA Science, and <b>NASA DONKI ${CFG.flareClass}</b> space weather across 7 Sols! Real Artemis planners face these exact mass, power, and radiation trade-offs every day.`;
  } else {
    playSfx(220, 0.45, "sawtooth", 0.09, 110);
    codeWrap.style.display = "none";
    document.getElementById("debrief-icon").innerText = "🛠️📡";
    document.getElementById("debrief-title").innerText = `LEARNING DEBRIEF — SOL ${state.sol} OF 7`;
    document.getElementById("debrief-rank").innerText = `Science Logged Before Pause: ${state.science} pts`;
    const lessons = {
      POWER: "⚡ <b>Power Budget Depleted:</b> Leaving the Radiation Shield ON during calm skies or letting lunar dust cover solar arrays drains batteries. Next run, toggle the Shield OFF as soon as the NASA DONKI flare passes!",
      OXYGEN: "🫁 <b>Oxygen Reserve Depleted:</b> Leaving the Airlock open or taking too many EVA core drills without mining Shackleton Crater water-ice (H₂O → O₂) empties cabin air fast!",
      FOOD: "🍽️ <b>Pantry Empty:</b> Keep harvesting Tomatoes, Lettuce, Radishes & Potatoes in the CSA Greenhouse Dome and stocking your Pantry Table!",
      RADIATION: "☢️ <b>Solar Flare Exposure:</b> Unshielded astronauts absorb dangerous radiation during NASA DONKI storms. When the siren sounds, rush inside, seal the airlock, and raise the shield!"
    };
    document.getElementById("debrief-sub").innerText = `Constraint reached: ${cause}. Real engineers learn from every simulation!`;
    document.getElementById("debrief-lesson").innerHTML = lessons[cause] || lessons.POWER;
  }
  drawDebriefChart();
}

function drawDebriefChart() {
  const canvas = document.getElementById("debrief-chart");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#1e293b"; ctx.lineWidth = 1;
  for (let y = 24; y <= 132; y += 27) { ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(580, y); ctx.stroke(); }
  ctx.fillStyle = "#94a3b8"; ctx.font = "11px sans-serif";
  ctx.fillText("100%", 6, 27); ctx.fillText("50%", 12, 81); ctx.fillText("0%", 18, 135);

  const pts = telemetryLog.length > 1 ? telemetryLog : [...telemetryLog, { sol: state.sol+0.5, pwr: state.power, ox: state.oxygen, hp: state.hp }];
  function plotSeries(key, color) {
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.beginPath();
    pts.forEach((p, idx) => {
      const x = 45 + (idx / Math.max(1, pts.length - 1)) * 525;
      const y = 132 - (Math.max(0, Math.min(100, p[key])) / 100) * 108;
      if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }
  plotSeries("pwr", "#facc15"); plotSeries("ox", "#38bdf8"); plotSeries("hp", "#f43f5e");
  ctx.fillStyle = "#facc15"; ctx.fillText("■ Power", 410, 15);
  ctx.fillStyle = "#38bdf8"; ctx.fillText("■ Oxygen", 470, 15);
  ctx.fillStyle = "#f43f5e"; ctx.fillText("■ Crew HP", 535, 15);
}

function startMission() {
  ensureAudio();
  document.getElementById("start-overlay").style.display = "none";
  document.getElementById("game-root").focus();
  state.started = true;
  playSfx(440, 0.25, "triangle", 0.09, 880);
  setStatus(`🚀 Mission Live! Explore Shackleton Crater as ${CFG.heroName} — click any ? chip for NASA science tips!`);

  clearInterval(bgmTimer);
  bgmTimer = setInterval(() => {
    if (soundOn && state.started && !state.ended && !state.paused) {
      playSfx(bgmScale[bgmStep % bgmScale.length], 0.15, "sine", 0.015);
      bgmStep++;
    }
  }, 650);
}

function restartMission() {
  document.getElementById("debrief-overlay").style.display = "none";
  resetState();
  heroPos.set(0, 0, 1.5); wasInside = true;
  refreshBasketVisuals(); refreshPantryVisuals(); updateHUD();
  startMission();
}

window.addEventListener("keydown", e => {
  if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)) e.preventDefault();
  keys[e.code] = true;
  if (e.code === "Space") triggerJump();
  if (e.code === "KeyE") toggleDoor();
  if (e.code === "KeyQ") toggleShield();
});
window.addEventListener("keyup", e => { keys[e.code] = false; });

function bootWhenReady() {
  if (typeof THREE !== "undefined") {
    init3D(); updateHUD(); drawMinimap(); animate();
  } else {
    setTimeout(bootWhenReady, 120);
  }
}
bootWhenReady();
</script>
</body>
</html>
"""

final_html = GAME_HTML_TEMPLATE.replace("__GAME_CONFIG_JSON__", json.dumps(game_config))
components.html(final_html, height=842, scrolling=False)

st.caption("🤖 **NASA Space Apps Challenge SI Disclosure:** Conceived by our team; Python/Streamlit, Three.js WebGL 3D, and Web Audio code built with SI assistance from Gemini. Grounded in live & archived NASA DONKI (FLR/CME), NASA EPIC, NASA OSDR (OSD-895, OSD-767, OSD-137), NASA RadLab BLEO, CSA Deep Space Food Toolkit, ISRO Chandrayaan-3 South Pole research, and ESA lunar habitat/comms concepts.")
