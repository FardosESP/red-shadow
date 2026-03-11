"""
Tests for Event Analyzer
"""

import pytest
import json
import tempfile
import os
from ambani_integration.intelligence.event_analyzer import EventAnalyzer, FarmingStrategy


@pytest.fixture
def sample_captured_data():
    """Sample captured events data"""
    return {
        "sessionStart": 1234567890,
        "sessionEnd": 1234571490,
        "sessionDuration": 3600,
        "totalEvents": 25,
        "uniqueEvents": 3,
        "jobEvents": 2,
        "rewardEvents": 2,
        "events": [
            {
                "name": "job:taxi:payment",
                "params": [500],
                "timestamp": "2024-01-01 10:00:00",
                "gameTime": 1000,
                "rewardType": "money",
                "rewardAmount": 500,
                "isJob": True
            },
            {
                "name": "job:taxi:payment",
                "params": [500],
                "timestamp": "2024-01-01 10:05:00",
                "gameTime": 6000,
                "rewardType": "money",
                "rewardAmount": 500,
                "isJob": True
            },
            {
                "name": "job:delivery:complete",
                "params": [300],
                "timestamp": "2024-01-01 10:10:00",
                "gameTime": 11000,
                "rewardType": "money",
                "rewardAmount": 300,
                "isJob": True
            }
        ],
        "stats": [
            {
                "name": "job:taxi:payment",
                "count": 10,
                "totalReward": 5000,
                "avgReward": 500,
                "isJob": True,
                "rewardType": "money",
                "firstSeen": 1234567890,
                "lastSeen": 1234571490,
                "duration": 3600
            },
            {
                "name": "job:delivery:complete",
                "count": 8,
                "totalReward": 2400,
                "avgReward": 300,
                "isJob": True,
                "rewardType": "money",
                "firstSeen": 1234567890,
                "lastSeen": 1234571490,
                "duration": 3600
            },
            {
                "name": "admin:log",
                "count": 7,
                "totalReward": 0,
                "avgReward": 0,
                "isJob": False,
                "rewardType": None,
                "firstSeen": 1234567890,
                "lastSeen": 1234571490,
                "duration": 3600
            }
        ]
    }


@pytest.fixture
def analyzer():
    """Create EventAnalyzer instance"""
    return EventAnalyzer()


def test_load_captured_data(analyzer, sample_captured_data):
    """Test loading captured data from JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_captured_data, f)
        temp_file = f.name
    
    try:
        success = analyzer.load_captured_data(temp_file)
        assert success
        assert analyzer.captured_data is not None
        assert analyzer.captured_data['totalEvents'] == 25
        assert analyzer.captured_data['uniqueEvents'] == 3
    finally:
        os.unlink(temp_file)


def test_load_invalid_file(analyzer):
    """Test loading non-existent file"""
    success = analyzer.load_captured_data("nonexistent.json")
    assert not success


def test_analyze_farming_opportunities(analyzer, sample_captured_data):
    """Test analyzing farming opportunities"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_captured_data, f)
        temp_file = f.name
    
    try:
        analyzer.load_captured_data(temp_file)
        strategies = analyzer.analyze_farming_opportunities(
            min_sample_size=5,
            min_success_rate=0.7,
            min_confidence=0.8
        )
        
        assert len(strategies) == 2  # taxi and delivery
        
        # Check taxi strategy (should be first - higher profit)
        taxi = strategies[0]
        assert taxi.event_name == "job:taxi:payment"
        assert taxi.avg_reward == 500
        assert taxi.reward_type == "money"
        assert taxi.sample_size == 10
        assert taxi.profit_per_hour > 0
        
        # Check delivery strategy
        delivery = strategies[1]
        assert delivery.event_name == "job:delivery:complete"
        assert delivery.avg_reward == 300
        
    finally:
        os.unlink(temp_file)


