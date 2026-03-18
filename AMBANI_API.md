FiveM - LUA API
Introduction
Welcome to the Ambani Lua API reference. This guide covers all available functions inside the ambani.* namespace, accessible from within the executor.

The API is organized into the following categories: Input, Key Callbacks, Player, General, Logger, Notifications, Clipboard, Screen, HTTP, Utility, Resource Injection, and Graphics/GUI.

Compatibility Notice
This API is exclusive to the Ambani executor environment.
Input
Functions for reading keyboard and mouse state on the current frame.

ambani.IsKeyDown(vk)
Checks if a key is currently held down.

vk number — Virtual key code (e.g. 0x41 for A)
Returns boolean
if ambani.IsKeyDown(0x41) then print("A is held") end
ambani.IsKeyPressed(vk)
Checks if a key was just pressed this frame (transition from up → down).

vk number — Virtual key code
Returns boolean
if ambani.IsKeyPressed(0x45) then print("E just pressed") end
ambani.IsKeyReleased(vk)
Checks if a key was just released this frame (transition from down → up).

vk number — Virtual key code
Returns boolean
if ambani.IsKeyReleased(0x45) then print("E just released") end
ambani.GetCursorX()
Gets the cursor X position on screen (pixels from left).

Returns number
local x = ambani.GetCursorX()
ambani.GetCursorY()
Gets the cursor Y position on screen (pixels from top).

Returns number
local y = ambani.GetCursorY()
ambani.GetCursorPos()
Gets both cursor coordinates at once.

Returns number, number — x, y
local x, y = ambani.GetCursorPos()
ambani.IsMouseDown(btn)
Checks if a mouse button is currently held down.

btn number — 0 = Left, 1 = Right, 2 = Middle
Returns boolean
if ambani.IsMouseDown(0) then print("Left mouse held") end
ambani.IsMouseClicked(btn)
Checks if a mouse button was just clicked this frame.

btn number — 0 = Left, 1 = Right, 2 = Middle
Returns boolean
if ambani.IsMouseClicked(0) then print("Left click!") end
ambani.IsMouseReleased(btn)
Checks if a mouse button was just released this frame.

btn number — 0 = Left, 1 = Right, 2 = Middle
Returns boolean
if ambani.IsMouseReleased(1) then print("Right mouse released") end
Key Callbacks
Register persistent callbacks that fire on key events.

ambani.OnKeyDown(callback)
Registers a callback for key press events. Called once per key when it goes down.

callback function(vk) — Receives the virtual key code
ambani.OnKeyDown(function(vk)
    print("Key pressed: " .. vk)
end)
ambani.OnKeyUp(callback)
Registers a callback for key release events.

callback function(vk) — Receives the virtual key code
ambani.OnKeyUp(function(vk)
    print("Key released: " .. vk)
end)
Player
Functions for reading local player state and session info.

ambani.GetHealth()
Gets local player health.

Returns number — Current health (0–200)
print("Health: " .. ambani.GetHealth())
ambani.GetMaxHealth()
Gets local player max health.

Returns number — Always 200
print("Max HP: " .. ambani.GetMaxHealth())
ambani.GetArmor()
Gets local player armor.

Returns number — Current armor (0–100)
print("Armor: " .. ambani.GetArmor())
ambani.GetPosX() / ambani.GetPosY() / ambani.GetPosZ()
Gets a single coordinate axis for the local player.

Returns number
ambani.GetPos()
Gets all three coordinates at once.

Returns number, number, number — x, y, z
local x, y, z = ambani.GetPos()
print(("Position: %.1f, %.1f, %.1f"):format(x, y, z))
ambani.IsDead()
Checks if local player is dead.

Returns boolean
if ambani.IsDead() then print("You are dead") end
ambani.GetPlayerCount()
Gets the number of players in the session.

Returns number
print("Players: " .. ambani.GetPlayerCount())
ambani.GetVehicleCount()
Gets the number of vehicles in the cache.

Returns number
print("Vehicles: " .. ambani.GetVehicleCount())
General
Miscellaneous session and UI state functions.

ambani.GetAuthKey()
Gets the authenticated username.

Returns string
print("Logged in as: " .. ambani.GetAuthKey())
ambani.GetName()
Alias for ambani.GetAuthKey().

