"""
Example usage of Auto Stop Engine with Professional Strategies

This example demonstrates how to use the AutoStopEngine to make intelligent
decisions about stopping resources based on professional knowledge and ML.
"""

from ambani_integration.execution.auto_stop_engine import (
    AutoStopEngine, StopMode, ResourceClassification
)
from ambani_integration.analysis.anticheat_analyzer import AnticheatAnalyzer
from ambani_integration.analysis.behavioral_analyzer import BehavioralAnalyzer


def example_basic_usage():
    """Basic usage of Auto Stop Engine"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Auto Stop Engine Usage")
    print("=" * 80)
    
    # Initialize engine in notify mode
    engine = AutoStopEngine(
        mode=StopMode.NOTIFY,
        confidence_threshold=0.7
    )
    
    # Example resource with triggers
    resource_name = "banking_system"
    triggers = [
        {
            'event_name': 'bank:deposit',
            'risk_score': 0.8,
            'category': 'CRITICAL'
        }
    ]
    code_content = """
    RegisterServerEvent('bank:deposit')
    AddEventHandler('bank:deposit', function(amount)
        -- No validation!
        AddMoney(source, amount)
    end)
    """
    
    # Make stop decision
    decision = engine.should_stop_resource(
        resource_name, triggers, code_content
    )
    
    print(f"\nResource: {decision.resource_name}")
    print(f"Should Stop: {decision.should_stop}")
    print(f"Confidence: {decision.confidence_score:.2f}")
    print(f"Classification: {decision.classification.value}")
    print(f"Recommended Action: {decision.recommended_action}")
    print(f"Reasons:")
    for reason in decision.reasons:
        print(f"  - {reason}")


def example_with_anticheat():
    """Example with anticheat detection"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Auto Stop with Anticheat Detection")
    print("=" * 80)
    
    # Initialize with anticheat analyzer
    anticheat_analyzer = AnticheatAnalyzer()
    engine = AutoStopEngine(
        mode=StopMode.AUTO,
        confidence_threshold=0.7,
        anticheat_analyzer=anticheat_analyzer
    )
    
    # Test with different anticheats
    anticheats = ['FiveGuard', 'WaveShield', 'Phoenix AC']
    resource_name = "screenshot_capture"
    triggers = [{'risk_score': 0.6}]
    code_content = "RegisterCommand('screenshot', function() end)"
    
    for ac_name in anticheats:
        decision = engine.should_stop_resource(
            resource_name, triggers, code_content, ac_name
        )
        
        print(f"\n--- With {ac_name} ---")
        print(f"Should Stop: {decision.should_stop}")
        print(f"Confidence: {decision.confidence_score:.2f}")
        print(f"Anticheat Risk: {decision.anticheat_risk:.2f}")
        print(f"Detection Probability: {decision.detection_probability:.2f}")


def example_professional_recommendations():
    """Example showing professional recommendations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Professional Recommendations")
    print("=" * 80)
    
    engine = AutoStopEngine()
    
    # Test different resource types with FiveGuard
    test_cases = [
        ('screenshot_resource', 'FiveGuard'),
        ('webhook_logger', 'FiveGuard'),
        ('admin_panel', 'FiveGuard'),
        ('clothing_shop', 'WaveShield'),
        ('banking_system', 'Phoenix AC'),
    ]
    
    for resource, anticheat in test_cases:
        rec = engine.get_professional_recommendation(resource, anticheat)
        
        print(f"\n--- {resource} with {anticheat} ---")
        print(f"Recommended: {rec['recommended']}")
        print(f"Detection Risk: {rec['detection_risk']:.2f}")
        print(f"Reason: {rec['reason']}")
        print(f"Timing: {rec['timing']}")
        if rec['professional_tip']:
            print(f"Pro Tip: {rec['professional_tip'][:80]}...")


def example_classification():
    """Example of resource classification"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Resource Classification")
    print("=" * 80)
    
    engine = AutoStopEngine()
    
    # Test different resources
    resources = [
        ('es_extended', []),
        ('banking_system', []),
        ('clothing_shop', []),
        ('vulnerable_resource', [{'risk_score': 0.9}]),
    ]
    
    for resource, triggers in resources:
        classification = engine.classify_resource(resource, triggers)
        print(f"{resource:30} -> {classification.value}")


