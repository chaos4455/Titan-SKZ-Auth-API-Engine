# -*- coding: utf-8 -*-
"""
TITAN MONITOR OMNISCIENCE V9-ZKP - ULTIMATE OBSERVABILITY
Sistema de Visualização de Alta Performance para TitanAuth Engine.
Inclui painéis ZKP: identidades, challenges, mints, CA, KPIs e indicadores.
Design: O2 Data Solutions Standard | Elias Andrade — Replika AI Solutions
Micro-revisão: 000000002
"""

import os
from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# =======================================================================================
# 💎 UI/UX ENGINE: HTML5 + CSS3 + MODERN JAVASCRIPT — TODAS AS STATS DA API
# =======================================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titan Omniscience V9-ZKP | Observabilidade Definitiva</title>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-body: #F0F2F9;
            --white: #FFFFFF;
            --primary: #4318FF;
            --primary-grad: linear-gradient(135deg, #4318FF 0%, #B085FF 100%);
            --secondary-grad: linear-gradient(135deg, #11047A 0%, #2111A5 100%);
            --accent-purple: #868CFF;
            --success: #05CD99;
            --success-bg: rgba(5, 205, 153, 0.1);
            --warning: #FFB800;
            --warning-bg: rgba(255, 184, 0, 0.1);
            --error: #EE5D50;
            --error-bg: rgba(238, 93, 80, 0.1);
            --text-main: #1B2559;
            --text-sec: #A3AED0;
            --shadow-sm: 0px 4px 12px rgba(0, 0, 0, 0.03);
            --shadow-lg: 0px 40px 50px -20px rgba(0, 0, 0, 0.08);
            --glass: rgba(255, 255, 255, 0.8);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg-body); color: var(--text-main); overflow-x: hidden; -webkit-font-smoothing: antialiased; }

        .txt-success { color: var(--success) !important; }
        .txt-warning { color: var(--warning) !important; }
        .txt-error { color: var(--error) !important; }
        .bg-success { background: var(--success-bg); }
        .bg-warning { background: var(--warning-bg); }
        .bg-error { background: var(--error-bg); }

        header {
            background: var(--glass);
            padding: 15px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-sm);
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }

        .brand { display: flex; align-items: center; gap: 15px; }
        .brand-logo { width: 45px; height: 45px; background: var(--primary-grad); border-radius: 14px; display: flex; align-items: center; justify-content: center; color: white; font-size: 22px; box-shadow: 0 8px 16px rgba(67, 24, 255, 0.2); }
        .brand-name { font-size: 24px; font-weight: 800; letter-spacing: -1px; }

        .sys-status { display: flex; align-items: center; gap: 10px; background: var(--bg-body); padding: 8px 16px; border-radius: 12px; font-weight: 700; font-size: 13px; }

        .wrapper { padding: 30px 50px; }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }

        .kpi-card {
            background: var(--white);
            border-radius: 20px;
            padding: 22px;
            display: flex;
            align-items: center;
            gap: 18px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.3s ease;
        }
        .kpi-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-lg); }

        .kpi-icon-circle { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .kpi-content .kpi-label { color: var(--text-sec); font-size: 13px; font-weight: 600; margin-bottom: 4px; }
        .kpi-content .kpi-value { font-size: 26px; font-weight: 800; color: var(--text-main); }

        .section-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 28px; margin-bottom: 28px; }
        .section-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-bottom: 28px; }

        .card-panel {
            background: var(--white);
            border-radius: 24px;
            padding: 28px;
            box-shadow: var(--shadow-sm);
            position: relative;
        }

        .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; }
        .panel-title { font-size: 18px; font-weight: 800; display: flex; align-items: center; gap: 10px; }

        .progress-group { margin-bottom: 18px; }
        .progress-label { display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
        .progress-bar-bg { background: var(--bg-body); height: 10px; border-radius: 5px; overflow: hidden; }
        .progress-bar-fill { height: 100%; width: 0%; border-radius: 5px; transition: width 0.8s ease; }

        .metrics-table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
        .metrics-table tr { background: var(--bg-body); border-radius: 12px; }
        .metrics-table td { padding: 12px 14px; font-size: 13px; font-weight: 600; }
        .metrics-table td:first-child { border-radius: 12px 0 0 12px; color: var(--text-sec); }
        .metrics-table td:last-child { border-radius: 0 12px 12px 0; text-align: right; font-weight: 800; }

        .chart-wrapper { width: 100%; height: 320px; }
        .chart-wrapper-sm { width: 100%; height: 260px; }

        footer { padding: 36px 50px; background: var(--white); display: flex; justify-content: space-between; color: var(--text-sec); font-size: 13px; font-weight: 600; }

        @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(5, 205, 153, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(5, 205, 153, 0); } 100% { box-shadow: 0 0 0 0 rgba(5, 205, 153, 0); } }
        .pulse { animation: pulse-green 2s infinite; }

        .stat-badge { display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; background: var(--bg-body); color: var(--text-sec); margin-right: 6px; margin-bottom: 6px; }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo"><i class="fa-solid fa-shuttle-space"></i></div>
            <div class="brand-name">TITAN OMNISCIENCE <span style="font-weight: 400; color: var(--accent-purple);">V9-ZKP</span></div>
        </div>
        <div class="sys-status">
            <div id="status-indicator" class="pulse" style="width: 10px; height: 10px; border-radius: 50%; background: var(--success);"></div>
            <span id="status-text">ENGINE OPERATIONAL</span>
            <span style="margin-left: 16px; color: var(--text-sec);">| <span id="header-engine-name">TitanAuth Supreme</span></span>
            <span class="stat-badge" id="header-arch">-</span>
            <span class="stat-badge" id="header-python">-</span>
        </div>
    </header>

    <div class="wrapper">

        <!-- ROW 1: TOP KPIs — TODOS OS PRINCIPAIS DA API + EXTRAS -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E9EDF7; color: #4318FF;"><i class="fa-solid fa-arrows-up-down-left-right"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">TOTAL REQUESTS</div>
                    <div id="kpi-total-req" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E2FFF9; color: var(--success);"><i class="fa-solid fa-bolt"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">TPS CURRENT</div>
                    <div id="kpi-tps" class="kpi-value">0.00</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #FFF8E6; color: var(--warning);"><i class="fa-solid fa-stopwatch"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">LAT AVG (ms)</div>
                    <div id="kpi-latency" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #FFF0F0; color: var(--error);"><i class="fa-solid fa-chart-line"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">LAT PEAK (ms)</div>
                    <div id="kpi-lat-peak" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #F4F0FF; color: var(--accent-purple);"><i class="fa-solid fa-clock"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">LAT MIN (ms)</div>
                    <div id="kpi-lat-min" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #FEEfef; color: var(--error);"><i class="fa-solid fa-microchip"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">CPU %</div>
                    <div id="kpi-cpu" class="kpi-value">0%</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #F4F7FE; color: var(--accent-purple);"><i class="fa-solid fa-memory"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">RAM USS (MB)</div>
                    <div id="kpi-ram" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E8F4FD; color: #0ea5e9;"><i class="fa-solid fa-plug"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ACTIVE CONNECTIONS</div>
                    <div id="kpi-connections" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E9EDF7; color: var(--primary);"><i class="fa-solid fa-users-gear"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">THREADS</div>
                    <div id="kpi-workers" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" id="cb-icon-box" style="background: #E2FFF9; color: var(--success);"><i class="fa-solid fa-shield-halved"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">CIRCUIT BREAKER</div>
                    <div id="kpi-cb" class="kpi-value">CLOSED</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: var(--secondary-grad); color: white;"><i class="fa-solid fa-percent"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">SUCCESS RATE</div>
                    <div id="kpi-success-rate" class="kpi-value">0%</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E2FFF9; color: var(--success);"><i class="fa-solid fa-coins"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">TOKENS MINTED</div>
                    <div id="kpi-minted" class="kpi-value">0</div>
                </div>
            </div>
            <!-- ZKP KPIs -->
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E8F5E9; color: #2E7D32;"><i class="fa-solid fa-fingerprint"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP IDENTITIES</div>
                    <div id="kpi-zkp-identities" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E3F2FD; color: #1565C0;"><i class="fa-solid fa-puzzle-piece"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP CHALLENGES</div>
                    <div id="kpi-zkp-challenges" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E8F5E9; color: var(--success);"><i class="fa-solid fa-shield-check"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP MINTS OK</div>
                    <div id="kpi-zkp-mints-ok" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #FFEBEE; color: var(--error);"><i class="fa-solid fa-shield-xmark"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP MINTS FAIL</div>
                    <div id="kpi-zkp-mints-fail" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #FFF3E0; color: #E65100;"><i class="fa-solid fa-percent"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP SUCCESS RATE</div>
                    <div id="kpi-zkp-success-rate" class="kpi-value">100%</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #F3E5F5; color: #7B1FA2;"><i class="fa-solid fa-bolt"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">ZKP TPS</div>
                    <div id="kpi-zkp-tps" class="kpi-value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon-circle" style="background: #E1F5FE; color: #0277BD;"><i class="fa-solid fa-certificate"></i></div>
                <div class="kpi-content">
                    <div class="kpi-label">CA IDENTITIES</div>
                    <div id="kpi-ca-total" class="kpi-value">0</div>
                </div>
            </div>
        </div>

        <!-- ROW 2: TOTAL TRAFFIC — 30 MIN -->
        <div class="section-grid">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-chart-line"></i> Total Traffic — Histórico 30 min</div>
                    <div style="font-weight: 700; color: var(--text-sec);">30 min</div>
                </div>
                <div class="chart-wrapper">
                    <canvas id="chartTraffic30m"></canvas>
                </div>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-gauge-high"></i> Resource & Traffic</div>
                </div>
                <div class="progress-group">
                    <div class="progress-label"><span>CPU</span><span id="val-cpu-bar">0%</span></div>
                    <div class="progress-bar-bg"><div id="bar-cpu" class="progress-bar-fill" style="background: var(--primary-grad);"></div></div>
                </div>
                <div class="progress-group">
                    <div class="progress-label"><span>RAM VMS (MB)</span><span id="val-ram-bar">0</span></div>
                    <div class="progress-bar-bg"><div id="bar-ram" class="progress-bar-fill" style="background: var(--accent-purple);"></div></div>
                </div>
                <table class="metrics-table" style="margin-top: 20px;">
                    <tr><td>Success Rate (API)</td><td id="t-success-rate" class="txt-success">0%</td></tr>
                    <tr><td>Dropped Requests</td><td id="t-dropped" class="txt-error">0</td></tr>
                    <tr><td>Active Sockets</td><td id="t-sockets">0</td></tr>
                    <tr><td>Cumulative Processing (s)</td><td id="t-cumulative">0</td></tr>
                </table>
            </div>
        </div>

        <!-- ROW 3: TPS 60s + TPM 60s -->
        <div class="section-grid">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-bolt"></i> TPS — Últimos 60 s</div>
                    <div style="font-weight: 700; color: var(--text-sec);">60 s</div>
                </div>
                <div class="chart-wrapper-sm">
                    <canvas id="chartTps60s"></canvas>
                </div>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-chart-column"></i> TPM — Tokens mintados por minuto (30 min)</div>
                    <div style="font-weight: 700; color: var(--text-sec);">30 min</div>
                </div>
                <div class="chart-wrapper-sm">
                    <canvas id="chartTpm30m"></canvas>
                </div>
            </div>
        </div>

        <!-- ROW 4: WORKERS 60s + AVG LATENCY 60s -->
        <div class="section-grid">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-users-gear"></i> Workers (threads) — Últimos 60 s</div>
                    <div style="font-weight: 700; color: var(--text-sec);">60 s</div>
                </div>
                <div class="chart-wrapper-sm">
                    <canvas id="chartWorkers60s"></canvas>
                </div>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-stopwatch"></i> Avg Latency (ms) — Últimos 60 s</div>
                    <div style="font-weight: 700; color: var(--text-sec);">60 s</div>
                </div>
                <div class="chart-wrapper-sm">
                    <canvas id="chartLatency60s"></canvas>
                </div>
            </div>
        </div>

        <!-- ROW 5: ORQUESTRAÇÃO (Semáforos, Pistas, Cabeças, Workers, Processos) + REDE -->
        <div class="section-grid">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-diagram-project"></i> Orchestration — Semáforos, Pistas, Workers, Processos</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Semaphore Slots Total</td><td id="orch-sem-total">0</td></tr>
                    <tr><td>Semaphore In Use</td><td id="orch-sem-in-use" class="txt-warning">0</td></tr>
                    <tr><td>Semaphore Available</td><td id="orch-sem-available" class="txt-success">0</td></tr>
                    <tr><td>Thread Pool Max Workers</td><td id="orch-pool-max">0</td></tr>
                    <tr><td>Num Processes (cabeças)</td><td id="orch-num-processes">0</td></tr>
                    <tr><td>Active Workers</td><td id="orch-active-workers">0</td></tr>
                    <tr><td>Max Queue Capacity</td><td id="orch-max-queue">0</td></tr>
                    <tr><td>Q Current Size</td><td id="orch-q-current">0</td></tr>
                    <tr><td>Q Peak Size</td><td id="orch-q-peak">0</td></tr>
                </table>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-network-wired"></i> Network — API</div>
                </div>
                <table class="metrics-table">
                    <tr><td>HTTP Bytes Sent</td><td id="net-bytes-sent">0</td></tr>
                    <tr><td>HTTP Bytes Received</td><td id="net-bytes-recv">0</td></tr>
                    <tr><td>IO Read (MB)</td><td id="net-io-read">0</td></tr>
                    <tr><td>IO Write (MB)</td><td id="net-io-write">0</td></tr>
                </table>
                <div class="panel-header" style="margin-top: 20px;">
                    <div class="panel-title"><i class="fa-solid fa-server"></i> Engine Metadata</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Engine Name</td><td id="meta-name">-</td></tr>
                    <tr><td>Version</td><td id="meta-version">-</td></tr>
                    <tr><td>Uptime (s)</td><td id="meta-uptime">0</td></tr>
                    <tr><td>Architecture</td><td id="meta-arch">-</td></tr>
                    <tr><td>Python</td><td id="meta-python">-</td></tr>
                </table>
            </div>
        </div>

        <!-- ROW 4: LATENCY ANALYTICS + CRYPTO + SYSTEM (100% stats API) -->
        <div class="section-grid-2">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-wave-square"></i> Latency Analytics (ms) — API</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Average</td><td id="lat-avg">0</td></tr>
                    <tr><td>Peak</td><td id="lat-peak">0</td></tr>
                    <tr><td>Minimum</td><td id="lat-min">0</td></tr>
                    <tr><td>Cumulative (s)</td><td id="lat-cumulative">0</td></tr>
                </table>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-vault"></i> Cryptography Performance — API</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Algorithm</td><td id="sec-algo">-</td></tr>
                    <tr><td>Tokens Minted</td><td id="sec-minted">0</td></tr>
                    <tr><td>Signatures Generated</td><td id="sec-signatures">0</td></tr>
                    <tr><td>Blocked Attempts</td><td id="sec-blocked" class="txt-error">0</td></tr>
                    <tr><td>Last User</td><td id="sec-user">-</td></tr>
                    <tr><td>Last JTI</td><td id="sec-jti" style="font-size: 10px;">-</td></tr>
                </table>
            </div>
        </div>

        <div class="section-grid-2">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-microchip"></i> System Resources (low-level) — API</div>
                </div>
                <table class="metrics-table">
                    <tr><td>CPU %</td><td id="sys-cpu">0</td></tr>
                    <tr><td>Memory USS (MB)</td><td id="sys-uss">0</td></tr>
                    <tr><td>Memory VMS (MB)</td><td id="sys-vms">0</td></tr>
                    <tr><td>Open FDs</td><td id="sys-fds">0</td></tr>
                    <tr><td>Active Threads</td><td id="sys-threads">0</td></tr>
                    <tr><td>Voluntary Ctx Switches</td><td id="sys-ctx">0</td></tr>
                    <tr><td>IO Read (MB)</td><td id="sys-io-r">0</td></tr>
                    <tr><td>IO Write (MB)</td><td id="sys-io-w">0</td></tr>
                </table>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-list"></i> Traffic Telemetry — API</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Total Requests</td><td id="traffic-total">0</td></tr>
                    <tr><td>TPS Current</td><td id="traffic-tps">0</td></tr>
                    <tr><td>Active Connections</td><td id="traffic-conn">0</td></tr>
                    <tr><td>Success Rate</td><td id="traffic-success">0%</td></tr>
                    <tr><td>Dropped</td><td id="traffic-dropped">0</td></tr>
                    <tr><td>Circuit Breaker</td><td id="traffic-cb">-</td></tr>
                </table>
            </div>
        </div>

        <!-- ROW: ZKP PERFORMANCE + CA STATUS -->
        <div class="section-grid-2">
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-fingerprint"></i> ZKP Performance — Zero Knowledge Proof</div>
                    <div style="font-weight: 700; color: var(--text-sec);">60 s</div>
                </div>
                <div class="chart-wrapper-sm" style="margin-bottom: 18px;">
                    <canvas id="chartZkpTps60s"></canvas>
                </div>
                <table class="metrics-table">
                    <tr><td>Identities Created</td><td id="zkp-identities" class="txt-success">0</td></tr>
                    <tr><td>Challenges Issued</td><td id="zkp-challenges">0</td></tr>
                    <tr><td>Mints Success</td><td id="zkp-mints-ok" class="txt-success">0</td></tr>
                    <tr><td>Mints Failed</td><td id="zkp-mints-fail" class="txt-error">0</td></tr>
                    <tr><td>Mint Success Rate (%)</td><td id="zkp-success-rate">100%</td></tr>
                    <tr><td>ZKP TPS</td><td id="zkp-tps">0</td></tr>
                    <tr><td>Last Identity ID</td><td id="zkp-last-id" style="font-size: 10px;">-</td></tr>
                </table>
            </div>
            <div class="card-panel">
                <div class="panel-header">
                    <div class="panel-title"><i class="fa-solid fa-certificate"></i> CA — Certificate Authority</div>
                </div>
                <table class="metrics-table">
                    <tr><td>Identities Total (active)</td><td id="ca-identities-total" class="txt-success">0</td></tr>
                    <tr><td>Identities Revoked</td><td id="ca-identities-revoked" class="txt-warning">0</td></tr>
                    <tr><td>CA Status</td><td id="ca-status" class="txt-success">ok</td></tr>
                </table>
            </div>
        </div>

    </div>

    <footer>
        <div>&copy; Titan Engine Project | Elias Andrade — Replika AI Solutions</div>
        <div id="footer-uptime">UPTIME: 0s</div>
        <div id="footer-version">-</div>
    </footer>

    <script>
        const API_URL = "http://localhost:8000/v6/engine/stats";
        const MAX_HISTORY_30M = 1800;
        const MAX_HISTORY_60S = 60;
        const MAX_TPM_30M = 30;
        
        let trafficHistory30m = [], labels30m = [];
        let tpsHistory60 = [], workersHistory60 = [], latencyHistory60 = [], labels60 = [];
        let zkpTpsHistory60 = [];
        let tpmHistory30m = [], labels30mTpm = [];
        let lastMinuteId = null, lastMinuteStartTokensMinted = 0;

        function fmtMs(v) { return (v == null || isNaN(v)) ? "0" : Number(v).toFixed(2); }
        function fmtMb(b) { return (b == null) ? "0" : (b / 1024 / 1024).toFixed(2); }
        function colorClass(val, lowOk, highWarn) {
            if (val == null || isNaN(val)) return "";
            if (highWarn !== undefined) { if (val <= lowOk) return "txt-success"; if (val <= highWarn) return "txt-warning"; return "txt-error"; }
            if (val >= lowOk) return "txt-success"; if (val >= highWarn) return "txt-warning"; return "txt-error";
        }
        function colorCpu(cpu) {
            if (cpu == null || isNaN(cpu)) return "";
            if (cpu <= 70) return "txt-success"; if (cpu <= 90) return "txt-warning"; return "txt-error";
        }
        function colorLatency(ms) {
            if (ms == null || isNaN(ms)) return "";
            if (ms <= 500) return "txt-success"; if (ms <= 1000) return "txt-warning"; return "txt-error";
        }
        function colorSuccessRate(pctStr) {
            const n = parseFloat(String(pctStr).replace("%",""));
            if (isNaN(n)) return ""; if (n >= 90) return "txt-success"; if (n >= 60) return "txt-warning"; return "txt-error";
        }

        const optsLine = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { beginAtZero: true, grid: { color: 'rgba(163, 174, 208, 0.1)' }, ticks: { color: '#A3AED0', font: { weight: '600' } } } } };
        const optsLine60 = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: true, ticks: { maxTicksLimit: 10, color: '#A3AED0', font: { size: 9 } } }, y: { beginAtZero: true, grid: { color: 'rgba(163, 174, 208, 0.1)' }, ticks: { color: '#A3AED0' } } } };

        const chartTraffic30m = new Chart(document.getElementById('chartTraffic30m').getContext('2d'), { type: 'line', data: { labels: labels30m, datasets: [{ label: 'Total Traffic', data: trafficHistory30m, borderColor: '#4318FF', backgroundColor: 'rgba(67, 24, 255, 0.08)', borderWidth: 3, fill: true, tension: 0.4, pointRadius: 0 }] }, options: optsLine });
        const chartTps60s = new Chart(document.getElementById('chartTps60s').getContext('2d'), { type: 'line', data: { labels: labels60, datasets: [{ label: 'TPS', data: tpsHistory60, borderColor: '#05CD99', backgroundColor: 'rgba(5, 205, 153, 0.12)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 1 }] }, options: optsLine60 });
        const chartTpm30m = new Chart(document.getElementById('chartTpm30m').getContext('2d'), { type: 'line', data: { labels: labels30mTpm, datasets: [{ label: 'Tokens/min', data: tpmHistory30m, borderColor: '#FFB800', backgroundColor: 'rgba(255, 184, 0, 0.12)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 2 }] }, options: optsLine60 });
        const chartWorkers60s = new Chart(document.getElementById('chartWorkers60s').getContext('2d'), { type: 'line', data: { labels: labels60, datasets: [{ label: 'Workers', data: workersHistory60, borderColor: '#0ea5e9', backgroundColor: 'rgba(14, 165, 233, 0.12)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 1 }] }, options: optsLine60 });
        const chartLatency60s = new Chart(document.getElementById('chartLatency60s').getContext('2d'), { type: 'line', data: { labels: labels60, datasets: [{ label: 'Avg Latency ms', data: latencyHistory60, borderColor: '#EE5D50', backgroundColor: 'rgba(238, 93, 80, 0.12)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 1 }] }, options: optsLine60 });
        const chartZkpTps60s = new Chart(document.getElementById('chartZkpTps60s').getContext('2d'), { type: 'line', data: { labels: labels60, datasets: [{ label: 'ZKP TPS', data: zkpTpsHistory60, borderColor: '#7B1FA2', backgroundColor: 'rgba(123, 31, 162, 0.12)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 1 }] }, options: optsLine60 });

        async function updateData() {
            try {
                const response = await fetch(API_URL);
                if (!response.ok) throw new Error("Connection Lost");
                const data = await response.json();

                const em = data.engine_metadata || {};
                const tt = data.traffic_telemetry || {};
                const la = data.latency_analytics_ms || {};
                const cp = data.cryptography_performance || {};
                const sr = data.system_resources_low_level || {};
                const orch = data.orchestration || {};
                const net = data.network || {};
                const zkp = data.zkp_performance || {};
                const ca = data.ca_status || {};
                // Fallback quando API não expõe orchestration/network (ex.: DDD): derivar de system_resources e traffic
                const semTotal = orch.semaphore_slots_total ?? (sr.active_threads ? sr.active_threads * 2 : 128);
                const semInUse = orch.semaphore_in_use ?? 0;
                const semAvail = orch.semaphore_available ?? (semTotal - semInUse);
                const poolMax = orch.thread_pool_max_workers ?? sr.active_threads ?? 64;
                const numProc = orch.num_processes ?? 1;
                const activeWork = orch.active_workers ?? orch.num_processes ?? 1;
                const maxQueue = orch.max_queue_capacity ?? 20000;
                const qCurrent = orch.q_current_size ?? tt.active_connections ?? 0;
                const qPeak = orch.q_peak_size ?? 0;
                const netBytesSent = net.http_bytes_sent ?? 0;
                const netBytesRecv = net.http_bytes_received ?? 0;
                const netIoRead = net.io_read_bytes ?? sr.io_read_bytes ?? 0;
                const netIoWrite = net.io_write_bytes ?? sr.io_write_bytes ?? 0;

                const tps = tt.tps_current || 0;
                const lat = la.average || 0;
                const cpu = (sr.cpu_percent != null && !isNaN(sr.cpu_percent)) ? Number(sr.cpu_percent) : 0;
                const totalReq = tt.total_requests || 0;
                const workers = sr.active_threads || 0;
                const tokensMinted = Number(cp.tokens_minted ?? 0);

                // TPM 30 min: tokens mintados por minuto (um ponto por minuto; janela 30 min; grafico preenche com o tempo)
                const nowMinuteId = Math.floor(Date.now() / 60000);
                if (lastMinuteId !== null && nowMinuteId > lastMinuteId) {
                    const tpmMinute = Math.max(0, tokensMinted - lastMinuteStartTokensMinted);
                    tpmHistory30m.push(tpmMinute);
                    labels30mTpm.push(new Date().toLocaleTimeString());
                    if (tpmHistory30m.length > MAX_TPM_30M) { tpmHistory30m.shift(); labels30mTpm.shift(); }
                }
                lastMinuteId = nowMinuteId;
                lastMinuteStartTokensMinted = tokensMinted;

                // KPIs (all with color: OK / warning / bad)
                document.getElementById('kpi-total-req').innerText = totalReq;
                const tpsEl = document.getElementById('kpi-tps');
                tpsEl.innerText = tps.toFixed(2);
                tpsEl.className = 'kpi-value ' + (tps >= 100 ? 'txt-success' : (tps >= 50 ? 'txt-warning' : 'txt-error'));

                const latEl = document.getElementById('kpi-latency');
                latEl.innerText = fmtMs(lat) + " ms";
                latEl.className = 'kpi-value ' + colorLatency(lat);

                const latPeakEl = document.getElementById('kpi-lat-peak');
                latPeakEl.innerText = fmtMs(la.peak);
                latPeakEl.className = 'kpi-value ' + colorLatency(la.peak);

                const latMinEl = document.getElementById('kpi-lat-min');
                latMinEl.innerText = fmtMs(la.minimum);
                latMinEl.className = 'kpi-value ' + colorLatency(la.minimum);

                const cpuEl = document.getElementById('kpi-cpu');
                cpuEl.innerText = cpu.toFixed(1) + "%";
                cpuEl.className = 'kpi-value ' + colorCpu(cpu);

                const ramEl = document.getElementById('kpi-ram');
                ramEl.innerText = (sr.memory_uss_mb ?? 0).toFixed(2);
                ramEl.className = 'kpi-value';

                document.getElementById('kpi-connections').innerText = tt.active_connections ?? 0;
                document.getElementById('kpi-workers').innerText = workers;
                const srEl = document.getElementById('kpi-success-rate');
                srEl.innerText = tt.success_rate ?? "0%";
                srEl.className = 'kpi-value ' + colorSuccessRate(tt.success_rate ?? "0%");
                document.getElementById('kpi-minted').innerText = cp.tokens_minted ?? 0;

                const cb = tt.circuit_breaker || "CLOSED";
                const kpiCbEl = document.getElementById('kpi-cb');
                kpiCbEl.innerText = cb;
                kpiCbEl.className = 'kpi-value ' + (cb === "CLOSED" ? "txt-success" : "txt-error");
                const cbBox = document.getElementById('cb-icon-box');
                cbBox.style.background = cb === "CLOSED" ? "#E2FFF9" : "#FFF0F0";
                cbBox.style.color = cb === "CLOSED" ? "var(--success)" : "var(--error)";

                document.getElementById('bar-cpu').style.width = Math.min(100, cpu) + "%";
                const valCpuBar = document.getElementById('val-cpu-bar');
                valCpuBar.innerText = cpu.toFixed(1) + "%";
                valCpuBar.className = colorCpu(cpu);
                const vms = sr.memory_vms_mb || 0;
                document.getElementById('bar-ram').style.width = Math.min(100, vms / 2) + "%";
                document.getElementById('val-ram-bar').innerText = vms.toFixed(0);

                const tSuccess = document.getElementById('t-success-rate');
                tSuccess.innerText = tt.success_rate ?? "0%";
                tSuccess.className = colorSuccessRate(tt.success_rate ?? "0%");
                const tDropped = document.getElementById('t-dropped');
                tDropped.innerText = tt.dropped_requests ?? 0;
                tDropped.className = (tt.dropped_requests || 0) > 0 ? 'txt-error' : 'txt-success';
                document.getElementById('t-sockets').innerText = tt.active_connections ?? 0;
                document.getElementById('t-cumulative').innerText = (la.cumulative_processing_time ?? 0).toFixed(2);

                const time = new Date().toLocaleTimeString();
                trafficHistory30m.push(totalReq);
                labels30m.push(time);
                if (trafficHistory30m.length > MAX_HISTORY_30M) { trafficHistory30m.shift(); labels30m.shift(); }
                chartTraffic30m.update('none');

                const zkpTps = Number(zkp.zkp_tps ?? 0);
                tpsHistory60.push(tps);
                workersHistory60.push(workers);
                latencyHistory60.push(lat);
                zkpTpsHistory60.push(zkpTps);
                labels60.push(time);
                if (tpsHistory60.length > MAX_HISTORY_60S) { tpsHistory60.shift(); workersHistory60.shift(); latencyHistory60.shift(); zkpTpsHistory60.shift(); labels60.shift(); }
                chartTps60s.update('none');
                chartTpm30m.update('none');
                chartWorkers60s.update('none');
                chartLatency60s.update('none');
                chartZkpTps60s.update('none');

                document.getElementById('orch-sem-total').innerText = semTotal;
                document.getElementById('orch-sem-in-use').innerText = semInUse;
                document.getElementById('orch-sem-available').innerText = semAvail;
                document.getElementById('orch-pool-max').innerText = poolMax;
                document.getElementById('orch-num-processes').innerText = numProc;
                document.getElementById('orch-active-workers').innerText = activeWork;
                document.getElementById('orch-max-queue').innerText = maxQueue;
                document.getElementById('orch-q-current').innerText = qCurrent;
                document.getElementById('orch-q-peak').innerText = qPeak;

                document.getElementById('net-bytes-sent').innerText = Number(netBytesSent).toLocaleString();
                document.getElementById('net-bytes-recv').innerText = Number(netBytesRecv).toLocaleString();
                document.getElementById('net-io-read').innerText = fmtMb(netIoRead);
                document.getElementById('net-io-write').innerText = fmtMb(netIoWrite);

                // Engine metadata
                document.getElementById('header-engine-name').innerText = em.name || "-";
                document.getElementById('header-arch').innerText = em.architecture || "-";
                document.getElementById('header-python').innerText = em.python_version || "-";
                document.getElementById('meta-name').innerText = em.name || "-";
                document.getElementById('meta-version').innerText = em.version || "-";
                document.getElementById('meta-uptime').innerText = (em.uptime_seconds ?? 0).toFixed(0);
                document.getElementById('meta-arch').innerText = em.architecture || "-";
                document.getElementById('meta-python').innerText = em.python_version || "-";

                // Latency analytics (with color)
                const latAvgEl = document.getElementById('lat-avg');
                latAvgEl.innerText = fmtMs(la.average);
                latAvgEl.className = colorLatency(la.average);
                const latPeakEl2 = document.getElementById('lat-peak');
                latPeakEl2.innerText = fmtMs(la.peak);
                latPeakEl2.className = colorLatency(la.peak);
                const latMinEl2 = document.getElementById('lat-min');
                latMinEl2.innerText = fmtMs(la.minimum);
                latMinEl2.className = colorLatency(la.minimum);
                document.getElementById('lat-cumulative').innerText = (la.cumulative_processing_time ?? 0).toFixed(2);

                // Crypto
                document.getElementById('sec-algo').innerText = cp.algorithm || "-";
                document.getElementById('sec-minted').innerText = cp.tokens_minted ?? 0;
                document.getElementById('sec-signatures').innerText = cp.signatures_generated ?? 0;
                document.getElementById('sec-blocked').innerText = cp.sec_blocked_attempts ?? 0;
                document.getElementById('sec-user').innerText = (cp.last_authenticated_user || "-").toString().slice(0, 20);
                document.getElementById('sec-jti').innerText = (cp.last_issued_jti || "-").toString().slice(0, 24);

                // System resources (CPU with color)
                const sysCpuEl = document.getElementById('sys-cpu');
                sysCpuEl.innerText = (sr.cpu_percent ?? 0).toFixed(2);
                sysCpuEl.className = colorCpu(sr.cpu_percent ?? 0);
                document.getElementById('sys-uss').innerText = (sr.memory_uss_mb ?? 0).toFixed(2);
                document.getElementById('sys-vms').innerText = (sr.memory_vms_mb ?? 0).toFixed(2);
                document.getElementById('sys-fds').innerText = sr.open_fds ?? 0;
                document.getElementById('sys-threads').innerText = sr.active_threads ?? 0;
                document.getElementById('sys-ctx').innerText = sr.voluntary_ctx_switches ?? 0;
                document.getElementById('sys-io-r').innerText = fmtMb(sr.io_read_bytes);
                document.getElementById('sys-io-w').innerText = fmtMb(sr.io_write_bytes);

                // Traffic telemetry (with color)
                document.getElementById('traffic-total').innerText = tt.total_requests ?? 0;
                document.getElementById('traffic-tps').innerText = (tt.tps_current ?? 0).toFixed(2);
                document.getElementById('traffic-conn').innerText = tt.active_connections ?? 0;
                const trSuccess = document.getElementById('traffic-success');
                trSuccess.innerText = tt.success_rate ?? "0%";
                trSuccess.className = colorSuccessRate(tt.success_rate ?? "0%");
                const trDropped = document.getElementById('traffic-dropped');
                trDropped.innerText = tt.dropped_requests ?? 0;
                trDropped.className = (tt.dropped_requests || 0) > 0 ? 'txt-error' : 'txt-success';
                const trCb = document.getElementById('traffic-cb');
                trCb.innerText = tt.circuit_breaker ?? "-";
                trCb.className = (tt.circuit_breaker === "CLOSED") ? "txt-success" : "txt-error";

                document.getElementById('footer-uptime').innerText = "UPTIME: " + (em.uptime_seconds ?? 0).toFixed(0) + "s";
                document.getElementById('footer-version').innerText = em.version || "-";

                // ZKP KPIs
                document.getElementById('kpi-zkp-identities').innerText = zkp.zkp_identities_created ?? 0;
                document.getElementById('kpi-zkp-challenges').innerText = zkp.zkp_challenges_issued ?? 0;
                document.getElementById('kpi-zkp-mints-ok').innerText = zkp.zkp_mints_success ?? 0;
                document.getElementById('kpi-zkp-mints-fail').innerText = zkp.zkp_mints_failed ?? 0;
                const zkpSuccessRate = zkp.zkp_mint_success_rate_pct ?? 100;
                const zkpSuccessEl = document.getElementById('kpi-zkp-success-rate');
                zkpSuccessEl.innerText = zkpSuccessRate.toFixed(1) + "%";
                zkpSuccessEl.className = 'kpi-value ' + (zkpSuccessRate >= 90 ? 'txt-success' : (zkpSuccessRate >= 60 ? 'txt-warning' : 'txt-error'));
                document.getElementById('kpi-zkp-tps').innerText = (zkp.zkp_tps ?? 0).toFixed(2);
                document.getElementById('kpi-ca-total').innerText = ca.ca_identities_total ?? 0;

                // ZKP Performance table
                document.getElementById('zkp-identities').innerText = zkp.zkp_identities_created ?? 0;
                document.getElementById('zkp-challenges').innerText = zkp.zkp_challenges_issued ?? 0;
                document.getElementById('zkp-mints-ok').innerText = zkp.zkp_mints_success ?? 0;
                document.getElementById('zkp-mints-fail').innerText = zkp.zkp_mints_failed ?? 0;
                const zkpTableSuccess = document.getElementById('zkp-success-rate');
                zkpTableSuccess.innerText = (zkp.zkp_mint_success_rate_pct ?? 100).toFixed(1) + "%";
                zkpTableSuccess.className = (zkpSuccessRate >= 90 ? 'txt-success' : (zkpSuccessRate >= 60 ? 'txt-warning' : 'txt-error'));
                document.getElementById('zkp-tps').innerText = (zkp.zkp_tps ?? 0).toFixed(2);
                document.getElementById('zkp-last-id').innerText = (zkp.zkp_last_identity_id || "-").toString().slice(0, 24);

                // CA table
                document.getElementById('ca-identities-total').innerText = ca.ca_identities_total ?? 0;
                document.getElementById('ca-identities-revoked').innerText = ca.ca_identities_revoked ?? 0;
                const caStatusEl = document.getElementById('ca-status');
                caStatusEl.innerText = ca.ca_status ?? "unknown";
                caStatusEl.className = (ca.ca_status === "ok") ? "txt-success" : "txt-error";

                document.getElementById('status-indicator').style.background = "var(--success)";
                document.getElementById('status-text').innerText = "ENGINE OPERATIONAL";
            } catch (err) {
                document.getElementById('status-indicator').style.background = "var(--error)";
                document.getElementById('status-text').innerText = "CONNECTION LOST";
            }
        }

        setInterval(updateData, 1000);
        updateData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("\033[95m" + "="*60)
    print("\033[94m🚀 TITAN MONITOR OMNISCIENCE V9-ZKP — OBSERVABILIDADE DEFINITIVA")
    print("\033[94m📡 Dashboard: http://localhost:5000")
    print("\033[94m📊 Gráficos: Total Traffic 30m | TPS/TPM/Workers/Latency 60s | ZKP TPS 60s | ZKP+CA KPIs")
    print("\033[95m" + "="*60 + "\033[0m")
    app.run(host='0.0.0.0', port=5000, debug=False)
