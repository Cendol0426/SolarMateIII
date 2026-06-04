"""Isometric neighborhood scene renderer for the Streamlit dashboard."""

from __future__ import annotations

import json
from textwrap import dedent


def neighborhood_scene_height(building_count: int) -> int:
    """Return an iframe height large enough for the responsive SVG scene."""

    return 1040


def render_neighborhood_scene(payload: dict, always_show_flow: bool = False) -> str:
    """Render a self-contained HTML/SVG 3D-style neighborhood scene.

    The payload comes from ``smart_grid.build_simulation_payload`` and keeps the
    simulation data separate from the rendering details in this module.
    """

    data_json = json.dumps(payload)

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
              --seller: #1f9d55;
              --buyer: #e08b21;
              --balanced: #718096;
            }

            * { box-sizing: border-box; }

            body {
              margin: 0;
              color: var(--text);
              font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
              background: #eef5fb;
            }

            .dashboard {
              min-height: 980px;
              position: relative;
              overflow: hidden;
              border: 1px solid rgba(32, 48, 64, 0.12);
              border-radius: 8px;
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
              --panel: rgba(247, 250, 255, 0.92);
            }

            .dashboard[data-period="dawn"] {
              --sky-top: #f0a36a;
              --sky-bottom: #f7d891;
              --ground: #63ad69;
              --ground-dark: #438757;
            }

            .dashboard[data-period="dusk"] {
              --sky-top: #34416a;
              --sky-bottom: #dc875f;
              --ground: #3f7655;
              --ground-dark: #2f5e43;
            }

            .dashboard[data-weather="Cloudy"] {
              --sky-top: #aebdca;
              --sky-bottom: #dbe3ea;
              --ground: #5d9a65;
              --ground-dark: #3f754d;
            }

            .dashboard[data-weather="Rainy"] {
              --sky-top: #657383;
              --sky-bottom: #a0acb7;
              --ground: #4d7b5b;
              --ground-dark: #315a42;
              --road: #46515c;
              --road-dark: #36404c;
            }

            .dashboard[data-weather="Cloudy"][data-period="night"],
            .dashboard[data-weather="Rainy"][data-period="night"] {
              --sky-top: #151b27;
              --sky-bottom: #313a4b;
              --ground: #20362b;
              --ground-dark: #192a22;
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
              z-index: 1;
              pointer-events: none;
              overflow: hidden;
            }

            .cloud {
              position: absolute;
              width: 180px;
              height: 58px;
              opacity: 0;
              border-radius: 999px;
              background:
                radial-gradient(circle at 24% 55%, rgba(255, 255, 255, 0.88) 0 29px, transparent 30px),
                radial-gradient(circle at 48% 35%, rgba(255, 255, 255, 0.94) 0 39px, transparent 40px),
                radial-gradient(circle at 72% 55%, rgba(255, 255, 255, 0.86) 0 31px, transparent 32px),
                rgba(255, 255, 255, 0.78);
            }

            .cloud.one { left: 6%; top: 10%; }
            .cloud.two { left: 42%; top: 14%; transform: scale(1.15); }
            .cloud.three { right: 7%; top: 8%; transform: scale(0.92); }

            .dashboard[data-weather="Cloudy"] .cloud {
              opacity: 0.72;
            }

            .dashboard[data-weather="Rainy"] .cloud {
              opacity: 0.84;
              filter: grayscale(0.45) brightness(0.82);
            }

            .rain {
              position: absolute;
              inset: -90px 0 0;
              opacity: 0;
              background-image:
                repeating-linear-gradient(104deg, rgba(238, 247, 255, 0) 0 18px, rgba(238, 247, 255, 0.58) 19px 21px, rgba(238, 247, 255, 0) 22px 43px);
              background-size: 112px 124px;
              animation: rain-fall 0.75s linear infinite;
            }

            .dashboard[data-weather="Rainy"] .rain {
              opacity: 0.62;
            }

            @keyframes rain-fall {
              from { transform: translate3d(0, -42px, 0); }
              to { transform: translate3d(-30px, 82px, 0); }
            }

            .topbar {
              position: relative;
              z-index: 4;
              display: grid;
              grid-template-columns: minmax(280px, 0.9fr) minmax(360px, 1.35fr);
              gap: 14px;
              padding: 16px;
            }

            .control-panel,
            .stats-panel {
              background: var(--panel);
              border: 1px solid rgba(22, 34, 48, 0.14);
              border-radius: 8px;
              box-shadow: 0 14px 32px rgba(24, 36, 48, 0.12);
              backdrop-filter: blur(10px);
            }

            .control-panel {
              display: grid;
              grid-template-columns: auto minmax(200px, 1fr);
              align-items: center;
              gap: 14px;
              padding: 14px;
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
              padding: 12px;
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
              padding: 9px 10px;
              border: 1px solid rgba(30, 44, 60, 0.1);
              border-radius: 8px;
              background: rgba(255, 255, 255, 0.58);
            }

            .stat-label {
              color: var(--muted);
              font-size: 11px;
              font-weight: 800;
            }

            .stat-value {
              margin-top: 6px;
              font-size: 18px;
              font-weight: 900;
              font-variant-numeric: tabular-nums;
            }

            .scene-shell {
              position: relative;
              z-index: 2;
              padding: 0 16px 30px;
            }

            .grid-svg {
              width: 100%;
              max-width: 1080px;
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
            .building-group:focus { outline: none; }
            .building-shadow { fill: rgba(15, 24, 32, 0.18); }
            .hover-area {
              fill: #fff;
              opacity: 0.001;
              pointer-events: all;
            }

            .home-front {
              fill: #f0c66c;
              stroke: #8e6334;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .home-side {
              fill: #d7a957;
              stroke: #8e6334;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .home-roof-main {
              fill: #a43a32;
              stroke: #72302b;
              stroke-width: 3;
              shape-rendering: crispEdges;
            }
            .home-roof-side {
              fill: #7d2e2a;
              stroke: #72302b;
              stroke-width: 3;
              shape-rendering: crispEdges;
            }
            .window {
              fill: #8bd3ff;
              stroke: #6d4d32;
              stroke-width: 2.6;
              shape-rendering: crispEdges;
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

            .shop-front {
              fill: #dfe8ef;
              stroke: #5a6c7b;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .shop-side {
              fill: #b8c8d3;
              stroke: #5a6c7b;
              stroke-width: 3.3;
              shape-rendering: crispEdges;
            }
            .shop-top {
              fill: #546879;
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
              fill: #fff0c9;
              stroke: #8d7150;
              stroke-width: 2;
              shape-rendering: crispEdges;
            }
            .shop-awning-stripe {
              fill: rgba(214, 67, 67, 0.78);
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

            .connection {
              fill: #fbfdff;
              stroke: var(--cable);
              stroke-width: 3;
            }

            .tooltip.hidden { display: none; }
            .tooltip {
              pointer-events: none;
              filter: drop-shadow(0 13px 20px rgba(14, 23, 34, 0.24));
            }
            .tooltip-bg {
              fill: rgba(255, 255, 255, 0.97);
              stroke: rgba(20, 32, 43, 0.16);
              stroke-width: 1.3;
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
            .tooltip-value.positive { fill: #1f9d55; }
            .tooltip-value.negative { fill: #c93535; }
            .tooltip-value.neutral { fill: #6b7280; }

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
              <div class="rain"></div>
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
            };
            const DEBUG_GRID_NODES = false;

            let activeHour = 12;
            let playTimer = null;
            let currentSvg = null;
            let alwaysShowFlow = __ALWAYS_SHOW_FLOW__;

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
              if (type === "Restaurant") return "Eatery";
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
                Hardware: "#a66a27",
              };
              return colors[buildingType(snapshot)] || "#2b7a8f";
            }

            function periodForHour(hour) {
              if (hour < 5 || hour >= 20) return "night";
              if (hour < 8) return "dawn";
              if (hour >= 18) return "dusk";
              return "day";
            }

            function hourText(hour) {
              return `${String(hour).padStart(2, "0")}:00`;
            }

            function stageWidth(buildingCount) {
              const columns = Math.ceil(buildingCount / 2);
              return Math.max(
                LAYOUT.baseWidth,
                LAYOUT.sidePadding * 2 + columns * LAYOUT.slotWidth + LAYOUT.clusterGap + LAYOUT.buildingWidth
              );
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
              const gap = shopWidth > 0 && homeWidth > 0 ? LAYOUT.clusterGap : 0;
              const totalWidth = shopWidth + homeWidth + gap;
              const startX = (width - totalWidth) / 2;
              const homeStartX = startX + shopWidth + gap;

              assignClusterPositions(shops, startX, positions, "commercial");
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

            function connectionPoint(position) {
              const local = connectionLocal(position);
              return {
                x: position.x + local.x,
                y: position.y + local.y,
              };
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
                  d: `M ${network.stationX} ${substationAttachY()} L ${network.stationX} ${LAYOUT.mainGridY} ${mainGridSegmentTo(pylon.x)}`,
                  duration,
                },
                {
                  kind: "YELLOW",
                  d: pylonToBuildingPath(position),
                  duration: slowerDuration(duration),
                },
              ];
            }

            function localSharePath(sourcePosition, targetPosition) {
              const targetPylon = pylonPosition(targetPosition);
              return [
                buildingToPylonPath(sourcePosition),
                `L ${targetPylon.x} ${LAYOUT.mainGridY}`,
                pylonToBuildingCommands(targetPosition),
              ].join(" ");
            }

            function localShareSegments(sourcePosition, targetPosition) {
              const sourcePylon = pylonPosition(sourcePosition);
              const targetPylon = pylonPosition(targetPosition);
              return [
                {
                  kind: "GREEN",
                  d: `${buildingToPylonPath(sourcePosition)} ${mainGridSegmentTo(sourcePylon.x)} ${mainGridSegmentTo(targetPylon.x)}`,
                },
                {
                  kind: "YELLOW",
                  d: pylonToBuildingPath(targetPosition),
                },
              ];
            }

            function sellerToGridPath(position, network) {
              const pylon = pylonPosition(position);
              return `${buildingToPylonPath(position)} ${mainGridSegmentTo(pylon.x)} ${mainGridSegmentTo(network.stationX)}`;
            }

            function renderScene() {
              const snapshots = DATA.hours[String(activeHour)] || [];
              const width = stageWidth(snapshots.length);
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
              const deficitDuration = durationForExport(Math.max(0, -currentGridNet()), maxGridDeficit());
              const pairKeys = new Set();

              function addPair(source, target) {
                pairKeys.add(`${source.id}->${target.id}`);
              }

              buyers.forEach((buyer) => {
                sellers
                  .slice()
                  .sort((a, b) => Math.abs(a.position.x - buyer.position.x) - Math.abs(b.position.x - buyer.position.x))
                  .slice(0, 2)
                  .forEach((seller) => addPair(seller, buyer));
              });

              sellers.forEach((seller) => {
                buyers
                  .slice()
                  .sort((a, b) => Math.abs(a.position.x - seller.position.x) - Math.abs(b.position.x - seller.position.x))
                  .slice(0, 2)
                  .forEach((buyer) => addPair(seller, buyer));
              });

              pairKeys.forEach((key) => {
                const [sourceId, targetId] = key.split("->");
                const source = entries.find((entry) => String(entry.id) === sourceId);
                const target = entries.find((entry) => String(entry.id) === targetId);
                if (!source || !target) return;
                renderFlow(layer, localShareSegments(source.position, target.position), {
                  "data-flow-role": "local-share",
                  "data-source-id": source.id,
                  "data-target-id": target.id,
                  "data-duration": durationForExport(source.snapshot.net_energy, exportReference),
                });
              });

              buyers.forEach((buyer) => {
                renderFlow(layer, substationToBuildingSegments(buyer.position, network, deficitDuration), {
                  "data-flow-role": "deficit-import",
                  "data-target-id": buyer.id,
                  "data-duration": deficitDuration,
                });
              });

              sellers.forEach((seller) => {
                renderFlow(layer, [{ kind: "GREEN", d: sellerToGridPath(seller.position, network) }], {
                  "data-flow-role": "seller-export",
                  "data-source-id": seller.id,
                  "data-duration": durationForExport(seller.snapshot.net_energy, exportReference),
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

                [0, 0.18, 0.36, 0.54, 0.72, 0.9].forEach((offset, index) => {
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
              });

              group.appendChild(svgEl("ellipse", {
                class: "building-shadow",
                cx: 56,
                cy: 126,
                rx: 64,
                ry: 14,
              }));

              if (snapshot.has_solar) {
                renderSolarHome(group);
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

            function renderSolarHome(group) {
              group.appendChild(svgEl("polygon", {
                class: "home-side",
                points: "84,52 106,41 106,105 84,116",
              }));
              group.appendChild(svgEl("rect", {
                class: "home-front",
                x: 18,
                y: 52,
                width: 66,
                height: 64,
              }));
              group.appendChild(svgEl("polygon", {
                class: "home-roof-main",
                points: "8,52 52,14 96,52 84,62 52,34 18,62",
              }));
              group.appendChild(svgEl("polygon", {
                class: "home-roof-side",
                points: "52,14 106,41 96,52",
              }));
              renderSolarPanel(group);
              group.appendChild(svgEl("rect", { class: "window", x: 27, y: 68, width: 15, height: 15 }));
              group.appendChild(svgEl("rect", { class: "window", x: 60, y: 68, width: 15, height: 15 }));
              group.appendChild(svgEl("rect", { class: "door", x: 43, y: 86, width: 20, height: 30 }));
              group.appendChild(svgEl("circle", { class: "door-knob", cx: 58, cy: 101, r: 2 }));
            }

            function renderSolarPanel(group) {
              group.appendChild(svgEl("polygon", {
                class: "solar-panel",
                points: "34,31 67,34 60,48 27,45",
              }));
              [
                "M 39 32 L 33 46",
                "M 47 32.6 L 41 46.7",
                "M 55 33.3 L 49 47.4",
                "M 63 34 L 57 48",
                "M 31 39 L 63 42",
              ].forEach((d) => group.appendChild(svgEl("path", { class: "solar-line", d })));
            }

            function renderShopLot(group, snapshot) {
              group.setAttribute("style", `--shop-color: ${shopColor(snapshot)}`);
              group.appendChild(svgEl("polygon", {
                class: "shop-side",
                points: "88,34 108,44 108,112 88,122",
              }));
              group.appendChild(svgEl("rect", {
                class: "shop-front",
                x: 14,
                y: 40,
                width: 74,
                height: 82,
                rx: 2,
              }));
              group.appendChild(svgEl("polygon", {
                class: "shop-top",
                points: "14,40 34,24 88,24 108,44 88,44 88,40",
              }));
              group.appendChild(svgEl("rect", {
                class: "shop-sign",
                x: 20,
                y: 46,
                width: 62,
                height: 19,
                rx: 2,
              }));
              const label = svgEl("text", {
                class: "shop-label",
                x: 51,
                y: 55,
                textLength: 55,
                lengthAdjust: "spacingAndGlyphs",
              });
              label.textContent = shortShopName(snapshot);
              group.appendChild(label);
              group.appendChild(svgEl("rect", {
                class: "shop-awning",
                x: 18,
                y: 68,
                width: 66,
                height: 12,
              }));
              [20, 36, 52, 68].forEach((x) => {
                group.appendChild(svgEl("rect", {
                  class: "shop-awning-stripe",
                  x,
                  y: 68,
                  width: 8,
                  height: 12,
                }));
              });
              group.appendChild(svgEl("rect", { class: "shop-window", x: 21, y: 88, width: 19, height: 21 }));
              group.appendChild(svgEl("rect", { class: "shop-window", x: 63, y: 88, width: 19, height: 21 }));
              group.appendChild(svgEl("rect", { class: "shop-door", x: 43, y: 84, width: 18, height: 38 }));
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
                  shown = showDeficitNetworkFlows({ targetId: id });
                }
              } else if (snapshot.status === "SELLER") {
                if (net > 0.005) {
                  shown = showFlows(`[data-flow-role="local-share"][data-source-id="${id}"]`);
                  if (shown === 0) {
                    shown = showFlows(`[data-flow-role="seller-export"][data-source-id="${id}"]`);
                  }
                } else if (net < -0.005) {
                  shown = showDeficitNetworkFlows({ sourceId: id });
                }
              }
              showTooltip(snapshot, position);
            }

            function showSubstationHover(width) {
              hideFlows();
              if (alwaysShowFlow) {
                showAutomaticFlows();
              } else if (currentGridNet() < -0.005) {
                showDeficitNetworkFlows();
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

            function showDeficitNetworkFlows({ targetId = null, sourceId = null } = {}) {
              const sellerSelector = sourceId
                ? `[data-flow-role="seller-export"][data-source-id="${sourceId}"]`
                : `[data-flow-role="seller-export"]`;
              const importSelector = targetId
                ? `[data-flow-role="deficit-import"][data-target-id="${targetId}"]`
                : `[data-flow-role="deficit-import"]`;

              return showFlows(sellerSelector) + showFlows(importSelector);
            }

            function showAutomaticFlows() {
              hideFlows();
              const net = currentGridNet();
              if (net > 0.005) {
                showFlows(`[data-flow-role="local-share"]`);
              } else if (net < -0.005) {
                showDeficitNetworkFlows();
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
              dashboard.dataset.period = period;
              dashboard.dataset.weather = DATA.weather || "Sunny";
              periodLabel.textContent = period;
              const sunAlpha = period === "day" ? 0.86 : period === "dawn" ? 0.64 : period === "dusk" ? 0.34 : 0;
              dashboard.style.setProperty("--orb-alpha", sunAlpha);
            }

            function updateStats() {
              const current = DATA.hourly_totals[String(activeHour)] || {};
              const daily = DATA.daily_totals || {};
              document.getElementById("currentGeneration").textContent = formatPlainEnergy(current.generation || 0);
              document.getElementById("currentConsumption").textContent = formatPlainEnergy(current.consumption || 0);
              document.getElementById("currentNet").textContent = formatEnergy(current.net_energy || 0);
              document.getElementById("dailyGeneration").textContent = formatPlainEnergy(daily.generation || 0);
              document.getElementById("dailyConsumption").textContent = formatPlainEnergy(daily.consumption || 0);
              document.getElementById("dailyNet").textContent = formatEnergy(daily.net_energy || 0);
            }

            function setHour(hour) {
              activeHour = Number(hour);
              timeSlider.value = String(activeHour);
              timeLabel.textContent = hourText(activeHour);
              setAtmosphere(activeHour);
              renderScene();
              updateStats();
            }

            function updatePlayButton() {
              playButton.textContent = playTimer ? "||" : ">";
            }

            function startPlay() {
              if (playTimer) return;
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
              updatePlayButton();
            }

            function togglePlay() {
              if (playTimer) stopPlay();
              else startPlay();
            }

            timeSlider.addEventListener("input", (event) => setHour(event.target.value));
            playButton.addEventListener("click", togglePlay);

            setHour(activeHour);
          </script>
        </body>
        </html>
        """
    )

    return (
        html.replace("__DATA_JSON__", data_json).replace(
            "__ALWAYS_SHOW_FLOW__", "true" if always_show_flow else "false"
        )
    )
