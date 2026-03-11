"""
Example usage of Trigger Analyzer

This script demonstrates how to use the TriggerAnalyzer to analyze
FiveM server dumps for Ambani-exploitable vulnerabilities.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ambani_integration.analysis.trigger_analyzer import TriggerAnalyzer


def main():
    """Main example function"""
    print("=" * 60)
    print("Trigger Analyzer - Example Usage")
    print("=" * 60)
    print()
    
    # Initialize analyzer
    analyzer = TriggerAnalyzer()
    print("✓ TriggerAnalyzer initialized")
    print()
    
    # Example 1: Analyze a single Lua file
    print("Example 1: Analyzing a single Lua file")
    print("-" * 60)
    
    # Create example Lua file
    example_lua = Path(__file__).parent / "example_server.lua"
    example_lua.write_text("""
-- Vulnerable event - no validation
RegisterNetEvent('esx:giveMoney')
AddEventHandler('esx:giveMoney', function(source, amount)
    local xPlayer = ESX.GetPlayerFromId(source)
    xPlayer.addMoney(amount)
end)

-- Safe event - has validation
RegisterNetEvent('esx:safeEvent')
AddEventHandler('esx:safeEvent', function(source)
    if not source then return end
    if not IsPlayerAceAllowed(source, 'admin') then return end
    print('Admin action executed')
end)

-- Honeypot - attractive name with ban logic
RegisterNetEvent('giveFreeMoneyNow')
AddEventHandler('giveFreeMoneyNow', function(source)
    BanPlayer(source, 'Cheat attempt detected')
end)

-- Dangerous natives without validation
RegisterNetEvent('teleport:player')
AddEventHandler('teleport:player', function(source, x, y, z)
    local ped = GetPlayerPed(source)
    SetEntityCoords(ped, x, y, z)
    GiveWeaponToPed(ped, 'WEAPON_PISTOL', 1000, false, true)
end)
    """)
    
    # Analyze the file
    result = analyzer.analyze_dump(str(example_lua))
    
    if result['success']:
        print(f"✓ Analysis completed successfully")
        print()
        print(f"Summary:")
        print(f"  Total triggers: {result['summary']['total_triggers']}")
        print(f"  CRITICAL: {result['summary']['critical']}")
        print(f"  HIGH: {result['summary']['high']}")
        print(f"  MEDIUM: {result['summary']['medium']}")
        print(f"  LOW: {result['summary']['low']}")
        print()
        
        # Show exploit vectors
        if result['exploit_vectors']:
            print(f"Exploit Vectors Found: {len(result['exploit_vectors'])}")
            print("-" * 60)
            for i, exploit in enumerate(result['exploit_vectors'], 1):
                print(f"\n{i}. {exploit.trigger.name}")
                print(f"   Type: {exploit.exploit_type}")
                print(f"   Severity: {exploit.severity}")
                print(f"   Risk Score: {exploit.trigger.risk_score}")
                print(f"   Impact: {exploit.impact}")
                print(f"   PoC: {exploit.proof_of_concept}")
                print(f"   Mitigation: {exploit.mitigation[:100]}...")
        
        # Show honeypots
        if result['honeypots']:
            print()
            print(f"\nHoneypots Detected: {len(result['honeypots'])}")
            print("-" * 60)
            for i, honeypot in enumerate(result['honeypots'], 1):
                print(f"\n{i}. {honeypot.trigger.name}")
                print(f"   Confidence: {honeypot.confidence:.2f}")
                print(f"   Detection: {honeypot.detection_mechanism}")
                print(f"   Silent: {honeypot.is_silent}")
    
    else:
        print(f"✗ Analysis failed: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 60)
    
    # Cleanup
    example_lua.unlink()


if __name__ == '__main__':
    main()
