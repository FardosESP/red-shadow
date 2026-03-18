# Requirements Document: DESTROYER v4 Offline Analysis with RP Location Detection

## Introduction

This document specifies the requirements for extending the RED-SHADOW DESTROYER v4 FiveM security analysis tool with a new RP Location Detection capability (Phase 17). The system performs offline static analysis of Lua dump files to identify roleplay locations, classify activities, assess exploitation risks, and integrate results into the existing web dashboard. All analysis is performed locally without network requests to maintain undetectable operation.

## Glossary

- **DESTROYER_Engine**: The main RedShadowV4 analysis engine that orchestrates all 17 analysis phases
- **Location_Detector**: Component responsible for detecting and classifying RP locations in Lua code
- **Coordinate_Extractor**: Pattern matching component that extracts coordinate data from various Lua formats
- **Activity_Classifier**: Component that classifies location activities using keyword analysis
- **Risk_Scorer**: Component that calculates exploitation risk scores for detected locations
- **RPLocation**: Data model representing a detected roleplay location with coordinates, activity type, and metadata
- **Web_Dashboard**: Flask-based web interface for displaying analysis results
- **Lua_Dump**: Collection of decompiled Lua files from a FiveM server
- **Offline_Analysis**: Static code analysis performed without network requests or API calls
- **Exploitation_Risk**: Numerical score (0-100) indicating how valuable a location is as an attack target
- **Activity_Type**: Classification of what happens at a location (drug operations, jobs, shops, services)
- **Location_Metadata**: Additional location data (radius, blip, marker, zone information)

## Requirements

### Requirement 1: Coordinate Extraction

**User Story:** As a security analyst, I want to extract all coordinate patterns from Lua dump files, so that I can identify where roleplay activities occur on the server map.

#### Acceptance Criteria

1. WHEN analyzing Lua code THEN THE Coordinate_Extractor SHALL detect vector3(x, y, z) coordinate patterns
2. WHEN analyzing Lua code THEN THE Coordinate_Extractor SHALL detect vector2(x, y) coordinate patterns and convert to 3D with z=0
3. WHEN analyzing Lua code THEN THE Coordinate_Extractor SHALL detect table format coordinates {x=..., y=..., z=...}
4. WHEN analyzing Lua code THEN THE Coordinate_Extractor SHALL detect Config.Locations array patterns
5. WHEN a coordinate pattern is detected THEN THE Coordinate_Extractor SHALL extract the file path and line number
6. WHEN a coordinate pattern is detected THEN THE Coordinate_Extractor SHALL extract surrounding code context (10 lines)
7. WHEN coordinate values contain decimals or negative numbers THEN THE Coordinate_Extractor SHALL parse them correctly
8. WHEN coordinate patterns are malformed THEN THE Coordinate_Extractor SHALL skip them and continue processing

### Requirement 2: Activity Classification

**User Story:** As a security analyst, I want to classify what activities occur at detected locations, so that I can understand the server's economy and identify high-value targets.

#### Acceptance Criteria

1. WHEN classifying a location THEN THE Activity_Classifier SHALL analyze surrounding code context for activity keywords
2. WHEN drug-related keywords are detected THEN THE Activity_Classifier SHALL classify as drug_planting, drug_processing, or drug_selling
3. WHEN job-related keywords are detected THEN THE Activity_Classifier SHALL classify as job_mining, job_fishing, job_farming, job_trucking, job_taxi, or job_mechanic
4. WHEN shop-related keywords are detected THEN THE Activity_Classifier SHALL classify as shop_weapon, shop_clothing, shop_vehicle, or shop_general
5. WHEN service-related keywords are detected THEN THE Activity_Classifier SHALL classify as service_atm, service_bank, service_garage, service_hospital, or service_police
6. WHEN multiple activity keywords are present THEN THE Activity_Classifier SHALL prioritize drug operations over other activities
7. WHEN no activity keywords are detected THEN THE Activity_Classifier SHALL classify as unknown with confidence <= 0.3
8. WHEN classifying activities THEN THE Activity_Classifier SHALL support both Spanish and English keywords
9. WHEN an activity is classified THEN THE Activity_Classifier SHALL return a confidence score between 0.0 and 1.0
10. WHEN more matching keywords are found THEN THE Activity_Classifier SHALL increase confidence score up to maximum 1.0

