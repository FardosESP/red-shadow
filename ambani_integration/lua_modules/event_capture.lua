--[[
    Event Capture Module (Lua)
    CLIENT-SIDE event capture for FiveM
    
    PURPOSE: Lightweight real-time event capture
    - Captures events as they happen in-game
    - Saves raw data to JSON
    - Minimal processing for performance
    
    ANALYSIS: Done by Python (event_analyzer.py)
    - Advanced statistical analysis
    - Machine learning pattern detection
    - Strategy generation
    
    EXECUTION: Done by Lua (auto_farmer.lua)
    - Reads strategies from Python
    - Executes farming with Ambani API
]]

local EventCapture = {}

-- Configuration
EventCapture.config = {
    enabled = false,
    maxEvents = 5000,
    autoSave = true,
    saveInterval = 60000, -- 1 minute
    outputFile = "captured_events.json",
    captureAllEvents = false, -- If true, captures ALL events (very verbose)
    verboseLogging = false
}

-- Storage
EventCapture.capturedEvents = {}
EventCapture.eventStats = {}
EventCapture.sessionStart = os.time()

-- Reward detection patterns
EventCapture.patterns = {
    money = {"money", "cash", "bank", "salary", "payment", "pay", "reward", "earn", "income", "deposit", "balance"},
    item = {"item", "inventory", "give", "add", "receive", "loot", "drop", "pickup", "collect"},
    xp = {"xp", "exp", "experience", "level", "rank", "skill", "progress", "achievement"},
    job = {"job:", "work:", "mission:", "delivery:", "taxi:", "mechanic:", "police:", "ems:", "trucker:", "miner:", "farmer:", "fisher:", "lumberjack:", "garbage:", "postop:", "courier:", "bus:", "pilot:"},
    blacklist = {"admin:", "ban:", "kick:", "anticheat:", "log:", "report:", "staff:", "mod:", "cheat:", "exploit:"}
}

-- Utility: Check if string contains pattern
local function ContainsPattern(str, patterns)
    local lowerStr = string.lower(str)
    for _, pattern in ipairs(patterns) do
        if string.find(lowerStr, pattern, 1, true) then
            return true
        end
    end
    return false
end

-- Basic reward detection (lightweight for real-time capture)
-- Full analysis will be done by Python analyzer
function EventCapture:DetectReward(eventName, params)
    local rewardType = nil
    local rewardAmount = nil
    
    -- Simple keyword matching
    if ContainsPattern(eventName, self.patterns.money) then
        rewardType = "money"
        for _, param in ipairs(params) do
            if type(param) == "number" and param > 0 then
                rewardAmount = param
                break
            end
        end
    elseif ContainsPattern(eventName, self.patterns.item) then
        rewardType = "item"
        for _, param in ipairs(params) do
            if type(param) == "number" and param > 0 then
                rewardAmount = param
                break
            end
        end
    elseif ContainsPattern(eventName, self.patterns.xp) then
        rewardType = "xp"
        for _, param in ipairs(params) do
            if type(param) == "number" and param > 0 then
                rewardAmount = param
                break
            end
        end
    end
    
    return rewardType, rewardAmount
end

-- Basic job event detection
function EventCapture:IsJobEvent(eventName)
    return ContainsPattern(eventName, self.patterns.job)
end

-- Basic blacklist check
function EventCapture:IsBlacklisted(eventName)
    return ContainsPattern(eventName, self.patterns.blacklist)
end

-- Capture an event
function EventCapture:Capture(eventName, ...)
    if not self.config.enabled then
        return
    end
    
    -- Check limits
    if #self.capturedEvents >= self.config.maxEvents then
        print("[EventCapture] Max events reached, stopping capture")
        self.config.enabled = false
        return
    end
    
    -- Skip blacklisted events
    if self:IsBlacklisted(eventName) then
        return
    end
    
    local params = {...}
    local rewardType, rewardAmount = self:DetectReward(eventName, params)
    local isJob = self:IsJobEvent(eventName)
    
    -- Create event record
    local event = {
        name = eventName,
        params = params,
        timestamp = os.date("%Y-%m-%d %H:%M:%S"),
        gameTime = GetGameTimer(),
        rewardType = rewardType,
        rewardAmount = rewardAmount,
        isJob = isJob,
        playerPos = GetEntityCoords(PlayerPedId())
    }
    
    table.insert(self.capturedEvents, event)
    
    -- Update statistics
    if not self.eventStats[eventName] then
        self.eventStats[eventName] = {
            count = 0,
            totalReward = 0,
            avgReward = 0,
            isJob = isJob,
            rewardType = rewardType,
            firstSeen = os.time(),
            lastSeen = os.time(),
            parameters = {}
        }
    end
    
    local stats = self.eventStats[eventName]
    stats.count = stats.count + 1
    stats.lastSeen = os.time()
    
    if rewardAmount then
        stats.totalReward = stats.totalReward + rewardAmount
        stats.avgReward = stats.totalReward / stats.count
    end
    
    -- Track parameter patterns
    local paramKey = json.encode(params)
    if not stats.parameters[paramKey] then
        stats.parameters[paramKey] = 0
    end
    stats.parameters[paramKey] = stats.parameters[paramKey] + 1
    
    -- Verbose logging
    if self.config.verboseLogging then
        if rewardAmount then
            print(string.format("[EventCapture] %s: %s = %.2f", eventName, rewardType, rewardAmount))
        else
            print(string.format("[EventCapture] %s", eventName))
        end
    end
