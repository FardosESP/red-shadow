"""
Database Schema
SQLite database schema for analysis history and learning feedback
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for analysis history and learning feedback
    
    Responsibilities:
    - Create and manage database schema
    - Store analysis results for ML training
    - Store stop decisions and admin feedback
    - Track anticheat detections
    - Maintain statistics (TP, FP, TN, FN)
    """
    
    def __init__(self, db_path: str = "./data/ambani_integration.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self.connection = None
        
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """
        Connect to database
        
        Returns:
            Database connection
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def init_schema(self):
        """Initialize database schema"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Analysis History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                server_name TEXT,
                resource_name TEXT,
                resource_type TEXT,
                risk_score INTEGER,
                vulnerabilities_count INTEGER,
                critical_vulns INTEGER,
                high_vulns INTEGER,
                medium_vulns INTEGER,
                low_vulns INTEGER,
                exploit_vectors TEXT,
                trigger_data TEXT,
                anticheat_detected TEXT,
                analysis_result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Stop Decisions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stop_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resource_name TEXT NOT NULL,
                stop_confidence REAL NOT NULL,
                risk_score INTEGER,
                critical_vulns INTEGER,
                active_exploits BOOLEAN,
                false_positive_rate REAL,
                mode TEXT,
                requires_confirmation BOOLEAN,
                executed BOOLEAN DEFAULT FALSE,
                execution_result TEXT,
                reasons TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Admin Feedback Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                decision_id INTEGER,
                resource_name TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                approved BOOLEAN NOT NULL,
                comment TEXT,
                action_taken TEXT,
                outcome TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (decision_id) REFERENCES stop_decisions(id)
            )
        """)
        
        # Anticheat Detections Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anticheat_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                server_name TEXT,
                anticheat_name TEXT NOT NULL,
                anticheat_version TEXT,
                confidence REAL,
                capabilities TEXT,
                bypass_difficulty REAL,
                detection_method TEXT,
                profile_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Statistics Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                true_positives INTEGER DEFAULT 0,
                false_positives INTEGER DEFAULT 0,
                true_negatives INTEGER DEFAULT 0,
                false_negatives INTEGER DEFAULT 0,
                precision REAL,
                recall REAL,
                f1_score REAL,
                accuracy REAL,
                period_start DATETIME,
                period_end DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_timestamp 
            ON analysis_history(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_resource 
            ON analysis_history(resource_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stop_timestamp 
            ON stop_decisions(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stop_resource 
            ON stop_decisions(resource_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_decision 
            ON admin_feedback(decision_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_anticheat_name 
            ON anticheat_detections(anticheat_name)
        """)
        
        conn.commit()
        logger.info(f"Database schema initialized at {self.db_path}")
    
    # ========================================================================
    # Analysis History Operations
    # ========================================================================
    
    def store_analysis_result(self, analysis_data: Dict) -> int:
        """
        Store analysis result for ML training
        
        Args:
            analysis_data: Analysis result data
            
        Returns:
            ID of inserted record
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_history (
                timestamp, server_name, resource_name, resource_type,
                risk_score, vulnerabilities_count, critical_vulns,
                high_vulns, medium_vulns, low_vulns, exploit_vectors,
                trigger_data, anticheat_detected, analysis_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_data.get('timestamp', datetime.now().isoformat()),
            analysis_data.get('server_name'),
            analysis_data.get('resource_name'),
            analysis_data.get('resource_type'),
            analysis_data.get('risk_score'),
            analysis_data.get('vulnerabilities_count'),
            analysis_data.get('critical_vulns'),
            analysis_data.get('high_vulns'),
            analysis_data.get('medium_vulns'),
            analysis_data.get('low_vulns'),
            json.dumps(analysis_data.get('exploit_vectors', [])),
            json.dumps(analysis_data.get('trigger_data', {})),
            json.dumps(analysis_data.get('anticheat_detected', [])),
            json.dumps(analysis_data.get('analysis_result', {}))
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_historical_analyses(self, 
                                resource_type: Optional[str] = None,
                                limit: Optional[int] = None) -> List[Dict]:
        """
        Get historical analysis results for ML training
        
        Args:
            resource_type: Filter by resource type
            limit: Maximum number of records
            
        Returns:
            List of analysis results
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM analysis_history"
        params = []
        
        if resource_type:
            query += " WHERE resource_type = ?"
            params.append(resource_type)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            result['exploit_vectors'] = json.loads(result['exploit_vectors']) if result['exploit_vectors'] else []
            result['trigger_data'] = json.loads(result['trigger_data']) if result['trigger_data'] else {}
            result['anticheat_detected'] = json.loads(result['anticheat_detected']) if result['anticheat_detected'] else []
            result['analysis_result'] = json.loads(result['analysis_result']) if result['analysis_result'] else {}
            results.append(result)
        
        return results
    
    # ========================================================================
    # Stop Decisions Operations
    # ========================================================================
    
    def store_stop_decision(self, decision_data: Dict) -> int:
        """
        Store stop decision
        
        Args:
            decision_data: Stop decision data
            
        Returns:
            ID of inserted record
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO stop_decisions (
                timestamp, resource_name, stop_confidence, risk_score,
                critical_vulns, active_exploits, false_positive_rate,
                mode, requires_confirmation, executed, execution_result, reasons
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision_data.get('timestamp', datetime.now().isoformat()),
            decision_data.get('resource_name'),
            decision_data.get('stop_confidence'),
            decision_data.get('risk_score'),
            decision_data.get('critical_vulns'),
            decision_data.get('active_exploits', False),
            decision_data.get('false_positive_rate'),
            decision_data.get('mode'),
            decision_data.get('requires_confirmation', False),
            decision_data.get('executed', False),
            json.dumps(decision_data.get('execution_result', {})),
            json.dumps(decision_data.get('reasons', []))
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_stop_decision_execution(self, decision_id: int, 
                                      executed: bool, 
                                      result: Dict):
        """
        Update stop decision execution status
        
        Args:
            decision_id: Decision ID
            executed: Whether decision was executed
            result: Execution result
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE stop_decisions 
            SET executed = ?, execution_result = ?
            WHERE id = ?
        """, (executed, json.dumps(result), decision_id))
        
        conn.commit()
    
    def get_stop_decisions(self, 
                          resource_name: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict]:
        """
        Get stop decisions
        
        Args:
            resource_name: Filter by resource name
            limit: Maximum number of records
            
        Returns:
            List of stop decisions
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM stop_decisions"
        params = []
        
        if resource_name:
            query += " WHERE resource_name = ?"
            params.append(resource_name)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            result['execution_result'] = json.loads(result['execution_result']) if result['execution_result'] else {}
            result['reasons'] = json.loads(result['reasons']) if result['reasons'] else []
            results.append(result)
        
        return results
    
    # ========================================================================
    # Admin Feedback Operations
    # ========================================================================
    
    def store_admin_feedback(self, feedback_data: Dict) -> int:
        """
        Store admin feedback for learning
        
        Args:
            feedback_data: Admin feedback data
            
        Returns:
            ID of inserted record
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO admin_feedback (
                timestamp, decision_id, resource_name, feedback_type,
                approved, comment, action_taken, outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback_data.get('timestamp', datetime.now().isoformat()),
            feedback_data.get('decision_id'),
            feedback_data.get('resource_name'),
            feedback_data.get('feedback_type'),
            feedback_data.get('approved'),
            feedback_data.get('comment'),
            feedback_data.get('action_taken'),
            feedback_data.get('outcome')
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_admin_feedback(self, 
                          decision_id: Optional[int] = None,
                          limit: Optional[int] = None) -> List[Dict]:
        """
        Get admin feedback
        
        Args:
            decision_id: Filter by decision ID
            limit: Maximum number of records
            
        Returns:
            List of admin feedback
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM admin_feedback"
        params = []
        
        if decision_id:
            query += " WHERE decision_id = ?"
            params.append(decision_id)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_feedback_for_learning(self) -> List[Dict]:
        """
        Get feedback data for ML learning
        
        Returns:
            List of decisions with feedback for training
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sd.*,
                af.approved,
                af.feedback_type,
                af.outcome
            FROM stop_decisions sd
            INNER JOIN admin_feedback af ON sd.id = af.decision_id
            ORDER BY sd.timestamp DESC
        """)
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            result['execution_result'] = json.loads(result['execution_result']) if result['execution_result'] else {}
            result['reasons'] = json.loads(result['reasons']) if result['reasons'] else []
            results.append(result)
        
        return results
    
    # ========================================================================
    # Anticheat Detections Operations
    # ========================================================================
    
    def store_anticheat_detection(self, detection_data: Dict) -> int:
        """
        Store anticheat detection
        
        Args:
            detection_data: Anticheat detection data
            
        Returns:
            ID of inserted record
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO anticheat_detections (
                timestamp, server_name, anticheat_name, anticheat_version,
                confidence, capabilities, bypass_difficulty, detection_method,
                profile_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            detection_data.get('timestamp', datetime.now().isoformat()),
            detection_data.get('server_name'),
            detection_data.get('anticheat_name'),
            detection_data.get('anticheat_version'),
            detection_data.get('confidence'),
            json.dumps(detection_data.get('capabilities', [])),
            detection_data.get('bypass_difficulty'),
            detection_data.get('detection_method'),
            json.dumps(detection_data.get('profile_data', {}))
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_anticheat_detections(self, 
                                 server_name: Optional[str] = None,
                                 limit: Optional[int] = None) -> List[Dict]:
        """
        Get anticheat detections
        
        Args:
            server_name: Filter by server name
            limit: Maximum number of records
            
        Returns:
            List of anticheat detections
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM anticheat_detections"
        params = []
        
        if server_name:
            query += " WHERE server_name = ?"
            params.append(server_name)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = dict(row)
            result['capabilities'] = json.loads(result['capabilities']) if result['capabilities'] else []
            result['profile_data'] = json.loads(result['profile_data']) if result['profile_data'] else {}
            results.append(result)
        
        return results
    
    # ========================================================================
    # Statistics Operations
    # ========================================================================
    
    def store_statistics(self, stats_data: Dict) -> int:
        """
        Store statistics (TP, FP, TN, FN)
        
        Args:
            stats_data: Statistics data
            
        Returns:
            ID of inserted record
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate derived metrics
        tp = stats_data.get('true_positives', 0)
        fp = stats_data.get('false_positives', 0)
        tn = stats_data.get('true_negatives', 0)
        fn = stats_data.get('false_negatives', 0)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
        
        cursor.execute("""
            INSERT INTO statistics (
                timestamp, metric_type, true_positives, false_positives,
                true_negatives, false_negatives, precision, recall,
                f1_score, accuracy, period_start, period_end
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stats_data.get('timestamp', datetime.now().isoformat()),
            stats_data.get('metric_type', 'auto_stop'),
            tp, fp, tn, fn,
            precision, recall, f1_score, accuracy,
            stats_data.get('period_start'),
            stats_data.get('period_end')
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_latest_statistics(self, metric_type: str = 'auto_stop') -> Optional[Dict]:
        """
        Get latest statistics
        
        Args:
            metric_type: Type of metric
            
        Returns:
            Latest statistics or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM statistics
            WHERE metric_type = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (metric_type,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_statistics_history(self, 
                               metric_type: str = 'auto_stop',
                               limit: Optional[int] = None) -> List[Dict]:
        """
        Get statistics history
        
        Args:
            metric_type: Type of metric
            limit: Maximum number of records
            
        Returns:
            List of statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM statistics
            WHERE metric_type = ?
            ORDER BY timestamp DESC
        """
        params = [metric_type]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def calculate_false_positive_rate(self, resource_type: Optional[str] = None) -> float:
        """
        Calculate historical false positive rate
        
        Args:
            resource_type: Filter by resource type
            
        Returns:
            False positive rate (0.0-1.0)
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get decisions with feedback
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN af.approved = 0 THEN 1 ELSE 0 END) as false_positives
            FROM stop_decisions sd
            INNER JOIN admin_feedback af ON sd.id = af.decision_id
        """
        
        if resource_type:
            query += """
                INNER JOIN analysis_history ah ON sd.resource_name = ah.resource_name
                WHERE ah.resource_type = ?
            """
            cursor.execute(query, (resource_type,))
        else:
            cursor.execute(query)
        
        row = cursor.fetchone()
        
        if row and row['total'] > 0:
            return row['false_positives'] / row['total']
        
        return 0.0


def init_database(db_path: str = "./data/ambani_integration.db") -> DatabaseManager:
    """
    Initialize database with schema
    
    Args:
        db_path: Path to database file
        
    Returns:
        DatabaseManager instance
    """
    db = DatabaseManager(db_path)
    db.init_schema()
    return db
