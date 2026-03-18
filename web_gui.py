#!/usr/bin/env python3
"""
RED-SHADOW v4.0 - Full Web GUI
Complete web application: dump selection, analysis and results dashboard.
Everything managed from the browser, no console needed.

No external dependencies - uses stdlib http.server.
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
    """Global application state"""
    report_data = None
    partial_data = None   # datos parciales durante el analisis (streaming)
    analysis_running = False
    analysis_progress = ""
    analysis_phase = ""   # fase actual
    analysis_phase_num = 0
    analysis_phase_total = 0
    analysis_error = None
    analysis_done = False
    dump_path = None


# ============================================================================
# HTML TEMPLATE - Landing page + Dashboard
# ============================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RED-SHADOW v4 - Trigger Finder</title>
<style>
:root {
    --bg: #0a0a0f; --bg2: #12121a; --bg3: #1a1a2e; --bgh: #22223a;
    --border: #2a2a3e; --t1: #e0e0e0; --t2: #888; --t3: #555;
    --red: #ff3344; --redd: #cc1133; --redg: rgba(255,51,68,.3);
    --green: #00cc66; --greend: #009944;
    --yellow: #ffcc00; --yellowd: #cc9900;
    --cyan: #00cccc; --cyand: #009999;
    --mag: #cc66ff; --ora: #ff8833; --crit: #ff0066;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--t1); font-family: 'Segoe UI','Consolas','Courier New',monospace; min-height: 100vh; overflow-x: hidden; }
.header { background: linear-gradient(180deg,var(--bg2) 0%,var(--bg) 100%); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
.header h1 { color: var(--red); font-size: 22px; text-shadow: 0 0 20px var(--redg); letter-spacing: 2px; }
.header .sub { color: var(--t2); font-size: 12px; }
.header .dpath { color: var(--cyan); font-size: 11px; opacity: .7; }

/* Landing */
.landing { display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:calc(100vh - 60px); padding:40px 20px; }
.lbox { background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:36px; max-width:580px; width:100%; text-align:center; }
.lbox h2 { color:var(--red); margin-bottom:6px; font-size:20px; }
.lbox p { color:var(--t2); margin-bottom:20px; font-size:13px; }
.linput { width:100%; background:var(--bg2); border:1px solid var(--border); border-radius:4px; padding:12px 14px; color:var(--t1); font-family:inherit; font-size:14px; outline:none; margin-bottom:12px; transition:border-color .2s; }
.linput:focus { border-color:var(--red); box-shadow:0 0 8px var(--redg); }
.linput::placeholder { color:var(--t3); }
.lbtn { width:100%; background:var(--redd); border:1px solid var(--red); border-radius:4px; padding:13px; color:#fff; font-family:inherit; font-size:15px; font-weight:bold; cursor:pointer; transition:all .2s; letter-spacing:1px; }
.lbtn:hover { background:var(--red); }
.lbtn:disabled { opacity:.5; cursor:not-allowed; }
.lhint { color:var(--t3); font-size:11px; margin-top:10px; }
/* Progress */
.prog { display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(10,10,15,.96); z-index:1000; flex-direction:column; align-items:center; justify-content:center; }
.prog.on { display:flex; }
.spin { display:inline-block; width:44px; height:44px; border:3px solid var(--border); border-top-color:var(--red); border-radius:50%; animation:spin .8s linear infinite; margin-bottom:18px; }
@keyframes spin { to { transform:rotate(360deg); } }
.prog-txt { color:var(--t1); font-size:15px; margin-bottom:8px; }
.prog-det { color:var(--t2); font-size:12px; min-height:18px; }
.prog-err { color:var(--red); font-size:13px; margin-top:14px; max-width:480px; word-break:break-word; }
/* Dashboard */
.dash { display:none; }
.dash.on { display:block; }
.nav { background:var(--bg2); border-bottom:1px solid var(--border); padding:0 16px; display:flex; flex-wrap:wrap; gap:1px; position:sticky; top:0; z-index:100; }
.nb { background:transparent; border:none; color:var(--t2); padding:11px 14px; cursor:pointer; font-family:inherit; font-size:12px; transition:all .2s; border-bottom:2px solid transparent; white-space:nowrap; }
.nb:hover { color:var(--t1); background:var(--bgh); }
.nb.on { color:var(--red); border-bottom-color:var(--red); }
.nb-new { background:transparent; border:1px solid var(--border); border-radius:4px; padding:7px 14px; color:var(--t2); cursor:pointer; font-family:inherit; font-size:12px; transition:all .2s; margin-left:auto; align-self:center; }
.nb-new:hover { border-color:var(--yellow); color:var(--yellow); }
.main { max-width:1400px; margin:0 auto; padding:18px; }
.sec { display:none; }
.sec.on { display:block; }
/* Cards */
.card { background:var(--bg3); border:1px solid var(--border); border-radius:6px; padding:18px; margin-bottom:14px; }
.ctitle { color:var(--cyan); font-size:14px; margin-bottom:12px; padding-bottom:7px; border-bottom:1px solid var(--border); letter-spacing:1px; }
/* Stats */
.sgrid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:10px; margin-bottom:18px; }
.sbox { background:var(--bg2); border:1px solid var(--border); border-radius:6px; padding:14px; text-align:center; }
.sval { font-size:26px; font-weight:bold; margin-bottom:3px; }
.slbl { font-size:10px; color:var(--t2); text-transform:uppercase; letter-spacing:1px; }
/* Table */
.dt { width:100%; border-collapse:collapse; font-size:12px; }
.dt th { background:var(--bg2); color:var(--cyan); padding:9px 10px; text-align:left; border:1px solid var(--border); font-weight:normal; text-transform:uppercase; font-size:10px; letter-spacing:1px; position:sticky; top:44px; z-index:10; }
.dt td { padding:7px 10px; border:1px solid var(--border); vertical-align:top; }
.dt tr:hover td { background:var(--bgh); }
.mono { font-family:'Consolas','Courier New',monospace; font-size:11px; }
/* Tags */
.tag { display:inline-block; padding:2px 7px; border-radius:3px; font-size:10px; font-weight:bold; margin:1px; }
.t-safe { background:var(--greend); color:#fff; }
.t-warn { background:var(--yellowd); color:#000; }
.t-danger { background:var(--redd); color:#fff; }
.t-crit { background:var(--crit); color:#fff; }
.t-hp { background:#ff0066; color:#fff; }
.t-ban { background:#cc0000; color:#fff; }
.t-val { background:var(--greend); color:#fff; }
.t-info { background:var(--cyand); color:#fff; }
.t-mag { background:var(--mag); color:#fff; }
/* Code */
.code { background:#0d0d12; border:1px solid var(--border); border-radius:4px; padding:10px; font-family:'Consolas','Courier New',monospace; font-size:12px; line-height:1.5; overflow-x:auto; color:var(--t2); max-height:180px; overflow-y:auto; white-space:pre-wrap; word-break:break-all; }
/* Search */
.sbox2 { display:flex; gap:8px; margin-bottom:14px; }
.sinput { flex:1; background:var(--bg2); border:1px solid var(--border); border-radius:4px; padding:9px 12px; color:var(--t1); font-family:inherit; font-size:13px; outline:none; transition:border-color .2s; }
.sinput:focus { border-color:var(--red); }
.sinput::placeholder { color:var(--t3); }
/* Filters */
.filters { display:flex; flex-wrap:wrap; gap:5px; margin-bottom:12px; }
.fb { background:var(--bg2); border:1px solid var(--border); border-radius:4px; padding:5px 12px; color:var(--t2); cursor:pointer; font-family:inherit; font-size:11px; transition:all .2s; }
.fb:hover,.fb.on { color:#fff; border-color:var(--red); background:rgba(255,51,68,.15); }
/* Exploit card */
.xcard { background:var(--bg2); border:1px solid var(--border); border-radius:6px; padding:14px; margin-bottom:10px; display:flex; align-items:flex-start; gap:12px; }
.xcard:hover { border-color:var(--greend); }
.xcard.hp { border-color:var(--crit) !important; }
.xname { font-size:14px; font-weight:bold; color:var(--green); font-family:'Consolas','Courier New',monospace; margin-bottom:4px; }
.xname.hp { color:var(--crit); }
.xline { font-family:'Consolas','Courier New',monospace; font-size:12px; color:var(--t2); background:#0d0d12; border:1px solid var(--border); border-radius:3px; padding:6px 10px; margin:6px 0; word-break:break-all; }
.xcopy { background:var(--greend); border:none; border-radius:4px; padding:7px 16px; color:#fff; cursor:pointer; font-family:inherit; font-size:12px; font-weight:bold; transition:all .2s; white-space:nowrap; flex-shrink:0; }
.xcopy:hover { background:var(--green); }
.xcopy.hp { background:var(--redd); }
.xcopy.hp:hover { background:var(--red); }
.xmeta { font-size:11px; color:var(--t3); margin-top:4px; }
/* Btn */
.btn { background:var(--bg3); border:1px solid var(--border); border-radius:4px; padding:7px 14px; color:var(--t1); cursor:pointer; font-family:inherit; font-size:12px; transition:all .2s; }
.btn:hover { border-color:var(--red); background:rgba(255,51,68,.1); }
.btn-g { background:var(--greend); border-color:var(--green); color:#fff; }
.btn-g:hover { background:var(--green); }
/* Risk */
.rs { color:var(--green); }
.rw { color:var(--yellow); }
.rd { color:var(--red); }
.rc { color:var(--crit); }
/* Conf bar */
.cb { display:inline-block; width:50px; height:5px; background:var(--bg); border-radius:3px; overflow:hidden; vertical-align:middle; margin-left:5px; }
.cbf { height:100%; border-radius:3px; }
/* Toast */
.toast { position:fixed; bottom:18px; right:18px; background:var(--bg3); border:1px solid var(--green); border-radius:6px; padding:10px 18px; color:var(--green); font-size:12px; z-index:10000; opacity:0; transform:translateY(8px); transition:all .3s; }
.toast.on { opacity:1; transform:translateY(0); }
/* AC card */
.accard { background:var(--bg2); border:1px solid var(--border); border-radius:6px; padding:14px; margin-bottom:10px; }
/* Scrollbar */
::-webkit-scrollbar { width:7px; height:7px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#444; }
@media(max-width:768px) { .sgrid { grid-template-columns:repeat(2,1fr); } .nb { padding:9px 9px; font-size:11px; } }
</style>
</head>
<body>

<div class="header">
    <div>
        <h1>🔥 RED-SHADOW v4</h1>
        <div class="sub">Trigger Finder &amp; Exploit Generator — Offline</div>
    </div>
    <div class="dpath" id="dump-path"></div>
</div>

<!-- LANDING -->
<div class="landing" id="landing">
  <div class="lbox">
    <h2>🔥 RED-SHADOW v4 — Trigger Finder</h2>
    <p>Analyze FiveM dumps offline. Generate ready-to-paste exploits for Ambani.</p>
    <label style="display:block;text-align:left;color:var(--t2);font-size:11px;margin-bottom:5px">📁 Dump path (.lua files)</label>
    <input type="text" class="linput" id="dump-input" placeholder="C:\Users\user\Desktop\FiveM_Dump" autofocus>

    <label style="display:block;text-align:left;color:var(--t2);font-size:11px;margin-bottom:5px">⚡ Ambani triggers.lua <span style="color:var(--green)">(optional)</span></label>
    <input type="text" class="linput" id="ambani-input" placeholder="C:\AmbaniFiles\xqw0FQ91\[Extracted]\triggers.lua">
    <div style="text-align:left;color:var(--t3);font-size:10px;margin-bottom:14px">triggers.lua only = instant analysis without full dump.</div>
    <button class="lbtn" id="analyze-btn" onclick="startAnalysis()">🔍 ANALYZE</button>
    <div class="lhint">✅ Undetected · ✅ Honeypots · ✅ Ready-to-copy exploits</div>
  </div>
</div>

<!-- PROGRESS -->
<div class="prog" id="prog">
  <div style="text-align:center;max-width:460px;padding:36px">
    <div class="spin"></div>
    <div class="prog-txt">Analyzing dump...</div>
    <div class="prog-det" id="prog-det">Starting...</div>
    <div class="prog-err" id="prog-err"></div>
  </div>
</div>

<!-- ==================== DASHBOARD ==================== -->
<div class="dash" id="dashboard">
  <nav class="nav" id="nav">
    <button class="nb on" data-s="summary">Summary</button>
    <button class="nb" data-s="exploitable">🎯 Exploitable</button>
    <button class="nb" data-s="knowndb">🗄️ Known DB</button>
    <button class="nb" data-s="triggers">Triggers</button>
    <button class="nb" data-s="honeypots">🍯 Honeypots</button>
    <button class="nb" data-s="webhooks">🔗 Webhooks</button>
    <button class="nb" data-s="anticheats">🛡️ Anticheats</button>
    <button class="nb" data-s="backdoors">Backdoors</button>
    <button class="nb" data-s="locations">🗺️ Spots</button>
    <button class="nb" data-s="resources">📦 Resources</button>
    <button class="nb" data-s="search">Search</button>
    <button class="nb-new" onclick="newAnalysis()">+ New</button>
  </nav>
  <div class="main">

    <!-- SUMMARY -->
    <div class="sec on" id="sec-summary">
      <div style="margin-bottom:12px"><button class="btn" onclick="downloadJSON()">⬇ Download JSON</button></div>
      <div class="sgrid" id="stats-grid"></div>
      <div class="card">
        <div class="ctitle">OVERALL RISK</div>
        <div id="risk-display"></div>
      </div>
      <div class="card">
        <div class="ctitle">RECOMMENDATIONS</div>
        <ul id="recommendations" style="padding-left:18px;font-size:13px;line-height:1.8;color:var(--t2)"></ul>
      </div>
    </div>

    <!-- EXPLOITABLE -->
    <div class="sec" id="sec-exploitable">
      <div class="filters" id="exploitable-filters">
        <button class="fb on" data-filter="all">All</button>
        <button class="fb" data-filter="money">💰 Money</button>
        <button class="fb" data-filter="item">📦 Items</button>
        <button class="fb" data-filter="xp">⭐ XP</button>
        <button class="fb" data-filter="other">🔧 Other</button>
      </div>
      <div id="exploitable-content"></div>
    </div>

    <!-- KNOWN DB -->
    <div class="sec" id="sec-knowndb">
      <div class="filters" id="knowndb-filters">
        <button class="fb on" data-filter="all">All</button>
        <button class="fb" data-filter="ready" style="border-color:var(--green)">✅ Ready</button>
        <button class="fb" data-filter="money">💰 Money</button>
        <button class="fb" data-filter="item">📦 Items</button>
        <button class="fb" data-filter="job">👔 Job</button>
        <button class="fb" data-filter="vehicle">🚗 Vehicles</button>
        <button class="fb" data-filter="ESX">ESX</button>
        <button class="fb" data-filter="QBCore">QBCore</button>
      </div>
      <div id="knowndb-content"></div>
    </div>

    <!-- TRIGGERS -->
    <div class="sec" id="sec-triggers">
      <div class="sbox2">
        <input type="text" class="sinput" id="trigger-search" placeholder="Filter by name...">
      </div>
      <div class="filters" id="trigger-filters">
        <button class="fb on" data-filter="all">All</button>
        <button class="fb" data-filter="safe">Safe</button>
        <button class="fb" data-filter="warn">Warning</button>
        <button class="fb" data-filter="danger">Dangerous</button>
        <button class="fb" data-filter="novalidation" style="border-color:var(--red)">🚨 No Validation</button>
        <button class="fb" data-filter="reward" style="border-color:var(--green)">💰 Has Reward</button>
      </div>
      <div id="triggers-table-wrap"></div>
    </div>

    <!-- HONEYPOTS -->
    <div class="sec" id="sec-honeypots">
      <div class="card" style="border-color:var(--crit)">
        <div class="ctitle" style="color:var(--crit)">🍯 HONEYPOTS — INSTANT BAN</div>
        <div id="honeypots-content"></div>
      </div>
    </div>

    <!-- WEBHOOKS -->
    <div class="sec" id="sec-webhooks">
      <div class="card" style="border-color:var(--ora)">
        <div class="ctitle" style="color:var(--ora)">🔗 HARDCODED WEBHOOKS</div>
        <div id="webhooks-content"></div>
      </div>
    </div>

    <!-- ANTICHEATS -->
    <div class="sec" id="sec-anticheats">
      <div id="anticheats-content"></div>
    </div>

    <!-- BACKDOORS -->
    <div class="sec" id="sec-backdoors">
      <div class="card" style="border-color:var(--crit)">
        <div class="ctitle" style="color:var(--crit)">DETECTED BACKDOORS</div>
        <div id="backdoors-content"></div>
      </div>
    </div>

    <!-- LOCATIONS -->
    <div class="sec" id="sec-locations">
      <div class="card">
        <div class="ctitle">🗺️ ILLEGAL SPOTS</div>
        <div class="filters" id="location-filters">
          <button class="fb on" data-filter="all">All</button>
          <button class="fb" data-filter="weed" style="border-color:#00cc66">🌿 Weed</button>
          <button class="fb" data-filter="meth" style="border-color:#00cccc">🧪 Meth</button>
          <button class="fb" data-filter="cocaine" style="border-color:#ffffff">❄️ Cocaine</button>
          <button class="fb" data-filter="heroin" style="border-color:#cc66ff">💉 Heroin</button>
          <button class="fb" data-filter="mdma" style="border-color:#ff8833">💊 MDMA</button>
          <button class="fb" data-filter="lsd" style="border-color:#ff3344">🔮 LSD</button>
          <button class="fb" data-filter="mush" style="border-color:#cc9900">🍄 Mush</button>
          <button class="fb" data-filter="generic">🎯 Generic</button>
          <button class="fb" data-filter="robbery" style="border-color:#ff3344">🔫 Robbery</button>
          <button class="fb" data-filter="chop_shop" style="border-color:#ff8833">🚗 Chop Shop</button>
          <button class="fb" data-filter="arms_dealing" style="border-color:#cc66ff">💣 Arms</button>
          <button class="fb" data-filter="illegal_mining" style="border-color:#cc9900">⛏️ Mining</button>
          <button class="fb" data-filter="illegal_trade" style="border-color:#888">🖤 Black Market</button>
        </div>
        <div style="margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap">
          <button class="btn" onclick="downloadLocationsCSV()">Export CSV</button>
          <button class="btn" onclick="downloadLocationsJSON()">Export JSON</button>
          <button class="btn" onclick="downloadLocationsLua()">Export Lua</button>
        </div>
        <div id="locations-content"></div>
      </div>
    </div>

    <!-- RESOURCES -->
    <div class="sec" id="sec-resources">
      <div style="margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-g" onclick="downloadLua()">⬇ Export Lua</button>
        <button class="btn" style="border-color:var(--cyan);color:var(--cyan)" onclick="downloadAmbani()">⬇ Export Ambani</button>
      </div>
      <div id="resources-content"></div>
    </div>

    <!-- SEARCH -->
    <div class="sec" id="sec-search">
      <div class="sbox2">
        <input type="text" class="sinput" id="global-search" placeholder="Search trigger by name...">
        <button class="btn btn-g" onclick="doGlobalSearch()">Search</button>
      </div>
      <div id="search-results"></div>
    </div>

  </div>
</div>

<div class="toast" id="toast"></div>

<script>
var DATA = null;
var curSec = 'summary';
var triggerFilter = 'all';

// PAGE ROUTING
function showLanding() {
    document.getElementById('landing').style.display = 'flex';
    document.getElementById('dashboard').classList.remove('on');
    document.getElementById('prog').classList.remove('on');
    document.getElementById('dump-path').textContent = '';
    document.getElementById('dump-input').value = '';
    document.getElementById('ambani-input').value = '';
    document.getElementById('dump-input').focus();
}

function showProgress() {
    document.getElementById('landing').style.display = 'none';
    document.getElementById('dashboard').classList.remove('on');
    document.getElementById('prog').classList.add('on');
    document.getElementById('prog-err').textContent = '';
}

function showDashboard() {
    document.getElementById('landing').style.display = 'none';
    document.getElementById('prog').classList.remove('on');
    document.getElementById('dashboard').classList.add('on');
    document.getElementById('dump-path').textContent = 'Dump: ' + (DATA.dump_path || 'N/A');
    renderSummary();
    showSection('summary');
}

function newAnalysis() { DATA = null; showLanding(); }

// ANALYSIS FLOW
function startAnalysis() {
    var path = document.getElementById('dump-input').value.trim();
    var ambaniPath = document.getElementById('ambani-input').value.trim();
    if (!path && !ambaniPath) { document.getElementById('dump-input').focus(); return; }
    document.getElementById('analyze-btn').disabled = true;
    showProgress();
    fetch('/api/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path: path, ambani_triggers: ambaniPath})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) {
            document.getElementById('prog-err').textContent = 'Error: ' + d.error;
            document.getElementById('analyze-btn').disabled = false;
            setTimeout(showLanding, 3000);
            return;
        }
        pollStatus();
    })
    .catch(function(e) {
        document.getElementById('prog-err').textContent = 'Connection error: ' + e.message;
        document.getElementById('analyze-btn').disabled = false;
    });
}

function pollStatus() {
    fetch('/api/status')
    .then(function(r) { return r.json(); })
    .then(function(d) {
        document.getElementById('prog-det').textContent = d.progress || '';
        if (d.error) { document.getElementById('prog-err').textContent = 'Error: ' + d.error; document.getElementById('analyze-btn').disabled = false; return; }
        if (d.done) {
            fetch('/api/data').then(function(r) { return r.json(); }).then(function(data) {
                DATA = data; document.getElementById('analyze-btn').disabled = false; showDashboard();
            });
            return;
        }
        setTimeout(pollStatus, 500);
    })
    .catch(function() { setTimeout(pollStatus, 1000); });
}

document.getElementById('dump-input').addEventListener('keydown', function(e) { if (e.key === 'Enter') startAnalysis(); });

// NAVIGATION
document.getElementById('nav').addEventListener('click', function(e) {
    var b = e.target.closest('.nb');
    if (b && b.dataset.s) showSection(b.dataset.s);
});

function showSection(name) {
    curSec = name;
    document.querySelectorAll('.nb').forEach(function(b) { b.classList.toggle('on', b.dataset.s === name); });
    document.querySelectorAll('.sec').forEach(function(s) { s.classList.remove('on'); });
    var el = document.getElementById('sec-' + name);
    if (el) el.classList.add('on');
    var r = {summary:renderSummary, exploitable:renderExploitable, knowndb:renderKnownDB,
             triggers:renderTriggers, honeypots:renderHoneypots, webhooks:renderWebhooks,
             anticheats:renderAnticheats, backdoors:renderBackdoors, locations:renderLocations,
             resources:renderResources, search:function(){}};
    if (r[name] && DATA) r[name]();
}

// HELPERS
function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') : ''; }
function riskCls(s) { return s >= 70 ? 'rc' : s >= 40 ? 'rw' : 'rs'; }
function riskColor(s) { return s >= 70 ? 'var(--red)' : s >= 40 ? 'var(--yellow)' : 'var(--green)'; }
function tagHTML(t, c) { return '<span class="tag t-' + c + '">' + esc(t) + '</span>'; }
function confBar(v) {
    var p = Math.round(v * 100);
    var c = v > 0.7 ? 'var(--red)' : v > 0.3 ? 'var(--yellow)' : 'var(--green)';
    return p + '% <span class="cb"><span class="cbf" style="width:' + p + '%;background:' + c + '"></span></span>';
}
function shortPath(p) { if (!p) return ''; var a = p.replace(/\\/g, '/').split('/'); return a.length > 2 ? '.../' + a.slice(-2).join('/') : p; }
function showToast(m) { var t = document.getElementById('toast'); t.textContent = m; t.classList.add('on'); setTimeout(function() { t.classList.remove('on'); }, 2500); }
function downloadJSON() {
    if (!DATA) return;
    var b = new Blob([JSON.stringify(DATA, null, 2)], {type: 'application/json'});
    var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'red_shadow_report.json'; a.click();
    showToast('JSON downloaded');
}
function copyText(txt, label) {
    navigator.clipboard.writeText(txt).then(function() { showToast('Copied: ' + (label||'')); }).catch(function() { showToast(txt.substring(0,60)); });
}
function buildTriggerLine(name, rewardType) {
    var line = 'TriggerServerEvent("' + name + '"';
    if (rewardType === 'money') line += ', 999999';
    else if (rewardType === 'item') line += ', "bread", 100';
    else if (rewardType === 'xp') line += ', 10000';
    return line + ')';
}

// RENDER: SUMMARY
function renderSummary() {
    var s = DATA.stats; var triggers = DATA.triggers || [];
    var honeypots = triggers.filter(function(t) { return t.is_honeypot; }).length;
    var exploitable = triggers.filter(function(t) { return !t.is_honeypot && t.has_reward_logic; }).length;
    var knownReady = (DATA.known_triggers || []).filter(function(k) { return k.ready_to_use; }).length;
    var oR = triggers.length > 0 ? triggers.reduce(function(a, t) { return a + t.risk_score; }, 0) / triggers.length : 0;

    document.getElementById('stats-grid').innerHTML = [
        {v: s.triggers, l: 'Triggers', c: 'var(--cyan)'},
        {v: exploitable, l: 'Exploitable', c: 'var(--green)'},
        {v: knownReady, l: 'Known DB Ready', c: 'var(--mag)'},
        {v: honeypots, l: 'Honeypots', c: 'var(--crit)'},
        {v: s.backdoors || 0, l: 'Backdoors', c: 'var(--crit)'},
        {v: s.anticheats, l: 'Anticheats', c: 'var(--yellow)'},
        {v: s.webhooks || 0, l: 'Webhooks', c: 'var(--ora)'},
        {v: s.rp_locations || 0, l: 'Spots', c: 'var(--cyan)'}
    ].map(function(i) {
        return '<div class="sbox"><div class="sval" style="color:' + i.c + '">' + i.v + '</div><div class="slbl">' + i.l + '</div></div>';
    }).join('');

    var rc = riskColor(oR);
    document.getElementById('risk-display').innerHTML = '<div style="font-size:36px;font-weight:bold;color:' + rc + ';margin-bottom:8px">' + oR.toFixed(1) + '%</div>';
    var recs = DATA.recommendations || [];
    document.getElementById('recommendations').innerHTML = recs.length > 0 ? recs.map(function(r) { return '<li>' + esc(r) + '</li>'; }).join('') : '<li>No recommendations.</li>';
}

// RENDER: EXPLOITABLE — action cards X9-style
var exploitableFilter = 'all';

function renderExploitable() {
    var triggers = (DATA.triggers || []).filter(function(t) { return !t.is_honeypot && t.has_reward_logic; });
    if (exploitableFilter !== 'all') {
        if (exploitableFilter === 'other') {
            triggers = triggers.filter(function(t) { return !t.reward_type || (t.reward_type !== 'money' && t.reward_type !== 'item' && t.reward_type !== 'xp'); });
        } else {
            triggers = triggers.filter(function(t) { return t.reward_type === exploitableFilter; });
        }
    }
    triggers.sort(function(a, b) { return a.risk_score - b.risk_score; });

    if (triggers.length === 0) {
        document.getElementById('exploitable-content').innerHTML = '<p style="color:var(--yellow);padding:20px">No exploitable triggers with these filters.</p>';
        return;
    }

    var html = '<p style="margin-bottom:12px;color:var(--t2);font-size:12px"><strong style="color:var(--green)">' + triggers.length + '</strong> exploitable triggers</p>';
    triggers.forEach(function(t) {
        var line = buildTriggerLine(t.event_name, t.reward_type);
        var rIcon = t.reward_type === 'money' ? '💰' : t.reward_type === 'item' ? '📦' : t.reward_type === 'xp' ? '⭐' : '🔧';
        var safeTag = !t.has_validation ? '<span class="tag t-safe">NO VAL</span>' : '<span class="tag t-warn">HAS VAL</span>';
        var rlTag = !t.has_rate_limiting ? '' : '<span class="tag t-warn">RATE LIMIT</span>';
        var vsColors = {none:'var(--green)',weak:'var(--yellow)',strong:'var(--red)'};
        var vsTag = t.validation_strength ? '<span class="tag" style="background:' + (vsColors[t.validation_strength]||'var(--t3)') + ';color:#000">' + (t.validation_strength||'').toUpperCase() + '</span>' : '';
        var fwTag = t.framework ? '<span class="tag t-info" style="font-size:10px">' + esc(t.framework) + '</span>' : '';
        var riskTag = '<span class="' + riskCls(t.risk_score) + '" style="font-size:11px">' + t.risk_score.toFixed(0) + '%</span>';
        var safeId = 'xc_' + t.event_name.replace(/[^a-zA-Z0-9]/g,'_');
        html += '<div class="xcard">';
        html += '<div style="flex:1;min-width:0">';
        html += '<div class="xname">' + rIcon + ' ' + esc(t.event_name) + '</div>';
        html += '<div class="xline">' + esc(line) + '</div>';
        html += '<div class="xmeta">' + safeTag + ' ' + rlTag + ' ' + vsTag + ' ' + fwTag + ' ' + riskTag + ' &nbsp; <span style="color:var(--t3)">' + esc(shortPath(t.file)) + ':' + t.line + '</span></div>';
        html += '</div>';
        html += '<button class="xcopy" id="' + safeId + '" onclick="copyText(' + JSON.stringify(line) + ',' + JSON.stringify(t.event_name) + ')">📋 Copy</button>';
        html += '</div>';
    });
    document.getElementById('exploitable-content').innerHTML = html;
}

document.getElementById('exploitable-filters').addEventListener('click', function(e) {
    var b = e.target.closest('.fb');
    if (b) {
        exploitableFilter = b.dataset.filter;
        document.querySelectorAll('#exploitable-filters .fb').forEach(function(x) { x.classList.toggle('on', x.dataset.filter === exploitableFilter); });
        renderExploitable();
    }
});

// RENDER: TRIGGERS
function renderTriggers() {
    var triggers = DATA.triggers || [];
    var search = (document.getElementById('trigger-search').value || '').toLowerCase();
    var filtered = triggers.filter(function(t) {
        if (search && t.event_name.toLowerCase().indexOf(search) === -1) return false;
        if (triggerFilter === 'safe') return t.risk_score < 40;
        if (triggerFilter === 'warn') return t.risk_score >= 40 && t.risk_score < 70;
        if (triggerFilter === 'danger') return t.risk_score >= 70;
        if (triggerFilter === 'novalidation') return !t.has_validation;
        if (triggerFilter === 'reward') return t.has_reward_logic;
        return true;
    });
    filtered.sort(function(a, b) { return b.risk_score - a.risk_score; });

    if (filtered.length === 0) {
        document.getElementById('triggers-table-wrap').innerHTML = '<p style="color:var(--t2);padding:20px">No results.</p>';
        return;
    }

    var html = '<p style="margin-bottom:10px;color:var(--t2);font-size:12px">Total: <strong style="color:var(--cyan)">' + filtered.length + '</strong></p>';
    html += '<table class="dt"><tr><th>Trigger</th><th>Type</th><th>Framework</th><th>File</th><th>Tags</th><th>Val</th><th>Risk</th><th>Copy</th></tr>';
    filtered.forEach(function(t) {
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'hp');
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban');
        if (t.has_validation) tags += tagHTML('VAL', 'val');
        if (t.has_reward_logic) tags += tagHTML(t.reward_type || 'REWARD', 'info');
        var vsColors = {none:'var(--green)',weak:'var(--yellow)',strong:'var(--red)'};
        var vs = t.validation_strength || 'none';
        var vsCell = '<span style="color:' + (vsColors[vs]||'var(--t3)') + ';font-weight:bold;font-size:11px">' + vs.toUpperCase() + '</span>';
        var fwCell = t.framework ? '<span class="tag t-info" style="font-size:10px">' + esc(t.framework) + '</span>' : '<span style="color:var(--t3)">—</span>';
        var line = buildTriggerLine(t.event_name, t.reward_type);
        html += '<tr>';
        html += '<td class="mono" style="color:var(--green)">' + esc(t.event_name) + '</td>';
        html += '<td>' + esc(t.event_type) + '</td>';
        html += '<td>' + fwCell + '</td>';
        html += '<td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td>';
        html += '<td>' + tags + '</td>';
        html += '<td>' + vsCell + '</td>';
        html += '<td class="' + riskCls(t.risk_score) + '" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td>';
        html += '<td><button class="xcopy" style="padding:4px 10px;font-size:11px" onclick="copyText(' + JSON.stringify(line) + ',' + JSON.stringify(t.event_name) + ')">📋</button></td>';
        html += '</tr>';
    });
    html += '</table>';
    document.getElementById('triggers-table-wrap').innerHTML = html;
}

document.getElementById('trigger-search').addEventListener('input', function() { if (curSec === 'triggers') renderTriggers(); });
document.getElementById('trigger-filters').addEventListener('click', function(e) {
    var b = e.target.closest('.fb');
    if (b) {
        triggerFilter = b.dataset.filter;
        document.querySelectorAll('#trigger-filters .fb').forEach(function(x) { x.classList.toggle('on', x.dataset.filter === triggerFilter); });
        renderTriggers();
    }
});

// RENDER: HONEYPOTS
function renderHoneypots() {
    var triggers = (DATA.triggers || []).filter(function(t) { return t.is_honeypot; });
    if (triggers.length === 0) { document.getElementById('honeypots-content').innerHTML = '<p style="color:var(--green)">No honeypots detected.</p>'; return; }
    var html = '<table class="dt"><tr><th>Trigger</th><th>Type</th><th>File</th><th>Ban</th><th>Risk</th></tr>';
    triggers.forEach(function(t) {
        html += '<tr><td class="mono" style="color:var(--crit)">' + esc(t.event_name) + '</td><td>' + esc(t.event_type) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</td><td>' + (t.has_ban_logic ? tagHTML('YES', 'danger') : 'NO') + '</td><td class="rc" style="font-weight:bold">' + t.risk_score.toFixed(0) + '%</td></tr>';
    });
    html += '</table>';
    document.getElementById('honeypots-content').innerHTML = html;
}

// RENDER: ANTICHEATS
function renderAnticheats() {
    var acs = DATA.anticheats || {}; var keys = Object.keys(acs);
    if (keys.length === 0) { document.getElementById('anticheats-content').innerHTML = '<div class="card"><p style="color:var(--green)">No anticheats detected.</p></div>'; return; }
    var html = '';
    keys.forEach(function(n) {
        var a = acs[n];
        var isFramework = a.risk_level === 'FRAMEWORK';
        var rlColor = {HIGH:'var(--red)', MEDIUM:'var(--yellow)', LOW:'var(--green)', FRAMEWORK:'var(--cyan)', UNKNOWN:'var(--t3)'}[a.risk_level] || 'var(--t3)';
        var safeIcon = a.safe_to_disable === true ? '<span style="color:var(--green)">✅ Safe to disable</span>' : a.safe_to_disable === false ? '<span style="color:var(--red)">⛔ DO NOT disable</span>' : '<span style="color:var(--yellow)">⚠️ Verify</span>';
        var borderColor = isFramework ? 'var(--cyan)' : a.safe_to_disable === false ? 'var(--red)' : 'var(--border)';
        html += '<div class="accard" style="border-left:3px solid ' + borderColor + ';margin-bottom:12px">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
        html += '<div style="font-size:15px;font-weight:bold;color:' + rlColor + '">' + esc(n) + '</div>';
        html += '<div>' + safeIcon + ' &nbsp; ' + confBar(a.confidence) + '</div></div>';
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px">';
        html += '<div><span style="color:var(--t2)">Description: </span>' + esc(a.description) + '</div>';
        html += '<div><span style="color:var(--t2)">Detection: </span>' + esc(a.detection_method || 'Unknown') + '</div>';
        html += '</div>';
        if (a.disable_method) {
            html += '<div style="margin-top:8px;padding:8px;background:var(--bg);border-radius:4px;font-size:12px"><span style="color:var(--t2)">How to handle: </span>' + esc(a.disable_method) + '</div>';
        }
        if (a.bypass_notes) {
            html += '<div style="margin-top:6px;padding:8px;background:rgba(0,204,102,.05);border-radius:4px;font-size:12px;color:var(--green)">' + esc(a.bypass_notes) + '</div>';
        }
        html += '</div>';
    });
    document.getElementById('anticheats-content').innerHTML = html;
}

// RENDER: BACKDOORS
function renderBackdoors() {
    var backdoors = DATA.backdoors || [];
    if (backdoors.length === 0) { document.getElementById('backdoors-content').innerHTML = '<p style="color:var(--green)">No backdoors detected.</p>'; return; }
    backdoors.sort(function(a, b) { return (a.severity === 'CRITICAL' ? 0 : 1) - (b.severity === 'CRITICAL' ? 0 : 1); });
    var st = {CRITICAL:'crit', HIGH:'danger'};
    var html = '<table class="dt"><tr><th>Type</th><th>Severity</th><th>Confidence</th><th>File</th><th>Description</th></tr>';
    backdoors.forEach(function(b) {
        html += '<tr><td>' + esc(b.backdoor_type.replace(/_/g,' ')) + '</td><td>' + tagHTML(b.severity, st[b.severity]||'danger') + '</td><td>' + confBar(b.confidence) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(b.file)) + ':' + b.line + '</td><td style="font-size:12px">' + esc(b.description) + '</td></tr>';
    });
    html += '</table>';
    var html = '<table class="dt"><tr><th>Tipo</th><th>Severidad</th><th>Confianza</th><th>Archivo</th><th>Descripcion</th></tr>';
    backdoors.forEach(function(b) {
        html += '<tr><td>' + esc(b.backdoor_type.replace(/_/g,' ')) + '</td><td>' + tagHTML(b.severity, st[b.severity]||'danger') + '</td><td>' + confBar(b.confidence) + '</td><td class="mono" style="font-size:11px">' + esc(shortPath(b.file)) + ':' + b.line + '</td><td style="font-size:12px">' + esc(b.description) + '</td></tr>';
    });
    html += '</table>';
    document.getElementById('backdoors-content').innerHTML = html;
}

// RENDER: LOCATIONS
var locationFilter = 'all';

var drugColors = {
    weed:    '#00cc66',
    meth:    '#00cccc',
    cocaine: '#e0e0e0',
    heroin:  '#cc66ff',
    mdma:    '#ff8833',
    lsd:     '#ff3344',
    mush:    '#cc9900',
    generic: '#888'
};
var drugIcons = {
    weed:'🌿', meth:'🧪', cocaine:'❄️', heroin:'💉', mdma:'💊', lsd:'🔮', mush:'🍄', generic:'🎯'
};

function getDrugType(loc) {
    if (loc.drug_type) return loc.drug_type;
    var parts = (loc.activity_type || '').split('_');
    if (parts[0] === 'drug' && parts.length >= 2) return parts[1];
    return 'generic';
}

function getIllegalType(loc) {
    var at = loc.activity_type || '';
    if (at.startsWith('illegal_')) return at.replace('illegal_', '');
    return null;
}

function getOperationType(loc) {
    var parts = (loc.activity_type || '').split('_');
    if (parts[0] === 'drug' && parts.length >= 3) return parts.slice(2).join('_');
    return '';
}

function getScriptName(loc) {
    var fp = loc.file_path || '';
    var parts = fp.replace(/\\/g, '/').split('/');
    if (parts.length >= 2) return parts[parts.length - 2];
    return parts[parts.length - 1] || 'unknown';
}

function matchesFilter(loc, filter) {
    if (filter === 'all') return true;
    var at = loc.activity_type || '';
    if (['weed','meth','cocaine','heroin','mdma','lsd','mush','generic'].indexOf(filter) >= 0) {
        return getDrugType(loc) === filter;
    }
    if (filter === 'robbery') return at.startsWith('illegal_robbery') || at.startsWith('illegal_heist');
    if (filter === 'chop_shop') return at.startsWith('illegal_chop');
    if (filter === 'arms_dealing') return at.startsWith('illegal_arms');
    if (filter === 'illegal_mining') return at.startsWith('illegal_mining');
    if (filter === 'illegal_trade') return at.startsWith('illegal_trade');
    return false;
}

function renderLocations() {
    var locations = DATA.rp_locations || [];
    if (locations.length === 0) { document.getElementById('locations-content').innerHTML = '<p style="color:var(--yellow);padding:20px">No illegal spots detected.</p>'; return; }
    var filtered = locations.filter(function(loc) { return matchesFilter(loc, locationFilter); });
    filtered.sort(function(a, b) { return b.risk_score - a.risk_score; });
    var html = '<p style="margin-bottom:12px;color:var(--t2);font-size:12px">Total: <strong style="color:var(--cyan)">' + filtered.length + '</strong></p>';
    filtered.forEach(function(loc) { html += renderLocationCard(loc); });
    document.getElementById('locations-content').innerHTML = html;
}

function renderLocationCard(loc) {
    var at = loc.activity_type || '';
    var isIllegal = at.startsWith('illegal_');
    var dtype = isIllegal ? null : getDrugType(loc);
    var illegalType = isIllegal ? getIllegalType(loc) : null;
    var illegalColors = {robbery:'#ff3344',heist:'#ff3344',chop_shop:'#ff8833',chop:'#ff8833',arms_dealing:'#cc66ff',arms:'#cc66ff',illegal_mining:'#cc9900',mining:'#cc9900',illegal_trade:'#888',trade:'#888'};
    var dcolor = isIllegal ? (illegalColors[illegalType] || '#888') : (drugColors[dtype] || '#888');
    var illegalIcons = {robbery:'\uD83D\uDD2B',heist:'\uD83D\uDD2B',chop_shop:'\uD83D\uDE97',chop:'\uD83D\uDE97',arms_dealing:'\uD83D\uDCA3',arms:'\uD83D\uDCA3',illegal_mining:'\u26CF\uFE0F',mining:'\u26CF\uFE0F',illegal_trade:'\uD83D\uDDA4',trade:'\uD83D\uDDA4'};
    var dicon = isIllegal ? (illegalIcons[illegalType] || '\u26A0\uFE0F') : (drugIcons[dtype] || '\uD83C\uDFAF');
    var opType = getOperationType(loc);
    var opLabel = opType ? (' \u2014 ' + opType) : '';
    var tagLabel = isIllegal ? (illegalType || 'ILLEGAL').toUpperCase() : (dtype || 'generic').toUpperCase() + opLabel;
    var coords = loc.coords || {};
    var coordStr = 'vector3(' + (coords.x||0).toFixed(1) + ', ' + (coords.y||0).toFixed(1) + ', ' + (coords.z||0).toFixed(1) + ')';
    var scriptName = getScriptName(loc);
    var card = '<div class="card" style="border-left:3px solid ' + dcolor + '">';
    card += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
    card += '<div style="font-size:14px;font-weight:bold;color:' + dcolor + '">' + dicon + ' ' + esc(loc.location_name) + '</div>';
    card += '<div style="display:flex;align-items:center;gap:8px">';
    card += '<span class="tag" style="background:' + dcolor + ';color:#000;font-weight:bold">' + tagLabel + '</span>';
    card += '<span class="' + riskCls(loc.risk_score) + '" style="font-weight:bold">' + loc.risk_score.toFixed(0) + '%</span>';
    card += '</div></div>';
    card += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">';
    card += '<span class="mono" style="color:var(--cyan);font-size:12px">' + esc(coordStr) + '</span>';
    card += '<button class="xcopy" style="padding:4px 10px;font-size:11px" onclick="copyText(' + JSON.stringify(coordStr) + ',\'coords\')">\uD83D\uDCCB</button>';
    card += '</div>';
    card += '<div style="font-size:11px;color:var(--t3);display:flex;gap:12px">';
    card += '<span>\uD83D\uDCC1 <span style="color:var(--yellow)">' + esc(scriptName) + '</span></span>';
    card += '<span>' + esc(shortPath(loc.file_path)) + ':' + loc.line_number + '</span>';
    card += '</div>';
    if (loc.context_code) card += '<div class="code" style="margin-top:8px;max-height:80px">' + esc(loc.context_code) + '</div>';
    card += '</div>';
    return card;
}
document.getElementById('location-filters').addEventListener('click', function(e) {
    var b = e.target.closest('.fb');
    if (b) {
        locationFilter = b.dataset.filter;
        document.querySelectorAll('#location-filters .fb').forEach(function(x) { x.classList.toggle('on', x.dataset.filter === locationFilter); });
        renderLocations();
    }
});

// ============================================================================
// EXPORT: LOCATIONS
// ============================================================================

function getFilteredLocations() {
    var locations = (DATA && DATA.rp_locations) ? DATA.rp_locations : [];
    if (locationFilter !== 'all') {
        locations = locations.filter(function(loc) { return getDrugType(loc) === locationFilter; });
    }
    locations = locations.slice().sort(function(a, b) { return b.risk_score - a.risk_score; });
    return locations;
}

function triggerDownload(content, filename, mimeType) {
    var blob = new Blob([content], { type: mimeType });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadLocationsCSV() {
    var locations = getFilteredLocations();
    if (locations.length === 0) { showToast('No locations to export'); return; }
    var rows = ['name,x,y,z,activity,category,risk,confidence,file,line'];
    locations.forEach(function(loc) {
        var coords = loc.coords || {};
        var row = [
            '"' + (loc.location_name || '').replace(/"/g, '""') + '"',
            (coords.x !== undefined ? coords.x : 0),
            (coords.y !== undefined ? coords.y : 0),
            (coords.z !== undefined ? coords.z : 0),
            '"' + (loc.activity_type || '').replace(/"/g, '""') + '"',
            '"' + (loc.category || '').replace(/"/g, '""') + '"',
            (loc.risk_score !== undefined ? loc.risk_score : 0),
            (loc.confidence !== undefined ? loc.confidence : 0),
            '"' + (loc.file_path || '').replace(/"/g, '""') + '"',
            (loc.line_number !== undefined ? loc.line_number : 0)
        ];
        rows.push(row.join(','));
    });
    triggerDownload(rows.join('\n'), 'locations.csv', 'text/csv;charset=utf-8;');
    showToast('CSV exported (' + locations.length + ' locations)');
}

function downloadLocationsJSON() {
    var locations = getFilteredLocations();
    if (locations.length === 0) { showToast('No locations to export'); return; }
    var output = JSON.stringify({ locations: locations, count: locations.length, filter: locationFilter }, null, 2);
    triggerDownload(output, 'locations.json', 'application/json');
    showToast('JSON exported (' + locations.length + ' locations)');
}

function downloadLocationsLua() {
    var locations = getFilteredLocations();
    if (locations.length === 0) { showToast('No locations to export'); return; }
    var lines = ['-- RED-SHADOW DESTROYER v4 - Exported Locations', '-- Filter: ' + locationFilter, '-- Count: ' + locations.length, '', 'local Locations = {'];
    locations.forEach(function(loc) {
        var coords = loc.coords || {};
        var x = (coords.x !== undefined ? coords.x : 0).toFixed(4);
        var y = (coords.y !== undefined ? coords.y : 0).toFixed(4);
        var z = (coords.z !== undefined ? coords.z : 0).toFixed(4);
        var name = (loc.location_name || 'unknown').replace(/['"\\]/g, '_');
        var activity = (loc.activity_type || 'unknown').replace(/['"\\]/g, '_');
        lines.push('    {');
        lines.push('        name = "' + name + '",');
        lines.push('        coords = vector3(' + x + ', ' + y + ', ' + z + '),');
        lines.push('        activity = "' + activity + '",');
        lines.push('        category = "' + (loc.category || 'unknown') + '",');
        lines.push('        risk = ' + (loc.risk_score !== undefined ? loc.risk_score.toFixed(1) : '0.0') + ',');
        lines.push('    },');
    });
    lines.push('}');
    lines.push('');
    lines.push('return Locations');
    triggerDownload(lines.join('\n'), 'locations.lua', 'text/plain;charset=utf-8;');
    showToast('Lua exported (' + locations.length + ' locations)');
}

// RENDER: WEBHOOKS
function renderWebhooks() {
    var webhooks = DATA.webhooks || [];
    if (webhooks.length === 0) { document.getElementById('webhooks-content').innerHTML = '<p style="color:var(--green)">No hardcoded webhooks detected.</p>'; return; }
    webhooks.sort(function(a, b) { return a.file.localeCompare(b.file); });
    var html = '<p style="margin-bottom:10px;color:var(--t2);font-size:12px">Total: <strong style="color:var(--ora)">' + webhooks.length + '</strong></p>';
    html += '<table class="dt"><tr><th>URL</th><th>Type</th><th>File</th><th>Line</th><th>Copy</th></tr>';
    webhooks.forEach(function(w) {
        var typeColor = w.webhook_type === 'discord' ? 'var(--mag)' : 'var(--ora)';
        html += '<tr>';
        html += '<td class="mono" style="font-size:11px;max-width:360px;overflow:hidden;text-overflow:ellipsis;color:var(--cyan)">' + esc(w.url) + '</td>';
        html += '<td><span class="tag" style="background:' + typeColor + ';color:#fff">' + esc(w.webhook_type.toUpperCase()) + '</span></td>';
        html += '<td class="mono" style="font-size:11px">' + esc(shortPath(w.file)) + '</td>';
        html += '<td>' + w.line + '</td>';
        html += '<td><button class="xcopy" style="padding:4px 10px;font-size:11px" onclick="copyText(' + JSON.stringify(w.url) + ',\'webhook\')">📋</button></td>';
        html += '</tr>';
    });
    html += '</table>';
    document.getElementById('webhooks-content').innerHTML = html;
}

// RENDER: KNOWN DB
var knowndbFilter = 'all';

function renderKnownDB() {
    var items = DATA.known_triggers || [];
    if (items.length === 0) { document.getElementById('knowndb-content').innerHTML = '<div class="card"><p style="color:var(--yellow)">No matches found in the database.</p></div>'; return; }

    var filtered = items.filter(function(k) {
        if (knowndbFilter === 'ready') return k.ready_to_use;
        if (knowndbFilter === 'money') return k.category === 'money';
        if (knowndbFilter === 'item') return k.category === 'item';
        if (knowndbFilter === 'job') return k.category === 'job' || k.category === 'admin';
        if (knowndbFilter === 'vehicle') return k.category === 'vehicle';
        if (knowndbFilter === 'ESX') return k.framework === 'ESX';
        if (knowndbFilter === 'QBCore') return k.framework === 'QBCore';
        return true;
    });

    var ready = filtered.filter(function(k) { return k.ready_to_use; }).length;
    var html = '<p style="margin-bottom:12px;color:var(--t2);font-size:12px">Matches: <strong style="color:var(--mag)">' + filtered.length + '</strong> — <strong style="color:var(--green)">' + ready + '</strong> ready</p>';
    var riskColor2 = {CRITICAL:'var(--crit)',HIGH:'var(--red)',MEDIUM:'var(--yellow)',LOW:'var(--green)'};
    var catIcon = {money:'💰',item:'📦',job:'👔',admin:'🔑',vehicle:'🚗',weapon:'🔫',framework:'⚙️'};

    filtered.forEach(function(k) {
        var rc = riskColor2[k.risk] || 'var(--t2)';
        var icon = catIcon[k.category] || '🔧';
        var readyBadge = k.ready_to_use ? '<span class="tag t-safe">✅ READY</span>' : (k.is_honeypot ? '<span class="tag t-hp">🍯 HONEYPOT</span>' : '<span class="tag t-warn">⚠️ VALIDATED</span>');
        var partialBadge = k.partial_match ? '<span class="tag t-info" style="font-size:10px">~PARTIAL</span> ' : '';

        html += '<div class="xcard" style="border-left:3px solid ' + rc + '">';
        html += '<div style="flex:1;min-width:0">';
        html += '<div class="xname" style="color:' + rc + '">' + icon + ' ' + esc(k.name) + ' ' + partialBadge + readyBadge + '</div>';
        if (k.exploit) html += '<div class="xline">' + esc(k.exploit) + '</div>';
        html += '<div class="xmeta"><span class="tag t-info" style="font-size:10px">' + esc(k.framework) + '</span> <span class="tag" style="background:' + rc + ';color:#000;font-size:10px">' + esc(k.risk) + '</span>';
        if (k.has_validation) html += ' <span style="color:var(--yellow)">⚠️ validation</span>';
        if (k.has_ban_logic) html += ' <span style="color:var(--red)">🚫 ban logic</span>';
        if (k.file) html += ' <span style="color:var(--t3)">' + esc(k.file.split(/[\\/]/).slice(-2).join('/')) + ':' + k.line + '</span>';
        html += '</div></div>';
        if (k.exploit && k.ready_to_use) {
            html += '<button class="xcopy" onclick="copyText(' + JSON.stringify(k.exploit) + ',\'exploit\')">📋 Copy</button>';
        }
        html += '</div>';
    });
    document.getElementById('knowndb-content').innerHTML = html;
}

document.getElementById('knowndb-filters').addEventListener('click', function(e) {
    var b = e.target.closest('.fb');
    if (b) {
        knowndbFilter = b.dataset.filter;
        document.querySelectorAll('#knowndb-filters .fb').forEach(function(x) { x.classList.toggle('on', x.dataset.filter === knowndbFilter); });
        renderKnownDB();
    }
});

// GLOBAL SEARCH
document.getElementById('global-search').addEventListener('keydown', function(e) { if (e.key === 'Enter') doGlobalSearch(); });

function doGlobalSearch() {
    var q = (document.getElementById('global-search').value || '').toLowerCase().trim();
    if (!q || !DATA) return;
    var triggers = (DATA.triggers || []).filter(function(t) { return t.event_name.toLowerCase().indexOf(q) !== -1; });
    if (triggers.length === 0) { document.getElementById('search-results').innerHTML = '<div class="card"><p style="color:var(--yellow)">No results for "' + esc(q) + '"</p></div>'; return; }
    var html = '';
    triggers.forEach(function(t) {
        var line = buildTriggerLine(t.event_name, t.reward_type);
        var tags = '';
        if (t.is_honeypot) tags += tagHTML('HONEYPOT', 'hp') + ' ';
        if (t.has_ban_logic) tags += tagHTML('BAN', 'ban') + ' ';
        if (t.has_validation) tags += tagHTML('VAL', 'val') + ' ';
        html += '<div class="xcard">';
        html += '<div style="flex:1;min-width:0">';
        html += '<div class="xname" style="color:' + riskColor(t.risk_score) + '">' + esc(t.event_name) + ' ' + tags + '</div>';
        html += '<div class="xline">' + esc(line) + '</div>';
        html += '<div class="xmeta"><span class="mono" style="font-size:11px">' + esc(shortPath(t.file)) + ':' + t.line + '</span> &nbsp; <span class="' + riskCls(t.risk_score) + '">' + t.risk_score.toFixed(1) + '%</span></div>';
        html += '</div>';
        html += '<button class="xcopy" onclick="copyText(' + JSON.stringify(line) + ',' + JSON.stringify(t.event_name) + ')">📋 Copy</button>';
        html += '</div>';
    });
    document.getElementById('search-results').innerHTML = html;
}

// RENDER: RESOURCES
function renderResources() {
    var resources = DATA.resource_summary || [];
    if (resources.length === 0) {
        document.getElementById('resources-content').innerHTML = '<p style="color:var(--yellow);padding:20px">No resource data available.</p>';
        return;
    }
    resources = resources.slice().sort(function(a, b) { return b.max_risk - a.max_risk; });
    var html = '<p style="margin-bottom:12px;color:var(--t2);font-size:12px">Resources: <strong style="color:var(--cyan)">' + resources.length + '</strong></p>';
    resources.forEach(function(r) {
        var rc = riskColor(r.max_risk);
        var fwTag = r.framework ? '<span class="tag t-info" style="font-size:10px">' + esc(r.framework) + '</span>' : '';
        html += '<div class="card" style="border-left:3px solid ' + rc + '">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div style="font-size:14px;font-weight:bold;color:' + rc + '">' + esc(r.resource) + ' ' + fwTag + '</div>';
        html += '<div style="font-size:12px;color:var(--t2)">Risk: <span style="color:' + rc + ';font-weight:bold">' + r.max_risk.toFixed(0) + '%</span></div>';
        html += '</div>';
        html += '<div style="display:flex;gap:16px;font-size:12px;color:var(--t2)">';
        html += '<span>Triggers: <strong style="color:var(--cyan)">' + r.trigger_count + '</strong></span>';
        html += '<span>Exploitable: <strong style="color:var(--green)">' + r.exploitable + '</strong></span>';
        if (r.honeypots > 0) html += '<span>Honeypots: <strong style="color:var(--crit)">' + r.honeypots + '</strong></span>';
        html += '</div>';
        if (r.triggers && r.triggers.length > 0) {
            html += '<div style="margin-top:8px;font-size:11px;color:var(--t3)">' + r.triggers.slice(0,8).map(esc).join(', ') + (r.triggers.length > 8 ? ' ...' : '') + '</div>';
        }
        html += '</div>';
    });
    document.getElementById('resources-content').innerHTML = html;
}

// EXPORT: TRIGGERS LUA
function downloadLua() {
    if (!DATA) return;
    var triggers = (DATA.triggers || []).filter(function(t) { return !t.is_honeypot && t.has_reward_logic; });
    if (triggers.length === 0) { showToast('No exploitable triggers to export'); return; }
    var lines = [
        '-- RED-SHADOW DESTROYER v4 - Exploitable Triggers',
        '-- Generated: ' + new Date().toISOString(),
        '-- Count: ' + triggers.length,
        '',
        '-- Paste into Ambani executor or any Lua executor',
        '',
    ];
    triggers.forEach(function(t) {
        lines.push('-- [' + (t.reward_type || 'other').toUpperCase() + '] ' + t.event_name + ' | Risk: ' + t.risk_score.toFixed(0) + '%');
        lines.push(buildTriggerLine(t.event_name, t.reward_type));
        lines.push('');
    });
    triggerDownload(lines.join('\n'), 'exploits.lua', 'text/plain;charset=utf-8;');
    showToast('Lua exported (' + triggers.length + ' triggers)');
}

// EXPORT: AMBANI FORMAT
function downloadAmbani() {
    if (!DATA) return;
    var triggers = (DATA.triggers || []).filter(function(t) { return !t.is_honeypot && t.has_reward_logic; });
    if (triggers.length === 0) { showToast('No exploitable triggers to export'); return; }
    var events = triggers.map(function(t) {
        return {
            name: t.event_name,
            args: t.observed_args && t.observed_args.length > 0 ? t.observed_args : [],
            reward_type: t.reward_type || 'other',
            risk: t.risk_score,
            framework: t.framework || 'standalone',
            validation: t.validation_strength || 'none',
        };
    });
    var output = JSON.stringify({ version: 1, source: 'RED-SHADOW v4', events: events }, null, 2);
    triggerDownload(output, 'ambani_triggers.json', 'application/json');
    showToast('Ambani export done (' + triggers.length + ' events)');
}

// BOOT
fetch('/api/data').then(function(r) { if (r.ok) return r.json(); return null; }).then(function(d) {
    if (d && d.stats && d.triggers) { DATA = d; showDashboard(); }
}).catch(function() {});
</script>
</body>
</html>"""


# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class RedShadowHandler(BaseHTTPRequestHandler):
    """HTTP handler for the web application"""

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
            'phase': AppState.analysis_phase,
            'phase_num': AppState.analysis_phase_num,
            'phase_total': AppState.analysis_phase_total,
            'error': AppState.analysis_error,
            'partial': AppState.partial_data,  # partial data for streaming
        })

    def _handle_analyze(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
        except Exception:
            self._json_response({'error': 'Invalid request'}, status=400)
            return

        dump_path = body.get('path', '').strip()
        ambani_triggers = body.get('ambani_triggers', '').strip()

        # Allow analysis with only Ambani triggers.lua (no full dump)
        ambani_only = False
        if not dump_path and ambani_triggers:
            # Ambani-only mode: use the triggers.lua directory as dump_path
            ambani_only = True
            dump_path = str(Path(ambani_triggers).parent)

        if not dump_path:
            self._json_response({'error': 'Provide the dump path or Ambani triggers.lua'}, status=400)
            return

        if not os.path.exists(dump_path):
            self._json_response({'error': f'Path not found: {dump_path}'}, status=400)
            return

        if ambani_triggers and not os.path.exists(ambani_triggers):
            self._json_response({'error': f'triggers.lua not found: {ambani_triggers}'}, status=400)
            return

        if AppState.analysis_running:
            self._json_response({'error': 'Analysis already running'}, status=409)
            return

        # Launch analysis in background thread
        AppState.analysis_running = True
        AppState.analysis_done = False
        AppState.analysis_error = None
        AppState.analysis_progress = "Starting analysis..."
        AppState.report_data = None
        AppState.dump_path = dump_path

        thread = threading.Thread(
            target=_run_analysis_thread,
            args=(dump_path, ambani_triggers, ambani_only),
            daemon=True
        )
        thread.start()

        self._json_response({'status': 'started', 'path': dump_path})

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))


