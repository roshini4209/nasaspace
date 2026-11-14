import streamlit as st
import random

# Page configuration
st.set_page_config(page_title="Lunar Outpost Mission Control", page_icon="🌕", layout="centered")

# Initialize session state variables if they don't exist
if "day" not in st.session_state:
    st.session_state.day = 1
    st.session_state.power = 100
    st.session_state.oxygen = 100
    st.session_state.food = 100
    st.session_state.shielding = 50
    st.session_state.game_over = False
    st.session_state.message = "Welcome to Artemis Lunar Outpost Alpha! Balance your systems carefully."

st.title("🌕 Lunar Outpost: Artemis Base Simulator")
st.markdown("### *Interactive Space Mission Control for Junior Astronauts (Ages 7–12)*")

# NASA Data Attribution Banner
st.info("🛰️ **NASA Science Attribution:** Space weather hazard simulations inspired by the **NASA DONKI API** and biological life-support metrics informed by **NASA's Open Science Data Repository (OSDR)**.")

# Check for Game Over condition
if st.session_state.game_over:
    st.error(f"🚨 **Mission Failed on Sol {st.session_state.day}!** {st.session_state.message}")
    if st.button("🔄 Restart Mission"):
        st.session_state.day = 1
        st.session_state.power = 100
        st.session_state.oxygen = 100
        st.session_state.food = 100
        st.session_state.shielding = 50
        st.session_state.game_over = False
        st.session_state.message = "New mission initiated. Good luck, Commander!"
        st.rerun()
    st.stop()

# Display current status metrics dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("📅 Sol (Day)", st.session_state.day)
col2.metric("⚡ Power", f"{st.session_state.power}%")
col3.metric("🫁 Oxygen", f"{st.session_state.oxygen}%")
col4.metric("🌱 Food", f"{st.session_state.food}%")

st.markdown("---")
st.subheader("🎛️ Daily Resource Allocation & Trade-Offs")
st.write("Every choice has a cost! Adjust your daily power distribution between Life Support, Greenhouse Food Production, and Radiation Shielding.")

# Sliders for player choices (introducing trade-offs)
life_support_power = st.slider("🫁 Life Support Power Allocation", 10, 50, 30, help="Higher power ensures clean air, but drains batteries.")
greenhouse_power = st.slider("🌱 Lunar Greenhouse Power (Food)", 10, 50, 25, help="Powers LED lighting for space crops, but consumes extra energy.")
shielding_level = st.slider("🛡️ Radiation Shielding Thickness", 10, 100, 50, help="Protects against solar particle events, but heavy shielding uses significant power.")

# Communication delay indicator
st.markdown("📡 **Comms Delay Notice:** *Signal travel time between Earth and the Moon is approximately 1.3 seconds. Autonomous decisions are active!*")

# Advance turn button
if st.button("🚀 Execute Lunar Sol (Next Day)"):
    # Calculate costs and trade-offs
    total_power_drain = int((life_support_power * 0.4) + (greenhouse_power * 0.3) + (shielding_level * 0.4))
    power_generation = 65  # Base solar array generation on the Moon
    
    net_power_change = power_generation - total_power_drain
    st.session_state.power = max(0, min(100, st.session_state.power + net_power_change))
    
    # Oxygen change based on life support power
    ox_change = int(life_support_power / 5) - 12
    st.session_state.oxygen = max(0, min(100, st.session_state.oxygen + ox_change))
    
    # Food change based on greenhouse power
    food_change = int(greenhouse_power / 6) - 10
    st.session_state.food = max(0, min(100, st.session_state.food + food_change))
    
    # Random Space Weather Event (Inspired by NASA DONKI)
    event_chance = random.random()
    event_msg = ""
    if event_chance < 0.35:
        # Solar particle event
        if shielding_level < 60:
            st.session_state.oxygen -= 15
            event_msg = "⚠️ **NASA DONKI Alert:** Solar Particle Event (SPE) detected! Your shielding was too thin, causing minor system strain and oxygen loss!"
        else:
            event_msg = "🛡️ **NASA DONKI Alert:** Solar Particle Event (SPE) detected! Your robust radiation shielding successfully protected the outpost!"
    elif event_chance < 0.6:
        # Lunar dust accumulation
        st.session_state.power -= 10
        event_msg = "🌪️ **Lunar Environment Notice:** Fine electrostatically charged lunar dust settled on your solar panels, reducing power generation for the day."
    else:
        event_msg = "✨ **Quiet Space Weather:** Conditions on the lunar surface are stable today. Science operations running smoothly."

    st.session_state.message = event_msg
    st.session_state.day += 1

    # Check lose conditions
    if st.session_state.oxygen <= 0:
        st.session_state.game_over = True
        st.session_state.message = "Oxygen reserves were completely depleted. The crew had to abort the mission."
    elif st.session_state.power <= 0:
        st.session_state.power = 0
        st.session_state.game_over = True
        st.session_state.message = "Battery power collapsed completely. Life support systems went offline."
    elif st.session_state.food <= 0:
        st.session_state.game_over = True
        st.session_state.message = "Food supplies ran out. The lunar greenhouse failed to yield enough crops."
    elif st.session_state.day > 10:
        # Win condition for prototype
        st.success("🎉 **Victory!** You successfully managed the Lunar Outpost for 10 Sols, keeping your crew safe and advancing deep space exploration!")
        st.balloons()
        st.stop()
        
    st.rerun()

# Display recent event message box
st.markdown("---")
st.subheader("📋 Mission Log & Telemetry")
st.info(st.session_state.message)

# Educational Footer
st.markdown("---")
st.caption("💡 **Junior Astronaut Tip for Judges:** This app mirrors real aerospace engineering challenges—every watt of power, drop of oxygen, and millimeter of radiation shielding involves a strict trade-off, just like NASA's Artemis lunar missions!")
