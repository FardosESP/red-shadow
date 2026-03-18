# Implementation Plan: DESTROYER v4 Offline Analysis with RP Location Detection

## Overview

This plan implements Phase 17 (RP Location Detection) for the existing DESTROYER v4 system. The existing 16 phases are already complete and working. This implementation adds location detection capabilities to identify roleplay locations (drug operations, jobs, shops, services) through static Lua code analysis, calculate exploitation risk scores, and integrate results into the web dashboard.

## Tasks

- [x] 1. Create RPLocation data model
  - Add RPLocation dataclass to red_shadow_destroyer_v4.py after existing data models
  - Include fields: coords, activity_type, location_name, file_path, line_number, confidence, metadata, risk_score, category, context_code
  - Implement to_dict(), get_coordinate_string(), and is_high_value_target() methods
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13_

- [ ]* 1.1 Write property test for RPLocation data model
  - **Property 1: Coordinate Validity** - All locations must have valid 3D float coordinates
  - **Property 2: Risk Score Bounds** - Risk scores must be within 0.0-100.0
  - **Property 5: Confidence Bounds** - Confidence must be within 0.0-1.0
  - **Property 7: Valid Category** - Category must be one of: illegal, legal_job, service, shop, unknown
  - **Validates: Requirements 6.1, 6.6, 6.8, 6.9**

- [x] 2. Implement coordinate extraction functionality
  - [x] 2.1 Add coordinate extraction methods to RedShadowV4 class
    - Implement _extract_vector3_coords() for vector3(x, y, z) patterns
    - Implement _extract_vector2_coords() for vector2(x, y) patterns (convert to 3D with z=0)
    - Implement _extract_table_coords() for {x=..., y=..., z=...} patterns
    - Implement _extract_config_locations() for Config.Locations arrays
    - Compile regex patterns once in __init__
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [ ]* 2.2 Write unit tests for coordinate extraction
    - Test each pattern type independently
    - Test edge cases: negative coords, decimals, malformed patterns
    - Test line number extraction accuracy
    - _Requirements: 1.7, 1.8_


- [x] 3. Implement activity classification system
  - [x] 3.1 Create activity keyword dictionaries
    - Define drug operation keywords (Spanish/English): planting, processing, selling
    - Define job keywords: mining, fishing, farming, trucking, taxi, mechanic
    - Define shop keywords: weapon, clothing, vehicle, general
    - Define service keywords: atm, bank, garage, hospital, police
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.8_

  - [x] 3.2 Implement _classify_activity() method
    - Analyze context code for activity keywords
    - Prioritize drug operations over other activities
    - Calculate confidence score based on keyword matches
    - Return activity_type and confidence tuple
    - Handle unknown classification with confidence <= 0.3
    - _Requirements: 2.1, 2.6, 2.7, 2.9, 2.10_

  - [ ]* 3.3 Write unit tests for activity classification
    - Test each activity category detection
    - Test priority ordering (drugs > jobs > shops > services)
    - Test multi-language keyword support
    - Test confidence score calculation
    - _Requirements: 2.6, 2.8, 2.9, 2.10_

- [x] 4. Implement location metadata parsing
  - [x] 4.1 Create _parse_location_metadata() method
    - Extract radius values from context
    - Extract blip sprite, color, and name
    - Extract marker type and color (RGBA)
    - Extract zone names and interaction keys
    - Extract draw distance values
    - Handle invalid metadata gracefully
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_


  - [ ]* 4.2 Write unit tests for metadata parsing
    - Test extraction of each metadata field type
    - Test handling of missing metadata
    - Test invalid value handling
    - _Requirements: 3.10_

