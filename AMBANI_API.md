# Ambani Executor — Lua API Reference

## Window Management

### `ambani.MenuWindow(px, py, sx, sy)`
Creates a simple window.
- `px, py` — Position (pixels)
- `sx, sy` — Size (pixels)
- Returns: `number` — Window handle

```lua
local win = ambani.MenuWindow(100, 100, 300, 400)
```

### `ambani.MenuTabbedWindow(name, px, py, sx, sy, tabWidth)`
Creates a tabbed window with a side tab bar.
- `name` — Window title
- `px, py` — Position
- `sx, sy` — Size
- `tabWidth` — Tab bar width (pixels)
- Returns: `number` — Window handle

```lua
local win = ambani.MenuTabbedWindow("My Menu", 200, 100, 400, 500, 120)
```

### `ambani.MenuDestroy(windowHandle)`
Destroys a window and all its children.

```lua
ambani.MenuDestroy(win)
```

### `ambani.MenuSetAccent(windowHandle, r, g, b)`
Sets the accent color of a window.
- `r, g, b` — Color components (0–255)

```lua
ambani.MenuSetAccent(win, 0, 150, 255) -- blue accent
```

### `ambani.MenuSetKeybind(windowHandle, key)`
Sets a toggle keybind for showing/hiding the window.
- `key` — Virtual key code

```lua
ambani.MenuSetKeybind(win, 0x74) -- F5 to toggle
```

---

## Tabs & Groups

### `ambani.MenuAddTab(windowHandle, name)`
Adds a tab to a tabbed window.
- Returns: `number` — Tab handle (used as parent for groups/widgets)

```lua
local tab1 = ambani.MenuAddTab(win, "Settings")
local tab2 = ambani.MenuAddTab(win, "Info")
```

### `ambani.MenuGroup(parent, name, x, y, ex, ey)`
Creates a group container inside a window or tab.
- `parent` — Window or Tab handle
- `name` — Group header text
- `x, y` — Position offset inside parent
- `ex, ey` — Size
- Returns: `number` — Group handle

```lua
local grp = ambani.MenuGroup(tab1, "Options", 10, 10, 350, 300)
```

### `ambani.MenuSmallText(parent, text)`
Adds a small text header to a window or tab.

```lua
ambani.MenuSmallText(tab1, "Configure your settings below")
```

---

## Widgets

### `ambani.MenuButton(groupHandle, name, callback)`
Creates a button. Callback fires on click.
- Returns: `number` — Widget handle

```lua
ambani.MenuButton(grp, "Click Me", function()
    ambani.Notify("Button", "Clicked!")
end)
```

### `ambani.MenuCheckbox(groupHandle, name, onEnable, onDisable)`
Creates a checkbox with separate on/off callbacks.
- Returns: `number` — Widget handle

```lua
ambani.MenuCheckbox(grp, "Feature", function()
    print("Enabled")
end, function()
    print("Disabled")
end)
```

### `ambani.MenuSlider(groupHandle, name, default, min, max, unit, precision, callback)`
Creates a slider. Callback receives the new value.
- `unit` — Label shown after value (e.g. `"m/s"`, `"%"`)
- `precision` — Decimal places (`0` = integer)
- Returns: `number` — Widget handle

```lua
ambani.MenuSlider(grp, "Speed", 50, 0, 100, "%", 0, function(val)
    print("Speed: " .. val)
end)
```

### `ambani.MenuText(groupHandle, text)`
Creates a static text label.
- Returns: `number` — Widget handle

```lua
local txt = ambani.MenuText(grp, "Status: OK")
```

### `ambani.MenuSetText(widgetHandle, text)`
Updates the text of any text widget at runtime.

```lua
ambani.MenuSetText(txt, "Status: Error!")
```

### `ambani.MenuInputbox(groupHandle, name, placeholder)`
Creates a text input field.
- Returns: `number` — Widget handle