# ============================================================================
# AMBANI FALLBACK PARSER (for engine versions without parse_ambani_triggers_lua)
# ============================================================================

def _parse_ambani_fallback(engine, triggers_lua_path: str) -> int:
    """Parse Ambani triggers.lua when the engine doesn't have the native method."""
    import re as _re
    from pathlib import Path as _Path
    try:
        content = _Path(triggers_lua_path).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return 0

    imported = 0
    seen = set(engine.triggers.keys()) if hasattr(engine.triggers, 'keys') else set()

    # Extract event names from any common format
    patterns = [
        r'(?:RegisterNetEvent|AddEventHandler|TriggerServerEvent|TriggerEvent)\s*\(\s*["\']([^"\']+)["\']',
        r'["\']([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-:\.]+)["\']',
    ]
    for pat in patterns:
        for m in _re.finditer(pat, content, _re.IGNORECASE):
            name = m.group(1).strip()
            if not name or name in seen:
                continue
            if ':' not in name and pat == patterns[1]:
                continue
            seen.add(name)
            # Create minimal compatible trigger
            try:
                if hasattr(engine, '_build_trigger_from_name'):
                    line_no = content[:m.start()].count('\n') + 1
                    trigger = engine._build_trigger_from_name(name, triggers_lua_path, line_no)
                    if hasattr(engine.triggers, '__setitem__'):
                        engine.triggers[name] = trigger
                    else:
                        engine.triggers.append(trigger)
                    imported += 1
            except Exception:
                pass

    return imported


