#!/usr/bin/env python3
"""
RED-SHADOW v4.0 - Embedded Web GUI
Servidor web local que muestra los resultados del analisis forense
en un dashboard interactivo en el navegador.

No requiere dependencias externas - usa http.server de la stdlib.
"""

import json
import os
import sys
import threading
import webbrowser
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from dataclasses import asdict
from datetime import datetime


# ============================================================================
# HTML TEMPLATE - Dashboard completo embebido
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

/* Scanline effect */
body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    z-index: 9999;
}

/* Header */
.header {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 30px;
    text-align: center;
    position: relative;
}

.header h1 {
    color: var(--red);
    font-size: 28px;
    text-shadow: 0 0 20px var(--red-glow);
    letter-spacing: 3px;
    margin-bottom: 5px;
}

.header .subtitle {
    color: var(--text-secondary);
    font-size: 13px;
    letter-spacing: 1px;
}

.header .dump-path {
    color: var(--cyan);
    font-size: 12px;
    margin-top: 8px;
    opacity: 0.7;
}

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

.nav-btn:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
}

.nav-btn.active {
    color: var(--red);
    border-bottom-color: var(--red);
    text-shadow: 0 0 10px var(--red-glow);
}

/* Main content */
.main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Section panels */
.section {
    display: none;
}
.section.active {
    display: block;
}

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

.stat-box:hover {
    transform: translateY(-2px);
    border-color: var(--cyan-dark);
}

.stat-value {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Risk meter */
.risk-meter {
    width: 100%;
    height: 8px;
    background: var(--bg-primary);
    border-radius: 4px;
    overflow: hidden;
    margin: 10px 0;
}

.risk-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.data-table th {
    background: var(--bg-secondary);
    color: var(--cyan);
    padding: 10px 12px;
    text-align: left;
    border: 1px solid var(--border);
    font-weight: normal;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
    position: sticky;
    top: 46px;
    z-index: 10;
}

.data-table td {
    padding: 8px 12px;
    border: 1px solid var(--border);
    vertical-align: top;
}

.data-table tr:hover td {
    background: var(--bg-hover);
}

.data-table .mono {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
    margin: 1px;
}

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
    background: #0d0d12;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
    overflow-x: auto;
    color: var(--text-secondary);
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* Search */
.search-box {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.search-input {
    flex: 1;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 10px 14px;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.search-input:focus {
    border-color: var(--red);
    box-shadow: 0 0 10px var(--red-glow);
}

.search-input::placeholder {
    color: var(--text-dim);
}

/* Filter buttons */
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
}

.filter-btn {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 6px 14px;
    color: var(--text-secondary);
    cursor: pointer;
    font-family: inherit;
    font-size: 12px;
    transition: all 0.2s;
}

.filter-btn:hover, .filter-btn.active {
    color: #fff;
    border-color: var(--red);
    background: rgba(255, 51, 68, 0.15);
}

/* Recommendations */
.rec-list {
    list-style: none;
    padding: 0;
}

.rec-list li {
    padding: 10px 14px;
    margin-bottom: 6px;
    background: var(--bg-secondary);
    border-left: 3px solid var(--yellow);
    border-radius: 0 4px 4px 0;
    font-size: 13px;
}

/* Chain visualization */
.chain-item {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 10px;
    padding: 10px;
    background: var(--bg-secondary);
    border-radius: 4px;
}

.chain-node {
    background: var(--bg-card);
    border: 1px solid var(--cyan-dark);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    color: var(--cyan);
}

.chain-arrow {
    color: var(--text-dim);
    font-size: 14px;
}

/* Loading */
.loading {
    text-align: center;
    padding: 60px;
    color: var(--text-secondary);
}

.loading .spinner {
    display: inline-block;
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--red);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .nav-btn {
        padding: 10px 10px;
        font-size: 12px;
    }
    .header h1 {
        font-size: 20px;
    }
}

/* Export button */
.export-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    justify-content: flex-end;
}

.btn {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 8px 16px;
    color: var(--text-primary);
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
    transition: all 0.2s;
}