Returns string
print("Name: " .. ambani.GetName())
ambani.GetSelectedPlayer()
Gets the net ID of the player currently selected in the Online Players list.

Returns number — Net ID, or -1 if none selected
local id = ambani.GetSelectedPlayer()
if id ~= -1 then print("Selected: " .. id) end
ambani.GetSelectedVehicle()
Gets the selected vehicle.

Returns number — Always 0 (stub, not yet implemented)
ambani.IsGuiOpen()
Checks if the main Ambani menu (RShift) is currently open.

Returns boolean
if ambani.IsGuiOpen() then print("Menu is open") end
Logger
Control over the internal event logger.

ambani.GetLoggerState()
Gets the current event logger capture state.

Returns number — 1 = enabled, 0 = disabled
print("Logger: " .. ambani.GetLoggerState())
ambani.SetLoggerState(state)
Sets the event logger capture state. Fails if logger is locked.

state number — 1 = enable, 0 = disable
Returns boolean — true if set, false if locked
ambani.SetLoggerState(1) -- enable logging
ambani.LockLogger(state)
Locks the logger so SetLoggerState becomes a no-op. One-way operation.

state number — 1 = lock
Returns boolean — Always true
ambani.LockLogger(1) -- prevent other scripts from changing logger
Lock is Permanent Per Session
Once LockLogger(1) is called, you cannot re-lock from a different state. Use UnlockLogger() first if needed.
ambani.UnlockLogger()
Unlocks the logger so SetLoggerState works again.

Returns boolean — Always true
ambani.UnlockLogger()
ambani.SetLoggerState(0) -- now this works
Notifications
ambani.Notify(title, desc)
Shows a toast notification in the Ambani UI.

title string — Notification title
desc string — Notification description
Returns boolean
ambani.Notify("Hello", "This is a notification!")
Clipboard
ambani.CopyToClipboard(text)
Copies text to the system clipboard.

text string — Text to copy
Returns boolean
ambani.CopyToClipboard("Hello from Ambani!")
ambani.GetClipboard()
Gets the current text from the system clipboard.

Returns string — Clipboard content (max 64KB)
local text = ambani.GetClipboard()
print("Clipboard: " .. text)
Screen
ambani.GetScreenWidth()
Gets the game display width in pixels.

Returns number
print("Width: " .. ambani.GetScreenWidth())
ambani.GetScreenHeight()
Gets the game display height in pixels.

Returns number
print("Height: " .. ambani.GetScreenHeight())
ambani.GetResolution()
Gets both screen dimensions at once.

Returns number, number — width, height
local w, h = ambani.GetResolution()
print("Resolution: " .. w .. "x" .. h)
HTTP
ambani.WebRequest(url)
Performs a synchronous HTTP GET request (blocks until response or error).

url string — Target URL
Returns string|nil — Response body, or nil on error
local resp = ambani.WebRequest("https://httpbin.org/get")
if resp then print("Response: " .. resp) end
ambani.HttpPost(url, body)
Performs a synchronous HTTP POST request (blocks until response or error).

url string — Target URL
body string — Request body (default: "")
Returns string|nil — Response body, or nil on error
local resp = ambani.HttpPost("https://httpbin.org/post", '{"key":"value"}')
if resp then print("Response: " .. resp) end
Single In-Flight Request
WebRequest and HttpPost share the same internal state. Only one HTTP request can be active at a time. Calling one while the other is pending will return nil. Always wrap inside a Citizen.CreateThread to avoid blocking.
Utility
ambani.OpenUrl(url)
Opens a URL in the default system browser.

url string — URL to open
Returns boolean
ambani.OpenUrl("https://google.com")
Resource Injection
Functions for interacting with FiveM resources at runtime.

ambani.InjectResource(resource, code)
Injects and executes Lua code in a specific resource's context. Works on any resource — handles both first-time and repeat injections automatically.

resource string — Resource name
code string — Lua code to execute
Returns boolean — true if injection started or queued, false on error
if ambani.ResourceInjectable("spawnmanager") then
    ambani.InjectResource("spawnmanager", 'print("Hello from spawnmanager!")')
end
ambani.ResourceInjectable(resource)
Checks if a resource exists and is in the Started state.

resource string — Resource name
Returns boolean
if ambani.ResourceInjectable("myresource") then
    print("Resource is running and ready")
end
ambani.ResourceStop(resource)
Stops a running resource.

