import os
from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =======================================================================================
# 💎 UI/UX ENGINE: HTML5 + CSS3 + MODERN JS (SINGLE FILE ARCHITECTURE)
# =======================================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titan Monitor Supreme | V6 Performance</title>
    
    <!-- Dependências Externas -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-body: #F4F7FE;
            --white: #FFFFFF;
            --primary-grad: linear-gradient(135deg, #4318FF 0%, #B085FF 100%);
            --secondary-grad: linear-gradient(135deg, #2D1582 0%, #190793 100%);
            --accent: #707EAE;
            --text-main: #1B2559;
            --text-sec: #A3AED0;
            --success: #05CD99;
            --error: #EE5D50;
            --warning: #FFB800;
            --lilac: #868CFF;
            --shadow: 0px 40px 50px -20px rgba(0, 0, 0, 0.08);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }

        body { 
            background-color: var(--bg-body); 
            color: var(--text-main); 
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* --- HEADER --- */
        header {
            background: var(--white);
            padding: 20px 60px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.02);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-icon { 
            width: 40px; height: 40px; background: var(--primary-grad); 
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            color: white; font-size: 20px;
        }
        .logo-text { font-size: 22px; font-weight: 800; color: var(--text-main); letter-spacing: -1px; }

        nav ul { display: flex; list-style: none; gap: 40px; }
        nav ul li { font-weight: 700; color: var(--text-sec); cursor: pointer; transition: 0.3s; font-size: 15px; }
        nav ul li:hover { color: var(--lilac); }
        nav ul li.active { color: #4318FF; border-bottom: 3px solid #4318FF; padding-bottom: 5px; }

        /* --- DASHBOARD WRAPPER --- */
        .dashboard-container {
            padding: 40px 60px;
            flex-grow: 1;
        }

        /* --- TOP KPI ROW (FLEX) --- */
        .kpi-row {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .kpi-card {
            flex: 1;
            min-width: 240px;
            background: var(--white);
            border-radius: 20px;
            padding: 20px;
            box-shadow: var(--shadow);
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .kpi-icon {
            width: 56px; height: 56px; border-radius: 50%;
            background: var(--bg-body);
            display: flex; align-items: center; justify-content: center;
            font-size: 24px; color: #4318FF;
        }

        .kpi-info .label { color: var(--text-sec); font-size: 14px; font-weight: 600; }
        .kpi-info .value { color: var(--text-main); font-size: 24px; font-weight: 800; }

        /* --- GRID SECTIONS --- */
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .section-card {
            background: var(--white);
            border-radius: 24px;
            padding: 30px;
            box-shadow: var(--shadow);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .card-title { font-size: 20px; font-weight: 800; color: var(--text-main); }

        /* --- LIST METRICS (FLEXBOX) --- */
        .metrics-list { display: flex; flex-direction: column; gap: 15px; }
        .metric-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 18px;
            background: var(--bg-body);
            border-radius: 14px;
            font-weight: 600;
        }
        .metric-label { color: var(--text-sec); font-size: 14px; }
        .metric-val { color: var(--text-main); font-size: 14px; font-weight: 700; }

        /* --- CHARTS --- */
        .chart-box { width: 100%; height: 350px; }

        /* --- SYSTEM GRID --- */
        .system-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 30px;
        }

        /* --- FOOTER --- */
        footer {
            background: var(--white);
            padding: 30px 60px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-sec);
            font-size: 14px;
            font-weight: 600;
            border-top: 1px solid rgba(0,0,0,0.05);
        }

        /* --- STATUS INDICATORS --- */
        .badge {
            padding: 6px 14px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
        }
        .badge-success { background: #E6FAF5; color: var(--success); }
        .badge-error { background: #FDEEEE; color: var(--error); }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-body); }
        ::-webkit-scrollbar-thumb { background: var(--text-sec); border-radius: 10px; }

    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <div class="logo-icon"><i class="fa-solid fa-bolt-lightning"></i></div>
            <div class="logo-text">TITAN MONITOR <span style="font-weight: 400; color: var(--accent);">v6.0</span></div>
        </div>
        <nav>
            <ul>
                <li class="active">API OPS ANALYTICS</li>
                <li>USER ANALYTICS</li>
                <li>SECURITY VAULT</li>
                <li>SYS INFRA</li>
            </ul>
        </nav>
        <div id="connection-status" class="badge badge-success">● SYSTEM ONLINE</div>
    </header>

    <div class="dashboard-container">
        
        <!-- ROW 1: TOP KPIs -->
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-icon"><i class="fa-solid fa-globe"></i></div>
                <div class="kpi-info">
                    <div class="label">Total Traffic</div>
                    <div id="stat-total-req" class="value">0</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: var(--lilac);"><i class="fa-solid fa-gauge-high"></i></div>
                <div class="kpi-info">
                    <div class="label">Current TPS</div>
                    <div id="stat-tps" class="value">0.00</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: var(--success);"><i class="fa-solid fa-clock-rotate-left"></i></div>
                <div class="kpi-info">
                    <div class="label">Avg Latency</div>
                    <div id="stat-lat" class="value">0ms</div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon" style="color: var(--warning);"><i class="fa-solid fa-microchip"></i></div>
                <div class="kpi-info">
                    <div class="label">CPU Usage</div>
                    <div id="stat-cpu" class="value">0%</div>
                </div>
            </div>
        </div>

        <!-- ROW 2: MAIN CHARTS & TRAFFIC -->
        <div class="main-grid">
            <div class="section-card">
                <div class="card-header">
                    <div class="card-title">Real-time Performance (TPS)</div>
                    <div class="badge badge-success">Live Stream</div>
                </div>
                <div class="chart-box">
                    <canvas id="tpsChart"></canvas>
                </div>
            </div>

            <div class="section-card">
                <div class="card-header">
                    <div class="card-title">Traffic Analytics</div>
                </div>
                <div class="metrics-list">
                    <div class="metric-item">
                        <span class="metric-label">Success (2xx)</span>
                        <span id="m-2xx" class="metric-val" style="color: var(--success);">0</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Client Errors (4xx)</span>
                        <span id="m-4xx" class="metric-val" style="color: var(--warning);">0</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Server Errors (5xx)</span>
                        <span id="m-5xx" class="metric-val" style="color: var(--error);">0</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Dropped Requests</span>
                        <span id="m-dropped" class="metric-val">0</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Circuit Breaker</span>
                        <span id="m-cb" class="metric-val">CLOSED</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Active Connections</span>
                        <span id="m-active" class="metric-val">0</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- ROW 3: CRYPTO & INFRA -->
        <div class="main-grid">
            <div class="section-card">
                <div class="card-header">
                    <div class="card-title">Cryptography Vault (RSA 512)</div>
                </div>
                <div class="system-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div class="metrics-list">
                        <div class="metric-item"><span class="metric-label">Algorithm</span><span id="c-algo" class="metric-val">-</span></div>
                        <div class="metric-item"><span class="metric-label">Tokens Minted</span><span id="c-minted" class="metric-val">0</span></div>
                        <div class="metric-item"><span class="metric-label">RSA Signatures</span><span id="c-sigs" class="metric-val">0</span></div>
                    </div>
                    <div class="metrics-list">
                        <div class="metric-item"><span class="metric-label">Last User</span><span id="c-user" class="metric-val">none</span></div>
                        <div class="metric-item"><span class="metric-label">Last JTI</span><span id="c-jti" class="metric-val" style="font-size: 10px;">-</span></div>
                    </div>
                </div>
            </div>

            <div class="section-card">
                <div class="card-header">
                    <div class="card-title">Latency Distribution</div>
                </div>
                <div class="metrics-list">
                    <div class="metric-item"><span class="metric-label">Min Latency</span><span id="l-min" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">Peak Latency</span><span id="l-max" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">Total Proc Time</span><span id="l-total" class="metric-val">0</span></div>
                </div>
            </div>
        </div>

        <!-- ROW 4: SYSTEM HARDWARE (ALL INDICATORS) -->
        <div class="section-card">
            <div class="card-header">
                <div class="card-title">System Low-Level Infrastructure</div>
            </div>
            <div class="system-grid">
                <div class="metrics-list">
                    <div class="metric-item"><span class="metric-label">RAM USS</span><span id="s-ram-uss" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">RAM VMS</span><span id="s-ram-vms" class="metric-val">0</span></div>
                </div>
                <div class="metrics-list">
                    <div class="metric-item"><span class="metric-label">Threads</span><span id="s-threads" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">Open FDs</span><span id="s-fds" class="metric-val">0</span></div>
                </div>
                <div class="metrics-list">
                    <div class="metric-item"><span class="metric-label">IO Read</span><span id="s-io-r" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">IO Write</span><span id="s-io-w" class="metric-val">0</span></div>
                </div>
                <div class="metrics-list">
                    <div class="metric-item"><span class="metric-label">Ctx Switches</span><span id="s-ctx" class="metric-val">0</span></div>
                    <div class="metric-item"><span class="metric-label">Uptime</span><span id="s-uptime" class="metric-val">0</span></div>
                </div>
            </div>
        </div>

    </div>

    <footer>
        <div>TITAN ENGINE v6 | POWERED BY O2 DATA SOLUTIONS</div>
        <div>&copy; 2023 | Maringá - PR - Brasil</div>
        <div id="meta-node">Node: -</div>
    </footer>

    <script>
        const STATS_URL = "http://localhost:8000/v6/engine/stats";
        let tpsData = [];
        let timeLabels = [];

        // Chart Init
        const ctx = document.getElementById('tpsChart').getContext('2d');
        const tpsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: 'TPS',
                    data: tpsData,
                    borderColor: '#4318FF',
                    backgroundColor: 'rgba(67, 24, 255, 0.05)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.03)' } }
                }
            }
        });

        async function pullData() {
            try {
                const response = await fetch(STATS_URL);
                if(!response.ok) throw new Error("Offline");
                const d = await response.json();

                // KPI Updates
                document.getElementById('stat-total-req').innerText = d.traffic_telemetry.total_requests;
                document.getElementById('stat-tps').innerText = d.traffic_telemetry.tps_current.toFixed(2);
                document.getElementById('stat-lat').innerText = d.latency_analytics_ms.average.toFixed(2) + "ms";
                document.getElementById('stat-cpu').innerText = d.system_resources_low_level.cpu_percent.toFixed(1) + "%";

                // Traffic Table
                document.getElementById('m-2xx').innerText = d.traffic_telemetry.total_requests - d.traffic_telemetry.dropped_requests; // Simplified for logic
                document.getElementById('m-4xx').innerText = "0"; // API doesn't track 4xx fully yet
                document.getElementById('m-5xx').innerText = "0";
                document.getElementById('m-dropped').innerText = d.traffic_telemetry.dropped_requests;
                document.getElementById('m-cb').innerText = d.traffic_telemetry.circuit_breaker;
                document.getElementById('m-active').innerText = d.traffic_telemetry.active_connections;

                // Crypto Vault
                document.getElementById('c-algo').innerText = d.cryptography_performance.algorithm;
                document.getElementById('c-minted').innerText = d.cryptography_performance.tokens_minted;
                document.getElementById('c-sigs').innerText = d.cryptography_performance.signatures_generated;
                document.getElementById('c-user').innerText = d.cryptography_performance.last_authenticated_user;
                document.getElementById('c-jti').innerText = d.cryptography_performance.last_issued_jti;

                // Latency
                document.getElementById('l-min').innerText = d.latency_analytics_ms.minimum.toFixed(2) + "ms";
                document.getElementById('l-max').innerText = d.latency_analytics_ms.peak.toFixed(2) + "ms";
                document.getElementById('l-total').innerText = d.latency_analytics_ms.cumulative_processing_time + "s";

                // System Low-Level
                document.getElementById('s-ram-uss').innerText = d.system_resources_low_level.memory_uss_mb + " MB";
                document.getElementById('s-ram-vms').innerText = d.system_resources_low_level.memory_vms_mb + " MB";
                document.getElementById('s-threads').innerText = d.system_resources_low_level.active_threads;
                document.getElementById('s-fds').innerText = d.system_resources_low_level.open_fds;
                document.getElementById('s-io-r').innerText = (d.system_resources_low_level.io_read_bytes / 1024 / 1024).toFixed(2) + " MB";
                document.getElementById('s-io-w').innerText = (d.system_resources_low_level.io_write_bytes / 1024 / 1024).toFixed(2) + " MB";
                document.getElementById('s-ctx').innerText = d.system_resources_low_level.voluntary_ctx_switches;
                document.getElementById('s-uptime').innerText = d.engine_metadata.uptime_seconds + "s";

                document.getElementById('meta-node').innerText = "Node: " + d.engine_metadata.architecture;
                document.getElementById('connection-status').className = "badge badge-success";
                document.getElementById('connection-status').innerText = "● SYSTEM ONLINE";

                // Update Chart
                const now = new Date().toLocaleTimeString();
                tpsData.push(d.traffic_telemetry.tps_current);
                timeLabels.push(now);
                if(tpsData.length > 30) { tpsData.shift(); timeLabels.shift(); }
                tpsChart.update();

            } catch (err) {
                document.getElementById('connection-status').className = "badge badge-error";
                document.getElementById('connection-status').innerText = "● SYSTEM OFFLINE";
            }
        }

        setInterval(pullData, 1000);
        pullData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Roda o dashboard na porta 5000 (Localhost)
    print("🚀 [TITAN-DASH] Interface Iniciada em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)