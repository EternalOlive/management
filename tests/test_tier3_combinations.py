# -*- coding: utf-8 -*-
"""
tests/test_tier3_combinations.py
Tier 3: Cross-Feature Combinations Test Suite (9 tests)
Covers pairwise combinatorial interactions between features F1 through F6.
Derived verbatim from Explorer 2 specification for Management Cards Chapter 02.
"""

from __future__ import annotations
import unittest
import re

try:
    from tests.test_utils import load_cards_data, get_chapter02_cards
except ImportError:
    from test_utils import load_cards_data, get_chapter02_cards


class TestTier3Combinations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_cards_data()
        cls.cards = get_chapter02_cards(cls.data)
        cls.cards_by_id = {c['id']: c for c in cls.cards}

        # Predefined sets
        cls.BOXED_4_CHOICE = ['mgmt_0323', 'mgmt_0342', 'mgmt_0428', 'mgmt_0429']
        cls.BOXED_5_CHOICE = [
            'mgmt_0313', 'mgmt_0325', 'mgmt_0367', 'mgmt_0372', 'mgmt_0374',
            'mgmt_0378', 'mgmt_0380', 'mgmt_0388', 'mgmt_0405', 'mgmt_0444',
            'mgmt_0450', 'mgmt_0460', 'mgmt_0461', 'mgmt_0480', 'mgmt_0490', 'mgmt_0507'
        ]
        cls.BOXED_ALL = cls.BOXED_4_CHOICE + cls.BOXED_5_CHOICE

    def test_tier3_boxed_statement_4choice_combination(self):
        """T3-1: F2 (Boxed Statement) × F1 (4-choice options) pairwise interaction."""
        btn_re = re.compile(r'<button\s+[^>]*class=["\']([^"\']+)["\'][^>]*>(.*?)</button>', re.DOTALL)
        label_re = re.compile(r'<span\s+class=["\']mcq-label["\']>(.*?)</span>', re.DOTALL)

        for cid in self.BOXED_4_CHOICE:
            card = self.cards_by_id[cid]
            self.assertEqual(card.get('typ'), '박스선택형', f"{cid} must be '박스선택형'")
            self.assertIn('statement-box', card.get('front', ''), f"{cid} missing statement-box")
            self.assertIn('mcq-statement-box', card.get('front', ''), f"{cid} missing mcq-statement-box")

            btns = btn_re.findall(card.get('front', ''))
            self.assertEqual(len(btns), 4, f"{cid} must have exactly 4 buttons, got {len(btns)}")
            self.assertEqual(len(card.get('choices', [])), 4, f"{cid} choices metadata must have 4 items")

            for idx, (cls_name, body) in enumerate(btns, start=1):
                self.assertIn('mcq-option', cls_name)
                self.assertIn('text-option', cls_name)
                self.assertIn(f'data-original="{idx}"', card.get('front', ''))

                lbl = label_re.search(body)
                self.assertIsNotNone(lbl, f"{cid} button {idx} missing label")
                self.assertEqual(lbl.group(1).strip(), ['①', '②', '③', '④'][idx - 1])

    def test_tier3_boxed_statement_5choice_combination(self):
        """T3-2: F2 (Boxed Statement) × F1 (5-choice options) pairwise interaction."""
        btn_re = re.compile(r'<button\s+[^>]*class=["\']([^"\']+)["\'][^>]*>(.*?)</button>', re.DOTALL)
        label_re = re.compile(r'<span\s+class=["\']mcq-label["\']>(.*?)</span>', re.DOTALL)

        for cid in self.BOXED_5_CHOICE:
            card = self.cards_by_id[cid]
            self.assertEqual(card.get('typ'), '박스선택형', f"{cid} must be '박스선택형'")
            self.assertIn('statement-box', card.get('front', ''), f"{cid} missing statement-box")
            self.assertIn('mcq-statement-box', card.get('front', ''), f"{cid} missing mcq-statement-box")

            btns = btn_re.findall(card.get('front', ''))
            self.assertEqual(len(btns), 5, f"{cid} must have exactly 5 buttons, got {len(btns)}")
            self.assertEqual(len(card.get('choices', [])), 5, f"{cid} choices metadata must have 5 items")

            for idx, (cls_name, body) in enumerate(btns, start=1):
                self.assertIn('mcq-option', cls_name)
                self.assertIn('text-option', cls_name)
                self.assertIn(f'data-original="{idx}"', card.get('front', ''))

                lbl = label_re.search(body)
                self.assertIsNotNone(lbl, f"{cid} button {idx} missing label")
                self.assertEqual(lbl.group(1).strip(), ['①', '②', '③', '④', '⑤'][idx - 1])

    def test_tier3_statement_box_item_and_badge_interaction(self):
        """T3-3: F2 (Boxed Statement) × F3 (Design System) container hierarchy."""
        item_re = re.compile(
            r'<div\s+class=["\']mcq-statement-item["\'][^>]*data-stmt=["\']([^"\']+)["\'][^>]*>'
            r'(.*?'
            r'<div\s+class=["\']mcq-stmt-text["\']>.*?</div>'
            r'.*?)'
            r'</div>\s*(?=<div\s+class=["\']mcq-statement-item|</div>)',
            re.DOTALL
        )
        badge_re = re.compile(r'<span\s+class=["\']mcq-stmt-badge["\']>(.*?)</span>', re.DOTALL)
        text_re = re.compile(r'<div\s+class=["\']mcq-stmt-text["\']>(.*?)</div>', re.DOTALL)

        for cid in self.BOXED_ALL:
            card = self.cards_by_id[cid]
            front = card.get('front', '')

            # Check container
            self.assertRegex(front, r'<div\s+class=["\'](?:statement-box\s+mcq-statement-box|mcq-statement-box)["\']')

            # Check items
            items = item_re.findall(front)
            self.assertGreaterEqual(len(items), 2, f"{cid} should have at least 2 statement items")

            box_stmts = card.get('boxStatements', [])
            if box_stmts:
                self.assertEqual(len(items), len(box_stmts), f"{cid} DOM item count != boxStatements count")

            for data_stmt, body in items:
                badge = badge_re.search(body)
                self.assertIsNotNone(badge, f"{cid} missing badge for stmt {data_stmt}")
                self.assertEqual(badge.group(1).strip(), data_stmt, f"{cid} data-stmt != badge text")

                stmt_text = text_re.search(body)
                self.assertIsNotNone(stmt_text, f"{cid} missing stmt-text for stmt {data_stmt}")
                self.assertGreater(len(stmt_text.group(1).strip()), 0, f"{cid} stmt-text is empty")

    def test_tier3_button_structure_label_choice_text_interaction(self):
        """T3-4: F1 (Text Option) × F3 (Design System) button child hierarchy."""
        btn_re = re.compile(r'<button\s+([^>]*)>(.*?)</button>', re.DOTALL)
        label_re = re.compile(r'<span\s+class=["\']mcq-label["\']>(.*?)</span>', re.DOTALL)
        choice_text_re = re.compile(r'<span\s+class=["\']mcq-choice-text["\']>(.*?)</span>', re.DOTALL)

        for card in self.cards:
            cid = card['id']
            front = card.get('front', '')
            btns = btn_re.findall(front)
            self.assertIn(len(btns), [4, 5], f"{cid} must have 4 or 5 buttons")

            for idx, (attr_str, body) in enumerate(btns, start=1):
                self.assertIn('type="button"', attr_str)
                self.assertIn('class="mcq-option text-option"', attr_str)
                self.assertIn(f'data-original="{idx}"', attr_str)

                # Check label
                lbl_match = label_re.search(body)
                self.assertIsNotNone(lbl_match, f"{cid} button {idx} missing mcq-label")
                self.assertEqual(lbl_match.group(1).strip(), ['①', '②', '③', '④', '⑤'][idx - 1])

                # Check choice text
                txt_match = choice_text_re.search(body)
                self.assertIsNotNone(txt_match, f"{cid} button {idx} missing mcq-choice-text")
                choice_text = txt_match.group(1).strip()
                self.assertGreater(len(choice_text), 0, f"{cid} button {idx} choice text is empty")
                self.assertNotRegex(choice_text, r'^[①②③④⑤❶❷❸❹❺]', f"{cid} button {idx} has leading circled number")
                self.assertNotRegex(choice_text, r'^[1-5]\s*번\s*[:\.]', f"{cid} button {idx} has leading 1번: prefix")

    def test_tier3_markup_tokens_css_styling_interaction(self):
        """T3-5: F1/F2/F3 × Design System Tokens & Allowed Class Whitelist."""
        class_attr_re = re.compile(r'class=["\']([^"\']+)["\']')
        allowed_classes = {
            'mcq-card', 'question-number', 'mcq-header', 'question-header-row',
            'mcq-qnum', 'mcq-stem', 'stem-ocr-text', 'source-badge', 'statement-box',
            'mcq-statement-box', 'mcq-statement-header', 'mcq-statement-item',
            'mcq-stmt-badge', 'mcq-stmt-content', 'mcq-stmt-text', 'mcq-stmt-status',
            'mcq-stmt-hint', 'mcq-options', 'mcq-option', 'text-option',
            'mcq-label', 'mcq-choice-text', 'mcq-help', 'grid-2col', 'has-statements'
        }

        for card in self.cards:
            cid = card['id']
            front = card.get('front', '')

            # Must strictly not contain obsolete classes
            self.assertNotIn('image-frame', front, f"{cid} contains obsolete image-frame")
            self.assertNotIn('number-option', front, f"{cid} contains obsolete number-option")
            self.assertNotIn('img-zoom', front, f"{cid} contains obsolete img-zoom")
            self.assertNotIn('<img', front, f"{cid} contains raw img tag")

            # Check all classes in front against whitelist
            found_classes = class_attr_re.findall(front)
            for cls_group in found_classes:
                for cls_name in cls_group.split():
                    self.assertIn(cls_name, allowed_classes, f"{cid} contains unknown class '{cls_name}'")

    def test_tier3_stem_metadata_and_html_synchronization(self):
        """T3-6: F4 (Metadata) × F1 (Stem Text in HTML)."""
        stem_html_re = re.compile(r'<div\s+class=["\']stem-ocr-text["\']>(.*?)</div>', re.DOTALL)
        badge_html_re = re.compile(r'<span\s+class=["\']source-badge["\']>(.*?)</span>', re.DOTALL)

        for card in self.cards:
            cid = card['id']
            stem_text = card.get('stemText', '').strip()
            self.assertGreater(len(stem_text), 5, f"{cid} stemText missing or too short")

            stem_match = stem_html_re.search(card.get('front', ''))
            self.assertIsNotNone(stem_match, f"{cid} missing div.stem-ocr-text in front HTML")

            # Source tag check
            source_tag = card.get('sourceTag', '').strip()
            badge_match = badge_html_re.search(card.get('front', ''))
            if source_tag:
                self.assertIsNotNone(badge_match, f"{cid} has sourceTag '{source_tag}' but missing badge in HTML")
                self.assertIn(source_tag, badge_match.group(1))

    def test_tier3_boxed_metadata_and_html_synchronization(self):
        """T3-7: F2 (Boxed Statement) × F4 (Metadata) synchronization."""
        boxed_cards = [c for c in self.cards if c.get('typ') == '박스선택형']
        self.assertEqual(len(boxed_cards), 20, f"Expected exactly 20 boxed cards, found {len(boxed_cards)}")
        for card in self.cards:
            cid = card['id']
            if card.get('typ') == '박스선택형':
                self.assertIn('statement-box', card.get('front', ''), f"{cid} is 박스선택형 but missing statement-box")
                box_stmts = card.get('boxStatements')
                self.assertIsInstance(box_stmts, list, f"{cid} boxStatements must be a list")
                self.assertGreaterEqual(len(box_stmts), 2, f"{cid} boxStatements count < 2")
                for s in box_stmts:
                    self.assertIn('id', s)
                    self.assertIn('label', s)
                    self.assertIn('text', s)
            else:
                self.assertEqual(card.get('typ'), '객관식', f"{cid} unknown typ '{card.get('typ')}'")
                self.assertNotIn('statement-box', card.get('front', ''), f"{cid} is 객관식 but contains statement-box")

    def test_tier3_outlier_0374_zero_byte_boxed_restoration(self):
        """T3-8: F5 (Outlier) × F2 (Boxed) × F1 (Option Restoration) on mgmt_0374."""
        card = self.cards_by_id['mgmt_0374']
        self.assertNotIn('image-frame', card.get('front', ''))
        self.assertNotIn('<img', card.get('front', ''))
        self.assertEqual(card.get('typ'), '박스선택형')
        self.assertIn('허츠버그', card.get('stemText', ''))
        self.assertIn('동기요인', card.get('stemText', ''))
        self.assertEqual(card.get('correct'), 4)

        box_stmts = card.get('boxStatements', [])
        self.assertEqual(len(box_stmts), 5)
        self.assertEqual([s['label'] for s in box_stmts], ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ'])

        btn_re = re.compile(r'<button\s+[^>]*class=["\']mcq-option\s+text-option["\']', re.DOTALL)
        self.assertEqual(len(btn_re.findall(card.get('front', ''))), 5)

    def test_tier3_outlier_0278_and_0454_interaction(self):
        """T3-9: F5 (Outliers) × F1/F4 Layout & Deduplication on mgmt_0278 and mgmt_0454."""
        # mgmt_0278
        c278 = self.cards_by_id['mgmt_0278']
        self.assertNotIn('image-frame', c278.get('front', ''))
        self.assertNotIn('<img', c278.get('front', ''))
        btn_re = re.compile(r'<button\s+[^>]*class=["\']mcq-option\s+text-option["\']', re.DOTALL)
        self.assertEqual(len(btn_re.findall(c278.get('front', ''))), 5)

        # mgmt_0454
        c454 = self.cards_by_id['mgmt_0454']
        self.assertNotIn('image-frame', c454.get('front', ''))
        self.assertNotIn('<img', c454.get('front', ''))
        self.assertEqual(len(btn_re.findall(c454.get('front', ''))), 5)
        self.assertEqual(c454.get('correct'), 3)
        self.assertIn('귀인이론', c454.get('stemText', ''))
        choices = c454.get('choices', [])
        self.assertEqual(len(choices), 5)
        self.assertIn('낮음 낮음 높음', choices[2])


if __name__ == "__main__":
    unittest.main()
