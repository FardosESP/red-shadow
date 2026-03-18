--[[
    RED-SHADOW v4.0  |  AC Destroyer  |  F5 to open
]]

-- ============================================================
--  SAFE LIST
-- ============================================================
local SAFE = {
    sessionmanager=true, mapmanager=true, spawnmanager=true,
    baseevents=true, chat=true, hardcap=true, rconlog=true,
    playernames=true, fivem=true,
    ["es_extended"]=true, ["qb-core"]=true, qbcore=true,
    ox_core=true, oxmysql=true, ["mysql-async"]=true,
    vrp=true, ["vRP"]=true,
}

-- ============================================================
--  EXACT KILL LIST
-- ============================================================
local EXACT = {
    -- FiveGuard
    "fiveguard","fg_anticheat","fg_core","fg_client","fg_screenshot",
    "fg_process","fg_monitor","fg_scanner","fiveguard_screencapture",
    "fiveguard_capture","fiveguard_scanner","fg-screenshot",
    -- WaveShield
    "waveshield","ws_anticheat","wave_shield","ws_core","ws_client",
    "ws_server","ws_screen","ws_scan","ws_watchdog","ws_monitor",
    "ws_cron","ws_updater","ws_restart","wshield",
    -- Guardian
    "guardian","grd_anticheat","guardian_ac","grd_core","grd_client",
    "grd_server","grd_monitor",
    -- ElectronAC
    "electronac","electron_ac","electron-ac","electron_core",
    -- FireAC
    "fireac","fire_ac","fireanticheat","fireac_screenshot",
    "fireac_screen","fireac_capture","fireac_ml","fireac_ai","fireac_learning",
    -- BadgerAC
    "badger-anticheat","badgerac","badger_anticheat","badgerac_screenshot",
    "badger_screen","badgerac_events","badger_monitor",
    -- PhoenixAC
    "phoenixac","phoenix_ac","pac_main","phoenixac_screenshot",
    "pac_screen","phoenix_capture","phoenixac_logger","pac_log","phoenix_behavior",
    -- MXShield
    "mxshield","mx_shield","mx_core",
    -- PegasusAC / Icarus
    "pegasusac","icarus_ac","icarusac","icarusadvancedanticheat",
    "icarus","icarus-ac","icarus_advanced",
    -- Qprotect / PrettyPackets
    "prettypackets","qprotect","qprotect_screenshot","qp_screen",
    "qprotect_logger","qprotect_webhook","qp_notify","qprotect_monitor",
    "prettypacketac","prettypacket_ac",
    -- SentinelAC
    "sentinelac","sentinel_ac","sentinel_core",
    -- SASAC
    "esx_anticheat","sasac",
    -- Guardex
    "guardex","guardex_ac","guardex_core",
    -- AntiCheese
    "anticheese","anticheese-anticheat","anticheese_anticheat",
    -- API-ANTICHEAT
    "api-anticheat","api_anticheat","apianticheat",
    -- Vulcan-AC
    "vulcan-ac","vulcan_ac","vulcanac",
    -- RuxoAC
    "ruxoac","ruxo_ac","ruxo-ac",
    -- TigoAntiCheat
    "tigoanticheats","tigo_anticheat","tigo-anticheat","tigoacc",
    -- M_Anticheat
    "m_anticheat","manticheat",
    -- ReaperAC
    "rac","reaperac","reaper_ac","reaper-ac",
    -- LunaAC
    "lunaac","luna_ac","luna-ac","luna_anticheat",
    -- FiveM-Guard
    "fivem-guard","fivemguard","fivem_guard",
    -- OxAC
    "ox_anticheat","oxac",
    -- Misc paid ACs
    "nativeshield","native_shield","native-shield",
    "servershield","server_shield",
    "proac","pro_ac","pro-ac",
    "zeroac","zero_ac","zero-ac",
    "alphaac","alpha_ac","alpha-ac",
    "omegaac","omega_ac",
    "shieldac","shield_ac","shield-ac",
    "protectac","protect_ac",
    "secureac","secure_ac",
    "guardac","guard_ac",
    "safeac","safe_ac",
    "blockac","block_ac",
    -- Generic AC
    "anticheat","ac_core","anti_cheat","anti-cheat",
    -- Screenshot
    "screenshot-basic","screenshot_basic","screenshotbasic",
    "discord-screenshot","discord_screenshot",
    "screenshot","screenshots","screencap",
    "screen-capture","screen_capture",
    "player-screenshot","player_screenshot",
    "admin-screenshot","admin_screenshot",
    "ss-basic","ss_basic",
    -- Admin menus - ESX
    "easyadmin","easy_admin",
    "esx_adminmenu","es_admin","es_admin2","esx_adminplus","esx_adminduty",
    -- Admin menus - txAdmin
    "txadmin","tx_admin",
    -- Admin menus - vMenu
    "vmenu","v_menu",
    -- Admin menus - QB
    "qb-adminmenu","qb_adminmenu","qb-admin","qb_admin",
    -- Admin menus - Project Sloth
    "ps-adminmenu","ps_adminmenu",
    -- Admin menus - Quasar
    "qs-adminmenu","qs_adminmenu",
    -- Admin menus - Wasabi
    "wasabi_adminmenu","wasabi-adminmenu","wasabiadmin",
    -- Admin menus - CodeSign
    "cd_adminmenu","cd-adminmenu","codesign_admin",
    -- Admin menus - JDV
    "jdv-adminmenu","jdv_adminmenu",
    -- Admin menus - CodeM
    "codem-xadminmenu","codem_xadminmenu","codem-mstaff","codem_mstaff",
    -- Admin menus - RCore
    "rcore_admin","rcore-admin",
    -- Admin menus - LJ
    "lj-adminmenu","lj_adminmenu",
    -- Admin menus - TS
    "ts-adminmenu","ts_adminmenu",
    -- Admin menus - UM
    "um-admin","um_admin",
    -- Admin menus - ERP
    "erp_adminmenu","erp-adminmenu",
    -- Admin menus - CQ
    "cq-admin","cq_admin",
    -- Admin menus - SA
    "sa-admin","sa_admin",
    -- Admin menus - generic
    "adminmenu","admin-menu","admin_menu",
    "staffmenu","staff-menu","staff_menu",
    "adminpanel","admin-panel","admin_panel",
    -- Spectate / freeze
    "esx_spectate","qb-spectate","spectate","admin_spectate",
    "freeze","admin_freeze","player_freeze","esx_freeze",
    -- Anti-dump / anti-inject
    "antidump","anti_dump","anti-dump",
    "antiinjection","anti_injection","anti-injection",
    "antileak","anti_leak",
    "anti_backdoor","anti-backdoor","antibackdoor",
    "anti_cipher","anti-cipher","anticipher",
    "anti_exploit","anti-exploit","antiexploit",
    "anti_hack","anti-hack","antihack",
    "anti_cheat_basic","protection","server_protection","sv_protection",
    -- Loggers / monitors
    "anticheat-logs","ac_logs","ac-logs",
    "monitor","server-monitor","servermonitor","sv_monitor",
    "logger","event-logger","eventlogger","event_logger",
    "triggerlogger","trigger_logger","trigger-logger",
    "chatlogger","chat_logger","discordlogger","discord_logger",
    "event_monitor","event-monitor","sv_logger","server_logger",
    "webhook_logger","webhook-logger","discord_webhook","discord-webhook",
    "log_system","logging","logs",
    "chat_log","chat-log","command_log","command-log",
    "player_log","player-log","activity_log","activity-log",
    "ban_log","kick_log","connect_log","disconnect_log",
    "death_log","deathlog","rup-deathlog","rup_deathlog",
    -- Framework built-in ACs
    "qb-anticheat","qb_anticheat","ox_anticheat",
    "vrp_anticheat","vrp_protection","qb-smallresources",
}

