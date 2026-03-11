"""
Tests for Auto Stop Engine with Professional Strategies
"""

import pytest
from ambani_integration.execution.auto_stop_engine import (
    AutoStopEngine, StopMode, ResourceClassification
)


class TestAutoStopEngine:
    """Test Auto Stop Engine functionality"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = AutoStopEngine(mode=StopMode.NOTIFY, confidence_threshold=0.7)
        
        assert engine.mode == StopMode.NOTIFY
        assert engine.confidence_threshold == 0.7
        assert engine.max_stops_per_minute == 3
        assert engine.grace_period_seconds == 300
        assert engine.learning_enabled is True
        assert isinstance(engine.professional_strategies, dict)
    
    def test_load_professional_strategies(self):
        """Test loading professional strategies from JSON"""
        engine = AutoStopEngine()
        
        # Should have loaded strategies
        assert len(engine.professional_strategies) > 0
        
        # Check for known anticheats
        assert 'FiveGuard' in engine.professional_strategies
        assert 'Phoenix AC' in engine.professional_strategies
        assert 'WaveShield' in engine.professional_strategies
        assert 'FireAC' in engine.professional_strategies
        assert 'BadgerAC' in engine.professional_strategies
        assert 'Qprotect' in engine.professional_strategies
        assert 'No Anticheat' in engine.professional_strategies
    
    def test_professional_recommendation_priority_stop(self):
        """Test professional recommendation for priority stop resources"""
        engine = AutoStopEngine()
        
        # Screenshot resource with FiveGuard
        rec = engine.get_professional_recommendation('screenshot_resource', 'FiveGuard')
        
        assert rec['recommended'] is True
        assert 'screenshot' in rec['reason'].lower()
        assert rec['detection_risk'] > 0.8
        assert len(rec['professional_tip']) > 0
    
    def test_professional_recommendation_never_stop(self):
        """Test professional recommendation for never-stop resources"""
        engine = AutoStopEngine()
        
        # Admin resource with FiveGuard (explicitly in never_stop list)
        rec = engine.get_professional_recommendation('admin_panel', 'FiveGuard')
        
        assert rec['recommended'] is False
        assert rec['detection_risk'] == 1.0  # Maximum risk for never_stop
        assert 'never stop' in rec['reason'].lower() or 'instant' in rec['professional_tip'].lower()
    
    def test_professional_recommendation_safe_stop(self):
        """Test professional recommendation for safe-stop resources"""
        engine = AutoStopEngine()
        
        # Cosmetic resource with WaveShield (very permissive)
        rec = engine.get_professional_recommendation('clothing_shop', 'WaveShield')
        
        assert rec['recommended'] is True
        assert rec['detection_risk'] < 0.5
    
    def test_professional_recommendation_no_anticheat(self):
        """Test professional recommendation with no anticheat"""
        engine = AutoStopEngine()
        
        # Any resource with no anticheat
        rec = engine.get_professional_recommendation('some_resource', None)
        
        assert 'No Anticheat' in rec['reason']
        assert rec['detection_risk'] < 0.3
    
    def test_classify_resource_with_professional_rules(self):
        """Test resource classification using professional rules"""
        engine = AutoStopEngine()
        
        # Critical resource (anticheat)
        classification = engine.classify_resource('fiveguard', [], 'FiveGuard')
        assert classification == ResourceClassification.CRITICAL
        
        # Safe resource with permissive anticheat
        classification = engine.classify_resource('clothing_shop', [], 'WaveShield')
        # Should not be critical
        assert classification != ResourceClassification.CRITICAL
    
    def test_classify_resource_critical_patterns(self):
        """Test classification of critical resources"""
        engine = AutoStopEngine()
        
        critical_resources = [
            'es_extended', 'qb-core', 'vrp', 'oxmysql',
            'txadmin', 'sessionmanager', 'fiveguard', 'phoenixac'
        ]
        
        for resource in critical_resources:
            classification = engine.classify_resource(resource, [])
            assert classification == ResourceClassification.CRITICAL
    
    def test_classify_resource_risky_patterns(self):
        """Test classification of risky resources"""
        engine = AutoStopEngine()
        
        risky_resources = [
            'banking_system', 'money_manager', 'admin_panel',
            'weapon_shop', 'inventory_system'
        ]
        
        for resource in risky_resources:
            classification = engine.classify_resource(resource, [])
            assert classification == ResourceClassification.RISKY
    
    def test_classify_resource_vulnerable(self):
        """Test classification of vulnerable resources"""
        engine = AutoStopEngine()
        
        # High risk triggers
        triggers = [
            {'risk_score': 0.8},
            {'risk_score': 0.9},
            {'risk_score': 0.85}
        ]
        
        classification = engine.classify_resource('some_resource', triggers)
        assert classification == ResourceClassification.VULNERABLE
    
    def test_classify_resource_safe(self):
        """Test classification of safe resources"""
        engine = AutoStopEngine()
        
        safe_resources = [
            'clothing_shop', 'barber_shop', 'hud_ui',
            'notification_system', 'tattoo_shop'
        ]
        
        for resource in safe_resources:
            classification = engine.classify_resource(resource, [])
            assert classification == ResourceClassification.SAFE
    
    def test_detect_stop_detection_logic(self):
        """Test detection of stop detection logic"""
        engine = AutoStopEngine()
        
        # Code with stop detection
        code_with_detection = """
        AddEventHandler('onResourceStop', function(resourceName)
            if resourceName == GetCurrentResourceName() then
                BanPlayer(source, 'Resource stopped')
            end
        end)
        """
        
        assert engine.detect_stop_detection_logic(code_with_detection) is True
        
        # Code without stop detection
        code_without_detection = """
        RegisterCommand('test', function(source, args)
            print('Test command')
        end)
        """
        
        assert engine.detect_stop_detection_logic(code_without_detection) is False
    
    def test_calculate_stop_confidence(self):
        """Test confidence score calculation"""
        engine = AutoStopEngine()
        
        # Vulnerable resource with high risk triggers
        triggers = [{'risk_score': 0.9}]
        code = "RegisterServerEvent('test')"
        
        confidence = engine.calculate_stop_confidence(
            'vulnerable_resource', triggers, code
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be relatively high
        
        # Critical resource should have 0 confidence
        confidence = engine.calculate_stop_confidence(
            'es_extended', [], code
        )
        
        assert confidence == 0.0
    
    def test_should_stop_resource_with_professional_approval(self):
        """Test stop decision with professional approval"""
        engine = AutoStopEngine(confidence_threshold=0.6)
        
        # Safe resource with WaveShield (permissive)
        triggers = [{'risk_score': 0.7}]
        code = "RegisterServerEvent('test')"
        
        decision = engine.should_stop_resource(
            'clothing_shop', triggers, code, 'WaveShield'
        )
        
        assert decision.resource_name == 'clothing_shop'
        assert isinstance(decision.should_stop, bool)
        assert 0.0 <= decision.confidence_score <= 1.0
        assert decision.classification in ResourceClassification
        assert len(decision.reasons) > 0
    
    def test_should_stop_resource_without_professional_approval(self):
        """Test stop decision without professional approval"""
        engine = AutoStopEngine(confidence_threshold=0.6)
        
        # Anticheat resource (never stop)
        triggers = [{'risk_score': 0.9}]
        code = "RegisterServerEvent('test')"
        
        decision = engine.should_stop_resource(
            'fiveguard', triggers, code, 'FiveGuard'
        )
        
        assert decision.should_stop is False
        assert decision.classification == ResourceClassification.CRITICAL
        assert decision.recommended_action == 'never_stop'
    
    def test_should_stop_resource_with_stop_detection(self):
        """Test stop decision when stop detection logic found"""
        engine = AutoStopEngine(confidence_threshold=0.6)
        
        triggers = [{'risk_score': 0.8}]
        code = """
        AddEventHandler('onResourceStop', function(resourceName)
            BanPlayer(source, 'Stopped')
        end)
        """
        
        decision = engine.should_stop_resource(
            'some_resource', triggers, code
        )
        
        assert decision.should_stop is False
        assert any('stop detection' in r.lower() for r in decision.reasons)
    
    def test_should_stop_resource_grace_period(self):
        """Test grace period prevents stopping"""
        engine = AutoStopEngine()
        
        # Register resource start
        engine.register_resource_start('new_resource')
        
        triggers = [{'risk_score': 0.9}]
        code = "RegisterServerEvent('test')"
        
        decision = engine.should_stop_resource(
            'new_resource', triggers, code
        )
        
        assert decision.should_stop is False
        assert any('grace period' in r.lower() for r in decision.reasons)
    
    def test_check_rate_limit(self):
        """Test rate limiting"""
        engine = AutoStopEngine()
        
        # Should allow first 3 stops
        for i in range(3):
            assert engine.check_rate_limit() is True
            engine.recent_stops.append(engine.recent_stops[-1] if engine.recent_stops else 
                                      __import__('datetime').datetime.now())
        
        # Should block 4th stop
        assert engine.check_rate_limit() is False
    
    def test_record_feedback(self):
        """Test feedback recording"""
        engine = AutoStopEngine()
        
        # Record correct decision
        engine.record_feedback('test_resource', was_correct=True, 
                             admin_comment='Good stop')
        
        assert len(engine.feedback_history) == 1
        assert engine.statistics.true_positives == 1
        
        # Record incorrect decision
        engine.record_feedback('test_resource2', was_correct=False,
                             admin_comment='Bad stop')
        
        assert len(engine.feedback_history) == 2
        assert engine.statistics.false_positives == 1
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        engine = AutoStopEngine()
        
        # Add some feedback
        engine.record_feedback('r1', True)
        engine.record_feedback('r2', True)
        engine.record_feedback('r3', False)
        
        stats = engine.get_statistics()
        
        assert stats['true_positives'] == 2
        assert stats['false_positives'] == 1
        assert 'precision' in stats
        assert 'recall' in stats
        assert 'f1_score' in stats
        assert stats['current_threshold'] == engine.confidence_threshold
    
    def test_statistics_precision_calculation(self):
        """Test precision calculation"""
        engine = AutoStopEngine()
        
        # 2 TP, 1 FP -> precision = 2/3 = 0.667
        engine.statistics.true_positives = 2
        engine.statistics.false_positives = 1
        
        assert abs(engine.statistics.precision - 0.667) < 0.01
    
    def test_statistics_recall_calculation(self):
        """Test recall calculation"""
        engine = AutoStopEngine()
        
        # 2 TP, 1 FN -> recall = 2/3 = 0.667
        engine.statistics.true_positives = 2
        engine.statistics.false_negatives = 1
        
        assert abs(engine.statistics.recall - 0.667) < 0.01
    
    def test_statistics_f1_score_calculation(self):
        """Test F1 score calculation"""
        engine = AutoStopEngine()
        
        # Precision = 0.8, Recall = 0.8 -> F1 = 0.8
        engine.statistics.true_positives = 4
        engine.statistics.false_positives = 1
        engine.statistics.false_negatives = 1
        
        assert abs(engine.statistics.f1_score - 0.8) < 0.01
    
    def test_threshold_adjustment_from_feedback(self):
        """Test threshold adjustment based on feedback"""
        engine = AutoStopEngine(confidence_threshold=0.7)
        
        # Add many false positives (low precision)
        for i in range(15):
            engine.record_feedback(f'r{i}', was_correct=(i % 5 == 0))
        
        # Threshold should increase to reduce false positives
        assert engine.confidence_threshold > 0.7
    
    def test_different_modes(self):
        """Test different operation modes"""
        # Manual mode
        manual_engine = AutoStopEngine(mode=StopMode.MANUAL)
        assert manual_engine.mode == StopMode.MANUAL
        
        # Notify mode
        notify_engine = AutoStopEngine(mode=StopMode.NOTIFY)
        assert notify_engine.mode == StopMode.NOTIFY
        
        # Auto mode
        auto_engine = AutoStopEngine(mode=StopMode.AUTO)
        assert auto_engine.mode == StopMode.AUTO
    
    def test_professional_strategies_fiveguard(self):
        """Test FiveGuard professional strategies"""
        engine = AutoStopEngine()
        
        strategy = engine.professional_strategies.get('FiveGuard', {})
        
        assert strategy['difficulty'] == 'EXTREME'
        assert strategy['detection_level'] == 'VERY_HIGH'
        assert 'priority_stops' in strategy
        assert 'never_stop' in strategy
        assert 'professional_workflow' in strategy
    
    def test_professional_strategies_waveshield(self):
        """Test WaveShield professional strategies"""
        engine = AutoStopEngine()
        
        strategy = engine.professional_strategies.get('WaveShield', {})
        
        assert strategy['difficulty'] == 'LOW'
        assert strategy['detection_level'] == 'MINIMAL'
        assert 'safe_stops' in strategy
    
    def test_professional_recommendation_integration(self):
        """Test that professional recommendations affect decisions"""
        engine = AutoStopEngine(confidence_threshold=0.6)
        
        # Test with FiveGuard (strict)
        triggers = [{'risk_score': 0.7}]
        code = "RegisterServerEvent('test')"
        
        decision_fiveguard = engine.should_stop_resource(
            'test_resource', triggers, code, 'FiveGuard'
        )
        
        # Test with WaveShield (permissive)
        decision_waveshield = engine.should_stop_resource(
            'test_resource', triggers, code, 'WaveShield'
        )
        
        # WaveShield should be more likely to allow stops
        # (or at least have different confidence/risk scores)
        assert decision_fiveguard.anticheat_risk != decision_waveshield.anticheat_risk or \
               decision_fiveguard.confidence_score != decision_waveshield.confidence_score


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
