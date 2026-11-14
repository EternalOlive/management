# -*- coding: utf-8 -*-
"""
tests/test_tier1_features.py
Tier 1: Feature Coverage E2E Test Suite (Features F1 through F6, 36 tests)
Derived verbatim from Explorer 1 specification for Management Cards Chapter 02.
"""

from __future__ import annotations
import unittest
import json
import re
from pathlib import Path

try:
    from tests.test_utils import (
        get_chapter02_cards,
        load_cards_data,
        load_page_map,
        CARDS_DATA_PATH,
        PAGE_MAP_PATH,
        verify_restored_cards,
        has_leading_index_or_circle,
        has_emoji,
    )
except ImportError:
    from test_utils import (
        get_chapter02_cards,
        load_cards_data,
        load_page_map,
        CARDS_DATA_PATH,
        PAGE_MAP_PATH,
        verify_restored_cards,
        has_leading_index_or_circle,
        has_emoji,
    )


# ===========================================================================
# Feature F1: Card Text Option Restoration (ORIGINAL_REQUEST §R1)
# ===========================================================================
class TestTier1_F1_TextOptionRestoration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()

    def test_f1_01_all_cards_contain_only_text_option_buttons(self):
        """F1-01: Every card contains exclusively text-option buttons, zero number-option."""
        for c in self.cards:
            front = c.get('front', '')
            self.assertNotIn('number-option', front, f"{c['id']} contains legacy number-option")
            buttons = re.findall(r'<button\b([^>]*)>', front)
            self.assertGreater(len(buttons), 0, f"{c['id']} has no button tags")
            for b in buttons:
                self.assertRegex(b, r'class="[^"]*\bmcq-option\s+text-option\b[^"]*"', f"{c['id']} button missing text-option class: {b}")

    def test_f1_02_button_count_strictly_matches_choices_length(self):
        """F1-02: Button count strictly matches choices length (strictly 4 or 5)."""
        for c in self.cards:
            front = c.get('front', '')
            choices = c.get('choices', [])
            buttons = re.findall(r'<button\b[^>]*>.*?</button>', front, re.DOTALL)
            self.assertIn(len(choices), [4, 5], f"{c['id']} choices length must be 4 or 5, got {len(choices)}")
            self.assertEqual(len(buttons), len(choices), f"{c['id']} button count ({len(buttons)}) != choices length ({len(choices)})")

    def test_f1_03_button_labels_contain_sequential_circled_numbers(self):
        """F1-03: mcq-label elements contain sequential circled numbers (①..④ or ①..⑤)."""
        circles = ['①', '②', '③', '④', '⑤']
        for c in self.cards:
            front = c.get('front', '')
            labels = re.findall(r'<span class="mcq-label">\s*([^<]+?)\s*</span>', front)
            expected = circles[:len(c['choices'])]
            self.assertEqual(labels, expected, f"{c['id']} labels {labels} != expected {expected}")

    def test_f1_04_data_original_attributes_sequential_and_in_range(self):
        """F1-04: data-original attributes are sequential strings ('1'..'4' or '1'..'5')."""
        for c in self.cards:
            front = c.get('front', '')
            data_orig = re.findall(r'data-original="(\d+)"', front)
            expected = [str(i + 1) for i in range(len(c['choices']))]
            self.assertEqual(data_orig, expected, f"{c['id']} data-original {data_orig} != expected {expected}")

    def test_f1_05_choice_text_spans_clean_without_leading_indices(self):
        """F1-05: Choice text spans are non-empty and free of leading circled numbers or numeric indices."""
        for c in self.cards:
            front = c.get('front', '')
            choice_texts = re.findall(r'<span class="mcq-choice-text">(.*?)</span>', front, re.DOTALL)
            self.assertEqual(len(choice_texts), len(c['choices']), f"{c['id']} choice text spans count mismatch")
            for idx, text in enumerate(choice_texts):
                clean = text.strip()
                self.assertTrue(len(clean) > 0, f"{c['id']} choice {idx+1} is empty")
                self.assertFalse(has_leading_index_or_circle(clean), f"{c['id']} choice {idx+1} has leading number/circle: {clean}")

    def test_f1_06_choices_array_string_format(self):
        """F1-06: Raw choices array entries start with 'N번:' and contain no circled numbers."""
        for c in self.cards:
            choices = c.get('choices', [])
            for idx, ch in enumerate(choices):
                expected_prefix = f"{idx + 1}번:"
                self.assertTrue(ch.startswith(expected_prefix), f"{c['id']} choice {idx+1} missing prefix '{expected_prefix}': {ch}")
                self.assertNotRegex(ch, r'[①②③④⑤]', f"{c['id']} choice {idx+1} contains circled numbers: {ch}")


