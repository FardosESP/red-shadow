"""
Example usage of Lua Script Generator with Ambani API and GUI

This example demonstrates how to generate Lua exploit scripts with:
- Ambani API integration (events, natives, exports)
- GUI menus with tabs, buttons, sliders, checkboxes
- Rate limiting and safe mode
- Logging and error handling
- Script obfuscation
"""

from ambani_integration.execution.lua_script_generator import LuaScriptGenerator


def example_basic_exploit_script():
    """Generate a basic exploit script"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Exploit Script")
    print("=" * 80)
    
    generator = LuaScriptGenerator(safe_mode=True, obfuscate=False)
    
    exploit = {
        'event_name': 'bank:deposit',
        'method': 'TriggerServerEvent',
        'parameters': [1000000],  # Deposit 1 million
        'description': 'Exploit banking system to deposit money without validation',
        'risk_score': 0.9
    }
    
    script = generator.generate_exploit_script(exploit)
    
    print("\nGenerated Script:")
    print("-" * 80)
    print(script[:500] + "...")  # Print first 500 chars
    print("-" * 80)
    
    # Save to file
    with open('output_basic_exploit.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_basic_exploit.lua")


def example_poc_script():
    """Generate proof-of-concept script with multiple exploits"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Proof-of-Concept Script (Multiple Exploits)")
    print("=" * 80)
    
    generator = LuaScriptGenerator(safe_mode=True)
    
    exploits = [
        {
            'event_name': 'bank:deposit',
            'method': 'TriggerServerEvent',
            'parameters': [1000000],
            'description': 'Deposit money exploit',
            'risk_score': 0.9
        },
        {
            'event_name': 'inventory:addItem',
            'method': 'TriggerServerEvent',
            'parameters': ['weapon_pistol', 10],
            'description': 'Add weapons to inventory',
            'risk_score': 0.8
        },
        {
            'event_name': 'admin:givePerms',
            'method': 'TriggerServerEvent',
            'parameters': ['admin'],
            'description': 'Grant admin permissions',
            'risk_score': 1.0
        }
    ]
    
    script = generator.generate_poc_script(exploits, title="Banking & Inventory PoC")
    
    print(f"\nGenerated PoC with {len(exploits)} exploits")
    print(f"Script length: {len(script)} characters")
    
    # Save to file
    with open('output_poc_script.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✓ Script saved to: output_poc_script.lua")


def example_gui_script():
    """Generate script with Ambani GUI menu"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: GUI Menu Script")
    print("=" * 80)
    
    generator = LuaScriptGenerator(safe_mode=False)
    
    exploits = [
        {
            'event_name': 'bank:deposit',
            'method': 'TriggerServerEvent',
            'parameters': [1000000],
            'description': 'Deposit 1M',
            'risk_score': 0.9
        },
        {
            'event_name': 'bank:withdraw',
            'method': 'TriggerServerEvent',
            'parameters': [500000],
            'description': 'Withdraw 500K',
            'risk_score': 0.8
        },
        {
            'event_name': 'inventory:addItem',
            'method': 'TriggerServerEvent',
            'parameters': ['weapon_pistol', 5],
            'description': 'Add weapons',
            'risk_score': 0.8
        },
        {
            'event_name': 'vehicle:spawn',
            'method': 'TriggerServerEvent',
            'parameters': ['adder'],
            'description': 'Spawn vehicle',
            'risk_score': 0.7
        }
    ]
    
    script = generator.generate_gui_script(
        title="Exploit Menu",
        exploits=exploits,
        keybind='F5'
    )
    
    print(f"\nGenerated GUI menu with {len(exploits)} exploit buttons")
    print("Features:")
    print("  - Tabbed window (Exploits, Settings, Info)")
    print("  - Toggle with F5 key")
    print("  - Blue accent color")
    print("  - Rate limiting slider")
    print("  - Safe mode checkbox")
    print(f"  - Script length: {len(script)} characters")
    
    # Save to file
    with open('output_gui_menu.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_gui_menu.lua")


def example_interactive_gui():
    """Generate interactive GUI with all widget types"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Interactive GUI (All Widgets)")
    print("=" * 80)
    
    generator = LuaScriptGenerator(safe_mode=False)
    
    script = generator.generate_interactive_gui_script(title="Full Feature Menu")
    
    print("\nGenerated interactive GUI with:")
    print("  - 5 tabs (Events, Natives, Player, Vehicle, World)")
    print("  - Input boxes for custom events/natives")
    print("  - Sliders for health, armor, speed, time")
    print("  - Checkboxes for god mode, invisible, freeze time")
    print("  - Dropdown for weather selection")
    print("  - Buttons for heal, repair, flip, etc.")
    print(f"  - Script length: {len(script)} characters")
    
    # Save to file
    with open('output_interactive_gui.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_interactive_gui.lua")


def example_repl_script():
    """Generate REPL script"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: REPL Script")
    print("=" * 80)
    
    generator = LuaScriptGenerator()
    
    exploits = [
        {'event_name': 'test:event1', 'method': 'TriggerServerEvent', 'parameters': []},
        {'event_name': 'test:event2', 'method': 'TriggerServerEvent', 'parameters': []}
    ]
    
    script = generator.generate_repl_script(exploits)
    
    print("\nGenerated REPL with commands:")
    print("  - help: Show available commands")
    print("  - list: List exploits")
    print("  - run <id>: Run exploit by ID")
    print("  - trigger <event> <params>: Trigger custom event")
    print("  - native <hash> <params>: Invoke native")
    print("  - export <resource> <export> <params>: Call export")
    print("  - exit: Exit REPL")
    
    # Save to file
    with open('output_repl.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_repl.lua")


def example_rate_limiting():
    """Add rate limiting to script"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Rate Limiting")
    print("=" * 80)
    
    generator = LuaScriptGenerator()
    
    exploit = {
        'event_name': 'spam:event',
        'method': 'TriggerServerEvent',
        'parameters': ['test'],
        'description': 'Spam event',
        'risk_score': 0.5
    }
    
    script = generator.generate_exploit_script(exploit)
    
    # Add rate limiting (10 events per second)
    script_with_limit = generator.add_rate_limiting(script, rate=10)
    
    print("\nAdded rate limiting:")
    print("  - Maximum: 10 events per second")
    print("  - Minimum interval: 100ms between events")
    print(f"  - Original length: {len(script)} chars")
    print(f"  - With rate limit: {len(script_with_limit)} chars")
    
    # Save to file
    with open('output_rate_limited.lua', 'w', encoding='utf-8') as f:
        f.write(script_with_limit)
    
    print("\n✓ Script saved to: output_rate_limited.lua")


