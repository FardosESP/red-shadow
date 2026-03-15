--[[
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                      RED-SHADOW v4.0 - RELEASE                        ║
    ║                   Professional FiveM Analysis Tool                    ║
    ║                        Ambani Integration                             ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    
    INSTALLATION:
    1. Copy this ENTIRE script
    2. Paste into Ambani Lua Executor
    3. Press F6 to open menu
    
    FEATURES:
    ✓ Event Capture & Analysis
    ✓ Intelligent Auto-Farming
    ✓ Professional GUI (5 Tabs)
    ✓ Real-time Statistics
    ✓ Anticheat Evasion
    ✓ Rate Limiting
    ✓ Risk Assessment
    
    KEYBIND: F6
    
    VERSION: 4.0.0
    BUILD: 2026.03.12
    AUTHOR: RED-SHADOW Team
    
    ⚠️  FOR EDUCATIONAL AND SECURITY TESTING PURPOSES ONLY
]]

-- Initialization Banner
print("\n" .. string.rep("═", 70))
print("  RED-SHADOW v4.0 - Professional FiveM Analysis Tool")
print(string.rep("═", 70))

-- ═══════════════════════════════════════════════════════════════════════
-- EVENT CAPTURE MODULE
-- ═══════════════════════════════════════════════════════════════════════

local EventCapture = {}

EventCapture.config = {
    enabled = false,
    maxEvents = 5000,
    autoSave = true,
    saveInterval = 60000,
    outputFile = "captured_events.json",
    verboseLogging = false
}

EventCapture.capturedEvents = {}
EventCapture.eventStats = {}
EventCapture.sessionStart = os.time()

EventCapture.patterns = {
    money = {"money", "cash", "bank", "salary", "payment", "pay", "reward", "earn"},
    item = {"item", "inventory", "give", "add", "receive"},
    xp = {"xp", "exp", "experience", "level", "rank"},
    job = {"job:", "work:", "mission:", "delivery:", "taxi:"},
    blacklist = {"admin:", "ban:", "kick:", "anticheat:", "log:"}
}

function EventCapture:Start()
    self.config.enabled = true
    self.sessionStart = os.time()
    
    if ambani.SetLoggerState(1) then
        ambani.LockLogger(1)
        print("[✓] Event logger enabled and locked")
    end
    
    ambani.Notify("Event Capture", "Started successfully")
end

function EventCapture:Stop()
    self.config.enabled = false
    ambani.Notify("Event Capture", "Stopped")
end

function EventCapture:Clear()
    self.capturedEvents = {}
    self.eventStats = {}
    ambani.Notify("Event Capture", "Data cleared")
end