### Requirement 3: Location Metadata Parsing

**User Story:** As a security analyst, I want to extract location metadata from code context, so that I can understand interaction mechanics and visual indicators.

#### Acceptance Criteria

1. WHEN parsing location context THEN THE Location_Detector SHALL extract radius values if present
2. WHEN parsing location context THEN THE Location_Detector SHALL extract blip sprite IDs if present
3. WHEN parsing location context THEN THE Location_Detector SHALL extract blip color IDs if present
4. WHEN parsing location context THEN THE Location_Detector SHALL extract blip names if present
5. WHEN parsing location context THEN THE Location_Detector SHALL extract marker type IDs if present
6. WHEN parsing location context THEN THE Location_Detector SHALL extract marker color RGBA values if present
7. WHEN parsing location context THEN THE Location_Detector SHALL extract zone names if present
8. WHEN parsing location context THEN THE Location_Detector SHALL extract interaction key bindings if present
9. WHEN parsing location context THEN THE Location_Detector SHALL extract draw distance values if present
10. WHEN metadata values are invalid THEN THE Location_Detector SHALL skip them and continue parsing

### Requirement 4: Risk Scoring

**User Story:** As a security analyst, I want exploitation risk scores for each location, so that I can prioritize which locations are most valuable for attackers to exploit.

#### Acceptance Criteria

1. WHEN calculating risk score THEN THE Risk_Scorer SHALL assign base risk by category: illegal=50, legal_job=20, shop=15, service=10, unknown=5
2. WHEN a location involves drug operations THEN THE Risk_Scorer SHALL add 30 points to the risk score
3. WHEN a location involves weapon shops THEN THE Risk_Scorer SHALL add 20 points to the risk score
4. WHEN a location involves banks or ATMs THEN THE Risk_Scorer SHALL add 15 points to the risk score
5. WHEN security indicators are detected in context THEN THE Risk_Scorer SHALL reduce risk score by 5 points per indicator
6. WHEN exploitable event patterns are detected THEN THE Risk_Scorer SHALL increase risk score by 10 points per pattern
7. WHEN location radius exceeds 50 units THEN THE Risk_Scorer SHALL increase risk score by 5 points
8. WHEN location has visible map blip THEN THE Risk_Scorer SHALL increase risk score by 5 points
9. WHEN calculating risk score THEN THE Risk_Scorer SHALL clamp final value to range 0.0-100.0
10. WHEN a location is classified as drug operation THEN THE Risk_Scorer SHALL ensure final score is at least 50.0

### Requirement 5: Location Deduplication

**User Story:** As a security analyst, I want duplicate locations removed from results, so that I don't see the same location multiple times due to code patterns.

#### Acceptance Criteria

1. WHEN multiple locations are within 5.0 units of each other THEN THE Location_Detector SHALL identify them as duplicates
2. WHEN duplicate locations are identified THEN THE Location_Detector SHALL keep only the location with highest risk score
3. WHEN deduplicating locations THEN THE Location_Detector SHALL preserve original order for non-duplicates
4. WHEN distance calculation fails THEN THE Location_Detector SHALL skip that deduplication check and continue
5. WHEN all locations are processed THEN THE Location_Detector SHALL return a list with no duplicates within threshold

### Requirement 6: RPLocation Data Model

**User Story:** As a developer, I want a structured data model for locations, so that location data is consistently represented throughout the system.

#### Acceptance Criteria

1. THE RPLocation SHALL store coordinates as a 3-tuple of floats (x, y, z)
2. THE RPLocation SHALL store activity_type as a non-empty string
3. THE RPLocation SHALL store location_name as a string
4. THE RPLocation SHALL store file_path as a string indicating source file
5. THE RPLocation SHALL store line_number as a positive integer
6. THE RPLocation SHALL store confidence as a float between 0.0 and 1.0
7. THE RPLocation SHALL store metadata as a dictionary
8. THE RPLocation SHALL store risk_score as a float between 0.0 and 100.0
9. THE RPLocation SHALL store category as one of: illegal, legal_job, service, shop, unknown
10. THE RPLocation SHALL store context_code as a string containing surrounding code
11. THE RPLocation SHALL provide to_dict() method for JSON serialization
12. THE RPLocation SHALL provide get_coordinate_string() method for formatted output
13. THE RPLocation SHALL provide is_high_value_target() method returning true when risk_score >= 70.0