# ===========================================================================
# Feature F2: Boxed Statement Formatting (ORIGINAL_REQUEST §R2)
# ===========================================================================
BOXED_IDS = {
    'mgmt_0313', 'mgmt_0323', 'mgmt_0325', 'mgmt_0342', 'mgmt_0367',
    'mgmt_0372', 'mgmt_0374', 'mgmt_0378', 'mgmt_0380', 'mgmt_0388',
    'mgmt_0405', 'mgmt_0428', 'mgmt_0429', 'mgmt_0444', 'mgmt_0450',
    'mgmt_0460', 'mgmt_0461', 'mgmt_0480', 'mgmt_0490', 'mgmt_0507'
}

class TestTier1_F2_BoxedStatementFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()
        cls.cards_map = {c['id']: c for c in cls.cards}

    def test_f2_01_exactly_twenty_cards_classified_as_boxed_type(self):
        """F2-01: Exactly 20 cards in Chapter 02 have typ == '박스선택형' matching canonical set."""
        boxed_found = {c['id'] for c in self.cards if c.get('typ') == '박스선택형'}
        self.assertEqual(boxed_found, BOXED_IDS, f"Boxed cards set mismatch: diff={boxed_found.symmetric_difference(BOXED_IDS)}")
        self.assertEqual(len(boxed_found), 20)

    def test_f2_02_boxed_cards_contain_statement_box_container_in_stem(self):
        """F2-02: All 20 boxed cards place statement-box container inside mcq-stem."""
        for bid in BOXED_IDS:
            c = self.cards_map[bid]
            front = c.get('front', '')
            self.assertTrue(
                'statement-box' in front or 'mcq-statement-box' in front,
                f"{bid} front missing statement-box container"
            )
            stem_m = re.search(r'<div class="mcq-stem">(.*?)</div>\s*<div class="mcq-options', front, re.DOTALL)
            self.assertIsNotNone(stem_m, f"{bid} could not find mcq-stem boundary")
            self.assertTrue(
                'statement-box' in stem_m.group(1) or 'mcq-statement-box' in stem_m.group(1),
                f"{bid} statement-box is not placed inside mcq-stem"
            )

    def test_f2_03_statement_box_items_structure(self):
        """F2-03: Statement box items have mcq-statement-item, mcq-stmt-badge, and mcq-stmt-text."""
        for bid in BOXED_IDS:
            c = self.cards_map[bid]
            front = c.get('front', '')
            items = re.findall(r'<div class="mcq-statement-item"\s+data-stmt="([^"]+)">(.*?)</div>\s*(?=<div class="mcq-statement-item"|</div>\s*</div>)', front, re.DOTALL)
            self.assertGreater(len(items), 0, f"{bid} has no mcq-statement-item elements")
            for stmt_label, item_html in items:
                self.assertIn(f'<span class="mcq-stmt-badge">{stmt_label}</span>', item_html, f"{bid} badge mismatch for {stmt_label}")
                self.assertIn('mcq-stmt-text', item_html, f"{bid} missing mcq-stmt-text for {stmt_label}")

    def test_f2_04_box_statements_json_schema_completeness(self):
        """F2-04: boxStatements JSON array is populated with valid id, label, and text fields."""
        for bid in BOXED_IDS:
            c = self.cards_map[bid]
            stmts = c.get('boxStatements')
            self.assertIsInstance(stmts, list, f"{bid} boxStatements is not a list")
            self.assertGreater(len(stmts), 0, f"{bid} boxStatements is empty")
            for stmt in stmts:
                self.assertIn('id', stmt, f"{bid} stmt missing id")
                self.assertIn('label', stmt, f"{bid} stmt missing label")
                self.assertIn('text', stmt, f"{bid} stmt missing text")
                self.assertEqual(stmt['id'], stmt['label'], f"{bid} stmt id != label")
                self.assertTrue(len(stmt['text'].strip()) > 0, f"{bid} stmt text is empty")

    def test_f2_05_boxed_card_buttons_formatted_with_clean_choice_combinations(self):
        """F2-05: Boxed card buttons are concise combinations (<50 chars) without full question text."""
        for bid in BOXED_IDS:
            c = self.cards_map[bid]
            front = c.get('front', '')
            choice_texts = re.findall(r'<span class="mcq-choice-text">(.*?)</span>', front, re.DOTALL)
            for ct in choice_texts:
                clean = ct.strip()
                self.assertLess(len(clean), 50, f"{bid} choice text appears too long for boxed combination: '{clean}'")

    def test_f2_06_non_boxed_cards_have_no_statement_boxes(self):
        """F2-06: Exactly 211 non-boxed cards have typ == '객관식' and zero statement boxes."""
        non_boxed = [c for c in self.cards if c['id'] not in BOXED_IDS]
        self.assertEqual(len(non_boxed), 211)
        for c in non_boxed:
            self.assertEqual(c.get('typ'), '객관식', f"{c['id']} non-boxed typ should be '객관식'")
            front = c.get('front', '')
            self.assertNotIn('mcq-statement-box', front, f"{c['id']} unexpected mcq-statement-box")
            self.assertNotIn('statement-box', front, f"{c['id']} unexpected statement-box")