- [x] 5. Implement risk scoring algorithm
  - [x] 5.1 Create _calculate_location_risk() method
    - Assign base risk by category: illegal=50, legal_job=20, shop=15, service=10, unknown=5
    - Add 30 points for drug operations
    - Add 20 points for weapon shops
    - Add 15 points for banks/ATMs
    - Reduce 5 points per security indicator
    - Add 10 points per exploitable event pattern
    - Add 5 points for radius > 50 units
    - Add 5 points for visible map blip
    - Clamp final score to [0.0, 100.0]
    - Ensure drug operations score >= 50.0
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

  - [ ]* 5.2 Write property test for risk scoring
    - **Property 2: Risk Score Bounds** - All scores must be within 0.0-100.0
    - **Property 3: Drug Operations High Risk** - Drug operations must score >= 50.0
    - **Validates: Requirements 4.9, 4.10**

- [x] 6. Implement location categorization
  - [x] 6.1 Create _categorize_location() method
    - Categorize drug operations as "illegal"
    - Categorize legal jobs as "legal_job"
    - Categorize shops as "shop"
    - Categorize services as "service"
    - Categorize unknown activities as "unknown"
    - Use activity_type as primary input
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_


- [x] 7. Implement location name generation
  - [x] 7.1 Create _extract_location_name() method
    - Look for name patterns: name=, label=, blip.name
    - Prefer explicit name fields over comments
    - Generate name from activity_type and coordinates if not found
    - Use format: "{activity_type}_{x}_{y}" for generated names
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 8. Implement location deduplication
  - [x] 8.1 Create _deduplicate_locations() method
    - Calculate 3D distance between all location pairs
    - Identify duplicates within 5.0 unit threshold
    - Keep location with highest risk_score from duplicate groups
    - Preserve original order for non-duplicates
    - Handle distance calculation errors gracefully
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 8.2 Write property test for deduplication
    - **Property 4: No Duplicate Locations** - No locations within 5.0 units of each other
    - **Validates: Requirements 5.1, 5.2**

- [x] 9. Checkpoint - Ensure all core location detection logic is complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Integrate Phase 17 into DESTROYER engine
  - [x] 10.1 Add rp_locations attribute to RedShadowV4.__init__
    - Initialize self.rp_locations = [] in __init__ method
    - _Requirements: 7.2_

  - [x] 10.2 Implement detect_all_locations() method
    - Iterate through all loaded Lua files
    - Extract coordinates using all pattern methods
    - Extract context code (10 lines around match)
    - Classify activity type with confidence
    - Parse location metadata
    - Generate or extract location name
    - Categorize location
    - Calculate risk score
    - Create RPLocation objects
    - Deduplicate locations (5.0 unit threshold)
    - Sort by risk_score descending
    - Populate self.rp_locations
    - Log number of detected locations
    - Handle errors gracefully (log warnings, continue)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_


  - [ ]* 10.3 Write integration test for detect_all_locations
    - Test with sample Lua files containing various coordinate patterns
    - Verify locations are detected and classified correctly
    - Verify deduplication works
    - Verify sorting by risk score
    - _Requirements: 7.1, 7.7_

- [x] 11. Update JSON export to include locations
  - [x] 11.1 Modify export_json() method
    - Add rp_locations section to JSON output
    - Convert each RPLocation to dict using to_dict()
    - Include location count in summary
    - _Requirements: 7.4_

  - [ ]* 11.2 Write unit test for JSON export with locations
    - Verify rp_locations field is present in JSON
    - Verify all location fields are serialized correctly
    - _Requirements: 7.4_

- [x] 12. Update print_summary() to include location statistics
  - Add location detection summary section
  - Display total locations detected
  - Display high-risk locations count (risk >= 70)
  - Display locations by category breakdown
  - Display top 5 highest-risk locations
  - _Requirements: 7.3_

- [x] 13. Checkpoint - Ensure Phase 17 integration is complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Extend web dashboard with Locations tab
  - [x] 14.1 Update web_gui.py to add Locations tab
    - Add "Locations" tab to navigation
    - Create render_locations_tab() function
    - Display location count and filter controls
    - _Requirements: 8.1, 8.2_

  - [x] 14.2 Implement location card rendering
    - Create render_location_card() function
    - Display location name, coordinates, activity type
    - Display category, risk score, confidence
    - Display source file path and line number
    - Display context code snippet
    - Color-code risk levels: high (>=70) red, medium (40-69) yellow, low (<40) green
    - _Requirements: 8.3, 8.4, 8.5, 8.6, 8.7_


  - [x] 14.3 Handle empty locations state
    - Display "No locations detected" message when rp_locations is empty
    - _Requirements: 8.8_