### Requirement 7: Integration with Analysis Pipeline

**User Story:** As a security analyst, I want location detection integrated into the existing DESTROYER analysis pipeline, so that I can run all analyses together.

#### Acceptance Criteria

1. THE DESTROYER_Engine SHALL include location detection as Phase 17 in the analysis pipeline
2. WHEN detect_all_locations() is called THEN THE DESTROYER_Engine SHALL populate self.rp_locations attribute
3. WHEN location detection completes THEN THE DESTROYER_Engine SHALL log the number of detected locations
4. WHEN exporting JSON results THEN THE DESTROYER_Engine SHALL include rp_locations in the output
5. WHEN location detection encounters errors THEN THE DESTROYER_Engine SHALL log warnings and continue analysis
6. WHEN file_contents is empty THEN THE Location_Detector SHALL return empty list and log info message
7. WHEN all locations are detected THEN THE Location_Detector SHALL sort results by risk_score in descending order

### Requirement 8: Web Dashboard Display

**User Story:** As a security analyst, I want to view detected locations in the web dashboard, so that I can visually explore and analyze location data.

#### Acceptance Criteria

1. WHEN the web dashboard loads THEN THE Web_Dashboard SHALL display a Locations tab
2. WHEN the Locations tab is selected THEN THE Web_Dashboard SHALL render all detected locations
3. WHEN displaying a location THEN THE Web_Dashboard SHALL show location name, coordinates, activity type, category, and risk score
4. WHEN displaying a location THEN THE Web_Dashboard SHALL show the source file path and line number
5. WHEN displaying a location THEN THE Web_Dashboard SHALL show the confidence score
6. WHEN displaying a location THEN THE Web_Dashboard SHALL show the context code snippet
7. WHEN displaying locations THEN THE Web_Dashboard SHALL color-code risk levels (high=red, medium=yellow, low=green)
8. WHEN no locations are detected THEN THE Web_Dashboard SHALL display a message indicating no locations found

### Requirement 9: Location Filtering

**User Story:** As a security analyst, I want to filter locations by various criteria, so that I can focus on specific types of locations.

#### Acceptance Criteria

1. WHEN viewing locations THEN THE Web_Dashboard SHALL provide filter controls for category
2. WHEN viewing locations THEN THE Web_Dashboard SHALL provide filter controls for activity type
3. WHEN viewing locations THEN THE Web_Dashboard SHALL provide filter controls for risk score range
4. WHEN a category filter is applied THEN THE Web_Dashboard SHALL display only locations matching that category
5. WHEN an activity filter is applied THEN THE Web_Dashboard SHALL display only locations matching that activity type
6. WHEN a risk filter is applied THEN THE Web_Dashboard SHALL display only locations within that risk range
7. WHEN multiple filters are applied THEN THE Web_Dashboard SHALL display locations matching all filters
8. WHEN filters are cleared THEN THE Web_Dashboard SHALL display all locations again

### Requirement 10: Coordinate Export

**User Story:** As a security analyst, I want to export location coordinates in various formats, so that I can use them in mapping tools or in-game visualization scripts.

#### Acceptance Criteria

1. WHEN exporting locations THEN THE Web_Dashboard SHALL support CSV format export
2. WHEN exporting to CSV THEN THE Web_Dashboard SHALL include columns: name, x, y, z, activity, risk
3. WHEN exporting locations THEN THE Web_Dashboard SHALL support JSON format export
4. WHEN exporting to JSON THEN THE Web_Dashboard SHALL include all location fields and metadata
5. WHEN exporting locations THEN THE Web_Dashboard SHALL support Lua table format export
6. WHEN exporting to Lua THEN THE Web_Dashboard SHALL generate valid Lua table syntax with vector3() coordinates
7. WHEN exporting locations THEN THE Web_Dashboard SHALL provide download functionality for the exported file
8. WHEN no locations are available THEN THE Web_Dashboard SHALL disable export functionality