.btn:hover {
    border-color: var(--red);
    background: rgba(255, 51, 68, 0.1);
}

.btn-primary {
    background: var(--red-dark);
    border-color: var(--red);
    color: #fff;
}

.btn-primary:hover {
    background: var(--red);
}

/* Severity colors */
.sev-critical { color: var(--critical); }
.sev-high { color: var(--red); }
.sev-medium { color: var(--yellow); }
.sev-low { color: var(--green); }

/* Risk colors */
.risk-safe { color: var(--green); }
.risk-warn { color: var(--yellow); }
.risk-danger { color: var(--red); }
.risk-critical { color: var(--critical); }

/* Confidence bar */
.conf-bar {
    display: inline-block;
    width: 60px;
    height: 6px;
    background: var(--bg-primary);
    border-radius: 3px;
    overflow: hidden;
    vertical-align: middle;
    margin-left: 6px;
}

.conf-fill {
    height: 100%;
    border-radius: 3px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #444; }

/* Toast notification */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--bg-card);
    border: 1px solid var(--green);
    border-radius: 6px;
    padding: 12px 20px;
    color: var(--green);
    font-size: 13px;
    z-index: 10000;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s;
}

.toast.show {
    opacity: 1;
    transform: translateY(0);
}
</style>
</head>
<body>

<div class="header">
    <h1>RED-SHADOW "Destroyer" v4.0</h1>
    <div class="subtitle">Advanced Forensic Engine - Web Dashboard</div>
    <div class="dump-path" id="dump-path"></div>
</div>

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
</nav>

<div class="main" id="main">
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p style="margin-top:16px;">Cargando datos del analisis...</p>
    </div>

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

<div class="toast" id="toast"></div>

<script>
// ============================================================================
// DATA & STATE
// ============================================================================

let DATA = null;
let currentSection = 'summary';
let triggerFilter = 'all';

// ============================================================================
// INITIALIZATION
// ============================================================================

async function init() {
    try {
        const resp = await fetch('/api/data');
        DATA = await resp.json();
        document.getElementById('loading').style.display = 'none';
        document.getElementById('dump-path').textContent = 'Dump: ' + (DATA.dump_path || 'N/A');
        renderSummary();
        showSection('summary');
    } catch (e) {
        document.getElementById('loading').innerHTML =
            '<p style="color:var(--red)">Error cargando datos: ' + e.message + '</p>';
    }
}

// ============================================================================
// NAVIGATION
// ============================================================================

document.getElementById('nav').addEventListener('click', function(e) {
    if (e.target.classList.contains('nav-btn')) {
        var sec = e.target.dataset.section;
        showSection(sec);
    }
});

function showSection(name) {
    currentSection = name;

    // Update nav
    document.querySelectorAll('.nav-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.section === name);
    });

    // Hide all sections
    document.querySelectorAll('.section').forEach(function(s) {
        s.classList.remove('active');
    });

    // Show target
    var el = document.getElementById('sec-' + name);
    if (el) el.classList.add('active');

    // Lazy render
    var renderers = {
        summary: renderSummary,
        triggers: renderTriggers,
        honeypots: renderHoneypots,
        anticheats: renderAnticheats,
        obfuscation: renderObfuscation,
        natives: renderNatives,
        callbacks: renderCallbacks,
        security: renderSecurity,
        manifests: renderManifests,
        chains: renderChains,
        clones: renderClones
    };

    if (renderers[name] && DATA) renderers[name]();
}

// ============================================================================
// HELPERS
// ============================================================================

function esc(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function riskClass(score) {
    if (score >= 70) return 'risk-danger';
    if (score >= 40) return 'risk-warn';
    return 'risk-safe';
}

function riskColor(score) {
    if (score >= 70) return 'var(--red)';
    if (score >= 40) return 'var(--yellow)';
    return 'var(--green)';
}

function sevClass(sev) {
    return 'sev-' + sev.toLowerCase();
}

function tagHTML(text, cls) {
    return '<span class="tag tag-' + cls + '">' + esc(text) + '</span>';
}

function confBar(val) {
    var pct = Math.round(val * 100);
    var color = val > 0.7 ? 'var(--red)' : (val > 0.3 ? 'var(--yellow)' : 'var(--green)');
    return pct + '% <span class="conf-bar"><span class="conf-fill" style="width:' + pct + '%;background:' + color + '"></span></span>';
}

function shortPath(p) {
    if (!p) return '';
    var parts = p.replace(/\\/g, '/').split('/');
    return parts.length > 2 ? '.../' + parts.slice(-2).join('/') : p;
}

function showToast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(function() { t.classList.remove('show'); }, 2500);
}

