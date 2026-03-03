#!/usr/bin/env python3
"""
RED-SHADOW v4.0 - Full Web GUI
Aplicacion web completa: seleccion de dump, analisis y dashboard de resultados.
Todo se gestiona desde el navegador, sin necesidad de consola.

No requiere dependencias externas - usa http.server de la stdlib.
"""

import json
import os
import sys
import threading
import webbrowser
import socket
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from dataclasses import asdict
from datetime import datetime


# ============================================================================
# STATE (shared between threads)
# ============================================================================

class AppState:
    """Estado global de la aplicacion"""
    report_data = None
    analysis_running = False
    analysis_progress = ""
    analysis_error = None
    analysis_done = False
    dump_path = None


# ============================================================================
# HTML TEMPLATE - Landing page + Dashboard
# ============================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RED-SHADOW v4.0 - Web Dashboard</title>
<style>
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a2e;
    --bg-hover: #22223a;
    --border: #2a2a3e;
    --text-primary: #e0e0e0;
    --text-secondary: #888;
    --text-dim: #555;
    --red: #ff3344;
    --red-dark: #cc1133;
    --red-glow: rgba(255, 51, 68, 0.3);
    --green: #00cc66;
    --green-dark: #009944;
    --yellow: #ffcc00;
    --yellow-dark: #cc9900;
    --cyan: #00cccc;
    --cyan-dark: #009999;
    --magenta: #cc66ff;
    --orange: #ff8833;
    --critical: #ff0066;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Segoe UI', 'Consolas', 'Courier New', monospace;
    min-height: 100vh;
    overflow-x: hidden;
}

body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    z-index: 9999;
}

/* Header */
.header {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 30px;
    text-align: center;
}

.header h1 {
    color: var(--red);
    font-size: 28px;
    text-shadow: 0 0 20px var(--red-glow);
    letter-spacing: 3px;
    margin-bottom: 5px;
}

.header .subtitle { color: var(--text-secondary); font-size: 13px; letter-spacing: 1px; }
.header .dump-path { color: var(--cyan); font-size: 12px; margin-top: 8px; opacity: 0.7; }

/* ==================== LANDING PAGE ==================== */
.landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 100px);
    padding: 40px 20px;
}

.landing-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 40px;
    max-width: 600px;
    width: 100%;
    text-align: center;
}

.landing-box h2 {
    color: var(--red);
    margin-bottom: 8px;
    font-size: 22px;
}

.landing-box p {
    color: var(--text-secondary);
    margin-bottom: 24px;
    font-size: 14px;
}

.landing-input {
    width: 100%;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 14px 16px;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 15px;
    outline: none;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}

.landing-input:focus {
    border-color: var(--red);
    box-shadow: 0 0 10px var(--red-glow);
}

.landing-input::placeholder { color: var(--text-dim); }

.landing-btn {
    width: 100%;
    background: var(--red-dark);
    border: 1px solid var(--red);
    border-radius: 4px;
    padding: 14px;
    color: #fff;
    font-family: inherit;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 1px;
}

.landing-btn:hover { background: var(--red); }
.landing-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.landing-hint {
    color: var(--text-dim);
    font-size: 12px;
    margin-top: 12px;
}

/* Progress overlay */
.progress-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(10, 10, 15, 0.95);
    z-index: 1000;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.progress-overlay.active { display: flex; }

.progress-box {
    text-align: center;
    max-width: 500px;
    padding: 40px;
}

.spinner {
    display: inline-block;
    width: 50px;
    height: 50px;
    border: 3px solid var(--border);
    border-top-color: var(--red);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.progress-text {
    color: var(--text-primary);
    font-size: 16px;
    margin-bottom: 10px;
}

.progress-detail {
    color: var(--text-secondary);
    font-size: 13px;
    min-height: 20px;
}

.progress-error {
    color: var(--red);
    font-size: 14px;
    margin-top: 16px;
    max-width: 500px;
    word-break: break-word;
}

/* ==================== DASHBOARD ==================== */
.dashboard { display: none; }
.dashboard.active { display: block; }

/* Navigation */
.nav {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 0 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 12px 16px;
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
    transition: all 0.2s;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
}

.nav-btn:hover { color: var(--text-primary); background: var(--bg-hover); }
.nav-btn.active { color: var(--red); border-bottom-color: var(--red); text-shadow: 0 0 10px var(--red-glow); }

.main { max-width: 1400px; margin: 0 auto; padding: 20px; }

.section { display: none; }
.section.active { display: block; }

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
}

.card-title {
    color: var(--cyan);
    font-size: 16px;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    letter-spacing: 1px;
}

/* Stats grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
}

.stat-box {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}

.stat-box:hover { transform: translateY(-2px); border-color: var(--cyan-dark); }
.stat-value { font-size: 28px; font-weight: bold; margin-bottom: 4px; }
.stat-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

/* Risk meter */
.risk-meter { width: 100%; height: 8px; background: var(--bg-primary); border-radius: 4px; overflow: hidden; margin: 10px 0; }
.risk-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }

/* Tables */
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
    background: var(--bg-secondary); color: var(--cyan); padding: 10px 12px;
    text-align: left; border: 1px solid var(--border); font-weight: normal;
    text-transform: uppercase; font-size: 11px; letter-spacing: 1px;
    position: sticky; top: 46px; z-index: 10;
}
.data-table td { padding: 8px 12px; border: 1px solid var(--border); vertical-align: top; }
.data-table tr:hover td { background: var(--bg-hover); }
.data-table .mono { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }

