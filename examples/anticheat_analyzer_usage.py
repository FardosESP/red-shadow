"""
Example usage of Anticheat Analyzer

Demonstrates:
- Anticheat detection
- Profile creation
- Risk assessment
- Bypass technique suggestions
- Component stop risk analysis
- Main anticheat stop risk analysis
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ambani_integration.analysis.anticheat_analyzer import AnticheatAnalyzer


def print_separator(title=""):
    """Print a separator line"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def example_basic_detection():
    """Example 1: Basic anticheat detection"""
    print_separator("Example 1: Basic Anticheat Detection")
    
    analyzer = AnticheatAnalyzer()
    
    # Sample code with FiveGuard
    code_base = {
        "server.lua": """
            -- FiveGuard v2.5.1 Protection
            local FiveGuard = {}
            FiveGuard.version = "2.5.1"
            fg_version = "2.5.1"
            
            function FiveGuard.CheckPlayer(player)
                -- Memory scanning
                -- Event injection detection
                -- Native spoofing detection
            end
            
            function FG_AC.Init()
                print("FiveGuard initialized")
            end
        """,
        "config.lua": """
            Config = {}
            Config.FiveGuard = {
                enabled = true,
                aggressive_rate_limiting = true,
                memory_scanning = true
            }
        """
    }
    
    # Detect anticheats
    profiles = analyzer.detect_anticheats(code_base)
    
    print(f"Detected {len(profiles)} anticheat(s):\n")
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile.name} v{profile.version}")
        print(f"   Confidence: {profile.confidence:.2%}")
        print(f"   Bypass Difficulty: {profile.bypass_difficulty:.2f}")
        print(f"   Recommended Strategy: {profile.recommended_strategy}")
        print(f"   Capabilities: {', '.join(profile.capabilities[:3])}...")
        print(f"   Limitations: {', '.join(profile.limitations)}")
        print()


def example_risk_assessment():
    """Example 2: Detection risk assessment"""
    print_separator("Example 2: Detection Risk Assessment")
    
    analyzer = AnticheatAnalyzer()
    
    # Create sample profiles
    from ambani_integration.analysis.anticheat_analyzer import AnticheatProfile
    
    profiles = [
        AnticheatProfile(name="FiveGuard", bypass_difficulty=0.85),
        AnticheatProfile(name="Phoenix AC", bypass_difficulty=0.70)
    ]
    
    # Test different action scenarios
    scenarios = [
        (["trigger_event"], "Low Risk Actions"),
        (["stop_resource", "trigger_event"], "Medium Risk Actions"),
        (["modify_money", "teleport"], "High Risk Actions"),
        (["stop_anticheat", "god_mode"], "Extreme Risk Actions")
    ]
    
    for actions, scenario_name in scenarios:
        risk = analyzer.calculate_detection_risk(profiles, actions)
        risk_level = "LOW" if risk < 0.5 else "MEDIUM" if risk < 0.7 else "HIGH" if risk < 0.85 else "EXTREME"
        
        print(f"{scenario_name}:")
        print(f"  Actions: {', '.join(actions)}")
        print(f"  Detection Risk: {risk:.2%} ({risk_level})")
        print()


def example_bypass_suggestions():
    """Example 3: Bypass technique suggestions"""
    print_separator("Example 3: Bypass Technique Suggestions")
    
    analyzer = AnticheatAnalyzer()
    
    # Create profile for FiveGuard
    from ambani_integration.analysis.anticheat_analyzer import AnticheatProfile
    
    profile = AnticheatProfile(
        name="FiveGuard",
        bypass_difficulty=0.85,
        bypass_techniques=["ultra_stealth_mode", "timing_randomization", "payload_fragmentation"],
        capabilities=["memory_scanning", "event_injection_detection", "aggressive_rate_limiting"],
        limitations=["high_false_positive_rate", "resource_intensive"]
    )
    
    suggestions = analyzer.suggest_bypass_techniques(profile)
    
    print(f"Bypass suggestions for {profile.name}:\n")
    
    for i, suggestion in enumerate(suggestions[:8], 1):  # Show first 8
        print(f"{i}. {suggestion['technique']}")
        print(f"   Difficulty: {suggestion['difficulty']:.2f}")
        print(f"   Success Probability: {suggestion['success_probability']:.2%}")
        print(f"   Description: {suggestion['description']}")
        print(f"   Requirements: {', '.join(suggestion['requirements'])}")
        print()


