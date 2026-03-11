"""
Example: Database Usage
Demonstrates how to use the database module for storing analysis history and learning feedback
"""

from ambani_integration.database import DatabaseManager, init_database
from datetime import datetime
import json


def example_basic_usage():
    """Basic database usage example"""
    print("=" * 80)
    print("Example 1: Basic Database Usage")
    print("=" * 80)
    
    # Initialize database
    db = init_database("./data/example_ambani.db")
    print(f"✓ Database initialized at: {db.db_path}\n")
    
    # Store analysis result
    print("Storing analysis result...")
    analysis_data = {
        'server_name': 'MyFiveMServer',
        'resource_name': 'bank_robbery',
        'resource_type': 'bank',
        'risk_score': 95,
        'vulnerabilities_count': 5,
        'critical_vulns': 3,
        'high_vulns': 2,
        'medium_vulns': 0,
        'low_vulns': 0,
        'exploit_vectors': [
            {
                'type': 'event_injection',
                'severity': 'CRITICAL',
                'event_name': 'giveMoney',
                'description': 'No source validation'
            },
            {
                'type': 'callback_exploit',
                'severity': 'HIGH',
                'callback_name': 'getPlayerMoney',
                'description': 'Returns sensitive data without permission check'
            }
        ],
        'trigger_data': {
            'event_name': 'giveMoney',
            'has_validation': False,
            'has_rate_limiting': False,
            'dangerous_natives': ['AddCash', 'GiveWeaponToPed']
        },
        'anticheat_detected': ['FiveGuard'],
        'analysis_result': {
            'total_triggers': 15,
            'vulnerable_triggers': 5,
            'honeypots_detected': 1
        }
    }
    
    record_id = db.store_analysis_result(analysis_data)
    print(f"✓ Analysis result stored with ID: {record_id}\n")
    
    db.close()


def example_auto_stop_workflow():
    """Example of Auto Stop Engine workflow with database"""
    print("=" * 80)
    print("Example 2: Auto Stop Engine Workflow")
    print("=" * 80)
    
    db = DatabaseManager("./data/example_ambani.db")
    db.connect()
    
    # 1. Store stop decision
    print("1. Auto Stop Engine makes a decision...")
    decision_data = {
        'resource_name': 'bank_robbery',
        'stop_confidence': 0.92,
        'risk_score': 95,
        'critical_vulns': 3,
        'active_exploits': True,
        'false_positive_rate': 0.05,
        'mode': 'auto',
        'requires_confirmation': False,
        'executed': False,
        'reasons': [
            'Risk score >= 85 (threshold for auto-stop)',
            'Multiple critical vulnerabilities detected',
            'Active exploits detected in the wild',
            'Historical FP rate is low (5%)'
        ]
    }
    
    decision_id = db.store_stop_decision(decision_data)
    print(f"✓ Stop decision stored with ID: {decision_id}")
    print(f"  - Resource: {decision_data['resource_name']}")
    print(f"  - Confidence: {decision_data['stop_confidence']:.2f}")
    print(f"  - Mode: {decision_data['mode']}\n")
    
    # 2. Execute the stop
    print("2. Executing resource stop...")
    execution_result = {
        'success': True,
        'message': 'Resource stopped successfully',
        'timestamp': datetime.now().isoformat(),
        'backup_created': True,
        'players_affected': 3,
        'rollback_available': True
    }
    
    db.update_stop_decision_execution(decision_id, True, execution_result)
    print(f"✓ Resource stopped successfully\n")
    
    # 3. Admin reviews and provides feedback
    print("3. Administrator reviews the decision...")
    feedback_data = {
        'decision_id': decision_id,
        'resource_name': 'bank_robbery',
        'feedback_type': 'auto_stop_review',
        'approved': True,
        'comment': 'Correct decision. Resource had multiple critical vulnerabilities that were being actively exploited.',
        'action_taken': 'kept_stopped',
        'outcome': 'true_positive'
    }
    
    feedback_id = db.store_admin_feedback(feedback_data)
    print(f"✓ Admin feedback stored with ID: {feedback_id}")
    print(f"  - Approved: {feedback_data['approved']}")
    print(f"  - Outcome: {feedback_data['outcome']}\n")
    
    # 4. Update statistics
    print("4. Updating statistics...")
    stats_data = {
        'metric_type': 'auto_stop',
        'true_positives': 46,  # Incremented from 45
        'false_positives': 5,
        'true_negatives': 30,
        'false_negatives': 2,
        'period_start': '2024-01-01 00:00:00',
        'period_end': datetime.now().isoformat()
    }
    
    stats_id = db.store_statistics(stats_data)
    latest_stats = db.get_latest_statistics('auto_stop')
    
    print(f"✓ Statistics updated (ID: {stats_id})")
    print(f"  - Precision: {latest_stats['precision']:.2%}")
    print(f"  - Recall: {latest_stats['recall']:.2%}")
    print(f"  - F1 Score: {latest_stats['f1_score']:.3f}")
    print(f"  - Accuracy: {latest_stats['accuracy']:.2%}\n")
    
    db.close()