function downloadJSON() {
    if (!DATA) return;
    var blob = new Blob([JSON.stringify(DATA, null, 2)], {type: 'application/json'});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'red_shadow_report.json';
    a.click();
    showToast('Reporte JSON descargado');
}

// ============================================================================
// RENDER: SUMMARY
// ============================================================================

function renderSummary() {
    var s = DATA.stats;
    var triggers = DATA.triggers || [];
    var safe = triggers.filter(function(t) { return t.risk_score < 40; }).length;
    var warn = triggers.filter(function(t) { return t.risk_score >= 40 && t.risk_score < 70; }).length;
    var danger = triggers.filter(function(t) { return t.risk_score >= 70; }).length;
    var honeypots = triggers.filter(function(t) { return t.is_honeypot; }).length;
    var overallRisk = triggers.length > 0
        ? triggers.reduce(function(sum, t) { return sum + t.risk_score; }, 0) / triggers.length
        : 0;

    var statsHTML = [
        {val: s.lua_files, label: 'Archivos Lua', color: 'var(--cyan)'},
        {val: s.total_lines, label: 'Lineas', color: 'var(--cyan)'},
        {val: s.functions, label: 'Funciones', color: 'var(--cyan)'},
        {val: s.triggers, label: 'Triggers', color: 'var(--cyan)'},
        {val: safe, label: 'Seguros', color: 'var(--green)'},
        {val: warn, label: 'Advertencia', color: 'var(--yellow)'},
        {val: danger, label: 'Peligrosos', color: 'var(--red)'},
        {val: honeypots, label: 'Honeypots', color: 'var(--critical)'},
        {val: s.callbacks, label: 'Callbacks', color: 'var(--cyan)'},
        {val: s.natives, label: 'Natives', color: 'var(--cyan)'},
        {val: s.obfuscations, label: 'Ofuscacion', color: 'var(--magenta)'},
        {val: s.security_issues, label: 'Seguridad', color: 'var(--red)'},
        {val: s.anticheats, label: 'Anticheats', color: 'var(--yellow)'},
    ].map(function(item) {
        return '<div class="stat-box"><div class="stat-value" style="color:' + item.color + '">' +
            item.val + '</div><div class="stat-label">' + item.label + '</div></div>';
    }).join('');

    document.getElementById('stats-grid').innerHTML = statsHTML;

    // Risk meter
    var rc = riskColor(overallRisk);
    document.getElementById('risk-display').innerHTML =
        '<div style="font-size:36px;font-weight:bold;color:' + rc + ';margin-bottom:8px">' +
        overallRisk.toFixed(1) + '%</div>' +
        '<div class="risk-meter"><div class="risk-fill" style="width:' + overallRisk + '%;background:' + rc + '"></div></div>';

    // Recommendations
    var recs = DATA.recommendations || [];
    document.getElementById('recommendations').innerHTML = recs.length > 0
        ? recs.map(function(r) { return '<li>' + esc(r) + '</li>'; }).join('')
        : '<li>No se generaron recomendaciones.</li>';
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

    var html = '<table class="data-table"><tr>' +
        '<th>Trigger</th><th>Tipo</th><th>Archivo</th><th>Reward</th><th>Riesgo</th><th>Tags</th></tr>';

    filtered.forEach(function(t) {
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'honeypot');
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban');
        if (t.has_validation) tags += tagHTML('VAL', 'val');
        if (t.has_reward_logic) tags += tagHTML(t.reward_type || 'REWARD', 'info');

        html += '<tr>' +
            '<td class="mono">' + esc(t.event_name) + '</td>' +
            '<td>' + esc(t.event_type) + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td>' +
            '<td>' + esc(t.reward_type) + '</td>' +
            '<td class="' + riskClass(t.risk_score) + '" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td>' +
            '<td>' + tags + '</td></tr>';
    });

    html += '</table>';
    if (filtered.length === 0) html = '<p style="color:var(--text-secondary);padding:20px">No se encontraron triggers con estos filtros.</p>';

    document.getElementById('triggers-table-wrap').innerHTML = html;
}

