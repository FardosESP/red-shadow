"""
Event Monitor Usage Example
Real functional example for analyzing captured events and generating farming strategies
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ambani_integration.intelligence.event_monitor import EventMonitor
from ambani_integration.analysis.anticheat_analyzer import AnticheatAnalyzer


def main():
    # Initialize
    anticheat_analyzer = AnticheatAnalyzer()
    monitor = EventMonitor(anticheat_analyzer=anticheat_analyzer)
    
    # Analyze captured events
    captured_file = "captured_events.json"
    
    if not os.path.exists(captured_file):
        print(f"ERROR: {captured_file} not found")
        print("Run event_capture.lua in FiveM first to capture events")
        return
    
    print(f"Analyzing {captured_file}...")
    strategies = monitor.analyze_captured_events(
        captured_file=captured_file,
        min_sample_size=3,
        min_success_rate=0.7
    )
    
    if not strategies:
        print("No farming strategies found")
        return
    
    # Show strategies
    print(f"\nFound {len(strategies)} farming strategies:")
    for i, strategy in enumerate(strategies, 1):
        print(f"\n[{i}] {strategy.event_name}")
        print(f"    Reward: {strategy.avg_reward:.2f} {strategy.reward_type}")
        print(f"    Profit/Hour: {strategy.profit_per_hour:.2f}")
        print(f"    Cooldown: {strategy.cooldown_seconds}s")
        print(f"    Risk: {strategy.detection_risk*100:.1f}%")
        print(f"    Sample Size: {strategy.sample_size}")
        print(f"    Confidence: {strategy.confidence_level*100:.1f}%")
    
    # Export for Lua
    output_file = "farming_strategies.json"
    monitor.export_strategies_for_lua(output_file)
    print(f"\nStrategies exported to {output_file}")
    print("Load auto_farmer.lua in FiveM and run: /farmer load")
    
    # Show statistics
    stats = monitor.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Unique Events: {stats['unique_events']}")
    print(f"  Job Events: {stats['job_events']}")
    print(f"  Reward Events: {stats['reward_events']}")
    print(f"  Farming Strategies: {stats['farming_strategies']}")
    print(f"  Avg Profit/Hour: {stats['avg_profit_per_hour']:.2f}")


if __name__ == "__main__":
    main()
