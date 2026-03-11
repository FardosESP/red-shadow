"""
Lua Script Generator
Automated Lua exploit script generation for Ambani API
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LuaScriptGenerator:
    """
    Automated Lua exploit script generation for Ambani API
    
    Responsibilities:
    - Generate exploit scripts from vulnerability data (Task 12.2)
    - Create proof-of-concept scripts (Task 12.3)
    - Add rate limiting to scripts (Task 12.4)
    - Add cleanup code (Task 12.5)
    - Generate interactive REPL scripts (Task 12.6)
    - Implement logging in scripts (Task 12.7)
    - Add error handling and safe mode (Task 12.8)
    - Create script obfuscation (Task 12.9)
    - Implement Ambani API wrappers (Task 12.10)
    """
    
    def __init__(self, safe_mode: bool = True, obfuscate: bool = False):
        """
        Initialize the Lua Script Generator
        
        Args:
            safe_mode: Enable safe mode checks in generated scripts
            obfuscate: Enable script obfuscation for stealth
        """
        self.logger = get_logger(__name__)
        self.safe_mode = safe_mode
        self.obfuscate = obfuscate
        
        # Ambani API methods
        self.ambani_methods = {
            # Event/Native methods
            'TriggerServerEvent': 'Trigger server-side event',
            'TriggerClientEvent': 'Trigger client-side event',
            'InvokeNative': 'Call native function',
            'CallCallback': 'Call server callback',
            'InvokeExport': 'Call resource export',
            # NUI methods
            'SendNUIMessage': 'Send message to NUI (GUI)',
            'SetNuiFocus': 'Set NUI focus and cursor',
            'RegisterNUICallback': 'Register NUI callback',
            'CreateDui': 'Create DUI (web browser)',
            'GetDuiHandle': 'Get DUI texture handle',
            # Ambani Menu/GUI methods
            'MenuWindow': 'Create simple window',
            'MenuTabbedWindow': 'Create tabbed window',
            'MenuDestroy': 'Destroy window',
            'MenuSetAccent': 'Set window accent color',
            'MenuSetKeybind': 'Set window toggle keybind',
            'MenuAddTab': 'Add tab to window',
            'MenuGroup': 'Create group container',
            'MenuSmallText': 'Add small text header',
            'MenuButton': 'Create button widget',
            'MenuCheckbox': 'Create checkbox widget',
            'MenuSlider': 'Create slider widget',
            'MenuText': 'Create text label',
            'MenuSetText': 'Update text widget',
            'MenuInputbox': 'Create input field',
            'MenuGetInputbox': 'Get input field text',
            'MenuDropDown': 'Create dropdown selector',
            'OnKeyDown': 'Register key down callback',
            'Notify': 'Show notification'
        }
        
        # Virtual key codes for keybinds
        self.virtual_keys = {
            'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
            'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
            'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
            'Enter': 0x0D, 'Escape': 0x1B, 'Space': 0x20,
            'Shift': 0x10, 'Ctrl': 0x11, 'Alt': 0x12,
            'Tab': 0x09, 'Backspace': 0x08, 'Delete': 0x2E,
            'Left': 0x25, 'Up': 0x26, 'Right': 0x27, 'Down': 0x28
        }
        
        self.logger.info("LuaScriptGenerator initialized: safe_mode=%s, obfuscate=%s",
                        safe_mode, obfuscate)
    
    def generate_exploit_script(self, exploit: Dict) -> str:
        """
        Generate Lua script to exploit vulnerability (Task 12.2)
        
        Args:
            exploit: Exploit vector data with keys:
                - event_name: Name of the event to trigger
                - method: Ambani API method to use
                - parameters: List of parameters
                - description: Description of the exploit
                - risk_score: Risk score (0.0 to 1.0)
                
        Returns:
            Lua script code
        """
        event_name = exploit.get('event_name', 'unknown_event')
        method = exploit.get('method', 'TriggerServerEvent')
        parameters = exploit.get('parameters', [])
        description = exploit.get('description', 'No description')
        risk_score = exploit.get('risk_score', 0.5)
        
        script = f"""-- Exploit: {event_name}
-- Description: {description}
-- Risk Score: {risk_score:.2f}
-- Generated: {datetime.now().isoformat()}
-- Method: Ambani.{method}

