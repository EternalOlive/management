"""
tests/test_utils.py
Shared test utilities, safe loaders, HTML parsing engine, and constants
for Management Cards Chapter 02 E2E test suite.
"""

from __future__ import annotations
import json
import re
import sys
import os
from pathlib import Path
from html.parser import HTMLParser
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple

# ---------------------------------------------------------------------------
# Path & Directory Resolution
# ---------------------------------------------------------------------------
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CARDS_DATA_PATH = PROJECT_ROOT / "cards-data.json"
PAGE_MAP_PATH = PROJECT_ROOT / "pdf-page-map.json"
TOKENS_CSS_PATH = PROJECT_ROOT / "tokens.css"
if not TOKENS_CSS_PATH.exists():
    TOKENS_CSS_PATH = PROJECT_ROOT.parent / "tokens.css"

# ---------------------------------------------------------------------------
# Constants & Dataset Boundary Definitions
# ---------------------------------------------------------------------------
CH2_START_ID = "mgmt_0277"
CH2_END_ID = "mgmt_0507"
CH2_START_QID = "0277"
CH2_END_QID = "0507"
CH2_START_NUM = 277
CH2_END_NUM = 507
CH2_CARD_COUNT = 231
CH2_SUBJ = "1.02 조직행동: 개인"

# Exactly 20 Boxed Statement Cards in Chapter 02
BOXED_CARD_IDS = [
    "mgmt_0313", "mgmt_0323", "mgmt_0325", "mgmt_0342", "mgmt_0367",
    "mgmt_0372", "mgmt_0374", "mgmt_0378", "mgmt_0380", "mgmt_0388",
    "mgmt_0405", "mgmt_0428", "mgmt_0429", "mgmt_0444", "mgmt_0450",
    "mgmt_0460", "mgmt_0461", "mgmt_0480", "mgmt_0490", "mgmt_0507"
]

# 4-choice vs 5-choice breakdown for boxed statement cards
BOXED_CARDS_4_CHOICE = ["mgmt_0323", "mgmt_0342", "mgmt_0428", "mgmt_0429"]
BOXED_CARDS_5_CHOICE = [cid for cid in BOXED_CARD_IDS if cid not in BOXED_CARDS_4_CHOICE]

# Boxed statement label categories
BOXED_LABELS_HANGUL_CONSONANTS = [
    "mgmt_0313", "mgmt_0325", "mgmt_0342", "mgmt_0372", "mgmt_0374",
    "mgmt_0378", "mgmt_0380", "mgmt_0405", "mgmt_0428", "mgmt_0429"
]
BOXED_LABELS_CIRCLED_HANGUL = ["mgmt_0323"]
BOXED_LABELS_HANGUL_SYLLABLES = ["mgmt_0367", "mgmt_0388"]
BOXED_LABELS_LATIN_LETTERS = [
    "mgmt_0444", "mgmt_0450", "mgmt_0460", "mgmt_0461",
    "mgmt_0480", "mgmt_0490", "mgmt_0507"
]

# 4-choice cards in Chapter 02 (total 56 cards)
# 5-choice cards in Chapter 02 (total 175 cards)
TOTAL_4_CHOICE_COUNT = 56
TOTAL_5_CHOICE_COUNT = 175

# Outlier Card IDs
OUTLIER_0374_ZERO_BYTE = "mgmt_0374"
OUTLIER_0278_DUPLICATE_OPTIONS = "mgmt_0278"
OUTLIER_0454_MATRIX_LAYOUT = "mgmt_0454"
OUTLIER_0501_ANS_PAGE = "mgmt_0501"

VALID_OPTION_LABELS = {"①", "②", "③", "④", "⑤"}

# ---------------------------------------------------------------------------
# Caching & Safe Loaders
# ---------------------------------------------------------------------------
_cached_cards_data: Optional[dict] = None
_cached_page_map: Optional[dict] = None

def load_cards_data(path: Optional[Path | str] = None, reload: bool = False) -> dict:
    """Safely loads cards-data.json with memoization and detailed diagnostics."""
    global _cached_cards_data
    if _cached_cards_data is not None and not reload and path is None:
        return _cached_cards_data

    target_path = Path(path) if path else CARDS_DATA_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"cards-data.json not found at: {target_path}")

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON syntax in {target_path} at line {e.lineno}, col {e.colno}: {e.msg}"
        ) from e

    if "cards" not in data or not isinstance(data["cards"], list):
        raise ValueError("Malformed cards-data.json: missing top-level 'cards' array.")

    if path is None:
        _cached_cards_data = data
    return data


