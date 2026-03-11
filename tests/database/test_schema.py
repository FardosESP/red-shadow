"""
Tests for database schema
"""

import pytest
import os
import tempfile
from datetime import datetime
from ambani_integration.database import DatabaseManager, init_database


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db = DatabaseManager(path)
    db.init_schema()
    
    yield db
    
    db.close()
    os.unlink(path)


def test_init_database():
    """Test database initialization"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    try:
        db = init_database(path)
        assert db is not None
        assert os.path.exists(path)
        db.close()
    finally:
        os.unlink(path)


def test_store_analysis_result(temp_db):
    """Test storing analysis result"""
    analysis_data = {
        'server_name': 'TestServer',
        'resource_name': 'test_resource',
        'resource_type': 'bank',
        'risk_score': 85,
        'vulnerabilities_count': 3,
        'critical_vulns': 2,
        'high_vulns': 1,
        'medium_vulns': 0,
        'low_vulns': 0,
        'exploit_vectors': [
            {'type': 'event_injection', 'severity': 'CRITICAL'}
        ],
        'trigger_data': {
            'event_name': 'giveMoney',
            'has_validation': False
        }
    }
    
    record_id = temp_db.store_analysis_result(analysis_data)
    assert record_id > 0
    
    # Retrieve and verify
    results = temp_db.get_historical_analyses(limit=1)
    assert len(results) == 1
    assert results[0]['resource_name'] == 'test_resource'
    assert results[0]['risk_score'] == 85


def test_store_stop_decision(temp_db):
    """Test storing stop decision"""
    decision_data = {
        'resource_name': 'test_resource',
        'stop_confidence': 0.92,
        'risk_score': 95,
        'critical_vulns': 3,
        'active_exploits': True,
        'false_positive_rate': 0.05,
        'mode': 'auto',
        'requires_confirmation': False,
        'reasons': ['High risk score', 'Critical vulnerabilities']
    }
    
    decision_id = temp_db.store_stop_decision(decision_data)
    assert decision_id > 0
    
    # Retrieve and verify
    decisions = temp_db.get_stop_decisions(limit=1)
    assert len(decisions) == 1
    assert decisions[0]['resource_name'] == 'test_resource'
    assert decisions[0]['stop_confidence'] == 0.92


def test_store_admin_feedback(temp_db):
    """Test storing admin feedback"""
    # First create a decision
    decision_data = {
        'resource_name': 'test_resource',
        'stop_confidence': 0.85,
        'risk_score': 80,
        'critical_vulns': 2,
        'mode': 'auto'
    }
    decision_id = temp_db.store_stop_decision(decision_data)
    
    # Store feedback
    feedback_data = {
        'decision_id': decision_id,
        'resource_name': 'test_resource',
        'feedback_type': 'auto_stop_review',
        'approved': True,
        'comment': 'Correct decision',
        'action_taken': 'kept_stopped',
        'outcome': 'true_positive'
    }
    
    feedback_id = temp_db.store_admin_feedback(feedback_data)
    assert feedback_id > 0
    
    # Retrieve and verify
    feedback = temp_db.get_admin_feedback(decision_id=decision_id)
    assert len(feedback) == 1
    assert feedback[0]['approved'] == 1  # SQLite stores boolean as int
    assert feedback[0]['outcome'] == 'true_positive'


def test_store_anticheat_detection(temp_db):
    """Test storing anticheat detection"""
    detection_data = {
        'server_name': 'TestServer',
        'anticheat_name': 'FiveGuard',
        'anticheat_version': '2.0',
        'confidence': 0.95,
        'capabilities': ['event_injection_detection', 'native_spoofing_detection'],
        'bypass_difficulty': 0.85,
        'detection_method': 'signature_matching',
        'profile_data': {
            'aggressive_rate_limiting': True
        }
    }
    
    detection_id = temp_db.store_anticheat_detection(detection_data)
    assert detection_id > 0
    
    # Retrieve and verify
    detections = temp_db.get_anticheat_detections(server_name='TestServer')
    assert len(detections) == 1
    assert detections[0]['anticheat_name'] == 'FiveGuard'
    assert detections[0]['confidence'] == 0.95


def test_store_statistics(temp_db):
    """Test storing statistics"""
    stats_data = {
        'metric_type': 'auto_stop',
        'true_positives': 45,
        'false_positives': 5,
        'true_negatives': 30,
        'false_negatives': 2
    }
    
    stats_id = temp_db.store_statistics(stats_data)
    assert stats_id > 0
    
    # Retrieve and verify
    latest_stats = temp_db.get_latest_statistics('auto_stop')
    assert latest_stats is not None
    assert latest_stats['true_positives'] == 45
    assert latest_stats['false_positives'] == 5
    
    # Check calculated metrics
    assert latest_stats['precision'] > 0
    assert latest_stats['recall'] > 0
    assert latest_stats['f1_score'] > 0
    assert latest_stats['accuracy'] > 0


def test_calculate_false_positive_rate(temp_db):
    """Test calculating false positive rate"""
    # Create decisions with feedback
    for i in range(10):
        decision_data = {
            'resource_name': f'resource_{i}',
            'stop_confidence': 0.8,
            'risk_score': 80,
            'mode': 'auto'
        }
        decision_id = temp_db.store_stop_decision(decision_data)
        
        # 2 out of 10 are false positives
        approved = i >= 2
        feedback_data = {
            'decision_id': decision_id,
            'resource_name': f'resource_{i}',
            'feedback_type': 'review',
            'approved': approved,
            'outcome': 'true_positive' if approved else 'false_positive'
        }
        temp_db.store_admin_feedback(feedback_data)
    
    fp_rate = temp_db.calculate_false_positive_rate()
    assert fp_rate == 0.2  # 2/10 = 0.2


def test_get_feedback_for_learning(temp_db):
    """Test getting feedback for ML learning"""
    # Create decision with feedback
    decision_data = {
        'resource_name': 'test_resource',
        'stop_confidence': 0.9,
        'risk_score': 90,
        'critical_vulns': 3,
        'mode': 'auto'
    }
    decision_id = temp_db.store_stop_decision(decision_data)
    
    feedback_data = {
        'decision_id': decision_id,
        'resource_name': 'test_resource',
        'feedback_type': 'review',
        'approved': True,
        'outcome': 'true_positive'
    }
    temp_db.store_admin_feedback(feedback_data)
    
    # Get learning data
    learning_data = temp_db.get_feedback_for_learning()
    assert len(learning_data) == 1
    assert learning_data[0]['resource_name'] == 'test_resource'
    assert learning_data[0]['approved'] == 1


def test_update_stop_decision_execution(temp_db):
    """Test updating stop decision execution status"""
    decision_data = {
        'resource_name': 'test_resource',
        'stop_confidence': 0.9,
        'risk_score': 90,
        'mode': 'auto',
        'executed': False
    }
    decision_id = temp_db.store_stop_decision(decision_data)
    
    # Update execution status
    execution_result = {
        'success': True,
        'message': 'Resource stopped successfully'
    }
    temp_db.update_stop_decision_execution(decision_id, True, execution_result)
    
    # Verify update
    decisions = temp_db.get_stop_decisions(resource_name='test_resource')
    assert len(decisions) == 1
    assert decisions[0]['executed'] == 1
    assert decisions[0]['execution_result']['success'] is True


def test_statistics_history(temp_db):
    """Test getting statistics history"""
    # Store multiple statistics
    for i in range(5):
        stats_data = {
            'metric_type': 'auto_stop',
            'true_positives': 40 + i,
            'false_positives': 5,
            'true_negatives': 30,
            'false_negatives': 2
        }
        temp_db.store_statistics(stats_data)
    
    # Get history
    history = temp_db.get_statistics_history('auto_stop', limit=3)
    assert len(history) == 3
    # Should be in descending order
    assert history[0]['true_positives'] == 44
    assert history[1]['true_positives'] == 43
    assert history[2]['true_positives'] == 42