"""
        
        # Add safe mode check
        if self.safe_mode:
            script += self._generate_safe_mode_check()
        
        # Add logging
        script += self._generate_logging_setup()
        
        # Generate exploit code
        script += f"""
-- Exploit execution
local function executeExploit()
    Log("INFO", "Executing exploit: {event_name}")
    
    -- Prepare parameters
    local params = {{"""
        
        for i, param in enumerate(parameters):
            param_value = self._format_parameter(param)
            script += f"\n        {param_value},"
        
        script += """
    }
    
    -- Execute via Ambani API
"""
        
        if method == 'TriggerServerEvent':
            script += f"""    Ambani.TriggerServerEvent("{event_name}", table.unpack(params))
    Log("SUCCESS", "Event triggered: {event_name}")
"""
        elif method == 'TriggerClientEvent':
            script += f"""    Ambani.TriggerClientEvent("{event_name}", -1, table.unpack(params))
    Log("SUCCESS", "Client event triggered: {event_name}")
"""
        elif method == 'InvokeNative':
            native_hash = exploit.get('native_hash', '0x0')
            script += f"""    Ambani.InvokeNative("{native_hash}", table.unpack(params))
    Log("SUCCESS", "Native invoked: {native_hash}")
"""
        elif method == 'CallCallback':
            script += f"""    Ambani.CallCallback("{event_name}", params, function(result)
        Log("SUCCESS", "Callback result: " .. tostring(result))
    end)
"""
        elif method == 'InvokeExport':
            resource = exploit.get('resource', 'unknown')
            export_name = exploit.get('export_name', event_name)
            script += f"""    Ambani.InvokeExport("{resource}", "{export_name}", table.unpack(params))
    Log("SUCCESS", "Export invoked: {resource}.{export_name}")
"""
        
        script += """end

-- Execute
local success, error = pcall(executeExploit)
if not success then
    Log("ERROR", "Exploit failed: " .. tostring(error))
end
"""
        
        return script
    
    def generate_poc_script(self, exploits: List[Dict], title: str = "PoC Script") -> str:
        """
        Generate complete proof-of-concept script (Task 12.3)
        
        Args:
            exploits: List of exploit vectors
            title: Title for the PoC script
            
        Returns:
            Complete PoC Lua script
        """
        script = f"""-- {title}
-- Generated: {datetime.now().isoformat()}
-- Exploits: {len(exploits)}
-- Ambani API Integration

"""
        
        # Add header
        script += self._generate_header()
        
        # Add safe mode check
        if self.safe_mode:
            script += self._generate_safe_mode_check()
        
        # Add logging setup
        script += self._generate_logging_setup()
        
        # Add Ambani API wrapper
        script += self._generate_ambani_wrapper()
        
        # Add utility functions
        script += self._generate_utility_functions()
        
        # Add each exploit
        script += "\n-- Exploit Functions\n"
        for i, exploit in enumerate(exploits):
            script += self._generate_exploit_function(exploit, i + 1)
        
        # Add main execution
        script += self._generate_main_execution(len(exploits))
        
        # Add cleanup
        script += self._generate_cleanup_code()
        
        return script
    
    def generate_repl_script(self, exploits: Optional[List[Dict]] = None) -> str:
        """
        Generate interactive REPL script (Task 12.6)
        
        Args:
            exploits: Optional list of exploits to include
            
        Returns:
            REPL Lua script
        """
        script = """-- Interactive REPL Script
-- Ambani API Integration
-- Generated: """ + datetime.now().isoformat() + """

"""
        
        # Add logging
        script += self._generate_logging_setup()
        
        # Add Ambani wrapper
        script += self._generate_ambani_wrapper()
        
        # Add REPL commands
        script += """
-- REPL Commands
local commands = {
    help = function()
        print("Available commands:")
        print("  help - Show this help")
        print("  list - List available exploits")
        print("  run <id> - Run exploit by ID")
        print("  trigger <event> <params...> - Trigger custom event")
        print("  native <hash> <params...> - Invoke native")
        print("  export <resource> <export> <params...> - Call export")
        print("  exit - Exit REPL")
    end,
    
    list = function()
        print("Available exploits:")
"""
        
        if exploits:
            for i, exploit in enumerate(exploits):
                event_name = exploit.get('event_name', 'unknown')
                description = exploit.get('description', 'No description')
                script += f"""        print("  [{i+1}] {event_name} - {description}")
"""
        else:
            script += """        print("  No exploits loaded")
"""
        
        script += """    end,
    
    run = function(id)
        local exploit_id = tonumber(id)
        if not exploit_id then
            print("Error: Invalid exploit ID")
            return
        end
        
        print("Running exploit " .. exploit_id .. "...")
        -- Execute exploit
        ExecuteExploit(exploit_id)
    end,
    
    trigger = function(...)
        local args = {...}
        if #args < 1 then
            print("Usage: trigger <event> <params...>")
            return
        end
        
        local event = args[1]
        local params = {}
        for i = 2, #args do
            table.insert(params, args[i])
        end
        
        print("Triggering event: " .. event)
        Ambani.TriggerServerEvent(event, table.unpack(params))
    end,
    
    native = function(...)
        local args = {...}
        if #args < 1 then
            print("Usage: native <hash> <params...>")
            return
        end
        
        local hash = args[1]
        local params = {}
        for i = 2, #args do
            table.insert(params, args[i])
        end
        
        print("Invoking native: " .. hash)
        Ambani.InvokeNative(hash, table.unpack(params))
    end,
    
    export = function(...)
        local args = {...}
        if #args < 2 then
            print("Usage: export <resource> <export> <params...>")
            return
        end
        
        local resource = args[1]
        local export_name = args[2]
        local params = {}
        for i = 3, #args do
            table.insert(params, args[i])
        end
        
        print("Calling export: " .. resource .. "." .. export_name)
        Ambani.InvokeExport(resource, export_name, table.unpack(params))
    end,
    
    exit = function()
        print("Exiting REPL...")
        os.exit(0)
    end
}

-- REPL Loop
print("Ambani REPL - Type 'help' for commands")
while true do
    io.write("> ")
    local input = io.read()
    
    if not input then
        break
    end
    
    local parts = {}
    for part in input:gmatch("%S+") do
        table.insert(parts, part)
    end
    
    if #parts > 0 then
        local cmd = parts[1]
        local args = {}
        for i = 2, #parts do
            table.insert(args, parts[i])
        end
        
        if commands[cmd] then
            commands[cmd](table.unpack(args))
        else
            print("Unknown command: " .. cmd)
        end
    end
end
"""
        
        return script
    
    def add_rate_limiting(self, script: str, rate: int = 10) -> str:
        """
        Add rate limiting to script (Task 12.4)
        
        Args:
            script: Original script
            rate: Maximum events per second
            
        Returns:
            Script with rate limiting
        """
        rate_limit_code = f"""
-- Rate Limiting ({rate} events/second)
local rateLimiter = {{
    lastExecution = 0,
    minInterval = {1000 / rate}, -- milliseconds
    
    canExecute = function(self)
        local now = GetGameTimer()
        if now - self.lastExecution >= self.minInterval then
            self.lastExecution = now
            return true
        end
        return false
    end
}}

-- Wrap execution with rate limiting
local originalExecute = executeExploit
executeExploit = function()
    if rateLimiter:canExecute() then
        originalExecute()
    else
        Log("WARN", "Rate limit exceeded, skipping execution")
    end
end

"""
        
        # Insert rate limiting before execution
        if "-- Execute" in script:
            script = script.replace("-- Execute", rate_limit_code + "-- Execute")
        else:
            script = rate_limit_code + script
        
        return script
    
    def add_cleanup(self, script: str) -> str:
        """
        Add cleanup code to script (Task 12.5)
        
        Args:
            script: Original script
            
        Returns:
            Script with cleanup code
        """
        cleanup_code = self._generate_cleanup_code()
        
        # Append cleanup at the end
        script += "\n" + cleanup_code
        
        return script
    
    def add_logging(self, script: str) -> str:
        """
        Add logging to script (Task 12.7)
        
        Args:
            script: Original script
            
        Returns:
            Script with logging
        """
        if "-- Logging Setup" not in script:
            logging_code = self._generate_logging_setup()
            # Insert at the beginning
            script = logging_code + "\n" + script
        
        return script
    
    def add_error_handling(self, script: str) -> str:
        """
        Add error handling and safe mode checks (Task 12.8)
        
        Args:
            script: Original script
            
        Returns:
            Script with error handling
        """
        if self.safe_mode and "-- Safe Mode Check" not in script:
            safe_mode_code = self._generate_safe_mode_check()
            script = safe_mode_code + "\n" + script
        
        # Wrap main execution in pcall if not already wrapped
        if "pcall(executeExploit)" not in script and "executeExploit()" in script:
            script = script.replace(
                "executeExploit()",
                """local success, error = pcall(executeExploit)
if not success then
    Log("ERROR", "Execution failed: " .. tostring(error))
end"""
            )
        
        return script
    
    def obfuscate_script(self, script: str) -> str:
        """
        Obfuscate script for stealth (Task 12.9)
        
        Args:
            script: Original script
            
        Returns:
            Obfuscated script
        """
        if not self.obfuscate:
            return script
        
        # Simple obfuscation techniques
        # 1. Remove comments
        lines = script.split('\n')
        obfuscated_lines = []
        for line in lines:
            # Remove full-line comments
            if line.strip().startswith('--'):
                continue
            # Remove inline comments
            if '--' in line:
                line = line.split('--')[0]
            if line.strip():
                obfuscated_lines.append(line)
        
        obfuscated = '\n'.join(obfuscated_lines)
        
        # 2. Minify (remove extra whitespace)
        obfuscated = '\n'.join(line.strip() for line in obfuscated.split('\n') if line.strip())
        
        # 3. Add obfuscation wrapper
        obfuscated = f"""local _=loadstring;_([[{obfuscated}]])()"""
        
        return obfuscated
    
    # Helper methods
    
    def _generate_header(self) -> str:
        """Generate script header"""
        return """-- Ambani API Integration
-- WARNING: For authorized security testing only

"""
    
    def _generate_safe_mode_check(self) -> str:
        """Generate safe mode check code"""
        return """-- Safe Mode Check
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

"""
    
    def _generate_logging_setup(self) -> str:
        """Generate logging setup code"""
        return """-- Logging Setup
local function Log(level, message)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    print(string.format("[%s] [%s] %s", timestamp, level, message))
end

"""
    
    def _generate_ambani_wrapper(self) -> str:
        """Generate Ambani API wrapper (Task 12.10)"""
        return """-- Ambani API Wrapper
Ambani = Ambani or {}

-- Wrapper functions with error handling
function Ambani.TriggerServerEvent(eventName, ...)
    local success, error = pcall(function()
        -- Call actual Ambani API
        TriggerServerEvent(eventName, ...)
    end)
    if not success then
        Log("ERROR", "TriggerServerEvent failed: " .. tostring(error))
    end
    return success
end

function Ambani.TriggerClientEvent(eventName, target, ...)
    local success, error = pcall(function()
        TriggerClientEvent(eventName, target, ...)
    end)
    if not success then
        Log("ERROR", "TriggerClientEvent failed: " .. tostring(error))
    end
    return success
end

function Ambani.InvokeNative(hash, ...)
    local success, result = pcall(function()
        return Citizen.InvokeNative(hash, ...)
    end)
    if not success then
        Log("ERROR", "InvokeNative failed: " .. tostring(result))
        return nil
    end
    return result
end

function Ambani.CallCallback(eventName, data, callback)
    local success, error = pcall(function()
        TriggerServerEvent(eventName, data)
        if callback then
            callback(true)
        end
    end)
    if not success then
        Log("ERROR", "CallCallback failed: " .. tostring(error))
        if callback then
            callback(false)
        end
    end
end

function Ambani.InvokeExport(resource, exportName, ...)
    local success, result = pcall(function()
        return exports[resource][exportName](...)
    end)
    if not success then
        Log("ERROR", "InvokeExport failed: " .. tostring(result))
        return nil
    end
    return result
end

-- NUI/GUI Functions
function Ambani.SendNUIMessage(data)
    local success, error = pcall(function()
        SendNUIMessage(data)
    end)
    if not success then
        Log("ERROR", "SendNUIMessage failed: " .. tostring(error))
    end
    return success
end

function Ambani.SetNuiFocus(hasFocus, hasCursor)
    local success, error = pcall(function()
        SetNuiFocus(hasFocus, hasCursor)
    end)
    if not success then
        Log("ERROR", "SetNuiFocus failed: " .. tostring(error))
    end
    return success
end

function Ambani.RegisterNUICallback(callbackName, callback)
    local success, error = pcall(function()
        RegisterNUICallback(callbackName, callback)
    end)
    if not success then
        Log("ERROR", "RegisterNUICallback failed: " .. tostring(error))
    end
    return success
end

function Ambani.CreateDui(url, width, height)
    local success, result = pcall(function()
        return CreateDui(url, width, height)
    end)
    if not success then
        Log("ERROR", "CreateDui failed: " .. tostring(result))
        return nil
    end
    return result
end

function Ambani.GetDuiHandle(duiObject)
    local success, result = pcall(function()
        return GetDuiHandle(duiObject)
    end)
    if not success then
        Log("ERROR", "GetDuiHandle failed: " .. tostring(result))
        return nil
    end
    return result
end

"""
    
    def _generate_utility_functions(self) -> str:
        """Generate utility functions"""
        return """-- Utility Functions
local function Sleep(ms)
    Citizen.Wait(ms)
end

local function GetPlayerCoords()
    return GetEntityCoords(PlayerPedId())
end

local function GetPlayerId()
    return PlayerId()
end

"""
    
    def _generate_exploit_function(self, exploit: Dict, index: int) -> str:
        """Generate individual exploit function"""
        event_name = exploit.get('event_name', f'exploit_{index}')
        description = exploit.get('description', 'No description')
        
        return f"""
-- Exploit {index}: {event_name}
-- {description}
local function Exploit{index}()
    Log("INFO", "Executing exploit {index}: {event_name}")
    {self._generate_exploit_body(exploit)}
end

"""
    
    def _generate_exploit_body(self, exploit: Dict) -> str:
        """Generate exploit body code"""
        method = exploit.get('method', 'TriggerServerEvent')
        event_name = exploit.get('event_name', 'unknown')
        parameters = exploit.get('parameters', [])
        
        params_str = ', '.join(self._format_parameter(p) for p in parameters)
        
        if method == 'TriggerServerEvent':
            return f'Ambani.TriggerServerEvent("{event_name}", {params_str})'
        elif method == 'TriggerClientEvent':
            return f'Ambani.TriggerClientEvent("{event_name}", -1, {params_str})'
        elif method == 'InvokeNative':
            native_hash = exploit.get('native_hash', '0x0')
            return f'Ambani.InvokeNative("{native_hash}", {params_str})'
        elif method == 'CallCallback':
            return f'Ambani.CallCallback("{event_name}", {{{params_str}}})'
        elif method == 'InvokeExport':
            resource = exploit.get('resource', 'unknown')
            export_name = exploit.get('export_name', event_name)
            return f'Ambani.InvokeExport("{resource}", "{export_name}", {params_str})'
        
        return f'-- Unknown method: {method}'
    
    def generate_gui_script(self, title: str = "Ambani Menu", 
                           exploits: Optional[List[Dict]] = None,
                           keybind: str = 'F5') -> str:
        """
        Generate script with Ambani GUI menu
        
        Args:
            title: Menu window title
            exploits: List of exploits to add as buttons
            keybind: Key to toggle menu (default F5)
            
        Returns:
            Lua script with GUI
        """
        key_code = self.virtual_keys.get(keybind, 0x74)  # Default F5
        
        script = f"""-- {title}
-- Ambani GUI Menu
-- Generated: {datetime.now().isoformat()}
-- Toggle Key: {keybind}

"""
        
        # Add logging
        script += self._generate_logging_setup()
        
        # Add Ambani wrapper with GUI functions
        script += self._generate_ambani_gui_wrapper()
        
        # Create main window
        script += f"""
-- Create Main Window
local mainWindow = ambani.MenuTabbedWindow("{title}", 200, 100, 500, 600, 120)
ambani.MenuSetAccent(mainWindow, 0, 150, 255) -- Blue accent
ambani.MenuSetKeybind(mainWindow, {key_code}) -- {keybind} to toggle

Log("INFO", "Menu created - Press {keybind} to toggle")

"""
        
        # Add tabs
        if exploits and len(exploits) > 0:
            script += """-- Create Tabs
local exploitsTab = ambani.MenuAddTab(mainWindow, "Exploits")
local settingsTab = ambani.MenuAddTab(mainWindow, "Settings")
local infoTab = ambani.MenuAddTab(mainWindow, "Info")

"""
            
            # Add exploits group
            script += """-- Exploits Group
local exploitsGroup = ambani.MenuGroup(exploitsTab, "Available Exploits", 10, 10, 460, 500)

"""
            
            # Add exploit buttons
            for i, exploit in enumerate(exploits):
                event_name = exploit.get('event_name', f'exploit_{i+1}')
                description = exploit.get('description', 'No description')
                
                script += f"""-- Exploit {i+1}: {event_name}
ambani.MenuButton(exploitsGroup, "{event_name}", function()
    Log("INFO", "Executing: {event_name}")
    {self._generate_exploit_body(exploit)}
    ambani.Notify("Exploit", "{event_name} executed!")
end)

"""
            
            # Add settings
            script += """-- Settings Group
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

"""
            
            # Add info tab
            script += f"""-- Info Group
local infoGroup = ambani.MenuGroup(infoTab, "Information", 10, 10, 460, 500)

ambani.MenuSmallText(infoTab, "Ambani Integration")
ambani.MenuText(infoGroup, "Version: 1.0.0")
ambani.MenuText(infoGroup, "Exploits: {len(exploits)}")
ambani.MenuText(infoGroup, "Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
ambani.MenuText(infoGroup, "")
ambani.MenuText(infoGroup, "Press {keybind} to toggle menu")
ambani.MenuText(infoGroup, "")
ambani.MenuText(infoGroup, "WARNING: For authorized testing only")

"""
        
        # Add cleanup
        script += """
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
"""
        
        return script
    
    def generate_interactive_gui_script(self, title: str = "Interactive Menu") -> str:
        """
        Generate interactive GUI script with all widget types
        
        Args:
            title: Menu title
            
        Returns:
            Interactive GUI Lua script
        """
        script = f"""-- {title}
-- Interactive Ambani GUI Demo
-- Generated: {datetime.now().isoformat()}

"""
        
        script += self._generate_logging_setup()
        script += self._generate_ambani_gui_wrapper()
        
        script += f"""
-- Create Interactive Window
local window = ambani.MenuTabbedWindow("{title}", 150, 100, 600, 700, 140)
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
    local weathers = {"CLEAR", "EXTRASUNNY", "CLOUDS", "OVERCAST", "RAIN", "THUNDER", "SNOW", "BLIZZARD", "FOGGY"}
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
"""
        
        return script
    
    def generate_event_capture_script(self, output_file: str = "captured_events.json") -> str:
        """
        Generate script to capture all server events in real-time
        
        Args:
            output_file: File to save captured events
            
        Returns:
            Event capture Lua script
        """
        script = f"""-- Event Capture Script
-- Monitors and logs all server events in real-time
-- Generated: {datetime.now().isoformat()}

"""
        
        script += self._generate_logging_setup()
        
        script += f"""
-- Event Capture System
local capturedEvents = {{}}
local eventStats = {{}}
local captureEnabled = true
local maxEvents = 1000  -- Limit to prevent memory issues

-- Reward detection keywords
local moneyKeywords = {{"money", "cash", "bank", "salary", "payment", "pay", "reward", "earn"}}
local itemKeywords = {{"item", "inventory", "give", "add", "receive", "loot"}}
local xpKeywords = {{"xp", "exp", "experience", "level", "rank", "skill"}}

-- Job event patterns (legitimate farming opportunities)
local jobPatterns = {{
    "job:", "work:", "mission:", "delivery:", "taxi:",
    "mechanic:", "police:", "ems:", "trucker:", "miner:",
    "farmer:", "fisher:", "lumberjack:", "garbage:",
    "postop:", "courier:", "bus:", "pilot:"
}}

-- Detect reward type
local function DetectRewardType(eventName, params)
    local eventLower = string.lower(eventName)
    
    -- Check for money
    for _, keyword in ipairs(moneyKeywords) do
        if string.find(eventLower, keyword) then
            -- Try to find amount in parameters
            for _, param in ipairs(params) do
                if type(param) == "number" and param > 0 then
                    return "money", param
                end
            end
            return "money", nil
        end
    end
    
    -- Check for items
    for _, keyword in ipairs(itemKeywords) do
        if string.find(eventLower, keyword) then
            for _, param in ipairs(params) do
                if type(param) == "number" and param > 0 then
                    return "item", param
                end
            end
            return "item", nil
        end
    end
    
    -- Check for XP
    for _, keyword in ipairs(xpKeywords) do
        if string.find(eventLower, keyword) then
            for _, param in ipairs(params) do
                if type(param) == "number" and param > 0 then
                    return "xp", param
                end
            end
            return "xp", nil
        end
    end
    
    return nil, nil
end

-- Check if event is a job event
local function IsJobEvent(eventName)
    local eventLower = string.lower(eventName)
    for _, pattern in ipairs(jobPatterns) do
        if string.find(eventLower, pattern) then
            return true
        end
    end
    return false
end

-- Capture event
local function CaptureEvent(eventName, ...)
    if not captureEnabled then
        return
    end
    
    if #capturedEvents >= maxEvents then
        Log("WARN", "Max events reached, stopping capture")
        captureEnabled = false
        return
    end
    
    local params = {{...}}
    local rewardType, rewardAmount = DetectRewardType(eventName, params)
    local isJob = IsJobEvent(eventName)
    
    local event = {{
        name = eventName,
        params = params,
        timestamp = os.date("%Y-%m-%d %H:%M:%S"),
        rewardType = rewardType,
        rewardAmount = rewardAmount,
        isJob = isJob
    }}
    
    table.insert(capturedEvents, event)
    
    -- Update statistics
    if not eventStats[eventName] then
        eventStats[eventName] = {{
            count = 0,
            totalReward = 0,
            isJob = isJob
        }}
    end
    
    eventStats[eventName].count = eventStats[eventName].count + 1
    if rewardAmount then
        eventStats[eventName].totalReward = eventStats[eventName].totalReward + rewardAmount
    end
    
    -- Log interesting events
    if rewardAmount and rewardAmount > 0 then
        Log("CAPTURE", string.format("%s: %s = %.2f", eventName, rewardType, rewardAmount))
    end
end

-- Hook into all events (this is a simplified version)
-- In practice, you'd need to hook specific events you're interested in
local function HookEvent(eventName)
    AddEventHandler(eventName, function(...)
        CaptureEvent(eventName, ...)
    end)
end

-- Common events to monitor (add more as needed)
local eventsToMonitor = {{
    -- Job events
    "job:completed", "job:payment", "job:reward",
    "work:finish", "work:salary",
    "mission:complete", "mission:reward",
    
    -- Money events
    "bank:deposit", "bank:withdraw", "bank:transfer",
    "money:add", "money:remove", "money:set",
    "cash:add", "cash:remove",
    "salary:receive", "payment:receive",
    
    -- Item events
    "inventory:addItem", "inventory:removeItem",
    "item:give", "item:receive",
    
    -- XP events
    "xp:add", "xp:gain",
    "level:up", "skill:increase"
}}

-- Register event handlers
for _, eventName in ipairs(eventsToMonitor) do
    HookEvent(eventName)
    Log("INFO", "Monitoring: " .. eventName)
end

-- Statistics display
Citizen.CreateThread(function()
    while true do
        Citizen.Wait(30000)  -- Every 30 seconds
        
        if #capturedEvents > 0 then
            Log("STATS", string.format("Captured %d events (%d unique)", 
                #capturedEvents, #eventStats))
            
            -- Show top events
            local sortedEvents = {{}}
            for name, stats in pairs(eventStats) do
                table.insert(sortedEvents, {{name = name, stats = stats}})
            end
            
            table.sort(sortedEvents, function(a, b)
                return a.stats.count > b.stats.count
            end)
            
            Log("STATS", "Top events:")
            for i = 1, math.min(5, #sortedEvents) do
                local e = sortedEvents[i]
                Log("STATS", string.format("  %s: %d times (%.2f total reward)",
                    e.name, e.stats.count, e.stats.totalReward))
            end
        end
    end
end)

-- Commands
RegisterCommand('capture', function(source, args)
    if args[1] == 'start' then
        captureEnabled = true
        Log("INFO", "Event capture enabled")
    elseif args[1] == 'stop' then
        captureEnabled = false
        Log("INFO", "Event capture disabled")
    elseif args[1] == 'stats' then
        Log("STATS", string.format("Total events: %d", #capturedEvents))
        Log("STATS", string.format("Unique events: %d", #eventStats))
        
        -- Show job events
        local jobCount = 0
        for name, stats in pairs(eventStats) do
            if stats.isJob then
                jobCount = jobCount + 1
                Log("STATS", string.format("  JOB: %s (%d times, %.2f reward)",
                    name, stats.count, stats.totalReward))
            end
        end
        Log("STATS", string.format("Job events: %d", jobCount))
    elseif args[1] == 'clear' then
        capturedEvents = {{}}
        eventStats = {{}}
        Log("INFO", "Cleared captured events")
    elseif args[1] == 'export' then
        -- In a real implementation, you'd save to file
        -- For now, just print JSON
        Log("INFO", "Exporting events...")
        print(json.encode({{
            events = capturedEvents,
            stats = eventStats,
            exportTime = os.date("%Y-%m-%d %H:%M:%S")
        }}))
    end
end, false)

Log("INFO", "Event Capture loaded - Use /capture start|stop|stats|clear|export")
Log("INFO", "Monitoring " .. #eventsToMonitor .. " events")
"""
        
        return script
        """
        Generate interactive GUI script with all widget types
        
        Args:
            title: Menu title
            
        Returns:
            Interactive GUI Lua script
        """
        script = f"""-- {title}
-- Interactive Ambani GUI Demo
-- Generated: {datetime.now().isoformat()}

"""
        
        script += self._generate_logging_setup()
        script += self._generate_ambani_gui_wrapper()
        
        script += f"""
-- Create Interactive Window
local window = ambani.MenuTabbedWindow("{title}", 150, 100, 600, 700, 140)
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
    local weathers = {"CLEAR", "EXTRASUNNY", "CLOUDS", "OVERCAST", "RAIN", "THUNDER", "SNOW", "BLIZZARD", "FOGGY"}
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
"""
        
        return script
    
    def _generate_ambani_gui_wrapper(self) -> str:
        """Generate Ambani GUI API wrapper"""
        return """-- Ambani GUI API Wrapper
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

"""
    
    def _generate_main_execution(self, exploit_count: int) -> str:
        """Generate main execution code"""
        code = """
-- Main Execution
local function Main()
    Log("INFO", "Starting exploit execution...")
    
"""
        
        for i in range(1, exploit_count + 1):
            code += f"""    -- Execute exploit {i}
    local success{i}, error{i} = pcall(Exploit{i})
    if not success{i} then
        Log("ERROR", "Exploit {i} failed: " .. tostring(error{i}))
    else
        Log("SUCCESS", "Exploit {i} completed")
    end
    Sleep(1000) -- Wait 1 second between exploits
    
"""
        
        code += """    Log("INFO", "All exploits completed")
end

-- Run main
Main()
"""
        
        return code
    
    def _generate_cleanup_code(self) -> str:
        """Generate cleanup code (Task 12.5)"""
        return """
-- Cleanup
local function Cleanup()
    Log("INFO", "Cleaning up...")
    -- Clear any registered events
    -- Reset any modified state
    -- Close connections
    Log("INFO", "Cleanup completed")
end

-- Register cleanup on exit
AddEventHandler('onResourceStop', function(resourceName)
    if GetCurrentResourceName() == resourceName then
        Cleanup()
    end
end)
"""
    
    def _format_parameter(self, param) -> str:
        """Format parameter for Lua code"""
        if isinstance(param, str):
            return f'"{param}"'
        elif isinstance(param, bool):
            return 'true' if param else 'false'
        elif isinstance(param, (int, float)):
            return str(param)
        elif isinstance(param, dict):
            # Convert dict to Lua table
            items = [f'{k} = {self._format_parameter(v)}' for k, v in param.items()]
            return '{' + ', '.join(items) + '}'
        elif isinstance(param, list):
            # Convert list to Lua table
            items = [self._format_parameter(v) for v in param]
            return '{' + ', '.join(items) + '}'
        else:
            return 'nil'