def load_page_map(path: Optional[Path | str] = None, reload: bool = False) -> dict:
    """Safely loads pdf-page-map.json with memoization and validation."""
    global _cached_page_map
    if _cached_page_map is not None and not reload and path is None:
        return _cached_page_map

    target_path = Path(path) if path else PAGE_MAP_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"pdf-page-map.json not found at: {target_path}")

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON syntax in {target_path} at line {e.lineno}, col {e.colno}: {e.msg}"
        ) from e

    if not isinstance(data, dict):
        raise ValueError("Malformed pdf-page-map.json: expected dict mapping qid to metadata.")

    if path is None:
        _cached_page_map = data
    return data


# ---------------------------------------------------------------------------
# Dataset Slicing & Query Helpers
# ---------------------------------------------------------------------------
def get_chapter2_cards(cards_data: Optional[dict] = None) -> List[dict]:
    """Returns the contiguous list of 231 Chapter 02 cards (mgmt_0277~mgmt_0507)."""
    data = cards_data if cards_data is not None else load_cards_data()
    ch2 = [c for c in data["cards"] if CH2_START_ID <= c.get("id", "") <= CH2_END_ID]
    return ch2

# Standard alias matching alternate naming
get_chapter02_cards = get_chapter2_cards


def get_chapter2_card_map(cards_data: Optional[dict] = None) -> Dict[str, dict]:
    """Returns an O(1) dictionary mapping card id (e.g. 'mgmt_0277') to card dict."""
    cards = get_chapter2_cards(cards_data)
    return {c["id"]: c for c in cards}

get_chapter02_card_map = get_chapter2_card_map


def get_chapter2_card_by_id(card_id: str, cards_data: Optional[dict] = None) -> dict:
    """Looks up a Chapter 02 card by its full id (e.g. 'mgmt_0277')."""
    cmap = get_chapter2_card_map(cards_data)
    if card_id not in cmap:
        raise KeyError(f"Card {card_id} not found in Chapter 02 dataset.")
    return cmap[card_id]


def get_chapter2_card_by_qid(qid: str, cards_data: Optional[dict] = None) -> dict:
    """Looks up a Chapter 02 card by qid (e.g. '0277' or '277')."""
    qid_padded = qid.zfill(4)
    cid = f"mgmt_{qid_padded}"
    return get_chapter2_card_by_id(cid, cards_data)


# ---------------------------------------------------------------------------
# Pattern Detection & Validation Utilities
# ---------------------------------------------------------------------------
def has_emoji(s: str) -> bool:
    """
    Detects Unicode emojis across standard blocks with zero false positives
    for Korean Hangul syllables, Hanja, and standard punctuation.
    """
    for ch in s:
        cp = ord(ch)
        if (
            0x1F600 <= cp <= 0x1F64F or  # Emoticons
            0x1F300 <= cp <= 0x1F5FF or  # Misc Symbols & Pictographs
            0x1F680 <= cp <= 0x1F6FF or  # Transport & Map Symbols
            0x1F900 <= cp <= 0x1F9FF or  # Supplemental Symbols
            0x1FA70 <= cp <= 0x1FAFF or  # Symbols & Pictographs Ext-A
            0x2600  <= cp <= 0x26FF  or  # Misc Symbols
            0x2700  <= cp <= 0x27BF      # Dingbats
        ):
            return True
    return False


PREFIX_INDEX_OR_CIRCLE_PAT = re.compile(
    r"^\s*("
    r"[①②③④⑤⑥⑦⑧⑨⑩\u2460-\u2473]"         # circled digits (1-20)
    r"|[❶❷❸❹❺❻❼❽❾❿\u2776-\u277f]"       # dingbat negative circled digits (1-10)
    r"|[㉠㉡㉢㉣㉤\u3260-\u3264]"           # circled hangul consonants (ㄱ-ㅁ)
    r"|\(\s*\d+\s*\)\s*"                 # (1) or ( 1 ) with internal spaces
    r"|\d+[\.\:\)]\s*"                   # 1. or 1: or 1)
    r"|\d+번[\:\.]?\s*"                  # 1번:
    r")"
)

def has_leading_index_or_circle(text: str) -> bool:
    """
    Detects forbidden leading circled numbers or option indexes.
    Preserves legitimate terms like '3M의 혁신' or '1차원적 사고'.
    """
    return bool(PREFIX_INDEX_OR_CIRCLE_PAT.match(text))