// Trigger search
document.getElementById('trigger-search').addEventListener('input', function() {
    if (currentSection === 'triggers') renderTriggers();
});

// Trigger filters
document.getElementById('trigger-filters').addEventListener('click', function(e) {
    if (e.target.classList.contains('filter-btn')) {
        triggerFilter = e.target.dataset.filter;
        document.querySelectorAll('#trigger-filters .filter-btn').forEach(function(b) {
            b.classList.toggle('active', b.dataset.filter === triggerFilter);
        });
        renderTriggers();
    }
});

// ============================================================================
// RENDER: HONEYPOTS
// ============================================================================

function renderHoneypots() {
    var triggers = (DATA.triggers || []).filter(function(t) { return t.is_honeypot; });
    if (triggers.length === 0) {
        document.getElementById('honeypots-content').innerHTML =
            '<p style="color:var(--green)">No se detectaron honeypots en este dump.</p>';
        return;
    }

    var html = '<table class="data-table"><tr><th>Trigger</th><th>Tipo</th><th>Archivo</th><th>Ban</th><th>Reward</th><th>Riesgo</th></tr>';
    triggers.forEach(function(t) {
        html += '<tr>' +
            '<td class="mono" style="color:var(--critical)">' + esc(t.event_name) + '</td>' +
            '<td>' + esc(t.event_type) + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td>' +
            '<td>' + (t.has_ban_logic ? tagHTML('SI', 'danger') : 'NO') + '</td>' +
            '<td>' + (t.has_reward_logic ? tagHTML('SI', 'warn') : 'NO') + '</td>' +
            '<td class="risk-danger" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td></tr>';
    });
    html += '</table>';
    document.getElementById('honeypots-content').innerHTML = html;
}

// ============================================================================
// RENDER: ANTICHEATS
// ============================================================================

function renderAnticheats() {
    var acs = DATA.anticheats || {};
    var keys = Object.keys(acs);
    if (keys.length === 0) {
        document.getElementById('anticheats-content').innerHTML =
            '<p style="color:var(--green)">No se detectaron anticheats conocidos.</p>';
        return;
    }

    var html = '<table class="data-table"><tr><th>Anticheat</th><th>Confianza</th><th>Descripcion</th><th>Firmas</th></tr>';
    keys.forEach(function(name) {
        var ac = acs[name];
        html += '<tr>' +
            '<td style="font-weight:bold;color:var(--yellow)">' + esc(name) + '</td>' +
            '<td>' + confBar(ac.confidence) + '</td>' +
            '<td style="font-size:12px">' + esc(ac.description) + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc((ac.matched_signatures || []).join(', ')) + '</td></tr>';
    });
    html += '</table>';
    document.getElementById('anticheats-content').innerHTML = html;
}

// ============================================================================
// RENDER: OBFUSCATION
// ============================================================================

function renderObfuscation() {
    var obfs = DATA.obfuscations || [];
    if (obfs.length === 0) {
        document.getElementById('obfuscation-content').innerHTML =
            '<div class="card"><p style="color:var(--green)">No se detecto ofuscacion de codigo.</p></div>';
        return;
    }

    // Group by type
    var byType = {};
    obfs.forEach(function(o) {
        if (!byType[o.obf_type]) byType[o.obf_type] = [];
        byType[o.obf_type].push(o);
    });

    // Render filter buttons
    var types = Object.keys(byType).sort(function(a, b) { return byType[b].length - byType[a].length; });
    var filtersHTML = '<button class="filter-btn active" data-obf="all">Todos (' + obfs.length + ')</button>';
    types.forEach(function(t) {
        filtersHTML += '<button class="filter-btn" data-obf="' + t + '">' + t + ' (' + byType[t].length + ')</button>';
    });
    document.getElementById('obf-filters').innerHTML = filtersHTML;

    // Table
    renderObfTable('all');

    document.getElementById('obf-filters').onclick = function(e) {
        if (e.target.classList.contains('filter-btn')) {
            var f = e.target.dataset.obf;
            document.querySelectorAll('#obf-filters .filter-btn').forEach(function(b) {
                b.classList.toggle('active', b.dataset.obf === f);
            });
            renderObfTable(f);
        }
    };
}

