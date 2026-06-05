"""Isometric neighborhood scene renderer for the Streamlit dashboard."""

from __future__ import annotations

import json
from textwrap import dedent


def neighborhood_scene_height(building_count: int) -> int:
    """Return an iframe height large enough for the responsive SVG scene."""

    return 1040


def render_neighborhood_scene(
    payload: dict,
    always_show_flow: bool = False,
    quality_mode: str = "Balanced",
    camera_mode: str = "Neighborhood View",
) -> str:
    """Render a self-contained HTML/SVG 3D-style neighborhood scene.

    The payload comes from ``smart_grid.build_simulation_payload`` and keeps the
    simulation data separate from the rendering details in this module.
    """

    data_json = json.dumps(payload)
    quality_json = json.dumps(_normalize_quality_mode(quality_mode))
    camera_json = json.dumps(_normalize_camera_mode(camera_mode))

    html = dedent(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <style>
            :root {
              --sky-top: #8bd0ff;
              --sky-bottom: #e8f7ff;
              --ground: #60b86b;
              --ground-dark: #3f8a55;
              --road: #5d6672;
              --road-dark: #464f5c;
              --road-line: rgba(255, 255, 255, 0.62);
              --cable: #26384b;
              --cable-soft: rgba(38, 56, 75, 0.22);
              --panel: rgba(255, 255, 255, 0.9);
              --text: #142231;
              --muted: #5c6b78;
              --positive: #1f9d55;
              --negative: #c93535;
              --neutral: #6b7280;
              --seller: #1f9d55;
              --buyer: #e08b21;
              --balanced: #718096;
              --glass: rgba(255, 255, 255, 0.72);
              --glass-border: rgba(255, 255, 255, 0.46);
              --card-shadow: 0 18px 36px rgba(24, 36, 48, 0.13);
              --stat-bg: rgba(255, 255, 255, 0.48);
              --stat-border: rgba(255, 255, 255, 0.34);
              --tooltip-bg: rgba(255, 255, 255, 0.82);
              --tooltip-border: rgba(255, 255, 255, 0.58);
              --window-light: #8bd3ff;
              --streetlight-alpha: 0;
              --mist-alpha: 0;
            }

            * { box-sizing: border-box; }

            body {
              margin: 0;
              color: var(--text);
              font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              background: linear-gradient(180deg, #eef5fb, #dfeaf3);
            }

            .dashboard {
              min-height: 960px;
              position: relative;
              overflow: hidden;
              border: 1px solid rgba(32, 48, 64, 0.12);
              border-radius: 8px;
              color: var(--text);
              background: linear-gradient(180deg, var(--sky-top), var(--sky-bottom));
              transition: background 420ms ease;
            }

            .dashboard[data-period="night"] {
              --sky-top: #10182f;
              --sky-bottom: #29355d;
              --ground: #263f35;
              --ground-dark: #1d3028;
              --road: #313946;
              --road-dark: #252d38;
              --road-line: rgba(255, 255, 255, 0.28);
              --panel: rgba(31, 43, 67, 0.68);
              --text: #eef5ff;
              --muted: #c4d0e0;
              --positive: #4cff88;
              --negative: #ff6b6b;
              --neutral: #d0d0d0;
              --glass: rgba(20, 24, 38, 0.78);
              --glass-border: rgba(255, 255, 255, 0.18);
              --card-shadow: 0 18px 44px rgba(0, 0, 0, 0.34), 0 0 18px rgba(164, 202, 255, 0.08);
              --stat-bg: rgba(255, 255, 255, 0.1);
              --stat-border: rgba(255, 255, 255, 0.16);
              --tooltip-bg: rgba(20, 24, 38, 0.9);
              --tooltip-border: rgba(255, 255, 255, 0.22);
              --window-light: #ffd982;
              --streetlight-alpha: 0.9;
            }

            .dashboard[data-period="dawn"] {
              --sky-top: #f0a36a;
              --sky-bottom: #f7d891;
              --ground: #63ad69;
              --ground-dark: #438757;
              --window-light: #aee3ff;
            }

            .dashboard[data-period="dusk"] {
              --sky-top: #34416a;
              --sky-bottom: #dc875f;
              --ground: #3f7655;
              --ground-dark: #2f5e43;
              --streetlight-alpha: 0.32;
            }

            .dashboard[data-weather="Cloudy"] {
              --sky-top: #aebdca;
              --sky-bottom: #dbe3ea;
              --ground: #5d9a65;
              --ground-dark: #3f754d;
              --glass: rgba(246, 249, 252, 0.66);
            }

            .dashboard[data-weather="Rainy"] {
              --sky-top: #657383;
              --sky-bottom: #a0acb7;
              --ground: #4d7b5b;
              --ground-dark: #315a42;
              --road: #46515c;
              --road-dark: #36404c;
              --mist-alpha: 0.22;
            }

            .dashboard[data-weather="Cloudy"][data-period="night"],
            .dashboard[data-weather="Rainy"][data-period="night"] {
              --sky-top: #151b27;
              --sky-bottom: #313a4b;
              --ground: #20362b;
              --ground-dark: #192a22;
              --mist-alpha: 0.16;
            }

            .dashboard::before {
              content: "";
              position: absolute;
              inset: 0;
              pointer-events: none;
              background:
                radial-gradient(circle at 82% 14%, rgba(255, 232, 130, var(--orb-alpha, 0.82)) 0 32px, transparent 34px),
                linear-gradient(180deg, rgba(255, 255, 255, 0.16), transparent 34%);
            }

            .dashboard[data-period="night"]::before {
              background:
                radial-gradient(circle at 80% 14%, rgba(238, 244, 255, 0.9) 0 24px, transparent 26px),
                radial-gradient(circle at 18% 13%, rgba(255, 255, 255, 0.7) 0 1px, transparent 2px),
                radial-gradient(circle at 32% 23%, rgba(255, 255, 255, 0.6) 0 1px, transparent 2px),
                radial-gradient(circle at 45% 10%, rgba(255, 255, 255, 0.66) 0 1px, transparent 2px),
                radial-gradient(circle at 66% 25%, rgba(255, 255, 255, 0.52) 0 1px, transparent 2px);
            }

            .weather-layer {
              position: absolute;
              inset: 0;
              z-index: 3;
              pointer-events: none;
              overflow: hidden;
            }

            .cloud {
              position: absolute;
              z-index: 0;
              width: 180px;
              height: 58px;
              opacity: 0;
              border-radius: 999px;
              background:
                radial-gradient(circle at 24% 55%, rgba(255, 255, 255, 0.88) 0 29px, transparent 30px),
                radial-gradient(circle at 48% 35%, rgba(255, 255, 255, 0.94) 0 39px, transparent 40px),
                radial-gradient(circle at 72% 55%, rgba(255, 255, 255, 0.86) 0 31px, transparent 32px),
                rgba(255, 255, 255, 0.78);
              animation: cloud-drift 26s ease-in-out infinite alternate;
            }

            .cloud.one { left: 6%; top: 10%; }
            .cloud.two { left: 42%; top: 14%; transform: scale(1.15); animation-duration: 32s; }
            .cloud.three { right: 7%; top: 8%; transform: scale(0.92); animation-duration: 29s; }

            @keyframes cloud-drift {
              from { margin-left: -18px; }
              to { margin-left: 34px; }
            }

            .dashboard[data-weather="Cloudy"] .cloud {
              opacity: 0.72;
            }

            .dashboard[data-weather="Rainy"] .cloud {
              opacity: 0.84;
              filter: grayscale(0.45) brightness(0.82);
            }

            .rain-layer {
              position: absolute;
              inset: -70px 0 0;
              z-index: 2;
              opacity: 0;
              background-image: repeating-linear-gradient(
                110deg,
                rgba(255, 255, 255, 0) 0 8px,
                rgba(235, 247, 255, 0.56) 9px 10px,
                rgba(255, 255, 255, 0) 11px 26px
              );
              background-size: 118px 96px;
              animation: rain-move 0.48s linear infinite;
            }

            .dashboard[data-weather="Rainy"] .rain-layer {
              opacity: 0.34;
            }

            .dashboard[data-weather="Rainy"][data-period="night"] .rain-layer {
              opacity: 0.43;
            }

            .mist {
              position: absolute;
              inset: 0;
              z-index: 1;
              opacity: var(--mist-alpha);
              background:
                linear-gradient(180deg, transparent 0 42%, rgba(229, 239, 244, 0.34) 54%, transparent 78%),
                radial-gradient(ellipse at 50% 62%, rgba(236, 246, 250, 0.34), transparent 58%);
            }

            @keyframes rain-move {
              from { background-position: 0 0; }
              to { background-position: -32px 64px; }
            }

            .topbar {
              position: relative;
              z-index: 4;
              display: grid;
              grid-template-columns: minmax(280px, 0.9fr) minmax(360px, 1.35fr);
              gap: 12px;
              padding: 12px;
            }

            .control-panel,
            .stats-panel {
              background: var(--glass);
              border: 1px solid var(--glass-border);
              border-radius: 8px;
              color: var(--text);
              box-shadow: var(--card-shadow);
              backdrop-filter: blur(16px) saturate(1.14);
            }

            .control-panel {
              display: grid;
              grid-template-columns: auto minmax(200px, 1fr);
              align-items: center;
              gap: 12px;
              padding: 12px;
            }

            .play-button {
              width: 44px;
              height: 44px;
              border: 0;
              border-radius: 8px;
              color: #fff;
              background: #244c78;
              font-size: 18px;
              font-weight: 900;
              cursor: pointer;
              box-shadow: inset 0 -3px 0 rgba(0, 0, 0, 0.18);
            }

            .play-button:hover {
              background: #1c3d64;
            }

            .slider-wrap {
              display: grid;
              gap: 8px;
            }

            .time-row {
              display: flex;
              align-items: baseline;
              justify-content: space-between;
              gap: 12px;
            }

            .time-label {
              font-size: 24px;
              font-weight: 900;
              font-variant-numeric: tabular-nums;
            }

            .period-label {
              color: var(--muted);
              font-size: 12px;
              font-weight: 800;
              letter-spacing: 0.08em;
              text-transform: uppercase;
            }

            input[type="range"] {
              width: 100%;
              accent-color: #244c78;
            }

            .stats-panel {
              padding: 10px;
            }

            .stats-title {
              color: var(--muted);
              font-size: 12px;
              font-weight: 900;
              letter-spacing: 0.08em;
              text-transform: uppercase;
            }

            .stat-grid {
              display: grid;
              grid-template-columns: repeat(3, minmax(0, 1fr));
              gap: 10px;
              margin-top: 9px;
            }

            .stat {
              min-height: 62px;
              padding: 8px 10px;
              border: 1px solid var(--stat-border);
              border-radius: 8px;
              background: var(--stat-bg);
              box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.28);
            }

            .dashboard[data-period="night"] .stat,
            .dashboard[data-period="night"] .control-panel,
            .dashboard[data-period="night"] .stats-panel {
              background: rgba(28, 39, 62, 0.58);
              border-color: rgba(210, 226, 255, 0.2);
            }

            .stat-label {
              color: var(--muted);
              font-size: 11px;
              font-weight: 800;
            }

            .stat-value {
              margin-top: 6px;
              color: var(--text);
              font-size: 18px;
              font-weight: 900;
              font-variant-numeric: tabular-nums;
            }
            .stat-value.positive { color: var(--positive); }
            .stat-value.negative { color: var(--negative); }
            .stat-value.neutral { color: var(--neutral); }

            .scene-shell {
              position: relative;
              z-index: 2;
              padding: 0 16px 30px;
            }

            .grid-svg {
              width: 100%;
              max-width: 1380px;
              display: block;
              margin: 0 auto;
              overflow: visible;
            }

            .ground { fill: var(--ground); }
            .ground-dark { fill: var(--ground-dark); opacity: 0.82; }
            .grass-patch { fill: rgba(255, 255, 255, 0.12); }
            .road { fill: var(--road); }
            .road-side { fill: var(--road-dark); }
            .lane-line {
              stroke: var(--road-line);
              stroke-width: 3.2;
              stroke-linecap: round;
              stroke-dasharray: 19 18;
            }
            .cross-road { fill: rgba(75, 84, 96, 0.9); }
            .driveway {
              fill: rgba(80, 89, 101, 0.88);
              stroke: rgba(255, 255, 255, 0.18);
              stroke-width: 1.2;
            }
            .sidewalk {
              fill: rgba(229, 232, 218, 0.92);
              stroke: rgba(84, 95, 78, 0.2);
              stroke-width: 1.4;
            }
            .wet-gloss { fill: rgba(215, 232, 240, 0); }
            .dashboard[data-weather="Rainy"] .wet-gloss { fill: rgba(215, 232, 240, 0.18); }
            .rain-reflection {
              fill: rgba(235, 246, 255, 0);
            }
            .dashboard[data-weather="Rainy"] .rain-reflection {
              fill: rgba(235, 246, 255, 0.2);
            }
            .tree-trunk { fill: #7a5133; }
            .tree-canopy {
              fill: #2f8d58;
              transform-box: fill-box;
              transform-origin: bottom center;
              animation: tree-sway 5.8s ease-in-out infinite alternate;
            }
            @keyframes tree-sway {
              from { transform: rotate(-1.5deg); }
              to { transform: rotate(1.5deg); }
            }
            .streetlight-pole {
              stroke: #344354;
              stroke-width: 4;
              stroke-linecap: round;
            }
            .streetlight-lamp {
              fill: #ffe08a;
              stroke: #475569;
              stroke-width: 2;
              opacity: 0.36;
            }
            .dashboard[data-period="dusk"] .streetlight-lamp,
            .dashboard[data-period="night"] .streetlight-lamp {
              opacity: 1;
              filter: drop-shadow(0 0 10px rgba(255, 224, 138, 0.72));
            }
            .streetlight-glow {
              fill: rgba(255, 224, 138, 0.22);
              opacity: var(--streetlight-alpha);
              filter: blur(1px);
            }

            .grid-spine {
              stroke: #253446;
              stroke-width: 12;
              stroke-linecap: round;
              filter: drop-shadow(0 2px 1px rgba(255, 255, 255, 0.36));
            }

            .grid-spine-highlight {
              stroke: rgba(255, 255, 255, 0.42);
              stroke-width: 2;
              stroke-linecap: round;
            }

            .cable-soft {
              stroke: var(--cable-soft);
              stroke-width: 9;
              stroke-linecap: round;
              fill: none;
            }

            .cable {
              stroke: var(--cable);
              stroke-width: 3.8;
              stroke-linecap: round;
              fill: none;
            }

            .junction-node {
              fill: #fbfdff;
              stroke: var(--cable);
              stroke-width: 2.3;
            }

            .debug-grid-node {
              fill: #ff3b30;
              stroke: #fff;
              stroke-width: 2;
            }

            .pole-shadow { fill: rgba(20, 30, 38, 0.18); }
            .utility-pole {
              fill: #5b4632;
              stroke: #34281d;
              stroke-width: 2;
            }
            .pole-arm {
              stroke: #4b3929;
              stroke-width: 4.2;
              stroke-linecap: round;
            }
            .pole-insulator {
              fill: #e8f3ff;
              stroke: #53687d;
              stroke-width: 1.4;
            }

            .flow {
              display: none;
              pointer-events: none;
            }

            .flow.active {
              display: block;
            }

            .active-flow-line {
              fill: none;
              stroke-width: 8.5;
              stroke-linecap: round;
              stroke-linejoin: round;
              stroke-dasharray: 20 19;
              animation: flow-dash 0.72s linear infinite;
              opacity: 0.94;
              filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.96));
            }

            .active-flow-line.GREEN,
            .active-flow-line.SELLER,
            .active-flow-line.LOCAL,
            .active-flow-line.IMPORT,
            .active-flow-line.EXPORT {
              stroke: #2dff9d;
            }

            .active-flow-line.YELLOW,
            .active-flow-line.BUYER {
              stroke: #ffd166;
            }

            @keyframes flow-dash {
              from { stroke-dashoffset: 0; }
              to { stroke-dashoffset: -39; }
            }

            .flow-dot {
              filter:
                drop-shadow(0 0 5px rgba(255, 255, 255, 1))
                drop-shadow(0 0 12px currentColor);
            }
            .flow-dot.GREEN,
            .flow-dot.SELLER,
            .flow-dot.LOCAL,
            .flow-dot.IMPORT,
            .flow-dot.EXPORT {
              fill: #31e88d;
              color: #2dff9d;
            }

            .flow-dot.YELLOW,
            .flow-dot.BUYER {
              fill: #ffb14f;
              color: #ffd166;
            }

            .dashboard[data-quality="Balanced"] .active-flow-line {
              stroke-width: 7;
              filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.76));
            }

            .dashboard[data-quality="Balanced"] .flow-dot {
              filter: drop-shadow(0 0 8px currentColor);
            }

            .dashboard[data-quality="Performance"] .active-flow-line {
              stroke-width: 6;
              filter: none;
              opacity: 0.82;
            }

            .dashboard[data-quality="Performance"] .flow-dot {
              display: none;
            }

            .dashboard[data-camera-mode="Grid View"] .building-layer {
              opacity: 0.48;
            }

            .dashboard[data-camera-mode="Grid View"] .ground,
            .dashboard[data-camera-mode="Grid View"] .ground-dark,
            .dashboard[data-camera-mode="Grid View"] .road,
            .dashboard[data-camera-mode="Grid View"] .sidewalk,
            .dashboard[data-camera-mode="Grid View"] .driveway {
              opacity: 0.62;
            }

            .dashboard[data-camera-mode="Energy View"] .building-layer {
              opacity: 0.28;
            }

            .dashboard[data-camera-mode="Energy View"] .ground,
            .dashboard[data-camera-mode="Energy View"] .ground-dark,
            .dashboard[data-camera-mode="Energy View"] .road,
            .dashboard[data-camera-mode="Energy View"] .sidewalk,
            .dashboard[data-camera-mode="Energy View"] .driveway {
              opacity: 0.36;
            }

            .dashboard[data-camera-mode="Energy View"] .cable,
            .dashboard[data-camera-mode="Energy View"] .junction-node {
              filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.28));
            }

            .substation-pad { fill: rgba(20, 28, 38, 0.2); }
            .substation-base {
              fill: #2b4058;
              stroke: rgba(255, 255, 255, 0.75);
              stroke-width: 4;
              filter: drop-shadow(0 14px 16px rgba(18, 26, 36, 0.24));
            }
            .substation-side { fill: #1f2f42; }
            .substation-top { fill: #50697f; }
            .substation-bolt { fill: rgba(255, 255, 255, 0.86); }
            .transformer-box {
              fill: #435a70;
              stroke: #1f2e3d;
              stroke-width: 3;
            }
            .substation-label-bg {
              fill: rgba(255, 255, 255, 0.9);
              stroke: rgba(24, 34, 44, 0.18);
              stroke-width: 1;
            }
            .substation-label {
              fill: #1b2734;
              font-size: 11px;
              font-weight: 900;
              text-anchor: middle;
              dominant-baseline: middle;
              pointer-events: none;
            }
            .substation {
              cursor: pointer;
            }

            .building-group {
              cursor: pointer;
              filter: drop-shadow(0 12px 9px rgba(18, 28, 38, 0.2));
            }
            .dashboard[data-weather="Cloudy"] .building-group {
              filter: saturate(0.9) drop-shadow(0 10px 8px rgba(18, 28, 38, 0.16));
            }
            .dashboard[data-weather="Rainy"] .building-group {
              filter: saturate(0.82) brightness(0.9) drop-shadow(0 13px 10px rgba(10, 18, 26, 0.24));
            }
            .building-group:focus { outline: none; }
            .building-shadow { fill: rgba(15, 24, 32, 0.18); }
            .hover-area {
              fill: #fff;
              opacity: 0.001;
              pointer-events: all;
            }

            .home-front {
              fill: var(--wall-color, #f0c66c);
              stroke: #8e6334;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .home-side {
              fill: var(--wall-side, #d7a957);
              stroke: #8e6334;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .home-roof-main {
              fill: var(--roof-color, #a43a32);
              stroke: var(--roof-stroke, #72302b);
              stroke-width: 3;
              shape-rendering: crispEdges;
            }
            .home-roof-side {
              fill: var(--roof-side, #7d2e2a);
              stroke: var(--roof-stroke, #72302b);
              stroke-width: 3;
              shape-rendering: crispEdges;
            }
            .window {
              fill: var(--window-light);
              stroke: #6d4d32;
              stroke-width: 2.6;
              shape-rendering: crispEdges;
            }
            .dashboard[data-period="night"] .window,
            .dashboard[data-period="night"] .shop-window {
              fill: #ffd982;
              filter: drop-shadow(0 0 7px rgba(255, 217, 130, 0.76));
            }
            .wet-roof {
              fill: rgba(255, 255, 255, 0);
              pointer-events: none;
            }
            .dashboard[data-weather="Rainy"] .wet-roof {
              fill: rgba(220, 238, 246, 0.16);
            }
            .door {
              fill: #7f563b;
              stroke: #5c3b2a;
              stroke-width: 2.6;
              shape-rendering: crispEdges;
            }
            .door-knob { fill: #f8d56c; }
            .solar-panel {
              fill: #1d557f;
              stroke: #0e314c;
              stroke-width: 2;
              shape-rendering: crispEdges;
            }
            .solar-line {
              stroke: rgba(255, 255, 255, 0.3);
              stroke-width: 1.3;
            }
            .solar-panel.small { opacity: 0.94; }
            .solar-panel.medium { opacity: 0.98; }
            .solar-panel.large { filter: drop-shadow(0 0 4px rgba(116, 202, 255, 0.34)); }
            .residential[data-variant="luxury"] .home-front {
              fill: var(--wall-color, #f4d88d);
            }
            .residential[data-variant="terrace"] .home-front {
              fill: var(--wall-color, #efbd77);
            }
            .home-extension {
              fill: var(--wall-side, #e8b964);
              stroke: #8e6334;
              stroke-width: 3;
            }
            .porch {
              fill: rgba(255, 255, 255, 0.34);
              stroke: #8e6334;
              stroke-width: 2.2;
            }
            .yard {
              fill: rgba(75, 154, 89, 0.32);
              stroke: rgba(54, 112, 66, 0.28);
              stroke-width: 1.4;
            }
            .garden-dot { fill: #f8d56c; }
            .drive-pad {
              fill: rgba(91, 99, 112, 0.5);
              stroke: rgba(255, 255, 255, 0.24);
              stroke-width: 1.4;
            }
            .roof-trim {
              stroke: rgba(255, 255, 255, 0.34);
              stroke-width: 2;
              stroke-linecap: round;
              fill: none;
            }

            .shop-front {
              fill: var(--shop-wall, #dfe8ef);
              stroke: #5a6c7b;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .shop-side {
              fill: var(--shop-side, #b8c8d3);
              stroke: #5a6c7b;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .shop-top {
              fill: var(--shop-roof, #546879);
              stroke: #2d3c49;
              stroke-width: 3;
              shape-rendering: crispEdges;
            }
            .shop-sign {
              fill: var(--shop-color, #2b7a8f);
              stroke: rgba(19, 31, 42, 0.52);
              stroke-width: 2.2;
              shape-rendering: crispEdges;
            }
            .shop-label {
              fill: #fff;
              font-size: 10px;
              font-weight: 900;
              text-anchor: middle;
              dominant-baseline: middle;
              pointer-events: none;
            }
            .shop-awning {
              fill: var(--awning-base, #fff0c9);
              stroke: #8d7150;
              stroke-width: 2;
              shape-rendering: crispEdges;
            }
            .shop-awning-stripe {
              fill: var(--awning-stripe, rgba(214, 67, 67, 0.78));
              shape-rendering: crispEdges;
            }
            .shop-window {
              fill: #9bd8ef;
              stroke: #516675;
              stroke-width: 2.4;
              shape-rendering: crispEdges;
            }
            .shop-door {
              fill: #8a5e43;
              stroke: #5b3d2c;
              stroke-width: 2.5;
              shape-rendering: crispEdges;
            }
            .commercial[data-size="large"] .shop-front {
              fill: var(--shop-wall, #e8eef3);
            }
            .commercial[data-size="large"] .shop-top {
              fill: var(--shop-roof, #415567);
            }
            .commercial[data-size="industrial"] .shop-front {
              fill: var(--shop-wall, #c5ccd3);
            }
            .commercial[data-size="industrial"] .shop-top {
              fill: var(--shop-roof, #46515d);
            }
            .shop-icon {
              fill: #fff;
              stroke: rgba(15, 23, 42, 0.24);
              stroke-width: 1.4;
              pointer-events: none;
            }
            .shop-icon-line {
              fill: none;
              stroke: #fff;
              stroke-width: 2.2;
              stroke-linecap: round;
              pointer-events: none;
            }
            .garage-door {
              fill: #71808e;
              stroke: #445463;
              stroke-width: 2.5;
            }
            .garage-line {
              stroke: rgba(255, 255, 255, 0.42);
              stroke-width: 1.4;
            }
            .bakery-chimney {
              fill: #8d4938;
              stroke: #5d3028;
              stroke-width: 2;
            }
            .bakery-smoke {
              fill: rgba(245, 247, 250, 0.64);
              animation: smoke-rise 3.8s ease-in-out infinite;
            }
            .bakery-smoke.two { animation-delay: 1.2s; }
            @keyframes smoke-rise {
              from { transform: translateY(0); opacity: 0.18; }
              45% { opacity: 0.58; }
              to { transform: translateY(-22px); opacity: 0; }
            }
            .outdoor-table {
              fill: #7f563b;
              stroke: #503626;
              stroke-width: 1.4;
            }
            .chair {
              fill: #aa6d45;
              stroke: #503626;
              stroke-width: 1.2;
            }
            .tire-icon {
              fill: #202a35;
              stroke: #7c8794;
              stroke-width: 2;
            }
            .machine-door {
              fill: #c5f0ff;
              stroke: #347b93;
              stroke-width: 2.2;
            }
            .tool-detail {
              stroke: #2f3b46;
              stroke-width: 2;
              stroke-linecap: round;
            }

            .connection {
              fill: #fbfdff;
              stroke: var(--cable);
              stroke-width: 3;
            }

            .tooltip.hidden { display: none; }
            .tooltip {
              pointer-events: none;
              filter: drop-shadow(0 16px 24px rgba(14, 23, 34, 0.26));
            }
            .tooltip-bg {
              fill: var(--tooltip-bg);
              stroke: var(--tooltip-border);
              stroke-width: 1.3;
            }
            .dashboard[data-period="night"] .tooltip-bg {
              fill: var(--tooltip-bg);
              stroke: var(--tooltip-border);
            }
            .tooltip-title {
              fill: var(--text);
              font-size: 17px;
              font-weight: 900;
            }
            .tooltip-label {
              fill: var(--muted);
              font-size: 11px;
              font-weight: 800;
            }
            .tooltip-value {
              fill: var(--text);
              font-size: 12px;
              font-weight: 900;
              text-anchor: end;
            }
            .tooltip-value.positive { fill: var(--positive); }
            .tooltip-value.negative { fill: var(--negative); }
            .tooltip-value.neutral { fill: var(--neutral); }

            .dashboard[data-quality="Performance"] .cloud,
            .dashboard[data-quality="Performance"] .rain-layer,
            .dashboard[data-quality="Performance"] .tree-canopy,
            .dashboard[data-quality="Performance"] .bakery-smoke {
              animation: none;
            }

            .dashboard[data-quality="Performance"][data-weather="Rainy"] .rain-layer {
              opacity: 0.22;
            }

            @media (max-width: 760px) {
              .topbar {
                grid-template-columns: 1fr;
              }

              .stat-grid {
                grid-template-columns: 1fr;
              }
            }
          </style>
        </head>
        <body>
          <div class="dashboard" id="dashboard">
            <div class="weather-layer">
              <div class="cloud one"></div>
              <div class="cloud two"></div>
              <div class="cloud three"></div>
              <div class="rain-layer"></div>
              <div class="mist"></div>
            </div>

            <div class="topbar">
              <section class="control-panel" aria-label="Time controls">
                <button class="play-button" id="playButton" type="button" aria-label="Play or pause time">></button>
                <div class="slider-wrap">
                  <div class="time-row">
                    <div class="time-label" id="timeLabel">12:00</div>
                    <div class="period-label" id="periodLabel">Day</div>
                  </div>
                  <input id="timeSlider" type="range" min="0" max="23" step="1" value="12" aria-label="Hour of day" />
                </div>
              </section>

              <section class="stats-panel" aria-label="Grid totals">
                <div class="stats-title">Current hour</div>
                <div class="stat-grid">
                  <div class="stat">
                    <div class="stat-label">Generated power</div>
                    <div class="stat-value" id="currentGeneration">0.00 kWh</div>
                  </div>
                  <div class="stat">
                    <div class="stat-label">Consumption power</div>
                    <div class="stat-value" id="currentConsumption">0.00 kWh</div>
                  </div>
                  <div class="stat">
                    <div class="stat-label">Net Energy</div>
                    <div class="stat-value" id="currentNet">0.00 kWh</div>
                  </div>
                </div>
                <div class="stats-title" style="margin-top: 12px;">Daily totals</div>
                <div class="stat-grid">
                  <div class="stat">
                    <div class="stat-label">Generated power</div>
                    <div class="stat-value" id="dailyGeneration">0.00 kWh</div>
                  </div>
                  <div class="stat">
                    <div class="stat-label">Consumption power</div>
                    <div class="stat-value" id="dailyConsumption">0.00 kWh</div>
                  </div>
                  <div class="stat">
                    <div class="stat-label">Net Energy</div>
                    <div class="stat-value" id="dailyNet">0.00 kWh</div>
                  </div>
                </div>
              </section>
            </div>

            <div class="scene-shell" id="sceneStage"></div>
          </div>

          <script type="application/json" id="simulationData">__DATA_JSON__</script>
          <script>
            const DATA = JSON.parse(document.getElementById("simulationData").textContent);
            const SVG_NS = "http://www.w3.org/2000/svg";

            const dashboard = document.getElementById("dashboard");
            const sceneStage = document.getElementById("sceneStage");
            const playButton = document.getElementById("playButton");
            const timeSlider = document.getElementById("timeSlider");
            const timeLabel = document.getElementById("timeLabel");
            const periodLabel = document.getElementById("periodLabel");

            const LAYOUT = {
              baseWidth: 1400,
              height: 820,
              buildingWidth: 112,
              buildingHeight: 142,
              sidePadding: 120,
              slotWidth: 128,
              clusterGap: 260,
              topRowY: 176,
              bottomRowY: 524,
              roadY: 424,
              roadHeight: 88,
              mainGridY: 358,
              substationY: 58,
              substationCorridorHalfWidth: 138,
            };
            const DEBUG_GRID_NODES = false;
            const SCENE_STATE_KEY = "solarmate.sceneState";
            const savedSceneState = loadSceneState();

            let activeHour = savedHour(savedSceneState.hour);
            let playTimer = null;
            let currentSvg = null;
            let alwaysShowFlow = __ALWAYS_SHOW_FLOW__;
            const QUALITY_MODE = __QUALITY_MODE__;
            const CAMERA_MODE = __CAMERA_MODE__;
            let restorePlaying = savedSceneState.playing === true;

            const DAY_THEME = {
              text: "#142231",
              muted: "#5c6b78",
              positive: "#1f9d55",
              negative: "#c93535",
              neutral: "#6b7280",
              glass: "rgba(255, 255, 255, 0.72)",
              glassBorder: "rgba(255, 255, 255, 0.46)",
              cardShadow: "0 18px 36px rgba(24, 36, 48, 0.13)",
              statBg: "rgba(255, 255, 255, 0.48)",
              statBorder: "rgba(255, 255, 255, 0.34)",
              tooltipBg: "rgba(255, 255, 255, 0.82)",
              tooltipBorder: "rgba(255, 255, 255, 0.58)",
            };

            const NIGHT_THEME = {
              text: "#f5f7fb",
              muted: "#eaeaea",
              positive: "#4cff88",
              negative: "#ff6b6b",
              neutral: "#d0d0d0",
              glass: "rgba(20, 24, 38, 0.78)",
              glassBorder: "rgba(255, 255, 255, 0.2)",
              cardShadow: "0 18px 44px rgba(0, 0, 0, 0.34), 0 0 18px rgba(164, 202, 255, 0.08)",
              statBg: "rgba(255, 255, 255, 0.1)",
              statBorder: "rgba(255, 255, 255, 0.17)",
              tooltipBg: "rgba(20, 24, 38, 0.9)",
              tooltipBorder: "rgba(255, 255, 255, 0.24)",
            };

            function loadSceneState() {
              try {
                return JSON.parse(localStorage.getItem(SCENE_STATE_KEY) || "{}");
              } catch {
                return {};
              }
            }

            function saveSceneState(patch) {
              try {
                localStorage.setItem(SCENE_STATE_KEY, JSON.stringify({
                  ...loadSceneState(),
                  ...patch,
                }));
              } catch {
                // Some embedded-browser contexts block localStorage; the app still works without persistence.
              }
            }

            function savedHour(value) {
              const hour = Number(value);
              if (!Number.isFinite(hour)) return 12;
              return Math.min(23, Math.max(0, Math.round(hour)));
            }

            function svgEl(tag, attrs = {}) {
              const el = document.createElementNS(SVG_NS, tag);
              Object.entries(attrs).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                  el.setAttribute(key, String(value));
                }
              });
              return el;
            }

            function formatEnergy(value) {
              const number = Number(value);
              const sign = number > 0 ? "+" : "";
              return `${sign}${number.toFixed(2)} kWh`;
            }

            function formatPlainEnergy(value) {
              return `${Number(value).toFixed(2)} kWh`;
            }

            function buildingId(snapshot) {
              return snapshot.building_id || snapshot.house_id;
            }

            function buildingName(snapshot) {
              return snapshot.display_name || `Building ${buildingId(snapshot)}`;
            }

            function buildingType(snapshot) {
              return snapshot.building_type || (snapshot.has_solar ? "Solar Home" : "Shop");
            }

            function shortShopName(snapshot) {
              const type = buildingType(snapshot);
              if (type === "Supermarket") return "Market";
              if (type === "Mini Market") return "Mini Mart";
              if (type === "Restaurant") return "Eatery";
              if (type === "Hardware Shop" || type === "Hardware") return "Hardware";
              return type;
            }

            function shopColor(snapshot) {
              const colors = {
                Bakery: "#cc6f3f",
                Clinic: "#3178c6",
                Cafe: "#8b5e3c",
                Mechanic: "#59636f",
                Restaurant: "#b43f4c",
                Laundry: "#2a9fb6",
                Pharmacy: "#2e9466",
                Supermarket: "#4f7f38",
                "Hardware Shop": "#a66a27",
                Hardware: "#a66a27",
                "Mini Market": "#25805d",
              };
              return colors[buildingType(snapshot)] || "#2b7a8f";
            }

            function homeVariant(snapshot) {
              const type = buildingType(snapshot);
              if (type === "Luxury House") return "luxury";
              if (type === "Bungalow") return "bungalow";
              if (type === "Townhouse") return "townhouse";
              if (type === "Terrace House") return "terrace";
              if (type === "Corner House") return "corner";
              return "small";
            }

            function shopSize(snapshot) {
              const type = buildingType(snapshot);
              if (type === "Supermarket") return "large";
              if (type === "Mechanic" || type === "Hardware Shop" || type === "Hardware") return "industrial";
              return "small";
            }

            function stableHash(value) {
              return String(value).split("").reduce((hash, char) => {
                return ((hash << 5) - hash + char.charCodeAt(0)) >>> 0;
              }, 2166136261);
            }

            function stableIndex(snapshot, salt, length) {
              return stableHash(`${buildingId(snapshot)}-${buildingType(snapshot)}-${salt}`) % length;
            }

            function stableChoice(snapshot, salt, options) {
              return options[stableIndex(snapshot, salt, options.length)];
            }

            function shadeColor(hex, percent) {
              const clean = hex.replace("#", "");
              const number = parseInt(clean, 16);
              const amount = Math.round(255 * percent);
              const r = Math.max(0, Math.min(255, (number >> 16) + amount));
              const g = Math.max(0, Math.min(255, ((number >> 8) & 255) + amount));
              const b = Math.max(0, Math.min(255, (number & 255) + amount));
              return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
            }

            function solarPanelLevel(snapshot) {
              const capacity = Number(snapshot.max_power || 0);
              if (capacity >= 32) return "large";
              if (capacity >= 23) return "medium";
              return "small";
            }

            function homeVisualProfile(snapshot) {
              const walls = ["#f0c66c", "#f5d2a2", "#d9e6cb", "#cfe3f4", "#f0b8a8", "#e8d7b4"];
              const roofs = ["#a43a32", "#7d3d64", "#315d7b", "#7d5230", "#4d5c66"];
              const wall = stableChoice(snapshot, "home-wall", walls);
              const roof = stableChoice(snapshot, "home-roof", roofs);
              return {
                wall,
                wallSide: shadeColor(wall, -0.12),
                roof,
                roofSide: shadeColor(roof, -0.18),
                roofStroke: shadeColor(roof, -0.28),
              };
            }

            function shopVisualProfile(snapshot) {
              const type = buildingType(snapshot);
              const profile = {
                Bakery: ["#f4c29a", "#dca57d", "#8f493d", "#fff0c9", "rgba(196, 65, 51, 0.78)"],
                Cafe: ["#d6b28f", "#b98e6c", "#5d4535", "#f7e1b5", "rgba(90, 69, 53, 0.74)"],
                Clinic: ["#eef6fb", "#c8dfea", "#3178c6", "#ffffff", "rgba(49, 120, 198, 0.74)"],
                Mechanic: ["#c7ced6", "#aab3bc", "#4a5562", "#d8dde2", "rgba(80, 89, 101, 0.8)"],
                Restaurant: ["#f0b29b", "#d78c78", "#9f3346", "#ffd9a8", "rgba(178, 52, 60, 0.74)"],
                Laundry: ["#c9eef8", "#9ed5e4", "#2a9fb6", "#effcff", "rgba(42, 159, 182, 0.74)"],
                Pharmacy: ["#dff4e7", "#b8dbc5", "#2e9466", "#ffffff", "rgba(46, 148, 102, 0.78)"],
                Supermarket: ["#d9ead2", "#b7d2ad", "#4f7f38", "#f3f8e8", "rgba(78, 127, 56, 0.74)"],
                "Hardware Shop": ["#d8c1a1", "#b89468", "#7f5624", "#e8d2ad", "rgba(110, 82, 47, 0.78)"],
                Hardware: ["#d8c1a1", "#b89468", "#7f5624", "#e8d2ad", "rgba(110, 82, 47, 0.78)"],
                "Mini Market": ["#d7efe3", "#a9d0bc", "#25805d", "#fff3cd", "rgba(37, 128, 93, 0.75)"],
              }[type] || ["#dfe8ef", "#b8c8d3", "#546879", "#fff0c9", "rgba(214, 67, 67, 0.78)"];

              return {
                wall: profile[0],
                side: profile[1],
                roof: profile[2],
                awningBase: profile[3],
                awningStripe: profile[4],
              };
            }

            function buildingStyle(snapshot) {
              if (snapshot.has_solar) {
                const profile = homeVisualProfile(snapshot);
                return [
                  `--wall-color: ${profile.wall}`,
                  `--wall-side: ${profile.wallSide}`,
                  `--roof-color: ${profile.roof}`,
                  `--roof-side: ${profile.roofSide}`,
                  `--roof-stroke: ${profile.roofStroke}`,
                ].join("; ");
              }

              const profile = shopVisualProfile(snapshot);
              return [
                `--shop-color: ${shopColor(snapshot)}`,
                `--shop-wall: ${profile.wall}`,
                `--shop-side: ${profile.side}`,
                `--shop-roof: ${profile.roof}`,
                `--awning-base: ${profile.awningBase}`,
                `--awning-stripe: ${profile.awningStripe}`,
              ].join("; ");
            }

            function periodForHour(hour) {
              if (hour <= 5 || hour >= 19) return "night";
              if (hour < 8) return "dawn";
              if (hour >= 18) return "dusk";
              return "day";
            }

            function getTheme(hour, weather) {
              const nightMode = hour >= 19 || hour <= 5;
              if (nightMode) return NIGHT_THEME;
              if (weather === "Cloudy") {
                return { ...DAY_THEME, glass: "rgba(246, 249, 252, 0.66)" };
              }
              return DAY_THEME;
            }

            function applyTheme(theme) {
              Object.entries({
                "--text": theme.text,
                "--muted": theme.muted,
                "--positive": theme.positive,
                "--negative": theme.negative,
                "--neutral": theme.neutral,
                "--glass": theme.glass,
                "--glass-border": theme.glassBorder,
                "--card-shadow": theme.cardShadow,
                "--stat-bg": theme.statBg,
                "--stat-border": theme.statBorder,
                "--tooltip-bg": theme.tooltipBg,
                "--tooltip-border": theme.tooltipBorder,
              }).forEach(([name, value]) => dashboard.style.setProperty(name, value));
            }

            function hourText(hour) {
              return `${String(hour).padStart(2, "0")}:00`;
            }

            function stageWidth(buildingCount, snapshots = []) {
              const columns = Math.ceil(buildingCount / 2);
              let width = Math.max(
                LAYOUT.baseWidth,
                LAYOUT.sidePadding * 2 + columns * LAYOUT.slotWidth + LAYOUT.clusterGap + LAYOUT.buildingWidth
              );

              if (snapshots.length) {
                const shopColumns = Math.ceil(snapshots.filter((snapshot) => !snapshot.has_solar).length / 2);
                const homeColumns = Math.ceil(snapshots.filter((snapshot) => snapshot.has_solar).length / 2);
                const widestCluster = Math.max(clusterWidth(shopColumns), clusterWidth(homeColumns));
                width = Math.max(
                  width,
                  2 * (LAYOUT.sidePadding + LAYOUT.substationCorridorHalfWidth + widestCluster + 64)
                );
              }

              return width;
            }

            function stageHeight() {
              return LAYOUT.height;
            }

            function stageCenterX(width) {
              return width / 2;
            }

            function clusteredPositions(snapshots, width) {
              const positions = new Array(snapshots.length);
              const shops = [];
              const homes = [];

              snapshots.forEach((snapshot, index) => {
                (snapshot.has_solar ? homes : shops).push({ snapshot, index });
              });

              const shopColumns = Math.ceil(shops.length / 2);
              const homeColumns = Math.ceil(homes.length / 2);
              const shopWidth = clusterWidth(shopColumns);
              const homeWidth = clusterWidth(homeColumns);
              const stationX = stageCenterX(width);
              const corridorLeft = stationX - LAYOUT.substationCorridorHalfWidth;
              const corridorRight = stationX + LAYOUT.substationCorridorHalfWidth;
              const clusterMargin = 56;
              const shopStartX = shopWidth > 0
                ? Math.max(54, corridorLeft - shopWidth - clusterMargin)
                : 0;
              const homeStartX = homeWidth > 0
                ? Math.min(width - homeWidth - 54, corridorRight + clusterMargin)
                : 0;

              assignClusterPositions(shops, shopStartX, positions, "commercial");
              assignClusterPositions(homes, homeStartX, positions, "residential");
              return positions;
            }

            function clusterWidth(columns) {
              if (columns <= 0) return 0;
              return (columns - 1) * LAYOUT.slotWidth + LAYOUT.buildingWidth;
            }

            function assignClusterPositions(items, startX, positions, district) {
              items.forEach((item, groupIndex) => {
                const column = Math.floor(groupIndex / 2);
                const isTop = groupIndex % 2 === 0;
                positions[item.index] = {
                  column,
                  district,
                  isTop,
                  x: startX + column * LAYOUT.slotWidth,
                  y: isTop ? LAYOUT.topRowY : LAYOUT.bottomRowY,
                };
              });
            }

            function connectionLocal(position) {
              const tapX = position.column % 2 === 0 ? 76 : 36;
              return {
                x: tapX,
                y: position.isTop ? 62 : 42,
              };
            }

            function getBuildingConnectionPoint(snapshot, position, variant) {
              const local = connectionLocal(position);
              return {
                x: position.x + local.x,
                y: position.y + local.y,
              };
            }

            function connectionPoint(position, snapshot = null) {
              return getBuildingConnectionPoint(snapshot, position, snapshot ? homeVariant(snapshot) : "default");
            }

            function pylonPosition(position) {
              return {
                x: position.x + LAYOUT.buildingWidth / 2,
                y: LAYOUT.mainGridY,
                cableY: LAYOUT.mainGridY,
              };
            }

            function gridNetwork(positions, width) {
              const pylons = positions
                .map((position, index) => ({ ...pylonPosition(position), index, position }))
                .sort((a, b) => a.x - b.x);
              const stationX = stageCenterX(width);
              const pylonXs = pylons.map((pylon) => pylon.x);
              const pylonMinX = Math.min(...pylonXs);
              const pylonMaxX = Math.max(...pylonXs);

              // The substation tap is treated as a grid node so the vertical
              // feeder always lands on the same bus used by every pylon.
              return {
                pylons,
                stationX,
                pylonMinX,
                pylonMaxX,
                minX: Math.min(pylonMinX, stationX),
                maxX: Math.max(pylonMaxX, stationX),
              };
            }

            function mainGridSegmentTo(x) {
              return `L ${x} ${LAYOUT.mainGridY}`;
            }

            function pylonToBuildingCommands(position) {
              const connection = connectionPoint(position);
              const pylon = pylonPosition(position);
              const bow = position.column % 2 === 0 ? 20 : -20;

              if (position.isTop) {
                return `C ${pylon.x + bow} ${pylon.y - 76}, ${connection.x + bow} ${connection.y + 48}, ${connection.x} ${connection.y}`;
              }

              return `C ${pylon.x + bow} ${pylon.y + 82}, ${connection.x + bow} ${connection.y - 58}, ${connection.x} ${connection.y}`;
            }

            function buildingToPylonCommands(position) {
              const connection = connectionPoint(position);
              const pylon = pylonPosition(position);
              const bow = position.column % 2 === 0 ? 20 : -20;

              if (position.isTop) {
                return `C ${connection.x + bow} ${connection.y + 48}, ${pylon.x + bow} ${pylon.y - 76}, ${pylon.x} ${pylon.y}`;
              }

              return `C ${connection.x + bow} ${connection.y - 58}, ${pylon.x + bow} ${pylon.y + 82}, ${pylon.x} ${pylon.y}`;
            }

            function pylonToBuildingPath(position) {
              const pylon = pylonPosition(position);
              return `M ${pylon.x} ${pylon.y} ${pylonToBuildingCommands(position)}`;
            }

            function buildingToPylonPath(position) {
              const connection = connectionPoint(position);
              return `M ${connection.x} ${connection.y} ${buildingToPylonCommands(position)}`;
            }

            function substationAttachY() {
              return LAYOUT.substationY + 112;
            }

            function currentTotals() {
              return DATA.hourly_totals[String(activeHour)] || {};
            }

            function currentGridNet() {
              const totals = currentTotals();
              const net = Number(totals.net_energy);
              if (Number.isFinite(net)) return net;
              return Number(totals.generation || 0) - Number(totals.consumption || 0);
            }

            function netTone(value) {
              if (value > 0.005) return "positive";
              if (value < -0.005) return "negative";
              return "neutral";
            }

            function gridState(value) {
              if (value > 0.005) return "surplus";
              if (value < -0.005) return "deficit";
              return "balanced";
            }

            function flowOffsets() {
              if (QUALITY_MODE === "Performance") return [];
              if (QUALITY_MODE === "Balanced") return [0, 0.32, 0.64];
              return [0, 0.18, 0.36, 0.54, 0.72, 0.9];
            }

            function clamp(value, minimum, maximum) {
              return Math.min(maximum, Math.max(minimum, value));
            }

            function maxSellerExport(entries) {
              return Math.max(
                1,
                ...entries
                  .filter((entry) => entry.snapshot.status === "SELLER")
                  .map((entry) => Math.max(0, Number(entry.snapshot.net_energy || 0)))
              );
            }

            function maxGridDeficit() {
              return Math.max(
                1,
                ...Object.values(DATA.hourly_totals || {}).map((totals) =>
                  Math.max(0, -Number(totals.net_energy || 0))
                )
              );
            }

            function durationForExport(exportAmount, reference) {
              const ratio = clamp(Math.max(0, Number(exportAmount || 0)) / Math.max(1, reference), 0, 1);
              const speedFactor = Math.pow(ratio, 0.6);
              const minDuration = 0.35;
              const maxDuration = 3.5;
              const duration = maxDuration - speedFactor * (maxDuration - minDuration);
              return `${clamp(duration, minDuration, maxDuration).toFixed(2)}s`;
            }

            function slowerDuration(duration, factor = 1.12) {
              const seconds = Number(String(duration).replace("s", ""));
              return `${clamp(seconds * factor, 0.35, 3.5).toFixed(2)}s`;
            }

            function substationToBuildingPath(position, network) {
              const pylon = pylonPosition(position);

              return [
                `M ${network.stationX} ${substationAttachY()}`,
                `L ${network.stationX} ${LAYOUT.mainGridY}`,
                mainGridSegmentTo(pylon.x),
                pylonToBuildingCommands(position),
              ].join(" ");
            }

            function substationToBuildingSegments(position, network, duration) {
              const pylon = pylonPosition(position);

              return [
                {
                  kind: "GREEN",
                  d: `M ${network.stationX} ${substationAttachY()} L ${network.stationX} ${LAYOUT.mainGridY} L ${pylon.x} ${LAYOUT.mainGridY}`,
                  duration,
                },
              ];
            }

            function buildConnectedFlowPath(sourcePosition, targetPosition) {
              const sourcePylon = pylonPosition(sourcePosition);
              const targetPylon = pylonPosition(targetPosition);

              return {
                sourcePylon,
                targetPylon,
                toTargetPylon: `${buildingToPylonPath(sourcePosition)} ${mainGridSegmentTo(sourcePylon.x)} ${mainGridSegmentTo(targetPylon.x)}`,
                toTargetBuilding: pylonToBuildingPath(targetPosition),
              };
            }

            function localShareSegments(sourcePosition, targetPosition) {
              const path = buildConnectedFlowPath(sourcePosition, targetPosition);
              return [
                {
                  kind: "GREEN",
                  d: path.toTargetPylon,
                },
                {
                  kind: "YELLOW",
                  d: path.toTargetBuilding,
                },
              ];
            }

            function localDeficitContributionSegments(sourcePosition, targetPosition, duration) {
              const path = buildConnectedFlowPath(sourcePosition, targetPosition);
              return [{
                kind: "GREEN",
                d: path.toTargetPylon,
                duration,
              }];
            }

            function sellerToGridPath(position, network) {
              const pylon = pylonPosition(position);
              return `${buildingToPylonPath(position)} ${mainGridSegmentTo(pylon.x)} ${mainGridSegmentTo(network.stationX)}`;
            }

            function deficitSellerDestinationX(position, buyers, network) {
              const pylon = pylonPosition(position);
              const buyerPylons = buyers
                .map((buyer) => pylonPosition(buyer.position).x)
                .sort((a, b) => a - b);

              if (!buyerPylons.length) return network.stationX;

              // In the clustered layout, sellers usually sit on the right and buyers
              // sit on the left. Send deficit-time seller export onto the shared bus
              // toward the buyer cluster without rendering a final buyer branch.
              if (pylon.x >= network.stationX) return buyerPylons[0];
              return buyerPylons[buyerPylons.length - 1];
            }

            function deficitSellerToGridPath(position, buyers, network) {
              const pylon = pylonPosition(position);
              const destinationX = deficitSellerDestinationX(position, buyers, network);
              return `${buildingToPylonPath(position)} ${mainGridSegmentTo(pylon.x)} ${mainGridSegmentTo(destinationX)}`;
            }

            function renderScene() {
              const snapshots = DATA.hours[String(activeHour)] || [];
              const width = stageWidth(snapshots.length, snapshots);
              const height = stageHeight();
              const positions = clusteredPositions(snapshots, width);
              const svg = svgEl("svg", {
                class: "grid-svg",
                viewBox: `0 0 ${width} ${height}`,
                role: "img",
                "aria-label": "Isometric smart-grid neighborhood with power cables",
              });

              svg.addEventListener("mousemove", (event) => {
                if (!event.target.classList || !event.target.classList.contains("hover-area")) {
                  hideHoverState();
                }
              });
              svg.addEventListener("pointerleave", hideHoverState);
              svg.addEventListener("mouseleave", hideHoverState);

              currentSvg = svg;
              renderGround(svg, width, height, positions);
              renderPowerGrid(svg, snapshots, positions, width);
              renderBuildings(svg, snapshots, positions);
              renderTooltipLayer(svg);

              sceneStage.innerHTML = "";
              sceneStage.appendChild(svg);
              hideHoverState();
            }

            function renderGround(svg, width, height, positions) {
              const groundY = 190;
              const buildingXs = positions.map((position) => position.x);
              const roadStart = Math.max(54, Math.min(...buildingXs) - 78);
              const roadEnd = Math.min(width - 54, Math.max(...buildingXs) + LAYOUT.buildingWidth + 78);
              const roadTop = LAYOUT.roadY - LAYOUT.roadHeight / 2;
              const roadBottom = LAYOUT.roadY + LAYOUT.roadHeight / 2;

              svg.appendChild(svgEl("rect", {
                class: "ground",
                x: 0,
                y: groundY,
                width,
                height: height - groundY,
              }));
              svg.appendChild(svgEl("rect", {
                class: "ground-dark",
                x: 0,
                y: LAYOUT.roadY + 40,
                width,
                height: height - groundY - 96,
              }));

              svg.appendChild(svgEl("rect", {
                class: "sidewalk",
                x: roadStart,
                y: roadTop - 30,
                width: roadEnd - roadStart,
                height: 18,
              }));
              svg.appendChild(svgEl("rect", {
                class: "sidewalk",
                x: roadStart,
                y: roadBottom + 12,
                width: roadEnd - roadStart,
                height: 18,
              }));
              svg.appendChild(svgEl("rect", {
                class: "road-side",
                x: roadStart - 8,
                y: roadTop - 8,
                width: roadEnd - roadStart + 16,
                height: LAYOUT.roadHeight + 16,
                rx: 5,
              }));
              svg.appendChild(svgEl("rect", {
                class: "road",
                x: roadStart,
                y: roadTop,
                width: roadEnd - roadStart,
                height: LAYOUT.roadHeight,
                rx: 5,
              }));
              svg.appendChild(svgEl("line", {
                class: "lane-line",
                x1: roadStart + 30,
                y1: LAYOUT.roadY,
                x2: roadEnd - 30,
                y2: LAYOUT.roadY,
              }));

              positions.forEach((position) => {
                const centerX = position.x + LAYOUT.buildingWidth / 2;
                const drivewayTop = position.isTop
                  ? position.y + LAYOUT.buildingHeight - 10
                  : roadBottom;
                const drivewayHeight = position.isTop
                  ? roadTop - drivewayTop
                  : position.y + 6 - roadBottom;

                if (drivewayHeight > 0) {
                  svg.appendChild(svgEl("rect", {
                    class: "driveway",
                    x: centerX - 18,
                    y: drivewayTop,
                    width: 36,
                    height: drivewayHeight,
                    rx: 4,
                  }));
                }
              });

              svg.appendChild(svgEl("rect", {
                class: "wet-gloss",
                x: roadStart + 26,
                y: roadTop + 12,
                width: roadEnd - roadStart - 52,
                height: LAYOUT.roadHeight - 24,
                rx: 20,
              }));
              svg.appendChild(svgEl("ellipse", {
                class: "rain-reflection",
                cx: (roadStart + roadEnd) / 2,
                cy: LAYOUT.roadY + 16,
                rx: Math.max(80, (roadEnd - roadStart) / 3.2),
                ry: 16,
              }));

              renderStreetlights(svg, roadStart, roadEnd, roadTop, roadBottom);
              renderTrees(svg, roadStart, roadEnd);

              [roadStart + 120, roadEnd - 120].forEach((x) => {
                [LAYOUT.topRowY + 38, LAYOUT.bottomRowY + 58].forEach((y) => {
                  if (x > 0 && x < width) {
                    svg.appendChild(svgEl("ellipse", {
                      class: "grass-patch",
                      cx: x,
                      cy: y,
                      rx: 80,
                      ry: 24,
                    }));
                  }
                });
              });
            }

            function renderStreetlights(svg, roadStart, roadEnd, roadTop, roadBottom) {
              const count = Math.min(6, Math.max(2, Math.floor((roadEnd - roadStart) / 260)));
              const gap = (roadEnd - roadStart) / (count + 1);
              for (let index = 1; index <= count; index += 1) {
                const x = roadStart + gap * index;
                const y = index % 2 === 0 ? roadTop - 18 : roadBottom + 46;
                const group = svgEl("g", { class: "streetlight" });
                group.appendChild(svgEl("line", {
                  class: "streetlight-pole",
                  x1: x,
                  y1: y,
                  x2: x,
                  y2: y - 46,
                }));
                group.appendChild(svgEl("ellipse", {
                  class: "streetlight-glow",
                  cx: x,
                  cy: y - 52,
                  rx: 48,
                  ry: 30,
                }));
                group.appendChild(svgEl("circle", {
                  class: "streetlight-lamp",
                  cx: x,
                  cy: y - 50,
                  r: 8,
                }));
                svg.appendChild(group);
              }
            }

            function renderTrees(svg, roadStart, roadEnd) {
              [
                [roadStart + 62, LAYOUT.topRowY + 126],
                [roadStart + 186, LAYOUT.bottomRowY + 136],
                [roadEnd - 186, LAYOUT.topRowY + 128],
                [roadEnd - 62, LAYOUT.bottomRowY + 136],
              ].forEach(([x, y], index) => {
                const tree = svgEl("g", { class: "tree" });
                tree.appendChild(svgEl("rect", {
                  class: "tree-trunk",
                  x: x - 5,
                  y: y - 22,
                  width: 10,
                  height: 32,
                  rx: 3,
                }));
                tree.appendChild(svgEl("ellipse", {
                  class: "tree-canopy",
                  cx: x,
                  cy: y - 28,
                  rx: index % 2 === 0 ? 24 : 21,
                  ry: index % 2 === 0 ? 25 : 22,
                }));
                svg.appendChild(tree);
              });
            }

            function renderPowerGrid(svg, snapshots, positions, width) {
              const cableLayer = svgEl("g", { class: "cable-layer" });
              const flowLayer = svgEl("g", { class: "flow-layer" });
              const network = gridNetwork(positions, width);

              cableLayer.appendChild(svgEl("line", {
                class: "grid-spine",
                x1: network.minX,
                y1: LAYOUT.mainGridY,
                x2: network.maxX,
                y2: LAYOUT.mainGridY,
              }));
              cableLayer.appendChild(svgEl("line", {
                class: "grid-spine-highlight",
                x1: network.minX + 3,
                y1: LAYOUT.mainGridY - 2,
                x2: network.maxX - 3,
                y2: LAYOUT.mainGridY - 2,
              }));
              cableLayer.appendChild(svgEl("line", {
                class: "grid-spine",
                x1: network.stationX,
                y1: substationAttachY(),
                x2: network.stationX,
                y2: LAYOUT.mainGridY,
              }));
              cableLayer.appendChild(svgEl("line", {
                class: "grid-spine-highlight",
                x1: network.stationX - 2,
                y1: substationAttachY() + 3,
                x2: network.stationX - 2,
                y2: LAYOUT.mainGridY - 4,
              }));

              snapshots.forEach((snapshot, index) => {
                const position = positions[index];
                const branchPath = pylonToBuildingPath(position);

                cableLayer.appendChild(svgEl("path", { class: "cable-soft", d: branchPath }));
                cableLayer.appendChild(svgEl("path", { class: "cable", d: branchPath }));
                renderPylon(cableLayer, position);
              });

              renderDebugGridNodes(cableLayer, network);
              renderFlowSet(flowLayer, snapshots, positions, network);

              svg.appendChild(cableLayer);
              svg.appendChild(flowLayer);
              renderSubstation(svg, width);
            }

            function renderDebugGridNodes(layer, network) {
              if (!DEBUG_GRID_NODES) return;
              [
                ...network.pylons,
                { x: network.stationX, y: LAYOUT.mainGridY },
              ].forEach((node) => {
                layer.appendChild(svgEl("circle", {
                  class: "debug-grid-node",
                  cx: node.x,
                  cy: node.y,
                  r: 9,
                }));
              });
            }

            function renderPylon(layer, position) {
              const pylon = pylonPosition(position);
              const pole = svgEl("g", { class: "utility-pole-group" });

              pole.appendChild(svgEl("ellipse", {
                class: "pole-shadow",
                cx: pylon.x + 6,
                cy: pylon.cableY + 68,
                rx: 18,
                ry: 6,
              }));
              pole.appendChild(svgEl("rect", {
                class: "utility-pole",
                x: pylon.x - 5,
                y: pylon.cableY - 12,
                width: 10,
                height: 82,
                rx: 2,
              }));
              pole.appendChild(svgEl("line", {
                class: "pole-arm",
                x1: pylon.x - 28,
                y1: pylon.cableY,
                x2: pylon.x + 28,
                y2: pylon.cableY,
              }));
              [-20, 20].forEach((offset) => {
                pole.appendChild(svgEl("circle", {
                  class: "pole-insulator",
                  cx: pylon.x + offset,
                  cy: pylon.cableY,
                  r: 4.5,
                }));
              });
              layer.appendChild(pole);
              layer.appendChild(svgEl("circle", { class: "junction-node", cx: pylon.x, cy: pylon.cableY, r: 6 }));
            }

            function renderFlowSet(layer, snapshots, positions, network) {
              const entries = snapshots.map((snapshot, index) => ({
                snapshot,
                position: positions[index],
                id: buildingId(snapshot),
              }));
              const sellers = entries.filter((entry) => entry.snapshot.status === "SELLER");
              const buyers = entries.filter((entry) => entry.snapshot.status === "BUYER");
              const exportReference = maxSellerExport(entries);
              const net = currentGridNet();
              const aggregateExport = sellers.reduce(
                (sum, seller) => sum + Math.max(0, Number(seller.snapshot.net_energy || 0)),
                0
              );
              const aggregateDuration = durationForExport(
                aggregateExport,
                Math.max(1, exportReference * Math.max(1, sellers.length))
              );
              const deficitDuration = durationForExport(Math.max(0, -net), maxGridDeficit());
              const buyerBranchDuration = net > 0.005
                ? slowerDuration(aggregateDuration)
                : slowerDuration(deficitDuration);

              sellers.forEach((source) => {
                buyers.forEach((target) => {
                  const sellerDuration = durationForExport(source.snapshot.net_energy, exportReference);
                  renderFlow(layer, localShareSegments(source.position, target.position), {
                    "data-flow-role": "local-share",
                    "data-source-id": source.id,
                    "data-target-id": target.id,
                    "data-duration": sellerDuration,
                  });
                  renderFlow(layer, localDeficitContributionSegments(source.position, target.position, sellerDuration), {
                    "data-flow-role": "deficit-local-contribution",
                    "data-source-id": source.id,
                    "data-target-id": target.id,
                    "data-duration": sellerDuration,
                  });
                });
              });

              buyers.forEach((buyer) => {
                renderFlow(layer, substationToBuildingSegments(buyer.position, network, deficitDuration), {
                  "data-flow-role": "deficit-import",
                  "data-target-id": buyer.id,
                  "data-duration": deficitDuration,
                });
                renderFlow(layer, [{
                  kind: "GREEN",
                  d: `M ${network.stationX} ${LAYOUT.mainGridY} ${mainGridSegmentTo(pylonPosition(buyer.position).x)}`,
                  duration: aggregateDuration,
                }], {
                  "data-flow-role": "grid-to-buyer",
                  "data-target-id": buyer.id,
                  "data-duration": aggregateDuration,
                });
                renderFlow(layer, [{
                  kind: "YELLOW",
                  d: pylonToBuildingPath(buyer.position),
                  duration: buyerBranchDuration,
                }], {
                  "data-flow-role": "buyer-delivery",
                  "data-target-id": buyer.id,
                  "data-duration": buyerBranchDuration,
                });
              });

              sellers.forEach((seller) => {
                const duration = durationForExport(seller.snapshot.net_energy, exportReference);
                renderFlow(layer, [{ kind: "GREEN", d: sellerToGridPath(seller.position, network), duration }], {
                  "data-flow-role": "seller-export",
                  "data-source-id": seller.id,
                  "data-duration": duration,
                });
                renderFlow(layer, [{ kind: "GREEN", d: deficitSellerToGridPath(seller.position, buyers, network), duration }], {
                  "data-flow-role": "deficit-seller-export",
                  "data-source-id": seller.id,
                  "data-duration": duration,
                });
              });
            }

            function renderFlow(layer, segments, attrs = {}) {
              const baseDuration = attrs["data-duration"] || "1.20s";
              const flow = svgEl("g", {
                class: "flow",
                ...attrs,
              });

              segments.forEach((segment, segmentIndex) => {
                const duration = segment.duration || baseDuration;
                const pathId = `flowPath-${layer.childNodes.length}-${segmentIndex}`;
                flow.appendChild(svgEl("path", { id: pathId, d: segment.d, fill: "none", stroke: "none" }));
                flow.appendChild(svgEl("path", {
                  class: `active-flow-line ${segment.kind}`,
                  d: segment.d,
                  style: `animation-duration: ${duration};`,
                }));

                flowOffsets().forEach((offset, index) => {
                  const dot = svgEl("circle", {
                    class: `flow-dot ${segment.kind}`,
                    r: index % 2 === 0 ? 8.5 : 5.8,
                  });
                  const motion = svgEl("animateMotion", {
                    dur: duration,
                    repeatCount: "indefinite",
                    begin: `${offset}s`,
                  });
                  motion.appendChild(svgEl("mpath", { href: `#${pathId}` }));
                  dot.appendChild(motion);
                  flow.appendChild(dot);
                });
              });

              layer.appendChild(flow);
            }

            function renderSubstation(svg, width) {
              const x = stageCenterX(width) - 58;
              const y = LAYOUT.substationY;
              const station = svgEl("g", {
                class: "substation",
                tabindex: "0",
                role: "button",
                "aria-label": "Substation grid summary",
                transform: `translate(${x} ${y})`,
              });

              station.appendChild(svgEl("ellipse", {
                class: "substation-pad",
                cx: 58,
                cy: 92,
                rx: 78,
                ry: 22,
              }));
              station.appendChild(svgEl("polygon", {
                class: "substation-side",
                points: "22,38 116,38 132,54 38,54",
              }));
              station.appendChild(svgEl("rect", {
                class: "substation-base",
                x: 18,
                y: 44,
                width: 100,
                height: 68,
                rx: 8,
              }));
              station.appendChild(svgEl("polygon", {
                class: "substation-top",
                points: "18,44 38,28 118,28 118,44",
              }));
              station.appendChild(svgEl("rect", {
                class: "transformer-box",
                x: 0,
                y: 82,
                width: 30,
                height: 36,
                rx: 4,
              }));
              station.appendChild(svgEl("rect", {
                class: "transformer-box",
                x: 92,
                y: 82,
                width: 30,
                height: 36,
                rx: 4,
              }));
              station.appendChild(svgEl("polygon", {
                class: "substation-bolt",
                points: "61,50 75,50 66,70 78,70 53,98 60,75 49,75",
              }));
              station.appendChild(svgEl("rect", {
                class: "substation-label-bg",
                x: 26,
                y: 34,
                width: 84,
                height: 20,
                rx: 5,
              }));
              const label = svgEl("text", { class: "substation-label", x: 68, y: 44 });
              label.textContent = "SUBSTATION";
              station.appendChild(label);

              const hoverArea = svgEl("rect", {
                class: "hover-area",
                x: -16,
                y: 18,
                width: 156,
                height: 116,
                rx: 8,
              });
              const onEnter = () => showSubstationHover(width);
              const onLeave = () => hideHoverState();
              ["pointerenter", "mouseenter", "mouseover", "mousemove"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, onEnter);
              });
              ["pointerleave", "mouseleave", "mouseout"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, onLeave);
              });
              ["pointerdown", "click"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, (event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  onEnter();
                });
              });
              station.addEventListener("focus", onEnter);
              station.addEventListener("blur", onLeave);
              station.appendChild(hoverArea);

              svg.appendChild(station);
            }

            function renderBuildings(svg, snapshots, positions) {
              const layer = svgEl("g", { class: "building-layer" });
              snapshots.forEach((snapshot, index) => {
                layer.appendChild(renderBuilding(snapshot, positions[index]));
              });
              svg.appendChild(layer);
            }

            function renderBuilding(snapshot, position) {
              const idValue = buildingId(snapshot);
              const group = svgEl("g", {
                class: `building-group ${snapshot.has_solar ? "residential" : "commercial"}`,
                tabindex: "0",
                transform: `translate(${position.x} ${position.y})`,
                "aria-label": buildingName(snapshot),
                "data-building-id": idValue,
                "data-variant": snapshot.has_solar ? homeVariant(snapshot) : "",
                "data-size": snapshot.has_solar ? "" : shopSize(snapshot),
                style: buildingStyle(snapshot),
              });

              group.appendChild(svgEl("ellipse", {
                class: "building-shadow",
                cx: 56,
                cy: 126,
                rx: 64,
                ry: 14,
              }));

              if (snapshot.has_solar) {
                renderSolarHome(group, snapshot);
              } else {
                renderShopLot(group, snapshot);
              }

              const connection = connectionLocal(position);
              group.appendChild(svgEl("circle", {
                class: "connection",
                cx: connection.x,
                cy: connection.y,
                r: 5.5,
              }));
              bindBuildingHover(group, snapshot, position);
              return group;
            }

            function renderSolarHome(group, snapshot) {
              const variant = homeVariant(snapshot);
              if (variant === "luxury") {
                renderLargeHouse(group, snapshot);
              } else if (variant === "bungalow" || variant === "corner") {
                renderWideHouse(group, snapshot, variant);
              } else if (variant === "townhouse") {
                renderTallResidential(group, snapshot);
              } else {
                renderSmallHouse(group, snapshot, variant);
              }
            }

            function renderSmallHouse(group, snapshot, variant) {
              group.appendChild(svgEl("polygon", { class: "home-side", points: "84,52 106,41 106,105 84,116" }));
              group.appendChild(svgEl("rect", { class: "home-front", x: 18, y: 52, width: 66, height: 64 }));
              group.appendChild(svgEl("polygon", { class: "home-roof-main", points: "8,52 52,14 96,52 84,62 52,34 18,62" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-side", points: "52,14 106,41 96,52" }));
              group.appendChild(svgEl("path", { class: "wet-roof", d: "M 8 52 L 52 14 L 96 52 L 84 62 L 52 34 L 18 62 Z" }));
              if (variant === "terrace") {
                group.appendChild(svgEl("rect", { class: "home-extension", x: 8, y: 68, width: 18, height: 48 }));
              }
              renderSolarPanelArray(group, snapshot, variant);
              renderHomeWindows(group, [[27, 68], [60, 68]]);
              renderHomeDoor(group, 43, 86);
            }

            function renderWideHouse(group, snapshot, variant) {
              if (variant === "corner") {
                group.appendChild(svgEl("rect", { class: "yard", x: 76, y: 82, width: 30, height: 36, rx: 5 }));
                [86, 96, 91].forEach((x, index) => {
                  group.appendChild(svgEl("circle", { class: "garden-dot", cx: x, cy: 93 + index * 8, r: 2.2 }));
                });
              }
              group.appendChild(svgEl("polygon", { class: "home-side", points: "92,58 108,48 108,108 92,118" }));
              group.appendChild(svgEl("rect", { class: "home-front", x: 10, y: 58, width: 82, height: 60 }));
              group.appendChild(svgEl("polygon", { class: "home-roof-main", points: "0,58 52,28 104,58 92,68 52,45 10,68" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-side", points: "52,28 108,48 104,58" }));
              group.appendChild(svgEl("path", { class: "wet-roof", d: "M 0 58 L 52 28 L 104 58 L 92 68 L 52 45 L 10 68 Z" }));
              renderSolarPanelArray(group, snapshot, variant);
              renderHomeWindows(group, [[21, 75], [50, 75], [72, 75]]);
              renderHomeDoor(group, 39, 90);
            }

            function renderLargeHouse(group, snapshot) {
              group.appendChild(svgEl("rect", { class: "drive-pad", x: 14, y: 112, width: 66, height: 14, rx: 4 }));
              group.appendChild(svgEl("polygon", { class: "home-side", points: "86,50 108,40 108,108 86,120" }));
              group.appendChild(svgEl("rect", { class: "home-front", x: 14, y: 50, width: 72, height: 70 }));
              group.appendChild(svgEl("polygon", { class: "home-extension", points: "72,78 104,66 104,114 72,126" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-main", points: "4,50 46,14 92,50 82,62 46,34 14,62" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-side", points: "46,14 108,40 92,50" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-main", points: "62,78 88,56 108,66 74,88" }));
              group.appendChild(svgEl("path", { class: "roof-trim", d: "M 18 62 L 46 34 L 82 62" }));
              group.appendChild(svgEl("path", { class: "wet-roof", d: "M 4 50 L 46 14 L 92 50 L 82 62 L 46 34 L 14 62 Z" }));
              group.appendChild(svgEl("rect", { class: "porch", x: 34, y: 94, width: 38, height: 17, rx: 3 }));
              renderSolarPanelArray(group, snapshot, "luxury");
              renderHomeWindows(group, [[25, 66], [59, 66], [83, 88]]);
              renderHomeDoor(group, 43, 88);
            }

            function renderTallResidential(group, snapshot) {
              group.appendChild(svgEl("polygon", { class: "home-side", points: "78,36 100,48 100,118 78,128" }));
              group.appendChild(svgEl("rect", { class: "home-front", x: 30, y: 36, width: 48, height: 92 }));
              group.appendChild(svgEl("polygon", { class: "home-roof-main", points: "24,36 54,8 88,36 78,48 54,25 30,48" }));
              group.appendChild(svgEl("polygon", { class: "home-roof-side", points: "54,8 100,48 88,36" }));
              group.appendChild(svgEl("path", { class: "wet-roof", d: "M 24 36 L 54 8 L 88 36 L 78 48 L 54 25 L 30 48 Z" }));
              renderSolarPanelArray(group, snapshot, "townhouse");
              renderHomeWindows(group, [[40, 52], [59, 52], [40, 77], [59, 77]]);
              renderHomeDoor(group, 49, 100);
            }

            function renderHomeWindows(group, positions) {
              positions.forEach(([x, y]) => {
                group.appendChild(svgEl("rect", { class: "window", x, y, width: 14, height: 14 }));
              });
            }

            function renderHomeDoor(group, x, y) {
              group.appendChild(svgEl("rect", { class: "door", x, y, width: 20, height: 30 }));
              group.appendChild(svgEl("circle", { class: "door-knob", cx: x + 15, cy: y + 15, r: 2 }));
            }

            function renderSolarPanelArray(group, snapshot, variant) {
              const level = solarPanelLevel(snapshot);
              const panels = solarPanelShapes(variant, level);
              panels.forEach((points, index) => {
                group.appendChild(svgEl("polygon", {
                  class: `solar-panel ${level}`,
                  points,
                }));
                renderSolarPanelGrid(group, points, index);
              });
            }

            function solarPanelShapes(variant, level) {
              const shapes = {
                townhouse: {
                  small: ["42,20 62,23 57,33 37,30"],
                  medium: ["39,19 66,23 60,35 33,31"],
                  large: ["36,18 70,23 64,36 30,31"],
                },
                bungalow: {
                  small: ["35,42 67,44 63,55 31,53"],
                  medium: ["28,40 78,44 72,57 22,53"],
                  large: ["18,39 88,45 82,59 12,53"],
                },
                corner: {
                  small: ["35,42 67,44 63,55 31,53"],
                  medium: ["28,40 78,44 72,57 22,53"],
                  large: ["18,39 88,45 82,59 12,53"],
                },
                luxury: {
                  small: ["31,30 63,33 58,45 26,42"],
                  medium: ["26,29 67,33 61,47 20,43"],
                  large: ["22,28 69,33 63,48 16,43", "69,68 94,61 90,72 65,79"],
                },
                terrace: {
                  small: ["34,31 67,34 60,48 27,45"],
                  medium: ["30,30 72,34 64,50 22,46"],
                  large: ["25,29 76,34 68,51 18,46"],
                },
                small: {
                  small: ["34,31 67,34 60,48 27,45"],
                  medium: ["30,30 72,34 64,50 22,46"],
                  large: ["25,29 76,34 68,51 18,46"],
                },
              };

              return shapes[variant]?.[level] || shapes.small[level];
            }

            function renderSolarPanelGrid(group, points, index) {
              const values = points.split(/[ ,]+/).map(Number);
              const xs = values.filter((_, i) => i % 2 === 0);
              const ys = values.filter((_, i) => i % 2 === 1);
              const minX = Math.min(...xs);
              const maxX = Math.max(...xs);
              const minY = Math.min(...ys);
              const maxY = Math.max(...ys);

              [0.28, 0.52, 0.74].forEach((ratio) => {
                const x = minX + (maxX - minX) * ratio;
                group.appendChild(svgEl("path", {
                  class: "solar-line",
                  d: `M ${x} ${minY + 1} L ${x - 5} ${maxY - 1}`,
                }));
              });
              group.appendChild(svgEl("path", {
                class: "solar-line",
                d: `M ${minX + 4} ${(minY + maxY) / 2} L ${maxX - 4} ${(minY + maxY) / 2 + index}`,
              }));
            }

            function renderShopLot(group, snapshot) {
              const size = shopSize(snapshot);
              const isLarge = size === "large";
              const isIndustrial = size === "industrial";
              const frontX = isLarge ? 8 : isIndustrial ? 10 : 14;
              const frontWidth = isLarge ? 86 : isIndustrial ? 84 : 74;
              const signX = isLarge ? 16 : isIndustrial ? 18 : 20;
              const signWidth = isLarge ? 72 : isIndustrial ? 68 : 62;
              const roofPoints = isLarge
                ? "8,40 30,22 94,22 110,44 94,44 94,40"
                : isIndustrial
                  ? "10,40 28,26 94,26 110,44 94,44 94,40"
                  : "14,40 34,24 88,24 108,44 88,44 88,40";
              group.appendChild(svgEl("polygon", {
                class: "shop-side",
                points: isLarge || isIndustrial ? "94,34 110,44 110,112 94,122" : "88,34 108,44 108,112 88,122",
              }));
              group.appendChild(svgEl("rect", {
                class: "shop-front",
                x: frontX,
                y: 40,
                width: frontWidth,
                height: 82,
                rx: 2,
              }));
              group.appendChild(svgEl("polygon", {
                class: "shop-top",
                points: roofPoints,
              }));
              group.appendChild(svgEl("polygon", { class: "wet-roof", points: roofPoints }));
              if (buildingType(snapshot) === "Bakery") {
                group.appendChild(svgEl("rect", { class: "bakery-chimney", x: 78, y: 16, width: 12, height: 26, rx: 2 }));
                group.appendChild(svgEl("ellipse", { class: "bakery-smoke", cx: 84, cy: 10, rx: 6, ry: 4 }));
                group.appendChild(svgEl("ellipse", { class: "bakery-smoke two", cx: 91, cy: 2, rx: 4, ry: 3 }));
              }
              group.appendChild(svgEl("rect", {
                class: "shop-sign",
                x: signX,
                y: 46,
                width: signWidth,
                height: 19,
                rx: 2,
              }));
              const label = svgEl("text", {
                class: "shop-label",
                x: signX + signWidth / 2,
                y: 55,
                textLength: signWidth - 7,
                lengthAdjust: "spacingAndGlyphs",
              });
              label.textContent = shortShopName(snapshot);
              group.appendChild(label);
              renderShopIcon(group, snapshot, signX + 9, 55);
              group.appendChild(svgEl("rect", {
                class: "shop-awning",
                x: frontX + 4,
                y: 68,
                width: frontWidth - 8,
                height: 12,
              }));
              [frontX + 6, frontX + 22, frontX + 38, frontX + 54, frontX + 70].forEach((x) => {
                if (x + 8 > frontX + frontWidth - 4) return;
                group.appendChild(svgEl("rect", {
                  class: "shop-awning-stripe",
                  x,
                  y: 68,
                  width: 8,
                  height: 12,
                }));
              });
              if (buildingType(snapshot) === "Mechanic") {
                group.appendChild(svgEl("rect", { class: "garage-door", x: 22, y: 84, width: 60, height: 38, rx: 2 }));
                [92, 101, 110].forEach((y) => {
                  group.appendChild(svgEl("line", { class: "garage-line", x1: 26, y1: y, x2: 78, y2: y }));
                });
                group.appendChild(svgEl("circle", { class: "tire-icon", cx: 89, cy: 105, r: 8 }));
                group.appendChild(svgEl("circle", { class: "shop-icon", cx: 89, cy: 105, r: 3 }));
              } else if (buildingType(snapshot) === "Laundry") {
                group.appendChild(svgEl("rect", { class: "shop-window", x: frontX + 7, y: 88, width: 22, height: 25 }));
                group.appendChild(svgEl("circle", { class: "machine-door", cx: frontX + 18, cy: 101, r: 8 }));
                group.appendChild(svgEl("rect", { class: "shop-door", x: frontX + frontWidth - 28, y: 84, width: 18, height: 38 }));
              } else if (buildingType(snapshot) === "Cafe") {
                group.appendChild(svgEl("rect", { class: "shop-window", x: frontX + 7, y: 88, width: 19, height: 21 }));
                group.appendChild(svgEl("rect", { class: "shop-door", x: frontX + frontWidth - 30, y: 84, width: 18, height: 38 }));
                renderCafeTable(group, frontX + 45, 112);
              } else if (buildingType(snapshot) === "Hardware Shop" || buildingType(snapshot) === "Hardware") {
                group.appendChild(svgEl("rect", { class: "garage-door", x: 19, y: 86, width: 38, height: 36, rx: 2 }));
                group.appendChild(svgEl("rect", { class: "shop-window", x: 65, y: 89, width: 22, height: 20 }));
                group.appendChild(svgEl("path", { class: "tool-detail", d: "M 25 96 L 48 96 M 25 105 L 48 105 M 71 98 L 82 90 M 73 92 L 82 101" }));
              } else {
                group.appendChild(svgEl("rect", { class: "shop-window", x: frontX + 7, y: 88, width: 19, height: 21 }));
                group.appendChild(svgEl("rect", { class: "shop-window", x: frontX + frontWidth - 27, y: 88, width: 19, height: 21 }));
                group.appendChild(svgEl("rect", { class: "shop-door", x: frontX + frontWidth / 2 - 9, y: 84, width: 18, height: 38 }));
              }
            }

            function renderCafeTable(group, x, y) {
              group.appendChild(svgEl("circle", { class: "outdoor-table", cx: x, cy: y, r: 6 }));
              group.appendChild(svgEl("rect", { class: "chair", x: x - 16, y: y - 4, width: 7, height: 8, rx: 2 }));
              group.appendChild(svgEl("rect", { class: "chair", x: x + 9, y: y - 4, width: 7, height: 8, rx: 2 }));
            }

            function renderShopIcon(group, snapshot, x, y) {
              const type = buildingType(snapshot);
              if (type === "Clinic" || type === "Pharmacy") {
                group.appendChild(svgEl("rect", { class: "shop-icon", x: x - 4, y: y - 7, width: 8, height: 14, rx: 1 }));
                group.appendChild(svgEl("rect", { class: "shop-icon", x: x - 7, y: y - 4, width: 14, height: 8, rx: 1 }));
              } else if (type === "Cafe") {
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 6} ${y - 3} h 12 v 6 c 0 4 -12 4 -12 0 z` }));
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x + 6} ${y - 1} c 8 0 8 6 0 6` }));
              } else if (type === "Bakery") {
                group.appendChild(svgEl("ellipse", { class: "shop-icon", cx: x, cy: y, rx: 9, ry: 5 }));
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 5} ${y - 2} c 2 3 4 3 6 0` }));
              } else if (type === "Mechanic") {
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 8} ${y + 6} L ${x + 7} ${y - 7}` }));
                group.appendChild(svgEl("circle", { class: "shop-icon", cx: x - 7, cy: y + 7, r: 3 }));
              } else if (type === "Supermarket") {
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 8} ${y - 4} h 14 l -2 8 h -10 z` }));
                group.appendChild(svgEl("circle", { class: "shop-icon", cx: x - 3, cy: y + 7, r: 2 }));
                group.appendChild(svgEl("circle", { class: "shop-icon", cx: x + 5, cy: y + 7, r: 2 }));
              } else if (type === "Restaurant") {
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 7} ${y + 6} V ${y - 6} M ${x - 3} ${y - 6} V ${y + 6} M ${x - 7} ${y - 1} H ${x - 3}` }));
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x + 5} ${y - 6} c 5 5 4 9 -1 12` }));
              } else if (type === "Laundry") {
                group.appendChild(svgEl("rect", { class: "shop-icon", x: x - 7, y: y - 7, width: 14, height: 14, rx: 2 }));
                group.appendChild(svgEl("circle", { class: "machine-door", cx: x, cy: y + 1, r: 4 }));
              } else if (type === "Hardware Shop" || type === "Hardware") {
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 8} ${y + 6} L ${x + 6} ${y - 8} M ${x + 2} ${y - 8} h 6 v 6` }));
              } else if (type === "Mini Market") {
                group.appendChild(svgEl("rect", { class: "shop-icon", x: x - 7, y: y - 6, width: 14, height: 12, rx: 2 }));
                group.appendChild(svgEl("path", { class: "shop-icon-line", d: `M ${x - 5} ${y - 2} H ${x + 5}` }));
              } else {
                group.appendChild(svgEl("circle", { class: "shop-icon", cx: x, cy: y, r: 6 }));
              }
            }

            function bindBuildingHover(group, snapshot, position) {
              const onEnter = () => showBuildingHover(snapshot, position);
              const onLeave = () => hideHoverState();
              const hoverArea = svgEl("rect", {
                class: "hover-area",
                x: -16,
                y: -16,
                width: LAYOUT.buildingWidth + 32,
                height: LAYOUT.buildingHeight + 34,
              });

              ["pointerenter", "mouseenter", "mouseover", "mousemove"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, onEnter);
              });
              ["pointerleave", "mouseleave", "mouseout"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, onLeave);
              });
              ["pointerdown", "click"].forEach((eventName) => {
                hoverArea.addEventListener(eventName, (event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  onEnter();
                });
              });
              group.appendChild(hoverArea);
              group.addEventListener("focus", onEnter);
              group.addEventListener("blur", onLeave);
            }

            function renderTooltipLayer(svg) {
              const tooltip = svgEl("g", { id: "tooltip", class: "tooltip hidden" });
              tooltip.appendChild(svgEl("rect", {
                class: "tooltip-bg",
                x: 0,
                y: 0,
                width: 238,
                height: 112,
                rx: 8,
              }));
              tooltip.appendChild(svgEl("g", { id: "tooltipText" }));
              svg.appendChild(tooltip);
            }

            function showBuildingHover(snapshot, position) {
              hideFlows();
              const id = buildingId(snapshot);
              const net = currentGridNet();
              let shown = 0;

              if (alwaysShowFlow) {
                showAutomaticFlows();
              } else if (snapshot.status === "BUYER") {
                if (net > 0.005) {
                  shown = showFlows(`[data-flow-role="local-share"][data-target-id="${id}"]`);
                } else if (net < -0.005) {
                  shown = showDeficitNetworkFlows({ targetId: id, includeSubstation: true });
                }
              } else if (snapshot.status === "SELLER") {
                if (net > 0.005) {
                  shown = showFlows(`[data-flow-role="local-share"][data-source-id="${id}"]`);
                  if (shown === 0) {
                    shown = showFlows(`[data-flow-role="seller-export"][data-source-id="${id}"]`);
                  }
                } else if (net < -0.005) {
                  shown = showDeficitNetworkFlows({ sourceId: id, includeSubstation: false });
                }
              }
              showTooltip(snapshot, position);
            }

            function showSubstationHover(width) {
              hideFlows();
              if (alwaysShowFlow) {
                showAutomaticFlows();
              } else if (currentGridNet() < -0.005) {
                showDeficitNetworkFlows({ includeSellers: false, includeSubstation: true });
              }
              showSubstationTooltip(width);
            }

            function hideHoverState() {
              const tooltip = currentSvg && currentSvg.querySelector("#tooltip");
              if (tooltip) tooltip.classList.add("hidden");
              if (alwaysShowFlow) {
                showAutomaticFlows();
              } else {
                hideFlows();
              }
            }

            function hideFlows() {
              if (!currentSvg) return;
              currentSvg.querySelectorAll(".flow").forEach((flow) => {
                flow.style.display = "none";
                flow.classList.remove("active");
              });
            }

            function showFlows(selector) {
              if (!currentSvg) return 0;
              let count = 0;
              currentSvg.querySelectorAll(selector).forEach((flow) => {
                flow.style.display = "block";
                flow.classList.add("active");
                count += 1;
              });
              return count;
            }

            function showDeficitNetworkFlows({
              targetId = null,
              sourceId = null,
              includeSellers = true,
              includeSubstation = true,
              includeBuyerDelivery = true,
            } = {}) {
              const sellerSelector = sourceId
                ? `[data-flow-role="deficit-local-contribution"][data-source-id="${sourceId}"]`
                : targetId
                  ? `[data-flow-role="deficit-local-contribution"][data-target-id="${targetId}"]`
                  : `[data-flow-role="deficit-local-contribution"]`;
              const importSelector = targetId
                ? `[data-flow-role="deficit-import"][data-target-id="${targetId}"]`
                : `[data-flow-role="deficit-import"]`;
              const deliverySelector = targetId
                ? `[data-flow-role="buyer-delivery"][data-target-id="${targetId}"]`
                : `[data-flow-role="buyer-delivery"]`;

              const sellerCount = includeSellers ? showFlows(sellerSelector) : 0;
              const importCount = includeSubstation ? showFlows(importSelector) : 0;
              const deliveryCount = includeBuyerDelivery ? showFlows(deliverySelector) : 0;

              if (sellerCount === 0 && sourceId) {
                return showFlows(`[data-flow-role="deficit-seller-export"][data-source-id="${sourceId}"]`)
                  + importCount
                  + deliveryCount;
              }

              return sellerCount + importCount + deliveryCount;
            }

            function showAutomaticFlows() {
              hideFlows();
              const net = currentGridNet();
              if (net > 0.005) {
                showFlows(`[data-flow-role="seller-export"]`);
                showFlows(`[data-flow-role="grid-to-buyer"]`);
                showFlows(`[data-flow-role="buyer-delivery"]`);
              } else if (net < -0.005) {
                showFlows(`[data-flow-role="deficit-seller-export"]`);
                showFlows(`[data-flow-role="deficit-import"]`);
                showFlows(`[data-flow-role="buyer-delivery"]`);
              }
            }

            function showTooltip(snapshot, position) {
              const tooltip = currentSvg.querySelector("#tooltip");
              const tooltipBg = tooltip.querySelector(".tooltip-bg");
              const textGroup = currentSvg.querySelector("#tooltipText");
              const tooltipWidth = 238;
              const tooltipHeight = 112;
              const margin = 18;
              const viewBoxWidth = Number(currentSvg.getAttribute("viewBox").split(" ")[2]);
              const viewBoxHeight = Number(currentSvg.getAttribute("viewBox").split(" ")[3]);
              const buildingCenterX = position.x + LAYOUT.buildingWidth / 2;
              const leftX = position.x - tooltipWidth - 22;
              const rightX = position.x + LAYOUT.buildingWidth + 22;
              let x = buildingCenterX < viewBoxWidth / 2 ? rightX : leftX;

              if (x < margin) x = rightX;
              if (x + tooltipWidth > viewBoxWidth - margin) x = leftX;
              x = Math.max(margin, Math.min(x, viewBoxWidth - tooltipWidth - margin));

              let y = position.isTop
                ? Math.max(margin, position.y - tooltipHeight - 16)
                : Math.min(viewBoxHeight - tooltipHeight - margin, position.y + LAYOUT.buildingHeight + 16);
              if (position.isTop && y < margin) y = margin;
              if (!position.isTop && y + tooltipHeight > viewBoxHeight - margin) {
                y = viewBoxHeight - tooltipHeight - margin;
              }

              tooltipBg.setAttribute("width", tooltipWidth);
              tooltipBg.setAttribute("height", tooltipHeight);
              tooltip.setAttribute("transform", `translate(${x} ${y})`);
              tooltip.classList.remove("hidden");
              textGroup.innerHTML = "";

              [
                ["Generated power", formatPlainEnergy(snapshot.generation)],
                ["Consumption power", formatPlainEnergy(snapshot.consumption)],
                ["Net energy", formatEnergy(snapshot.net_energy)],
              ].forEach(([label, value], row) => {
                const rowY = 26 + row * 28;
                const labelText = svgEl("text", { class: "tooltip-label", x: 14, y: rowY });
                labelText.textContent = label;
                const tone = label === "Net energy" ? netTone(Number(snapshot.net_energy || 0)) : "";
                const valueText = svgEl("text", {
                  class: `tooltip-value ${tone}`.trim(),
                  x: tooltipWidth - 14,
                  y: rowY,
                });
                valueText.textContent = value;
                textGroup.appendChild(labelText);
                textGroup.appendChild(valueText);
              });
            }

            function showSubstationTooltip(width) {
              const tooltip = currentSvg.querySelector("#tooltip");
              const tooltipBg = tooltip.querySelector(".tooltip-bg");
              const textGroup = currentSvg.querySelector("#tooltipText");
              const tooltipWidth = 256;
              const tooltipHeight = 112;
              const totals = currentTotals();
              const net = currentGridNet();
              const x = Math.min(width - tooltipWidth - 18, stageCenterX(width) + 92);
              const y = 34;

              tooltipBg.setAttribute("width", tooltipWidth);
              tooltipBg.setAttribute("height", tooltipHeight);
              tooltip.setAttribute("transform", `translate(${x} ${y})`);
              tooltip.classList.remove("hidden");
              textGroup.innerHTML = "";

              [
                ["Generated power", formatPlainEnergy(totals.generation || 0), ""],
                ["Consumption power", formatPlainEnergy(totals.consumption || 0), ""],
                ["Net energy", formatEnergy(net), netTone(net)],
              ].forEach(([label, value, tone], row) => {
                const rowY = 26 + row * 28;
                const labelText = svgEl("text", { class: "tooltip-label", x: 14, y: rowY });
                labelText.textContent = label;
                const valueText = svgEl("text", {
                  class: `tooltip-value ${tone}`.trim(),
                  x: tooltipWidth - 14,
                  y: rowY,
                });
                valueText.textContent = value;
                textGroup.appendChild(labelText);
                textGroup.appendChild(valueText);
              });
            }

            function setAtmosphere(hour) {
              const period = periodForHour(hour);
              const weather = DATA.weather || "Sunny";
              dashboard.dataset.period = period;
              dashboard.dataset.weather = weather;
              dashboard.dataset.quality = QUALITY_MODE;
              dashboard.dataset.cameraMode = CAMERA_MODE;
              applyTheme(getTheme(Number(hour), weather));
              periodLabel.textContent = period;
              const sunAlpha = period === "day" ? 0.86 : period === "dawn" ? 0.64 : period === "dusk" ? 0.34 : 0;
              dashboard.style.setProperty("--orb-alpha", sunAlpha);
            }

            function updateStats() {
              const current = DATA.hourly_totals[String(activeHour)] || {};
              const daily = DATA.daily_totals || {};
              dashboard.dataset.gridState = gridState(Number(current.net_energy || 0));
              document.getElementById("currentGeneration").textContent = formatPlainEnergy(current.generation || 0);
              document.getElementById("currentConsumption").textContent = formatPlainEnergy(current.consumption || 0);
              document.getElementById("currentNet").textContent = formatEnergy(current.net_energy || 0);
              document.getElementById("dailyGeneration").textContent = formatPlainEnergy(daily.generation || 0);
              document.getElementById("dailyConsumption").textContent = formatPlainEnergy(daily.consumption || 0);
              document.getElementById("dailyNet").textContent = formatEnergy(daily.net_energy || 0);
              setToneClass(document.getElementById("currentNet"), Number(current.net_energy || 0));
              setToneClass(document.getElementById("dailyNet"), Number(daily.net_energy || 0));
            }

            function setToneClass(element, value) {
              if (!element) return;
              element.classList.remove("positive", "negative", "neutral");
              element.classList.add(netTone(value));
            }

            function setHour(hour) {
              activeHour = Number(hour);
              timeSlider.value = String(activeHour);
              timeLabel.textContent = hourText(activeHour);
              saveSceneState({ hour: activeHour });
              setAtmosphere(activeHour);
              renderScene();
              updateStats();
            }

            function updatePlayButton() {
              playButton.textContent = playTimer ? "||" : ">";
            }

            function startPlay() {
              if (playTimer) return;
              saveSceneState({ playing: true });
              playTimer = setInterval(() => {
                setHour((activeHour + 1) % 24);
              }, 950);
              updatePlayButton();
            }

            function stopPlay() {
              if (playTimer) {
                clearInterval(playTimer);
                playTimer = null;
              }
              saveSceneState({ playing: false });
              updatePlayButton();
            }

            function togglePlay() {
              if (playTimer) stopPlay();
              else startPlay();
            }

            timeSlider.addEventListener("input", (event) => setHour(event.target.value));
            playButton.addEventListener("click", togglePlay);

            setHour(activeHour);
            if (restorePlaying) {
              startPlay();
            } else {
              updatePlayButton();
            }
          </script>
        </body>
        </html>
        """
    )

    return (
        html.replace("__DATA_JSON__", data_json).replace(
            "__ALWAYS_SHOW_FLOW__", "true" if always_show_flow else "false"
        )
        .replace("__QUALITY_MODE__", quality_json)
        .replace("__CAMERA_MODE__", camera_json)
    )


def _normalize_quality_mode(value: str) -> str:
    if value not in {"High Quality", "Balanced", "Performance"}:
        return "Balanced"
    return value


def _normalize_camera_mode(value: str) -> str:
    if value not in {"Neighborhood View", "Grid View", "Energy View"}:
        return "Neighborhood View"
    return value