```lua
local input = ambani.MenuInputbox(grp, "Name", "Enter name...")
```

### `ambani.MenuGetInputbox(widgetHandle)`
Gets the current text from an input box.
- Returns: `string`

```lua
local text = ambani.MenuGetInputbox(input)
print("Input: " .. text)
```

### `ambani.MenuDropDown(groupHandle, name, callback, ...)`
Creates a dropdown selector. Callback receives the selected index (1-based).
- `...` — Item labels
- Returns: `number` — Widget handle

```lua
ambani.MenuDropDown(grp, "Mode", function(idx)
    print("Selected: " .. idx)
end, "Option A", "Option B", "Option C")
```

---

## Notifications & UI State

### `ambani.Notify(title, description)`
Shows a notification on screen.

```lua
ambani.Notify("RED-SHADOW", "Action completed")
```

### `ambani.IsGuiOpen()`
Returns `true` if the menu is currently visible.

```lua
if ambani.IsGuiOpen() then
    -- update live widgets
end
```

---

## Player / World Info

### `ambani.GetName()`
Returns the local player's name as `string`.

### `ambani.GetHealth()`
Returns the local player's health as `number`.

### `ambani.GetPos()`
Returns `x, y, z` position of the local player.

```lua
local x, y, z = ambani.GetPos()
```

### `ambani.GetPlayerCount()`
Returns the number of players on the server as `number`.

### `ambani.GetResourceCount()`
Returns the total number of resources loaded as `number`.

---

## Resource Management

### `ambani.GetResourceList()`
Returns a table of all resource names on the server.

```lua
for _, name in ipairs(ambani.GetResourceList()) do
    print(name)
end
```

### `ambani.GetResourceState(name)`
Returns the state of a resource as `number`.
- `3` = running

```lua
if ambani.GetResourceState("screenshot-basic") == 3 then
    -- resource is running
end
```

### `ambani.ResourceStop(name)`
Stops a resource. Note: triggers `onResourceStop` event (detectable).
Use `DestroyResource(name)` instead when possible — it bypasses the event.

```lua
ambani.ResourceStop("screenshot-basic")
-- or (preferred, bypasses onResourceStop):
DestroyResource("screenshot-basic")
```

---

## Input / Key Events

### `ambani.OnKeyUp(callback)`
Fires when a key is released.
- Callback receives `vk` — virtual key code

```lua
ambani.OnKeyUp(function(vk)
    print("Key released: " .. vk)
end)
```

---

## Threads

`Citizen.CreateThread` and `Citizen.Wait` work normally inside Ambani.

```lua
Citizen.CreateThread(function()
    while true do
        Citizen.Wait(500)
        -- runs every 500ms
    end
end)
```

---

## Virtual Key Codes

| Key       | Code   | Key       | Code   |
|-----------|--------|-----------|--------|
| A–Z       | 0x41–0x5A | 0–9    | 0x30–0x39 |
| F1–F12    | 0x70–0x7B | Enter  | 0x0D  |
| Escape    | 0x1B   | Space     | 0x20  |
| Shift     | 0x10   | Ctrl      | 0x11  |
| Alt       | 0x12   | Tab       | 0x09  |
| Backspace | 0x08   | Delete    | 0x2E  |
| Left      | 0x25   | Up        | 0x26  |
| Right     | 0x27   | Down      | 0x28  |
| F5        | 0x74   | F6        | 0x75  |

---

## Notes

- All GUI functions use a **handle-based system** — always store the return value
- `MenuGroup` positions are relative to the parent tab/window
- `MenuText` slots initialized as `""` will appear invisible — init with `"-"` or a placeholder if you need the group to be visible immediately
- `DestroyResource` is preferred over `ambani.ResourceStop` — it bypasses `onResourceStop` event handlers on the server
- `ambani.IsGuiOpen()` should gate live-update threads to avoid unnecessary work