resource string — Resource name
Returns boolean — true if stopped
ambani.ResourceStop("myresource")
ambani.ResourceStart(resource)
Starts a stopped resource.

resource string — Resource name
Returns boolean — true if started
ambani.ResourceStart("myresource")
ambani.GetResourceList()
Gets all resource names on the server.

Returns table — Array of resource name strings
local resources = ambani.GetResourceList()
for _, name in ipairs(resources) do
    print(name)
end
ambani.GetResourceState(resource)
Gets the current state of a resource.

resource string — Resource name
Returns number
Value	State
0	Uninitialized
1	Stopped
2	Starting
3	Started
4	Stopping
-1	Not found
local state = ambani.GetResourceState("spawnmanager")
if state == 3 then print("Running") end
ambani.GetResourceCount()
Gets the total number of resources on the server.

Returns number
print("Resources: " .. ambani.GetResourceCount())
Graphics / GUI
All GUI functions live under the ambani.Menu* prefix and use a handle-based system.

Window Management
ambani.MenuWindow(px, py, sx, sy)
Creates a simple window.

px, py number — Position (pixels)
sx, sy number — Size (pixels)
Returns number — Window handle
local win = ambani.MenuWindow(100, 100, 300, 400)
ambani.MenuTabbedWindow(name, px, py, sx, sy, tabWidth)
Creates a tabbed window with a side tab bar.

name string — Window title
px, py number — Position
sx, sy number — Size
tabWidth number — Tab bar width (pixels)
Returns number — Window handle
local win = ambani.MenuTabbedWindow("My Menu", 200, 100, 400, 500, 120)
ambani.MenuDestroy(windowHandle)
Destroys a window and all its children.

ambani.MenuDestroy(win)
ambani.MenuSetAccent(windowHandle, r, g, b)
Sets the accent color of a window.

r, g, b number — Color components (0–255)
ambani.MenuSetAccent(win, 0, 150, 255) -- blue accent
ambani.MenuSetKeybind(windowHandle, key)
Sets a toggle keybind for showing/hiding the window.

key number — Virtual key code
ambani.MenuSetKeybind(win, 0x74) -- F5 to toggle
Tabs & Groups
ambani.MenuAddTab(windowHandle, name)
Adds a tab to a tabbed window.

Returns number — Tab handle (used as parent for groups/widgets)
local tab1 = ambani.MenuAddTab(win, "Settings")
local tab2 = ambani.MenuAddTab(win, "Info")
ambani.MenuGroup(parent, name, x, y, ex, ey)
Creates a group container inside a window or tab.

parent number — Window or Tab handle
name string — Group header text
x, y number — Position offset inside parent
ex, ey number — Size
Returns number — Group handle
local grp = ambani.MenuGroup(tab1, "Options", 10, 10, 350, 300)
ambani.MenuSmallText(parent, text)
Adds a small text header to a window or tab.

ambani.MenuSmallText(tab1, "Configure your settings below")
Widgets
ambani.MenuButton(groupHandle, name, callback)
Creates a button. Callback fires on click.

Returns number — Widget handle
ambani.MenuButton(grp, "Click Me", function()
    ambani.Notify("Button", "Clicked!")
end)
ambani.MenuCheckbox(groupHandle, name, onEnable, onDisable)
Creates a checkbox with separate on/off callbacks.

Returns number — Widget handle
ambani.MenuCheckbox(grp, "Feature", function()
    print("Enabled")
end, function()
    print("Disabled")
end)
ambani.MenuSlider(groupHandle, name, default, min, max, unit, precision, callback)
Creates a slider. Callback receives the new value.

unit string — Label shown after value (e.g. "m/s", "%")
precision number — Decimal places (0 = integer)
Returns number — Widget handle
ambani.MenuSlider(grp, "Speed", 50, 0, 100, "%", 0, function(val)
    print("Speed: " .. val)
end)
ambani.MenuText(groupHandle, text)
Creates a static text label.

Returns number — Widget handle
local txt = ambani.MenuText(grp, "Status: OK")
ambani.MenuSetText(widgetHandle, text)
Updates the text of any text widget at runtime.

ambani.MenuSetText(txt, "Status: Error!")
ambani.MenuInputbox(groupHandle, name, placeholder)
Creates a text input field.