function renderObfTable(filter) {
    var obfs = DATA.obfuscations || [];
    if (filter !== 'all') obfs = obfs.filter(function(o) { return o.obf_type === filter; });
    obfs.sort(function(a, b) { return b.confidence - a.confidence; });

    var html = '<div class="card"><table class="data-table"><tr><th>Tipo</th><th>Archivo</th><th>Confianza</th><th>Snippet</th></tr>';
    obfs.slice(0, 100).forEach(function(o) {
        html += '<tr><td>' + tagHTML(o.obf_type, 'obf') + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(o.file)) + ':' + o.line + '</td>' +
            '<td>' + confBar(o.confidence) + '</td>' +
            '<td class="mono" style="font-size:11px;max-width:400px;overflow:hidden;text-overflow:ellipsis">' + esc(o.snippet) + '</td></tr>';
    });
    if (obfs.length > 100) html += '<tr><td colspan="4" style="color:var(--text-dim)">... y ' + (obfs.length - 100) + ' mas</td></tr>';
    html += '</table></div>';
    document.getElementById('obfuscation-content').innerHTML = html;
}

// ============================================================================
// RENDER: NATIVES
// ============================================================================

function renderNatives() {
    var natives = DATA.natives || [];
    if (natives.length === 0) {
        document.getElementById('natives-content').innerHTML =
            '<div class="card"><p style="color:var(--green)">No se detectaron llamadas a natives.</p></div>';
        return;
    }

    var byCategory = {};
    natives.forEach(function(n) {
        if (!byCategory[n.category]) byCategory[n.category] = [];
        byCategory[n.category].push(n);
    });

    var cats = Object.keys(byCategory).sort(function(a, b) { return byCategory[b].length - byCategory[a].length; });
    var filtersHTML = '<button class="filter-btn active" data-nat="all">Todos (' + natives.length + ')</button>';
    cats.forEach(function(c) {
        filtersHTML += '<button class="filter-btn" data-nat="' + c + '">' + c + ' (' + byCategory[c].length + ')</button>';
    });
    document.getElementById('native-filters').innerHTML = filtersHTML;

    renderNativesTable('all');

    document.getElementById('native-filters').onclick = function(e) {
        if (e.target.classList.contains('filter-btn')) {
            var f = e.target.dataset.nat;
            document.querySelectorAll('#native-filters .filter-btn').forEach(function(b) {
                b.classList.toggle('active', b.dataset.nat === f);
            });
            renderNativesTable(f);
        }
    };
}

function renderNativesTable(filter) {
    var natives = DATA.natives || [];
    if (filter !== 'all') natives = natives.filter(function(n) { return n.category === filter; });

    var catColors = {WEAPON:'danger',MONEY:'danger',PLAYER:'warn',NETWORK:'warn',VEHICLE:'info',WORLD:'info',UNKNOWN:'info'};

    var html = '<div class="card"><table class="data-table"><tr><th>Native</th><th>Categoria</th><th>Archivo</th></tr>';
    natives.slice(0, 100).forEach(function(n) {
        html += '<tr><td class="mono">' + esc(n.native_hash) + '</td>' +
            '<td>' + tagHTML(n.category, catColors[n.category] || 'info') + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(n.file)) + ':' + n.line + '</td></tr>';
    });
    if (natives.length > 100) html += '<tr><td colspan="3" style="color:var(--text-dim)">... y ' + (natives.length - 100) + ' mas</td></tr>';
    html += '</table></div>';
    document.getElementById('natives-content').innerHTML = html;
}

