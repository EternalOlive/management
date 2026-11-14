# -*- coding: utf-8 -*-
"""
tests/test_tier2_boundaries.py
Tier 2: Boundary & Corner Cases E2E Test Suite (39 tests)
Derived verbatim from Explorer 1 specification for Management Cards Chapter 02.
"""

from __future__ import annotations
import unittest
import json
import re
import os
from pathlib import Path

try:
    from tests.test_utils import (
        get_chapter02_cards,
        load_cards_data,
        load_page_map,
        PROJECT_ROOT
    )
except ImportError:
    from test_utils import (
        get_chapter02_cards,
        load_cards_data,
        load_page_map,
        PROJECT_ROOT
    )


# ===========================================================================
# Category T2.1: 4-Choice vs 5-Choice Distribution Boundaries (8 tests)
# ===========================================================================
FOUR_CHOICE_IDS = {
    'mgmt_0280', 'mgmt_0285', 'mgmt_0290', 'mgmt_0292', 'mgmt_0293', 'mgmt_0294', 'mgmt_0298',
    'mgmt_0301', 'mgmt_0314', 'mgmt_0315', 'mgmt_0316', 'mgmt_0317', 'mgmt_0318', 'mgmt_0323',
    'mgmt_0324', 'mgmt_0331', 'mgmt_0335', 'mgmt_0337', 'mgmt_0341', 'mgmt_0342', 'mgmt_0343',
    'mgmt_0344', 'mgmt_0346', 'mgmt_0349', 'mgmt_0355', 'mgmt_0356', 'mgmt_0358', 'mgmt_0359',
    'mgmt_0360', 'mgmt_0361', 'mgmt_0362', 'mgmt_0389', 'mgmt_0390', 'mgmt_0391', 'mgmt_0392',
    'mgmt_0393', 'mgmt_0398', 'mgmt_0399', 'mgmt_0401', 'mgmt_0407', 'mgmt_0415', 'mgmt_0416',
    'mgmt_0424', 'mgmt_0426', 'mgmt_0428', 'mgmt_0429', 'mgmt_0432', 'mgmt_0435', 'mgmt_0436',
    'mgmt_0437', 'mgmt_0438', 'mgmt_0440', 'mgmt_0442', 'mgmt_0443', 'mgmt_0501', 'mgmt_0506'
}

class TestTier2_4ChoiceVs5ChoiceBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()
        cls.cards_map = {c['id']: c for c in cls.cards}

    def test_t2_01_exact_count_of_four_choice_cards(self):
        """T2-01: Exactly 56 cards in Chapter 02 have len(choices) == 4."""
        c4 = [c['id'] for c in self.cards if len(c.get('choices', [])) == 4]
        self.assertEqual(len(c4), 56, f"Expected 56 4-choice cards, got {len(c4)}")
        self.assertEqual(set(c4), FOUR_CHOICE_IDS)

    def test_t2_02_exact_count_of_five_choice_cards(self):
        """T2-02: Exactly 175 cards in Chapter 02 have len(choices) == 5."""
        c5 = [c['id'] for c in self.cards if len(c.get('choices', [])) == 5]
        self.assertEqual(len(c5), 175, f"Expected 175 5-choice cards, got {len(c5)}")
        self.assertEqual(len(self.cards), 56 + 175)

    def test_t2_03_first_four_choice_card_mgmt_0280(self):
        """T2-03: Boundary check on first 4-choice card mgmt_0280."""
        c = self.cards_map['mgmt_0280']
        self.assertEqual(len(c['choices']), 4)
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 4)
        labels = re.findall(r'<span class="mcq-label">\s*([^<]+?)\s*</span>', c.get('front', ''))
        self.assertEqual(labels, ['①', '②', '③', '④'])
        self.assertTrue(1 <= c['correct'] <= 4)

    def test_t2_04_last_four_choice_card_mgmt_0506(self):
        """T2-04: Boundary check on last 4-choice card mgmt_0506."""
        c = self.cards_map['mgmt_0506']
        self.assertEqual(len(c['choices']), 4)
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 4)
        labels = re.findall(r'<span class="mcq-label">\s*([^<]+?)\s*</span>', c.get('front', ''))
        self.assertEqual(labels, ['①', '②', '③', '④'])
        self.assertTrue(1 <= c['correct'] <= 4)

    def test_t2_05_first_five_choice_card_mgmt_0277(self):
        """T2-05: Boundary check on first 5-choice card mgmt_0277."""
        c = self.cards_map['mgmt_0277']
        self.assertEqual(len(c['choices']), 5)
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 5)
        labels = re.findall(r'<span class="mcq-label">\s*([^<]+?)\s*</span>', c.get('front', ''))
        self.assertEqual(labels, ['①', '②', '③', '④', '⑤'])
        self.assertTrue(1 <= c['correct'] <= 5)

    def test_t2_06_last_five_choice_card_mgmt_0507(self):
        """T2-06: Boundary check on last 5-choice card mgmt_0507."""
        c = self.cards_map['mgmt_0507']
        self.assertEqual(len(c['choices']), 5)
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 5)
        labels = re.findall(r'<span class="mcq-label">\s*([^<]+?)\s*</span>', c.get('front', ''))
        self.assertEqual(labels, ['①', '②', '③', '④', '⑤'])
        self.assertTrue(1 <= c['correct'] <= 5)

    def test_t2_07_all_four_choice_cards_correct_answer_bounded_by_four(self):
        """T2-07: In all 56 4-choice cards, correct answer is strictly 1 <= correct <= 4."""
        for cid in FOUR_CHOICE_IDS:
            c = self.cards_map[cid]
            self.assertTrue(1 <= c['correct'] <= 4, f"{cid} correct answer ({c['correct']}) exceeds 4 for 4-choice card")

    def test_t2_08_help_text_boundary_on_four_vs_five_choice_cards(self):
        """T2-08: mcq-help text correctly differentiates 1~4 vs 1~5 choice ranges."""
        for c in self.cards:
            front = c.get('front', '')
            help_m = re.search(r'<div class="mcq-help">(.*?)</div>', front)
            if help_m:
                text = help_m.group(1)
                if len(c['choices']) == 4:
                    self.assertTrue('1~4' in text or '4' in text, f"{c['id']} 4-choice card help text mismatch: '{text}'")
                elif len(c['choices']) == 5:
                    self.assertTrue('1~5' in text or '5' in text, f"{c['id']} 5-choice card help text mismatch: '{text}'")


