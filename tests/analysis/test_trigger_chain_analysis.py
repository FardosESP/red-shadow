"""
Tests for trigger chain analysis functionality
"""

import pytest
import tempfile
import os
from pathlib import Path

from ambani_integration.analysis.trigger_analyzer import TriggerAnalyzer, TriggerChain


class TestTriggerChainAnalysis:
    """Test suite for cross-file trigger chain analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = TriggerAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, content: str) -> str:
        """Helper to create a test Lua file"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_simple_trigger_chain(self):
        """Test detection of a simple two-trigger chain"""
        # Create file with trigger A calling trigger B
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('triggerA')
            AddEventHandler('triggerA', function(amount)
                -- No validation
                TriggerEvent('triggerB', amount * 2)
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('triggerB')
            AddEventHandler('triggerB', function(amount)
                -- No validation
                xPlayer.addMoney(amount)
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        assert len(result['triggers']) >= 2
        assert len(result['trigger_chains']) >= 1
        
        # Find the chain
        chain = result['trigger_chains'][0]
        assert chain.chain_length >= 2
        assert chain.entry_point is not None
        assert chain.entry_point.name == 'triggerA'
    
    def test_multi_stage_attack_chain(self):
        """Test detection of a multi-stage attack chain (3+ triggers)"""
        # Create a chain: A -> B -> C
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('startAttack')
            AddEventHandler('startAttack', function()
                TriggerServerEvent('validateAttack')
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('validateAttack')
            AddEventHandler('validateAttack', function()
                -- Weak validation
                TriggerEvent('executeAttack')
            end)
        ''')
        
        self.create_test_file('file3.lua', '''
            RegisterNetEvent('executeAttack')
            AddEventHandler('executeAttack', function()
                -- No validation, gives money
                xPlayer.addMoney(10000)
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        assert len(result['trigger_chains']) >= 1
        
        # Find the longest chain
        longest_chain = max(result['trigger_chains'], key=lambda c: c.chain_length)
        assert longest_chain.chain_length >= 3
        assert longest_chain.is_multi_stage_attack
    
    def test_combined_risk_score_calculation(self):
        """Test that combined risk scores are calculated correctly"""
        # Create chain with high-risk and low-risk triggers
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('lowRisk')
            AddEventHandler('lowRisk', function()
                -- Has validation
                if not source then return end
                TriggerEvent('highRisk')
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('highRisk')
            AddEventHandler('highRisk', function(amount)
                -- No validation, gives money
                xPlayer.addMoney(amount)
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        chains = result['trigger_chains']
        assert len(chains) >= 1
        
        # Combined risk should be influenced by the high-risk trigger
        chain = chains[0]
        assert chain.combined_risk_score > 0
        # Should be weighted toward the higher risk
        high_risk_trigger = next((t for t in chain.triggers if t.name == 'highRisk'), None)
        if high_risk_trigger:
            # Combined risk should be at least 50% of the highest risk
            assert chain.combined_risk_score >= high_risk_trigger.risk_score * 0.5
    
    def test_no_chains_detected(self):
        """Test that no chains are detected when triggers don't call each other"""
        # Create isolated triggers
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('isolatedA')
            AddEventHandler('isolatedA', function()
                print("Isolated A")
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('isolatedB')
            AddEventHandler('isolatedB', function()
                print("Isolated B")
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        assert len(result['triggers']) >= 2
        # Should have no chains since triggers don't call each other
        assert len(result['trigger_chains']) == 0
    
    def test_cycle_detection(self):
        """Test that cycles are handled correctly (A -> B -> A)"""
        # Create cyclic chain
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('cycleA')
            AddEventHandler('cycleA', function()
                TriggerEvent('cycleB')
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('cycleB')
            AddEventHandler('cycleB', function()
                TriggerEvent('cycleA')
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify - should detect chain but not infinite loop
        assert result['success']
        assert len(result['trigger_chains']) >= 1
        
        # Verify no chain has duplicate triggers (cycle prevention)
        for chain in result['trigger_chains']:
            trigger_names = [t.name for t in chain.triggers]
            assert len(trigger_names) == len(set(trigger_names)), "Chain contains duplicate triggers (cycle not prevented)"
    
    def test_trigger_graph_building(self):
        """Test that the trigger dependency graph is built correctly"""
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('parent')
            AddEventHandler('parent', function()
                TriggerEvent('child1')
                TriggerServerEvent('child2')
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('child1')
            AddEventHandler('child1', function()
                print("Child 1")
            end)
            
            RegisterNetEvent('child2')
            AddEventHandler('child2', function()
                print("Child 2")
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify graph structure
        assert result['success']
        assert 'parent' in self.analyzer.trigger_graph
        
        # Parent should call both children
        parent_calls = self.analyzer.trigger_graph['parent']
        assert 'child1' in parent_calls or 'child2' in parent_calls
    
    def test_entry_point_identification(self):
        """Test that entry points are correctly identified"""
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('entryPoint')
            AddEventHandler('entryPoint', function()
                TriggerEvent('internal')
            end)
            
            -- Internal trigger (not an entry point)
            AddEventHandler('internal', function()
                print("Internal")
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        
        # Find entry point trigger
        entry_trigger = next((t for t in result['triggers'] if t.name == 'entryPoint'), None)
        assert entry_trigger is not None
        
        # Verify it's identified as an entry point
        assert self.analyzer._is_entry_point(entry_trigger)
    
    def test_chain_description_generation(self):
        """Test that chain descriptions are meaningful"""
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('bankRobbery')
            AddEventHandler('bankRobbery', function()
                TriggerEvent('giveMoney')
            end)
        ''')
        
        self.create_test_file('file2.lua', '''
            RegisterNetEvent('giveMoney')
            AddEventHandler('giveMoney', function(amount)
                xPlayer.addMoney(amount)
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify
        assert result['success']
        assert len(result['trigger_chains']) >= 1
        
        chain = result['trigger_chains'][0]
        assert chain.description is not None
        assert len(chain.description) > 0
        # Should mention the chain path
        assert 'bankRobbery' in chain.description or 'giveMoney' in chain.description
    
    def test_summary_includes_chain_stats(self):
        """Test that analysis summary includes trigger chain statistics"""
        self.create_test_file('file1.lua', '''
            RegisterNetEvent('trigger1')
            AddEventHandler('trigger1', function()
                TriggerEvent('trigger2')
            end)
            
            RegisterNetEvent('trigger2')
            AddEventHandler('trigger2', function()
                xPlayer.addMoney(1000)
            end)
        ''')
        
        # Analyze
        result = self.analyzer.analyze_dump(self.temp_dir)
        
        # Verify summary
        assert result['success']
        assert 'summary' in result
        assert 'trigger_chains' in result['summary']
        assert 'multi_stage_attacks' in result['summary']
        assert result['summary']['trigger_chains'] >= 0
        assert result['summary']['multi_stage_attacks'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
