"""
Tests for Trigger Analyzer
"""

import os
import tempfile
import pytest
from pathlib import Path

from ambani_integration.analysis.trigger_analyzer import (
    TriggerAnalyzer,
    Trigger,
    ExploitVector,
    Honeypot,
    ObfuscationAnalysis
)


class TestTriggerAnalyzer:
    """Test TriggerAnalyzer functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = TriggerAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization"""
        assert self.analyzer is not None
        assert self.analyzer.triggers == []
        assert self.analyzer.exploit_vectors == []
        assert self.analyzer.honeypots == []
    
    def test_has_validation_positive(self):
        """Test validation detection - positive case"""
        code = """
        RegisterNetEvent('test:event')
        AddEventHandler('test:event', function(source)
            if not source then return end
            -- do something
        end)
        """
        assert self.analyzer._has_validation(code) == True
    
    def test_has_validation_negative(self):
        """Test validation detection - negative case"""
        code = """
        RegisterNetEvent('test:event')
        AddEventHandler('test:event', function(source)
            -- no validation
        end)
        """
        assert self.analyzer._has_validation(code) == False
    
    def test_has_rate_limiting_positive(self):
        """Test rate limiting detection - positive case"""
        code = """
        local cooldown = {}
        RegisterNetEvent('test:event')
        AddEventHandler('test:event', function(source)
            if cooldown[source] then return end
            cooldown[source] = true
        end)
        """
        assert self.analyzer._has_rate_limiting(code) == True

    
    def test_has_rate_limiting_negative(self):
        """Test rate limiting detection - negative case"""
        code = """
        RegisterNetEvent('test:event')
        AddEventHandler('test:event', function(source)
            -- no rate limiting
        end)
        """
        assert self.analyzer._has_rate_limiting(code) == False
    
    def test_detect_dangerous_natives(self):
        """Test dangerous natives detection"""
        code = """
        GiveWeaponToPed(playerPed, 'WEAPON_PISTOL')
        SetEntityCoords(playerPed, x, y, z)
        """
        natives = self.analyzer._detect_dangerous_natives(code)
        assert 'GiveWeaponToPed' in natives
        assert 'SetEntityCoords' in natives
        assert len(natives) == 2
    
    def test_calculate_risk_score_no_validation(self):
        """Test risk score calculation - no validation"""
        trigger = Trigger(
            name='test:giveMoney',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='xPlayer.addMoney(1000)',
            parameters=['source', 'amount'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        score = self.analyzer.calculate_risk_score(trigger)
        # validation_score=100*0.30 + reward_score=100*0.25 + natives=0*0.25 + rate_limit=100*0.20
        # = 30 + 25 + 0 + 20 = 75
        assert score == 75
    
    def test_calculate_risk_score_with_validation(self):
        """Test risk score calculation - with validation"""
        trigger = Trigger(
            name='test:event',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='if not source then return end',
            parameters=['source'],
            has_validation=True,
            has_rate_limiting=True,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        score = self.analyzer.calculate_risk_score(trigger)
        # validation=0*0.30 + reward=0*0.25 + natives=0*0.25 + rate_limit=0*0.20 = 0
        assert score == 0

    
    def test_calculate_risk_score_with_natives(self):
        """Test risk score calculation - with dangerous natives"""
        trigger = Trigger(
            name='test:teleport',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='SetEntityCoords(ped, x, y, z)',
            parameters=['source', 'x', 'y', 'z'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=['SetEntityCoords'],
            risk_score=0,
            category='UNKNOWN'
        )
        
        score = self.analyzer.calculate_risk_score(trigger)
        # validation=100*0.30 + reward=0*0.25 + natives=33*0.25 + rate_limit=100*0.20
        # = 30 + 0 + 8.25 + 20 = 58.25 = 58
        assert score == 58
    
    def test_categorize_severity(self):
        """Test severity categorization"""
        assert self.analyzer._categorize_severity(75) == 'CRITICAL'
        assert self.analyzer._categorize_severity(55) == 'HIGH'
        assert self.analyzer._categorize_severity(35) == 'MEDIUM'
        assert self.analyzer._categorize_severity(15) == 'LOW'
    
    def test_generate_poc_event_injection(self):
        """Test PoC generation for event injection"""
        trigger = Trigger(
            name='esx:giveMoney',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='',
            parameters=['source', 'amount'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        poc = self.analyzer._generate_poc(trigger)
        assert 'TriggerServerEvent' in poc
        assert 'esx:giveMoney' in poc
    
    def test_detect_honeypots(self):
        """Test honeypot detection"""
        trigger = Trigger(
            name='giveMoney',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='BanPlayer(source, "Cheat detected")',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        honeypots = self.analyzer.detect_honeypots([trigger])
        assert len(honeypots) == 1
        assert honeypots[0].trigger.name == 'giveMoney'
        assert honeypots[0].confidence > 0.5

    
    def test_analyze_obfuscation_none(self):
        """Test obfuscation analysis - no obfuscation"""
        code = "print('Hello World')"
        result = self.analyzer.analyze_obfuscation(code)
        
        assert result.has_obfuscation == False
        assert len(result.techniques) == 0
        assert result.difficulty_score == 0
        assert result.deobfuscation_possible == True
    
    def test_analyze_obfuscation_loadstring(self):
        """Test obfuscation analysis - loadstring"""
        code = "loadstring('print(123)')"
        result = self.analyzer.analyze_obfuscation(code)
        
        assert result.has_obfuscation == True
        assert 'loadstring' in result.techniques
        assert result.difficulty_score > 0
    
    def test_analyze_obfuscation_string_char(self):
        """Test obfuscation analysis - string.char"""
        code = "local s = string.char(72, 101, 108, 108, 111)"
        result = self.analyzer.analyze_obfuscation(code)
        
        assert result.has_obfuscation == True
        assert 'string_char' in result.techniques
        assert len(result.obfuscated_strings) > 0
    
    def test_analyze_dump_nonexistent_path(self):
        """Test analyze_dump with nonexistent path"""
        result = self.analyzer.analyze_dump('/nonexistent/path')
        
        assert result['success'] == False
        assert 'error' in result
    
    def test_analyze_dump_with_lua_file(self):
        """Test analyze_dump with actual Lua file"""
        # Create temporary directory with separate Lua files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Vulnerable file
            vuln_file = Path(tmpdir) / 'vulnerable.lua'
            vuln_file.write_text("""
RegisterNetEvent('test:giveMoney')
AddEventHandler('test:giveMoney', function(source, amount)
    xPlayer.addMoney(amount)
end)
            """)
            
            # Safe file
            safe_file = Path(tmpdir) / 'safe.lua'
            safe_file.write_text("""
RegisterNetEvent('test:safe')
AddEventHandler('test:safe', function(source)
    if not source then return end
    print('Safe event')
end)
            """)
            
            result = self.analyzer.analyze_dump(tmpdir)
            
            assert result['success'] == True
            assert len(result['triggers']) >= 2
            assert result['summary']['total_triggers'] >= 2
            
            # Check that we detected the vulnerable trigger
            vulnerable = [t for t in result['triggers'] if t.name == 'test:giveMoney']
            assert len(vulnerable) > 0
            assert vulnerable[0].risk_score > 50
            
            # Check that we detected the safe trigger
            safe = [t for t in result['triggers'] if t.name == 'test:safe']
            assert len(safe) > 0
            assert safe[0].has_validation == True

    
    def test_detect_exploit_vectors(self):
        """Test exploit vector detection"""
        trigger_high_risk = Trigger(
            name='test:exploit',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='xPlayer.addMoney(1000)',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=75,
            category='CRITICAL'
        )
        
        trigger_low_risk = Trigger(
            name='test:safe',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=10,
            code='print("safe")',
            parameters=['source'],
            has_validation=True,
            has_rate_limiting=True,
            dangerous_natives=[],
            risk_score=10,
            category='LOW'
        )
        
        exploits = self.analyzer.detect_exploit_vectors([trigger_high_risk, trigger_low_risk])
        
        # Should only detect high-risk trigger
        assert len(exploits) == 1
        assert exploits[0].trigger.name == 'test:exploit'
        assert exploits[0].severity == 'CRITICAL'
        assert exploits[0].ambani_compatible == True
    
    def test_determine_impact_money(self):
        """Test impact determination - money manipulation"""
        trigger = Trigger(
            name='test:money',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='xPlayer.addMoney(1000)',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        impact = self.analyzer._determine_impact(trigger)
        assert 'Economy manipulation' in impact or 'money' in impact.lower()
    
    def test_determine_impact_teleport(self):
        """Test impact determination - teleportation"""
        trigger = Trigger(
            name='test:teleport',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='SetEntityCoords(ped, x, y, z)',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=['SetEntityCoords'],
            risk_score=0,
            category='UNKNOWN'
        )
        
        impact = self.analyzer._determine_impact(trigger)
        assert 'Teleportation' in impact or 'teleport' in impact.lower()

    
    def test_generate_mitigation(self):
        """Test mitigation generation"""
        trigger = Trigger(
            name='test:vulnerable',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='xPlayer.addMoney(1000)',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        mitigation = self.analyzer._generate_mitigation(trigger)
        assert 'validation' in mitigation.lower()
        assert 'rate limiting' in mitigation.lower()
    
    def test_calculate_honeypot_confidence(self):
        """Test honeypot confidence calculation"""
        trigger = Trigger(
            name='freeMoneyGiveaway',
            event_type='RegisterNetEvent',
            file_path='test.lua',
            line_number=1,
            code='BanPlayer(source, "Cheater")',
            parameters=['source'],
            has_validation=False,
            has_rate_limiting=False,
            dangerous_natives=[],
            risk_score=0,
            category='UNKNOWN'
        )
        
        confidence = self.analyzer._calculate_honeypot_confidence(trigger, 'BanPlayer')
        assert confidence > 0.5
        assert confidence <= 1.0
    
    def test_find_lua_files_single_file(self):
        """Test finding Lua files - single file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write('print("test")')
            lua_file = f.name
        
        try:
            files = self.analyzer._find_lua_files(lua_file)
            assert len(files) == 1
            assert files[0] == lua_file
        finally:
            os.unlink(lua_file)
    
    def test_find_lua_files_directory(self):
        """Test finding Lua files - directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple Lua files
            lua1 = Path(tmpdir) / 'test1.lua'
            lua2 = Path(tmpdir) / 'test2.lua'
            txt = Path(tmpdir) / 'test.txt'
            
            lua1.write_text('print("test1")')
            lua2.write_text('print("test2")')
            txt.write_text('not lua')
            
            files = self.analyzer._find_lua_files(tmpdir)
            assert len(files) == 2
            assert any('test1.lua' in f for f in files)
            assert any('test2.lua' in f for f in files)