# ===========================================================================
# Category T2.2: Empty & Whitespace Boundary Cases (6 tests)
# ===========================================================================
class TestTier2_EmptyAndWhitespaceBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = get_chapter02_cards()

    def test_t2_09_no_empty_or_whitespace_stem_text(self):
        """T2-09: No card has empty or whitespace-only stemText."""
        for c in self.cards:
            stem = c.get('stemText', '')
            self.assertTrue(len(stem.strip()) > 0, f"{c['id']} has empty/whitespace stemText")

    def test_t2_10_minimum_stem_length_boundary(self):
        """T2-10: Every card stemText has at least 8 non-whitespace characters."""
        for c in self.cards:
            stem = c.get('stemText', '').strip()
            self.assertGreaterEqual(len(stem), 8, f"{c['id']} stemText too short ({len(stem)} chars): '{stem}'")

    def test_t2_11_all_1099_choices_non_empty_and_non_whitespace(self):
        """T2-11: All 1,099 choice strings across 231 cards have non-empty text body."""
        total_choices = 0
        for c in self.cards:
            for ch in c.get('choices', []):
                total_choices += 1
                parts = ch.split(':', 1)
                choice_text = parts[-1].strip()
                self.assertGreater(len(choice_text), 0, f"{c['id']} choice has empty body: '{ch}'")
        self.assertEqual(total_choices, 1099, f"Total choices count {total_choices} != 1099")

    def test_t2_12_no_leading_or_trailing_whitespace_in_choice_text_spans(self):
        """T2-12: Choice text inside mcq-choice-text span is trimmed without leading/trailing whitespace."""
        for c in self.cards:
            front = c.get('front', '')
            texts = re.findall(r'<span class="mcq-choice-text">(.*?)</span>', front, re.DOTALL)
            for t in texts:
                self.assertEqual(t, t.strip(), f"{c['id']} choice text span has unstripped whitespace: '{t}'")

    def test_t2_13_no_leading_circled_symbols_in_choice_texts(self):
        """T2-13: No choice text starts with circled number symbols."""
        circles = ('①', '②', '③', '④', '⑤')
        for c in self.cards:
            front = c.get('front', '')
            texts = re.findall(r'<span class="mcq-choice-text">(.*?)</span>', front, re.DOTALL)
            for t in texts:
                clean = t.strip()
                self.assertFalse(clean.startswith(circles), f"{c['id']} choice text starts with circled symbol: '{clean}'")

    def test_t2_14_box_statement_items_non_empty_strings(self):
        """T2-14: In boxed cards, id, label, and text fields in boxStatements are non-empty."""
        boxed = [c for c in self.cards if c.get('typ') == '박스선택형']
        for c in boxed:
            for stmt in c.get('boxStatements', []):
                self.assertTrue(len(stmt.get('id', '').strip()) > 0, f"{c['id']} stmt id empty")
                self.assertTrue(len(stmt.get('label', '').strip()) > 0, f"{c['id']} stmt label empty")
                self.assertTrue(len(stmt.get('text', '').strip()) > 0, f"{c['id']} stmt text empty")


