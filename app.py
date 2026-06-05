"""Streamlit GUI dashboard for the smart-grid simulation."""

from __future__ import annotations

import streamlit as st

from neighborhood_3d import neighborhood_scene_height, render_neighborhood_scene
from smart_grid import build_simulation_payload


MAX_BUILDINGS = 24


def inject_page_css() -> None:
    """Apply a compact glass-style shell around the Streamlit controls."""

    st.markdown(
        """
        <style>
          .stApp {
            background:
              radial-gradient(circle at 12% 5%, rgba(76, 154, 255, 0.18), transparent 28%),
              linear-gradient(180deg, #edf6fb 0%, #dfeaf2 100%);
          }
          .block-container {
            max-width: 1480px;
            padding-top: 1.1rem;
            padding-bottom: 1.5rem;
          }
          h1 {
            margin-bottom: 0.65rem;
            letter-spacing: 0;
          }
          div[data-testid="stHorizontalBlock"] {
            padding: 0.55rem;
            margin-bottom: 0.55rem;
            border: 1px solid rgba(255, 255, 255, 0.54);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.58);
            box-shadow: 0 16px 36px rgba(30, 48, 68, 0.1);
            backdrop-filter: blur(16px) saturate(1.1);
          }
          label, .stCheckbox label {
            font-weight: 700;
            color: #28384a;
          }
          iframe {
            border-radius: 8px;
            box-shadow: 0 22px 54px rgba(30, 48, 68, 0.16);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="SolarMate",
        page_icon="SM",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_page_css()
    st.title("SolarMate")

    building_col, solar_col, weather_col, seed_col = st.columns([1.15, 1.15, 1, 1])
    with building_col:
        building_count = st.slider("Buildings to simulate", 1, MAX_BUILDINGS, 12)
    with solar_col:
        solar_ratio = st.slider("Solar adoption", 0, 100, 50, step=5) / 100
    with weather_col:
        weather = st.select_slider("Weather", options=["Sunny", "Cloudy", "Rainy"], value="Sunny")
    with seed_col:
        seed = st.number_input("Scenario seed", min_value=1, max_value=9999, value=42)

    view_col, quality_col, flow_col = st.columns([1, 1, 1.2])
    with view_col:
        camera_mode = st.selectbox(
            "View",
            ["Neighborhood View", "Grid View", "Energy View"],
            index=0,
        )
    with quality_col:
        quality_mode = st.selectbox(
            "Quality",
            ["High Quality", "Balanced", "Performance"],
            index=1,
        )
    with flow_col:
        always_show_flow = st.checkbox("Always show energy flow", value=False)

    payload = build_simulation_payload(
        house_count=building_count,
        solar_ratio=solar_ratio,
        seed=int(seed),
        weather=weather,
    )

    # The scene module owns the isometric layout, hover tooltips, cables, and flow animation.
    st.iframe(
        render_neighborhood_scene(
            payload,
            always_show_flow=always_show_flow,
            quality_mode=quality_mode,
            camera_mode=camera_mode,
        ),
        height=neighborhood_scene_height(building_count),
    )


if __name__ == "__main__":
    main()