end

-- Hook into an event
function EventCapture:HookEvent(eventName)
    AddEventHandler(eventName, function(...)
        self:Capture(eventName, ...)
    end)
end

-- Hook into ALL events (very verbose, use with caution)
function EventCapture:HookAllEvents()
    -- This is a meta-hook that captures everything
    -- WARNING: This can be very resource intensive
    local originalAddEventHandler = AddEventHandler
    
    AddEventHandler = function(eventName, callback)
        -- Wrap the callback to capture
        local wrappedCallback = function(...)
            EventCapture:Capture(eventName, ...)
            return callback(...)
        end
        
        return originalAddEventHandler(eventName, wrappedCallback)
    end
    
    print("[EventCapture] Hooked into ALL events (meta-hook active)")
end

-- Save captured data to JSON
function EventCapture:Save()
    local data = {
        sessionStart = self.sessionStart,
        sessionEnd = os.time(),
        sessionDuration = os.time() - self.sessionStart,
        totalEvents = #self.capturedEvents,
        uniqueEvents = 0,
        jobEvents = 0,
        rewardEvents = 0,
        events = self.capturedEvents,
        stats = {}
    }
    
    -- Convert stats to array for JSON
    for name, stats in pairs(self.eventStats) do
        data.uniqueEvents = data.uniqueEvents + 1
        if stats.isJob then
            data.jobEvents = data.jobEvents + 1
        end
        if stats.totalReward > 0 then
            data.rewardEvents = data.rewardEvents + 1
        end
        
        table.insert(data.stats, {
            name = name,
            count = stats.count,
            totalReward = stats.totalReward,
            avgReward = stats.avgReward,
            isJob = stats.isJob,
            rewardType = stats.rewardType,
            firstSeen = stats.firstSeen,
            lastSeen = stats.lastSeen,
            duration = stats.lastSeen - stats.firstSeen
        })
    end
    
    -- Sort stats by count
    table.sort(data.stats, function(a, b)
        return a.count > b.count
    end)
    
    -- Save to file (in real FiveM, use SaveResourceFile)
    local jsonData = json.encode(data, {indent = true})
    
    -- For FiveM resource
    if SaveResourceFile then
        SaveResourceFile(GetCurrentResourceName(), self.config.outputFile, jsonData, -1)
        print(string.format("[EventCapture] Saved %d events to %s", #self.capturedEvents, self.config.outputFile))
    else
        -- Fallback: print to console
        print("[EventCapture] JSON Data:")
        print(jsonData)
    end
    
    return jsonData
end

-- Get statistics
function EventCapture:GetStats()
    local jobEvents = 0
    local rewardEvents = 0
    local totalReward = 0
    
    for name, stats in pairs(self.eventStats) do
        if stats.isJob then
            jobEvents = jobEvents + 1
        end
        if stats.totalReward > 0 then
            rewardEvents = rewardEvents + 1
            totalReward = totalReward + stats.totalReward
        end
    end
    
    return {
        totalCaptured = #self.capturedEvents,
        uniqueEvents = self:CountKeys(self.eventStats),
        jobEvents = jobEvents,
        rewardEvents = rewardEvents,
        totalReward = totalReward,
        sessionDuration = os.time() - self.sessionStart
    }
end

-- Count table keys
function EventCapture:CountKeys(tbl)
    local count = 0
    for _ in pairs(tbl) do
        count = count + 1
    end
    return count
end

-- Get top events
function EventCapture:GetTopEvents(limit)
    limit = limit or 10
    
    local sorted = {}
    for name, stats in pairs(self.eventStats) do
        table.insert(sorted, {name = name, stats = stats})
    end
    
    table.sort(sorted, function(a, b)
        return a.stats.count > b.stats.count
    end)
    
    local result = {}
    for i = 1, math.min(limit, #sorted) do
        table.insert(result, sorted[i])
    end
    
    return result
end

-- Get farming opportunities (job events with rewards)
function EventCapture:GetFarmingOpportunities(minCount)
    minCount = minCount or 3
    
    local opportunities = {}
    
    for name, stats in pairs(self.eventStats) do
        if stats.isJob and stats.count >= minCount and stats.avgReward > 0 then
            -- Calculate cooldown (average time between events)
            local cooldown = 60 -- default
            if stats.count > 1 then
                cooldown = math.floor(stats.duration / stats.count)
            end
            
            -- Calculate profit per hour
            local profitPerHour = 0
            if cooldown > 0 then
                profitPerHour = (3600 / cooldown) * stats.avgReward
            end
            
            table.insert(opportunities, {
                name = name,
                avgReward = stats.avgReward,
                totalReward = stats.totalReward,
                count = stats.count,
                cooldown = cooldown,
                profitPerHour = profitPerHour,
                rewardType = stats.rewardType
            })
        end
    end
    
    -- Sort by profit per hour
    table.sort(opportunities, function(a, b)
        return a.profitPerHour > b.profitPerHour
    end)
    
    return opportunities
end

-- Start capture
function EventCapture:Start()
    self.config.enabled = true
    self.sessionStart = os.time()
    print("[EventCapture] Started capturing events")
end

-- Stop capture
function EventCapture:Stop()
    self.config.enabled = false
    print("[EventCapture] Stopped capturing events")
end

-- Clear data
function EventCapture:Clear()
    self.capturedEvents = {}
    self.eventStats = {}
    self.sessionStart = os.time()
    print("[EventCapture] Cleared all captured data")
end

-- Auto-save thread
Citizen.CreateThread(function()
    while true do
        Citizen.Wait(EventCapture.config.saveInterval)
        
        if EventCapture.config.enabled and EventCapture.config.autoSave then
            if #EventCapture.capturedEvents > 0 then
                EventCapture:Save()
            end
        end
    end
end)

-- Statistics display thread
Citizen.CreateThread(function()
    while true do
        Citizen.Wait(60000) -- Every minute
        
        if EventCapture.config.enabled and #EventCapture.capturedEvents > 0 then
            local stats = EventCapture:GetStats()
            print(string.format("[EventCapture] Stats: %d events | %d unique | %d jobs | %.2f total reward",
                stats.totalCaptured, stats.uniqueEvents, stats.jobEvents, stats.totalReward))
        end
    end
end)

-- Commands
RegisterCommand('capture', function(source, args)
    local cmd = args[1]
    
    if cmd == 'start' then
        EventCapture:Start()
    elseif cmd == 'stop' then
        EventCapture:Stop()
    elseif cmd == 'save' then
        EventCapture:Save()
    elseif cmd == 'clear' then
        EventCapture:Clear()
    elseif cmd == 'stats' then
        local stats = EventCapture:GetStats()
        print("=== Event Capture Statistics ===")
        print(string.format("Total Events: %d", stats.totalCaptured))
        print(string.format("Unique Events: %d", stats.uniqueEvents))
        print(string.format("Job Events: %d", stats.jobEvents))
        print(string.format("Reward Events: %d", stats.rewardEvents))
        print(string.format("Total Reward: %.2f", stats.totalReward))
        print(string.format("Session Duration: %d seconds", stats.sessionDuration))
    elseif cmd == 'top' then
        local limit = tonumber(args[2]) or 10
        local top = EventCapture:GetTopEvents(limit)
        print(string.format("=== Top %d Events ===", limit))
        for i, entry in ipairs(top) do
            print(string.format("[%d] %s: %d times (%.2f avg reward)",
                i, entry.name, entry.stats.count, entry.stats.avgReward))
        end
    elseif cmd == 'farm' then
        local opportunities = EventCapture:GetFarmingOpportunities()
        print("=== Farming Opportunities ===")
        for i, opp in ipairs(opportunities) do
            print(string.format("[%d] %s: %.2f/exec, %ds cooldown, %.2f/hour",
                i, opp.name, opp.avgReward, opp.cooldown, opp.profitPerHour))
        end
    elseif cmd == 'hook' then
        local eventName = args[2]
        if eventName then
            EventCapture:HookEvent(eventName)
            print("[EventCapture] Hooked into: " .. eventName)
        else
            print("[EventCapture] Usage: /capture hook <event_name>")
        end
    elseif cmd == 'hookall' then
        EventCapture:HookAllEvents()
    else
        print("=== Event Capture Commands ===")
        print("/capture start - Start capturing")
        print("/capture stop - Stop capturing")
        print("/capture save - Save to file")
        print("/capture clear - Clear data")
        print("/capture stats - Show statistics")
        print("/capture top [n] - Show top N events")
        print("/capture farm - Show farming opportunities")
        print("/capture hook <event> - Hook specific event")
        print("/capture hookall - Hook ALL events (verbose)")
    end
end, false)

-- Export for use in other scripts
exports('GetEventCapture', function()
    return EventCapture
end)

print("[EventCapture] Module loaded - Use /capture for commands")

return EventCapture