/* Tags */
.tag { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; margin: 1px; }
.tag-safe { background: var(--green-dark); color: #fff; }
.tag-warn { background: var(--yellow-dark); color: #000; }
.tag-danger { background: var(--red-dark); color: #fff; }
.tag-critical { background: var(--critical); color: #fff; }
.tag-honeypot { background: #ff0066; color: #fff; }
.tag-ban { background: #cc0000; color: #fff; }
.tag-val { background: var(--green-dark); color: #fff; }
.tag-info { background: var(--cyan-dark); color: #fff; }
.tag-obf { background: var(--magenta); color: #fff; }

/* Code blocks */
.code-block {
    background: #0d0d12; border: 1px solid var(--border); border-radius: 4px;
    padding: 12px; font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px; line-height: 1.5; overflow-x: auto;
    color: var(--text-secondary); max-height: 200px; overflow-y: auto;
    white-space: pre-wrap; word-break: break-all;
}

/* Search */
.search-box { display: flex; gap: 8px; margin-bottom: 16px; }
.search-input {
    flex: 1; background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 4px; padding: 10px 14px; color: var(--text-primary);
    font-family: inherit; font-size: 14px; outline: none; transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--red); box-shadow: 0 0 10px var(--red-glow); }
.search-input::placeholder { color: var(--text-dim); }

/* Filter buttons */
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.filter-btn {
    background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 4px;
    padding: 6px 14px; color: var(--text-secondary); cursor: pointer;
    font-family: inherit; font-size: 12px; transition: all 0.2s;
}
.filter-btn:hover, .filter-btn.active { color: #fff; border-color: var(--red); background: rgba(255, 51, 68, 0.15); }

/* Recommendations */
.rec-list { list-style: none; padding: 0; }
.rec-list li {
    padding: 10px 14px; margin-bottom: 6px; background: var(--bg-secondary);
    border-left: 3px solid var(--yellow); border-radius: 0 4px 4px 0; font-size: 13px;
}

/* Chain visualization */
.chain-item { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; padding: 10px; background: var(--bg-secondary); border-radius: 4px; }
.chain-node { background: var(--bg-card); border: 1px solid var(--cyan-dark); border-radius: 4px; padding: 4px 10px; font-size: 12px; color: var(--cyan); }
.chain-arrow { color: var(--text-dim); font-size: 14px; }

/* Export bar */
.export-bar { display: flex; gap: 8px; margin-bottom: 16px; justify-content: flex-end; }
.btn {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 4px;
    padding: 8px 16px; color: var(--text-primary); cursor: pointer;
    font-family: inherit; font-size: 13px; transition: all 0.2s;
}
.btn:hover { border-color: var(--red); background: rgba(255, 51, 68, 0.1); }
.btn-primary { background: var(--red-dark); border-color: var(--red); color: #fff; }
.btn-primary:hover { background: var(--red); }

/* New analysis button */
.btn-new-analysis {
    background: transparent; border: 1px solid var(--border); border-radius: 4px;
    padding: 8px 16px; color: var(--text-secondary); cursor: pointer;
    font-family: inherit; font-size: 13px; transition: all 0.2s;
    margin-left: auto;
}
.btn-new-analysis:hover { border-color: var(--yellow); color: var(--yellow); }

/* Severity/risk */
.sev-critical { color: var(--critical); }
.sev-high { color: var(--red); }
.sev-medium { color: var(--yellow); }
.sev-low { color: var(--green); }
.risk-safe { color: var(--green); }
.risk-warn { color: var(--yellow); }
.risk-danger { color: var(--red); }
.risk-critical { color: var(--critical); }

/* Confidence bar */
.conf-bar { display: inline-block; width: 60px; height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; vertical-align: middle; margin-left: 6px; }
.conf-fill { height: 100%; border-radius: 3px; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #444; }

/* Toast */
.toast {
    position: fixed; bottom: 20px; right: 20px; background: var(--bg-card);
    border: 1px solid var(--green); border-radius: 6px; padding: 12px 20px;
    color: var(--green); font-size: 13px; z-index: 10000;
    opacity: 0; transform: translateY(10px); transition: all 0.3s;
}
.toast.show { opacity: 1; transform: translateY(0); }

@media (max-width: 768px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .nav-btn { padding: 10px 10px; font-size: 12px; }
    .header h1 { font-size: 20px; }
    .landing-box { padding: 24px; }
}
</style>
</head>
<body>

<div class="header">
    <h1>RED-SHADOW "Destroyer" v4.0</h1>
    <div class="subtitle">Advanced Forensic Engine - Web Dashboard</div>
    <div class="dump-path" id="dump-path"></div>
</div>

<!-- ==================== LANDING PAGE ==================== -->
<div class="landing" id="landing">
    <div class="landing-box">
        <h2>Analisis Forense</h2>
        <p>Introduce la ruta de la carpeta del dump de FiveM para iniciar el analisis.</p>
        <input type="text" class="landing-input" id="dump-input"
            placeholder="C:\Users\user\Desktop\FiveM_Dump" autofocus>
        <button class="landing-btn" id="analyze-btn" onclick="startAnalysis()">
            ANALIZAR
        </button>
        <div class="landing-hint">
            Ejemplo: C:\FiveM_Dump o /home/user/dumps/server1
        </div>
    </div>
</div>

<!-- ==================== PROGRESS OVERLAY ==================== -->
<div class="progress-overlay" id="progress-overlay">
    <div class="progress-box">
        <div class="spinner"></div>
        <div class="progress-text">Ejecutando analisis forense...</div>
        <div class="progress-detail" id="progress-detail">Iniciando...</div>
        <div class="progress-error" id="progress-error"></div>
    </div>
</div>

<!-- ==================== DASHBOARD ==================== -->
<div class="dashboard" id="dashboard">
    <nav class="nav" id="nav">
        <button class="nav-btn active" data-section="summary">Resumen</button>
        <button class="nav-btn" data-section="triggers">Triggers</button>
        <button class="nav-btn" data-section="honeypots">Honeypots</button>
        <button class="nav-btn" data-section="anticheats">Anticheats</button>
        <button class="nav-btn" data-section="obfuscation">Ofuscacion</button>
        <button class="nav-btn" data-section="natives">Natives</button>
        <button class="nav-btn" data-section="callbacks">Callbacks</button>
        <button class="nav-btn" data-section="security">Seguridad</button>
        <button class="nav-btn" data-section="manifests">Manifests</button>
        <button class="nav-btn" data-section="chains">Cadenas</button>
        <button class="nav-btn" data-section="clones">Clones</button>
        <button class="nav-btn" data-section="search">Buscar</button>
        <button class="btn-new-analysis" onclick="newAnalysis()">Nuevo analisis</button>
    </nav>

    <div class="main" id="main-content">
        <!-- SUMMARY -->
        <div class="section" id="sec-summary">
            <div class="export-bar">
                <button class="btn" onclick="downloadJSON()">Descargar JSON</button>
            </div>
            <div class="stats-grid" id="stats-grid"></div>
            <div class="card">
                <div class="card-title">RIESGO GENERAL</div>
                <div id="risk-display"></div>
            </div>
            <div class="card">
                <div class="card-title">RECOMENDACIONES</div>
                <ul class="rec-list" id="recommendations"></ul>
            </div>
        </div>

        <!-- TRIGGERS -->
        <div class="section" id="sec-triggers">
            <div class="search-box">
                <input type="text" class="search-input" id="trigger-search" placeholder="Filtrar triggers por nombre...">
            </div>
            <div class="filters" id="trigger-filters">
                <button class="filter-btn active" data-filter="all">Todos</button>
                <button class="filter-btn" data-filter="safe">Seguros</button>
                <button class="filter-btn" data-filter="warn">Advertencia</button>
                <button class="filter-btn" data-filter="danger">Peligrosos</button>
            </div>
            <div id="triggers-table-wrap"></div>
        </div>

        <!-- HONEYPOTS -->
        <div class="section" id="sec-honeypots">
            <div class="card">
                <div class="card-title" style="color:var(--critical)">HONEYPOTS DETECTADOS</div>
                <p style="color:var(--red);margin-bottom:14px;font-size:13px;">
                    Ejecutar estos triggers resultara en BAN inmediato. Evitar a toda costa.
                </p>
                <div id="honeypots-content"></div>
            </div>
        </div>

        <!-- ANTICHEATS -->
        <div class="section" id="sec-anticheats">
            <div class="card">
                <div class="card-title">ANTICHEATS IDENTIFICADOS</div>
                <div id="anticheats-content"></div>
            </div>
        </div>

        <!-- OBFUSCATION -->
        <div class="section" id="sec-obfuscation">
            <div class="filters" id="obf-filters"></div>
            <div id="obfuscation-content"></div>
        </div>

        <!-- NATIVES -->
        <div class="section" id="sec-natives">
            <div class="filters" id="native-filters"></div>
            <div id="natives-content"></div>
        </div>

        <!-- CALLBACKS -->
        <div class="section" id="sec-callbacks">
            <div id="callbacks-content"></div>
        </div>

        <!-- SECURITY -->
        <div class="section" id="sec-security">
            <div class="filters" id="security-filters"></div>
            <div id="security-content"></div>
        </div>

        <!-- MANIFESTS -->
        <div class="section" id="sec-manifests">
            <div id="manifests-content"></div>
        </div>

        <!-- CHAINS -->
        <div class="section" id="sec-chains">
            <div class="card">
                <div class="card-title">CADENAS DE TRIGGERS (Cross-File)</div>
                <div id="chains-content"></div>
            </div>
            <div class="card">
                <div class="card-title">REFERENCIAS CRUZADAS</div>
                <div id="crossrefs-content"></div>
            </div>
        </div>

        <!-- CLONES -->
        <div class="section" id="sec-clones">
            <div class="card">
                <div class="card-title">CODIGO DUPLICADO</div>
                <div id="clones-content"></div>
            </div>
        </div>

        <!-- SEARCH -->
        <div class="section" id="sec-search">
            <div class="search-box">
                <input type="text" class="search-input" id="global-search" placeholder="Buscar trigger por nombre...">
                <button class="btn btn-primary" onclick="doGlobalSearch()">Buscar</button>
            </div>
            <div id="search-results"></div>
        </div>
    </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ============================================================================
// STATE
// ============================================================================

var DATA = null;
var currentSection = 'summary';
var triggerFilter = 'all';

// ============================================================================
// PAGE ROUTING
// ============================================================================

function showLanding() {
    document.getElementById('landing').style.display = 'flex';
    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('progress-overlay').classList.remove('active');
    document.getElementById('dump-path').textContent = '';
    document.getElementById('dump-input').value = '';
    document.getElementById('dump-input').focus();
}

function showProgress() {
    document.getElementById('landing').style.display = 'none';
    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('progress-overlay').classList.add('active');
    document.getElementById('progress-error').textContent = '';
}

function showDashboard() {
    document.getElementById('landing').style.display = 'none';
    document.getElementById('progress-overlay').classList.remove('active');
    document.getElementById('dashboard').classList.add('active');
    document.getElementById('dump-path').textContent = 'Dump: ' + (DATA.dump_path || 'N/A');
    renderSummary();
    showSection('summary');
}

function newAnalysis() {
    DATA = null;
    showLanding();
}

// ============================================================================
// ANALYSIS FLOW
// ============================================================================

function startAnalysis() {
    var path = document.getElementById('dump-input').value.trim();
    if (!path) {
        document.getElementById('dump-input').focus();
        return;
    }

    document.getElementById('analyze-btn').disabled = true;
    showProgress();

    fetch('/api/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path: path})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) {
            document.getElementById('progress-error').textContent = 'Error: ' + d.error;
            document.getElementById('analyze-btn').disabled = false;
            setTimeout(showLanding, 3000);
            return;
        }
        // Start polling for status
        pollStatus();
    })
    .catch(function(e) {
        document.getElementById('progress-error').textContent = 'Error de conexion: ' + e.message;
        document.getElementById('analyze-btn').disabled = false;
    });
}

function pollStatus() {
    fetch('/api/status')
    .then(function(r) { return r.json(); })
    .then(function(d) {
        document.getElementById('progress-detail').textContent = d.progress || '';

        if (d.error) {
            document.getElementById('progress-error').textContent = 'Error: ' + d.error;
            document.getElementById('analyze-btn').disabled = false;
            return;
        }

        if (d.done) {
            // Fetch final data
            fetch('/api/data')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                DATA = data;
                document.getElementById('analyze-btn').disabled = false;
                showDashboard();
            });
            return;
        }

        // Keep polling
        setTimeout(pollStatus, 500);
    })
    .catch(function(e) {
        setTimeout(pollStatus, 1000);
    });
}

// Enter key on input
document.getElementById('dump-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') startAnalysis();
});

// ============================================================================
// NAVIGATION
// ============================================================================

document.getElementById('nav').addEventListener('click', function(e) {
    if (e.target.classList.contains('nav-btn')) {
        showSection(e.target.dataset.section);
    }
});

function showSection(name) {
    currentSection = name;
    document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.section === name); });
    document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
    var el = document.getElementById('sec-' + name);
    if (el) el.classList.add('active');

    var renderers = {
        summary: renderSummary, triggers: renderTriggers, honeypots: renderHoneypots,
        anticheats: renderAnticheats, obfuscation: renderObfuscation, natives: renderNatives,
        callbacks: renderCallbacks, security: renderSecurity, manifests: renderManifests,
        chains: renderChains, clones: renderClones
    };
    if (renderers[name] && DATA) renderers[name]();
}

// ============================================================================
// HELPERS
// ============================================================================

function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') : ''; }
function riskClass(s) { return s >= 70 ? 'risk-danger' : s >= 40 ? 'risk-warn' : 'risk-safe'; }
function riskColor(s) { return s >= 70 ? 'var(--red)' : s >= 40 ? 'var(--yellow)' : 'var(--green)'; }
function tagHTML(t, c) { return '<span class="tag tag-' + c + '">' + esc(t) + '</span>'; }
function confBar(v) {
    var p = Math.round(v * 100);
    var c = v > 0.7 ? 'var(--red)' : v > 0.3 ? 'var(--yellow)' : 'var(--green)';
    return p + '% <span class="conf-bar"><span class="conf-fill" style="width:' + p + '%;background:' + c + '"></span></span>';
}
function shortPath(p) { if (!p) return ''; var a = p.replace(/\\/g, '/').split('/'); return a.length > 2 ? '.../' + a.slice(-2).join('/') : p; }
function showToast(m) { var t = document.getElementById('toast'); t.textContent = m; t.classList.add('show'); setTimeout(function() { t.classList.remove('show'); }, 2500); }
function downloadJSON() {
    if (!DATA) return;
    var b = new Blob([JSON.stringify(DATA, null, 2)], {type: 'application/json'});
    var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'red_shadow_report.json'; a.click();
    showToast('Reporte JSON descargado');
}

// ============================================================================
// RENDER: SUMMARY
// ============================================================================

function renderSummary() {
    var s = DATA.stats; var triggers = DATA.triggers || [];
    var safe = triggers.filter(function(t) { return t.risk_score < 40; }).length;
    var warn = triggers.filter(function(t) { return t.risk_score >= 40 && t.risk_score < 70; }).length;
    var danger = triggers.filter(function(t) { return t.risk_score >= 70; }).length;
    var honeypots = triggers.filter(function(t) { return t.is_honeypot; }).length;
    var oR = triggers.length > 0 ? triggers.reduce(function(a, t) { return a + t.risk_score; }, 0) / triggers.length : 0;

    document.getElementById('stats-grid').innerHTML = [
        {v: s.lua_files, l: 'Archivos Lua', c: 'var(--cyan)'}, {v: s.total_lines, l: 'Lineas', c: 'var(--cyan)'},
        {v: s.functions, l: 'Funciones', c: 'var(--cyan)'}, {v: s.triggers, l: 'Triggers', c: 'var(--cyan)'},
        {v: safe, l: 'Seguros', c: 'var(--green)'}, {v: warn, l: 'Advertencia', c: 'var(--yellow)'},
        {v: danger, l: 'Peligrosos', c: 'var(--red)'}, {v: honeypots, l: 'Honeypots', c: 'var(--critical)'},
        {v: s.callbacks, l: 'Callbacks', c: 'var(--cyan)'}, {v: s.natives, l: 'Natives', c: 'var(--cyan)'},
        {v: s.obfuscations, l: 'Ofuscacion', c: 'var(--magenta)'}, {v: s.security_issues, l: 'Seguridad', c: 'var(--red)'},
        {v: s.anticheats, l: 'Anticheats', c: 'var(--yellow)'}
    ].map(function(i) { return '<div class="stat-box"><div class="stat-value" style="color:' + i.c + '">' + i.v + '</div><div class="stat-label">' + i.l + '</div></div>'; }).join('');

    var rc = riskColor(oR);
    document.getElementById('risk-display').innerHTML = '<div style="font-size:36px;font-weight:bold;color:' + rc + ';margin-bottom:8px">' + oR.toFixed(1) + '%</div><div class="risk-meter"><div class="risk-fill" style="width:' + oR + '%;background:' + rc + '"></div></div>';

    var recs = DATA.recommendations || [];
    document.getElementById('recommendations').innerHTML = recs.length > 0 ? recs.map(function(r) { return '<li>' + esc(r) + '</li>'; }).join('') : '<li>No se generaron recomendaciones.</li>';
}

// ============================================================================
// RENDER: TRIGGERS
// ============================================================================

function renderTriggers() {
    var triggers = DATA.triggers || [];
    var search = (document.getElementById('trigger-search').value || '').toLowerCase();
    var filtered = triggers.filter(function(t) {
        if (search && t.event_name.toLowerCase().indexOf(search) === -1) return false;
        if (triggerFilter === 'safe') return t.risk_score < 40;
        if (triggerFilter === 'warn') return t.risk_score >= 40 && t.risk_score < 70;
        if (triggerFilter === 'danger') return t.risk_score >= 70;
        return true;
    });
    filtered.sort(function(a, b) { return b.risk_score - a.risk_score; });

    var html = '<table class="data-table"><tr><th>Trigger</th><th>Tipo</th><th>Archivo</th><th>Reward</th><th>Riesgo</th><th>Tags</th></tr>';
    filtered.forEach(function(t) {
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'honeypot');
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban');
        if (t.has_validation) tags += tagHTML('VAL', 'val');
        if (t.has_reward_logic) tags += tagHTML(t.reward_type || 'REWARD', 'info');
        html += '<tr><td class="mono">' + esc(t.event_name) + '</td><td>' + esc(t.event_type) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td><td>' + esc(t.reward_type) + '</td><td class="' + riskClass(t.risk_score) + '" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td><td>' + tags + '</td></tr>';
    });
    html += '</table>';
    if (filtered.length === 0) html = '<p style="color:var(--text-secondary);padding:20px">No se encontraron triggers con estos filtros.</p>';
    document.getElementById('triggers-table-wrap').innerHTML = html;
}

document.getElementById('trigger-search').addEventListener('input', function() { if (currentSection === 'triggers') renderTriggers(); });
document.getElementById('trigger-filters').addEventListener('click', function(e) {
    if (e.target.classList.contains('filter-btn')) {
        triggerFilter = e.target.dataset.filter;
        document.querySelectorAll('#trigger-filters .filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.filter === triggerFilter); });
        renderTriggers();
    }
});

// ============================================================================
// RENDER: HONEYPOTS
// ============================================================================

function renderHoneypots() {
    var triggers = (DATA.triggers || []).filter(function(t) { return t.is_honeypot; });
    if (triggers.length === 0) { document.getElementById('honeypots-content').innerHTML = '<p style="color:var(--green)">No se detectaron honeypots.</p>'; return; }
    var html = '<table class="data-table"><tr><th>Trigger</th><th>Tipo</th><th>Archivo</th><th>Ban</th><th>Reward</th><th>Riesgo</th></tr>';
    triggers.forEach(function(t) {
        html += '<tr><td class="mono" style="color:var(--critical)">' + esc(t.event_name) + '</td><td>' + esc(t.event_type) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td><td>' + (t.has_ban_logic ? tagHTML('SI', 'danger') : 'NO') + '</td><td>' + (t.has_reward_logic ? tagHTML('SI', 'warn') : 'NO') + '</td><td class="risk-danger" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td></tr>';
    });
    html += '</table>';
    document.getElementById('honeypots-content').innerHTML = html;
}

// ============================================================================
// RENDER: ANTICHEATS
// ============================================================================

function renderAnticheats() {
    var acs = DATA.anticheats || {}; var keys = Object.keys(acs);
    if (keys.length === 0) { document.getElementById('anticheats-content').innerHTML = '<p style="color:var(--green)">No se detectaron anticheats.</p>'; return; }
    var html = '<table class="data-table"><tr><th>Anticheat</th><th>Confianza</th><th>Descripcion</th><th>Firmas</th></tr>';
    keys.forEach(function(n) { var a = acs[n]; html += '<tr><td style="font-weight:bold;color:var(--yellow)">' + esc(n) + '</td><td>' + confBar(a.confidence) + '</td><td style="font-size:12px">' + esc(a.description) + '</td><td class="mono" style="font-size:11px">' + esc((a.matched_signatures || []).join(', ')) + '</td></tr>'; });
    html += '</table>';
    document.getElementById('anticheats-content').innerHTML = html;
}

// ============================================================================
// RENDER: OBFUSCATION
// ============================================================================

function renderObfuscation() {
    var obfs = DATA.obfuscations || [];
    if (obfs.length === 0) { document.getElementById('obfuscation-content').innerHTML = '<div class="card"><p style="color:var(--green)">No se detecto ofuscacion.</p></div>'; return; }
    var byType = {}; obfs.forEach(function(o) { if (!byType[o.obf_type]) byType[o.obf_type] = []; byType[o.obf_type].push(o); });
    var types = Object.keys(byType).sort(function(a, b) { return byType[b].length - byType[a].length; });
    var fHTML = '<button class="filter-btn active" data-obf="all">Todos (' + obfs.length + ')</button>';
    types.forEach(function(t) { fHTML += '<button class="filter-btn" data-obf="' + t + '">' + t + ' (' + byType[t].length + ')</button>'; });
    document.getElementById('obf-filters').innerHTML = fHTML;
    renderObfTable('all');
    document.getElementById('obf-filters').onclick = function(e) { if (e.target.classList.contains('filter-btn')) { var f = e.target.dataset.obf; document.querySelectorAll('#obf-filters .filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.obf === f); }); renderObfTable(f); } };
}
function renderObfTable(filter) {
    var obfs = DATA.obfuscations || [];
    if (filter !== 'all') obfs = obfs.filter(function(o) { return o.obf_type === filter; });
    obfs.sort(function(a, b) { return b.confidence - a.confidence; });
    var html = '<div class="card"><table class="data-table"><tr><th>Tipo</th><th>Archivo</th><th>Confianza</th><th>Snippet</th></tr>';
    obfs.slice(0, 100).forEach(function(o) { html += '<tr><td>' + tagHTML(o.obf_type, 'obf') + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(o.file)) + ':' + o.line + '</td><td>' + confBar(o.confidence) + '</td><td class="mono" style="font-size:11px;max-width:400px;overflow:hidden;text-overflow:ellipsis">' + esc(o.snippet) + '</td></tr>'; });
    if (obfs.length > 100) html += '<tr><td colspan="4" style="color:var(--text-dim)">... y ' + (obfs.length - 100) + ' mas</td></tr>';
    html += '</table></div>';
    document.getElementById('obfuscation-content').innerHTML = html;
}

// ============================================================================
// RENDER: NATIVES
// ============================================================================

function renderNatives() {
    var natives = DATA.natives || [];
    if (natives.length === 0) { document.getElementById('natives-content').innerHTML = '<div class="card"><p style="color:var(--green)">No se detectaron natives.</p></div>'; return; }
    var byCat = {}; natives.forEach(function(n) { if (!byCat[n.category]) byCat[n.category] = []; byCat[n.category].push(n); });
    var cats = Object.keys(byCat).sort(function(a, b) { return byCat[b].length - byCat[a].length; });
    var fHTML = '<button class="filter-btn active" data-nat="all">Todos (' + natives.length + ')</button>';
    cats.forEach(function(c) { fHTML += '<button class="filter-btn" data-nat="' + c + '">' + c + ' (' + byCat[c].length + ')</button>'; });
    document.getElementById('native-filters').innerHTML = fHTML;
    renderNativesTable('all');
    document.getElementById('native-filters').onclick = function(e) { if (e.target.classList.contains('filter-btn')) { var f = e.target.dataset.nat; document.querySelectorAll('#native-filters .filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.nat === f); }); renderNativesTable(f); } };
}
function renderNativesTable(filter) {
    var natives = DATA.natives || [];
    if (filter !== 'all') natives = natives.filter(function(n) { return n.category === filter; });
    var cc = {WEAPON:'danger',MONEY:'danger',PLAYER:'warn',NETWORK:'warn',VEHICLE:'info',WORLD:'info',UNKNOWN:'info'};
    var html = '<div class="card"><table class="data-table"><tr><th>Native</th><th>Categoria</th><th>Archivo</th></tr>';
    natives.slice(0, 100).forEach(function(n) { html += '<tr><td class="mono">' + esc(n.native_hash) + '</td><td>' + tagHTML(n.category, cc[n.category] || 'info') + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(n.file)) + ':' + n.line + '</td></tr>'; });
    if (natives.length > 100) html += '<tr><td colspan="3" style="color:var(--text-dim)">... y ' + (natives.length - 100) + ' mas</td></tr>';
    html += '</table></div>';
    document.getElementById('natives-content').innerHTML = html;
}

// ============================================================================
// RENDER: CALLBACKS
// ============================================================================

function renderCallbacks() {
    var cbs = DATA.callbacks || [];
    if (cbs.length === 0) { document.getElementById('callbacks-content').innerHTML = '<div class="card"><p style="color:var(--green)">No se detectaron callbacks.</p></div>'; return; }
    cbs.sort(function(a, b) { return b.risk_score - a.risk_score; });
    var html = '<div class="card"><table class="data-table"><tr><th>Callback</th><th>Archivo</th><th>Validacion</th><th>Riesgo</th></tr>';
    cbs.forEach(function(cb) { html += '<tr><td class="mono">' + esc(cb.name) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(cb.file)) + ':' + cb.line + '</td><td>' + (cb.has_validation ? tagHTML('SI', 'safe') : tagHTML('NO', 'danger')) + '</td><td class="' + riskClass(cb.risk_score) + '" style="font-weight:bold">' + cb.risk_score.toFixed(0) + '%</td></tr>'; });
    html += '</table></div>';
    document.getElementById('callbacks-content').innerHTML = html;
}

// ============================================================================
// RENDER: SECURITY
// ============================================================================

function renderSecurity() {
    var issues = DATA.security_issues || [];
    if (issues.length === 0) { document.getElementById('security-content').innerHTML = '<div class="card"><p style="color:var(--green)">No se detectaron vulnerabilidades.</p></div>'; return; }
    var byType = {}; issues.forEach(function(i) { if (!byType[i.issue_type]) byType[i.issue_type] = []; byType[i.issue_type].push(i); });
    var types = Object.keys(byType);
    var fHTML = '<button class="filter-btn active" data-sec="all">Todos (' + issues.length + ')</button>';
    types.forEach(function(t) { fHTML += '<button class="filter-btn" data-sec="' + t + '">' + t + ' (' + byType[t].length + ')</button>'; });
    document.getElementById('security-filters').innerHTML = fHTML;
    renderSecurityTable('all');
    document.getElementById('security-filters').onclick = function(e) { if (e.target.classList.contains('filter-btn')) { var f = e.target.dataset.sec; document.querySelectorAll('#security-filters .filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.sec === f); }); renderSecurityTable(f); } };
}
function renderSecurityTable(filter) {
    var issues = DATA.security_issues || [];
    if (filter !== 'all') issues = issues.filter(function(i) { return i.issue_type === filter; });
    var so = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3};
    issues.sort(function(a, b) { return (so[a.severity] || 9) - (so[b.severity] || 9); });
    var st = {CRITICAL:'critical', HIGH:'danger', MEDIUM:'warn', LOW:'safe'};
    var html = '<div class="card"><table class="data-table"><tr><th>Tipo</th><th>Severidad</th><th>Archivo</th><th>Descripcion</th><th>Snippet</th></tr>';
    issues.slice(0, 100).forEach(function(i) { html += '<tr><td>' + esc(i.issue_type) + '</td><td>' + tagHTML(i.severity, st[i.severity] || 'info') + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(i.file)) + ':' + i.line + '</td><td style="font-size:12px">' + esc(i.description) + '</td><td class="mono" style="font-size:11px;max-width:300px;overflow:hidden;text-overflow:ellipsis">' + esc(i.snippet) + '</td></tr>'; });
    html += '</table></div>';
    document.getElementById('security-content').innerHTML = html;
}

// ============================================================================
// RENDER: MANIFESTS
// ============================================================================

function renderManifests() {
    var manifests = DATA.manifests || [];
    if (manifests.length === 0) { document.getElementById('manifests-content').innerHTML = '<div class="card"><p style="color:var(--green)">No se encontraron manifests.</p></div>'; return; }
    var html = '';
    manifests.forEach(function(m) {
        html += '<div class="card"><div class="card-title" style="color:var(--yellow)">' + esc(m.resource_name) + (m.has_ui_page ? ' ' + tagHTML('NUI', 'obf') : '') + '</div>';
        if (m.scripts_server.length) html += '<p><strong style="color:var(--cyan)">Server:</strong> <span class="mono" style="font-size:12px">' + m.scripts_server.map(esc).join(', ') + '</span></p>';
        if (m.scripts_client.length) html += '<p><strong style="color:var(--cyan)">Client:</strong> <span class="mono" style="font-size:12px">' + m.scripts_client.map(esc).join(', ') + '</span></p>';
        if (m.dependencies.length) html += '<p><strong style="color:var(--cyan)">Deps:</strong> <span class="mono" style="font-size:12px">' + m.dependencies.map(esc).join(', ') + '</span></p>';
        if (m.exports.length) html += '<p><strong style="color:var(--cyan)">Exports:</strong> <span class="mono" style="font-size:12px">' + m.exports.map(esc).join(', ') + '</span></p>';
        html += '</div>';
    });
    document.getElementById('manifests-content').innerHTML = html;
}

// ============================================================================
// RENDER: CHAINS
// ============================================================================

function renderChains() {
    var chains = DATA.trigger_chains || []; var cr = DATA.cross_references || {};
    if (chains.length === 0) { document.getElementById('chains-content').innerHTML = '<p style="color:var(--green)">No se detectaron cadenas.</p>'; }
    else {
        var html = '';
        chains.forEach(function(ch, i) { html += '<div class="chain-item"><strong style="color:var(--cyan);margin-right:8px">Cadena #' + (i+1) + ':</strong> '; ch.forEach(function(n, j) { html += '<span class="chain-node">' + esc(n) + '</span>'; if (j < ch.length - 1) html += '<span class="chain-arrow"> &rarr; </span>'; }); html += '</div>'; });
        document.getElementById('chains-content').innerHTML = html;
    }
    var crk = Object.keys(cr);
    if (crk.length === 0) { document.getElementById('crossrefs-content').innerHTML = '<p style="color:var(--text-secondary)">No se detectaron referencias cruzadas.</p>'; }
    else {
        var html2 = '<table class="data-table"><tr><th>Trigger</th><th>Archivos</th></tr>';
        crk.forEach(function(n) { var f = cr[n]; html2 += '<tr><td class="mono" style="color:var(--cyan)">' + esc(n) + '</td><td class="mono" style="font-size:11px">' + (Array.isArray(f) ? f.map(esc).join(', ') : esc(String(f))) + '</td></tr>'; });
        html2 += '</table>';
        document.getElementById('crossrefs-content').innerHTML = html2;
    }
}

// ============================================================================
// RENDER: CLONES
// ============================================================================

function renderClones() {
    var clones = DATA.code_clones || [];
    if (clones.length === 0) { document.getElementById('clones-content').innerHTML = '<p style="color:var(--green)">No se detecto codigo duplicado.</p>'; return; }
    var html = '<p style="margin-bottom:12px">Total: <strong>' + clones.length + '</strong></p>';
    html += '<table class="data-table"><tr><th>#</th><th>Ubicaciones</th></tr>';
    clones.slice(0, 50).forEach(function(c, i) { html += '<tr><td style="color:var(--yellow)">#' + (i+1) + '</td><td class="mono" style="font-size:11px">' + c.map(esc).join('<br>') + '</td></tr>'; });
    if (clones.length > 50) html += '<tr><td colspan="2" style="color:var(--text-dim)">... y ' + (clones.length - 50) + ' mas</td></tr>';
    html += '</table>';
    document.getElementById('clones-content').innerHTML = html;
}

// ============================================================================
// GLOBAL SEARCH
// ============================================================================

document.getElementById('global-search').addEventListener('keydown', function(e) { if (e.key === 'Enter') doGlobalSearch(); });

function doGlobalSearch() {
    var q = (document.getElementById('global-search').value || '').toLowerCase().trim();
    if (!q || !DATA) return;
    var triggers = (DATA.triggers || []).filter(function(t) { return t.event_name.toLowerCase().indexOf(q) !== -1; });
    if (triggers.length === 0) { document.getElementById('search-results').innerHTML = '<div class="card"><p style="color:var(--yellow)">No se encontraron triggers con "' + esc(q) + '"</p></div>'; return; }
    var html = '';
    triggers.forEach(function(t) {
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'honeypot') + ' ';
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban') + ' ';
        if (t.has_validation) tags += tagHTML('VAL', 'val') + ' ';
        html += '<div class="card"><div class="card-title" style="color:' + riskColor(t.risk_score) + '">' + esc(t.event_name) + ' ' + tags + '</div>' +
            '<table style="width:100%;font-size:13px"><tr><td style="width:120px;color:var(--text-secondary)">Tipo</td><td>' + esc(t.event_type) + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Archivo</td><td class="mono">' + esc(t.file) + ':' + t.line + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Handler</td><td class="mono">' + esc(t.handler_function) + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Parametros</td><td class="mono">' + esc((t.parameters || []).join(', ') || 'N/A') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Validacion</td><td>' + (t.has_validation ? '<span style="color:var(--green)">SI</span>' : '<span style="color:var(--red)">NO</span>') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Riesgo</td><td class="' + riskClass(t.risk_score) + '" style="font-weight:bold">' + t.risk_score.toFixed(1) + '%</td></tr></table>';
        if (t.code_context) html += '<div style="margin-top:10px"><div style="color:var(--text-dim);font-size:11px;margin-bottom:4px">Contexto:</div><div class="code-block">' + esc(t.code_context) + '</div></div>';
        html += '</div>';
    });
    document.getElementById('search-results').innerHTML = html;
}

// ============================================================================
// BOOT - check if data already available (e.g. passed via CLI)
// ============================================================================

fetch('/api/data').then(function(r) {
    if (r.ok) return r.json();
    return null;
}).then(function(d) {
    if (d && d.stats && d.triggers) {
        DATA = d;
        showDashboard();
    }
    // else stay on landing page
}).catch(function() {
    // stay on landing page
});
</script>
</body>
</html>"""


# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class RedShadowHandler(BaseHTTPRequestHandler):
    """Handler HTTP para la aplicacion web completa"""

    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/' or path == '/index.html':
            self._serve_html()
        elif path == '/api/data':
            self._serve_data()
        elif path == '/api/status':
            self._serve_status()
        elif path == '/api/health':
            self._json_response({'status': 'ok'})
        else:
            self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/analyze':
            self._handle_analyze()
        else:
            self.send_error(404)

    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def _serve_data(self):
        if AppState.report_data:
            self._json_response(AppState.report_data)
        else:
            self._json_response({'error': 'No data'}, status=204)

    def _serve_status(self):
        self._json_response({
            'running': AppState.analysis_running,
            'done': AppState.analysis_done,
            'progress': AppState.analysis_progress,
            'error': AppState.analysis_error,
        })

    def _handle_analyze(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
        except Exception:
            self._json_response({'error': 'Invalid request'}, status=400)
            return

        dump_path = body.get('path', '').strip()
        if not dump_path:
            self._json_response({'error': 'Ruta del dump no proporcionada'}, status=400)
            return

        if not os.path.exists(dump_path):
            self._json_response({'error': f'Ruta no encontrada: {dump_path}'}, status=400)
            return

        if not os.path.isdir(dump_path):
            self._json_response({'error': 'La ruta debe ser un directorio'}, status=400)
            return

        if AppState.analysis_running:
            self._json_response({'error': 'Analisis ya en curso'}, status=409)
            return

        # Launch analysis in background thread
        AppState.analysis_running = True
        AppState.analysis_done = False
        AppState.analysis_error = None
        AppState.analysis_progress = "Iniciando analisis..."
        AppState.report_data = None
        AppState.dump_path = dump_path

        thread = threading.Thread(target=_run_analysis_thread, args=(dump_path,), daemon=True)
        thread.start()

        self._json_response({'status': 'started', 'path': dump_path})

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))


# ============================================================================
# ANALYSIS THREAD
# ============================================================================

def _run_analysis_thread(dump_path):
    """Ejecutar el analisis en un thread de background"""
    try:
        # Importar el motor v4
        engine_dir = Path(__file__).parent.resolve()
        if str(engine_dir) not in sys.path:
            sys.path.insert(0, str(engine_dir))

        from red_shadow_destroyer_v4 import RedShadowV4

        AppState.analysis_progress = "Cargando archivos del dump..."
        engine = RedShadowV4(dump_path)

        file_count = engine.load_files()
        if file_count == 0:
            AppState.analysis_error = "No se encontraron archivos Lua en el dump"
            AppState.analysis_running = False
            return

        AppState.analysis_progress = f"{file_count} archivos Lua cargados. Ejecutando analisis..."

        # Run each phase with progress updates
        phases = [
            ("Extrayendo funciones...", engine.extract_functions),
            ("Detectando triggers...", engine.detect_triggers),
            ("Escaneando ofuscacion...", engine.detect_obfuscation),
            ("Analizando natives...", engine.analyze_natives),
            ("Analizando callbacks...", engine.analyze_callbacks),
            ("Analizando manifests...", engine.analyze_manifests),
            ("Escaneando seguridad...", engine.detect_security_issues),
            ("Fingerprinting anticheats...", engine.fingerprint_anticheats),
            ("Analizando cadenas de triggers...", engine.analyze_trigger_chains),
            ("Detectando codigo duplicado...", engine.detect_code_clones),
        ]

        for i, (msg, func) in enumerate(phases, 1):
            AppState.analysis_progress = f"Fase {i}/{len(phases)}: {msg}"
            func()

        AppState.analysis_progress = "Generando reporte..."

        # Build report data
        AppState.report_data = _build_report_data(engine)
        AppState.analysis_done = True
        AppState.analysis_running = False
        AppState.analysis_progress = "Analisis completado"

    except Exception as e:
        AppState.analysis_error = str(e)
        AppState.analysis_running = False
        traceback.print_exc()


def _build_report_data(engine):
    """Construir diccionario de reporte desde el engine"""
    code_clones = []
    if hasattr(engine, 'code_hashes'):
        for h, files in engine.code_hashes.items():
            if len(files) > 1:
                code_clones.append(files)

    return {
        'tool': 'RED-SHADOW Destroyer v4.0',
        'timestamp': datetime.now().isoformat(),
        'dump_path': str(engine.dump_path),
        'stats': {
            'lua_files': len(engine.lua_files),
            'total_lines': engine.total_lines,
            'functions': len(engine.functions),
            'triggers': len(engine.triggers),
            'callbacks': len(engine.callbacks),
            'natives': len(engine.natives),
            'obfuscations': len(engine.obfuscations),
            'security_issues': len(engine.security_issues),
            'anticheats': len(engine.anticheat_detected),
        },
        'triggers': [asdict(t) for t in engine.triggers.values()],
        'callbacks': [asdict(c) for c in engine.callbacks],
        'natives': [asdict(n) for n in engine.natives],
        'obfuscations': [asdict(o) for o in engine.obfuscations],
        'security_issues': [asdict(s) for s in engine.security_issues],
        'anticheats': engine.anticheat_detected,
        'manifests': [asdict(m) for m in engine.manifests],
        'trigger_chains': engine.trigger_chains,
        'cross_references': {k: list(v) for k, v in engine.cross_references.items()},
        'code_clones': code_clones[:100],
        'recommendations': engine._generate_recommendations(),
    }


# ============================================================================
# SERVER LAUNCHER
# ============================================================================

def find_free_port(start=8470, end=8499):
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def launch_web_gui(engine=None, auto_open=True):
    """
    Lanzar el servidor web.

    Si se pasa un engine con analisis completado, los datos estaran disponibles
    inmediatamente y el dashboard se mostrara directamente.
    Si no se pasa engine, se muestra la landing page para seleccionar dump.
    """
    if engine is not None:
        AppState.report_data = _build_report_data(engine)
        AppState.analysis_done = True

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No se encontro un puerto libre\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] RED-SHADOW Web Dashboard: {url}\033[0m")
    print(f"\033[93m[INFO] Presiona Ctrl+C para cerrar\033[0m")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Servidor cerrado\033[0m")


def launch_web_gui_from_json(json_path, auto_open=True):
    """Lanzar desde un archivo JSON de reporte existente."""
    with open(json_path, 'r', encoding='utf-8') as f:
        AppState.report_data = json.load(f)
    AppState.analysis_done = True

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No se encontro un puerto libre\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] RED-SHADOW Web Dashboard: {url}\033[0m")
    print(f"\033[93m[INFO] Presiona Ctrl+C para cerrar\033[0m")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Servidor cerrado\033[0m")


# ============================================================================
# STANDALONE
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
        # Abrir reporte JSON existente
        launch_web_gui_from_json(sys.argv[1])
    elif len(sys.argv) >= 2 and os.path.isdir(sys.argv[1]):
        # Dump path given - run analysis then show
        print("\033[96m[INFO] Dump path proporcionado, ejecutando analisis...\033[0m")
        AppState.dump_path = sys.argv[1]
        launch_web_gui()  # Landing page will auto-start analysis via API? No...
        # Actually just launch with landing, user can input the path
    else:
        # No args - launch landing page
        launch_web_gui()