# ============================================================================
# ANALYSIS THREAD
# ============================================================================

def _run_analysis_thread(dump_path, ambani_triggers_path=None, ambani_only=False):
    """Ejecutar el analisis en un thread de background"""
    try:
        engine_dir = Path(__file__).parent.resolve()
        if str(engine_dir) not in sys.path:
            sys.path.insert(0, str(engine_dir))

        try:
            from red_shadow_destroyer_v4 import RedShadowV4
        except ImportError:
        # Fallback: user copied the engine as main.py or another name
            import importlib.util as _ilu
            _candidates = ['main', 'red_shadow', 'destroyer_v4', 'red_shadow_v4']
            RedShadowV4 = None
            for _cname in _candidates:
                try:
                    _mod = __import__(_cname)
                    if hasattr(_mod, 'RedShadowV4'):
                        RedShadowV4 = _mod.RedShadowV4
                        break
                except ImportError:
                    pass
            if RedShadowV4 is None:
                # Search any .py in engine_dir that has RedShadowV4
                for _pyf in engine_dir.glob('*.py'):
                    try:
                        _spec = _ilu.spec_from_file_location('_rs_engine', _pyf)
                        _mod = _ilu.module_from_spec(_spec)
                        _spec.loader.exec_module(_mod)
                        if hasattr(_mod, 'RedShadowV4'):
                            RedShadowV4 = _mod.RedShadowV4
                            break
                    except Exception:
                        pass
            if RedShadowV4 is None:
                raise ImportError("RedShadowV4 not found in any file in the directory")

        AppState.analysis_progress = "Loading dump files..."
        engine = RedShadowV4(dump_path)

        file_count = engine.load_files()

        # Import Ambani triggers.lua if provided
        ambani_imported = 0
        if ambani_triggers_path:
            AppState.analysis_progress = "Importing Ambani triggers.lua..."
            if hasattr(engine, 'parse_ambani_triggers_lua'):
                ambani_imported = engine.parse_ambani_triggers_lua(ambani_triggers_path)
            else:
                # Fallback: parse manually if the engine doesn't have the method
                ambani_imported = _parse_ambani_fallback(engine, ambani_triggers_path)

        if file_count == 0 and ambani_imported == 0:
            AppState.analysis_error = "No Lua files or Ambani triggers found"
            AppState.analysis_running = False
            return

        if ambani_only and ambani_imported > 0:
            AppState.analysis_progress = f"{ambani_imported} triggers imported from Ambani. Analyzing..."
        else:
            extra = f", {ambani_imported} Ambani triggers" if ambani_imported else ""
            AppState.analysis_progress = f"{file_count} Lua files loaded{extra}. Running analysis..."

        def _phase(name, method_name):
            fn = getattr(engine, method_name, None)
            if fn:
                return (name, fn)
            return None

        phases = list(filter(None, [
            _phase("Extracting functions...", "extract_functions"),
            _phase("Detecting triggers...", "detect_triggers"),
            _phase("Scanning obfuscation...", "detect_obfuscation"),
            _phase("Decoding obfuscated strings...", "detect_string_obfuscation"),
            _phase("Analyzing natives...", "analyze_natives"),
            _phase("Analyzing callbacks...", "analyze_callbacks"),
            _phase("Analyzing manifests...", "analyze_manifests"),
            _phase("Scanning security...", "detect_security_issues"),
            _phase("Fingerprinting anticheats...", "fingerprint_anticheats"),
            _phase("Analyzing trigger chains...", "analyze_trigger_chains"),
            _phase("Detecting code clones...", "detect_code_clones"),
            _phase("Complexity analysis...", "analyze_code_complexity"),
            _phase("Detecting backdoors...", "detect_backdoors"),
            _phase("Detecting anomalies...", "detect_behavioral_anomalies"),
            _phase("Detecting webhooks...", "detect_webhooks"),
            _phase("Building call graph...", "build_call_graph"),
            _phase("Detecting RP locations...", "detect_all_locations"),
        ]))

        AppState.analysis_phase_total = len(phases)

        # Phases that emit partial data after completing (for streaming)
        STREAMING_PHASES = {
            'detect_triggers', 'fingerprint_anticheats', 'detect_backdoors',
            'detect_webhooks', 'detect_all_locations', 'detect_security_issues',
        }

        for i, (msg, func) in enumerate(phases, 1):
            AppState.analysis_progress = f"Fase {i}/{len(phases)}: {msg}"
            AppState.analysis_phase = msg
            AppState.analysis_phase_num = i
            func()
            # Emit partial data after key phases so the frontend can update
            if func.__name__ in STREAMING_PHASES or getattr(func, '__func__', None) and getattr(func.__func__, '__name__', '') in STREAMING_PHASES:
                try:
                    AppState.partial_data = _build_report_data(engine)
                except Exception:
                    pass

        AppState.analysis_progress = "Generating report..."

        report = _build_report_data(engine)
        if ambani_imported:
            report['ambani_triggers_imported'] = ambani_imported
            report['stats']['ambani_triggers_imported'] = ambani_imported
        AppState.report_data = report
        AppState.partial_data = None
        AppState.analysis_done = True
        AppState.analysis_running = False
        AppState.analysis_progress = "Analysis complete"

    except Exception as e:
        AppState.analysis_error = str(e)
        AppState.analysis_running = False
        traceback.print_exc()