### Requirement 11: Offline Operation

**User Story:** As a security analyst, I want all analysis to be performed offline, so that my analysis activities remain undetectable by server administrators.

#### Acceptance Criteria

1. THE Location_Detector SHALL perform all analysis using local static code analysis only
2. THE Location_Detector SHALL NOT make any network requests during analysis
3. THE Location_Detector SHALL NOT call any external APIs during analysis
4. THE Location_Detector SHALL NOT execute any analyzed Lua code
5. THE DESTROYER_Engine SHALL maintain zero-dependency operation using only Python standard library
6. WHEN analyzing code THEN THE Location_Detector SHALL sanitize all extracted strings before display
7. WHEN validating coordinates THEN THE Location_Detector SHALL validate all values before use

### Requirement 12: Error Handling

**User Story:** As a security analyst, I want the system to handle errors gracefully, so that analysis continues even when encountering problematic code.

#### Acceptance Criteria

1. WHEN coordinate values are not valid numbers THEN THE Coordinate_Extractor SHALL skip the match and log a warning
2. WHEN file_contents is empty THEN THE Location_Detector SHALL return empty list and log info message
3. WHEN Lua code contains syntax errors THEN THE Location_Detector SHALL extract what is possible and skip problematic sections
4. WHEN surrounding context is insufficient THEN THE Location_Detector SHALL use default classification with lower confidence
5. WHEN distance calculation fails THEN THE Location_Detector SHALL skip that deduplication check and log warning
6. WHEN metadata parsing fails THEN THE Location_Detector SHALL continue with empty metadata
7. WHEN any error occurs THEN THE DESTROYER_Engine SHALL log the error and continue with remaining analysis phases

### Requirement 13: Performance

**User Story:** As a security analyst, I want location detection to complete in reasonable time, so that I can analyze large server dumps efficiently.

#### Acceptance Criteria

1. WHEN analyzing dumps with 1000+ files THEN THE Location_Detector SHALL complete within 5 minutes
2. WHEN compiling regex patterns THEN THE Location_Detector SHALL compile them once at initialization
3. WHEN processing files THEN THE Location_Detector SHALL skip non-Lua files early
4. WHEN deduplicating large location sets THEN THE Location_Detector SHALL use efficient spatial algorithms
5. WHEN processing large files THEN THE Location_Detector SHALL limit context window size to prevent memory issues
6. WHEN analysis completes THEN THE DESTROYER_Engine SHALL clear intermediate data structures to free memory

### Requirement 14: Location Name Generation

**User Story:** As a security analyst, I want meaningful names for detected locations, so that I can easily identify and reference them.

#### Acceptance Criteria

1. WHEN a location name is present in code context THEN THE Location_Detector SHALL extract and use it
2. WHEN no location name is found THEN THE Location_Detector SHALL generate a name from activity type and coordinates
3. WHEN generating names THEN THE Location_Detector SHALL use format: "{activity_type}_{x}_{y}"
4. WHEN extracting names THEN THE Location_Detector SHALL look for common patterns: name=, label=, blip.name
5. WHEN multiple name candidates exist THEN THE Location_Detector SHALL prefer explicit name fields over comments

### Requirement 15: Location Categorization

**User Story:** As a security analyst, I want locations categorized by legality and purpose, so that I can understand the server's structure.

#### Acceptance Criteria

1. WHEN an activity involves drug operations THEN THE Location_Detector SHALL categorize as illegal
2. WHEN an activity involves legal jobs THEN THE Location_Detector SHALL categorize as legal_job
3. WHEN an activity involves shops THEN THE Location_Detector SHALL categorize as shop
4. WHEN an activity involves services THEN THE Location_Detector SHALL categorize as service
5. WHEN an activity cannot be determined THEN THE Location_Detector SHALL categorize as unknown
6. WHEN categorizing THEN THE Location_Detector SHALL use activity_type as primary input
7. WHEN categorizing THEN THE Location_Detector SHALL consider metadata as secondary input