local EXACT_SET = {}
for _, v in ipairs(EXACT) do EXACT_SET[v:lower()] = true end

-- ============================================================
--  KEYWORDS (substring match)
-- ============================================================
local KEYWORDS = {
    -- AC names
    "anticheat","anti_cheat","anti-cheat",
    "waveshield","fiveguard","fireac","guardian",
    "phoenixac","sentinelac","badgerac","mxshield","guardex",
    "pegasusac","electronac","lunaac","reaperac",
    "anticheese","vulcan","ruxo","tigo","luna",
    -- Screenshot
    "screenshot","screencap","screen_cap","screenshoot",
    -- Cron / scheduler / updater / watchdog (AC background tasks)
    "cron","watchdog","updater","scheduler","heartbeat",
    -- Loggers
    "logger","_log","-log",
    "deathlog","chatlog","eventlog","triggerlog","discordlog",
    "webhook",
    -- Anti-* generic
    "antidump","antileak","antiinjection",
    "antihack","antiexploit","antibackdoor","anticipher",
    -- Admin / staff
    "adminmenu","staffmenu","adminpanel",
    -- Spectate / monitor
    "spectate","monitor",
}

-- ============================================================
--  CORE LOGIC
-- ============================================================
local function isAC(name)
    local low = name:lower()
    if SAFE[low] or SAFE[name] then return false end
    if EXACT_SET[low] then return true end
    for _, kw in ipairs(KEYWORDS) do
        if low:find(kw, 1, true) then return true end
    end
    return false