- [x] 15. Implement location filtering in web dashboard
  - [x] 15.1 Add filter controls to Locations tab
    - Add category filter dropdown (illegal, legal_job, service, shop, unknown, all)
    - Add activity type filter dropdown (populate from detected activities)
    - Add risk score range slider (0-100)
    - Add "Clear Filters" button
    - _Requirements: 9.1, 9.2, 9.3_

  - [x] 15.2 Implement client-side filtering logic
    - Filter locations by selected category
    - Filter locations by selected activity type
    - Filter locations by risk score range
    - Apply all filters simultaneously (AND logic)
    - Update displayed location count
    - _Requirements: 9.4, 9.5, 9.6, 9.7, 9.8_

- [x] 16. Implement coordinate export functionality
  - [x] 16.1 Add export buttons to Locations tab
    - Add "Export CSV" button
    - Add "Export JSON" button
    - Add "Export Lua" button
    - Disable buttons when no locations available
    - _Requirements: 10.1, 10.3, 10.5, 10.8_

  - [x] 16.2 Implement CSV export
    - Generate CSV with columns: name, x, y, z, activity, risk
    - Include all locations (or filtered subset)
    - Provide download functionality
    - _Requirements: 10.2, 10.7_

  - [x] 16.3 Implement JSON export
    - Generate JSON with all location fields and metadata
    - Use RPLocation.to_dict() for serialization
    - Provide download functionality
    - _Requirements: 10.4, 10.7_

  - [x] 16.4 Implement Lua export
    - Generate valid Lua table syntax
    - Use vector3() for coordinates
    - Include location name and activity type
    - Provide download functionality
    - _Requirements: 10.6, 10.7_


- [x] 17. Add error handling and validation
  - [x] 17.1 Add input validation to coordinate extraction
    - Validate coordinate values are valid floats
    - Skip malformed patterns and log warnings
    - Handle empty file_contents gracefully
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 17.2 Add error handling to classification and metadata parsing
    - Handle insufficient context with default classification
    - Handle metadata parsing failures gracefully
    - Continue processing on errors
    - _Requirements: 12.4, 12.6_

  - [x] 17.3 Add error handling to deduplication
    - Handle distance calculation failures
    - Log warnings and continue with remaining checks
    - _Requirements: 12.5_

  - [x] 17.4 Add security validation
    - Sanitize all extracted strings before display
    - Validate coordinate values before use
    - Never execute analyzed Lua code
    - _Requirements: 11.6, 11.7, 11.4_

- [x] 18. Optimize performance for large dumps
  - [x] 18.1 Optimize regex compilation
    - Compile all regex patterns once in __init__
    - Use non-capturing groups where possible
    - _Requirements: 13.2_

  - [x] 18.2 Optimize file processing
    - Skip non-Lua files early
    - Limit context window size to prevent memory issues
    - _Requirements: 13.3, 13.5_

  - [x] 18.3 Optimize deduplication
    - Use efficient distance calculations
    - Early termination when possible
    - _Requirements: 13.4_

- [x] 19. Final checkpoint - Complete end-to-end testing
  - Ensure all tests pass, ask the user if questions arise.


- [x] 20. Update documentation and examples
  - [x] 20.1 Add Phase 17 to main() function
    - Call engine.detect_all_locations() after Phase 16
    - Add to analysis pipeline documentation
    - _Requirements: 7.1_

  - [x] 20.2 Create usage examples
    - Add example of basic location detection usage
    - Add example of filtering high-risk locations
    - Add example of exporting coordinates
    - Add example of web dashboard with locations
    - Document in docstrings or comments

  - [x] 20.3 Update existing documentation
    - Update DESTROYER_V4_COMPLETE.md to mention Phase 17
    - Update web GUI documentation to mention Locations tab
    - Update JSON export documentation to include rp_locations field

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The existing 16 phases are already complete - focus only on Phase 17 implementation
- All implementation uses Python to match existing DESTROYER v4 codebase
- Maintain zero-dependency operation using only Python standard library
- All analysis must remain offline (no network requests or API calls)