# ---------------------------------------------------------------------------
# HTML Parsing Engine (Dependency-Free Standard Library)
# ---------------------------------------------------------------------------
@dataclass
class ParsedOption:
    tag: str
    classes: List[str]
    data_original: str
    label: str
    choice_text: str

    @property
    def is_text_option(self) -> bool:
        return "text-option" in self.classes

    @property
    def is_number_option(self) -> bool:
        return "number-option" in self.classes


@dataclass
class ParsedStatementItem:
    data_stmt: str
    badge: str
    text: str


@dataclass
class ParsedCardFront:
    raw_html: str = ""
    card_classes: List[str] = field(default_factory=list)
    data_qid: str = ""
    data_mode: str = ""
    question_number: str = ""
    source_badge: str = ""
    stem_ocr_text: str = ""
    has_image_frame: bool = False
    image_frame_count: int = 0
    img_tags: List[Dict[str, str]] = field(default_factory=list)
    has_statement_box: bool = False
    statement_box_classes: List[str] = field(default_factory=list)
    statement_header: str = ""
    statement_items: List[ParsedStatementItem] = field(default_factory=list)
    options: List[ParsedOption] = field(default_factory=list)
    has_ox_buttons: bool = False
    has_elim_buttons: bool = False

    @property
    def choice_texts(self) -> List[str]:
        return [opt.choice_text for opt in self.options]

    @property
    def labels(self) -> List[str]:
        return [opt.label for opt in self.options]

    @property
    def is_pure_text(self) -> bool:
        return not self.has_image_frame and len(self.img_tags) == 0

    @property
    def option_count(self) -> int:
        return len(self.options)


class CardFrontParser(HTMLParser):
    """
    Standard-library HTML state parser for MCQ Card front HTML.
    Handles Korean text, nested elements, unescaped literal <보기>, and tags.
    """
    def __init__(self):
        super().__init__()
        self.result = ParsedCardFront()
        self._tag_stack: List[Tuple[str, List[str], Dict[str, str]]] = []
        self._current_button: Optional[ParsedOption] = None
        self._current_stmt_item: Optional[ParsedStatementItem] = None
        self._active_capture: Optional[str] = None
        self._stem_depth: int = 0
        self._in_stem: bool = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k: v or "" for k, v in attrs}
        classes = attr_dict.get("class", "").split()
        self._tag_stack.append((tag, classes, attr_dict))

        if "mcq-card" in classes:
            self.result.card_classes = classes
            self.result.data_qid = attr_dict.get("data-qid", "")
            self.result.data_mode = attr_dict.get("data-mode", "")

        if "image-frame" in classes:
            self.result.has_image_frame = True
            self.result.image_frame_count += 1

        if tag == "img":
            self.result.img_tags.append(attr_dict)

        if "statement-box" in classes or "mcq-statement-box" in classes:
            self.result.has_statement_box = True
            self.result.statement_box_classes = classes

        if "mcq-statement-item" in classes:
            self._current_stmt_item = ParsedStatementItem(
                data_stmt=attr_dict.get("data-stmt", ""),
                badge="",
                text=""
            )

        if "mcq-ox-btn" in classes:
            self.result.has_ox_buttons = True
        if "mcq-elim-btn" in classes:
            self.result.has_elim_buttons = True

        if tag == "button" and "mcq-option" in classes:
            self._current_button = ParsedOption(
                tag=tag,
                classes=classes,
                data_original=attr_dict.get("data-original", ""),
                label="",
                choice_text=""
            )

        if "stem-ocr-text" in classes:
            self._in_stem = True
            self._stem_depth = len(self._tag_stack)

        if "question-number" in classes or "mcq-qnum" in classes:
            self._active_capture = "question-number"
        elif "source-badge" in classes:
            self._active_capture = "source-badge"
        elif "mcq-statement-header" in classes:
            self._active_capture = "statement-header"
        elif "mcq-stmt-badge" in classes:
            self._active_capture = "stmt-badge"
        elif "mcq-stmt-text" in classes:
            self._active_capture = "stmt-text"
        elif "mcq-label" in classes:
            self._active_capture = "mcq-label"
        elif "mcq-choice-text" in classes:
            self._active_capture = "mcq-choice-text"

    def _update_active_capture(self) -> None:
        """Restores _active_capture to the nearest enclosing capture element on the stack."""
        for _, classes, _ in reversed(self._tag_stack):
            if "question-number" in classes or "mcq-qnum" in classes:
                self._active_capture = "question-number"
                return
            if "source-badge" in classes:
                self._active_capture = "source-badge"
                return
            if "mcq-statement-header" in classes:
                self._active_capture = "statement-header"
                return
            if "mcq-stmt-badge" in classes:
                self._active_capture = "stmt-badge"
                return
            if "mcq-stmt-text" in classes:
                self._active_capture = "stmt-text"
                return
            if "mcq-label" in classes:
                self._active_capture = "mcq-label"
                return
            if "mcq-choice-text" in classes:
                self._active_capture = "mcq-choice-text"
                return
        self._active_capture = None

    def handle_endtag(self, tag: str):
        if self._in_stem and len(self._tag_stack) <= self._stem_depth:
            self._in_stem = False

        if tag == "button" and self._current_button:
            self.result.options.append(self._current_button)
            self._current_button = None

        if self._current_stmt_item and self._tag_stack and "mcq-statement-item" in self._tag_stack[-1][1]:
            self.result.statement_items.append(self._current_stmt_item)
            self._current_stmt_item = None

        if self._tag_stack:
            self._tag_stack.pop()

        self._update_active_capture()

    def handle_data(self, data: str):
        cleaned = data.strip()
        if not cleaned:
            return

        if self._in_stem and self._active_capture not in (
            "source-badge", "statement-header", "stmt-badge", "stmt-text"
        ):
            if self.result.stem_ocr_text:
                self.result.stem_ocr_text += " " + cleaned
            else:
                self.result.stem_ocr_text = cleaned

        if self._active_capture == "question-number":
            self.result.question_number += (" " if self.result.question_number else "") + cleaned
        elif self._active_capture == "source-badge":
            self.result.source_badge += (" " if self.result.source_badge else "") + cleaned
        elif self._active_capture == "statement-header":
            self.result.statement_header += (" " if self.result.statement_header else "") + cleaned
        elif self._active_capture == "stmt-badge" and self._current_stmt_item:
            self._current_stmt_item.badge += cleaned
        elif self._active_capture == "stmt-text" and self._current_stmt_item:
            self._current_stmt_item.text += (" " if self._current_stmt_item.text else "") + cleaned
        elif self._active_capture == "mcq-label" and self._current_button:
            self._current_button.label += cleaned
        elif self._active_capture == "mcq-choice-text" and self._current_button:
            self._current_button.choice_text += (" " if self._current_button.choice_text else "") + cleaned