def example_with_feedback():
    """Example with admin feedback and learning"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Learning from Feedback")
    print("=" * 80)
    
    engine = AutoStopEngine(confidence_threshold=0.7)
    
    print(f"Initial threshold: {engine.confidence_threshold:.2f}")
    
    # Simulate feedback
    feedback_data = [
        ('resource1', True, 'Good stop'),
        ('resource2', True, 'Correct decision'),
        ('resource3', False, 'Should not have stopped'),
        ('resource4', False, 'False positive'),
        ('resource5', False, 'Bad stop'),
        ('resource6', True, 'Good'),
        ('resource7', False, 'FP'),
        ('resource8', False, 'FP'),
        ('resource9', False, 'FP'),
        ('resource10', False, 'FP'),
    ]
    
    for resource, correct, comment in feedback_data:
        engine.record_feedback(resource, correct, comment)
    
    # Get statistics
    stats = engine.get_statistics()
    
    print(f"\nAfter feedback:")
    print(f"New threshold: {engine.confidence_threshold:.2f}")
    print(f"True Positives: {stats['true_positives']}")
    print(f"False Positives: {stats['false_positives']}")
    print(f"Precision: {stats['precision']:.2f}")
    print(f"Recall: {stats['recall']:.2f}")
    print(f"F1 Score: {stats['f1_score']:.2f}")


def example_rate_limiting():
    """Example of rate limiting"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Rate Limiting")
    print("=" * 80)
    
    engine = AutoStopEngine()
    
    print(f"Max stops per minute: {engine.max_stops_per_minute}")
    
    # Simulate stops
    from datetime import datetime
    for i in range(5):
        can_stop = engine.check_rate_limit()
        print(f"Stop {i+1}: {'Allowed' if can_stop else 'BLOCKED (rate limit)'}")
        if can_stop:
            engine.recent_stops.append(datetime.now())


def example_grace_period():
    """Example of grace period"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Grace Period")
    print("=" * 80)
    
    engine = AutoStopEngine()
    
    print(f"Grace period: {engine.grace_period_seconds} seconds")
    
    # Register new resource
    resource_name = "new_resource"
    engine.register_resource_start(resource_name)
    
    # Try to stop immediately
    triggers = [{'risk_score': 0.9}]
    code = "RegisterServerEvent('test')"
    
    decision = engine.should_stop_resource(resource_name, triggers, code)
    
    print(f"\nResource: {resource_name}")
    print(f"Should Stop: {decision.should_stop}")
    print(f"Reason: {decision.reasons[0]}")


def example_stop_detection():
    """Example of stop detection logic"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Stop Detection Logic")
    print("=" * 80)
    
    engine = AutoStopEngine()
    
    # Code with stop detection
    code_with_detection = """
    AddEventHandler('onResourceStop', function(resourceName)
        if resourceName == GetCurrentResourceName() then
            BanPlayer(source, 'Resource stopped - cheating detected')
        end
    end)
    """
    
    # Code without stop detection
    code_without_detection = """
    RegisterCommand('test', function(source, args)
        print('Test command executed')
    end)
    """
    
    print("Code WITH stop detection:")
    print(f"  Detected: {engine.detect_stop_detection_logic(code_with_detection)}")
    
    print("\nCode WITHOUT stop detection:")
    print(f"  Detected: {engine.detect_stop_detection_logic(code_without_detection)}")


def example_different_modes():
    """Example of different operation modes"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Different Operation Modes")
    print("=" * 80)
    
    modes = [
        (StopMode.MANUAL, "Requires admin approval for each stop"),
        (StopMode.NOTIFY, "Stops automatically but notifies admin"),
        (StopMode.AUTO, "Fully automatic stopping"),
    ]
    
    for mode, description in modes:
        engine = AutoStopEngine(mode=mode)
        print(f"\n{mode.value.upper()} Mode:")
        print(f"  {description}")
        print(f"  Mode: {engine.mode.value}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("AUTO STOP ENGINE - PROFESSIONAL STRATEGIES EXAMPLES")
    print("=" * 80)
    
    example_basic_usage()
    example_with_anticheat()
    example_professional_recommendations()
    example_classification()
    example_with_feedback()
    example_rate_limiting()
    example_grace_period()
    example_stop_detection()
    example_different_modes()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