// ============================================================================
// RENDER: CALLBACKS
// ============================================================================

function renderCallbacks() {
    var cbs = DATA.callbacks || [];
    if (cbs.length === 0) {
        document.getElementById('callbacks-content').innerHTML =
            '<div class="card"><p style="color:var(--green)">No se detectaron server callbacks.</p></div>';
        return;
    }

    cbs.sort(function(a, b) { return b.risk_score - a.risk_score; });

    var html = '<div class="card"><table class="data-table"><tr><th>Callback</th><th>Archivo</th><th>Validacion</th><th>Riesgo</th></tr>';
    cbs.forEach(function(cb) {
        html += '<tr>' +
            '<td class="mono">' + esc(cb.name) + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(cb.file)) + ':' + cb.line + '</td>' +
            '<td>' + (cb.has_validation ? tagHTML('SI', 'safe') : tagHTML('NO', 'danger')) + '</td>' +
            '<td class="' + riskClass(cb.risk_score) + '" style="font-weight:bold">' + cb.risk_score.toFixed(0) + '%</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('callbacks-content').innerHTML = html;
}

// ============================================================================
// RENDER: SECURITY
// ============================================================================

function renderSecurity() {
    var issues = DATA.security_issues || [];
    if (issues.length === 0) {
        document.getElementById('security-content').innerHTML =
            '<div class="card"><p style="color:var(--green)">No se detectaron vulnerabilidades.</p></div>';
        return;
    }

    var byType = {};
    issues.forEach(function(i) {
        if (!byType[i.issue_type]) byType[i.issue_type] = [];
        byType[i.issue_type].push(i);
    });

    var types = Object.keys(byType);
    var filtersHTML = '<button class="filter-btn active" data-sec="all">Todos (' + issues.length + ')</button>';
    types.forEach(function(t) {
        filtersHTML += '<button class="filter-btn" data-sec="' + t + '">' + t + ' (' + byType[t].length + ')</button>';
    });
    document.getElementById('security-filters').innerHTML = filtersHTML;

    renderSecurityTable('all');

    document.getElementById('security-filters').onclick = function(e) {
        if (e.target.classList.contains('filter-btn')) {
            var f = e.target.dataset.sec;
            document.querySelectorAll('#security-filters .filter-btn').forEach(function(b) {
                b.classList.toggle('active', b.dataset.sec === f);
            });
            renderSecurityTable(f);
        }
    };
}

function renderSecurityTable(filter) {
    var issues = DATA.security_issues || [];
    if (filter !== 'all') issues = issues.filter(function(i) { return i.issue_type === filter; });

    var sevOrder = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3};
    issues.sort(function(a, b) { return (sevOrder[a.severity] || 9) - (sevOrder[b.severity] || 9); });

    var sevTags = {CRITICAL:'critical', HIGH:'danger', MEDIUM:'warn', LOW:'safe'};

    var html = '<div class="card"><table class="data-table"><tr><th>Tipo</th><th>Severidad</th><th>Archivo</th><th>Descripcion</th><th>Snippet</th></tr>';
    issues.slice(0, 100).forEach(function(i) {
        html += '<tr><td>' + esc(i.issue_type) + '</td>' +
            '<td>' + tagHTML(i.severity, sevTags[i.severity] || 'info') + '</td>' +
            '<td class="mono" style="font-size:11px">' + esc(shortPath(i.file)) + ':' + i.line + '</td>' +
            '<td style="font-size:12px">' + esc(i.description) + '</td>' +
            '<td class="mono" style="font-size:11px;max-width:300px;overflow:hidden;text-overflow:ellipsis">' + esc(i.snippet) + '</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('security-content').innerHTML = html;
}

// ============================================================================
// RENDER: MANIFESTS
// ============================================================================

function renderManifests() {
    var manifests = DATA.manifests || [];
    if (manifests.length === 0) {
        document.getElementById('manifests-content').innerHTML =
            '<div class="card"><p style="color:var(--green)">No se encontraron resource manifests.</p></div>';
        return;
    }

    var html = '';
    manifests.forEach(function(m) {
        html += '<div class="card">' +
            '<div class="card-title" style="color:var(--yellow)">' + esc(m.resource_name) +
            (m.has_ui_page ? ' ' + tagHTML('NUI', 'obf') : '') + '</div>';

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
    var chains = DATA.trigger_chains || [];
    var crossRefs = DATA.cross_references || {};

    if (chains.length === 0) {
        document.getElementById('chains-content').innerHTML =
            '<p style="color:var(--green)">No se detectaron cadenas de triggers.</p>';
    } else {
        var html = '';
        chains.forEach(function(chain, idx) {
            html += '<div class="chain-item"><strong style="color:var(--cyan);margin-right:8px">Cadena #' + (idx+1) + ':</strong> ';
            chain.forEach(function(node, i) {
                html += '<span class="chain-node">' + esc(node) + '</span>';
                if (i < chain.length - 1) html += '<span class="chain-arrow"> &rarr; </span>';
            });
            html += '</div>';
        });
        document.getElementById('chains-content').innerHTML = html;
    }

    var crKeys = Object.keys(crossRefs);
    if (crKeys.length === 0) {
        document.getElementById('crossrefs-content').innerHTML =
            '<p style="color:var(--text-secondary)">No se detectaron referencias cruzadas.</p>';
    } else {
        var html2 = '<table class="data-table"><tr><th>Trigger</th><th>Archivos</th></tr>';
        crKeys.forEach(function(name) {
            var files = crossRefs[name];
            html2 += '<tr><td class="mono" style="color:var(--cyan)">' + esc(name) + '</td>' +
                '<td class="mono" style="font-size:11px">' + (Array.isArray(files) ? files.map(esc).join(', ') : esc(String(files))) + '</td></tr>';
        });
        html2 += '</table>';
        document.getElementById('crossrefs-content').innerHTML = html2;
    }
}

// ============================================================================
// RENDER: CLONES
// ============================================================================

function renderClones() {
    var clones = DATA.code_clones || [];
    if (clones.length === 0) {
        document.getElementById('clones-content').innerHTML =
            '<p style="color:var(--green)">No se detecto codigo duplicado.</p>';
        return;
    }

    var html = '<p style="margin-bottom:12px">Total bloques duplicados: <strong>' + clones.length + '</strong></p>';
    html += '<table class="data-table"><tr><th>#</th><th>Ubicaciones</th></tr>';
    clones.slice(0, 50).forEach(function(c, idx) {
        html += '<tr><td style="color:var(--yellow)">#' + (idx+1) + '</td>' +
            '<td class="mono" style="font-size:11px">' + c.map(esc).join('<br>') + '</td></tr>';
    });
    if (clones.length > 50) html += '<tr><td colspan="2" style="color:var(--text-dim)">... y ' + (clones.length - 50) + ' mas</td></tr>';
    html += '</table>';
    document.getElementById('clones-content').innerHTML = html;
}

// ============================================================================
// GLOBAL SEARCH
// ============================================================================

document.getElementById('global-search').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') doGlobalSearch();
});

function doGlobalSearch() {
    var query = (document.getElementById('global-search').value || '').toLowerCase().trim();
    if (!query) return;

    var triggers = (DATA.triggers || []).filter(function(t) {
        return t.event_name.toLowerCase().indexOf(query) !== -1;
    });

    if (triggers.length === 0) {
        document.getElementById('search-results').innerHTML =
            '<div class="card"><p style="color:var(--yellow)">No se encontraron triggers con "' + esc(query) + '"</p></div>';
        return;
    }

    var html = '';
    triggers.forEach(function(t) {
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'honeypot') + ' ';
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban') + ' ';
        if (t.has_validation) tags += tagHTML('VAL', 'val') + ' ';

        html += '<div class="card">' +
            '<div class="card-title" style="color:' + riskColor(t.risk_score) + '">' + esc(t.event_name) + ' ' + tags + '</div>' +
            '<table style="width:100%;font-size:13px">' +
            '<tr><td style="width:120px;color:var(--text-secondary)">Tipo</td><td>' + esc(t.event_type) + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Archivo</td><td class="mono">' + esc(t.file) + ':' + t.line + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Handler</td><td class="mono">' + esc(t.handler_function) + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Parametros</td><td class="mono">' + esc((t.parameters || []).join(', ') || 'N/A') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Funciones</td><td class="mono">' + esc((t.calls_functions || []).slice(0, 8).join(', ') || 'N/A') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Validacion</td><td>' + (t.has_validation ? '<span style="color:var(--green)">SI</span>' : '<span style="color:var(--red)">NO</span>') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Reward</td><td>' + (t.has_reward_logic ? esc(t.reward_type) : 'NO') + '</td></tr>' +
            '<tr><td style="color:var(--text-secondary)">Riesgo</td><td class="' + riskClass(t.risk_score) + '" style="font-weight:bold">' + t.risk_score.toFixed(1) + '%</td></tr>' +
            '</table>';

        if (t.code_context) {
            html += '<div style="margin-top:10px"><div style="color:var(--text-dim);font-size:11px;margin-bottom:4px">Contexto:</div>' +
                '<div class="code-block">' + esc(t.code_context) + '</div></div>';
        }

        html += '</div>';
    });

    document.getElementById('search-results').innerHTML = html;
}

// ============================================================================
// BOOT
// ============================================================================

init();
</script>
</body>
</html>"""


# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class RedShadowHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servir el dashboard y la API de datos"""

    report_data = None  # Set by the server before starting

    def log_message(self, format, *args):
        # Suprimir logs del servidor para no ensuciar la terminal
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            self._serve_html()
        elif path == '/api/data':
            self._serve_data()
        elif path == '/api/health':
            self._json_response({'status': 'ok'})
        else:
            self.send_error(404, 'Not Found')

    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def _serve_data(self):
        if RedShadowHandler.report_data:
            self._json_response(RedShadowHandler.report_data)
        else:
            self._json_response({'error': 'No data available'}, status=503)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))