def example_strategy_recommendation():
    """Example 4: Overall strategy recommendation"""
    print_separator("Example 4: Strategy Recommendation")
    
    analyzer = AnticheatAnalyzer()
    
    from ambani_integration.analysis.anticheat_analyzer import AnticheatProfile
    
    # Test different anticheat scenarios
    scenarios = [
        ([], "No Anticheat"),
        ([AnticheatProfile(name="BadgerAC", bypass_difficulty=0.30)], "Weak Anticheat"),
        ([AnticheatProfile(name="WaveShield", bypass_difficulty=0.50)], "Moderate Anticheat"),
        ([AnticheatProfile(name="FireAC", bypass_difficulty=0.75)], "Strong Anticheat"),
        ([AnticheatProfile(name="FiveGuard", bypass_difficulty=0.85)], "Very Strong Anticheat"),
        ([
            AnticheatProfile(name="FiveGuard", bypass_difficulty=0.85),
            AnticheatProfile(name="Phoenix AC", bypass_difficulty=0.70)
        ], "Multiple Anticheats")
    ]
    
    for profiles, scenario_name in scenarios:
        strategy = analyzer.get_recommended_strategy(profiles)
        
        print(f"{scenario_name}:")
        print(f"  Strategy: {strategy['strategy'].upper()}")
        print(f"  Confidence: {strategy['confidence']:.2%}")
        print(f"  Max Stops/Minute: {strategy['max_stops_per_minute']}")
        print(f"  Grace Period: {strategy['grace_period']}s")
        if profiles:
            print(f"  Detected: {', '.join(strategy['detected_anticheats'])}")
            print(f"  Highest Difficulty: {strategy['highest_difficulty']:.2f}")
        print()


def example_component_stop_risk():
    """Example 5: Component stop risk analysis"""
    print_separator("Example 5: Component Stop Risk Analysis")
    
    analyzer = AnticheatAnalyzer()
    
    # Test different components with different anticheats
    components = ["screen_capture", "process_scanner", "event_monitor", "webhook_logger"]
    anticheats = ["FiveGuard", "Phoenix AC", "WaveShield", "BadgerAC"]
    
    print("Component Stop Risk Matrix:\n")
    print(f"{'Component':<20} {'Anticheat':<15} {'Risk':<8} {'Safety':<12} {'Benefit'}")
    print("-" * 80)
    
    for component in components:
        for anticheat in anticheats:
            risk = analyzer.get_component_stop_risk(anticheat, component)
            
            detection_risk = risk.get('detection_risk', 0.5)
            risk_level = "LOW" if detection_risk < 0.4 else "MED" if detection_risk < 0.7 else "HIGH"
            
            print(f"{component:<20} {anticheat:<15} {risk_level:<8} "
                  f"{risk.get('stop_safety', 'unknown'):<12} "
                  f"{risk.get('bypass_benefit', 'N/A')[:40]}")
        print()


