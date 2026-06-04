"""Streamlit GUI dashboard for the smart-grid simulation."""

from __future__ import annotations

import streamlit as st

from neighborhood_scene import neighborhood_scene_height, render_neighborhood_scene
from smart_grid import build_simulation_payload


MAX_BUILDINGS = 24


def main() -> None:
    st.set_page_config(
        page_title="Smart Grid Dashboard",
        page_icon="SG",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("Smart-Grid Town Dashboard")
    st.caption(
        "A one-day town simulation with shop lots, solar homes, weather-aware solar output, "
        "and hover-based power flow."
    )

    building_col, solar_col, weather_col, seed_col = st.columns([1.15, 1.15, 1, 1])
    with building_col:
        building_count = st.slider("Buildings to simulate", 1, MAX_BUILDINGS, 12)
    with solar_col:
        solar_ratio = st.slider("Solar adoption", 0, 100, 50, step=5) / 100
    with weather_col:
        weather = st.select_slider("Weather", options=["Sunny", "Cloudy", "Rainy"], value="Sunny")
    with seed_col:
        seed = st.number_input("Scenario seed", min_value=1, max_value=9999, value=42)

    always_show_flow = st.checkbox("Always show energy flow", value=False)

    payload = build_simulation_payload(
        house_count=building_count,
        solar_ratio=solar_ratio,
        seed=int(seed),
        weather=weather,
    )

    # The scene module owns the isometric layout, hover tooltips, cables, and flow animation.
    st.iframe(
        render_neighborhood_scene(payload, always_show_flow=always_show_flow),
        height=neighborhood_scene_height(building_count),
    )


if __name__ == "__main__":
    main()