def parse_card_front(html_str: str) -> ParsedCardFront:
    """Parses front HTML string into a structured ParsedCardFront object."""
    parser = CardFrontParser()
    parser.result.raw_html = html_str
    parser.feed(html_str)
    return parser.result


# ---------------------------------------------------------------------------
# Targeted Assertion Helpers
# ---------------------------------------------------------------------------
def assert_zero_image_frames(card: dict, parsed: Optional[ParsedCardFront] = None) -> None:
    """Asserts that the card contains zero image frames and zero img tags."""
    cid = card.get("id", "unknown")
    pf = parsed or parse_card_front(card.get("front", ""))
    assert not pf.has_image_frame, f"Card {cid} contains {pf.image_frame_count} image-frame tags in front HTML."
    assert len(pf.img_tags) == 0, f"Card {cid} contains {len(pf.img_tags)} img tags in front HTML: {pf.img_tags}"
    assert "image-frame" not in card.get("front", ""), f"Card {cid} front contains substring 'image-frame'."


def assert_clean_options(card: dict, parsed: Optional[ParsedCardFront] = None) -> None:
    """Asserts that all options are clean text buttons without leading circles or indexes."""
    cid = card.get("id", "unknown")
    pf = parsed or parse_card_front(card.get("front", ""))
    assert pf.option_count in (4, 5), f"Card {cid} has {pf.option_count} options (must be 4 or 5)."
    for i, opt in enumerate(pf.options, 1):
        assert opt.is_text_option, f"Card {cid} option {i} missing 'text-option' class: {opt.classes}"
        assert not opt.is_number_option, f"Card {cid} option {i} still has 'number-option' class."
        assert opt.data_original == str(i), f"Card {cid} option {i} data-original is '{opt.data_original}'."
        assert opt.label in VALID_OPTION_LABELS, f"Card {cid} option {i} label '{opt.label}' invalid."
        assert len(opt.choice_text.strip()) > 0, f"Card {cid} option {i} has empty choice text."
        assert not has_leading_index_or_circle(opt.choice_text), (
            f"Card {cid} option {i} contains leading circled number or index prefix: '{opt.choice_text}'"
        )
        assert not has_emoji(opt.choice_text), f"Card {cid} option {i} contains emoji: '{opt.choice_text}'"


