"""
Event Monitor (Coordinator)
Coordinates event capture → analysis → farming workflow

ARCHITECTURE:
- event_capture.lua (Lua CLIENT) → captured_events.json
- event_analyzer.py (Python) → farming_strategies.json  
- auto_farmer.lua (Lua CLIENT) → executes farming

This coordinator automates the complete pipeline.
"""

from typing import List, Dict, Optional
from .event_analyzer import EventAnalyzer, FarmingStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EventMonitor:
    """
    Event Monitor Coordinator
    
    Automates: event capture → analysis → farming
    - Loads captured_events.json from Lua client
    - Analyzes with EventAnalyzer
    - Exports farming_strategies.json for auto_farmer.lua
    """
    
    def __init__(self, anticheat_analyzer=None, auto_stop_engine=None):
        """
        Initialize Event Monitor
        
        Args:
            anticheat_analyzer: AnticheatAnalyzer for risk assessment
            auto_stop_engine: AutoStopEngine for safe resource management
        """
        self.logger = get_logger(__name__)
        self.anticheat_analyzer = anticheat_analyzer
        self.auto_stop_engine = auto_stop_engine
        
        # Create analyzer
        self.analyzer = EventAnalyzer(
            anticheat_analyzer=anticheat_analyzer,
            behavioral_analyzer=None  # TODO: Add behavioral analyzer
        )
        
        self.logger.info("EventMonitor initialized (coordinator mode)")
    
    def analyze_captured_events(self, captured_file: str = "captured_events.json",
                               min_sample_size: int = 5,
                               min_success_rate: float = 0.7) -> List[FarmingStrategy]:
        """
        Analyze captured events and generate farming strategies
        
        Args:
            captured_file: Path to captured_events.json from Lua
            min_sample_size: Minimum events to analyze
            min_success_rate: Minimum success rate
            
        Returns:
            List of farming strategies
        """
        self.logger.info("Analyzing captured events from %s", captured_file)
        
        # Load captured data
        if not self.analyzer.load_captured_data(captured_file):
            self.logger.error("Failed to load captured data")
            return []
        
        # Analyze opportunities
        strategies = self.analyzer.analyze_farming_opportunities(
            min_sample_size=min_sample_size,
            min_success_rate=min_success_rate
        )
        
        self.logger.info("Found %d farming strategies", len(strategies))
        return strategies
    
    def export_strategies_for_lua(self, output_file: str = "farming_strategies.json"):
        """
        Export strategies to JSON for auto_farmer.lua
        
        Args:
            output_file: Output file path
        """
        self.analyzer.export_strategies_for_lua(output_file)
        self.logger.info("Strategies exported to %s", output_file)
    

    
    def get_statistics(self) -> Dict:
        """Get analysis statistics"""
        return self.analyzer.get_statistics()