# ============================================================================
# WEB GUI SERVER
# ============================================================================

def find_free_port(start=8470, end=8499):
    """Encontrar un puerto libre en el rango"""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def build_report_data(engine):
    """Construir el diccionario de datos del reporte a partir del engine v4"""
    from dataclasses import asdict

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
        'code_clones': code_clones[:100],  # Limitar a 100 para no sobrecargar
        'recommendations': engine._generate_recommendations(),
    }


def launch_web_gui(engine, auto_open=True):
    """
    Lanzar el servidor web con los datos del analisis.
    Abre el navegador automaticamente.

    Args:
        engine: Instancia de RedShadowV4 con analisis completado
        auto_open: Si True, abre el navegador automaticamente
    """
    report_data = build_report_data(engine)
    RedShadowHandler.report_data = report_data

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No se encontro un puerto libre para el servidor web\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] Servidor web iniciado en {url}\033[0m")
    print(f"\033[93m[INFO] Presiona Ctrl+C para detener el servidor y continuar\033[0m")

    if auto_open:
        # Abrir en un thread para no bloquear
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Servidor web detenido\033[0m")


def launch_web_gui_from_json(json_path, auto_open=True):
    """
    Lanzar el servidor web desde un archivo JSON de reporte existente.

    Args:
        json_path: Ruta al archivo JSON de reporte
        auto_open: Si True, abre el navegador automaticamente
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # Asegurar que tiene los campos minimos
    if 'stats' not in report_data:
        report_data['stats'] = {}
    if 'triggers' not in report_data:
        report_data['triggers'] = []

    RedShadowHandler.report_data = report_data

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No se encontro un puerto libre\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] Servidor web iniciado en {url}\033[0m")
    print(f"\033[93m[INFO] Presiona Ctrl+C para detener el servidor\033[0m")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Servidor web detenido\033[0m")


# ============================================================================
# STANDALONE USAGE
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\033[91mUso: python web_gui.py <reporte.json>\033[0m")
        print("\033[96mAbre un reporte JSON existente en el dashboard web.\033[0m")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"\033[91m[ERROR] Archivo no encontrado: {json_path}\033[0m")
        sys.exit(1)

    launch_web_gui_from_json(json_path)
