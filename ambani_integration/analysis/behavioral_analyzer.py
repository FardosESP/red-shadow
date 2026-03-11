"""
Behavioral Analyzer
Machine learning-based anomaly detection and behavior analysis
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import re
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Anomaly:
    """Detected anomaly"""
    trigger: Dict
    anomaly_score: float
    detected_by: List[str]
    deviation_type: str
    explanation: str
    confidence: float = 0.0
    features: Dict = field(default_factory=dict)


@dataclass
class BehaviorProfile:
    """Behavior profile for a resource type"""
    resource_type: str
    normal_patterns: List[Dict]
    typical_frequency: float
    typical_parameters: Dict
    typical_complexity: float
    risk_threshold: float
    sample_count: int


@dataclass
class ClusterResult:
    """Clustering result"""
    cluster_id: int
    resources: List[str]
    centroid: np.ndarray
    outliers: List[str]
    characteristics: Dict


class BehavioralAnalyzer:
    """
    ML-based behavioral analysis for anomaly detection
    
    Responsibilities:
    - Train ML models (Isolation Forest, One-Class SVM, Autoencoder) (Tasks 4.1-4.4)
    - Extract features from triggers (Task 4.5)
    - Detect anomalies using ensemble scoring (Task 4.6)
    - Create behavior profiles for resource types (Task 4.7)
    - Cluster resources and detect outliers (Task 4.8)
    - Detect active exploitation patterns (Task 4.9)
    - Optimize strategies with reinforcement learning (Task 4.10)
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize the Behavioral Analyzer
        
        Args:
            contamination: Expected proportion of outliers (0.0 to 0.5)
        """
        self.logger = get_logger(__name__)
        self.contamination = contamination
        
        # ML Models (Task 4.1)
        self.models = {
            'isolation_forest': None,  # Task 4.2
            'one_class_svm': None,     # Task 4.3
            'autoencoder': None        # Task 4.4 (placeholder for TensorFlow)
        }
        
        # Feature scaler
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Keep 95% variance
        
        # Behavior profiles (Task 4.7)
        self.behavior_profiles: Dict[str, BehaviorProfile] = {}
        
        # Clustering model (Task 4.8)
        self.kmeans = None
        self.optimal_k = 5
        
        # Temporal analysis (Task 4.9)
        self.exploitation_patterns = []
        
        # RL strategy optimizer (Task 4.10)
        self.strategy_rewards = {}
        self.strategy_counts = {}
        
        # Training state
        self.is_trained = False
        self.feature_names = []
        
        self.logger.info("BehavioralAnalyzer initialized with contamination=%.2f", contamination)
    
    def extract_features(self, trigger: Dict) -> np.ndarray:
        """
        Extract features from trigger for ML analysis (Task 4.5)
        
        Features extracted:
        - Frequency metrics
        - Parameter complexity
        - Code length and complexity
        - Cyclomatic complexity estimate
        - Pattern indicators
        
        Args:
            trigger: Trigger dictionary
            
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # 1. Frequency metrics
        event_name = trigger.get('event_name', '')
        # Estimate frequency based on common patterns
        frequency_score = 0.5  # Default
        if 'money' in event_name.lower() or 'bank' in event_name.lower():
            frequency_score = 0.8
        elif 'admin' in event_name.lower():
            frequency_score = 0.3
        features.append(frequency_score)
        
        # 2. Parameter count and complexity
        parameters = trigger.get('parameters', [])
        param_count = len(parameters)
        features.append(param_count)
        
        # Parameter complexity (nested structures, arrays, etc.)
        param_complexity = sum(1 for p in parameters if isinstance(p, (list, dict)))
        features.append(param_complexity)
        
        # 3. Code length
        code = trigger.get('code', '')
        code_length = len(code)
        features.append(code_length)
        
        # Normalized code length (log scale)
        features.append(np.log1p(code_length))
        
        # 4. Cyclomatic complexity estimate
        # Count decision points: if, while, for, and, or
        complexity = (
            code.count('if ') + 
            code.count('while ') + 
            code.count('for ') +
            code.count(' and ') +
            code.count(' or ')
        )
        features.append(complexity)
        
        # 5. Pattern indicators
        # Dangerous patterns
        dangerous_count = sum([
            code.count('TriggerServerEvent'),
            code.count('TriggerClientEvent'),
            code.count('ExecuteCommand'),
            code.count('SetEntityCoords'),
            code.count('GiveWeaponToPed')
        ])
        features.append(dangerous_count)
        
        # Validation patterns
        validation_count = sum([
            code.count('if ') + code.count('then'),
            code.count('IsPlayerAceAllowed'),
            code.count('HasPermission'),
            code.count('CheckAuth')
        ])
        features.append(validation_count)
        
        # 6. Risk score (if available)
        risk_score = trigger.get('risk_score', 0.5)
        features.append(risk_score)
        
        # 7. Callback presence
        has_callback = 1.0 if 'callback' in code.lower() else 0.0
        features.append(has_callback)
        
        # 8. Permission check presence
        has_permission = 1.0 if any(p in code for p in ['permission', 'ace', 'auth', 'admin']) else 0.0
        features.append(has_permission)
        
        # 9. Event type indicators
        is_server_event = 1.0 if 'TriggerServerEvent' in code else 0.0
        is_client_event = 1.0 if 'TriggerClientEvent' in code else 0.0
        features.append(is_server_event)
        features.append(is_client_event)
        
        # 10. Native function count
        native_count = len(re.findall(r'[A-Z][a-z]+[A-Z][a-zA-Z]*\(', code))
        features.append(native_count)
        
        return np.array(features, dtype=np.float32)
    
    def train_models(self, historical_data: List[Dict]) -> None:
        """
        Train ML models with historical data (Task 4.1)
        
        Args:
            historical_data: Historical analysis results (list of trigger dicts)
        """
        if not historical_data:
            self.logger.warning("No historical data provided for training")
            return
        
        self.logger.info("Training ML models with %d samples", len(historical_data))
        
        # Extract features from all samples
        X = np.array([self.extract_features(trigger) for trigger in historical_data])
        
        # Store feature names for reference
        self.feature_names = [
            'frequency_score', 'param_count', 'param_complexity',
            'code_length', 'log_code_length', 'cyclomatic_complexity',
            'dangerous_count', 'validation_count', 'risk_score',
            'has_callback', 'has_permission', 'is_server_event',
            'is_client_event', 'native_count'
        ]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply PCA for dimensionality reduction
        X_reduced = self.pca.fit_transform(X_scaled)
        
        self.logger.info("Feature extraction complete: %d features -> %d components (%.1f%% variance)",
                        X.shape[1], X_reduced.shape[1], self.pca.explained_variance_ratio_.sum() * 100)
        
        # Train Isolation Forest (Task 4.2)
        self.logger.info("Training Isolation Forest...")
        self.models['isolation_forest'] = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        self.models['isolation_forest'].fit(X_reduced)
        
        # Train One-Class SVM (Task 4.3)
        self.logger.info("Training One-Class SVM...")
        self.models['one_class_svm'] = OneClassSVM(
            kernel='rbf',
            gamma='auto',
            nu=self.contamination
        )
        self.models['one_class_svm'].fit(X_reduced)
        
        # Autoencoder placeholder (Task 4.4)
        # Note: Full autoencoder implementation would require TensorFlow/Keras
        # For now, we use PCA as a linear autoencoder approximation
        self.models['autoencoder'] = {
            'type': 'pca_approximation',
            'reconstruction_threshold': self._calculate_reconstruction_threshold(X_scaled, X_reduced)
        }
        
        self.is_trained = True
        self.logger.info("ML pipeline training complete")
    
    def _calculate_reconstruction_threshold(self, X_original: np.ndarray, X_reduced: np.ndarray) -> float:
        """Calculate reconstruction error threshold for anomaly detection"""
        # Reconstruct from reduced dimensions
        X_reconstructed = self.pca.inverse_transform(X_reduced)
        
        # Calculate reconstruction errors
        reconstruction_errors = np.mean((X_original - X_reconstructed) ** 2, axis=1)
        
        # Threshold at 95th percentile
        threshold = np.percentile(reconstruction_errors, 95)
        
        return threshold
    
    def detect_anomalies(self, trigger: Dict) -> Optional[Anomaly]:
        """
        Detect anomalous behavior using ensemble of models (Task 4.6)
        
        Args:
            trigger: Trigger to analyze
            
        Returns:
            Anomaly if detected, None otherwise
        """
        if not self.is_trained:
            self.logger.warning("Models not trained, cannot detect anomalies")
            return None
        
        # Extract and scale features
        features = self.extract_features(trigger)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        features_reduced = self.pca.transform(features_scaled)
        
        # Get predictions from each model
        predictions = {}
        scores = {}
        
        # Isolation Forest (Task 4.2)
        if_pred = self.models['isolation_forest'].predict(features_reduced)[0]
        if_score = self.models['isolation_forest'].score_samples(features_reduced)[0]
        predictions['isolation_forest'] = if_pred
        scores['isolation_forest'] = if_score
        
        # One-Class SVM (Task 4.3)
        svm_pred = self.models['one_class_svm'].predict(features_reduced)[0]
        svm_score = self.models['one_class_svm'].score_samples(features_reduced)[0]
        predictions['one_class_svm'] = svm_pred
        scores['one_class_svm'] = svm_score
        
        # Autoencoder (PCA approximation) (Task 4.4)
        X_reconstructed = self.pca.inverse_transform(features_reduced)
        reconstruction_error = np.mean((features_scaled - X_reconstructed) ** 2)
        ae_threshold = self.models['autoencoder']['reconstruction_threshold']
        ae_pred = -1 if reconstruction_error > ae_threshold else 1
        predictions['autoencoder'] = ae_pred
        scores['autoencoder'] = -reconstruction_error  # Negative because higher error = more anomalous
        
        # Ensemble scoring with weighted combination (Task 4.6)
        weights = {
            'isolation_forest': 0.4,
            'one_class_svm': 0.35,
            'autoencoder': 0.25
        }
        
        # Normalize scores to [0, 1] range (higher = more anomalous)
        normalized_scores = {}
        for model_name, score in scores.items():
            # Convert to anomaly score (higher = more anomalous)
            if model_name == 'autoencoder':
                normalized_scores[model_name] = min(1.0, reconstruction_error / ae_threshold)
            else:
                # For IF and SVM, negative scores indicate anomalies
                normalized_scores[model_name] = 1.0 / (1.0 + np.exp(score))  # Sigmoid
        
        # Calculate weighted ensemble score
        ensemble_score = sum(
            weights[model] * normalized_scores[model]
            for model in weights.keys()
        )
        
        # Determine if anomaly
        detected_by = [model for model, pred in predictions.items() if pred == -1]
        
        if len(detected_by) >= 2 or ensemble_score > 0.7:  # Majority vote or high ensemble score
            # Determine deviation type
            deviation_type = self._determine_deviation_type(trigger, features, normalized_scores)
            
            # Generate explanation
            explanation = self._generate_anomaly_explanation(
                trigger, features, normalized_scores, detected_by
            )
            
            anomaly = Anomaly(
                trigger=trigger,
                anomaly_score=ensemble_score,
                detected_by=detected_by,
                deviation_type=deviation_type,
                explanation=explanation,
                confidence=len(detected_by) / len(predictions),
                features={name: float(val) for name, val in zip(self.feature_names, features)}
            )
            
            self.logger.info("Anomaly detected: %s (score: %.2f, detected by: %s)",
                           trigger.get('event_name', 'unknown'), ensemble_score, detected_by)
            
            return anomaly
        
        return None
    
    def _determine_deviation_type(self, trigger: Dict, features: np.ndarray, 
                                  scores: Dict[str, float]) -> str:
        """Determine the type of deviation"""
        # Analyze which features are most anomalous
        risk_score = features[8]  # risk_score feature
        dangerous_count = features[6]
        validation_count = features[7]
        
        if risk_score > 0.8:
            return "high_risk_pattern"
        elif dangerous_count > 3 and validation_count == 0:
            return "unvalidated_dangerous_operations"
        elif scores.get('isolation_forest', 0) > 0.8:
            return "statistical_outlier"
        elif scores.get('autoencoder', 0) > 0.8:
            return "unusual_feature_combination"
        else:
            return "general_anomaly"
    
    def _generate_anomaly_explanation(self, trigger: Dict, features: np.ndarray,
                                     scores: Dict[str, float], detected_by: List[str]) -> str:
        """Generate human-readable explanation for anomaly"""
        explanations = []
        
        # Check specific features
        if features[6] > 2:  # dangerous_count
            explanations.append(f"High number of dangerous operations ({int(features[6])})")
        
        if features[7] == 0 and features[6] > 0:  # validation_count == 0
            explanations.append("No validation checks found")
        
        if features[8] > 0.7:  # risk_score
            explanations.append(f"High risk score ({features[8]:.2f})")
        
        if features[4] > 8:  # log_code_length (e^8 ≈ 3000 chars)
            explanations.append("Unusually long code")
        
        if features[5] > 10:  # cyclomatic_complexity
            explanations.append(f"High complexity ({int(features[5])} decision points)")
        
        # Add model-specific insights
        if 'isolation_forest' in detected_by:
            explanations.append("Statistical outlier detected")
        
        if 'autoencoder' in detected_by:
            explanations.append("Unusual feature combination")
        
        if not explanations:
            explanations.append("General behavioral anomaly")
        
        return "; ".join(explanations)

    
    def create_behavior_profile(self, resource_type: str, triggers: List[Dict]) -> BehaviorProfile:
        """
        Create normal behavior profile for resource type (Task 4.7)
        
        Args:
            resource_type: Type of resource (bank, shop, admin, etc.)
            triggers: List of triggers from this resource type
            
        Returns:
            Behavior profile
        """
        self.logger.info("Creating behavior profile for resource type: %s", resource_type)
        
        if not triggers:
            self.logger.warning("No triggers provided for profile creation")
            return BehaviorProfile(
                resource_type=resource_type,
                normal_patterns=[],
                typical_frequency=0.0,
                typical_parameters={},
                typical_complexity=0.0,
                risk_threshold=0.5,
                sample_count=0
            )
        
        # Extract features from all triggers
        features_list = [self.extract_features(t) for t in triggers]
        features_array = np.array(features_list)
        
        # Calculate typical values
        typical_frequency = np.mean(features_array[:, 0])  # frequency_score
        typical_param_count = np.mean(features_array[:, 1])  # param_count
        typical_complexity = np.mean(features_array[:, 5])  # cyclomatic_complexity
        typical_risk = np.mean(features_array[:, 8])  # risk_score
        
        # Identify normal patterns
        normal_patterns = []
        for trigger in triggers:
            if trigger.get('risk_score', 0.5) < typical_risk + 0.2:  # Within normal range
                normal_patterns.append({
                    'event_name': trigger.get('event_name', ''),
                    'pattern': trigger.get('code', '')[:100],  # First 100 chars
                    'risk_score': trigger.get('risk_score', 0.5)
                })
        
        # Calculate risk threshold (mean + 1.5 * std)
        risk_threshold = typical_risk + 1.5 * np.std(features_array[:, 8])
        
        profile = BehaviorProfile(
            resource_type=resource_type,
            normal_patterns=normal_patterns[:10],  # Keep top 10
            typical_frequency=float(typical_frequency),
            typical_parameters={
                'param_count': float(typical_param_count),
                'complexity': float(typical_complexity)
            },
            typical_complexity=float(typical_complexity),
            risk_threshold=float(min(risk_threshold, 0.9)),  # Cap at 0.9
            sample_count=len(triggers)
        )
        
        # Store profile
        self.behavior_profiles[resource_type] = profile
        
        self.logger.info("Profile created: %d samples, risk_threshold=%.2f",
                        len(triggers), profile.risk_threshold)
        
        return profile
    
    def cluster_resources(self, resources: List[Dict]) -> List[ClusterResult]:
        """
        Group similar resources and detect outliers (Task 4.8)
        
        Args:
            resources: List of resources with their triggers
            
        Returns:
            List of clustering results
        """
        self.logger.info("Clustering %d resources", len(resources))
        
        if len(resources) < 3:
            self.logger.warning("Too few resources for clustering")
            return []
        
        # Extract aggregate features for each resource
        resource_features = []
        resource_names = []
        
        for resource in resources:
            triggers = resource.get('triggers', [])
            if not triggers:
                continue
            
            # Aggregate features across all triggers in resource
            features_list = [self.extract_features(t) for t in triggers]
            features_array = np.array(features_list)
            
            # Use mean and std as aggregate features
            mean_features = np.mean(features_array, axis=0)
            std_features = np.std(features_array, axis=0)
            aggregate = np.concatenate([mean_features, std_features])
            
            resource_features.append(aggregate)
            resource_names.append(resource.get('name', 'unknown'))
        
        if len(resource_features) < 3:
            self.logger.warning("Not enough valid resources for clustering")
            return []
        
        X = np.array(resource_features)
        
        # Scale features
        X_scaled = StandardScaler().fit_transform(X)
        
        # Determine optimal number of clusters using elbow method
        if len(X) >= 10:
            self.optimal_k = min(5, len(X) // 2)
        else:
            self.optimal_k = min(3, len(X) // 2)
        
        # Perform K-Means clustering
        self.kmeans = KMeans(n_clusters=self.optimal_k, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Detect outliers using distance from centroid
        distances = self.kmeans.transform(X_scaled)
        min_distances = np.min(distances, axis=1)
        outlier_threshold = np.percentile(min_distances, 90)
        
        # Group results by cluster
        results = []
        for cluster_id in range(self.optimal_k):
            cluster_mask = cluster_labels == cluster_id
            cluster_resources = [name for name, mask in zip(resource_names, cluster_mask) if mask]
            cluster_distances = min_distances[cluster_mask]
            
            # Identify outliers in this cluster
            outliers = [
                name for name, dist in zip(cluster_resources, cluster_distances)
                if dist > outlier_threshold
            ]
            
            # Determine cluster characteristics
            cluster_features = X_scaled[cluster_mask]
            characteristics = self._analyze_cluster_characteristics(cluster_features)
            
            result = ClusterResult(
                cluster_id=cluster_id,
                resources=cluster_resources,
                centroid=self.kmeans.cluster_centers_[cluster_id],
                outliers=outliers,
                characteristics=characteristics
            )
            results.append(result)
        
        self.logger.info("Clustering complete: %d clusters, %d total outliers",
                        self.optimal_k, sum(len(r.outliers) for r in results))
        
        return results
    
    def _analyze_cluster_characteristics(self, cluster_features: np.ndarray) -> Dict:
        """Analyze characteristics of a cluster"""
        mean_features = np.mean(cluster_features, axis=0)
        
        # Interpret first few features (before std features)
        n_original = len(mean_features) // 2
        
        characteristics = {
            'avg_frequency': float(mean_features[0]) if n_original > 0 else 0.0,
            'avg_param_count': float(mean_features[1]) if n_original > 1 else 0.0,
            'avg_complexity': float(mean_features[5]) if n_original > 5 else 0.0,
            'avg_risk': float(mean_features[8]) if n_original > 8 else 0.0,
            'size': len(cluster_features)
        }
        
        # Classify cluster
        if characteristics['avg_risk'] > 0.7:
            characteristics['classification'] = 'high_risk'
        elif characteristics['avg_risk'] > 0.5:
            characteristics['classification'] = 'medium_risk'
        else:
            characteristics['classification'] = 'low_risk'
        
        return characteristics
    
    def detect_active_exploitation(self, event_sequence: List[Dict]) -> Tuple[bool, Dict]:
        """
        Detect active exploitation patterns via temporal analysis (Task 4.9)
        
        Args:
            event_sequence: Sequence of events with timestamps
            
        Returns:
            Tuple of (is_exploiting, analysis_details)
        """
        self.logger.info("Analyzing event sequence for active exploitation (%d events)",
                        len(event_sequence))
        
        if len(event_sequence) < 3:
            return False, {'reason': 'insufficient_events'}
        
        analysis = {
            'total_events': len(event_sequence),
            'suspicious_patterns': [],
            'risk_score': 0.0,
            'indicators': []
        }
        
        # 1. Check for rapid-fire events (potential automation)
        timestamps = [e.get('timestamp', 0) for e in event_sequence if 'timestamp' in e]
        if len(timestamps) >= 2:
            time_diffs = np.diff(timestamps)
            avg_interval = np.mean(time_diffs)
            
            if avg_interval < 0.1:  # Less than 100ms between events
                analysis['suspicious_patterns'].append('rapid_fire_events')
                analysis['indicators'].append(f'Average interval: {avg_interval:.3f}s')
                analysis['risk_score'] += 0.3
        
        # 2. Check for repeated high-risk events
        high_risk_events = [e for e in event_sequence if e.get('risk_score', 0) > 0.7]
        if len(high_risk_events) > len(event_sequence) * 0.5:
            analysis['suspicious_patterns'].append('high_risk_concentration')
            analysis['indicators'].append(f'{len(high_risk_events)} high-risk events')
            analysis['risk_score'] += 0.4
        
        # 3. Check for money/economy manipulation patterns
        money_events = [
            e for e in event_sequence
            if any(keyword in e.get('event_name', '').lower() 
                  for keyword in ['money', 'bank', 'cash', 'economy', 'balance'])
        ]
        if len(money_events) > 3:
            analysis['suspicious_patterns'].append('economy_manipulation')
            analysis['indicators'].append(f'{len(money_events)} economy-related events')
            analysis['risk_score'] += 0.3
        
        # 4. Check for teleportation/god mode patterns
        exploit_keywords = ['teleport', 'coords', 'invincible', 'god', 'noclip', 'weapon']
        exploit_events = [
            e for e in event_sequence
            if any(keyword in e.get('event_name', '').lower() for keyword in exploit_keywords)
        ]
        if len(exploit_events) > 2:
            analysis['suspicious_patterns'].append('exploit_usage')
            analysis['indicators'].append(f'{len(exploit_events)} exploit-related events')
            analysis['risk_score'] += 0.4
        
        # 5. Check for escalating risk pattern
        risk_scores = [e.get('risk_score', 0) for e in event_sequence]
        if len(risk_scores) >= 3:
            # Check if risk is increasing over time
            first_half_avg = np.mean(risk_scores[:len(risk_scores)//2])
            second_half_avg = np.mean(risk_scores[len(risk_scores)//2:])
            
            if second_half_avg > first_half_avg + 0.2:
                analysis['suspicious_patterns'].append('escalating_risk')
                analysis['indicators'].append('Risk increasing over time')
                analysis['risk_score'] += 0.2
        
        # 6. Check for lack of validation
        unvalidated_count = sum(
            1 for e in event_sequence
            if 'validation' not in e.get('code', '').lower() and
               'permission' not in e.get('code', '').lower()
        )
        if unvalidated_count > len(event_sequence) * 0.7:
            analysis['suspicious_patterns'].append('missing_validation')
            analysis['indicators'].append(f'{unvalidated_count} unvalidated events')
            analysis['risk_score'] += 0.2
        
        # Determine if active exploitation
        is_exploiting = (
            analysis['risk_score'] > 0.7 or
            len(analysis['suspicious_patterns']) >= 3
        )
        
        if is_exploiting:
            self.logger.warning("Active exploitation detected! Risk: %.2f, Patterns: %s",
                              analysis['risk_score'], analysis['suspicious_patterns'])
        
        return is_exploiting, analysis
    
    def optimize_strategy(self, strategy: str, success: bool, reward: float) -> str:
        """
        Optimize exploitation strategies using reinforcement learning (Task 4.10)
        
        Uses Thompson Sampling (Multi-Armed Bandit) approach
        
        Args:
            strategy: Strategy name that was used
            success: Whether the strategy succeeded
            reward: Reward value (0.0 to 1.0)
            
        Returns:
            Recommended strategy for next attempt
        """
        # Initialize strategy if not seen before
        if strategy not in self.strategy_rewards:
            self.strategy_rewards[strategy] = []
            self.strategy_counts[strategy] = 0
        
        # Record result
        self.strategy_rewards[strategy].append(reward if success else 0.0)
        self.strategy_counts[strategy] += 1
        
        self.logger.info("Strategy '%s' result: success=%s, reward=%.2f",
                        strategy, success, reward)
        
        # Thompson Sampling: sample from Beta distribution for each strategy
        available_strategies = list(self.strategy_rewards.keys())
        
        if len(available_strategies) == 1:
            return strategy  # Only one strategy known
        
        # Calculate Beta parameters (alpha, beta) for each strategy
        best_strategy = strategy
        best_sample = 0.0
        
        for strat in available_strategies:
            rewards = self.strategy_rewards[strat]
            successes = sum(1 for r in rewards if r > 0)
            failures = len(rewards) - successes
            
            # Beta distribution parameters (add 1 for prior)
            alpha = successes + 1
            beta = failures + 1
            
            # Sample from Beta distribution
            sample = np.random.beta(alpha, beta)
            
            if sample > best_sample:
                best_sample = sample
                best_strategy = strat
        
        self.logger.info("Recommended strategy: %s (sample: %.3f)", best_strategy, best_sample)
        
        return best_strategy
    
    def get_strategy_statistics(self) -> Dict[str, Dict]:
        """Get statistics for all strategies"""
        stats = {}
        
        for strategy, rewards in self.strategy_rewards.items():
            if not rewards:
                continue
            
            successes = sum(1 for r in rewards if r > 0)
            stats[strategy] = {
                'attempts': len(rewards),
                'successes': successes,
                'success_rate': successes / len(rewards),
                'avg_reward': np.mean(rewards),
                'total_reward': sum(rewards)
            }
        
        return stats
    
    def save_models(self, filepath: str) -> None:
        """Save trained models to file"""
        import pickle
        
        model_data = {
            'models': self.models,
            'scaler': self.scaler,
            'pca': self.pca,
            'behavior_profiles': self.behavior_profiles,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'strategy_rewards': self.strategy_rewards,
            'strategy_counts': self.strategy_counts
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info("Models saved to %s", filepath)
    
    def load_models(self, filepath: str) -> None:
        """Load trained models from file"""
        import pickle
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.models = model_data['models']
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.behavior_profiles = model_data['behavior_profiles']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        self.strategy_rewards = model_data.get('strategy_rewards', {})
        self.strategy_counts = model_data.get('strategy_counts', {})
        
        self.logger.info("Models loaded from %s", filepath)
