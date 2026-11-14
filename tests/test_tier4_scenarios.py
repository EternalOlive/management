# -*- coding: utf-8 -*-
"""
tests/test_tier4_scenarios.py
Tier 4: Real-World Workload Scenarios Test Suite (6 scenarios)
Executes exhaustive end-to-end acceptance scenarios covering all 231 cards in Chapter 02.
Derived verbatim from Explorer 2 specification for Management Cards Chapter 02.
"""

from __future__ import annotations
import unittest
import json
import re

try:
    from tests.test_utils import (
        load_cards_data,
        load_page_map,
        get_chapter02_cards,
        has_emoji,
        has_leading_index_or_circle,
    )
except ImportError:
    from test_utils import (
        load_cards_data,
        load_page_map,
        get_chapter02_cards,
        has_emoji,
        has_leading_index_or_circle,
    )


class TestTier4Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_cards_data()
        cls.page_map = load_page_map()
        cls.cards = get_chapter02_cards(cls.data)
        cls.cards_by_id = {c['id']: c for c in cls.cards}

    def test_tier4_scenario_1_complete_json_parse_and_schema_validation(self):
        """
        Scenario 1: Complete JSON parse and structural schema validation across all 231 cards.
        Verifies contiguous range mgmt_0277~mgmt_0507 and strict adherence to data contract.
        """
        # Exactly 231 cards
        self.assertEqual(len(self.cards), 231, f"Expected 231 cards in Chapter 02, got {len(self.cards)}")

        # Contiguous ID check
        expected_ids = [f"mgmt_{i:04d}" for i in range(277, 508)]
        actual_ids = [c['id'] for c in self.cards]
        self.assertEqual(actual_ids, expected_ids, "Chapter 02 card IDs are not contiguous")

        required_keys = [
            'id', 'qid', 'subj', 'typ', 'correct', 'front', 'back',
            'stemText', 'choices', 'note', 'probPage', 'ansPage',
            'probPdf', 'ansPdf'
        ]

        for c in self.cards:
            cid = c['id']
            for k in required_keys:
                self.assertIn(k, c, f"{cid} missing required schema field '{k}'")

            # Value validations
            self.assertEqual(c['subj'], '1.02 조직행동: 개인')
            self.assertIn(c['typ'], ['객관식', '박스선택형'])
            self.assertIn(c['correct'], [1, 2, 3, 4, 5])
            self.assertIn(len(c['choices']), [4, 5])
            self.assertGreater(len(c['front']), 50)
            self.assertGreater(len(c['back']), 50)
            self.assertGreater(len(c['stemText']), 5)
            self.assertEqual(c['probPdf'], 'prob_02.pdf')
            self.assertEqual(c['ansPdf'], 'ans_02.pdf')

    def test_tier4_scenario_2_exhaustive_image_frame_and_img_elimination(self):
        """
        Scenario 2: Exhaustive scan verifying exactly 0 image-frames and 0 img tags across all 231 cards.
        """
        frame_pattern = re.compile(r'<div[^>]*class=["\'][^"\']*image-frame[^"\']*["\']')
        img_pattern = re.compile(r'<img\b')
        num_opt_pattern = re.compile(r'class=["\'][^"\']*number-option[^"\']*["\']')

        violations_frame = []
        violations_img = []
        violations_num_opt = []
        violations_ext = []

        for c in self.cards:
            cid = c['id']
            front = c.get('front', '')

            if 'image-frame' in front or frame_pattern.search(front):
                violations_frame.append(cid)
            if '<img' in front or img_pattern.search(front):
                violations_img.append(cid)
            if 'number-option' in front or num_opt_pattern.search(front):
                violations_num_opt.append(cid)
            if any(ext in front for ext in ['.webp', '.png', '.jpg']):
                violations_ext.append(cid)

        self.assertEqual(violations_frame, [], f"image-frame found in {len(violations_frame)} cards: {violations_frame[:5]}")
        self.assertEqual(violations_img, [], f"<img> found in {len(violations_img)} cards: {violations_img[:5]}")
        self.assertEqual(violations_num_opt, [], f"number-option found in {len(violations_num_opt)} cards: {violations_num_opt[:5]}")
        self.assertEqual(violations_ext, [], f"Image file extensions found in {len(violations_ext)} cards: {violations_ext[:5]}")

    def test_tier4_scenario_3_exhaustive_button_markup_and_cleanness(self):
        """
        Scenario 3: Exhaustive scan verifying 100% of options are clean text-option buttons
        with NO leading circled numbers, NO numeric prefixes, and NO emojis.
        """
        btn_re = re.compile(r'<button\s+([^>]*)>(.*?)</button>', re.DOTALL)
        choice_text_re = re.compile(r'<span\s+class=["\']mcq-choice-text["\']>(.*?)</span>', re.DOTALL)

        total_buttons = 0
        for c in self.cards:
            cid = c['id']
            btns = btn_re.findall(c.get('front', ''))
            self.assertIn(len(btns), [4, 5], f"{cid} has invalid button count {len(btns)}")
            total_buttons += len(btns)

            for idx, (attr_str, body) in enumerate(btns, start=1):
                self.assertIn('class="mcq-option text-option"', attr_str, f"{cid} button {idx} not text-option")
                self.assertIn(f'data-original="{idx}"', attr_str, f"{cid} button {idx} missing data-original")

                txt_match = choice_text_re.search(body)
                self.assertIsNotNone(txt_match, f"{cid} button {idx} missing mcq-choice-text")
                choice_text = txt_match.group(1).strip()

                # Explicit non-empty assertion
                self.assertGreater(len(choice_text), 0, f"{cid} button {idx} choice text is empty")

                # Prohibited prefix and index patterns (catches (1), ❶, ㉠, ①~⑳, N번:, N.)
                self.assertFalse(
                    has_leading_index_or_circle(choice_text),
                    f"{cid} button {idx} has leading circled number or prefix: '{choice_text[:20]}'"
                )

                # Full-spectrum emoji check (BMP + Astral)
                self.assertFalse(
                    has_emoji(choice_text),
                    f"{cid} button {idx} contains emoji: '{choice_text[:20]}'"
                )

                self.assertNotIn('mcq-ox-btn', body, f"{cid} button {idx} contains leaked runtime ox button")
                self.assertNotIn('mcq-elim-btn', body, f"{cid} button {idx} contains leaked runtime elim button")

        self.assertGreaterEqual(total_buttons, 231 * 4, f"Total button count {total_buttons} is lower than minimum")

    def test_tier4_scenario_4_exhaustive_boxed_statement_audit(self):
        """
        Scenario 4: Exhaustive audit of all 20 boxed statement cards verifying proper
        statement box container, badge text, and option references.
        """
        boxed_ids = [
            'mgmt_0313', 'mgmt_0323', 'mgmt_0325', 'mgmt_0342', 'mgmt_0367',
            'mgmt_0372', 'mgmt_0374', 'mgmt_0378', 'mgmt_0380', 'mgmt_0388',
            'mgmt_0405', 'mgmt_0428', 'mgmt_0429', 'mgmt_0444', 'mgmt_0450',
            'mgmt_0460', 'mgmt_0461', 'mgmt_0480', 'mgmt_0490', 'mgmt_0507'
        ]

        item_re = re.compile(
            r'<div\s+class=["\']mcq-statement-item["\'][^>]*data-stmt=["\']([^"\']+)["\'][^>]*>'
            r'(.*?'
            r'<div\s+class=["\']mcq-stmt-text["\']>.*?</div>'
            r'.*?)'
            r'</div>\s*(?=<div\s+class=["\']mcq-statement-item|</div>)',
            re.DOTALL
        )
        badge_re = re.compile(r'<span\s+class=["\']mcq-stmt-badge["\']>(.*?)</span>', re.DOTALL)

        # 1. Audit the 20 boxed cards
        for bid in boxed_ids:
            card = self.cards_by_id[bid]
            self.assertEqual(card.get('typ'), '박스선택형', f"{bid} must be 박스선택형")
            self.assertIn('statement-box', card.get('front', ''), f"{bid} missing statement-box")
            self.assertIn('mcq-statement-box', card.get('front', ''), f"{bid} missing mcq-statement-box")

            items = item_re.findall(card.get('front', ''))
            self.assertGreaterEqual(len(items), 2, f"{bid} must have >=2 statement items")

            for data_stmt, body in items:
                b = badge_re.search(body)
                self.assertIsNotNone(b, f"{bid} missing badge in statement item")
                self.assertEqual(b.group(1).strip(), data_stmt, f"{bid} badge text != data-stmt")

        # 2. Audit remaining 211 non-boxed cards
        non_boxed = [c for c in self.cards if c['id'] not in boxed_ids]
        self.assertEqual(len(non_boxed), 211)
        for c in non_boxed:
            cid = c['id']
            self.assertEqual(c.get('typ'), '객관식', f"{cid} should be 객관식")
            self.assertNotIn('statement-box', c.get('front', ''), f"{cid} should not contain statement-box")

    def test_tier4_scenario_5_master_reference_and_outlier_validation(self):
        """
        Scenario 5: Master reference & outlier validation:
        - mgmt_0374 restored text from master PDF page 106
        - mgmt_0501 answer page corrected to 56 (PDF page 31)
        - mgmt_0454 Kelley attribution theory matrix layout
        - mgmt_0278 duplicate options eliminated
        """
        # 1. mgmt_0374
        c374 = self.cards_by_id['mgmt_0374']
        self.assertNotIn('image-frame', c374.get('front', ''))
        self.assertNotIn('<img', c374.get('front', ''))
        self.assertEqual(c374.get('typ'), '박스선택형')
        self.assertIn('허츠버그', c374.get('stemText', ''))
        self.assertIn('동기요인', c374.get('stemText', ''))
        self.assertEqual(c374.get('correct'), 4)
        self.assertEqual(len(c374.get('boxStatements', [])), 5)

        # 2. mgmt_0501
        c501 = self.cards_by_id['mgmt_0501']
        self.assertEqual(c501.get('ansPage'), 56, "mgmt_0501 ansPage must be 56")
        page_entry_501 = self.page_map.get('0501', {})
        self.assertEqual(page_entry_501.get('ans_page'), 56, "pdf-page-map.json '0501' ans_page must be 56")
        self.assertEqual(page_entry_501.get('ans_pdf_page'), 31, "pdf-page-map.json '0501' ans_pdf_page must be 31")

        # 3. mgmt_0454
        c454 = self.cards_by_id['mgmt_0454']
        self.assertNotIn('image-frame', c454.get('front', ''))
        self.assertEqual(c454.get('correct'), 3)
        choices_454 = c454.get('choices', [])
        self.assertEqual(len(choices_454), 5)
        self.assertIn('높음 높음 높음', choices_454[0])
        self.assertIn('낮음 낮음 높음', choices_454[2])

        # 4. mgmt_0278
        c278 = self.cards_by_id['mgmt_0278']
        self.assertNotIn('image-frame', c278.get('front', ''))
        self.assertNotIn('<img', c278.get('front', ''))
        btn_re = re.compile(r'<button\s+[^>]*class=["\']mcq-option\s+text-option["\']', re.DOTALL)
        self.assertEqual(len(btn_re.findall(c278.get('front', ''))), 5)

    def test_tier4_scenario_6_full_dataset_back_and_answer_integrity(self):
        """
        Scenario 6 (Bonus Workload): Full dataset back HTML, result container,
        and answer key integrity scan across all 231 cards.
        """
        res_re = re.compile(r'<div\s+class=["\']mcq-result["\'][^>]*data-qid=["\'](\d{4})["\'][^>]*data-correct=["\'](\d)["\']', re.DOTALL)
        badge_re = re.compile(r'<div\s+class=["\']mcq-answer-badge["\']>', re.DOTALL)
        exp_re = re.compile(r'<div\s+class=["\']mcq-explanation["\']>', re.DOTALL)

        for c in self.cards:
            cid = c['id']
            back = c.get('back', '')

            # Back must not contain images
            self.assertNotIn('<img', back, f"{cid} back contains <img> tag")
            self.assertNotIn('image-frame', back, f"{cid} back contains image-frame")

            # Structural containers
            m = res_re.search(back)
            self.assertIsNotNone(m, f"{cid} back missing valid mcq-result container")
            self.assertEqual(m.group(1), c['qid'], f"{cid} back data-qid != card.qid")
            self.assertEqual(int(m.group(2)), c['correct'], f"{cid} back data-correct != card.correct")

            self.assertIsNotNone(badge_re.search(back), f"{cid} back missing mcq-answer-badge")
            self.assertIsNotNone(exp_re.search(back), f"{cid} back missing mcq-explanation")

            # Note synchronization
            note = c.get('note', '')
            self.assertIn(f"정답: {c['correct']}번", note, f"{cid} note does not match correct answer")


if __name__ == "__main__":
    unittest.main()
