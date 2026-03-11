-- Full Feature Menu
-- Interactive Ambani GUI Demo
-- Generated: 2026-03-11T21:20:35.493389

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


-- Create Interactive Window
local window = ambani.MenuTabbedWindow("Full Feature Menu", 150, 100, 600, 700, 140)
ambani.MenuSetAccent(window, 255, 100, 0) -- Orange accent
ambani.MenuSetKeybind(window, 0x74) -- F5

-- Tabs
local eventsTab = ambani.MenuAddTab(window, "Events")
local nativesTab = ambani.MenuAddTab(window, "Natives")
local playerTab = ambani.MenuAddTab(window, "Player")
local vehicleTab = ambani.MenuAddTab(window, "Vehicle")
local worldTab = ambani.MenuAddTab(window, "World")

-- Events Tab
local eventsGroup = ambani.MenuGroup(eventsTab, "Trigger Events", 10, 10, 540, 600)

ambani.MenuSmallText(eventsTab, "Server Events")

local eventInput = ambani.MenuInputbox(eventsGroup, "Event Name", "Enter event name...")
local param1Input = ambani.MenuInputbox(eventsGroup, "Parameter 1", "param1...")
local param2Input = ambani.MenuInputbox(eventsGroup, "Parameter 2", "param2...")

ambani.MenuButton(eventsGroup, "Trigger Server Event", function()
    local eventName = ambani.MenuGetInputbox(eventInput)
    local param1 = ambani.MenuGetInputbox(param1Input)
    local param2 = ambani.MenuGetInputbox(param2Input)
    
    if eventName ~= "" then
        TriggerServerEvent(eventName, param1, param2)
        ambani.Notify("Event", "Triggered: " .. eventName)
        Log("INFO", "Triggered event: " .. eventName)
    else
        ambani.Notify("Error", "Event name required")
    end
end)

ambani.MenuButton(eventsGroup, "Trigger Client Event (All)", function()
    local eventName = ambani.MenuGetInputbox(eventInput)
    local param1 = ambani.MenuGetInputbox(param1Input)
    
    if eventName ~= "" then
        TriggerClientEvent(eventName, -1, param1)
        ambani.Notify("Event", "Triggered client event")
    end
end)

-- Natives Tab
local nativesGroup = ambani.MenuGroup(nativesTab, "Native Functions", 10, 10, 540, 600)

ambani.MenuSmallText(nativesTab, "Common Natives")

local nativeHashInput = ambani.MenuInputbox(nativesGroup, "Native Hash", "0x...")

ambani.MenuButton(nativesGroup, "Invoke Native", function()
    local hash = ambani.MenuGetInputbox(nativeHashInput)
    if hash ~= "" then
        Citizen.InvokeNative(hash)
        ambani.Notify("Native", "Invoked: " .. hash)
    end
end)

-- Player Tab
local playerGroup = ambani.MenuGroup(playerTab, "Player Options", 10, 10, 540, 600)

ambani.MenuSmallText(playerTab, "Player Modifications")

local healthSlider = ambani.MenuSlider(playerGroup, "Health", 200, 0, 500, " HP", 0, function(val)
    SetEntityHealth(PlayerPedId(), val)
    ambani.Notify("Player", "Health set to " .. val)
end)

local armorSlider = ambani.MenuSlider(playerGroup, "Armor", 100, 0, 100, "%", 0, function(val)
    SetPedArmour(PlayerPedId(), val)
    ambani.Notify("Player", "Armor set to " .. val)
end)

ambani.MenuCheckbox(playerGroup, "God Mode",
    function()
        SetEntityInvincible(PlayerPedId(), true)
        ambani.Notify("Player", "God mode enabled")
    end,
    function()
        SetEntityInvincible(PlayerPedId(), false)
        ambani.Notify("Player", "God mode disabled")
    end
)

ambani.MenuCheckbox(playerGroup, "Invisible",
    function()
        SetEntityVisible(PlayerPedId(), false, false)
        ambani.Notify("Player", "Invisible enabled")
    end,
    function()
        SetEntityVisible(PlayerPedId(), true, false)
        ambani.Notify("Player", "Invisible disabled")
    end
)

