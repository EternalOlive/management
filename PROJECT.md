# Project: Management Cards - Chapter 02 Card Text Option Restoration

## Architecture
- **Target Working Directory**: `c:\Users\yoon\Downloads\management-cards`
- **Target Dataset**: `cards-data.json` (Chapter 02: `'1.02 조직행동: 개인'`, IDs: `mgmt_0277` through `mgmt_0507`, 231 cards total)
- **Reference Assets**:
  - `images/_jh_q_*.webp` (cropped question images, 230 valid, 1 corrupted `0374`)
  - `pdf-page-map.json` (question-to-page mapping, contains `0501` bug to be patched)
  - `전수환_경영학_문제.pdf` (master exam question PDF for rendering/fallback)
  - `전수환_경영학_답지.pdf` / `ans_02.pdf` (answer key & explanation ground truth)
- **Design System & UI**:
  - `tokens.css` (color and dimension tokens: `--c-card`, `--c-fill`, `--c-sec`, `--c-sep`, `--r-cell: 12px`, etc.)
  - `cards.html` (production web viewer & runtime button handler)
- **Canonical Card Markup Standards**:
  - Container: `<div class="mcq-card">`
  - Header: `<div class="mcq-header"><span class="mcq-qnum">문제 {qid}</span><span class="source-badge">{sourceTag}</span></div>`
  - Stem: `<div class="mcq-stem"><div class="stem-ocr-text">{stemText}</div></div>`
  - Boxed Statement Container: `<div class="statement-box mcq-statement-box"><div class="mcq-statement-header">&lt;보기&gt;</div>...<div class="mcq-statement-item" data-stmt="..."><span class="mcq-stmt-badge">...</span><span class="mcq-stmt-text">...</span></div></div>`
  - Text Option Button: `<button type="button" class="mcq-option text-option" data-original="{num}"><span class="mcq-label">{label}</span><span class="mcq-choice-text">{cleanChoiceText}</span></button>`
  - Strictly 0 `<div class="image-frame">` and 0 `<img>` tags in `front`.
  - Strictly no leading circled numbers or option indexes inside `<span class="mcq-choice-text">`.
  - Strictly no emojis or runtime buttons (`.mcq-ox-btn`, `.mcq-elim-btn`) in `cards-data.json`.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Card Text Option Restoration | Replace image-based option buttons with `<button class="mcq-option text-option">` across all 231 cards | M1, M2, M3 | ORIGINAL_REQUEST §R1 |
| F2 | Boxed Statement Formatting | Format 20 boxed statement questions with `<div class="statement-box mcq-statement-box">` in stem and clean `<span class="mcq-choice-text">` buttons | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| F3 | Frame Cleanup & Design System Compliance | 100% elimination of `<div class="image-frame">` tags across all 231 cards, tokens.css compliance, no emojis | M2, M3 | ORIGINAL_REQUEST §R3 |
| F4 | Stem Text & Metadata Population | Extract full Korean stems into `stemText`, populate `sourceTag` and structured `choices` | M1, M2 | ORIGINAL_REQUEST §R1 |
| F5 | Outlier & Anomaly Resolutions | Fix 0-byte `_jh_q_0374.webp` fallback, `0501` ans_page bug, `0278` duplicate options, `0454` table matrix | M1, M2 | Survey Reports 1 & 2 |
| F6 | Automated Verification Tooling & E2E Suite | 4-tier requirement-driven opaque-box test suite and structural JSON verification script | E2E Track, M3 | ORIGINAL_REQUEST §R4 |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Requirement-driven opaque-box test suite (Tiers 1-4) & automated validator, publishes `TEST_READY.md` | none | IN_PROGRESS |
| M1 | Extraction & Pipeline | Hybrid WinOCR/PyMuPDF extraction, `0374` fallback, `0501` mapping patch, output `chapter02_extracted.json` | none | IN_PROGRESS |
| M2 | Schema & Card Assembly | Restructure `cards-data.json` for all 231 cards, eliminate 100% of image-frames, format boxed statements | M1 | PLANNED |
| M3 | Final E2E Verification & Hardening | Pass 100% of E2E test suite (Tiers 1-4), adversarial coverage hardening (Tier 5), forensic audit | M2, E2E (TEST_READY.md) | PLANNED |

---

## Interface Contracts

### M1 (Extraction Pipeline) ↔ M2 (Card Assembly)
- **Data File**: `c:\Users\yoon\Downloads\management-cards\chapter02_extracted.json`
- **Schema**:
  ```json
  {
    "mgmt_0277": {
      "id": "mgmt_0277",
      "qid": "0277",
      "sourceTag": "2020 공인회계사",
      "stemText": "...",
      "typ": "객관식" | "박스선택형",
      "boxStatements": [
        {"id": "ㄱ", "label": "ㄱ", "text": "...", "isCorrect": false}
      ],
      "choices": [
        "1번: ...",
        "2번: ..."
      ],
      "answer": "3",
      "choiceCount": 4 | 5
    }
  }
  ```
- **Error Handling**: Every card in `mgmt_0277` ~ `mgmt_0507` must be present (231 keys). Choice count must strictly equal 4 or 5. Stems and choices must not be empty or truncated.

### M2 (Card Assembly) ↔ E2E Testing Track & M3 (Verification)
- **Target File**: `c:\Users\yoon\Downloads\management-cards\cards-data.json`
- **Contract Rules**:
  1. Valid JSON, parseable with `json.loads()`.
  2. Total cards in Chapter 02: exactly 231 (`mgmt_0277` ~ `mgmt_0507`).
  3. `image-frame` in `front` HTML: exactly 0 across all 231 cards.
  4. `<img>` tag in `front` HTML: exactly 0 across all 231 cards.
  5. `number-option` in `front` HTML: exactly 0 across all 231 cards.
  6. Every card has either 4 or 5 `<button type="button" class="mcq-option text-option" data-original="{num}">`.
  7. Every button contains `<span class="mcq-choice-text">` with non-empty text, free of leading circled numbers.
  8. Every boxed card (`typ: "박스선택형"`) contains `<div class="statement-box mcq-statement-box">`.

---

## Code Layout
- `c:\Users\yoon\Downloads\management-cards\cards-data.json`: Production dataset.
- `c:\Users\yoon\Downloads\management-cards\pdf-page-map.json`: Question mapping dataset.
- `c:\Users\yoon\Downloads\management-cards\scripts\`: Extraction, assembly, and validation scripts.
- `c:\Users\yoon\Downloads\management-cards\tests\`: E2E opaque-box test runner and test suites.
- `c:\Users\yoon\Downloads\management-cards\.agents\teamwork\`: Coordination & orchestration metadata only.
