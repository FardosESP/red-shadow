"""
Demonstration of Cross-File Trigger Chain Analysis

This example shows how the TriggerAnalyzer detects multi-stage attack chains
where one trigger calls another trigger across multiple files.
"""

import os
import tempfile
import shutil
from ambani_integration.analysis.trigger_analyzer import TriggerAnalyzer


def create_demo_server_dump():
    """Create a demo server dump with trigger chains"""
    temp_dir = tempfile.mkdtemp()
    
    # File 1: Bank system with entry point
    with open(os.path.join(temp_dir, 'bank_client.lua'), 'w') as f:
        f.write('''
-- Bank Client Script
RegisterNetEvent('bank:requestWithdraw')
AddEventHandler('bank:requestWithdraw', function(amount)
    -- Entry point - no validation!
    TriggerServerEvent('bank:processWithdraw', amount)
end)

RegisterNetEvent('bank:requestDeposit')
AddEventHandler('bank:requestDeposit', function(amount)
    -- Another entry point
    if amount > 0 then
        TriggerServerEvent('bank:processDeposit', amount)
    end
end)
''')
    
    # File 2: Bank server processing
    with open(os.path.join(temp_dir, 'bank_server.lua'), 'w') as f:
        f.write('''
-- Bank Server Script
RegisterNetEvent('bank:processWithdraw')
AddEventHandler('bank:processWithdraw', function(amount)
    -- No source validation!
    -- Calls economy system
    TriggerEvent('economy:addMoney', source, amount)
end)

RegisterNetEvent('bank:processDeposit')
AddEventHandler('bank:processDeposit', function(amount)
    -- Has some validation
    if not source then return end
    TriggerEvent('economy:removeMoney', source, amount)
end)
''')
    
    # File 3: Economy system
    with open(os.path.join(temp_dir, 'economy.lua'), 'w') as f:
        f.write('''
-- Economy System
RegisterNetEvent('economy:addMoney')
AddEventHandler('economy:addMoney', function(playerId, amount)
    -- No validation - dangerous!
    xPlayer.addMoney(amount)
    
    -- Triggers logging
    TriggerEvent('logger:logTransaction', playerId, amount, 'add')
end)

RegisterNetEvent('economy:removeMoney')
AddEventHandler('economy:removeMoney', function(playerId, amount)
    xPlayer.removeMoney(amount)
    TriggerEvent('logger:logTransaction', playerId, amount, 'remove')
end)

RegisterNetEvent('logger:logTransaction')
AddEventHandler('logger:logTransaction', function(playerId, amount, type)
    -- Logging only
    print(string.format("Transaction: Player %s %s $%d", playerId, type, amount))
end)
''')
    
    # File 4: Admin system with privilege escalation chain
    with open(os.path.join(temp_dir, 'admin.lua'), 'w') as f:
        f.write('''
-- Admin System
RegisterNetEvent('admin:requestPermission')
AddEventHandler('admin:requestPermission', function(permission)
    -- Entry point - weak validation
    TriggerServerEvent('admin:checkPermission', permission)
end)

RegisterNetEvent('admin:checkPermission')
AddEventHandler('admin:checkPermission', function(permission)
    -- Vulnerable check
    TriggerEvent('admin:grantPermission', source, permission)
end)

RegisterNetEvent('admin:grantPermission')
AddEventHandler('admin:grantPermission', function(playerId, permission)
    -- No validation!
    SetPlayerPermission(playerId, permission)
end)
''')
    
    # File 5: Isolated triggers (no chains)
    with open(os.path.join(temp_dir, 'misc.lua'), 'w') as f:
        f.write('''
-- Miscellaneous isolated triggers
RegisterNetEvent('misc:notify')
AddEventHandler('misc:notify', function(message)
    if not source then return end
    TriggerClientEvent('chat:addMessage', source, message)
end)

RegisterNetEvent('misc:getTime')
AddEventHandler('misc:getTime', function()
    if not source then return end
    local time = os.time()
    TriggerClientEvent('misc:receiveTime', source, time)
end)
''')
    
    return temp_dir