ambani.MenuButton(playerGroup, "Heal", function()
    SetEntityHealth(PlayerPedId(), 200)
    SetPedArmour(PlayerPedId(), 100)
    ambani.Notify("Player", "Healed")
end)

ambani.MenuButton(playerGroup, "Suicide", function()
    SetEntityHealth(PlayerPedId(), 0)
    ambani.Notify("Player", "Suicide")
end)

-- Vehicle Tab
local vehicleGroup = ambani.MenuGroup(vehicleTab, "Vehicle Options", 10, 10, 540, 600)

ambani.MenuSmallText(vehicleTab, "Vehicle Modifications")

ambani.MenuCheckbox(vehicleGroup, "Vehicle God Mode",
    function()
        local veh = GetVehiclePedIsIn(PlayerPedId(), false)
        if veh ~= 0 then
            SetEntityInvincible(veh, true)
            ambani.Notify("Vehicle", "God mode enabled")
        end
    end,
    function()
        local veh = GetVehiclePedIsIn(PlayerPedId(), false)
        if veh ~= 0 then
            SetEntityInvincible(veh, false)
            ambani.Notify("Vehicle", "God mode disabled")
        end
    end
)

local speedSlider = ambani.MenuSlider(vehicleGroup, "Speed Multiplier", 1.0, 0.5, 5.0, "x", 1, function(val)
    local veh = GetVehiclePedIsIn(PlayerPedId(), false)
    if veh ~= 0 then
        SetVehicleEnginePowerMultiplier(veh, val)
        ambani.Notify("Vehicle", "Speed set to " .. val .. "x")
    end
end)

ambani.MenuButton(vehicleGroup, "Repair Vehicle", function()
    local veh = GetVehiclePedIsIn(PlayerPedId(), false)
    if veh ~= 0 then
        SetVehicleFixed(veh)
        SetVehicleDeformationFixed(veh)
        ambani.Notify("Vehicle", "Repaired")
    else
        ambani.Notify("Error", "Not in vehicle")
    end
end)

ambani.MenuButton(vehicleGroup, "Flip Vehicle", function()
    local veh = GetVehiclePedIsIn(PlayerPedId(), false)
    if veh ~= 0 then
        SetVehicleOnGroundProperly(veh)
        ambani.Notify("Vehicle", "Flipped")
    end
end)

-- World Tab
local worldGroup = ambani.MenuGroup(worldTab, "World Options", 10, 10, 540, 600)

ambani.MenuSmallText(worldTab, "World Modifications")

local timeSlider = ambani.MenuSlider(worldGroup, "Time", 12, 0, 23, ":00", 0, function(val)
    NetworkOverrideClockTime(val, 0, 0)
    ambani.Notify("World", "Time set to " .. val .. ":00")
end)

ambani.MenuDropDown(worldGroup, "Weather", function(idx)
    local weathers = ('CLEAR', 'EXTRASUNNY', 'CLOUDS', 'OVERCAST', 'RAIN', 'THUNDER', 'SNOW', 'BLIZZARD', 'FOGGY')
    if weathers[idx] then
        SetWeatherTypeNowPersist(weathers[idx])
        ambani.Notify("World", "Weather: " .. weathers[idx])
    end
end, "Clear", "Extra Sunny", "Clouds", "Overcast", "Rain", "Thunder", "Snow", "Blizzard", "Foggy")

ambani.MenuCheckbox(worldGroup, "Freeze Time",
    function()
        Citizen.CreateThread(function()
            while true do
                NetworkOverrideClockTime(12, 0, 0)
                Citizen.Wait(100)
            end
        end)
        ambani.Notify("World", "Time frozen")
    end,
    function()
        ambani.Notify("World", "Time unfrozen")
    end
)

-- Cleanup
AddEventHandler('onResourceStop', function(resourceName)
    if GetCurrentResourceName() == resourceName then
        ambani.MenuDestroy(window)
        Log("INFO", "Interactive menu destroyed")
    end
end)

Log("INFO", "Interactive menu loaded - Press F5 to toggle")
