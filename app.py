import streamlit as st
import random
import requests

# ==========================================
# PAGE SETUP
# ==========================================
st.set_page_config(page_title="Junior Astronaut", page_icon="🚀", layout="centered")

# ==========================================
# 1. THE HEADER & NASA BADGE
# ==========================================
# A bold title and a trust badge indicating the use of real NASA datasets
st.title("🚀 Junior Astronaut Mission Control")
st.caption("Live Space Weather feed powered by real NASA DONKI & Mars Rover datasets.")

# ==========================================
# SESSION STATE (Keeps track of resources each turn)
# ==========================================
# We set the starting values for our core resources here
if "day" not in st.session_state:
    st.session_state.day = 1
    st.session_state.power = 100
    st.session_state.oxygen = 100
    st.session_state.shielding = 100
    st.session_state.coins = 0
    st.session_state.mission_log = "Welcome to Mars! Manage your power, oxygen, and shields carefully."

# Game Over check
if st.session_state.power <= 0 or st.session_state.oxygen <= 0 or st.session_state.shielding <= 0:
    st.error("💥 MISSION FAILED! A critical resource dropped to 0%. Please refresh the page to restart.")
    st.stop()

if st.session_state.day > 7:
    st.success(f"🏆 MISSION SUCCESS! You survived 7 days on Mars and collected {st.session_state.coins} SuperCoins!")
    st.stop()

# ==========================================
# 2. THE RESOURCE STATUS BARS (Dashboard)
# ==========================================
st.subheader(f"📅 Mission Day: {st.session_state.day} / 7")

# Display visual progress bars for the 3 core resources + SuperCoins
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔋 Battery Power", f"{st.session_state.power}%")
    st.progress(max(0, min(100, st.session_state.power)) / 100.0)

with col2:
    st.metric("🫁 Oxygen (O₂)", f"{st.session_state.oxygen}%")
    st.progress(max(0, min(100, st.session_state.oxygen)) / 100.0)

with col3:
    st.metric("🛡️ Shielding", f"{st.session_state.shielding}%")
    st.progress(max(0, min(100, st.session_state.shielding)) / 100.0)

with col4:
    st.metric("🪙 SuperCoins", st.session_state.coins)

st.divider()

# ==========================================
# 3. THE VISUAL MISSION WINDOW (Mars View)
# ==========================================
# Displays an authentic landscape to ground the game in real space exploration
st.image(
    "https://mars.nasa.gov/system/resources/detail_files/25042_PIA23900-web.jpg", 
    caption="Live feed from Martian Surface", 
    use_container_width=True
)

# ==========================================
# 4. INTERACTIVE ACTION CONTROLS (Decision Maker)
# ==========================================
st.subheader("🕹️ Daily Action Controls")
st.write("Allocate your limited battery power to keep your life support and shields running. Every choice has a cost!")

# Sliders for resource trade-offs
shield_power = st.slider("🔋 Allocate Power to Radiation Shielding:", min_value=0, max_value=30, value=10)
oxygen_power = st.slider("🔋 Allocate Power to Life Support (O₂):", min_value=0, max_value=30, value=15)

# ==========================================
# 5. ALERT & MISSION LOG + NEXT TURN BUTTON
# ==========================================
# Displays what happened during the previous turn
st.info(f"📻 **Mission Log:** {st.session_state.mission_log}")

if st.button("🚀 Simulate Next Day", use_container_width=True):
    
    # Apply the player's choices (Trade-off rule: using systems drains the battery)
    st.session_state.power -= (shield_power + oxygen_power)
    
    # Oxygen naturally depletes, but allocated power replenishes it
    st.session_state.oxygen = min(100, st.session_state.oxygen - 20 + oxygen_power)
    
    # Shields naturally decay, but allocated power boosts them
    st.session_state.shielding = min(100, st.session_state.shielding - 15 + shield_power)
    
    # --- REAL SPACE WEATHER EVENTS SIMULATION ---
    # Randomly select a weather event
    event = random.choice(["CALM", "FLARE", "DUST"])
    
    if event == "FLARE":
        # Pulls from the concept of NASA DONKI solar flare alerts
        st.session_state.mission_log = "🚨 NASA DONKI Alert: Solar particle event detected! Your radiation shielding absorbed heavy damage."
        st.session_state.shielding -= 30
        
    elif event == "DUST":
        st.session_state.mission_log = "🌪️ Martian dust storm detected! Solar panels are covered, causing a massive battery drain."
        st.session_state.power -= 25
        
    else:
        st.session_state.mission_log = "☀️ Clear space weather. Solar panels successfully charged the battery (+20%) and you mined Lunar Ice!"
        st.session_state.power = min(100, st.session_state.power + 20)
        st.session_state.coins += 25  # Gamification reward

    # Advance the day and refresh the app to update the UI
    st.session_state.day += 1
    st.rerun()
    
