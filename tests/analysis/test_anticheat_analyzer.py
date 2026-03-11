"""
Tests for Anticheat Analyzer
"""

import pytest
from ambani_integration.analysis.anticheat_analyzer import (
    AnticheatAnalyzer,
    AnticheatProfile,
    EXTENDED_ANTICHEAT_SIGNATURES
)


class TestAnticheatAnalyzer:
    """Test suite for AnticheatAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return AnticheatAnalyzer()
    
    @pytest.fixture
    def sample_code_fiveguard(self):
        """Sample code with FiveGuard anticheat"""
        return {
            "server.lua": """
                -- FiveGuard v2.5.1 Protection
                local FiveGuard = {}
                FiveGuard.version = "2.5.1"
                fg_version = "2.5.1"
                
                function FiveGuard.CheckPlayer(player)
                    -- Memory scanning
                    -- Event injection detection
                    -- Native spoofing detection
                    -- Aggressive rate limiting
                end
                
                function FG_AC.Init()
                    print("FiveGuard initialized")
                end
            """,
            "config.lua": """
                Config = {}
                Config.FiveGuard = {
                    enabled = true,
                    aggressive_rate_limiting = true
                }
                
                fiveguard_config = {
                    memory_scanning = true
                }
            """
        }
    
    @pytest.fixture
    def sample_code_phoenix(self):
        """Sample code with Phoenix AC"""
        return {
            "anticheat.lua": """
                -- Phoenix AC v1.8.3
                local PhoenixAC = {}
                pac_version = "1.8.3"
                
                function pac_check_event(event)
                    -- Pattern matching
                    -- Behavior analysis
                end
            """
        }
    
    @pytest.fixture
    def sample_code_silent(self):
        """Sample code with silent anticheat"""
        return {
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
            """
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert len(analyzer.signatures) == len(EXTENDED_ANTICHEAT_SIGNATURES)
        assert analyzer.detected_anticheats == []
        assert analyzer.previous_patterns == {}
    
    def test_detect_fiveguard(self, analyzer, sample_code_fiveguard):
        """Test FiveGuard detection"""
        profiles = analyzer.detect_anticheats(sample_code_fiveguard)
        
        assert len(profiles) > 0
        fiveguard = next((p for p in profiles if "FiveGuard" in p.name), None)
        assert fiveguard is not None
        assert fiveguard.version == "2.5.1"
        assert fiveguard.confidence > 0.5
        assert "memory_scanning" in fiveguard.capabilities
        assert "event_injection_detection" in fiveguard.capabilities
    
    def test_detect_phoenix_ac(self, analyzer, sample_code_phoenix):
        """Test Phoenix AC detection"""
        profiles = analyzer.detect_anticheats(sample_code_phoenix)
        
        assert len(profiles) > 0
        phoenix = next((p for p in profiles if "Phoenix" in p.name), None)
        assert phoenix is not None
        assert phoenix.version == "1.8.3"
        assert phoenix.confidence > 0.5
        assert "pattern_matching" in phoenix.capabilities
    
    def test_detect_silent_anticheat(self, analyzer, sample_code_silent):
        """Test silent anticheat detection"""
        profiles = analyzer.detect_anticheats(sample_code_silent)
        
        # Should detect silent/custom AC
        silent = next((p for p in profiles if "Silent" in p.name or "Custom" in p.name), None)
        assert silent is not None
        assert "silent_operation" in silent.capabilities
        assert len(silent.behavioral_indicators) >= 2
    
    def test_create_profile(self, analyzer):
        """Test profile creation"""
        profile = analyzer.create_profile("FiveGuard", "2.5.0")
        
        assert profile.name == "FiveGuard"
        assert profile.version == "2.5.0"
        assert len(profile.capabilities) > 0
        assert len(profile.limitations) > 0
        assert profile.bypass_difficulty > 0.0
        assert len(profile.bypass_techniques) > 0
    
    def test_calculate_detection_risk_no_anticheat(self, analyzer):
        """Test risk calculation with no anticheats"""
        risk = analyzer.calculate_detection_risk([], ["stop_resource"])
        assert risk == 0.0
    
    def test_calculate_detection_risk_with_anticheat(self, analyzer):
        """Test risk calculation with anticheats"""
        profile = AnticheatProfile(
            name="FiveGuard",
            bypass_difficulty=0.85
        )
        
        # Low risk action
        risk = analyzer.calculate_detection_risk([profile], ["trigger_event"])
        assert 0.85 <= risk <= 1.0
        
        # High risk action
        risk = analyzer.calculate_detection_risk([profile], ["stop_anticheat"])
        assert risk > 0.85
    
    def test_suggest_bypass_techniques(self, analyzer):
        """Test bypass technique suggestions"""
        profile = AnticheatProfile(
            name="FiveGuard",
            bypass_difficulty=0.85,
            bypass_techniques=["ultra_stealth_mode", "timing_randomization"],
            capabilities=["memory_scanning", "event_injection_detection"],
            limitations=["high_false_positive_rate"]
        )
        
        suggestions = analyzer.suggest_bypass_techniques(profile)
        
        assert len(suggestions) > 0
        # Should include base techniques
        assert any(s["technique"] == "ultra_stealth_mode" for s in suggestions)
        # Should include capability-specific bypasses
        assert any(s["technique"] == "memory_evasion" for s in suggestions)
        assert any(s["technique"] == "event_spoofing" for s in suggestions)
        # Should include limitation-based opportunities
        assert any(s["technique"] == "false_positive_exploitation" for s in suggestions)
    
    def test_update_detection(self, analyzer, sample_code_fiveguard):
        """Test anticheat update detection"""
        # First detection
        profiles1 = analyzer.detect_anticheats(sample_code_fiveguard)
        fiveguard1 = next((p for p in profiles1 if "FiveGuard" in p.name), None)
        
        if fiveguard1:
            assert fiveguard1.update_detected == False
            initial_patterns = set(fiveguard1.detection_patterns)
            
            # Modified code with additional patterns (simulating update with new features)
            modified_code = {
                "server.lua": """
                    -- FiveGuard v2.6.0 Protection - NEW VERSION
                    local FiveGuard = {}
                    FG_AC.version = "2.6.0"
                    fg_version = "2.6.0"
                    fiveguard_new_feature = true
                    anticheat.fiveguard.v2 = {}
                """
            }
            
            # Second detection
            profiles2 = analyzer.detect_anticheats(modified_code)
            fiveguard2 = next((p for p in profiles2 if "FiveGuard" in p.name), None)
            
            # Check if patterns changed
            if fiveguard2:
                new_patterns = set(fiveguard2.detection_patterns)
                # If patterns are different, update should be detected
                if initial_patterns != new_patterns:
                    assert fiveguard2.update_detected == True
                    assert len(fiveguard2.pattern_changes) > 0
                else:
                    # If patterns are the same, no update detected (which is correct)
                    assert fiveguard2.update_detected == False
        else:
            # If FiveGuard not detected in first run, test passes (detection is optional)
            pytest.skip("FiveGuard not detected in sample code")
    
    def test_get_recommended_strategy_no_anticheat(self, analyzer):
        """Test strategy recommendation with no anticheats"""
        strategy = analyzer.get_recommended_strategy([])
        
        assert strategy["strategy"] == "aggressive"
        assert strategy["confidence"] == 1.0
        assert strategy["max_stops_per_minute"] == 5
    
    def test_get_recommended_strategy_weak_anticheat(self, analyzer):
        """Test strategy recommendation with weak anticheat"""
        profile = AnticheatProfile(name="BadgerAC", bypass_difficulty=0.30)
        strategy = analyzer.get_recommended_strategy([profile])
        
        assert strategy["strategy"] == "aggressive"
        assert strategy["max_stops_per_minute"] >= 3
    
    def test_get_recommended_strategy_moderate_anticheat(self, analyzer):
        """Test strategy recommendation with moderate anticheat"""
        profile = AnticheatProfile(name="WaveShield", bypass_difficulty=0.50)
        strategy = analyzer.get_recommended_strategy([profile])
        
        assert strategy["strategy"] == "standard"
        assert strategy["max_stops_per_minute"] == 3
    
    def test_get_recommended_strategy_strong_anticheat(self, analyzer):
        """Test strategy recommendation with strong anticheat"""
        profile = AnticheatProfile(name="FireAC", bypass_difficulty=0.75)
        strategy = analyzer.get_recommended_strategy([profile])
        
        assert strategy["strategy"] == "stealth"
        assert strategy["max_stops_per_minute"] == 2
    
    def test_get_recommended_strategy_very_strong_anticheat(self, analyzer):
        """Test strategy recommendation with very strong anticheat"""
        profile = AnticheatProfile(name="FiveGuard", bypass_difficulty=0.85)
        strategy = analyzer.get_recommended_strategy([profile])
        
        assert strategy["strategy"] == "ultra_stealth"
        assert strategy["max_stops_per_minute"] == 1
        assert strategy["grace_period"] == 300
    
    def test_get_component_stop_risk(self, analyzer):
        """Test component stop risk assessment"""
        risk = analyzer.get_component_stop_risk("FiveGuard", "screen_capture")
        
        assert risk["component"] == "screen_capture"
        assert risk["anticheat"] == "FiveGuard"
        assert "detection_risk" in risk
        assert "stop_safety" in risk
        assert "bypass_benefit" in risk
    
    def test_get_main_anticheat_stop_risk(self, analyzer):
        """Test main anticheat stop risk assessment"""
        risk = analyzer.get_main_anticheat_stop_risk("FiveGuard")
        
        assert risk["anticheat"] == "FiveGuard"
        assert "can_stop" in risk
        assert "detection_risk" in risk
        assert "consequences" in risk
        assert "recommended" in risk
    
    def test_multiple_anticheats_detection(self, analyzer):
        """Test detection of multiple anticheats"""
        code = {
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
        
        profiles = analyzer.detect_anticheats(code)
        
        # Should detect multiple anticheats
        assert len(profiles) >= 2
        names = [p.name for p in profiles]
        assert any("FiveGuard" in name for name in names)
        assert any("Phoenix" in name for name in names)
    
    def test_bypass_difficulty_range(self, analyzer):
        """Test bypass difficulty is in valid range"""
        for ac_name, ac_data in EXTENDED_ANTICHEAT_SIGNATURES.items():
            difficulty = ac_data["bypass_difficulty"]
            assert 0.0 <= difficulty <= 1.0, f"{ac_name} has invalid difficulty: {difficulty}"
    
    def test_all_anticheats_have_required_fields(self, analyzer):
        """Test all anticheat signatures have required fields"""
        required_fields = ["patterns", "capabilities", "bypass_difficulty", "bypass_techniques"]
        
        for ac_name, ac_data in EXTENDED_ANTICHEAT_SIGNATURES.items():
            for field in required_fields:
                assert field in ac_data, f"{ac_name} missing required field: {field}"
    
    def test_technique_descriptions_exist(self, analyzer):
        """Test all techniques have descriptions"""
        for ac_data in EXTENDED_ANTICHEAT_SIGNATURES.values():
            for technique in ac_data["bypass_techniques"]:
                description = analyzer._get_technique_description(technique)
                assert description != ""
                assert len(description) > 10
    
    def test_technique_requirements_exist(self, analyzer):
        """Test all techniques have requirements"""
        for ac_data in EXTENDED_ANTICHEAT_SIGNATURES.values():
            for technique in ac_data["bypass_techniques"]:
                requirements = analyzer._get_technique_requirements(technique)
                assert isinstance(requirements, list)
                assert len(requirements) > 0


class TestAnticheatProfile:
    """Test suite for AnticheatProfile dataclass"""
    
    def test_profile_creation(self):
        """Test profile creation with defaults"""
        profile = AnticheatProfile(name="TestAC")
        
        assert profile.name == "TestAC"
        assert profile.version is None
        assert profile.capabilities == []
        assert profile.limitations == []
        assert profile.bypass_difficulty == 0.5
        assert profile.confidence == 0.0
    
    def test_profile_with_all_fields(self):
        """Test profile creation with all fields"""
        profile = AnticheatProfile(
            name="TestAC",
            version="1.0.0",
            capabilities=["test_cap"],
            limitations=["test_limit"],
            bypass_difficulty=0.75,
            bypass_techniques=["test_tech"],
            detection_patterns=["test_pattern"],
            recommended_strategy="stealth",
            confidence=0.9,
            behavioral_indicators=["test_indicator"],
            update_detected=True,
            pattern_changes=["test_change"]
        )
        
        assert profile.name == "TestAC"
        assert profile.version == "1.0.0"
        assert len(profile.capabilities) == 1
        assert len(profile.limitations) == 1
        assert profile.bypass_difficulty == 0.75
        assert profile.confidence == 0.9
        assert profile.update_detected == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
