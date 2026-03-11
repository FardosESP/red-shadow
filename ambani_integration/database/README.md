# Database Module

This module provides database schema and operations for storing analysis history and learning feedback for the Ambani Integration system.

## Overview

The database uses SQLite to store:
- **Analysis History**: Historical analysis results for ML training
- **Stop Decisions**: Auto-stop decisions made by the Auto Stop Engine
- **Admin Feedback**: Administrator feedback for learning and threshold adjustment
- **Anticheat Detections**: Detected anticheats and their profiles
- **Statistics**: Performance metrics (TP, FP, TN, FN, precision, recall, F1, accuracy)

## Database Schema

### Tables

#### 1. analysis_history
Stores analysis results for ML training by the Behavioral Analyzer.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Analysis timestamp |
| server_name | TEXT | Server name |
| resource_name | TEXT | Resource name |
| resource_type | TEXT | Resource type (bank, shop, admin, etc.) |
| risk_score | INTEGER | Risk score (0-100) |
| vulnerabilities_count | INTEGER | Total vulnerabilities |
| critical_vulns | INTEGER | Critical vulnerabilities |
| high_vulns | INTEGER | High severity vulnerabilities |
| medium_vulns | INTEGER | Medium severity vulnerabilities |
| low_vulns | INTEGER | Low severity vulnerabilities |
| exploit_vectors | TEXT | JSON array of exploit vectors |
| trigger_data | TEXT | JSON object with trigger details |
| anticheat_detected | TEXT | JSON array of detected anticheats |
| analysis_result | TEXT | JSON object with full analysis result |
| created_at | DATETIME | Record creation timestamp |

**Indexes**: `idx_analysis_timestamp`, `idx_analysis_resource`

#### 2. stop_decisions
Stores auto-stop decisions made by the Auto Stop Engine.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Decision timestamp |
| resource_name | TEXT | Resource name |
| stop_confidence | REAL | Stop confidence score (0.0-1.0) |
| risk_score | INTEGER | Risk score |
| critical_vulns | INTEGER | Number of critical vulnerabilities |
| active_exploits | BOOLEAN | Active exploits detected |
| false_positive_rate | REAL | Historical FP rate |
| mode | TEXT | Engine mode (manual, notify, auto) |
| requires_confirmation | BOOLEAN | Requires admin confirmation |
| executed | BOOLEAN | Whether decision was executed |
| execution_result | TEXT | JSON object with execution result |
| reasons | TEXT | JSON array of reasons |
| created_at | DATETIME | Record creation timestamp |

**Indexes**: `idx_stop_timestamp`, `idx_stop_resource`

#### 3. admin_feedback
Stores administrator feedback for learning mode.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Feedback timestamp |
| decision_id | INTEGER | Foreign key to stop_decisions |
| resource_name | TEXT | Resource name |
| feedback_type | TEXT | Type of feedback |
| approved | BOOLEAN | Whether admin approved the decision |
| comment | TEXT | Admin comment |
| action_taken | TEXT | Action taken by admin |
| outcome | TEXT | Outcome of the action |
| created_at | DATETIME | Record creation timestamp |

**Indexes**: `idx_feedback_decision`

**Foreign Keys**: `decision_id` → `stop_decisions(id)`

#### 4. anticheat_detections
Stores detected anticheats and their profiles.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Detection timestamp |
| server_name | TEXT | Server name |
| anticheat_name | TEXT | Anticheat name |
| anticheat_version | TEXT | Anticheat version |
| confidence | REAL | Detection confidence (0.0-1.0) |
| capabilities | TEXT | JSON array of capabilities |
| bypass_difficulty | REAL | Bypass difficulty (0.0-1.0) |
| detection_method | TEXT | Detection method used |
| profile_data | TEXT | JSON object with full profile |
| created_at | DATETIME | Record creation timestamp |

**Indexes**: `idx_anticheat_name`

#### 5. statistics
Stores performance metrics for the Auto Stop Engine.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Statistics timestamp |
| metric_type | TEXT | Type of metric (auto_stop, etc.) |
| true_positives | INTEGER | True positives count |
| false_positives | INTEGER | False positives count |
| true_negatives | INTEGER | True negatives count |
| false_negatives | INTEGER | False negatives count |
| precision | REAL | Precision metric |
| recall | REAL | Recall metric |
| f1_score | REAL | F1 score |
| accuracy | REAL | Accuracy metric |
| period_start | DATETIME | Period start |
| period_end | DATETIME | Period end |
| created_at | DATETIME | Record creation timestamp |

## Usage

### Initialize Database

```python
from ambani_integration.database import init_database

# Initialize database with default path
db = init_database()

# Or specify custom path
db = init_database("./custom/path/database.db")
```

### Store Analysis Result

```python
from ambani_integration.database import DatabaseManager

db = DatabaseManager()
db.connect()

analysis_data = {
    'server_name': 'MyServer',
    'resource_name': 'bank_robbery',
    'resource_type': 'bank',
    'risk_score': 95,
    'vulnerabilities_count': 5,
    'critical_vulns': 3,
    'high_vulns': 2,
    'medium_vulns': 0,
    'low_vulns': 0,
    'exploit_vectors': [
        {'type': 'event_injection', 'severity': 'CRITICAL'},
        {'type': 'callback_exploit', 'severity': 'HIGH'}
    ],
    'trigger_data': {
        'event_name': 'giveMoney',
        'has_validation': False
    }
}

record_id = db.store_analysis_result(analysis_data)
```

