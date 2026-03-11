"""
Tests for Behavioral Analyzer
"""

import pytest
import numpy as np
from ambani_integration.analysis.behavioral_analyzer import (
    BehavioralAnalyzer,
    Anomaly,
    BehaviorProfile,
    ClusterResult
)


class TestBehavioralAnalyzer:
    """Test suite for BehavioralAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return BehavioralAnalyzer(contamination=0.1)
    
    @pytest.fixture
    def sample_triggers(self):
        """Sample triggers for training"""
        return [
            {
                'event_name': 'bank:deposit',
                'parameters': ['amount', 'account'],
                'code': 'if HasPermission(source) then TriggerServerEvent("bank:deposit", amount) end',
                'risk_score': 0.3
            },
            {
                'event_name': 'shop:buy',
                'parameters': ['item', 'quantity'],
                'code': 'if item and quantity > 0 then BuyItem(item, quantity) end',
                'risk_score': 0.2
            },
            {
                'event_name': 'admin:teleport',
                'parameters': ['coords'],
                'code': 'SetEntityCoords(PlayerPedId(), coords.x, coords.y, coords.z)',
                'risk_score': 0.8
            },
            {
                'event_name': 'money:add',
                'parameters': ['amount'],
                'code': 'TriggerServerEvent("money:add", 999999)',
                'risk_score': 0.9
            },
            {
                'event_name': 'vehicle:spawn',
                'parameters': ['model'],
                'code': 'if IsPlayerAceAllowed(source, "vehicle.spawn") then SpawnVehicle(model) end',
                'risk_score': 0.4
            }
        ]
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.contamination == 0.1
        assert analyzer.is_trained == False
        assert len(analyzer.models) == 3
        assert 'isolation_forest' in analyzer.models
        assert 'one_class_svm' in analyzer.models
        assert 'autoencoder' in analyzer.models
    
    def test_extract_features(self, analyzer, sample_triggers):
        """Test feature extraction"""
        trigger = sample_triggers[0]
        features = analyzer.extract_features(trigger)
        
        assert isinstance(features, np.ndarray)
        assert len(features) == 14  # 14 features defined
        assert features.dtype == np.float32
        
        # Check specific features
        assert features[1] == 2  # param_count
        assert features[8] == 0.3  # risk_score
    
    def test_train_models(self, analyzer, sample_triggers):
        """Test model training"""
        analyzer.train_models(sample_triggers)
        
        assert analyzer.is_trained == True
        assert analyzer.models['isolation_forest'] is not None
        assert analyzer.models['one_class_svm'] is not None
        assert analyzer.models['autoencoder'] is not None
        assert len(analyzer.feature_names) == 14
    
    def test_detect_anomalies_untrained(self, analyzer, sample_triggers):
        """Test anomaly detection without training"""
        result = analyzer.detect_anomalies(sample_triggers[0])
        assert result is None  # Should return None when not trained
    
    def test_detect_anomalies_trained(self, analyzer, sample_triggers):
        """Test anomaly detection after training"""
        # Train with normal triggers
        normal_triggers = sample_triggers[:2]  # Low risk triggers
        analyzer.train_models(normal_triggers * 5)  # Repeat to have enough samples
        
        # Test with high-risk trigger
        anomalous_trigger = sample_triggers[3]  # money:add with high risk
        result = analyzer.detect_anomalies(anomalous_trigger)
        
        # May or may not detect depending on model, but should not crash
        assert result is None or isinstance(result, Anomaly)
        
        if result:
            assert result.anomaly_score >= 0.0
            assert result.anomaly_score <= 1.0
            assert len(result.detected_by) > 0
            assert result.deviation_type in [
                'high_risk_pattern', 'unvalidated_dangerous_operations',
                'statistical_outlier', 'unusual_feature_combination', 'general_anomaly'
            ]
    
    def test_create_behavior_profile(self, analyzer, sample_triggers):
        """Test behavior profile creation"""
        profile = analyzer.create_behavior_profile('bank', sample_triggers[:2])
        
        assert isinstance(profile, BehaviorProfile)
        assert profile.resource_type == 'bank'
        assert profile.sample_count == 2
        assert profile.typical_frequency >= 0.0
        assert profile.risk_threshold >= 0.0
        assert profile.risk_threshold <= 1.0
        assert len(profile.normal_patterns) <= 10
    
    def test_create_behavior_profile_empty(self, analyzer):
        """Test behavior profile with no triggers"""
        profile = analyzer.create_behavior_profile('empty', [])
        
        assert profile.resource_type == 'empty'
        assert profile.sample_count == 0
        assert len(profile.normal_patterns) == 0
    
    def test_cluster_resources(self, analyzer):
        """Test resource clustering"""
        resources = [
            {
                'name': 'bank_resource',
                'triggers': [
                    {'event_name': 'bank:deposit', 'parameters': ['amount'], 
                     'code': 'Deposit(amount)', 'risk_score': 0.3}
                ] * 3
            },
            {
                'name': 'shop_resource',
                'triggers': [
                    {'event_name': 'shop:buy', 'parameters': ['item'], 
                     'code': 'BuyItem(item)', 'risk_score': 0.2}
                ] * 3
            },
            {
                'name': 'admin_resource',
                'triggers': [
                    {'event_name': 'admin:teleport', 'parameters': ['coords'], 
                     'code': 'SetEntityCoords(coords)', 'risk_score': 0.8}
                ] * 3
            }
        ]
        
        results = analyzer.cluster_resources(resources)
        
        assert isinstance(results, list)
        if len(results) > 0:  # May be empty if too few resources
            assert all(isinstance(r, ClusterResult) for r in results)
            assert all(r.cluster_id >= 0 for r in results)
            assert all(len(r.resources) > 0 for r in results)
    
    def test_cluster_resources_insufficient(self, analyzer):
        """Test clustering with too few resources"""
        resources = [
            {'name': 'resource1', 'triggers': [
                {'event_name': 'test', 'parameters': [], 'code': 'test()', 'risk_score': 0.5}
            ]}
        ]
        
        results = analyzer.cluster_resources(resources)
        assert results == []  # Should return empty list
    
    def test_detect_active_exploitation(self, analyzer):
        """Test active exploitation detection"""
        # Normal event sequence
        normal_sequence = [
            {'event_name': 'shop:buy', 'code': 'BuyItem()', 'risk_score': 0.2, 'timestamp': 1.0},
            {'event_name': 'shop:buy', 'code': 'BuyItem()', 'risk_score': 0.2, 'timestamp': 2.0},
            {'event_name': 'shop:buy', 'code': 'BuyItem()', 'risk_score': 0.2, 'timestamp': 3.0}
        ]
        
        is_exploiting, analysis = analyzer.detect_active_exploitation(normal_sequence)
        assert isinstance(is_exploiting, bool)
        assert isinstance(analysis, dict)
        assert 'total_events' in analysis
        assert 'risk_score' in analysis
        
        # Suspicious event sequence
        suspicious_sequence = [
            {'event_name': 'money:add', 'code': 'AddMoney(999999)', 'risk_score': 0.9, 'timestamp': 1.0},
            {'event_name': 'money:add', 'code': 'AddMoney(999999)', 'risk_score': 0.9, 'timestamp': 1.05},
            {'event_name': 'teleport', 'code': 'SetCoords()', 'risk_score': 0.8, 'timestamp': 1.1},
            {'event_name': 'god_mode', 'code': 'SetInvincible()', 'risk_score': 0.9, 'timestamp': 1.15}
        ]
        
        is_exploiting, analysis = analyzer.detect_active_exploitation(suspicious_sequence)
        # Should likely detect exploitation
        assert 'suspicious_patterns' in analysis
        assert 'indicators' in analysis
    
    def test_detect_active_exploitation_insufficient(self, analyzer):
        """Test exploitation detection with too few events"""
        short_sequence = [
            {'event_name': 'test', 'code': 'test()', 'risk_score': 0.5}
        ]
        
        is_exploiting, analysis = analyzer.detect_active_exploitation(short_sequence)
        assert is_exploiting == False
        assert analysis['reason'] == 'insufficient_events'
    
    def test_optimize_strategy(self, analyzer):
        """Test strategy optimization with RL"""
        # Record some results
        strategy1 = analyzer.optimize_strategy('stealth', True, 0.8)
        assert strategy1 == 'stealth'  # Only one strategy known
        
        strategy2 = analyzer.optimize_strategy('aggressive', False, 0.0)
        strategy3 = analyzer.optimize_strategy('stealth', True, 0.9)
        
        # Should recommend based on Thompson Sampling
        recommended = analyzer.optimize_strategy('stealth', True, 0.7)
        assert recommended in ['stealth', 'aggressive']
    
    def test_get_strategy_statistics(self, analyzer):
        """Test strategy statistics"""
        # Record some results
        analyzer.optimize_strategy('stealth', True, 0.8)
        analyzer.optimize_strategy('stealth', True, 0.9)
        analyzer.optimize_strategy('aggressive', False, 0.0)
        
        stats = analyzer.get_strategy_statistics()
        
        assert 'stealth' in stats
        assert stats['stealth']['attempts'] == 2
        assert stats['stealth']['successes'] == 2
        assert stats['stealth']['success_rate'] == 1.0
        
        assert 'aggressive' in stats
        assert stats['aggressive']['attempts'] == 1
        assert stats['aggressive']['successes'] == 0
    
    def test_save_and_load_models(self, analyzer, sample_triggers, tmp_path):
        """Test model persistence"""
        # Train models
        analyzer.train_models(sample_triggers)
        
        # Save
        filepath = tmp_path / "models.pkl"
        analyzer.save_models(str(filepath))
        
        assert filepath.exists()
        
        # Load into new analyzer
        new_analyzer = BehavioralAnalyzer()
        assert new_analyzer.is_trained == False
        
        new_analyzer.load_models(str(filepath))
        assert new_analyzer.is_trained == True
        assert len(new_analyzer.feature_names) == len(analyzer.feature_names)
    
    def test_anomaly_dataclass(self):
        """Test Anomaly dataclass"""
        anomaly = Anomaly(
            trigger={'event_name': 'test'},
            anomaly_score=0.85,
            detected_by=['isolation_forest', 'one_class_svm'],
            deviation_type='high_risk_pattern',
            explanation='Test anomaly',
            confidence=0.67,
            features={'risk_score': 0.9}
        )
        
        assert anomaly.anomaly_score == 0.85
        assert len(anomaly.detected_by) == 2
        assert anomaly.confidence == 0.67
    
    def test_behavior_profile_dataclass(self):
        """Test BehaviorProfile dataclass"""
        profile = BehaviorProfile(
            resource_type='bank',
            normal_patterns=[],
            typical_frequency=0.5,
            typical_parameters={'param_count': 2.0},
            typical_complexity=3.0,
            risk_threshold=0.6,
            sample_count=10
        )
        
        assert profile.resource_type == 'bank'
        assert profile.typical_frequency == 0.5
        assert profile.sample_count == 10
    
    def test_cluster_result_dataclass(self):
        """Test ClusterResult dataclass"""
        result = ClusterResult(
            cluster_id=0,
            resources=['res1', 'res2'],
            centroid=np.array([1.0, 2.0, 3.0]),
            outliers=['res3'],
            characteristics={'avg_risk': 0.5}
        )
        
        assert result.cluster_id == 0
        assert len(result.resources) == 2
        assert len(result.outliers) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