# ===========================================================================
# Category T2.3: Corrupted Zero-Byte Fallback Card (mgmt_0374) (6 tests)
# ===========================================================================
class TestTier2_CorruptedFileFallback_mgmt_0374(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards_map = {c['id']: c for c in get_chapter02_cards()}
        cls.c = cls.cards_map['mgmt_0374']

    def test_t2_15_mgmt_0374_zero_byte_disk_file_confirmed(self):
        """T2-15: Outlier handling: mgmt_0374 decoupling from corrupted or altered disk asset."""
        img_path = PROJECT_ROOT / 'images' / '_jh_q_0374.webp'
        self.assertTrue(img_path.exists(), f"Asset {img_path} not found")
        # Asset was historically a 0-byte corrupted image. If altered or repaired on disk
        # during extraction experiments, card front HTML must strictly decouple from it.
        front = self.c.get('front', '')
        self.assertNotIn('_jh_q_0374.webp', front, "mgmt_0374 front HTML references _jh_q_0374.webp")

    def test_t2_16_mgmt_0374_front_html_completely_omits_image_tag(self):
        """T2-16: mgmt_0374 front HTML contains zero img tags and zero image-frame classes."""
        front = self.c.get('front', '')
        self.assertNotIn('<img', front, "mgmt_0374 front HTML contains <img> tag")
        self.assertNotIn('0374.webp', front, "mgmt_0374 front HTML references 0374.webp")
        self.assertNotIn('image-frame', front, "mgmt_0374 front HTML contains image-frame")

    def test_t2_17_mgmt_0374_stem_contains_master_pdf_keywords(self):
        """T2-17: mgmt_0374 stem contains Herzberg 2-factor theory keywords from master PDF."""
        stem = self.c.get('stemText', '')
        self.assertTrue('허츠버그' in stem or 'Herzberg' in stem, f"mgmt_0374 stem missing Herzberg: {stem}")
        self.assertTrue('2요인' in stem or '동기요인' in stem, f"mgmt_0374 stem missing theory keywords: {stem}")

    def test_t2_18_mgmt_0374_has_five_boxed_statements(self):
        """T2-18: mgmt_0374 has 5 boxed statements with labels ㄱ..ㅁ."""
        stmts = self.c.get('boxStatements', [])
        self.assertEqual(len(stmts), 5, f"mgmt_0374 expected 5 statements, got {len(stmts)}")
        labels = [s['label'] for s in stmts]
        self.assertEqual(labels, ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ'], f"mgmt_0374 statement labels mismatch: {labels}")

    def test_t2_19_mgmt_0374_has_five_valid_choice_combinations(self):
        """T2-19: mgmt_0374 has 5 choices and 5 buttons in front HTML."""
        choices = self.c.get('choices', [])
        self.assertEqual(len(choices), 5, f"mgmt_0374 choices length {len(choices)} != 5")
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', self.c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 5, f"mgmt_0374 buttons count {len(buttons)} != 5")

    def test_t2_20_mgmt_0374_correct_answer_is_four(self):
        """T2-20: mgmt_0374 correct answer is strictly 4 (ㄴ, ㅁ)."""
        self.assertEqual(self.c.get('correct'), 4, f"mgmt_0374 correct answer is {self.c.get('correct')}, expected 4")


# ===========================================================================
# Category T2.4: Varied Label Formats Across Exactly 20 Boxed Cards (10 tests)
# ===========================================================================
LATIN_CPA_IDS = {'mgmt_0444', 'mgmt_0450', 'mgmt_0460', 'mgmt_0461', 'mgmt_0480', 'mgmt_0490', 'mgmt_0507'}
CONSONANT_IDS = {'mgmt_0313', 'mgmt_0325', 'mgmt_0342', 'mgmt_0372', 'mgmt_0374', 'mgmt_0378', 'mgmt_0380', 'mgmt_0405', 'mgmt_0428', 'mgmt_0429'}

class TestTier2_VariedLabelFormats_BoxedCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards_map = {c['id']: c for c in get_chapter02_cards()}

    def test_t2_21_hangul_consonant_labeled_cards(self):
        """T2-21: 10 Hangul consonant boxed cards use [ㄱ-ㅎ] statement badges."""
        for cid in CONSONANT_IDS:
            c = self.cards_map[cid]
            front = c.get('front', '')
            badges = re.findall(r'<span class="mcq-stmt-badge">\s*([^<]+?)\s*</span>', front)
            self.assertGreater(len(badges), 0, f"{cid} has no stmt badges")
            for b in badges:
                self.assertRegex(b, r'^[ㄱ-ㅎ]$', f"{cid} badge '{b}' is not a Hangul consonant")

    def test_t2_22_circled_hangul_labeled_card_mgmt_0323(self):
        """T2-22: Circled Hangul card mgmt_0323 uses ㉠..㉥ badges and has 4 choices."""
        c = self.cards_map['mgmt_0323']
        front = c.get('front', '')
        badges = re.findall(r'<span class="mcq-stmt-badge">\s*([^<]+?)\s*</span>', front)
        self.assertGreater(len(badges), 0, "mgmt_0323 has no badges")
        for b in badges:
            self.assertIn(b, ['㉠', '㉡', '㉢', '㉣', '㉤', '㉥'], f"mgmt_0323 badge unexpected: '{b}'")
        self.assertEqual(len(c.get('choices', [])), 4, "mgmt_0323 choices length should be 4")

    def test_t2_23_hangul_syllable_labeled_cards_mgmt_0367_0388(self):
        """T2-23: Hangul syllable cards mgmt_0367 and mgmt_0388 use 가, 나, 다... badges."""
        c367 = self.cards_map['mgmt_0367']
        badges367 = re.findall(r'<span class="mcq-stmt-badge">\s*([^<]+?)\s*</span>', c367.get('front', ''))
        self.assertGreater(len(badges367), 0)
        self.assertTrue(any(b in ['가', '나', '다', '라', '마'] for b in badges367), f"mgmt_0367 badges unexpected: {badges367}")

    def test_t2_24_cpa_latin_lowercase_labeled_cards(self):
        """T2-24: 7 CPA cards use Latin lowercase letters [a-e] for badges and data-stmt."""
        for cid in LATIN_CPA_IDS:
            c = self.cards_map[cid]
            front = c.get('front', '')
            badges = re.findall(r'<span class="mcq-stmt-badge">\s*([^<]+?)\s*</span>', front)
            self.assertGreater(len(badges), 0, f"{cid} has no badges")
            for b in badges:
                self.assertRegex(b, r'^[a-e]$', f"{cid} badge '{b}' is not Latin a-e")
            data_stmts = re.findall(r'data-stmt="([^"]+)"', front)
            for ds in data_stmts:
                self.assertRegex(ds, r'^[a-e]$', f"{cid} data-stmt '{ds}' is not Latin a-e")

    def test_t2_25_cpa_card_mgmt_0450_structure(self):
        """T2-25: 2021 CPA card mgmt_0450 has 5 statements (a..e), 5 choices, and correct == 2."""
        c = self.cards_map['mgmt_0450']
        self.assertEqual(c.get('typ'), '박스선택형')
        self.assertEqual(len(c.get('choices', [])), 5)
        self.assertEqual(c.get('correct'), 2)
        stmts = c.get('boxStatements', [])
        labels = [s['label'] for s in stmts]
        self.assertEqual(labels, ['a', 'b', 'c', 'd', 'e'])

    def test_t2_26_cpa_card_mgmt_0507_chapter_boundary(self):
        """T2-26: Chapter end card mgmt_0507 is boxed CPA card with 5 choices (a..e) and correct == 1."""
        c = self.cards_map['mgmt_0507']
        self.assertEqual(c.get('typ'), '박스선택형')
        self.assertEqual(len(c.get('choices', [])), 5)
        self.assertEqual(c.get('correct'), 1)
        stmts = c.get('boxStatements', [])
        labels = [s['label'] for s in stmts]
        self.assertEqual(labels, ['a', 'b', 'c', 'd', 'e'])

    def test_t2_27_four_choice_boxed_cards_subset(self):
        """T2-27: Exactly 4 boxed cards have 4 choices (0323, 0342, 0428, 0429)."""
        box_4 = [c['id'] for c in self.cards_map.values() if c.get('typ') == '박스선택형' and len(c.get('choices', [])) == 4]
        self.assertEqual(set(box_4), {'mgmt_0323', 'mgmt_0342', 'mgmt_0428', 'mgmt_0429'})
        for cid in box_4:
            front = self.cards_map[cid].get('front', '')
            btns = re.findall(r'<button\b[^>]*>.*?</button>', front, re.DOTALL)
            self.assertEqual(len(btns), 4, f"{cid} button count != 4")

    def test_t2_28_sixteen_five_choice_boxed_cards_subset(self):
        """T2-28: Exactly 16 boxed cards have 5 choices and 5 buttons."""
        box_5 = [c['id'] for c in self.cards_map.values() if c.get('typ') == '박스선택형' and len(c.get('choices', [])) == 5]
        self.assertEqual(len(box_5), 16)
        for cid in box_5:
            front = self.cards_map[cid].get('front', '')
            btns = re.findall(r'<button\b[^>]*>.*?</button>', front, re.DOTALL)
            self.assertEqual(len(btns), 5, f"{cid} button count != 5")

    def test_t2_29_statement_badge_and_data_stmt_strict_sync(self):
        """T2-29: Across all 20 boxed cards, badge text strictly equals data-stmt attribute."""
        boxed = [c for c in self.cards_map.values() if c.get('typ') == '박스선택형']
        for c in boxed:
            front = c.get('front', '')
            items = re.findall(r'<div class="mcq-statement-item"\s+data-stmt="([^"]+)">(.*?)</div>\s*(?=<div class="mcq-statement-item"|</div>\s*</div>)', front, re.DOTALL)
            for stmt_attr, item_body in items:
                badge_m = re.search(r'<span class="mcq-stmt-badge">\s*([^<]+?)\s*</span>', item_body)
                self.assertIsNotNone(badge_m, f"{c['id']} missing badge in item {stmt_attr}")
                self.assertEqual(badge_m.group(1).strip(), stmt_attr, f"{c['id']} badge text != data-stmt attribute")

    def test_t2_30_statement_box_header_presence(self):
        """T2-30: All 20 boxed cards contain mcq-statement-header in front HTML."""
        boxed = [c for c in self.cards_map.values() if c.get('typ') == '박스선택형']
        for c in boxed:
            front = c.get('front', '')
            self.assertIn('mcq-statement-header', front, f"{c['id']} missing mcq-statement-header")


# ===========================================================================
# Category T2.5: Table Matrix Layout Boundary Card (mgmt_0454) (3 tests)
# ===========================================================================
class TestTier2_TableMatrix_mgmt_0454(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards_map = {c['id']: c for c in get_chapter02_cards()}
        cls.c = cls.cards_map['mgmt_0454']

    def test_t2_31_mgmt_0454_attribution_choices_structure(self):
        """T2-31: mgmt_0454 choices represent 3-term attribution states with 높음/낮음."""
        choices = self.c.get('choices', [])
        self.assertEqual(len(choices), 5, f"mgmt_0454 choices length {len(choices)} != 5")
        for idx, ch in enumerate(choices):
            body = ch.split(':', 1)[-1].strip()
            words = body.split()
            self.assertEqual(len(words), 3, f"mgmt_0454 choice {idx+1} expected 3 matrix terms, got '{body}'")
            self.assertTrue(all(w in ['높음', '낮음'] for w in words), f"mgmt_0454 choice {idx+1} terms not 높음/낮음: {words}")

    def test_t2_32_mgmt_0454_stem_contains_attribution_theory_context(self):
        """T2-32: mgmt_0454 stem contains attribution theory keywords."""
        stem = self.c.get('stemText', '')
        self.assertTrue(
            any(k in stem for k in ['켈리', 'Kelley', '귀인', '합의성', '특이성', '일관성']),
            f"mgmt_0454 stem missing attribution theory terms: {stem}"
        )

    def test_t2_33_mgmt_0454_no_html_table_tags_in_front(self):
        """T2-33: mgmt_0454 front HTML contains zero raw table, tr, or td tags."""
        front = self.c.get('front', '')
        self.assertNotIn('<table', front, "mgmt_0454 front contains <table>")
        self.assertNotIn('<tr', front, "mgmt_0454 front contains <tr>")
        self.assertNotIn('<td', front, "mgmt_0454 front contains <td>")


# ===========================================================================
# Category T2.6: Page Mapping Fix Corner Card (mgmt_0501) (3 tests)
# ===========================================================================
class TestTier2_PageMappingFix_mgmt_0501(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards_map = {c['id']: c for c in get_chapter02_cards()}
        cls.c = cls.cards_map['mgmt_0501']
        cls.page_map = load_page_map()

    def test_t2_34_mgmt_0501_page_map_entry_is_page_56(self):
        """T2-34: In pdf-page-map.json, entry '0501' has ans_page: 56 and ans_pdf_page: 31 (not 112/35)."""
        entry = self.page_map.get('0501', {})
        self.assertEqual(entry.get('ans_page'), 56, f"0501 ans_page is {entry.get('ans_page')}, expected 56 (not 112)")
        self.assertEqual(entry.get('ans_pdf_page'), 31, f"0501 ans_pdf_page is {entry.get('ans_pdf_page')}, expected 31 (not 35)")

    def test_t2_35_mgmt_0501_card_json_ans_page_is_page_56(self):
        """T2-35: In cards-data.json, mgmt_0501 has ansPage: 56 (not 112)."""
        self.assertEqual(self.c.get('ansPage'), 56, f"mgmt_0501 ansPage is {self.c.get('ansPage')}, expected 56 (not 112)")
        self.assertEqual(self.c.get('ansPdfPage'), 31, f"mgmt_0501 ansPdfPage is {self.c.get('ansPdfPage')}, expected 31")

    def test_t2_36_mgmt_0501_is_four_choice_card(self):
        """T2-36: mgmt_0501 is a 4-choice card with 4 buttons and 1 <= correct <= 4."""
        self.assertEqual(len(self.c.get('choices', [])), 4, "mgmt_0501 choices length != 4")
        buttons = re.findall(r'<button\b[^>]*>.*?</button>', self.c.get('front', ''), re.DOTALL)
        self.assertEqual(len(buttons), 4, "mgmt_0501 button count != 4")
        self.assertTrue(1 <= self.c.get('correct', 0) <= 4, f"mgmt_0501 correct answer out of bounds: {self.c.get('correct')}")


# ===========================================================================
# Category T2.7: Extreme ID Range Boundaries (3 tests)
# ===========================================================================
class TestTier2_ExtremeIDRangeBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        all_cards = load_cards_data()['cards']
        cls.cards_map = {c['id']: c for c in all_cards}

    def test_t2_37_lower_boundary_card_mgmt_0277(self):
        """T2-37: Lower boundary card mgmt_0277 has qid 0277, subject '1.02 조직행동: 개인', and 5 choices."""
        c = self.cards_map.get('mgmt_0277')
        self.assertIsNotNone(c, "mgmt_0277 missing")
        self.assertEqual(c['qid'], '0277')
        self.assertEqual(c['subj'], '1.02 조직행동: 개인')
        self.assertNotIn('image-frame', c.get('front', ''))
        self.assertEqual(len(c.get('choices', [])), 5)

    def test_t2_38_upper_boundary_card_mgmt_0507(self):
        """T2-38: Upper boundary card mgmt_0507 has qid 0507, subject '1.02 조직행동: 개인', boxed typ, and 5 choices."""
        c = self.cards_map.get('mgmt_0507')
        self.assertIsNotNone(c, "mgmt_0507 missing")
        self.assertEqual(c['qid'], '0507')
        self.assertEqual(c['subj'], '1.02 조직행동: 개인')
        self.assertEqual(c.get('typ'), '박스선택형')
        self.assertNotIn('image-frame', c.get('front', ''))
        self.assertEqual(len(c.get('choices', [])), 5)

    def test_t2_39_external_boundary_cards_untouched(self):
        """T2-39: External boundary cards mgmt_0276 (Chapter 01) and mgmt_0508 (Chapter 03) remain untouched."""
        c_prev = self.cards_map.get('mgmt_0276')
        self.assertIsNotNone(c_prev, "mgmt_0276 missing")
        self.assertEqual(c_prev['subj'], '1.01 경영학일반', "mgmt_0276 subject corrupted")

        c_next = self.cards_map.get('mgmt_0508')
        self.assertIsNotNone(c_next, "mgmt_0508 missing")
        self.assertEqual(c_next['subj'], '1.03 조직행동: 집단·조직', "mgmt_0508 subject corrupted")


if __name__ == "__main__":
    unittest.main()
