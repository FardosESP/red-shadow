"""
Event Analyzer
Advanced analysis of captured event data from Lua event_capture module

This module reads captured_events.json from the Lua client-side capture
and performs sophisticated analysis to identify farming opportunities.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter
import json
import statistics
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FarmingStrategy:
    """Optimized farming strategy based on analysis"""
    event_name: str
    parameters: List
    reward_type: str
    avg_reward: float
    success_rate: float
    cooldown_seconds: int
    detection_risk: float
    anticheat_safe: bool
    profit_per_hour: float
    sample_size: int
    confidence_level: float


class EventAnalyzer:
    """
    Advanced event data analyzer
    
    Reads captured_events.json from Lua client and performs:
    - Statistical analysis of event patterns
    - Reward optimization calculations
    - Risk assessment with anticheat integration
    - Machine learning pattern detection
    - Strategy generation for auto_farmer.lua
    """
    
    def __init__(self, anticheat_analyzer=None, behavioral_analyzer=None):
        """
        Initialize Event Analyzer
        
        Args:
            anticheat_analyzer: AnticheatAnalyzer for risk assessment
            behavioral_analyzer: BehavioralAnalyzer for ML predictions
        """
        self.logger = get_logger(__name__)
        self.anticheat_analyzer = anticheat_analyzer
        self.behavioral_analyzer = behavioral_analyzer
        
        # Analysis data
        self.captured_data: Optional[Dict] = None
        self.farming_strategies: List[FarmingStrategy] = []
        
        self.logger.info("EventAnalyzer initialized")
    
    def load_captured_data(self, filepath: str) -> bool:
        """
        Load captured events from JSON file
        
        Args:
            filepath: Path to captured_events.json
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.captured_data = json.load(f)
            
            total_events = self.captured_data.get('totalEvents', 0)
            unique_events = self.captured_data.get('uniqueEvents', 0)
            
            self.logger.info("Loaded %d events (%d unique) from %s",
                           total_events, unique_events, filepath)
            return True
            
        except Exception as e:
            self.logger.error("Failed to load captured data: %s", e)
            return False
    
    def analyze_farming_opportunities(self, min_sample_size: int = 5,
                                     min_success_rate: float = 0.7,
                                     min_confidence: float = 0.8) -> List[FarmingStrategy]:
        """
        Analyze captured data to identify optimal farming strategies
        
        Args:
            min_sample_size: Minimum number of events to analyze
            min_success_rate: Minimum success rate threshold
            min_confidence: Minimum statistical confidence
            
        Returns:
            List of farming strategies sorted by profit/hour
        """
        if not self.captured_data:
            self.logger.error("No captured data loaded")
            return []
        
        stats = self.captured_data.get('stats', [])
        strategies = []
        
        for event_stat in stats:
            # Filter by sample size
            if event_stat['count'] < min_sample_size:
                continue
            
            # Must be job event with rewards
            if not event_stat.get('isJob', False):
                continue
            
            if event_stat.get('avgReward', 0) <= 0:
                continue
            
            # Calculate success rate (assume 100% if not tracked)
            success_rate = 1.0  # TODO: Track failures in Lua capture
            
            if success_rate < min_success_rate:
                continue
            
            # Calculate statistical confidence
            sample_size = event_stat['count']
            confidence = self._calculate_confidence(sample_size)
            
            if confidence < min_confidence:
                continue
            
            # Calculate cooldown
            duration = event_stat.get('duration', 0)
            if duration > 0 and sample_size > 1:
                cooldown = max(30, int(duration / sample_size))
            else:
                cooldown = 60  # Default
            
            # Calculate detection risk
            detection_risk = self._calculate_detection_risk(
                event_stat['name'],
                cooldown,
                event_stat['avgReward']
            )
            
            # Calculate profit per hour
            if cooldown > 0:
                executions_per_hour = 3600 / cooldown
                profit_per_hour = executions_per_hour * event_stat['avgReward'] * success_rate
            else:
                profit_per_hour = 0
            
            # Get most common parameters from events
            parameters = self._extract_common_parameters(event_stat['name'])
            
            strategy = FarmingStrategy(
                event_name=event_stat['name'],
                parameters=parameters,
                reward_type=event_stat.get('rewardType', 'unknown'),
                avg_reward=event_stat['avgReward'],
                success_rate=success_rate,
                cooldown_seconds=cooldown,
                detection_risk=detection_risk,
                anticheat_safe=detection_risk < 0.5,
                profit_per_hour=profit_per_hour,
                sample_size=sample_size,
                confidence_level=confidence
            )
            
            strategies.append(strategy)
            
            self.logger.info("Strategy: %s (%.2f/hour, %.1f%% risk, %d samples)",
                           event_stat['name'], profit_per_hour, 
                           detection_risk * 100, sample_size)
        
        # Sort by profit per hour
        strategies.sort(key=lambda s: s.profit_per_hour, reverse=True)
        
        self.farming_strategies = strategies
        return strategies
    
    def _calculate_confidence(self, sample_size: int) -> float:
        """
        Calculate statistical confidence based on sample size
        
        Args:
            sample_size: Number of samples
            
        Returns:
            Confidence level (0.0 to 1.0)
        """
        # Simple confidence calculation based on sample size
        # More samples = higher confidence
        if sample_size >= 50:
            return 0.95
        elif sample_size >= 20:
            return 0.90
        elif sample_size >= 10:
            return 0.85
        elif sample_size >= 5:
            return 0.80
        else:
            return 0.70
    
    def _calculate_detection_risk(self, event_name: str, cooldown: int,
                                  avg_reward: float) -> float:
        """
        Calculate detection risk for farming an event
        
        Args:
            event_name: Event name
            cooldown: Cooldown in seconds
            avg_reward: Average reward amount
            
        Returns:
            Risk score (0.0 to 1.0)
        """
        risk = 0.3  # Base risk
        
        # Factor 1: Cooldown (shorter = riskier)
        if cooldown < 30:
            risk += 0.3
        elif cooldown < 60:
            risk += 0.2
        elif cooldown < 120:
            risk += 0.1
        
        # Factor 2: Reward amount (higher = riskier)
        if avg_reward > 10000:
            risk += 0.2
        elif avg_reward > 5000:
            risk += 0.1
        
        # Factor 3: Event name patterns
        validation_keywords = ['check', 'verify', 'validate', 'auth', 'permission']
        if any(keyword in event_name.lower() for keyword in validation_keywords):
            risk += 0.2
        
        # Factor 4: Anticheat integration
        if self.anticheat_analyzer and self.anticheat_analyzer.detected_anticheats:
            avg_difficulty = sum(ac.bypass_difficulty 
                               for ac in self.anticheat_analyzer.detected_anticheats)
            avg_difficulty /= len(self.anticheat_analyzer.detected_anticheats)
            risk += avg_difficulty * 0.2
        
        return min(1.0, risk)
    
    def _extract_common_parameters(self, event_name: str) -> List:
        """
        Extract most common parameters for an event
        
        Args:
            event_name: Event name
            
        Returns:
            List of most common parameters
        """
        if not self.captured_data:
            return []
        
        # Find all events with this name
        events = [e for e in self.captured_data.get('events', [])
                 if e.get('name') == event_name]
        
        if not events:
            return []
        
        # Get most common parameter set
        param_sets = [tuple(e.get('params', [])) for e in events]
        if not param_sets:
            return []
        
        most_common = Counter(param_sets).most_common(1)[0][0]
        return list(most_common)
    
    def export_strategies_for_lua(self, filepath: str):
        """
        Export strategies to JSON for auto_farmer.lua
        
        Args:
            filepath: Output file path
        """
        data = {
            'generated': datetime.now().isoformat(),
            'total_strategies': len(self.farming_strategies),
            'strategies': [
                {
                    'event': s.event_name,
                    'params': s.parameters,
                    'rewardType': s.reward_type,
                    'avgReward': s.avg_reward,
                    'cooldown': s.cooldown_seconds,
                    'detectionRisk': s.detection_risk,
                    'profitPerHour': s.profit_per_hour,
                    'sampleSize': s.sample_size,
                    'confidence': s.confidence_level
                }
                for s in self.farming_strategies
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info("Exported %d strategies to %s",
                        len(self.farming_strategies), filepath)
    
    def get_statistics(self) -> Dict:
        """Get analysis statistics"""
        if not self.captured_data:
            return {}
        
        return {
            'total_events': self.captured_data.get('totalEvents', 0),
            'unique_events': self.captured_data.get('uniqueEvents', 0),
            'job_events': self.captured_data.get('jobEvents', 0),
            'reward_events': self.captured_data.get('rewardEvents', 0),
            'farming_strategies': len(self.farming_strategies),
            'avg_profit_per_hour': statistics.mean([s.profit_per_hour 
                                                   for s in self.farming_strategies])
                                  if self.farming_strategies else 0
        }
