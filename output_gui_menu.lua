-- Exploit Menu
-- Ambani GUI Menu
-- Generated: 2026-03-11T21:20:35.492130
-- Toggle Key: F5

-- Logging Setup
local function Log(level, message)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    print(string.format("[%s] [%s] %s", timestamp, level, message))
end

-- Ambani GUI API Wrapper
-- All GUI functions are already available via ambani.Menu* prefix
-- This wrapper adds error handling and logging

-- Notification helper
if not ambani.Notify then
    function ambani.Notify(title, message)
        SetNotificationTextEntry("STRING")
        AddTextComponentString(message)
        DrawNotification(false, false)
        Log("NOTIFY", title .. ": " .. message)
    end
end

-- Key detection helper
if not ambani.OnKeyDown then
    function ambani.OnKeyDown(callback)
        Citizen.CreateThread(function()
            while true do
                Citizen.Wait(0)
                for key = 0, 255 do
                    if IsControlJustPressed(0, key) then
                        callback(key)
                    end
                end
            end
        end)
    end
end


-- Create Main Window
local mainWindow = ambani.MenuTabbedWindow("Exploit Menu", 200, 100, 500, 600, 120)
ambani.MenuSetAccent(mainWindow, 0, 150, 255) -- Blue accent
ambani.MenuSetKeybind(mainWindow, 116) -- F5 to toggle

Log("INFO", "Menu created - Press F5 to toggle")

-- Create Tabs
local exploitsTab = ambani.MenuAddTab(mainWindow, "Exploits")
local settingsTab = ambani.MenuAddTab(mainWindow, "Settings")
local infoTab = ambani.MenuAddTab(mainWindow, "Info")

-- Exploits Group
local exploitsGroup = ambani.MenuGroup(exploitsTab, "Available Exploits", 10, 10, 460, 500)

-- Exploit 1: bank:deposit
ambani.MenuButton(exploitsGroup, "bank:deposit", function()
    Log("INFO", "Executing: bank:deposit")
    Ambani.TriggerServerEvent("bank:deposit", 1000000)
    ambani.Notify("Exploit", "bank:deposit executed!")
end)

-- Exploit 2: bank:withdraw
ambani.MenuButton(exploitsGroup, "bank:withdraw", function()
    Log("INFO", "Executing: bank:withdraw")
    Ambani.TriggerServerEvent("bank:withdraw", 500000)
    ambani.Notify("Exploit", "bank:withdraw executed!")
end)

-- Exploit 3: inventory:addItem
ambani.MenuButton(exploitsGroup, "inventory:addItem", function()
    Log("INFO", "Executing: inventory:addItem")
    Ambani.TriggerServerEvent("inventory:addItem", "weapon_pistol", 5)
    ambani.Notify("Exploit", "inventory:addItem executed!")
end)

-- Exploit 4: vehicle:spawn
ambani.MenuButton(exploitsGroup, "vehicle:spawn", function()
    Log("INFO", "Executing: vehicle:spawn")
    Ambani.TriggerServerEvent("vehicle:spawn", "adder")
    ambani.Notify("Exploit", "vehicle:spawn executed!")
end)

-- Settings Group
local settingsGroup = ambani.MenuGroup(settingsTab, "Configuration", 10, 10, 460, 500)

-- Rate limiting slider
local rateLimit = 10
ambani.MenuSlider(settingsGroup, "Rate Limit", 10, 1, 100, " evt/s", 0, function(val)
    rateLimit = val
    Log("INFO", "Rate limit set to: " .. val)
end)

-- Safe mode checkbox
local safeMode = true
ambani.MenuCheckbox(settingsGroup, "Safe Mode", 
    function() 
        safeMode = false
        Log("WARN", "Safe mode disabled")
    end,
    function() 
        safeMode = true
        Log("INFO", "Safe mode enabled")
    end
)

-- Server input
local serverInput = ambani.MenuInputbox(settingsGroup, "Server IP", "Enter server IP...")

-- Info Group
local infoGroup = ambani.MenuGroup(infoTab, "Information", 10, 10, 460, 500)

ambani.MenuSmallText(infoTab, "Ambani Integration")
ambani.MenuText(infoGroup, "Version: 1.0.0")
ambani.MenuText(infoGroup, "Exploits: 4")
ambani.MenuText(infoGroup, "Generated: 2026-03-11 21:20")
ambani.MenuText(infoGroup, "")
ambani.MenuText(infoGroup, "Press F5 to toggle menu")
ambani.MenuText(infoGroup, "")
ambani.MenuText(infoGroup, "WARNING: For authorized testing only")


-- Cleanup on resource stop
AddEventHandler('onResourceStop', function(resourceName)
    if GetCurrentResourceName() == resourceName then
        if mainWindow then
            ambani.MenuDestroy(mainWindow)
            Log("INFO", "Menu destroyed")
        end
    end
end)

Log("INFO", "Script loaded successfully")
