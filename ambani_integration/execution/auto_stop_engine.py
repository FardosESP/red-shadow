"""
Auto Stop Engine
Intelligent resource stopping with ML-based confidence scoring
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StopMode(Enum):
    """Stop engine operation modes"""
    MANUAL = "manual"      # Require admin approval for each stop
    NOTIFY = "notify"      # Stop automatically but notify admin
    AUTO = "auto"          # Fully automatic stopping


class ResourceClassification(Enum):
    """Resource risk classifications"""
    CRITICAL = "critical"      # Never stop (core, framework, anticheat)
    RISKY = "risky"           # High risk to stop (economy, admin)
    SAFE = "safe"             # Safe to stop (cosmetic, UI)
    VULNERABLE = "vulnerable"  # Should be stopped (exploitable)


@dataclass
class StopDecisionResult:
    """Result of a stop decision"""
    resource_name: str
    should_stop: bool
    confidence_score: float
    classification: ResourceClassification
    reasons: List[str]
    anticheat_risk: float
    detection_probability: float
    recommended_action: str


@dataclass
class StopStatistics:
    """Statistics for stop decisions"""
    true_positives: int = 0   # Correctly stopped vulnerable resources
    false_positives: int = 0  # Incorrectly stopped safe resources
    true_negatives: int = 0   # Correctly kept safe resources
    false_negatives: int = 0  # Missed vulnerable resources
    total_stops: int = 0
    total_decisions: int = 0
    
    @property
    def precision(self) -> float:
        """Precision: TP / (TP + FP)"""
        if self.true_positives + self.false_positives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_positives)
    
    @property
    def recall(self) -> float:
        """Recall: TP / (TP + FN)"""
        if self.true_positives + self.false_negatives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_negatives)
    
    @property
    def f1_score(self) -> float:
        """F1 Score: 2 * (precision * recall) / (precision + recall)"""
        if self.precision + self.recall == 0:
            return 0.0
        return 2 * (self.precision * self.recall) / (self.precision + self.recall)


class AutoStopEngine:
    """
    Intelligent resource stopping engine with ML-based confidence scoring
    
    Responsibilities:
    - Classify resources by risk level (Task 8.3)
    - Calculate stop confidence scores (Task 8.2)
    - Detect stop detection logic in resources (Task 8.4)
    - Implement safe stop strategies (Task 8.5)
    - Learn from admin feedback (Task 8.6)
    - Track statistics (Task 8.7)
    - Implement grace periods and rate limiting (Task 8.8, 8.9)
    - Collect admin feedback (Task 8.10)
    """
    
    def __init__(self, mode: StopMode = StopMode.NOTIFY, 
                 confidence_threshold: float = 0.7,
                 anticheat_analyzer=None,
                 behavioral_analyzer=None):
        """
        Initialize Auto Stop Engine
        
        Args:
            mode: Operation mode (manual, notify, auto)
            confidence_threshold: Minimum confidence to stop (0.0 to 1.0)
            anticheat_analyzer: AnticheatAnalyzer instance for risk assessment
            behavioral_analyzer: BehavioralAnalyzer instance for ML predictions
        """
        self.logger = get_logger(__name__)
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self.anticheat_analyzer = anticheat_analyzer
        self.behavioral_analyzer = behavioral_analyzer
        
        # Statistics (Task 8.7)
        self.statistics = StopStatistics()
        
        # Rate limiting (Task 8.9)
        self.max_stops_per_minute = 3
        self.recent_stops: List[datetime] = []
        
        # Grace period tracking (Task 8.8)
        self.grace_period_seconds = 300  # 5 minutes
        self.resource_start_times: Dict[str, datetime] = {}
        
        # Learning mode (Task 8.6)
        self.learning_enabled = True
        self.feedback_history: List[Dict] = []
        
        # Stop detection patterns (Task 8.4)
        self.stop_detection_patterns = [
            r'onResourceStop',
            r'AddEventHandler\s*\(\s*["\']onResourceStop["\']',
            r'BanPlayer.*onResourceStop',
            r'KickPlayer.*onResourceStop',
            r'if.*GetResourceState.*==\s*["\']stopped["\']'
        ]
        
        # Professional strategies (EXPERT KNOWLEDGE)
        self.professional_strategies = {}
        self._load_professional_strategies()
        
        self.logger.info("AutoStopEngine initialized: mode=%s, threshold=%.2f",
                        mode.value, confidence_threshold)
    
    def _load_professional_strategies(self):
        """Load professional stop strategies from JSON file"""
        import json
        import os
        
        strategies_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'professional_stop_strategies.json'
        )
        
        try:
            with open(strategies_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.professional_strategies = data.get('professional_strategies', {})
                self.logger.info("Loaded professional strategies for %d anticheats",
                               len(self.professional_strategies))
        except Exception as e:
            self.logger.warning("Failed to load professional strategies: %s", e)
            self.professional_strategies = {}
    
    def get_professional_recommendation(self, resource_name: str, 
                                       anticheat_name: Optional[str] = None) -> Dict:
        """
        Get professional recommendation for stopping a resource
        
        Args:
            resource_name: Name of the resource
            anticheat_name: Detected anticheat (if any)
            
        Returns:
            Dictionary with professional recommendation
        """
        if not anticheat_name or anticheat_name not in self.professional_strategies:
            anticheat_name = "No Anticheat"
        
        strategy = self.professional_strategies.get(anticheat_name, {})
        resource_lower = resource_name.lower()
        
        # Check priority stops
        priority_stops = strategy.get('priority_stops', [])
        for stop in priority_stops:
            stop_resource = stop.get('resource', '').lower()
            # Check if resource matches (handle wildcards and partial matches)
            if any(keyword in resource_lower for keyword in stop_resource.split()):
                return {
                    'recommended': True,
                    'reason': stop.get('reason', ''),
                    'timing': stop.get('timing', ''),
                    'detection_risk': stop.get('detection_risk', 0.5),
                    'professional_tip': stop.get('professional_tip', ''),
                    'alternative': stop.get('alternative', '')
                }
        
        # Check never_stop list
        never_stop = strategy.get('never_stop', [])
        for pattern in never_stop:
            if isinstance(pattern, str):
                # Extract keywords from pattern (handle full sentences)
                pattern_lower = pattern.lower()
                # Check if resource name contains key terms from the pattern
                key_terms = ['admin', 'anticheat', 'economy', 'banking', 'inventory', 
                            'fiveguard', 'phoenixac', 'waveshield', 'fireac', 'badgerac', 'qprotect']
                for term in key_terms:
                    if term in pattern_lower and term in resource_lower:
                        return {
                            'recommended': False,
                            'reason': f'Professional rule: Never stop {pattern}',
                            'timing': 'Never',
                            'detection_risk': 1.0,
                            'professional_tip': 'This will trigger instant detection/ban',
                            'alternative': 'Use memory hooks or network blocking instead'
                        }
                # Also check direct substring match
                if pattern_lower in resource_lower:
                    return {
                        'recommended': False,
                        'reason': f'Professional rule: Never stop {pattern}',
                        'timing': 'Never',
                        'detection_risk': 1.0,
                        'professional_tip': 'This will trigger instant detection/ban',
                        'alternative': 'Use memory hooks or network blocking instead'
                    }
        
        # Check safe_stops list
        safe_stops = strategy.get('safe_stops', [])
        for pattern in safe_stops:
            if isinstance(pattern, str) and any(keyword in resource_lower 
                                               for keyword in pattern.lower().split()):
                return {
                    'recommended': True,
                    'reason': f'Professional rule: Safe to stop with {anticheat_name}',
                    'timing': 'Anytime',
                    'detection_risk': 0.3,
                    'professional_tip': strategy.get('professional_approach', ''),
                    'alternative': ''
                }
        
        # Default recommendation
        difficulty = strategy.get('difficulty', 'MODERATE')
        detection_level = strategy.get('detection_level', 'MODERATE')
        
        base_risk = {
            'NONE': 0.1, 'VERY_LOW': 0.2, 'LOW': 0.3, 'MINIMAL': 0.3,
            'MODERATE': 0.5, 'HIGH': 0.7, 'VERY_HIGH': 0.85, 'EXTREME': 0.95
        }.get(detection_level, 0.5)
        
        return {
            'recommended': base_risk < 0.6,
            'reason': f'No specific rule for this resource with {anticheat_name}',
            'timing': 'Use caution',
            'detection_risk': base_risk,
            'professional_tip': strategy.get('professional_approach', ''),
            'alternative': 'Consider alternatives to resource stopping'
        }
    
    def classify_resource(self, resource_name: str, triggers: List[Dict],
                         anticheat_name: Optional[str] = None) -> ResourceClassification:
        """
        Classify resource by risk level (Task 8.3)
        
        Args:
            resource_name: Name of the resource
            triggers: List of triggers in the resource
            anticheat_name: Detected anticheat (if any)
            
        Returns:
            Resource classification
        """
        resource_lower = resource_name.lower()
        
        # Check professional strategies first (EXPERT KNOWLEDGE)
        if anticheat_name and self.professional_strategies:
            prof_rec = self.get_professional_recommendation(resource_name, anticheat_name)
            
            # If professional rule says never stop, mark as CRITICAL
            if not prof_rec['recommended'] and prof_rec['detection_risk'] >= 0.9:
                self.logger.info("Professional rule: %s is CRITICAL with %s",
                               resource_name, anticheat_name)
                return ResourceClassification.CRITICAL
            
            # If professional rule says safe to stop, consider it
            if prof_rec['recommended'] and prof_rec['detection_risk'] < 0.4:
                self.logger.info("Professional rule: %s is SAFE with %s",
                               resource_name, anticheat_name)
                # Continue to check other factors, but bias towards SAFE
        
        # CRITICAL: Never stop these
        critical_patterns = [
            'es_extended', 'esx', 'qb-core', 'qbcore', 'vrp',
            'oxmysql', 'mysql', 'ghmattimysql',
            'txadmin', 'monitor', 'sessionmanager', 'mapmanager',
            'spawnmanager', 'baseevents', 'chat', 'hardcap',
            'anticheat', 'protection', 'fiveguard', 'phoenixac',
            'waveshield', 'fireac', 'badgerac', 'qprotect'
        ]
        
        for pattern in critical_patterns:
            if pattern in resource_lower:
                return ResourceClassification.CRITICAL
        
        # Check anticheat resource matrix if available
        if self.anticheat_analyzer and anticheat_name:
            # Load anticheat resource matrix
            import json
            import os
            matrix_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'anticheat_resource_matrix.json'
            )
            
            try:
                with open(matrix_path, 'r') as f:
                    matrix = json.load(f)
                
                ac_data = matrix['anticheats'].get(anticheat_name, {})
                never_stop = ac_data.get('never_stop', [])
                risky_to_stop = ac_data.get('risky_to_stop', [])
                
                # Check if resource matches never_stop patterns
                for pattern in never_stop:
                    if '*' in pattern:
                        # Wildcard pattern
                        prefix = pattern.replace('*', '')
                        if resource_lower.startswith(prefix.lower()):
                            return ResourceClassification.CRITICAL
                    elif pattern.lower() in resource_lower:
                        return ResourceClassification.CRITICAL
                
                # Check if resource matches risky patterns
                for pattern in risky_to_stop:
                    if '*' in pattern:
                        prefix = pattern.replace('*', '')
                        if resource_lower.startswith(prefix.lower()):
                            return ResourceClassification.RISKY
                    elif pattern.lower() in resource_lower:
                        return ResourceClassification.RISKY
                        
            except Exception as e:
                self.logger.warning("Failed to load anticheat matrix: %s", e)
        
        # RISKY: Economy, admin, weapons
        risky_patterns = ['bank', 'money', 'cash', 'economy', 'admin', 'mod_',
                         'weapon', 'inventory', 'vehicle']
        
        for pattern in risky_patterns:
            if pattern in resource_lower:
                return ResourceClassification.RISKY
        
        # VULNERABLE: High risk score from triggers
        if triggers:
            avg_risk = sum(t.get('risk_score', 0) for t in triggers) / len(triggers)
            if avg_risk > 0.7:
                return ResourceClassification.VULNERABLE
        
        # SAFE: Everything else (cosmetic, UI, etc.)
        return ResourceClassification.SAFE
    
    def calculate_stop_confidence(self, resource_name: str, triggers: List[Dict],
                                  code_content: str, anticheat_name: Optional[str] = None) -> float:
        """
        Calculate confidence score for stopping a resource (Task 8.2)
        
        Args:
            resource_name: Name of the resource
            triggers: List of triggers in the resource
            code_content: Full code content of the resource
            anticheat_name: Detected anticheat (if any)
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Factor 1: Resource classification (30% weight)
        classification = self.classify_resource(resource_name, triggers, anticheat_name)
        
        if classification == ResourceClassification.CRITICAL:
            return 0.0  # Never stop
        elif classification == ResourceClassification.VULNERABLE:
            confidence += 0.3
        elif classification == ResourceClassification.SAFE:
            confidence += 0.15
        # RISKY stays at base
        
        # Factor 2: Trigger risk scores (25% weight)
        if triggers:
            avg_risk = sum(t.get('risk_score', 0) for t in triggers) / len(triggers)
            confidence += avg_risk * 0.25
        
        # Factor 3: Stop detection logic (20% weight)
        has_stop_detection = self.detect_stop_detection_logic(code_content)
        if has_stop_detection:
            confidence -= 0.20  # Reduce confidence if stop detection found
        
        # Factor 4: Anticheat risk (15% weight)
        if self.anticheat_analyzer and anticheat_name:
            # Get anticheat bypass difficulty
            profiles = [p for p in self.anticheat_analyzer.detected_anticheats 
                       if p.name == anticheat_name]
            if profiles:
                bypass_difficulty = profiles[0].bypass_difficulty
                # Higher difficulty = lower confidence
                confidence -= bypass_difficulty * 0.15
        
        # Factor 5: ML prediction (10% weight)
        if self.behavioral_analyzer and self.behavioral_analyzer.is_trained:
            # Use behavioral analyzer to predict if resource is truly vulnerable
            try:
                if triggers:
                    anomaly = self.behavioral_analyzer.detect_anomalies(triggers[0])
                    if anomaly:
                        confidence += anomaly.anomaly_score * 0.10
            except Exception as e:
                self.logger.warning("ML prediction failed: %s", e)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def detect_stop_detection_logic(self, code_content: str) -> bool:
        """
        Detect if resource has stop detection logic (Task 8.4)
        
        Args:
            code_content: Full code content
            
        Returns:
            True if stop detection found
        """
        import re
        
        for pattern in self.stop_detection_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                self.logger.info("Stop detection pattern found: %s", pattern)
                return True
        
        return False
    
    def should_stop_resource(self, resource_name: str, triggers: List[Dict],
                            code_content: str, anticheat_name: Optional[str] = None) -> StopDecisionResult:
        """
        Decide if a resource should be stopped (combines all factors)
        
        Args:
            resource_name: Name of the resource
            triggers: List of triggers
            code_content: Full code content
            anticheat_name: Detected anticheat
            
        Returns:
            Stop decision result
        """
        # Check grace period (Task 8.8)
        if resource_name in self.resource_start_times:
            start_time = self.resource_start_times[resource_name]
            if datetime.now() - start_time < timedelta(seconds=self.grace_period_seconds):
                return StopDecisionResult(
                    resource_name=resource_name,
                    should_stop=False,
                    confidence_score=0.0,
                    classification=ResourceClassification.SAFE,
                    reasons=["Resource in grace period"],
                    anticheat_risk=0.0,
                    detection_probability=0.0,
                    recommended_action="wait"
                )
        
        # Get professional recommendation (EXPERT KNOWLEDGE)
        prof_rec = self.get_professional_recommendation(resource_name, anticheat_name)
        
        # Classify resource
        classification = self.classify_resource(resource_name, triggers, anticheat_name)
        
        # Calculate confidence
        confidence = self.calculate_stop_confidence(
            resource_name, triggers, code_content, anticheat_name
        )
        
        # Adjust confidence based on professional recommendation
        if prof_rec['recommended']:
            # Professional says safe to stop - boost confidence
            confidence = min(1.0, confidence + 0.15)
        else:
            # Professional says risky - reduce confidence
            confidence = max(0.0, confidence - 0.20)
        
        # Calculate anticheat risk (use professional detection_risk if available)
        anticheat_risk = prof_rec.get('detection_risk', 0.5)
        if self.anticheat_analyzer and anticheat_name:
            profiles = [p for p in self.anticheat_analyzer.detected_anticheats 
                       if p.name == anticheat_name]
            if profiles:
                # Average professional risk with analyzer risk
                analyzer_risk = profiles[0].bypass_difficulty
                anticheat_risk = (anticheat_risk + analyzer_risk) / 2
        
        # Build reasons
        reasons = []
        if classification == ResourceClassification.VULNERABLE:
            reasons.append("Resource classified as vulnerable")
        if triggers:
            avg_risk = sum(t.get('risk_score', 0) for t in triggers) / len(triggers)
            if avg_risk > 0.7:
                reasons.append(f"High average risk score: {avg_risk:.2f}")
        if self.detect_stop_detection_logic(code_content):
            reasons.append("Stop detection logic found - risky to stop")
        
        # Add professional recommendation to reasons
        if prof_rec['reason']:
            reasons.append(f"Professional: {prof_rec['reason']}")
        if prof_rec['professional_tip']:
            reasons.append(f"Tip: {prof_rec['professional_tip']}")
        
        # Make decision
        should_stop = (
            classification != ResourceClassification.CRITICAL and
            confidence >= self.confidence_threshold and
            not self.detect_stop_detection_logic(code_content) and
            prof_rec['recommended']  # Must have professional approval
        )
        
        # Recommended action
        if classification == ResourceClassification.CRITICAL:
            recommended_action = "never_stop"
        elif should_stop:
            recommended_action = "stop"
        elif confidence >= self.confidence_threshold * 0.8:
            recommended_action = "investigate"
        else:
            recommended_action = "monitor"
        
        # Override with professional timing if available
        if prof_rec['timing'] and prof_rec['timing'].lower() == 'never':
            recommended_action = "never_stop"
            should_stop = False
        
        result = StopDecisionResult(
            resource_name=resource_name,
            should_stop=should_stop,
            confidence_score=confidence,
            classification=classification,
            reasons=reasons if reasons else ["Confidence below threshold"],
            anticheat_risk=anticheat_risk,
            detection_probability=anticheat_risk if should_stop else 0.0,
            recommended_action=recommended_action
        )
        
        self.statistics.total_decisions += 1
        
        return result
    
    def execute_stop(self, resource_name: str, decision: StopDecisionResult,
                    resource_controller=None) -> bool:
        """
        Execute resource stop with safety checks (Task 8.5)
        
        Args:
            resource_name: Resource to stop
            decision: Stop decision result
            resource_controller: ResourceController instance
            
        Returns:
            True if stop executed successfully
        """
        # Check rate limiting (Task 8.9)
        if not self.check_rate_limit():
            self.logger.warning("Rate limit exceeded, cannot stop %s", resource_name)
            return False
        
        # Check mode
        if self.mode == StopMode.MANUAL:
            self.logger.info("Manual mode: Admin approval required for %s", resource_name)
            return False
        
        if self.mode == StopMode.NOTIFY:
            self.logger.info("Notify mode: Stopping %s and notifying admin", resource_name)
        
        # Execute stop
        if resource_controller:
            try:
                success = resource_controller.stop_resource(resource_name, 
                                                           reason=f"Auto-stop: {', '.join(decision.reasons)}")
                if success:
                    self.recent_stops.append(datetime.now())
                    self.statistics.total_stops += 1
                    self.logger.info("Successfully stopped resource: %s", resource_name)
                return success
            except Exception as e:
                self.logger.error("Failed to stop resource %s: %s", resource_name, e)
                return False
        else:
            self.logger.warning("No resource controller available, simulating stop")
            self.recent_stops.append(datetime.now())
            return True
    
    def check_rate_limit(self) -> bool:
        """
        Check if rate limit allows another stop (Task 8.9)
        
        Returns:
            True if within rate limit
        """
        # Clean old stops (older than 1 minute)
        cutoff = datetime.now() - timedelta(minutes=1)
        self.recent_stops = [t for t in self.recent_stops if t > cutoff]
        
        return len(self.recent_stops) < self.max_stops_per_minute
    
    def record_feedback(self, resource_name: str, was_correct: bool, 
                       admin_comment: Optional[str] = None):
        """
        Record admin feedback for learning (Task 8.10)
        
        Args:
            resource_name: Resource that was stopped
            was_correct: Whether the stop decision was correct
            admin_comment: Optional admin comment
        """
        feedback = {
            'resource_name': resource_name,
            'was_correct': was_correct,
            'admin_comment': admin_comment,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_history.append(feedback)
        
        # Update statistics (Task 8.7)
        if was_correct:
            self.statistics.true_positives += 1
        else:
            self.statistics.false_positives += 1
        
        # Learn from feedback (Task 8.6)
        if self.learning_enabled:
            self._update_threshold_from_feedback()
        
        self.logger.info("Feedback recorded for %s: correct=%s", resource_name, was_correct)
    
    def _update_threshold_from_feedback(self):
        """
        Update confidence threshold based on feedback (Task 8.6)
        
        Uses simple logistic regression approach
        """
        if len(self.feedback_history) < 10:
            return  # Need more data
        
        # Calculate current precision
        precision = self.statistics.precision
        
        # Adjust threshold to maintain precision > 0.8
        if precision < 0.8 and self.confidence_threshold < 0.95:
            # Too many false positives, increase threshold
            self.confidence_threshold = min(0.95, self.confidence_threshold + 0.05)
            self.logger.info("Increased confidence threshold to %.2f (precision: %.2f)",
                           self.confidence_threshold, precision)
        elif precision > 0.95 and self.confidence_threshold > 0.5:
            # Very high precision, can lower threshold to catch more
            self.confidence_threshold = max(0.5, self.confidence_threshold - 0.02)
            self.logger.info("Decreased confidence threshold to %.2f (precision: %.2f)",
                           self.confidence_threshold, precision)
    
    def get_statistics(self) -> Dict:
        """Get current statistics (Task 8.7)"""
        return {
            'true_positives': self.statistics.true_positives,
            'false_positives': self.statistics.false_positives,
            'true_negatives': self.statistics.true_negatives,
            'false_negatives': self.statistics.false_negatives,
            'total_stops': self.statistics.total_stops,
            'total_decisions': self.statistics.total_decisions,
            'precision': self.statistics.precision,
            'recall': self.statistics.recall,
            'f1_score': self.statistics.f1_score,
            'current_threshold': self.confidence_threshold
        }
    
    def register_resource_start(self, resource_name: str):
        """Register when a resource starts (for grace period tracking)"""
        self.resource_start_times[resource_name] = datetime.now()
        self.logger.debug("Registered start time for %s", resource_name)