def example_obfuscation():
    """Obfuscate script for stealth"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Script Obfuscation")
    print("=" * 80)
    
    generator = LuaScriptGenerator(obfuscate=True)
    
    exploit = {
        'event_name': 'secret:event',
        'method': 'TriggerServerEvent',
        'parameters': ['hidden'],
        'description': 'Secret exploit',
        'risk_score': 0.9
    }
    
    script = generator.generate_exploit_script(exploit)
    obfuscated = generator.obfuscate_script(script)
    
    print("\nObfuscation applied:")
    print("  - Comments removed")
    print("  - Whitespace minimized")
    print("  - Wrapped in loadstring")
    print(f"  - Original length: {len(script)} chars")
    print(f"  - Obfuscated length: {len(obfuscated)} chars")
    print(f"  - Size reduction: {100 * (1 - len(obfuscated)/len(script)):.1f}%")
    
    print("\nObfuscated preview:")
    print("-" * 80)
    print(obfuscated[:200] + "...")
    print("-" * 80)
    
    # Save to file
    with open('output_obfuscated.lua', 'w', encoding='utf-8') as f:
        f.write(obfuscated)
    
    print("\n✓ Script saved to: output_obfuscated.lua")


def example_native_invocation():
    """Generate script with native invocation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Native Invocation")
    print("=" * 80)
    
    generator = LuaScriptGenerator()
    
    exploit = {
        'event_name': 'teleport',
        'method': 'InvokeNative',
        'native_hash': '0x06843DA7060A026B',  # SET_ENTITY_COORDS
        'parameters': [
            'PlayerPedId()',
            0.0,  # x
            0.0,  # y
            100.0,  # z
            'false',
            'false',
            'false',
            'true'
        ],
        'description': 'Teleport player to coordinates',
        'risk_score': 0.7
    }
    
    script = generator.generate_exploit_script(exploit)
    
    print("\nGenerated native invocation script:")
    print(f"  - Native: {exploit['native_hash']}")
    print(f"  - Parameters: {len(exploit['parameters'])}")
    
    # Save to file
    with open('output_native.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_native.lua")


def example_export_invocation():
    """Generate script with export invocation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Export Invocation")
    print("=" * 80)
    
    generator = LuaScriptGenerator()
    
    exploit = {
        'event_name': 'getSharedObject',
        'method': 'InvokeExport',
        'resource': 'es_extended',
        'export_name': 'getSharedObject',
        'parameters': [],
        'description': 'Get ESX shared object',
        'risk_score': 0.6
    }
    
    script = generator.generate_exploit_script(exploit)
    
    print("\nGenerated export invocation script:")
    print(f"  - Resource: {exploit['resource']}")
    print(f"  - Export: {exploit['export_name']}")
    
    # Save to file
    with open('output_export.lua', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("\n✓ Script saved to: output_export.lua")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("LUA SCRIPT GENERATOR - AMBANI API & GUI EXAMPLES")
    print("=" * 80)
    
    example_basic_exploit_script()
    example_poc_script()
    example_gui_script()
    example_interactive_gui()
    example_repl_script()
    example_rate_limiting()
    example_obfuscation()
    example_native_invocation()
    example_export_invocation()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("Generated 9 Lua scripts in current directory")
    print("=" * 80)


if __name__ == '__main__':
    main()