---

## Phase 18: Smart Trigger Usability Detection

These tasks improve how the engine determines whether a trigger is directly usable from an executor, and generates better ready-to-paste exploit lines.

- [ ] 21. Distinguish weak vs strong validation
  - Currently `has_validation=True` blocks a trigger from being "ready_to_use" even if the validation is bypasseable (e.g. `if amount > 0` is weak — just pass a valid value)
  - Add `validation_strength` field to Trigger: `'none'`, `'weak'`, `'strong'`
  - `'strong'` = permission/group/ace checks (`IsPlayerAceAllowed`, `xPlayer.getGroup`, `HasPermission`, `IsAdmin`) — not bypasseable
  - `'weak'` = data/range checks (`if amount > 0`, `if item ~= nil`, `if count < 1000`) — bypasseable with correct params
  - Update `ready_to_use` logic: `not is_honeypot and validation_strength != 'strong'`
  - Update dashboard: show "WEAK VAL" tag in yellow (still exploitable) vs "STRONG VAL" in red (blocked)

- [ ] 22. Infer exploit parameters from handler code
  - Currently exploit lines use hardcoded values (`999999`, `"bread"`, `100`)
  - Parse the handler body to extract real parameter usage:
    - If handler does `xPlayer.addMoney(amount)` → param is numeric, use `999999`
    - If handler does `xPlayer.addInventoryItem(item, count)` → infer item name from nearby string literals in the same file (e.g. `"weed"`, `"cocaine"`, `"bread"`)
    - If handler has `if amount > X and amount < Y` → use `Y - 1` as the exploit value
    - If handler has `if item == "specificitem"` → use that exact item name
  - Add `inferred_params` list to Trigger with `{name, value, source}` dicts
  - Generate exploit line using inferred params instead of generic defaults
  - Fall back to generic values when inference fails

- [ ] 23. Framework detection per trigger
  - Detect which framework a trigger belongs to based on:
    - Resource folder name (e.g. `es_extended`, `qb-core`, `vrp`)
    - Imports/exports in the same file (`ESX = exports['es_extended']:getSharedObject()`)
    - API calls in handler (`xPlayer.addMoney` → ESX, `Player.Functions.AddMoney` → QBCore)
  - Add `framework` field to Trigger: `'ESX'`, `'QBCore'`, `'vRP'`, `'standalone'`, `'unknown'`
  - Use framework to generate framework-specific exploit lines:
    - ESX: `TriggerServerEvent("esx:addMoney", 999999)`
    - QBCore: `TriggerServerEvent("QBCore:server:addMoney", "cash", 999999)`
  - Show framework badge in dashboard trigger cards

- [ ] 24. Detect and exploit RegisterServerCallback / CreateCallback
  - Currently only `RegisterNetEvent`/`AddEventHandler` are detected
  - Add detection for:
    - `ESX.RegisterServerCallback("name", function(source, cb, ...))`
    - `QBCore.Functions.CreateCallback("name", function(source, cb, ...)`
    - `CfxCallback:Register("name", ...)`
  - These are exploitable via `TriggerServerCallback("name", function(result) end, ...args)`
  - Add `event_type = 'ServerCallback'` and generate correct exploit line
  - Mark as separate category in dashboard with 📞 icon

- [ ] 25. Update web dashboard for new trigger fields
  - Show `validation_strength` as colored tag: green=none, yellow=weak, red=strong
  - Show `framework` badge on each trigger card
  - Show inferred params in the exploit line (not generic values)
  - Add filter: "Weak Validation" (bypasseable) separate from "No Validation"
  - Update "Exploitable" section to include weak-validation triggers


---

## Phase 19: Extended Known Triggers Database