# ===========================================================================
# Feature F3: Frame Cleanup & Design System Compliance (ORIGINAL_REQUEST §R3)
# ===========================================================================
class TestTier1_F3_FrameCleanupAndTokensCss(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()

    def test_f3_01_zero_image_frames_in_front_html(self):
        """F3-01: Zero image-frame classes in front HTML across all 231 cards."""
        violating_cards = [c['id'] for c in self.cards if 'image-frame' in c.get('front', '')]
        self.assertEqual(len(violating_cards), 0, f"Cards retaining image-frame: {violating_cards}")

    def test_f3_02_zero_img_tags_in_front_html(self):
        """F3-02: Zero <img> tags in front HTML across all 231 cards."""
        violating_cards = [c['id'] for c in self.cards if '<img' in c.get('front', '')]
        self.assertEqual(len(violating_cards), 0, f"Cards retaining <img>: {violating_cards}")

    def test_f3_03_zero_number_option_classes(self):
        """F3-03: Zero number-option classes in front HTML across all 231 cards."""
        violating_cards = [c['id'] for c in self.cards if 'number-option' in c.get('front', '')]
        self.assertEqual(len(violating_cards), 0, f"Cards retaining number-option: {violating_cards}")

    def test_f3_04_root_container_and_canonical_css_classes(self):
        """F3-04: Canonical DOM structure exists with mcq-card, mcq-stem, mcq-options, and mcq-help."""
        for c in self.cards:
            front = c.get('front', '')
            qid = c['qid']
            self.assertIn(f'<div class="mcq-card" data-qid="{qid}" data-shuffle="false"', front, f"{c['id']} missing canonical root container")
            self.assertIn('mcq-stem', front, f"{c['id']} missing mcq-stem class")
            self.assertIn('mcq-options', front, f"{c['id']} missing mcq-options class")
            self.assertIn('mcq-help', front, f"{c['id']} missing mcq-help class")

    def test_f3_05_no_emojis_in_front_or_back(self):
        """F3-05: Strictly zero emojis in front or back HTML."""
        for c in self.cards:
            front = c.get('front', '')
            back = c.get('back', '')
            self.assertFalse(has_emoji(front), f"{c['id']} contains emoji in front HTML")
            self.assertFalse(has_emoji(back), f"{c['id']} contains emoji in back HTML")

    def test_f3_06_no_runtime_injected_buttons_in_stored_json(self):
        """F3-06: Neither mcq-ox-btn nor mcq-elim-btn is statically saved in JSON."""
        for c in self.cards:
            front = c.get('front', '')
            back = c.get('back', '')
            self.assertNotIn('mcq-ox-btn', front, f"{c['id']} statically stores mcq-ox-btn in front")
            self.assertNotIn('mcq-elim-btn', front, f"{c['id']} statically stores mcq-elim-btn in front")
            self.assertNotIn('mcq-ox-btn', back, f"{c['id']} statically stores mcq-ox-btn in back")


# ===========================================================================
# Feature F4: Stem Text & Metadata Population (ORIGINAL_REQUEST §R1)
# ===========================================================================
class TestTier1_F4_StemTextAndMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()

    def test_f4_01_all_chapter02_cards_have_non_empty_stem_text(self):
        """F4-01: stemText is non-empty string with len >= 5 for all 231 cards."""
        for c in self.cards:
            stem = c.get('stemText', '')
            self.assertIsInstance(stem, str, f"{c['id']} stemText is not str")
            self.assertGreaterEqual(len(stem.strip()), 5, f"{c['id']} stemText too short or empty: '{stem}'")

    def test_f4_02_front_html_contains_stem_ocr_text_container(self):
        """F4-02: front HTML contains stem-ocr-text element with non-empty content."""
        for c in self.cards:
            front = c.get('front', '')
            self.assertIn('stem-ocr-text', front, f"{c['id']} missing stem-ocr-text in front HTML")
            stem_m = re.search(r'<div class="stem-ocr-text">(.*?)</div>', front, re.DOTALL)
            self.assertIsNotNone(stem_m, f"{c['id']} cannot match stem-ocr-text element")
            self.assertGreater(len(stem_m.group(1).strip()), 0, f"{c['id']} stem-ocr-text is empty")

    def test_f4_03_source_tag_rendered_as_badge_when_populated(self):
        """F4-03: When sourceTag is present, rendered as <span class="source-badge">."""
        for c in self.cards:
            src = c.get('sourceTag', '')
            front = c.get('front', '')
            if src and src.strip():
                self.assertIn(f'<span class="source-badge">{src.strip()}</span>', front, f"{c['id']} sourceTag badge missing or mismatch")

    def test_f4_04_subject_field_strictly_constant(self):
        """F4-04: subj field strictly equals '1.02 조직행동: 개인' for all 231 cards."""
        for c in self.cards:
            self.assertEqual(c.get('subj'), '1.02 조직행동: 개인', f"{c['id']} subj mismatch")

    def test_f4_05_search_field_populated_and_synchronized(self):
        """F4-05: search index contains qid and subj separated by pipes."""
        for c in self.cards:
            search = c.get('search', '')
            self.assertIn(c['qid'], search, f"{c['id']} search missing qid")
            self.assertIn(c['subj'], search, f"{c['id']} search missing subj")
            self.assertIn('|', search, f"{c['id']} search missing pipe delimiter")

    def test_f4_06_tags_list_structure(self):
        """F4-06: tags is a list containing subj and '문 {qid}'."""
        for c in self.cards:
            tags = c.get('tags', [])
            self.assertIsInstance(tags, list, f"{c['id']} tags is not a list")
            self.assertIn(c['subj'], tags, f"{c['id']} tags missing subj")
            self.assertIn(f"문 {c['qid']}", tags, f"{c['id']} tags missing '문 {c['qid']}'")


# ===========================================================================
# Feature F5: Outlier & Anomaly Resolutions (Survey Reports 1 & 2)
# ===========================================================================
class TestTier1_F5_OutlierResolutions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards_map = {c['id']: c for c in get_chapter02_cards()}
        cls.page_map = load_page_map()

    def test_f5_01_mgmt_0374_zero_byte_fallback_restored(self):
        """F5-01: mgmt_0374 zero-byte image fallback restored with Herzberg 2-factor theory."""
        c = self.cards_map['mgmt_0374']
        front = c.get('front', '')
        self.assertNotIn('_jh_q_0374.webp', front, "mgmt_0374 front references 0-byte image")
        self.assertNotIn('<img', front, "mgmt_0374 front contains <img>")
        self.assertEqual(c.get('typ'), '박스선택형', "mgmt_0374 typ should be '박스선택형'")
        self.assertEqual(len(c.get('choices', [])), 5, "mgmt_0374 choices length should be 5")
        self.assertEqual(c.get('correct'), 4, "mgmt_0374 correct answer should be 4")
        stem = c.get('stemText', '')
        self.assertTrue('허츠버그' in stem or '2요인' in stem or '동기요인' in stem, f"mgmt_0374 stem unexpected: {stem}")

    def test_f5_02_mgmt_0501_answer_page_patched(self):
        """F5-02: mgmt_0501 ans_page patched to 56 in both cards-data.json and pdf-page-map.json."""
        c = self.cards_map['mgmt_0501']
        self.assertEqual(c.get('ansPage'), 56, f"mgmt_0501 ansPage in cards-data.json is {c.get('ansPage')}, expected 56 (not 112)")
        entry = self.page_map.get('0501', {})
        self.assertEqual(entry.get('ans_page'), 56, f"0501 ans_page in pdf-page-map.json is {entry.get('ans_page')}, expected 56 (not 112)")

    def test_f5_03_mgmt_0278_no_duplicate_options(self):
        """F5-03: mgmt_0278 contains no duplicate options or full image frame."""
        c = self.cards_map['mgmt_0278']
        front = c.get('front', '')
        self.assertNotIn('image-frame', front, "mgmt_0278 contains image-frame")
        self.assertNotIn('_jh_q_0278.webp', front, "mgmt_0278 contains _jh_q_0278.webp")
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', front, re.DOTALL)
        self.assertEqual(len(buttons), 5, f"mgmt_0278 button count {len(buttons)} != 5")

    def test_f5_04_mgmt_0454_table_matrix_layout(self):
        """F5-04: mgmt_0454 represents 3-column attribution matrix cleanly without raw table tags."""
        c = self.cards_map['mgmt_0454']
        front = c.get('front', '')
        self.assertNotIn('<table', front, "mgmt_0454 front contains raw <table> tag")
        choices = c.get('choices', [])
        self.assertEqual(len(choices), 5, f"mgmt_0454 choices length {len(choices)} != 5")
        expected_patterns = ['높음 높음 높음', '높음 높음 낮음', '낮음 낮음 높음', '낮음 높음 낮음', '낮음 낮음 낮음']
        for idx, pat in enumerate(expected_patterns):
            self.assertIn(pat, choices[idx], f"mgmt_0454 choice {idx+1} does not contain '{pat}'")

    def test_f5_05_mgmt_0277_truncated_options_restored(self):
        """F5-05: mgmt_0277 OCR sentence truncations restored with complete sentences."""
        c = self.cards_map['mgmt_0277']
        choices = c.get('choices', [])
        self.assertEqual(len(choices), 5)
        self.assertTrue(choices[1].endswith('.') or '보완' in choices[1], f"mgmt_0277 choice 2 truncated: {choices[1]}")
        self.assertTrue(choices[3].endswith('.') or '논쟁' in choices[3], f"mgmt_0277 choice 4 truncated: {choices[3]}")
        self.assertNotIn('Ghjst', choices[4], "mgmt_0277 choice 5 retains 'Ghjst' OCR noise")

    def test_f5_06_master_pdf_source_integrity_for_outliers(self):
        """F5-06: Outliers retain valid probPage and ansPage integers."""
        for qid in ['mgmt_0278', 'mgmt_0374', 'mgmt_0454', 'mgmt_0501']:
            c = self.cards_map[qid]
            self.assertGreater(c.get('probPage', 0), 0, f"{qid} invalid probPage")
            self.assertGreater(c.get('ansPage', 0), 0, f"{qid} invalid ansPage")


# ===========================================================================
# Feature F6: Automated Verification Tooling & Schema Integrity (ORIGINAL_REQUEST §R4)
# ===========================================================================
class TestTier1_F6_AutomatedVerificationTooling(unittest.TestCase):
    def test_f6_01_cards_data_json_syntax_and_load(self):
        """F6-01: cards-data.json loads cleanly as valid JSON with top-level 'cards' array."""
        with open(CARDS_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('cards', data, "cards-data.json missing top-level 'cards' key")
        self.assertIsInstance(data['cards'], list, "'cards' is not a list")

    def test_f6_02_chapter02_card_count_and_continuity(self):
        """F6-02: Chapter 02 slice contains exactly 231 contiguous cards (mgmt_0277~mgmt_0507)."""
        cards = get_chapter02_cards()
        self.assertEqual(len(cards), 231, f"Chapter 02 card count {len(cards)} != 231")
        for i, c in enumerate(cards):
            expected_qid = f"{277 + i:04d}"
            expected_id = f"mgmt_{expected_qid}"
            self.assertEqual(c['id'], expected_id, f"Index {i} expected {expected_id}, got {c['id']}")
            self.assertEqual(c['qid'], expected_qid, f"{c['id']} qid mismatch")

    def test_f6_03_correct_answer_range_and_type(self):
        """F6-03: correct field is integer within range [1, len(choices)]."""
        for c in get_chapter02_cards():
            correct = c.get('correct')
            choices = c.get('choices', [])
            self.assertIsInstance(correct, int, f"{c['id']} correct is not int")
            self.assertTrue(1 <= correct <= len(choices), f"{c['id']} correct ({correct}) out of range [1, {len(choices)}]")

    def test_f6_04_back_html_structure_intact(self):
        """F6-04: back HTML retains mcq-result, mcq-answer-badge, and mcq-explanation without images."""
        for c in get_chapter02_cards():
            back = c.get('back', '')
            self.assertIn('mcq-result', back, f"{c['id']} back missing mcq-result")
            self.assertIn('mcq-answer-badge', back, f"{c['id']} back missing mcq-answer-badge")
            self.assertIn('mcq-explanation', back, f"{c['id']} back missing mcq-explanation")
            self.assertNotIn('image-frame', back, f"{c['id']} back contains image-frame")

    def test_f6_05_automated_validator_function_passes(self):
        """F6-05: Programmatic invocation of verify_restored_cards validator."""
        errors = verify_restored_cards(CARDS_DATA_PATH, start_id="mgmt_0277", end_id="mgmt_0507", expected_count=231)
        self.assertEqual(errors, [], f"verify_restored_cards reported errors: {errors}")

    def test_f6_06_pdf_page_map_json_integrity(self):
        """F6-06: pdf-page-map.json contains all 231 keys with valid integer pages."""
        with open(PAGE_MAP_PATH, 'r', encoding='utf-8') as f:
            pmap = json.load(f)
        for i in range(277, 508):
            qid = f"{i:04d}"
            self.assertIn(qid, pmap, f"pdf-page-map.json missing qid {qid}")
            entry = pmap[qid]
            self.assertGreater(entry.get('prob_page', 0), 0, f"{qid} prob_page invalid")
            self.assertGreater(entry.get('ans_page', 0), 0, f"{qid} ans_page invalid")


if __name__ == "__main__":
    unittest.main()