def _build_report_data(engine):
    """Build report dictionary from the engine"""
    code_clones = []
    if hasattr(engine, 'code_hashes'):
        for h, files in engine.code_hashes.items():
            if len(files) > 1:
                code_clones.append(files)

    # Convert triggers dict to list with asdict
    triggers_list = []
    if hasattr(engine.triggers, 'values'):
        # It's a dict
        triggers_list = [asdict(t) for t in engine.triggers.values()]
    elif isinstance(engine.triggers, list):
        # Already a list
        triggers_list = [asdict(t) if hasattr(t, '__dataclass_fields__') else t for t in engine.triggers]
    
    # Convert rp_locations to dict format
    rp_locations_list = []
    if hasattr(engine, 'rp_locations'):
        for loc in engine.rp_locations:
            if hasattr(loc, 'to_dict'):
                rp_locations_list.append(loc.to_dict())
            elif hasattr(loc, '__dataclass_fields__'):
                rp_locations_list.append(asdict(loc))
            else:
                rp_locations_list.append(loc)
    
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
            'backdoors': len(getattr(engine, 'backdoors', [])),
            'anomalies': len(getattr(engine, 'anomalies', [])),
            'complexity_files': len(getattr(engine, 'complexity_metrics', [])),
            'rp_locations': len(getattr(engine, 'rp_locations', [])),
            'webhooks': len(getattr(engine, 'webhooks', [])),
        },
        'triggers': triggers_list,
        'callbacks': [asdict(c) for c in engine.callbacks],
        'natives': [asdict(n) for n in engine.natives],
        'obfuscations': [asdict(o) for o in engine.obfuscations],
        'security_issues': [asdict(s) for s in engine.security_issues],
        'anticheats': engine.anticheat_detected,
        'manifests': [asdict(m) for m in engine.manifests],
        'trigger_chains': engine.trigger_chains,
        'cross_references': {k: list(v) for k, v in engine.cross_references.items()},
        'code_clones': code_clones[:100],
        'backdoors': [asdict(b) for b in getattr(engine, 'backdoors', [])],
        'anomalies': [asdict(a) for a in getattr(engine, 'anomalies', [])],
        'complexity_metrics': [asdict(m) for m in getattr(engine, 'complexity_metrics', [])],
        'recommendations': engine._generate_recommendations(),
        'rp_locations': rp_locations_list,
        'webhooks': getattr(engine, 'webhooks', []),
        'known_triggers': engine.match_known_triggers() if hasattr(engine, 'match_known_triggers') else [],
        'resource_summary': list(engine.build_resource_summary().values()) if hasattr(engine, 'build_resource_summary') else [],
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
    Launch the web server.

    If an engine with completed analysis is passed, data will be available
    immediately and the dashboard will be shown directly.
    If no engine is passed, the landing page is shown to select a dump.
    """
    if engine is not None:
        AppState.report_data = _build_report_data(engine)
        AppState.analysis_done = True

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No free port found\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] RED-SHADOW Web Dashboard: {url}\033[0m")
    print(f"\033[93m[INFO] Press Ctrl+C to stop\033[0m")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Server closed\033[0m")


def launch_web_gui_from_json(json_path, auto_open=True):
    """Launch from an existing report JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        AppState.report_data = json.load(f)
    AppState.analysis_done = True

    port = find_free_port()
    if port is None:
        print("\033[91m[ERROR] No free port found\033[0m")
        return

    server = HTTPServer(('127.0.0.1', port), RedShadowHandler)
    url = f'http://127.0.0.1:{port}'

    print(f"\033[92m[OK] RED-SHADOW Web Dashboard: {url}\033[0m")
    print(f"\033[93m[INFO] Press Ctrl+C to stop\033[0m")

    if auto_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print(f"\n\033[96m[INFO] Server closed\033[0m")


# ============================================================================
# STANDALONE
# ============================================================================

if __name__ == '__main__':
    if len(sys.argv) >= 2 and os.path.isfile(sys.argv[1]):
        launch_web_gui_from_json(sys.argv[1])
    elif len(sys.argv) >= 2 and os.path.isdir(sys.argv[1]):
        print("\033[96m[INFO] Dump path provided, launching...\033[0m")
        AppState.dump_path = sys.argv[1]
        launch_web_gui()
    else:
        # No args - launch landing page
        launch_web_gui()