### Store Stop Decision

```python
decision_data = {
    'resource_name': 'bank_robbery',
    'stop_confidence': 0.92,
    'risk_score': 95,
    'critical_vulns': 3,
    'active_exploits': True,
    'false_positive_rate': 0.05,
    'mode': 'auto',
    'requires_confirmation': False,
    'reasons': [
        'Risk score >= 85',
        'Multiple critical vulnerabilities',
        'Active exploits detected'
    ]
}

decision_id = db.store_stop_decision(decision_data)
```

### Store Admin Feedback

```python
feedback_data = {
    'decision_id': decision_id,
    'resource_name': 'bank_robbery',
    'feedback_type': 'auto_stop_review',
    'approved': True,
    'comment': 'Correct decision, resource was vulnerable',
    'action_taken': 'kept_stopped',
    'outcome': 'true_positive'
}

feedback_id = db.store_admin_feedback(feedback_data)
```

### Get Historical Data for ML Training

```python
# Get all historical analyses
historical_data = db.get_historical_analyses(limit=1000)

# Get analyses for specific resource type
bank_analyses = db.get_historical_analyses(resource_type='bank', limit=500)

# Get feedback for learning
learning_data = db.get_feedback_for_learning()
```

### Calculate False Positive Rate

```python
# Overall FP rate
fp_rate = db.calculate_false_positive_rate()

# FP rate for specific resource type
bank_fp_rate = db.calculate_false_positive_rate(resource_type='bank')
```

### Store and Retrieve Statistics

```python
# Store statistics
stats_data = {
    'metric_type': 'auto_stop',
    'true_positives': 45,
    'false_positives': 5,
    'true_negatives': 30,
    'false_negatives': 2,
    'period_start': '2024-01-01 00:00:00',
    'period_end': '2024-01-31 23:59:59'
}

stats_id = db.store_statistics(stats_data)

# Get latest statistics
latest_stats = db.get_latest_statistics('auto_stop')
print(f"Precision: {latest_stats['precision']:.2f}")
print(f"Recall: {latest_stats['recall']:.2f}")
print(f"F1 Score: {latest_stats['f1_score']:.2f}")

# Get statistics history
stats_history = db.get_statistics_history('auto_stop', limit=10)
```

## Integration with Other Components

### Auto Stop Engine

The Auto Stop Engine uses the database to:
- Store stop decisions
- Retrieve admin feedback for learning
- Calculate false positive rates
- Track statistics (TP, FP, TN, FN)

```python
from ambani_integration.execution import AutoStopEngine
from ambani_integration.database import DatabaseManager

engine = AutoStopEngine(mode='auto')
db = DatabaseManager()
db.connect()

# Make decision
decision = engine.evaluate_resource(resource_data)

# Store decision
decision_id = db.store_stop_decision({
    'resource_name': decision.resource_name,
    'stop_confidence': decision.stop_confidence,
    'reasons': decision.reasons,
    # ... other fields
})

# Later, admin provides feedback
db.store_admin_feedback({
    'decision_id': decision_id,
    'approved': True,
    'outcome': 'true_positive'
})

# Engine learns from feedback
learning_data = db.get_feedback_for_learning()
engine.learn_from_feedback(learning_data)
```

### Behavioral Analyzer

The Behavioral Analyzer uses the database to:
- Retrieve historical analysis data for ML training
- Store new analysis results

```python
from ambani_integration.analysis import BehavioralAnalyzer
from ambani_integration.database import DatabaseManager

analyzer = BehavioralAnalyzer()
db = DatabaseManager()
db.connect()

# Get historical data for training
historical_data = db.get_historical_analyses(limit=5000)

# Train models
analyzer.train_models(historical_data)

# Store new analysis
db.store_analysis_result(new_analysis_data)
```

### Anticheat Analyzer

The Anticheat Analyzer uses the database to:
- Store detected anticheats
- Retrieve historical detections

```python
from ambani_integration.analysis import AnticheatAnalyzer
from ambani_integration.database import DatabaseManager

analyzer = AnticheatAnalyzer()
db = DatabaseManager()
db.connect()

# Detect anticheats
profiles = analyzer.detect_anticheats(code_base)

# Store detections
for profile in profiles:
    db.store_anticheat_detection({
        'server_name': 'MyServer',
        'anticheat_name': profile.name,
        'anticheat_version': profile.version,
        'confidence': profile.confidence,
        'capabilities': profile.capabilities,
        'bypass_difficulty': profile.bypass_difficulty,
        'detection_method': 'signature_matching',
        'profile_data': profile.to_dict()
    })
```

## Configuration

The database path is configured in `ambani_integration/config/settings.py`:

```python
"database": {
    "path": "./data/ambani_integration.db",
    "connection_string": None,  # Optional: for external databases
    "pool_size": 5,
    "timeout": 30
}
```

Access via ConfigManager:

```python
from ambani_integration.config import ConfigManager

config = ConfigManager()
db_path = config.database_path
```

## Performance Considerations

- **Indexes**: Created on frequently queried columns (timestamp, resource_name, decision_id)
- **JSON Storage**: Complex data stored as JSON for flexibility
- **Connection Management**: Use `connect()` and `close()` appropriately
- **Batch Operations**: For bulk inserts, consider using transactions

## Future Enhancements

- Migration to PostgreSQL for production deployments
- Connection pooling for concurrent access
- Automatic backup and archival
- Data retention policies
- Query optimization for large datasets