Returns number — Widget handle
local input = ambani.MenuInputbox(grp, "Name", "Enter name...")
ambani.MenuGetInputbox(widgetHandle)
Gets the current text from an input box.

Returns string
local text = ambani.MenuGetInputbox(input)
print("Input: " .. text)
ambani.MenuDropDown(groupHandle, name, callback, ...)
Creates a dropdown selector. Callback receives the selected index (1-based).

... string — Item labels
Returns number — Widget handle
ambani.MenuDropDown(grp, "Mode", function(idx)
    print("Selected: " .. idx)
end, "Option A", "Option B", "Option C")
Virtual Key Codes
Common virtual key codes for use with input functions:

Key	Code	Key	Code
A–Z	0x41–0x5A	0–9	0x30–0x39
F1–F12	0x70–0x7B	Enter	0x0D
Escape	0x1B	Space	0x20
Shift	0x10	Ctrl	0x11
Alt	0x12	Tab	0x09
Backspace	0x08	Delete	0x2E
Left Arrow	0x25	Up Arrow	0x26
Right Arrow	0x27	Down Arrow	0x28
Finding Key Codes
Use ambani.OnKeyDown(function(vk) print(vk) end) to discover the virtual key code for any key in real time.
Full Example
A complete script demonstrating a tabbed menu with live player info, action buttons, clipboard utilities, and logger control.

-- Create a tabbed menu
local win = ambani.MenuTabbedWindow("Ambani", 200, 100, 420, 500, 120)
ambani.MenuSetAccent(win, 100, 180, 255)
ambani.MenuSetKeybind(win, 0x74) -- F5

-- Tab 1: Info
local tabInfo = ambani.MenuAddTab(win, "Info")
local grpInfo = ambani.MenuGroup(tabInfo, "Player Info", 10, 10, 280, 250)
local txtHealth  = ambani.MenuText(grpInfo, "Health: --")
local txtPos     = ambani.MenuText(grpInfo, "Position: --")
local txtPlayers = ambani.MenuText(grpInfo, "Players: --")
local txtScreen  = ambani.MenuText(grpInfo, "Screen: --")

Citizen.CreateThread(function()
    while true do
        ambani.MenuSetText(txtHealth, ("Health: %.0f / %.0f"):format(
            ambani.GetHealth(), ambani.GetMaxHealth()
        ))
        local x, y, z = ambani.GetPos()
        ambani.MenuSetText(txtPos, ("Pos: %.1f, %.1f, %.1f"):format(x, y, z))
        ambani.MenuSetText(txtPlayers, "Players: " .. ambani.GetPlayerCount())
        local sw, sh = ambani.GetResolution()
        ambani.MenuSetText(txtScreen, "Screen: " .. sw .. "x" .. sh)
        Citizen.Wait(500)
    end
end)

-- Tab 2: Actions
local tabAct = ambani.MenuAddTab(win, "Actions")
local grpAct = ambani.MenuGroup(tabAct, "Quick Actions", 10, 10, 280, 300)

ambani.MenuButton(grpAct, "Copy Position", function()
    local x, y, z = ambani.GetPos()
    ambani.CopyToClipboard(("%.2f, %.2f, %.2f"):format(x, y, z))
    ambani.Notify("Clipboard", "Position copied!")
end)

ambani.MenuButton(grpAct, "Open Google", function()
    ambani.OpenUrl("https://google.com")
end)

ambani.MenuButton(grpAct, "Test HTTP POST", function()
    Citizen.CreateThread(function()
        local resp = ambani.HttpPost("https://httpbin.org/post", "hello=world")
        if resp then
            ambani.Notify("POST", "Response received! (" .. #resp .. " bytes)")
        else
            ambani.Notify("POST", "Request failed!")
        end
    end)
end)

ambani.MenuButton(grpAct, "Show Clipboard", function()
    local text = ambani.GetClipboard()
    ambani.Notify("Clipboard", text ~= "" and text or "(empty)")
end)

ambani.MenuCheckbox(grpAct, "Event Logger", function()
    ambani.SetLoggerState(1)
    ambani.Notify("Logger", "Enabled")
end, function()
    ambani.SetLoggerState(0)
    ambani.Notify("Logger", "Disabled")
end)

ambani.Notify("Script", "Loaded! Press F5 to toggle menu.")
print("[Ambani] Script loaded. User: " .. ambani.GetName())