end

local function scanACs()
    local found = {}
    for _, name in ipairs(ambani.GetResourceList()) do
        if ambani.GetResourceState(name) == 3 and isAC(name) then
            found[#found+1] = name
        end
    end
    return found
end

local function stopResource(name)
    local ok = pcall(DestroyResource, name)
    if not ok then pcall(ambani.ResourceStop, name) end
end

-- ============================================================
--  WINDOW
-- ============================================================
local MAX_SLOTS = 20
local LOG_SLOTS = 14

local win = ambani.MenuTabbedWindow("RED-SHADOW", 200, 60, 500, 640, 130)
ambani.MenuSetAccent(win, 180, 0, 0)
ambani.MenuSetKeybind(win, 0x74)

-- ============================================================
--  TAB 1: SCANNER
-- ============================================================
local tabScan = ambani.MenuAddTab(win, "Scanner")

local gAct = ambani.MenuGroup(tabScan, "Actions", 10, 10, 460, 150)

local gStat     = ambani.MenuGroup(tabScan, "Status", 10, 170, 460, 70)
local txtStatus = ambani.MenuText(gStat, "  Ready  --  press SCAN")
local txtCount  = ambani.MenuText(gStat, "  Scanned: --   Threats: --")

local gRes      = ambani.MenuGroup(tabScan, "Detected Threats", 10, 250, 460, 360)
local scanSlots = {}
for i = 1, MAX_SLOTS do
    scanSlots[i] = ambani.MenuText(gRes, "  -")
end

local lastFound = {}

local function doScan()
    lastFound = scanACs()
    local total = #ambani.GetResourceList()
    if #lastFound > 0 then
        ambani.MenuSetText(txtStatus, "  ! " .. #lastFound .. " threat(s) detected")
    else
        ambani.MenuSetText(txtStatus, "  Clean  --  no threats found")
    end
    ambani.MenuSetText(txtCount, "  Scanned: " .. total .. "   Threats: " .. #lastFound)
    for i = 1, MAX_SLOTS do
        if lastFound[i] then
            ambani.MenuSetText(scanSlots[i], "  > " .. lastFound[i])
        else
            ambani.MenuSetText(scanSlots[i], "  -")
        end
    end
    if #lastFound > 0 then
        ambani.Notify("RED-SHADOW", #lastFound .. " threat(s) found")
    end
end

local function doKill(found)
    if #found == 0 then
        ambani.Notify("RED-SHADOW", "Nothing to kill")
        return 0
    end
    for i, name in ipairs(found) do
        stopResource(name)
        print("^1[RS] ^7Killed: " .. name)
        if scanSlots[i] then
            ambani.MenuSetText(scanSlots[i], "  [KILLED] " .. name)
        end
    end
    for i = #found + 1, MAX_SLOTS do
        ambani.MenuSetText(scanSlots[i], "  -")
    end
    ambani.MenuSetText(txtStatus, "  Killed " .. #found .. " resource(s)")
    ambani.Notify("RED-SHADOW", "Killed " .. #found .. " resource(s)")
    return #found
end

ambani.MenuButton(gAct, "  [ SCAN ]  --  detect all threats", function()
    doScan()
end)

ambani.MenuButton(gAct, "  [ KILL ALL ]  --  stop last scan results", function()
    if #lastFound == 0 then lastFound = scanACs() end
    doKill(lastFound)
    lastFound = {}
end)

ambani.MenuButton(gAct, "  [ SCAN + KILL ]  --  detect and stop in one click", function()
    local found = scanACs()
    local total = #ambani.GetResourceList()
    ambani.MenuSetText(txtCount, "  Scanned: " .. total .. "   Killed: " .. #found)
    doKill(found)
    lastFound = {}
end)

-- ============================================================
--  TAB 2: KILL LOG
-- ============================================================
local tabLog   = ambani.MenuAddTab(win, "Kill Log")
local gLog     = ambani.MenuGroup(tabLog, "Session Log", 10, 10, 460, 540)
local logSlots = {}
for i = 1, LOG_SLOTS do
    logSlots[i] = ambani.MenuText(gLog, "  -")
end
local logLines = {}

local function pushLog(msg)
    table.insert(logLines, 1, msg)
    if #logLines > LOG_SLOTS then logLines[LOG_SLOTS + 1] = nil end
    for i = 1, LOG_SLOTS do
        ambani.MenuSetText(logSlots[i], logLines[i] or "  -")
    end
end

-- ============================================================
--  TAB 3: AUTO-KILL
-- ============================================================
local tabAuto = ambani.MenuAddTab(win, "Auto-Kill")
local gAuto   = ambani.MenuGroup(tabAuto, "Settings", 10, 10, 460, 200)

local autoKill    = false
local autoKillInt = 5000

ambani.MenuCheckbox(gAuto, "Enable Auto-Kill", function()
    autoKill = true
    ambani.Notify("RED-SHADOW", "Auto-Kill: ON")
    pushLog("[AUTO] Enabled")
end, function()
    autoKill = false
    ambani.Notify("RED-SHADOW", "Auto-Kill: OFF")
    pushLog("[AUTO] Disabled")
end)

ambani.MenuSlider(gAuto, "Interval", 5, 2, 60, "s", 0, function(v)
    autoKillInt = v * 1000
    pushLog("[AUTO] Interval: " .. v .. "s")
end)

local gAutoStat    = ambani.MenuGroup(tabAuto, "Stats", 10, 220, 460, 120)
local txtAutoLast  = ambani.MenuText(gAutoStat, "  Last run: --")
local txtAutoTotal = ambani.MenuText(gAutoStat, "  Session killed: 0")
local sessionKilled = 0

-- ============================================================
--  TAB 4: INFO
-- ============================================================
local tabInfo     = ambani.MenuAddTab(win, "Info")
local gInfo       = ambani.MenuGroup(tabInfo, "Session", 10, 10, 460, 200)
local txtUser     = ambani.MenuText(gInfo, "  User: --")
local txtPlayers  = ambani.MenuText(gInfo, "  Players: --")
local txtResCount = ambani.MenuText(gInfo, "  Resources: --")
local txtHealth   = ambani.MenuText(gInfo, "  Health: --")
local txtPos      = ambani.MenuText(gInfo, "  Position: --")

local gAbout = ambani.MenuGroup(tabInfo, "About", 10, 220, 460, 120)
ambani.MenuText(gAbout, "  RED-SHADOW v4.0  |  AC Destroyer")
ambani.MenuText(gAbout, "  Exact entries: " .. #EXACT)
ambani.MenuText(gAbout, "  Keyword patterns: " .. #KEYWORDS)
ambani.MenuText(gAbout, "  Safe list: framework resources protected")

-- ============================================================
--  THREADS
-- ============================================================
Citizen.CreateThread(function()
    while true do
        Citizen.Wait(800)
        if ambani.IsGuiOpen() then
            local x, y, z = ambani.GetPos()
            ambani.MenuSetText(txtUser,     "  User: "      .. ambani.GetName())
            ambani.MenuSetText(txtPlayers,  "  Players: "   .. ambani.GetPlayerCount())
            ambani.MenuSetText(txtResCount, "  Resources: " .. ambani.GetResourceCount())
            ambani.MenuSetText(txtHealth,   "  Health: "    .. math.floor(ambani.GetHealth()) .. " / 200")
            ambani.MenuSetText(txtPos,      ("  Pos: %.1f, %.1f, %.1f"):format(x, y, z))
        end
    end
end)

Citizen.CreateThread(function()
    while true do
        Citizen.Wait(autoKillInt)
        if autoKill then
            local found = scanACs()
            if #found > 0 then
                for _, name in ipairs(found) do
                    stopResource(name)
                    sessionKilled = sessionKilled + 1
                    pushLog("[AUTO] Killed: " .. name)
                    print("^1[RS-AUTO] ^7Killed: " .. name)
                end
                ambani.MenuSetText(txtAutoLast,  "  Last run: killed " .. #found)
                ambani.MenuSetText(txtAutoTotal, "  Session killed: " .. sessionKilled)
                ambani.Notify("RED-SHADOW", "[AUTO] Killed " .. #found)
            end
        end
    end
end)

-- ============================================================
--  EVENT BYPASS
-- ============================================================
local BYPASS = {
    "screenshot_basic:requestScreenshot","screenshot_basic:takeScreenshot",
    "EasyAdmin:CaptureScreenshot","EasyAdmin:FreezePlayer","EasyAdmin:spectate",
    "txAdmin:action","txAdmin:checkIn","txAdmin:clientLog",
    "anticheat:screenshot","anticheat:freeze","anticheat:teleport",
    "ac:screenshot","ac:freeze",
    "fiveguard:screenshot","guardian:screenshot",
    "waveshield:screenshot","fireac:screenshot",
    "phoenixac:screenshot","sentinelac:screenshot",
    "badgerac:screenshot","qprotect:screenshot","guardex:screenshot",
}
for _, ev in ipairs(BYPASS) do
    RegisterNetEvent(ev)
    AddEventHandler(ev, function() CancelEvent() end)
end

-- ============================================================
ambani.Notify("RED-SHADOW v4", "Loaded -- F5 to open")
print("^2[RS] ^7AC Destroyer ready | F5 | User: " .. ambani.GetName())