def test_filter_by_sample_size(analyzer, sample_captured_data):
    """Test filtering by minimum sample size"""
    # Modify data to have small sample
    sample_captured_data['stats'][0]['count'] = 2
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_captured_data, f)
        temp_file = f.name
    
    try:
        analyzer.load_captured_data(temp_file)
        strategies = analyzer.analyze_farming_opportunities(
            min_sample_size=5
        )
        
        # Should only get delivery (8 samples)
        assert len(strategies) == 1
        assert strategies[0].event_name == "job:delivery:complete"
        
    finally:
        os.unlink(temp_file)


def test_calculate_confidence(analyzer):
    """Test confidence calculation"""
    assert analyzer._calculate_confidence(50) == 0.95
    assert analyzer._calculate_confidence(20) == 0.90
    assert analyzer._calculate_confidence(10) == 0.85
    assert analyzer._calculate_confidence(5) == 0.80
    assert analyzer._calculate_confidence(3) == 0.70


def test_calculate_detection_risk(analyzer):
    """Test detection risk calculation"""
    # Low risk: long cooldown, low reward
    risk1 = analyzer._calculate_detection_risk("job:taxi:payment", 120, 100)
    assert risk1 < 0.5
    
    # High risk: short cooldown, high reward
    risk2 = analyzer._calculate_detection_risk("job:money:give", 20, 15000)
    assert risk2 > 0.5
    
    # Medium risk: validation keyword
    risk3 = analyzer._calculate_detection_risk("job:verify:payment", 60, 500)
    assert risk3 > 0.4


def test_export_strategies(analyzer, sample_captured_data):
    """Test exporting strategies to JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_captured_data, f)
        temp_file = f.name
    
    output_file = tempfile.mktemp(suffix='.json')
    
    try:
        analyzer.load_captured_data(temp_file)
        analyzer.analyze_farming_opportunities()
        analyzer.export_strategies_for_lua(output_file)
        
        # Verify output file
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert 'generated' in data
        assert 'total_strategies' in data
        assert 'strategies' in data
        assert len(data['strategies']) == 2
        
        # Check strategy format
        strategy = data['strategies'][0]
        assert 'event' in strategy
        assert 'params' in strategy
        assert 'avgReward' in strategy
        assert 'cooldown' in strategy
        assert 'detectionRisk' in strategy
        assert 'profitPerHour' in strategy
        
    finally:
        os.unlink(temp_file)
        if os.path.exists(output_file):
            os.unlink(output_file)


def test_get_statistics(analyzer, sample_captured_data):
    """Test getting statistics"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_captured_data, f)
        temp_file = f.name
    
    try:
        analyzer.load_captured_data(temp_file)
        analyzer.analyze_farming_opportunities()
        
        stats = analyzer.get_statistics()
        
        assert stats['total_events'] == 25
        assert stats['unique_events'] == 3
        assert stats['job_events'] == 2
        assert stats['reward_events'] == 2
        assert stats['farming_strategies'] == 2
        assert stats['avg_profit_per_hour'] > 0
        
    finally:
        os.unlink(temp_file)


def test_no_job_events_filtered(analyzer):
    """Test that non-job events are filtered out"""
    data = {
        "totalEvents": 5,
        "uniqueEvents": 1,
        "stats": [
            {
                "name": "admin:log",
                "count": 5,
                "totalReward": 0,
                "avgReward": 0,
                "isJob": False,
                "rewardType": None,
                "duration": 300
            }
        ],
        "events": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name
    
    try:
        analyzer.load_captured_data(temp_file)
        strategies = analyzer.analyze_farming_opportunities()
        
        assert len(strategies) == 0
        
    finally:
        os.unlink(temp_file)


def test_no_rewards_filtered(analyzer):
    """Test that events without rewards are filtered"""
    data = {
        "totalEvents": 5,
        "uniqueEvents": 1,
        "stats": [
            {
                "name": "job:taxi:start",
                "count": 5,
                "totalReward": 0,
                "avgReward": 0,
                "isJob": True,
                "rewardType": None,
                "duration": 300
            }
        ],
        "events": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name
    
    try:
        analyzer.load_captured_data(temp_file)
        strategies = analyzer.analyze_farming_opportunities()
        
        assert len(strategies) == 0
        
    finally:
        os.unlink(temp_file)
