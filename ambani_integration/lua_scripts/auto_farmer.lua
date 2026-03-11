--[[
    Auto Farmer (Lua)
    Automated event farming with Ambani API
    
    Reads farming strategies from Python analyzer (farming_strategies.json)
    and executes them with rate limiting and anticheat evasion.
]]

local AutoFarmer = {}

-- Configuration
AutoFarmer.config = {
    enabled = false,
    safeMode = true,  -- Requires manual activation
    strategiesFile = "farming_strategies.json",
    respectCooldowns = true,
    randomizeTimings = true,
    maxExecutionsPerHour = 50,
    stopOnDetection = true,
    minConfidence = 0.80,
    maxRisk = 0.60
}

-- State
AutoFarmer.strategies = {}
AutoFarmer.stats = {
    totalExecutions = 0,
    totalProfit = 0,
    startTime = os.time(),
    successfulExecutions = 0,
    failedExecutions = 0
}

-- Logging
local function Log(level, message)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    print(string.format("[%s] [AutoFarmer] [%s] %s", timestamp, level, message))
end

-- Load strategies from JSON file
function AutoFarmer:LoadStrategies()
    -- In real FiveM, use LoadResourceFile
    local jsonData = LoadResourceFile(GetCurrentResourceName(), self.config.strategiesFile)
    
    if not jsonData then
        Log("ERROR", "Failed to load strategies file: " .. self.config.strategiesFile)
        return false
    end
    
    local data = json.decode(jsonData)
    if not data or not data.strategies then
        Log("ERROR", "Invalid strategies file format")
        return false
    end
    
    -- Filter strategies by confidence and risk
    local filtered = {}
    for _, strategy in ipairs(data.strategies) do
        if strategy.confidence >= self.config.minConfidence and
           strategy.detectionRisk <= self.config.maxRisk then
            table.insert(filtered, {
                event = strategy.event,
                params = strategy.params,
                rewardType = strategy.rewardType,
                avgReward = strategy.avgReward,
                cooldown = strategy.cooldown,
                detectionRisk = strategy.detectionRisk,
                profitPerHour = strategy.profitPerHour,
                enabled = true,
                executions = 0,
                lastExecution = 0,
                successCount = 0,
                failCount = 0
            })
        end
    end
    
    -- Sort by profit per hour
    table.sort(filtered, function(a, b)
        return a.profitPerHour > b.profitPerHour
    end)
    
    self.strategies = filtered
    
    Log("INFO", string.format("Loaded %d strategies (filtered from %d)", 
        #filtered, #data.strategies))
    
    return true
end

-- Check if strategy can be executed
function AutoFarmer:CanExecute(strategy)
    if not self.config.enabled or not strategy.enabled then
        return false
    end
    
    -- Check cooldown
    if self.config.respectCooldowns then
        local now = GetGameTimer()
        local elapsed = (now - strategy.lastExecution) / 1000
        if elapsed < strategy.cooldown then
            return false
        end
    end
    
    -- Check rate limit
    local hoursElapsed = (os.time() - self.stats.startTime) / 3600
    if hoursElapsed > 0 then
        local currentRate = self.stats.totalExecutions / hoursElapsed
        if currentRate >= self.config.maxExecutionsPerHour then
            Log("WARN", "Rate limit reached, pausing farming")
            return false
        end
    end
    
    return true
end

-- Execute a farming strategy
function AutoFarmer:Execute(strategy)
    if not self:CanExecute(strategy) then
        return false
    end
    
    -- Add random delay for stealth
    if self.config.randomizeTimings then
        local randomDelay = math.random(1000, 5000)
        Citizen.Wait(randomDelay)
    end
    
    -- Execute event via Ambani API
    Log("INFO", "Farming: " .. strategy.event)
    
    local success, error = pcall(function()
        TriggerServerEvent(strategy.event, table.unpack(strategy.params))
    end)
    
    -- Update tracking
    strategy.lastExecution = GetGameTimer()
    strategy.executions = strategy.executions + 1
    self.stats.totalExecutions = self.stats.totalExecutions + 1
    
    if success then
        strategy.successCount = strategy.successCount + 1
        self.stats.successfulExecutions = self.stats.successfulExecutions + 1
        self.stats.totalProfit = self.stats.totalProfit + strategy.avgReward
        
        Log("SUCCESS", string.format("Executed %s (Total: %d, Profit: %.2f)",
            strategy.event, self.stats.totalExecutions, self.stats.totalProfit))
    else
        strategy.failCount = strategy.failCount + 1
        self.stats.failedExecutions = self.stats.failedExecutions + 1
        Log("ERROR", "Execution failed: " .. tostring(error))
    end
    
    return success
end

-- Main farming loop
function AutoFarmer:Start()
    if self.config.safeMode then
        Log("WARN", "Safe mode enabled - Set config.safeMode = false to start")
        return
    end
    
    if #self.strategies == 0 then
        Log("ERROR", "No strategies loaded - Run /farmer load first")
        return
    end
    
    self.config.enabled = true
    self.stats.startTime = os.time()
    
    Log("INFO", "Auto Farmer started with " .. #self.strategies .. " strategies")
    
    Citizen.CreateThread(function()
        while self.config.enabled do
            -- Try each strategy
            for _, strategy in ipairs(self.strategies) do
                if self:Execute(strategy) then
                    -- Wait after successful execution
                    Citizen.Wait(5000)
                end
            end
            
            -- Wait before next cycle
            Citizen.Wait(10000)
        end
        
        Log("INFO", "Auto Farmer stopped")
    end)
end

-- Stop farming
function AutoFarmer:Stop()
    self.config.enabled = false
    Log("INFO", "Stopping auto farmer...")
end

-- Get statistics
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

-- Print statistics
function AutoFarmer:PrintStats()
    local stats = self:GetStats()
    
    print("=== Auto Farmer Statistics ===")
    print(string.format("Total Executions: %d", stats.totalExecutions))
    print(string.format("Successful: %d", stats.successfulExecutions))
    print(string.format("Failed: %d", stats.failedExecutions))
    print(string.format("Total Profit: %.2f", stats.totalProfit))
    print(string.format("Profit/Hour: %.2f", stats.profitPerHour))
    print(string.format("Hours Elapsed: %.2f", stats.hoursElapsed))
    print(string.format("Strategies: %d", stats.strategiesLoaded))
    
    print("\n=== Strategy Performance ===")
    for i, strategy in ipairs(self.strategies) do
        local successRate = 0
        if strategy.executions > 0 then
            successRate = (strategy.successCount / strategy.executions) * 100
        end
        
        print(string.format("[%d] %s: %d execs (%.1f%% success, %.2f/hour)",
            i, strategy.event, strategy.executions, successRate, strategy.profitPerHour))
    end
end

-- Commands
RegisterCommand('farmer', function(source, args)
    local cmd = args[1]
    
    if cmd == 'load' then
        if AutoFarmer:LoadStrategies() then
            print("Strategies loaded successfully")
        else
            print("Failed to load strategies")
        end
        
    elseif cmd == 'start' then
        AutoFarmer:Start()
        
    elseif cmd == 'stop' then
        AutoFarmer:Stop()
        
    elseif cmd == 'stats' then
        AutoFarmer:PrintStats()
        
    elseif cmd == 'list' then
        print("=== Available Strategies ===")
        for i, strategy in ipairs(AutoFarmer.strategies) do
            print(string.format("[%d] %s (%.2f/hour, %.1f%% risk, %ds cooldown)",
                i, strategy.event, strategy.profitPerHour, 
                strategy.detectionRisk * 100, strategy.cooldown))
        end
        
    elseif cmd == 'enable' then
        local id = tonumber(args[2])
        if id and AutoFarmer.strategies[id] then
            AutoFarmer.strategies[id].enabled = true
            print("Enabled strategy: " .. AutoFarmer.strategies[id].event)
        else
            print("Invalid strategy ID")
        end
        
    elseif cmd == 'disable' then
        local id = tonumber(args[2])
        if id and AutoFarmer.strategies[id] then
            AutoFarmer.strategies[id].enabled = false
            print("Disabled strategy: " .. AutoFarmer.strategies[id].event)
        else
            print("Invalid strategy ID")
        end
        
    elseif cmd == 'config' then
        print("=== Configuration ===")
        print(string.format("Enabled: %s", tostring(AutoFarmer.config.enabled)))
        print(string.format("Safe Mode: %s", tostring(AutoFarmer.config.safeMode)))
        print(string.format("Respect Cooldowns: %s", tostring(AutoFarmer.config.respectCooldowns)))
        print(string.format("Randomize Timings: %s", tostring(AutoFarmer.config.randomizeTimings)))
        print(string.format("Max Executions/Hour: %d", AutoFarmer.config.maxExecutionsPerHour))
        print(string.format("Min Confidence: %.2f", AutoFarmer.config.minConfidence))
        print(string.format("Max Risk: %.2f", AutoFarmer.config.maxRisk))
        
    else
        print("=== Auto Farmer Commands ===")
        print("/farmer load - Load strategies from file")
        print("/farmer start - Start farming")
        print("/farmer stop - Stop farming")
        print("/farmer stats - Show statistics")
        print("/farmer list - List strategies")
        print("/farmer enable <id> - Enable strategy")
        print("/farmer disable <id> - Disable strategy")
        print("/farmer config - Show configuration")
    end
end, false)

-- Export for use in other scripts
exports('GetAutoFarmer', function()
    return AutoFarmer
end)

Log("INFO", "Auto Farmer loaded - Use /farmer for commands")

return AutoFarmer