def example_ml_training_data():
    """Example of retrieving data for ML training"""
    print("=" * 80)
    print("Example 3: Retrieving Data for ML Training")
    print("=" * 80)
    
    db = DatabaseManager("./data/example_ambani.db")
    db.connect()
    
    # Get historical analyses for training
    print("1. Retrieving historical analysis data...")
    historical_data = db.get_historical_analyses(limit=100)
    print(f"✓ Retrieved {len(historical_data)} historical analyses")
    
    if historical_data:
        print(f"\nSample analysis:")
        sample = historical_data[0]
        print(f"  - Resource: {sample['resource_name']}")
        print(f"  - Type: {sample['resource_type']}")
        print(f"  - Risk Score: {sample['risk_score']}")
        print(f"  - Vulnerabilities: {sample['vulnerabilities_count']}")
        print(f"  - Timestamp: {sample['timestamp']}\n")
    
    # Get feedback for learning
    print("2. Retrieving feedback for learning mode...")
    learning_data = db.get_feedback_for_learning()
    print(f"✓ Retrieved {len(learning_data)} decisions with feedback")
    
    if learning_data:
        print(f"\nSample feedback:")
        sample = learning_data[0]
        print(f"  - Resource: {sample['resource_name']}")
        print(f"  - Confidence: {sample['stop_confidence']:.2f}")
        print(f"  - Approved: {bool(sample['approved'])}")
        print(f"  - Outcome: {sample['outcome']}\n")
    
    # Calculate false positive rate
    print("3. Calculating false positive rate...")
    fp_rate = db.calculate_false_positive_rate()
    print(f"✓ Overall FP rate: {fp_rate:.2%}")
    
    # FP rate by resource type
    bank_fp_rate = db.calculate_false_positive_rate(resource_type='bank')
    print(f"✓ Bank resources FP rate: {bank_fp_rate:.2%}\n")
    
    db.close()


def example_anticheat_tracking():
    """Example of tracking anticheat detections"""
    print("=" * 80)
    print("Example 4: Anticheat Detection Tracking")
    print("=" * 80)
    
    db = DatabaseManager("./data/example_ambani.db")
    db.connect()
    
    # Store anticheat detection
    print("Storing anticheat detection...")
    detection_data = {
        'server_name': 'MyFiveMServer',
        'anticheat_name': 'FiveGuard',
        'anticheat_version': '2.5.1',
        'confidence': 0.95,
        'capabilities': [
            'event_injection_detection',
            'native_spoofing_detection',
            'aggressive_rate_limiting',
            'behavior_analysis'
        ],
        'bypass_difficulty': 0.85,
        'detection_method': 'signature_matching',
        'profile_data': {
            'monitors_resource_stops': True,
            'has_honeypots': True,
            'rate_limit_threshold': 5,
            'ban_on_detection': True
        }
    }
    
    detection_id = db.store_anticheat_detection(detection_data)
    print(f"✓ Anticheat detection stored with ID: {detection_id}")
    print(f"  - Name: {detection_data['anticheat_name']}")
    print(f"  - Version: {detection_data['anticheat_version']}")
    print(f"  - Confidence: {detection_data['confidence']:.2%}")
    print(f"  - Bypass Difficulty: {detection_data['bypass_difficulty']:.2%}\n")
    
    # Retrieve detections
    print("Retrieving anticheat detections...")
    detections = db.get_anticheat_detections(server_name='MyFiveMServer')
    print(f"✓ Found {len(detections)} anticheat(s) on server\n")
    
    for detection in detections:
        print(f"Anticheat: {detection['anticheat_name']}")
        print(f"  Capabilities: {', '.join(detection['capabilities'])}")
        print(f"  Profile: {json.dumps(detection['profile_data'], indent=2)}\n")
    
    db.close()


def example_statistics_tracking():
    """Example of tracking statistics over time"""
    print("=" * 80)
    print("Example 5: Statistics Tracking Over Time")
    print("=" * 80)
    
    db = DatabaseManager("./data/example_ambani.db")
    db.connect()
    
    # Store statistics for multiple periods
    print("Storing statistics for multiple periods...")
    periods = [
        {'month': 'January', 'tp': 45, 'fp': 5, 'tn': 30, 'fn': 2},
        {'month': 'February', 'tp': 52, 'fp': 4, 'tn': 35, 'fn': 1},
        {'month': 'March', 'tp': 58, 'fp': 3, 'tn': 40, 'fn': 1},
    ]
    
    for period in periods:
        stats_data = {
            'metric_type': 'auto_stop',
            'true_positives': period['tp'],
            'false_positives': period['fp'],
            'true_negatives': period['tn'],
            'false_negatives': period['fn']
        }
        db.store_statistics(stats_data)
    
    print(f"✓ Stored statistics for {len(periods)} periods\n")
    
    # Get statistics history
    print("Statistics History:")
    print("-" * 80)
    history = db.get_statistics_history('auto_stop', limit=3)
    
    for i, stats in enumerate(history, 1):
        print(f"\nPeriod {i}:")
        print(f"  TP: {stats['true_positives']}, FP: {stats['false_positives']}, "
              f"TN: {stats['true_negatives']}, FN: {stats['false_negatives']}")
        print(f"  Precision: {stats['precision']:.2%}")
        print(f"  Recall: {stats['recall']:.2%}")
        print(f"  F1 Score: {stats['f1_score']:.3f}")
        print(f"  Accuracy: {stats['accuracy']:.2%}")
    
    print()
    db.close()


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("DATABASE MODULE USAGE EXAMPLES")
    print("=" * 80 + "\n")
    
    try:
        example_basic_usage()
        print("\n")
        
        example_auto_stop_workflow()
        print("\n")
        
        example_ml_training_data()
        print("\n")
        
        example_anticheat_tracking()
        print("\n")
        
        example_statistics_tracking()
        print("\n")
        
        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