# ---------------------------------------------------------------------------
# Automated Verification Tooling (Survey / R4 Validator)
# ---------------------------------------------------------------------------
def verify_restored_cards(
    path: Optional[Path | str] = None,
    start_id: str = CH2_START_ID,
    end_id: str = CH2_END_ID,
    expected_count: int = CH2_CARD_COUNT
) -> List[str]:
    """
    Automated verification function that audits restored cards in the specified slice.
    Returns a list of human-readable error descriptions. Empty list means 100% valid.
    Audits image frames, emojis, button markup, clean choice texts, sequential data-original,
    and boxed statement formatting.
    """
    errors: List[str] = []
    target_path = Path(path) if path else CARDS_DATA_PATH
    if not target_path.exists():
        return [f"File not found: {target_path}"]

    try:
        data = load_cards_data(target_path)
    except Exception as e:
        return [f"Failed to load JSON: {str(e)}"]

    cards = data.get("cards", [])
    ch_cards = [c for c in cards if start_id <= c.get("id", "") <= end_id]

    if len(ch_cards) != expected_count:
        errors.append(f"Card count mismatch: expected {expected_count}, got {len(ch_cards)}")

    for c in ch_cards:
        cid = c.get("id", "unknown")
        front = c.get("front", "")

        # 1. Image frame, img, and emoji elimination check
        if "image-frame" in front:
            errors.append(f"{cid}: contains 'image-frame'")
        if "<img" in front:
            errors.append(f"{cid}: contains '<img>' tag")
        if "number-option" in front:
            errors.append(f"{cid}: contains 'number-option'")
        if has_emoji(front):
            errors.append(f"{cid}: front HTML contains emoji")
        stem_text = c.get("stemText", "")
        if has_emoji(stem_text):
            errors.append(f"{cid}: stemText contains emoji")

        # 2. Choices check
        choices = c.get("choices", [])
        if len(choices) not in (4, 5):
            errors.append(f"{cid}: choices count {len(choices)} not 4 or 5")
        for idx, ch in enumerate(choices, 1):
            if has_emoji(ch):
                errors.append(f"{cid}: choices[{idx}] contains emoji: '{ch}'")

        # 3. Text options check
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', front, re.DOTALL)
        if len(buttons) != len(choices):
            errors.append(f"{cid}: button count ({len(buttons)}) != choices count ({len(choices)})")

        for i, btn in enumerate(buttons, 1):
            # 3a. Sequential data-original check
            data_orig_match = re.search(r'data-original=["\']([^"\']*)["\']', btn)
            if not data_orig_match:
                errors.append(f"{cid}: button {i} missing data-original attribute")
            elif data_orig_match.group(1) != str(i):
                errors.append(f"{cid}: button {i} data-original is '{data_orig_match.group(1)}', expected '{i}'")

            # 3b. <span class="mcq-choice-text"> presence check
            choice_span_match = re.search(
                r'<span\b[^>]*class=["\'][^"\']*mcq-choice-text[^"\']*["\'][^>]*>(.*?)</span>',
                btn,
                re.DOTALL
            )
            if not choice_span_match:
                errors.append(f"{cid}: button {i} missing '<span class=\"mcq-choice-text\">'")
            else:
                clean_choice = re.sub(r'<[^>]+>', '', choice_span_match.group(1)).strip()
                if not clean_choice:
                    errors.append(f"{cid}: button {i} choice text is empty")
                if has_leading_index_or_circle(clean_choice):
                    errors.append(
                        f"{cid}: button {i} choice text contains leading circled number or index prefix: '{clean_choice}'"
                    )
                if has_emoji(clean_choice):
                    errors.append(f"{cid}: button {i} choice text contains emoji: '{clean_choice}'")

        # 4. Boxed statement check
        if c.get("typ") == "박스선택형":
            if "statement-box" not in front and "mcq-statement-box" not in front:
                errors.append(f"{cid}: 박스선택형 card missing statement-box container")
            stmts = c.get("boxStatements")
            if not isinstance(stmts, list) or len(stmts) == 0:
                errors.append(f"{cid}: 박스선택형 card has invalid or empty boxStatements")

    return errors