X9 and other tools have large databases of known vulnerable events. The CFX community maintains lists of hundreds of abused events. Our KNOWN_TRIGGERS_DB has only 21 entries.

- [ ] 26. Expand KNOWN_TRIGGERS_DB with community-sourced vulnerable events
  - Add all known ESX drug events: `esx_drugs:startHarvestWeed/Coke/Meth/Opium`, `startTransform*`, `startSell*`, `stopHarvest*`
  - Add ESX job pay events: `esx_billing:sendBill`, `esx_garbagejob:pay`, `esx_truckerjob:pay`, `esx_pizza:pay`, `esx_ranger:pay`, `esx_fueldelivery:pay`, `esx_carthief:pay`, `esx_gopostaljob:pay`, `esx_godirtyjob:pay`, `esx_banksecurity:pay`, `esx_mecanojob:onNPCJobCompleted`
  - Add ESX admin/social: `esx_society:setJob`, `esx_society:openBossMenu`, `esx_jail:sendToJail`, `esx_jailer:sendToJail`, `esx_dmvschool:addLicense`, `esx_dmvschool:pay`, `esx_skin:responseSaveSkin`
  - Add ESX vehicle: `esx_vehicleshop:setVehicleOwned`, `eden_garage:payhealth`, `lscustoms:payGarage`
  - Add ESX banking: `bank:deposit`, `bank:withdraw`, `bank:transfer`, `Banca:deposit`, `Banca:withdraw`, `esx_banking:addAccountMoney`, `esx_moneywash:deposit`, `esx_moneywash:withdraw`
  - Add QBCore equivalents: `qb-banking:*`, `qb-drugs:*`, `qb-inventory:*`, `qb-garages:*`, `qb-vehicleshop:*`
  - Add vRP events: `vrp:give_money`, `vrp:give_item`, `vrp_slotmachine:server:2`
  - Add standalone admin events: `AdminMenu:giveBank`, `AdminMenu:giveCash`, `AdminMenu:giveDirtyMoney`, `adminmenu:setsalary`, `adminmenu:cashoutall`
  - Add revive/cuff events (useful for griefing detection): `esx_ambulancejob:revive`, `esx_policejob:handcuff`, `ems:revive`, `paramedic:revive`
  - Add paycheck/salary events: `paycheck:bonus`, `paycheck:salary`
  - Mark each entry with `is_honeypot_risk: True/False` based on community knowledge
  - Target: 200+ entries covering ESX, QBCore, vRP, standalone

---

## Phase 20: Trigger Cross-Reference & Call Graph

X9 and advanced tools show which client-side code calls which server triggers, letting you understand the full flow before exploiting.

- [ ] 27. Build client→server call graph
  - Scan all client-side Lua files for `TriggerServerEvent("name", ...)` calls
  - For each call, extract: trigger name, file, line, surrounding context, literal argument values passed
  - Cross-reference with server-side `RegisterNetEvent`/`AddEventHandler` handlers
  - Build a graph: `{trigger_name: {callers: [...], handler: {...}, args_seen: [...]}}`
  - Store in `self.trigger_call_graph` dict

- [ ] 28. Infer real argument values from client call sites
  - When a client calls `TriggerServerEvent("esx_drugs:sell", "weed", 50)`, extract `["weed", 50]` as known-good args
  - Store these as `observed_args` on the trigger
  - Use observed args to generate exploit lines with real values instead of generic placeholders
  - If multiple call sites exist, pick the one with highest numeric values (most profitable)
  - Show "args from source" badge in dashboard when exploit uses real observed values

- [ ] 29. Detect triggers only called from specific conditions (bypass hints)
  - If a trigger is only called inside `if IsPlayerAceAllowed(...)` or `if xPlayer.getGroup() == "admin"` on the client side, flag it as "client-gated" — the server may not re-check
  - These are high-value: the server trusts the client already passed the check
  - Add `client_gated: True` field and show "CLIENT GATE ONLY" warning tag in dashboard

---

## Phase 21: Export Formats for Executor

Tools like X9 export ready-to-paste Lua scripts. We should do the same.