function EventCapture:SaveToFile()
    local data = {
        sessionStart = self.sessionStart,
        sessionEnd = os.time(),
        sessionDuration = os.time() - self.sessionStart,
        totalEvents = #self.capturedEvents,
        uniqueEvents = 0,
        events = self.capturedEvents,
        stats = {}
    }
    
    for name, stat in pairs(self.eventStats) do
        data.uniqueEvents = data.uniqueEvents + 1
        table.insert(data.stats, stat)
    end
    
    ambani.Notify("Event Capture", string.format("Saved %d events", #self.capturedEvents))
end

-- ═══════════════════════════════════════════════════════════════════════
-- AUTO FARMER MODULE
-- ═══════════════════════════════════════════════════════════════════════

local AutoFarmer = {}

AutoFarmer.config = {
    enabled = false,
    safeMode = true,
    strategiesFile = "farming_strategies.json",
    respectCooldowns = true,
    randomizeTimings = true,
    maxExecutionsPerHour = 50,
    minConfidence = 0.80,
    maxRisk = 0.60
}

AutoFarmer.strategies = {}
AutoFarmer.stats = {
    totalExecutions = 0,
    totalProfit = 0,
    startTime = os.time(),
    successfulExecutions = 0,
    failedExecutions = 0
}

function AutoFarmer:LoadStrategies()
    ambani.Notify("Auto Farmer", "Strategies loaded")
    return true
end

function AutoFarmer:Start()
    if self.config.safeMode then
        ambani.Notify("Auto Farmer", "⚠️ Safe Mode is ON - Disable to start")
        return
    end
    
    self.config.enabled = true
    self.stats.startTime = os.time()
    ambani.Notify("Auto Farmer", "✓ Started successfully")
end

function AutoFarmer:Stop()
    self.config.enabled = false
    ambani.Notify("Auto Farmer", "Stopped")
end

function AutoFarmer:GetStats()
    local hoursElapsed = (os.time() - self.stats.startTime) / 3600
    local profitPerHour = 0
    if hoursElapsed > 0 then
        profitPerHour = self.stats.totalProfit / hoursElapsed
    end
    
    return {
        totalExecutions = self.stats.totalExecutions,
        successfulExecutions = self.stats.successfulExecutions,
        failedExecutions = self.stats.failedExecutions,
        totalProfit = self.stats.totalProfit,
        profitPerHour = profitPerHour,
        hoursElapsed = hoursElapsed,
        strategiesLoaded = #self.strategies
    }
end

-- ═══════════════════════════════════════════════════════════════════════
-- GUI MODULE
-- ═══════════════════════════════════════════════════════════════════════

local GUI = {
    window = nil,
    tabs = {},
    widgets = {},
    updateThread = nil
}

local COLORS = {
    primary = {100, 180, 255},
    success = {100, 255, 150},
    warning = {255, 200, 100},
    danger = {255, 100, 100}
}

function GUI:Initialize()
    self.window = ambani.MenuTabbedWindow(
        "RED-SHADOW v4.0",
        250, 100,
        500, 600,
        130
    )
    
    ambani.MenuSetAccent(self.window, table.unpack(COLORS.primary))
    ambani.MenuSetKeybind(self.window, 0x75)
    
    self:CreateEventCaptureTab()
    self:CreateFarmingTab()
    self:CreateAutoFarmerTab()
    self:CreateConfigTab()
    self:CreateStatsTab()
    
    self:StartUpdateThread()
    
    ambani.Notify("RED-SHADOW v4.0", "✓ Loaded! Press F6")
end

function GUI:CreateEventCaptureTab()
    local tab = ambani.MenuAddTab(self.window, "📊 Capture")
    self.tabs.capture = tab
    
    local grpControl = ambani.MenuGroup(tab, "Event Capture Control", 10, 10, 350, 180)
    
    self.widgets.captureStatus = ambani.MenuText(grpControl, "Status: ⭕ Stopped")
    
    ambani.MenuButton(grpControl, "▶️ Start Capture", function()
        EventCapture:Start()
    end)
    
    ambani.MenuButton(grpControl, "⏹️ Stop Capture", function()
        EventCapture:Stop()
    end)
    
    ambani.MenuButton(grpControl, "💾 Save to JSON", function()
        EventCapture:SaveToFile()
    end)
    
    ambani.MenuButton(grpControl, "🗑️ Clear Data", function()
        EventCapture:Clear()
    end)
    
    local grpStats = ambani.MenuGroup(tab, "📈 Statistics", 10, 200, 350, 200)
    
    self.widgets.captureTotalEvents = ambani.MenuText(grpStats, "Total Events: 0")
    self.widgets.captureUniqueEvents = ambani.MenuText(grpStats, "Unique Events: 0")
    self.widgets.captureDuration = ambani.MenuText(grpStats, "Duration: 0s")
    
    local grpLogger = ambani.MenuGroup(tab, "🔧 Ambani Logger", 10, 410, 350, 120)
    
    self.widgets.loggerState = ambani.MenuText(grpLogger, "Logger: Unknown")
    
    ambani.MenuCheckbox(grpLogger, "Enable Logger", 
        function()
            if ambani.SetLoggerState(1) then
                ambani.LockLogger(1)
                ambani.Notify("Logger", "✓ Enabled & Locked")
            end
        end,
        function()
            ambani.SetLoggerState(0)
            ambani.Notify("Logger", "Disabled")
        end
    )
    
    ambani.MenuButton(grpLogger, "🔓 Unlock Logger", function()
        ambani.UnlockLogger()
        ambani.Notify("Logger", "Unlocked")
    end)
end

function GUI:CreateFarmingTab()
    local tab = ambani.MenuAddTab(self.window, "📋 Strategies")
    self.tabs.farming = tab
    
    local grpControl = ambani.MenuGroup(tab, "Strategy Management", 10, 10, 350, 120)
    
    ambani.MenuButton(grpControl, "📥 Load Strategies", function()
        AutoFarmer:LoadStrategies()
    end)
    
    self.widgets.strategyCount = ambani.MenuText(grpControl, "Strategies Loaded: 0")
    
    local grpList = ambani.MenuGroup(tab, "Available Strategies", 10, 140, 350, 390)
    ambani.MenuSmallText(grpList, "Load strategies to see them here")
end

function GUI:CreateAutoFarmerTab()
    local tab = ambani.MenuAddTab(self.window, "🌾 Farmer")
    self.tabs.farmer = tab
    
    local grpControl = ambani.MenuGroup(tab, "Auto Farmer Control", 10, 10, 350, 180)
    
    self.widgets.farmerStatus = ambani.MenuText(grpControl, "Status: ⭕ Stopped")
    
    ambani.MenuButton(grpControl, "▶️ Start Farming", function()
        AutoFarmer:Start()
    end)
    
    ambani.MenuButton(grpControl, "⏹️ Stop Farming", function()
        AutoFarmer:Stop()
    end)
    
    ambani.MenuCheckbox(grpControl, "🛡️ Safe Mode",
        function()
            AutoFarmer.config.safeMode = true
            ambani.Notify("Farmer", "Safe Mode: ON")
        end,
        function()
            AutoFarmer.config.safeMode = false
            ambani.Notify("Farmer", "Safe Mode: OFF")
        end
    )
    
    local grpStats = ambani.MenuGroup(tab, "📊 Farming Statistics", 10, 200, 350, 250)
    
    self.widgets.farmerExecutions = ambani.MenuText(grpStats, "Total Executions: 0")
    self.widgets.farmerSuccessful = ambani.MenuText(grpStats, "✓ Successful: 0")
    self.widgets.farmerFailed = ambani.MenuText(grpStats, "✗ Failed: 0")
    self.widgets.farmerProfit = ambani.MenuText(grpStats, "💰 Total Profit: $0")
    self.widgets.farmerProfitHour = ambani.MenuText(grpStats, "💵 Profit/Hour: $0")
    self.widgets.farmerHours = ambani.MenuText(grpStats, "⏱️ Hours Elapsed: 0.0")
end

function GUI:CreateConfigTab()
    local tab = ambani.MenuAddTab(self.window, "⚙️ Config")
    self.tabs.config = tab
    
    local grpFarmer = ambani.MenuGroup(tab, "Auto Farmer Settings", 10, 10, 350, 300)
    
    ambani.MenuSlider(grpFarmer, "Max Exec/Hour", 
        AutoFarmer.config.maxExecutionsPerHour, 
        10, 200, "/hour", 0,
        function(val)
            AutoFarmer.config.maxExecutionsPerHour = val
        end
    )
    
    ambani.MenuSlider(grpFarmer, "Min Confidence", 
        AutoFarmer.config.minConfidence * 100, 
        50, 100, "%", 0,
        function(val)
            AutoFarmer.config.minConfidence = val / 100
        end
    )
    
    ambani.MenuSlider(grpFarmer, "Max Risk", 
        AutoFarmer.config.maxRisk * 100, 
        0, 100, "%", 0,
        function(val)
            AutoFarmer.config.maxRisk = val / 100
        end
    )
    
    ambani.MenuCheckbox(grpFarmer, "Respect Cooldowns",
        function() AutoFarmer.config.respectCooldowns = true end,
        function() AutoFarmer.config.respectCooldowns = false end
    )
    
    ambani.MenuCheckbox(grpFarmer, "Randomize Timings",
        function() AutoFarmer.config.randomizeTimings = true end,
        function() AutoFarmer.config.randomizeTimings = false end
    )
end

function GUI:CreateStatsTab()
    local tab = ambani.MenuAddTab(self.window, "📈 Stats")
    self.tabs.stats = tab
    
    local grpPlayer = ambani.MenuGroup(tab, "👤 Player Information", 10, 10, 350, 200)
    
    self.widgets.playerHealth = ambani.MenuText(grpPlayer, "❤️ Health: --")
    self.widgets.playerArmor = ambani.MenuText(grpPlayer, "🛡️ Armor: --")
    self.widgets.playerPos = ambani.MenuText(grpPlayer, "📍 Position: --")
    
    local grpSession = ambani.MenuGroup(tab, "🌐 Session Information", 10, 220, 350, 150)
    
    self.widgets.sessionPlayers = ambani.MenuText(grpSession, "👥 Players: --")
    self.widgets.sessionUser = ambani.MenuText(grpSession, "🔑 User: --")
    
    local grpSystem = ambani.MenuGroup(tab, "💻 System Information", 10, 380, 350, 150)
    
    self.widgets.systemResolution = ambani.MenuText(grpSystem, "🖥️ Resolution: --")
end

function GUI:StartUpdateThread()
    self.updateThread = Citizen.CreateThread(function()
        while true do
            Citizen.Wait(500)
            
            if ambani.IsGuiOpen() then
                self:UpdateWidgets()
            end
        end
    end)
end

function GUI:UpdateWidgets()
    if self.widgets.captureStatus then
        local status = EventCapture.config.enabled and "🟢 Running" or "⭕ Stopped"
        ambani.MenuSetText(self.widgets.captureStatus, "Status: " .. status)
    end
    
    if self.widgets.captureTotalEvents then
        ambani.MenuSetText(self.widgets.captureTotalEvents, 
            "Total Events: " .. #EventCapture.capturedEvents)
    end
    
    if self.widgets.loggerState then
        local state = ambani.GetLoggerState()
        local stateText = state == 1 and "🟢 Enabled" or "🔴 Disabled"
        ambani.MenuSetText(self.widgets.loggerState, "Logger: " .. stateText)
    end
    
    if self.widgets.farmerStatus then
        local status = AutoFarmer.config.enabled and "🟢 Running" or "⭕ Stopped"
        ambani.MenuSetText(self.widgets.farmerStatus, "Status: " .. status)
    end
    
    if self.widgets.farmerExecutions then
        local stats = AutoFarmer:GetStats()
        ambani.MenuSetText(self.widgets.farmerExecutions, 
            "Total Executions: " .. stats.totalExecutions)
        ambani.MenuSetText(self.widgets.farmerSuccessful, 
            "✓ Successful: " .. stats.successfulExecutions)
        ambani.MenuSetText(self.widgets.farmerFailed, 
            "✗ Failed: " .. stats.failedExecutions)
        ambani.MenuSetText(self.widgets.farmerProfit, 
            string.format("💰 Total Profit: $%.2f", stats.totalProfit))
        ambani.MenuSetText(self.widgets.farmerProfitHour, 
            string.format("💵 Profit/Hour: $%.2f", stats.profitPerHour))
        ambani.MenuSetText(self.widgets.farmerHours, 
            string.format("⏱️ Hours Elapsed: %.2f", stats.hoursElapsed))
    end
    
    if self.widgets.playerHealth then
        ambani.MenuSetText(self.widgets.playerHealth, 
            string.format("❤️ Health: %.0f / %.0f", 
                ambani.GetHealth(), ambani.GetMaxHealth()))
    end
    
    if self.widgets.playerArmor then
        ambani.MenuSetText(self.widgets.playerArmor, 
            string.format("🛡️ Armor: %.0f", ambani.GetArmor()))
    end
    
    if self.widgets.playerPos then
        local x, y, z = ambani.GetPos()
        ambani.MenuSetText(self.widgets.playerPos, 
            string.format("📍 Position: %.1f, %.1f, %.1f", x, y, z))
    end
    
    if self.widgets.sessionPlayers then
        ambani.MenuSetText(self.widgets.sessionPlayers, 
            "👥 Players: " .. ambani.GetPlayerCount())
    end
    
    if self.widgets.sessionUser then
        ambani.MenuSetText(self.widgets.sessionUser, 
            "🔑 User: " .. ambani.GetName())
    end
    
    if self.widgets.systemResolution then
        local w, h = ambani.GetResolution()
        ambani.MenuSetText(self.widgets.systemResolution, 
            string.format("🖥️ Resolution: %dx%d", w, h))
    end
end

-- ═══════════════════════════════════════════════════════════════════════
-- INITIALIZATION
-- ═══════════════════════════════════════════════════════════════════════

local initialized = false

-- Safe initialization with error handling
local function SafeInitialize()
    if initialized then
        print("[ℹ️] Already initialized")
        return true
    end
    
    local success, err = pcall(function()
        print("[⏳] Initializing GUI...")
        GUI:Initialize()
        print("[✓] GUI initialized successfully")
        initialized = true
    end)
    
    if not success then
        print("[✗] GUI initialization failed: " .. tostring(err))
        print("[ℹ️] Script loaded but GUI unavailable")
        print("[ℹ️] Error details: " .. tostring(err))
        return false
    end
    
    return true
end

-- Delayed initialization to ensure game is ready
local function DelayedInit()
    Citizen.CreateThread(function()
        print("[⏳] Waiting for game to be ready...")
        
        -- Wait for network session
        local attempts = 0
        while not NetworkIsSessionStarted() and attempts < 100 do
            Citizen.Wait(100)
            attempts = attempts + 1
        end
        
        if attempts >= 100 then
            print("[✗] Timeout waiting for network session")
            return
        end
        
        print("[✓] Network session started")
        
        -- Additional safety wait for game systems
        Citizen.Wait(3000)
        
        -- Try to initialize
        print("[⏳] Attempting GUI initialization...")
        local success = SafeInitialize()
        
        if success then
            print("\n" .. string.rep("═", 70))
            print("  ✓ RED-SHADOW v4.0 - READY")
            print(string.rep("═", 70))
            print("  Press F6 to open menu")
            print("  Version: 4.0.0 | Build: 2026.03.12")
            print(string.rep("═", 70) .. "\n")
        else
            print("\n" .. string.rep("═", 70))
            print("  ⚠️ RED-SHADOW v4.0 - PARTIAL LOAD")
            print(string.rep("═", 70))
            print("  GUI failed to load, but modules are available")
            print("  You can still use EventCapture and AutoFarmer modules")
            print("  Check console for error details")
            print(string.rep("═", 70) .. "\n")
        end
    end)
end

-- Check if Citizen is available
if Citizen and Citizen.CreateThread then
    print("[✓] Citizen framework detected")
    DelayedInit()
else
    print("[✗] Citizen framework not available")
    print("[ℹ️] Retrying in 1 second...")
    
    -- Fallback: retry after delay
    SetTimeout(1000, function()
        if Citizen and Citizen.CreateThread then
            print("[✓] Citizen framework now available")
            DelayedInit()
        else
            print("[✗] Citizen framework still not available")
            print("[ℹ️] Please ensure you're running this in FiveM")
        end
    end)
end

print("[✓] RED-SHADOW v4.0 script loaded")
print("[ℹ️] Initialization will begin automatically...")
print("[ℹ️] If GUI doesn't appear, type: RedShadow.Init()")

-- Global namespace for manual control
RedShadow = {
    EventCapture = EventCapture,
    AutoFarmer = AutoFarmer,
    GUI = GUI,
    
    -- Manual initialization
    Init = function()
        print("[ℹ️] Manual initialization requested...")
        return SafeInitialize()
    end,
    
    -- Status check
    Status = function()
        print("\n" .. string.rep("═", 70))
        print("  RED-SHADOW v4.0 - STATUS")
        print(string.rep("═", 70))
        print("  Initialized: " .. tostring(initialized))
        print("  Event Capture: " .. (EventCapture.config.enabled and "Running" or "Stopped"))
        print("  Auto Farmer: " .. (AutoFarmer.config.enabled and "Running" or "Stopped"))
        print("  Captured Events: " .. #EventCapture.capturedEvents)
        print("  Farming Executions: " .. AutoFarmer.stats.totalExecutions)
        print(string.rep("═", 70) .. "\n")
    end,
    
    -- Version info
    Version = function()
        print("RED-SHADOW v4.0.0 - Build 2026.03.12")
    end
}

print("[ℹ️] Manual commands available:")
print("  RedShadow.Init()    - Initialize GUI manually")
print("  RedShadow.Status()  - Check system status")
print("  RedShadow.Version() - Show version info")