def example_main_anticheat_stop():
    """Example 6: Main anticheat stop risk analysis"""
    print_separator("Example 6: Main Anticheat Stop Risk Analysis")
    
    analyzer = AnticheatAnalyzer()
    
    anticheats = ["FiveGuard", "Phoenix AC", "WaveShield", "FireAC", "BadgerAC", "Qprotect"]
    
    print("Main Anticheat Stop Risk Analysis:\n")
    
    for anticheat in anticheats:
        risk = analyzer.get_main_anticheat_stop_risk(anticheat)
        
        print(f"{anticheat}:")
        print(f"  Can Stop: {risk.get('can_stop', True)}")
        print(f"  Detection Risk: {risk.get('detection_risk', 0.9):.2%}")
        print(f"  Consequences: {risk.get('consequences', 'Unknown')}")
        print(f"  Detection Method: {risk.get('detection_method', 'Unknown')}")
        print(f"  Recommended: {risk.get('recommended', 'DO NOT ATTEMPT')}")
        
        strategies = risk.get('bypass_strategies', [])
        if strategies:
            print(f"  Bypass Strategies:")
            for strategy in strategies[:2]:  # Show first 2
                print(f"    - {strategy['name']}")
                print(f"      Difficulty: {strategy['difficulty']:.2f}")
                print(f"      Success Rate: {strategy['success_rate']:.2%}")
        print()


def example_silent_detection():
    """Example 7: Silent anticheat detection"""
    print_separator("Example 7: Silent Anticheat Detection")
    
    analyzer = AnticheatAnalyzer()
    
    # Code with silent anticheat indicators
    code_base = {
        "hidden.lua": """
            local function a(b)
                -- silent ban
                BanPlayer(b) -- silent
            end
            
            local function c()
                -- stealth log
                PerformHttpRequest("https://webhook.site/xxx", function() end, "POST", "silent")
            end
            
            -- Encrypted communication
            local encrypted = base64.encode(data)
            
            -- Obfuscated checks
            local x = function(y) return string.char(65) end
        """
    }
    
    profiles = analyzer.detect_anticheats(code_base)
    
    print(f"Detected {len(profiles)} anticheat(s):\n")
    
    for profile in profiles:
        print(f"Name: {profile.name}")
        print(f"Confidence: {profile.confidence:.2%}")
        print(f"Capabilities: {', '.join(profile.capabilities)}")
        print(f"Behavioral Indicators: {', '.join(profile.behavioral_indicators)}")
        print(f"Bypass Difficulty: {profile.bypass_difficulty:.2f}")
        print()


def example_multiple_anticheats():
    """Example 8: Multiple anticheats detection"""
    print_separator("Example 8: Multiple Anticheats Detection")
    
    analyzer = AnticheatAnalyzer()
    
    # Code with multiple anticheats
    code_base = {
        "ac1.lua": """
            -- FiveGuard v2.5.0
            local FiveGuard = {}
            FG_AC = {}
            fg_version = "2.5.0"
        """,
        "ac2.lua": """
            -- Phoenix AC v1.8.0
            local PhoenixAC = {}
            pac_version = "1.8.0"
        """,
        "ac3.lua": """
            -- WaveShield protection
            local WaveShield = {}
            ws_version = "1.0.0"
        """
    }
    
    profiles = analyzer.detect_anticheats(code_base)
    
    print(f"Detected {len(profiles)} anticheats:\n")
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile.name} v{profile.version}")
        print(f"   Confidence: {profile.confidence:.2%}")
        print(f"   Bypass Difficulty: {profile.bypass_difficulty:.2f}")
        print()
    
    # Get combined strategy
    strategy = analyzer.get_recommended_strategy(profiles)
    
    print(f"Combined Strategy:")
    print(f"  Strategy: {strategy['strategy'].upper()}")
    print(f"  Max Stops/Minute: {strategy['max_stops_per_minute']}")
    print(f"  Grace Period: {strategy['grace_period']}s")
    print(f"  Highest Difficulty: {strategy['highest_difficulty']:.2f}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("  ANTICHEAT ANALYZER - USAGE EXAMPLES")
    print("  FOR SECURITY RESEARCH AND AUTHORIZED TESTING ONLY")
    print("="*80)
    
    try:
        example_basic_detection()
        example_risk_assessment()
        example_bypass_suggestions()
        example_strategy_recommendation()
        example_component_stop_risk()
        example_main_anticheat_stop()
        example_silent_detection()
        example_multiple_anticheats()
        
        print_separator("All Examples Completed Successfully")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
