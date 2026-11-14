# E2E Test Infra: Management Cards - Chapter 02 Card Text Option Restoration

## Test Philosophy
- **Opaque-box & Requirement-driven**: Test cases are derived strictly from `ORIGINAL_REQUEST.md`, `PROJECT.md`, and design specifications (`tokens.css`), with zero dependency on internal extraction or pipeline implementation details.
- **Methodology**: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Interaction Testing + Real-World Workload Scenarios.
- **Progressive Testability**: Verification mechanisms for earlier tiers do not require components more complex than the tier itself.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| F1 | Card Text Option Restoration | ORIGINAL_REQUEST §R1 | ≥5 | ≥5 | ✓ |
| F2 | Boxed Statement Formatting | ORIGINAL_REQUEST §R2 | ≥5 | ≥5 | ✓ |
| F3 | Frame Cleanup & Design System Compliance | ORIGINAL_REQUEST §R3 | ≥5 | ≥5 | ✓ |
| F4 | Stem Text & Metadata Population | ORIGINAL_REQUEST §R1 | ≥5 | ≥5 | ✓ |
| F5 | Outlier & Anomaly Resolutions | Survey Reports 1 & 2 | ≥5 | ≥5 | ✓ |
| F6 | Automated Verification Tooling & E2E Suite | ORIGINAL_REQUEST §R4 | ≥5 | ≥5 | ✓ |

## Test Architecture
- **Location**: `c:\Users\yoon\Downloads\management-cards\tests\`
- **Test Runner**: `tests/run_e2e_tests.py`
  - Invocation: `python tests/run_e2e_tests.py` (or `python -m unittest discover tests`)
  - Pass/Fail semantics: Exit code 0 if 100% of tests pass; non-zero if any test fails.
- **Test Modules**:
  - `tests/test_tier1_features.py`: Independent equivalence-class tests for each feature F1 through F6 (>=30 tests).
  - `tests/test_tier2_boundaries.py`: Boundary and edge cases (4-choice vs 5-choice cards, empty checks, `mgmt_0374` zero-byte fallback, 20 boxed statement formats Hangul/Latin, `mgmt_0454` table matrix, `mgmt_0501` answer page fix) (>=30 tests).
  - `tests/test_tier3_combinations.py`: Pairwise interactions (boxed statements with 4 vs 5 options, data attributes, tokens.css styles, button types with stems) (>=6 tests).
  - `tests/test_tier4_scenarios.py`: Full dataset acceptance workloads (parse valid JSON, complete scan of all 231 cards verifying 0 image-frames, 0 img tags, clean text options without circled numbers, no emojis, consistent metadata) (>=5 tests).
- **Directory Layout**:
  ```
  tests/
  ├── __init__.py
  ├── conftest.py / test_utils.py
  ├── run_e2e_tests.py
  ├── test_tier1_features.py
  ├── test_tier2_boundaries.py
  ├── test_tier3_combinations.py
  └── test_tier4_scenarios.py
  ```

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Entire Chapter 02 JSON Parse & Schema Integrity Scan | F1, F3, F4, F6 | High |
| 2 | Total Elimination of Image Frames & Raw Image Tags Across 231 Cards | F1, F3 | High |
| 3 | Full Button Markup & Option Cleanness Scan (No Circled Numbers / Emojis) | F1, F3, F4 | High |
| 4 | Complete Boxed Statement Structural Audit for All Boxed Cards | F2, F3, F4 | High |
| 5 | Master Reference & Outlier Verification (0374, 0501, 0454, 0278) | F1, F2, F5 | High |

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥30 tests (≥5 per feature across 6 features)
- **Tier 2 (Boundary & Corner Cases)**: ≥30 tests (≥5 per feature)
- **Tier 3 (Cross-Feature Combinations)**: ≥6 pairwise combination tests
- **Tier 4 (Real-World Workloads)**: ≥5 comprehensive application scenarios
- **Total Minimum Test Count**: ≥71 test cases
