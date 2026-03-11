-- Exploit: spam:event
-- Description: Spam event
-- Risk Score: 0.50
-- Generated: 2026-03-11T21:20:35.496215
-- Method: Ambani.TriggerServerEvent

-- Safe Mode Check
local SAFE_MODE = true
if SAFE_MODE then
    print("WARNING: Safe mode enabled. Set SAFE_MODE = false to execute.")
    -- Uncomment to enable execution:
    -- SAFE_MODE = false
end

if SAFE_MODE then
    print("Exiting due to safe mode...")
    return
end

-- Logging Setup
local function Log(level, message)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    print(string.format("[%s] [%s] %s", timestamp, level, message))
end


-- Exploit execution
local function executeExploit()
    Log("INFO", "Executing exploit: spam:event")
    
    -- Prepare parameters
    local params = {
        "test",
    }
    
    
-- Rate Limiting (10 events/second)
local rateLimiter = {
    lastExecution = 0,
    minInterval = 100.0, -- milliseconds
    
    canExecute = function(self)
        local now = GetGameTimer()
        if now - self.lastExecution >= self.minInterval then
            self.lastExecution = now
            return true
        end
        return false
    end
}

-- Wrap execution with rate limiting
local originalExecute = executeExploit
executeExploit = function()
    if rateLimiter:canExecute() then
        originalExecute()
    else
        Log("WARN", "Rate limit exceeded, skipping execution")
    end
end

-- Execute via Ambani API
    Ambani.TriggerServerEvent("spam:event", table.unpack(params))
    Log("SUCCESS", "Event triggered: spam:event")
end


-- Rate Limiting (10 events/second)
local rateLimiter = {
    lastExecution = 0,
    minInterval = 100.0, -- milliseconds
    
    canExecute = function(self)
        local now = GetGameTimer()
        if now - self.lastExecution >= self.minInterval then
            self.lastExecution = now
            return true
        end
        return false
    end
}

-- Wrap execution with rate limiting
local originalExecute = executeExploit
executeExploit = function()
    if rateLimiter:canExecute() then
        originalExecute()
    else
        Log("WARN", "Rate limit exceeded, skipping execution")
    end
end

-- Execute
local success, error = pcall(executeExploit)
if not success then
    Log("ERROR", "Exploit failed: " .. tostring(error))
end