- [ ] 30. Generate ready-to-paste Lua executor scripts
  - For each exploitable trigger, generate a complete Lua snippet ready to paste in Ambani/redENGINE:
    ```lua
    -- [RED-SHADOW] esx:addMoney | Risk: 95% | No Validation
    TriggerServerEvent("esx:addMoney", 999999)
    ```
  - For batch mode, generate a single Lua file with all exploitable triggers as commented blocks
  - Add "Export All as Lua Script" button in dashboard that downloads a `.lua` file
  - Add "Copy Lua" button per trigger card (replaces current "Copy" which copies just the event name)
  - Include safety comments: honeypot warnings, rate limit warnings, validation warnings

- [ ] 31. Generate Ambani-format trigger list
  - Ambani executor has a specific format for bulk trigger execution
  - Generate a list in Ambani's native format (one trigger per line with params)
  - Add "Export for Ambani" button in dashboard
  - Include only `ready_to_use` triggers (no honeypots, no strong validation)

---

## Phase 22: Resource-Level Risk Scoring

X9 shows risk per resource/script, not just per trigger. This helps prioritize which scripts to focus on.

- [ ] 32. Add per-resource risk aggregation
  - Group all triggers by their source resource (folder name)
  - Calculate resource-level risk score: average of trigger risk scores, boosted by count of exploitable triggers
  - Add `resource_summary` to report: `{resource_name: {trigger_count, exploitable_count, honeypot_count, max_risk, avg_risk, framework}}`
  - Add "Resources" tab in dashboard showing resource cards sorted by risk
  - Each resource card shows: name, framework badge, trigger count, exploitable count, top trigger

- [ ] 33. Detect resource framework automatically
  - For each resource folder, detect framework from:
    - `fxmanifest.lua` dependencies (`'es_extended'`, `'qb-core'`)
    - Imports in Lua files (`ESX = exports['es_extended']:getSharedObject()`)
    - API usage patterns (`xPlayer.`, `Player.Functions.`, `vRP.`)
  - Tag each resource with detected framework
  - Use framework to improve exploit generation (correct API format per framework)

---

## Phase 23: Obfuscation Bypass & Deobfuscation Hints

Many FiveM scripts use basic obfuscation. Tools like X9 flag these and try to hint at what's inside.

- [ ] 34. Detect and classify obfuscation techniques
  - Extend current obfuscation detection with:
    - `string.byte`/`string.char` encoding (common in FiveM scripts)
    - XOR-based string encoding patterns
    - Base64 encoded strings inside `loadstring`
    - Hex-encoded strings (`\x41\x42...`)
    - Variable name mangling (all vars are single chars or random strings)
  - For each obfuscated file, attempt simple deobfuscation:
    - Decode `string.char(...)` sequences to readable strings
    - Decode hex escape sequences
    - Extract any readable strings from obfuscated code
  - Show decoded strings in dashboard — often reveals trigger names, webhook URLs, or AC logic

- [ ] 35. Flag obfuscated triggers as higher risk
  - If a trigger's handler is inside an obfuscated block, mark `is_obfuscated: True`
  - Obfuscated triggers with reward logic = very high risk (server is hiding something)
  - Show "OBFUSCATED" tag in red on trigger cards
  - Add filter for obfuscated triggers in dashboard

---

## Phase 24: Streaming/Progressive Dashboard

Currently the dashboard only shows after full analysis. For large dumps this means long waits.

- [ ] 36. Implement progressive dashboard rendering
  - After each analysis phase completes, push partial results to the frontend via `/api/status` `partial` field
  - Frontend polls every 500ms and renders available sections as they arrive
  - Show a phase progress bar at the top: `[████░░░░] Phase 5/17: Detecting triggers...`
  - Sections appear one by one as phases complete: Summary → Triggers → Exploitable → Known DB → etc.
  - Each section shows a skeleton loader while its phase is still running
  - When a section's data arrives, animate it in (fade/slide)
  - "Next loading: Anticheats..." status line below the progress bar