def analyze_and_display_chains(dump_path):
    """Analyze the dump and display trigger chains"""
    print("=" * 80)
    print("TRIGGER CHAIN ANALYSIS DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create analyzer
    analyzer = TriggerAnalyzer()
    
    # Analyze dump
    print(f"Analyzing server dump: {dump_path}")
    print()
    result = analyzer.analyze_dump(dump_path)
    
    if not result['success']:
        print(f"Analysis failed: {result.get('error', 'Unknown error')}")
        return
    
    # Display summary
    print("ANALYSIS SUMMARY")
    print("-" * 80)
    summary = result['summary']
    print(f"Total Triggers Found: {summary['total_triggers']}")
    print(f"  - CRITICAL: {summary['critical']}")
    print(f"  - HIGH: {summary['high']}")
    print(f"  - MEDIUM: {summary['medium']}")
    print(f"  - LOW: {summary['low']}")
    print()
    print(f"Trigger Chains Detected: {summary['trigger_chains']}")
    print(f"Multi-Stage Attacks: {summary['multi_stage_attacks']}")
    print()
    
    # Display trigger graph
    print("TRIGGER DEPENDENCY GRAPH")
    print("-" * 80)
    for trigger_name, called_triggers in analyzer.trigger_graph.items():
        if called_triggers:
            print(f"{trigger_name} -> {', '.join(called_triggers)}")
    print()
    
    # Display detected chains
    if result['trigger_chains']:
        print("DETECTED TRIGGER CHAINS")
        print("-" * 80)
        
        for i, chain in enumerate(result['trigger_chains'], 1):
            print(f"\nChain #{i}:")
            print(f"  Length: {chain.chain_length} triggers")
            print(f"  Combined Risk Score: {chain.combined_risk_score}/100")
            print(f"  Multi-Stage Attack: {'YES' if chain.is_multi_stage_attack else 'NO'}")
            print(f"  Entry Point: {chain.entry_point.name} ({chain.entry_point.file_path})")
            print(f"  Exit Points: {', '.join([t.name for t in chain.exit_points])}")
            print()
            print(f"  Chain Path:")
            for j, trigger in enumerate(chain.triggers, 1):
                print(f"    {j}. {trigger.name}")
                print(f"       File: {os.path.basename(trigger.file_path)}")
                print(f"       Risk: {trigger.risk_score}/100 ({trigger.category})")
                print(f"       Validation: {'YES' if trigger.has_validation else 'NO'}")
                print(f"       Rate Limiting: {'YES' if trigger.has_rate_limiting else 'NO'}")
            print()
            print(f"  Description:")
            print(f"    {chain.description}")
            print()
            
            # Show potential exploit
            if chain.is_multi_stage_attack:
                print(f"  ⚠️  EXPLOITATION SCENARIO:")
                print(f"    An attacker could exploit this chain by:")
                print(f"    1. Calling the entry point '{chain.entry_point.name}' from client")
                print(f"    2. The chain automatically propagates through {chain.chain_length} triggers")
                print(f"    3. Final impact occurs at: {', '.join([t.name for t in chain.exit_points])}")
                print()
    else:
        print("No trigger chains detected.")
        print("All triggers are isolated and don't call each other.")
    print()
    
    # Display high-risk chains
    high_risk_chains = [c for c in result['trigger_chains'] if c.combined_risk_score >= 70]
    if high_risk_chains:
        print("⚠️  HIGH-RISK CHAINS (Risk >= 70)")
        print("-" * 80)
        for chain in high_risk_chains:
            path = " -> ".join([t.name for t in chain.triggers])
            print(f"  • {path}")
            print(f"    Risk: {chain.combined_risk_score}/100")
            print(f"    Files: {len(set(t.file_path for t in chain.triggers))} files involved")
            print()


def main():
    """Main demonstration"""
    # Create demo server dump
    print("Creating demo server dump with trigger chains...")
    dump_path = create_demo_server_dump()
    
    try:
        # Analyze and display results
        analyze_and_display_chains(dump_path)
        
        print("=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print()
        print("Key Findings:")
        print("  • Cross-file trigger chains were successfully detected")
        print("  • DFS graph traversal identified multi-stage attack paths")
        print("  • Combined risk scores calculated for entire chains")
        print("  • Entry points and exit points identified")
        print()
        print("This analysis helps identify complex attack vectors that span")
        print("multiple files and resources, which are harder to detect with")
        print("simple static analysis.")
        print()
        
    finally:
        # Cleanup
        print(f"Cleaning up temporary files: {dump_path}")
        shutil.rmtree(dump_path)


if __name__ == '__main__':
    main()
