"""
tests/adversarial_stress_runner.py
Empirical Adversarial Stress Testing Harness for CardFrontParser,
assertion utilities, and Tier 1-4 test sensitivity.
Executed by Challenger 1 (e2e_challenger_1).
"""

import sys
import os
import re
import traceback
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tests.test_utils import (
    CardFrontParser,
    parse_card_front,
    has_emoji,
    has_leading_index_or_circle,
    PREFIX_INDEX_OR_CIRCLE_PAT,
    assert_zero_image_frames,
    assert_clean_options,
    verify_restored_cards,
    VALID_OPTION_LABELS
)

def run_suite(name):
    print(f"\n{'='*70}\n[SUITE] {name}\n{'='*70}")

def log_test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(f"       -> {detail}")

def test_parser_adversarial_inputs():
    run_suite("1. CardFrontParser Adversarial HTML Stress Testing")
    failures = []
    
    test_cases = [
        # (name, html_input, expected_checks)
        ("Empty string", "", lambda p: p.option_count == 0 and not p.has_image_frame),
        ("Whitespace only", "   \n\t   \n", lambda p: p.option_count == 0),
        ("Plain text no HTML", "이것은 태그가 전혀 없는 순수 한국어 텍스트입니다.", lambda p: p.option_count == 0),
        (
            "Nested unescaped <보기> brackets",
            '<div class="mcq-card" data-qid="0999">'
            '<div class="mcq-stem"><div class="stem-ocr-text">다음 <보기>에서 옳은 것을 모두 고른 것은? <보기> 중첩 태그 테스트</div></div>'
            '</div>',
            lambda p: "옳은 것을" in p.stem_ocr_text
        ),
        (
            "Malformed unescaped angle brackets in stem",
            '<div class="mcq-card">'
            '<div class="mcq-stem"><div class="stem-ocr-text">조건: A < B 이고 C > D 일 때 <보기> 참조</div></div>'
            '</div>',
            lambda p: "A < B" in p.stem_ocr_text or "C > D" in p.stem_ocr_text or len(p.stem_ocr_text) > 0
        ),
        (
            "Unclosed tags and missing closing tags",
            '<div class="mcq-card">'
            '<div class="mcq-stem"><div class="stem-ocr-text">닫히지 않은 줄기 텍스트'
            '<div class="statement-box mcq-statement-box">'
            '<div class="mcq-statement-item" data-stmt="ㄱ">'
            '<span class="mcq-stmt-badge">ㄱ</span>'
            '<span class="mcq-stmt-text">항목 내용'
            '<div class="mcq-options">'
            '<button type="button" class="mcq-option text-option" data-original="1">'
            '<span class="mcq-label">①</span>'
            '<span class="mcq-choice-text">선택지 1번 내용',
            lambda p: p.has_statement_box and (p.option_count >= 0)
        ),
        (
            "Unexpected casing (uppercase tags and classes)",
            '<DIV CLASS="MCQ-CARD" DATA-QID="0123">'
            '<DIV CLASS="MCQ-STEM"><DIV CLASS="STEM-OCR-TEXT">대문자 태그 테스트</DIV></DIV>'
            '<DIV CLASS="MCQ-OPTIONS">'
            '<BUTTON TYPE="BUTTON" CLASS="MCQ-OPTION TEXT-OPTION" DATA-ORIGINAL="1">'
            '<SPAN CLASS="MCQ-LABEL">①</SPAN>'
            '<SPAN CLASS="MCQ-CHOICE-TEXT">대문자 선택지</SPAN>'
            '</BUTTON>'
            '</DIV>'
            '</DIV>',
            lambda p: True  # Parser must not crash
        ),
        (
            "Malformed attributes with multiple equals, missing quotes",
            '<div class="mcq-card" data-qid===123 class="extra" broken=attr="test">'
            '<button class="mcq-option text-option" data-original=1>'
            '<span class="mcq-label">①</span><span class="mcq-choice-text">옵션</span>'
            '</button></div>',
            lambda p: True  # Parser must not crash
        ),
        (
            "Script, style, and comments injection",
            '<div class="mcq-card">'
            '<script>alert("xss")</script>'
            '<style>.mcq-card { color: red; }</style>'
            '<!-- HTML 주석 <보기> <button> -->'
            '<![CDATA[ <button class="mcq-option"> ]]>'
            '<button type="button" class="mcq-option text-option" data-original="1">'
            '<span class="mcq-label">①</span><span class="mcq-choice-text">정상 옵션</span>'
            '</button>'
            '</div>',
            lambda p: p.option_count >= 1
        ),
        (
            "Deeply nested elements (500 levels)",
            "".join(["<div>" for _ in range(500)]) +
            '<button class="mcq-option text-option" data-original="1">'
            '<span class="mcq-label">①</span><span class="mcq-choice-text">심층 중첩</span>'
            '</button>' +
            "".join(["</div>" for _ in range(500)]),
            lambda p: p.option_count >= 1
        ),
        (
            "Null bytes and unicode control characters",
            '<div class="mcq-card">\x00\x01\x08<div class="stem-ocr-text">\x1f본문\x0b</div>'
            '<button class="mcq-option text-option" data-original="1">'
            '<span class="mcq-label">①</span><span class="mcq-choice-text">널\x00문자</span></button></div>',
            lambda p: p.option_count == 1
        ),
        (
            "Multi-line choice text with internal inline markup (<b>, <span>, <br>)",
            '<div class="mcq-card">'
            '<button type="button" class="mcq-option text-option" data-original="1">'
            '<span class="mcq-label">①</span>'
            '<span class="mcq-choice-text">핵심 <b>강조</b> 키워드 및 <i>기울임</i> 추가 텍스트</span>'
            '</button>'
            '</div>',
            lambda p: len(p.options) == 1
        )
    ]

    for name, snippet, validator in test_cases:
        try:
            parsed = parse_card_front(snippet)
            check_ok = validator(parsed)
            if check_ok:
                log_test(f"Parser: {name}", True)
            else:
                log_test(f"Parser: {name}", False, f"Parsed result failed validation: {parsed}")
                failures.append(name)
        except Exception as e:
            log_test(f"Parser: {name}", False, f"CRASH with exception: {type(e).__name__}: {e}")
            failures.append(name)

    return failures

def test_inline_markup_in_choice_text():
    run_suite("1.1 CardFrontParser Inline Tag Truncation Investigation")
    # Test whether inline tags cause text loss in choice_text
    snippet = (
        '<div class="mcq-card">'
        '<button type="button" class="mcq-option text-option" data-original="1">'
        '<span class="mcq-label">①</span>'
        '<span class="mcq-choice-text">앞부분 <b>중간강조</b> 뒷부분텍스트</span>'
        '</button>'
        '</div>'
    )
    parsed = parse_card_front(snippet)
    opt = parsed.options[0]
    full_text = opt.choice_text
    print(f"       Captured choice_text: '{full_text}'")
    # Check if '뒷부분텍스트' is retained
    if "뒷부분텍스트" in full_text:
        log_test("Inline markup preserves subsequent text", True)
        return []
    else:
        log_test("Inline markup preserves subsequent text", False, 
                 f"BUG DETECTED: '뒷부분텍스트' lost because _active_capture reset on </b>! Captured: '{full_text}'")
        return ["Inline tag resets _active_capture prematurely"]

def test_circled_number_and_prefix_detection():
    run_suite("2. Circled Numbers & Option Prefix Adversarial Stress Testing")
    failures = []

    # Cases that MUST match has_leading_index_or_circle (forbidden prefixes)
    true_positive_cases = [
        ("Circled digit ①", "① 직무특성이론"),
        ("Circled digit ⑤", "⑤ 기대이론"),
        ("Circled digit ⑩", "⑩ 기타요인"),
        ("Circled digit ⑳", "⑳ 최종항목"),
        ("Parenthesized number (1)", "(1) 직무충실화"),
        ("Parenthesized number with space ( 2 )", "( 2 ) 리더십 이론"),
        ("Number with dot '1.'", "1. 목표설정이론"),
        ("Number with colon '1:'", "1: 강화이론"),
        ("Number with closing paren '1)'", "1) 공정성이론"),
        ("Korean question prefix '1번:'", "1번: 허츠버그 2요인 이론"),
        ("Korean question prefix '2번.'", "2번. 매슬로우 욕구 5단계"),
        ("Korean question prefix '3번 '", "3번 알더퍼 ERG 이론"),
        ("Leading whitespace then ①", "   ① 공정성 이론"),
        ("Leading tab then (1)", "\t(1) 피들러 상황모형"),
        ("Two-digit number with dot '10.'", "10. 경로-목표 이론")
    ]

    # Cases that SHOULD be flagged if they are circled prefixes:
    # ㉠ (Circled Hangul) and ❶ (Dingbat Negative Circled Digit)
    special_circled_cases = [
        ("Circled Hangul ㉠", "㉠ 조직시민행동"),
        ("Dingbat Negative Circled Digit ❶", "❶ 변혁적 리더십"),
        ("Circled Hangul ㉡", "㉡ 직무만족"),
        ("Dingbat Negative Circled Digit ❺", "❺ 감성지능")
    ]

    # Cases that MUST NOT match (False Positives - legitimate terms starting with numbers)
    false_positive_cases = [
        ("3M 혁신 문화", "3M의 경영 혁신과 15% 룰"),
        ("1차원 모델", "1차원 모델은 단순한 리더십 유형을 설명한다."),
        ("2요인 이론", "2요인 이론에서 위생요인은 불만족을 방지한다."),
        ("5대 힘 모델", "5대 힘 분석(Porter's Five Forces Model)"),
        ("7S 프레임워크", "7S 프레임워크는 맥킨지가 개발하였다."),
        ("6시그마", "6시그마 품질경영 기법"),
        ("100인의 전문가", "100인의 전문가를 대상으로 한 델파이 기법"),
        ("4단계 평가모델", "4단계 교육훈련 평가모델 (Kirkpatrick)"),
        ("Mid-sentence circled ①", "주요 요인은 ①위생요인과 ②동기요인이다."),
        ("Mid-sentence parenthesized (1)", "두 가지 차원 (1)과업지향 및 (2)관계지향"),
        ("Pure Korean text", "경영학적 관리방안에 대한 설명"),
        ("English text", "Two-factor theory of motivation")
    ]

    print("\n--- Subtest 2.1: True Positive Detection ---")
    for name, text in true_positive_cases:
        matched = has_leading_index_or_circle(text)
        if matched:
            log_test(f"TP: {name}", True)
        else:
            log_test(f"TP: {name}", False, f"Failed to detect forbidden prefix in '{text}'")
            failures.append(name)

    print("\n--- Subtest 2.2: Special Circled Numbers (㉠, ❶) ---")
    for name, text in special_circled_cases:
        matched = has_leading_index_or_circle(text)
        print(f"       has_leading_index_or_circle('{text}') = {matched}")
        if not matched:
            print(f"       [NOTE] '{name}' is NOT matched by PREFIX_INDEX_OR_CIRCLE_PAT in test_utils.py!")
            # Check what Tier 4 scenario regex does:
            t4_matched = bool(re.search(r'^[①②③④⑤❶❷❸❹❺\u2460-\u2473]', text))
            print(f"       Tier 4 regex match: {t4_matched}")

    print("\n--- Subtest 2.3: False Positive Resistance (Zero False Positives) ---")
    for name, text in false_positive_cases:
        matched = has_leading_index_or_circle(text)
        if not matched:
            log_test(f"FP Resistance: {name}", True)
        else:
            log_test(f"FP Resistance: {name}", False, f"FALSE POSITIVE: erroneously flagged legitimate term '{text}'")
            failures.append(f"FP: {name}")

    return failures

def test_emoji_detection():
    run_suite("3. Unicode Emoji Adversarial Detection Stress Testing")
    failures = []

    # True positives (MUST be detected as emojis)
    emoji_cases = [
        ("Emoticons (Grinning Face)", "정답 해설 😀 확인"),
        ("Misc Symbols & Pictographs (Fire)", "중요도 🔥🔥🔥 표시"),
        ("Transport & Map (Rocket)", "핵심 요약 🚀 출발"),
        ("Supplemental Symbols (Brain)", "인지적 오류 🧠 분석"),
        ("Symbols & Pictographs Ext-A (Diya Lamp)", "전통 문화 🪔 설명"),
        ("Misc Symbols (Warning sign)", "주의 ⚠️ 오답 함정"),
        ("Dingbats (Sparkles)", "합격 기원 ✨ 팁"),
        ("Dingbats (Check mark)", "맞춤 ✅ 완료"),
        ("Dingbats (Cross mark)", "틀림 ❌ 확인"),
        ("Misc Symbols (Heart)", "조직 몰입 ❤️ 증대")
    ]

    # False positives (MUST NOT be detected as emojis - Korean, Hanja, punctuation)
    non_emoji_cases = [
        ("Standard Hangul Syllables", "조직행동론: 개인차원의 다양성 및 지각과 성격"),
        ("Hangul Consonants (Jamo)", "ㄱ. 직무만족 ㄴ. 조직몰입 ㄷ. 조직시민행동"),
        ("Circled Hangul", "㉠ 직무충실 ㉡ 직무확대 ㉢ 직무순환"),
        ("Circled Numbers", "① ② ③ ④ ⑤"),
        ("Hanja Characters", "組織行動論, 狀況適合理論, 動機附與, 目標設定"),
        ("Standard Korean Punctuation (·, …)", "직무·과업·역할의 구분… 그리고 성과"),
        ("Korean Quotation Marks (“ ”, ‘ ’)", "“변혁적 리더십” 및 ‘거래적 리더십’ 비교"),
        ("Korean Brackets (〈 〉, 《 》, 【 】)", "〈보기〉 《경영학원론》 【참고문헌】"),
        ("Tilde & Wave Dash (∼, ~)", "1950년대∼1960년대 동기부여 이론"),
        ("Reference Mark (※)", "※ 주의: 본 문제는 2020년 기출문제임"),
        ("Mathematical Symbols (±, ×, ÷, ≠, ≤, ≥)", "허용오차: ±5%, 계산식: 100 × 2 ÷ 4 ≠ 0"),
        ("ASCII symbols & punctuation", "! @ # $ % ^ & * ( ) _ + - = [ ] { } | : ; < > , . ? /")
    ]

    print("\n--- Subtest 3.1: True Positive Emoji Detection ---")
    for name, text in emoji_cases:
        detected = has_emoji(text)
        if detected:
            log_test(f"TP Emoji: {name}", True)
        else:
            log_test(f"TP Emoji: {name}", False, f"Failed to detect emoji in '{text}'")
            failures.append(f"Emoji TP: {name}")

    print("\n--- Subtest 3.2: False Positive Emoji Resistance (Hangul / Punctuation) ---")
    for name, text in non_emoji_cases:
        detected = has_emoji(text)
        if not detected:
            log_test(f"FP Emoji Resistance: {name}", True)
        else:
            log_test(f"FP Emoji Resistance: {name}", False, f"FALSE POSITIVE: erroneously detected emoji in '{text}'")
            failures.append(f"Emoji FP: {name}")

    return failures

def test_mutation_fault_injection():
    run_suite("4. Mutation Testing & Fault Injection Sensitivity")
    failures = []

    # Let's construct a canonical compliant mock card
    canonical_front = (
        '<div class="mcq-card" data-qid="0277" data-shuffle="false">\n'
        '  <div class="mcq-header"><span class="mcq-qnum">문제 0277</span><span class="source-badge">2020 CPA</span></div>\n'
        '  <div class="mcq-stem"><div class="stem-ocr-text">태도와 행동에 관한 설명으로 가장 적절하지 않은 것은?</div></div>\n'
        '  <div class="mcq-options">\n'
        '    <button type="button" class="mcq-option text-option" data-original="1"><span class="mcq-label">①</span><span class="mcq-choice-text">태도의 인지적 요소는 신념이나 가치관을 의미한다.</span></button>\n'
        '    <button type="button" class="mcq-option text-option" data-original="2"><span class="mcq-label">②</span><span class="mcq-choice-text">정서적 요소는 감정이나 기분을 나타낸다.</span></button>\n'
        '    <button type="button" class="mcq-option text-option" data-original="3"><span class="mcq-label">③</span><span class="mcq-choice-text">행동적 요소는 특정 대상에 대한 행동 의도를 의미한다.</span></button>\n'
        '    <button type="button" class="mcq-option text-option" data-original="4"><span class="mcq-label">④</span><span class="mcq-choice-text">인지부조화 이론은 페스팅거에 의해 제안되었다.</span></button>\n'
        '    <button type="button" class="mcq-option text-option" data-original="5"><span class="mcq-label">⑤</span><span class="mcq-choice-text">태도와 행동 간의 일관성은 자기지각이론으로도 설명된다.</span></button>\n'
        '  </div>\n'
        '  <div class="mcq-help">1~5번 키 또는 보기를 눌러 답을 선택하세요.</div>\n'
        '</div>'
    )

    canonical_card = {
        "id": "mgmt_0277",
        "qid": "0277",
        "subj": "1.02 조직행동: 개인",
        "typ": "객관식",
        "correct": 3,
        "stemText": "태도와 행동에 관한 설명으로 가장 적절하지 않은 것은?",
        "choices": [
            "1번: 태도의 인지적 요소는 신념이나 가치관을 의미한다.",
            "2번: 정서적 요소는 감정이나 기분을 나타낸다.",
            "3번: 행동적 요소는 특정 대상에 대한 행동 의도를 의미한다.",
            "4번: 인지부조화 이론은 페스팅거에 의해 제안되었다.",
            "5번: 태도와 행동 간의 일관성은 자기지각이론으로도 설명된다."
        ],
        "front": canonical_front,
        "back": '<div class="mcq-result" data-qid="0277" data-correct="3"><div class="mcq-answer-badge">정답 3번</div><div class="mcq-explanation">해설</div></div>',
        "note": "정답: 3번",
        "probPage": 10,
        "ansPage": 20,
        "probPdf": "prob_02.pdf",
        "ansPdf": "ans_02.pdf"
    }

    # Verify baseline is clean
    parsed_base = parse_card_front(canonical_card["front"])
    try:
        assert_zero_image_frames(canonical_card, parsed_base)
        assert_clean_options(canonical_card, parsed_base)
        log_test("Baseline Canonical Card Validation", True)
    except AssertionError as e:
        log_test("Baseline Canonical Card Validation", False, str(e))
        failures.append("Baseline validation failed")

    # Mutations:
    mutations = [
        (
            "Mutant 1: Injected image-frame tag",
            lambda c: {**c, "front": c["front"].replace('class="stem-ocr-text"', 'class="stem-ocr-text"><div class="image-frame">')},
            assert_zero_image_frames,
            "assert_zero_image_frames caught injected image-frame"
        ),
        (
            "Mutant 2: Injected <img> tag",
            lambda c: {**c, "front": c["front"].replace('class="stem-ocr-text"', 'class="stem-ocr-text"><img src="x.webp">')},
            assert_zero_image_frames,
            "assert_zero_image_frames caught injected <img>"
        ),
        (
            "Mutant 3: Button missing text-option class (number-option regression)",
            lambda c: {**c, "front": c["front"].replace('mcq-option text-option', 'mcq-option number-option', 1)},
            assert_clean_options,
            "assert_clean_options caught number-option class"
        ),
        (
            "Mutant 4: Mismatched data-original attribute (e.g. data-original='0')",
            lambda c: {**c, "front": c["front"].replace('data-original="1"', 'data-original="0"')},
            assert_clean_options,
            "assert_clean_options caught non-sequential data-original"
        ),
        (
            "Mutant 5: Forbidden leading circled digit in choice text",
            lambda c: {**c, "front": c["front"].replace('>태도의 인지적', '>① 태도의 인지적')},
            assert_clean_options,
            "assert_clean_options caught leading circled digit"
        ),
        (
            "Mutant 6: Forbidden leading '1번:' in choice text",
            lambda c: {**c, "front": c["front"].replace('>태도의 인지적', '>1번: 태도의 인지적')},
            assert_clean_options,
            "assert_clean_options caught leading '1번:' prefix"
        ),
        (
            "Mutant 7: Forbidden leading '1. ' in choice text",
            lambda c: {**c, "front": c["front"].replace('>태도의 인지적', '>1. 태도의 인지적')},
            assert_clean_options,
            "assert_clean_options caught leading '1. ' prefix"
        ),
        (
            "Mutant 8: Emoji injected in choice text",
            lambda c: {**c, "front": c["front"].replace('>태도의 인지적', '>💡 태도의 인지적')},
            assert_clean_options,
            "assert_clean_options caught emoji in choice text"
        ),
        (
            "Mutant 9: Empty choice text",
            lambda c: {**c, "front": c["front"].replace('태도의 인지적 요소는 신념이나 가치관을 의미한다.', '   ')},
            assert_clean_options,
            "assert_clean_options caught empty choice text"
        ),
        (
            "Mutant 10: Wrong label (e.g. '1' instead of '①')",
            lambda c: {**c, "front": c["front"].replace('<span class="mcq-label">①</span>', '<span class="mcq-label">1</span>')},
            assert_clean_options,
            "assert_clean_options caught non-circled label"
        ),
        (
            "Mutant 11: Invalid option count (3 options)",
            lambda c: {**c, "front": re.sub(r'<button[^>]*data-original="[45]"[^>]*>.*?</button>', '', c["front"], flags=re.DOTALL)},
            assert_clean_options,
            "assert_clean_options caught 3 options (boundary violation)"
        )
    ]

    for name, mutator, check_func, success_msg in mutations:
        mutant_card = mutator(canonical_card)
        parsed_mutant = parse_card_front(mutant_card["front"])
        try:
            check_func(mutant_card, parsed_mutant)
            # If no assertion error, the test FAILED to catch the mutation!
            log_test(name, False, "MUTATION MISSED! Check failed to raise AssertionError")
            failures.append(name)
        except AssertionError as e:
            log_test(name, True, f"Caught: {e.args[0] if e.args else ''}")

    return failures

def test_verify_restored_cards_validation_gap():
    run_suite("5. verify_restored_cards() Automated Tooling Sensitivity")
    import tempfile
    import json
    failures = []

    # Card with emoji and leading circle in choices and button
    corrupt_card = {
        "id": "mgmt_0277",
        "qid": "0277",
        "typ": "객관식",
        "choices": [
            "1번: ① 이모지 🚀 옵션",
            "2번: (1) 괄호숫자 옵션",
            "3번: 정상 옵션",
            "4번: 💡 전구 이모지 옵션"
        ],
        "front": (
            '<div class="mcq-card">'
            '<button type="button" class="mcq-option text-option" data-original="1"><span class="mcq-choice-text">① 이모지 🚀 옵션</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="2"><span class="mcq-choice-text">(1) 괄호숫자 옵션</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="3"><span class="mcq-choice-text">정상 옵션</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="4"><span class="mcq-choice-text">💡 전구 이모지 옵션</span></button>'
            '</div>'
        )
    }

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"cards": [corrupt_card]}, f)
        tmp_name = f.name

    try:
        errors = verify_restored_cards(tmp_name, start_id="mgmt_0277", end_id="mgmt_0277", expected_count=1)
        print(f"       verify_restored_cards() output on card with emojis & circled numbers: {errors}")
        if len(errors) == 0:
            log_test("verify_restored_cards catches emojis & leading circles", False,
                     "CRITICAL GAP: verify_restored_cards() returned 0 errors on card with emojis and leading circles!")
            failures.append("verify_restored_cards lacks option cleanness / emoji validation")
        else:
            log_test("verify_restored_cards catches emojis & leading circles", True)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

    return failures


def test_tier_test_suites_mutation_sensitivity():
    run_suite("6. Test Module Suite Sensitivity to Injected Defects")
    import unittest
    from tests.test_tier1_features import TestTier1_F1_TextOptionRestoration
    from tests.test_tier4_scenarios import TestTier4Scenarios

    failures = []

    # Case 1: Injected '(1) ' in choice text
    # Does Tier 1 test_f1_05 catch it?
    tc1 = TestTier1_F1_TextOptionRestoration()
    tc1.cards = [{
        "id": "mgmt_0277",
        "choices": ["1번: 태도", "2번: 행동", "3번: 인지", "4번: 정서"],
        "front": (
            '<div class="mcq-card">'
            '<button type="button" class="mcq-option text-option" data-original="1"><span class="mcq-choice-text">(1) 태도</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="2"><span class="mcq-choice-text">행동</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="3"><span class="mcq-choice-text">인지</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="4"><span class="mcq-choice-text">정서</span></button>'
            '</div>'
        )
    }]

    try:
        tc1.test_f1_05_choice_text_spans_clean_without_leading_indices()
        log_test("Tier 1 test_f1_05 catches '(1)' prefix", False,
                 "ESCAPE: test_f1_05 PASSED despite '(1) 태도' in choice text!")
        failures.append("Tier 1 test_f1_05 blind to '(1)'")
    except AssertionError as e:
        log_test("Tier 1 test_f1_05 catches '(1)' prefix", True)

    # Case 2: Injected '(1) ' in choice text against Tier 4 scenario 3 inner assertion logic
    choice_text_1 = "(1) 태도"
    t4_caught_paren = False
    try:
        assert not re.search(r'^[①②③④⑤❶❷❸❹❺\u2460-\u2473]', choice_text_1)
        assert not re.search(r'^[1-5]\s*번\s*[:\.]', choice_text_1)
        assert not re.search(r'^[1-5]\s*[\.\)]', choice_text_1)
    except AssertionError:
        t4_caught_paren = True

    if not t4_caught_paren:
        log_test("Tier 4 scenario_3 regex catches '(1)' prefix", False,
                 "ESCAPE: Tier 4 scenario 3 regexes do NOT catch '(1)' prefix!")
        failures.append("Tier 4 scenario_3 regex blind to '(1)'")
    else:
        log_test("Tier 4 scenario_3 regex catches '(1)' prefix", True)

    # Case 3: Injected '❶ ' in choice text against Tier 1 test_f1_05
    tc1.cards = [{
        "id": "mgmt_0277",
        "choices": ["1번: 태도", "2번: 행동", "3번: 인지", "4번: 정서"],
        "front": (
            '<div class="mcq-card">'
            '<button type="button" class="mcq-option text-option" data-original="1"><span class="mcq-choice-text">❶ 태도</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="2"><span class="mcq-choice-text">행동</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="3"><span class="mcq-choice-text">인지</span></button>'
            '<button type="button" class="mcq-option text-option" data-original="4"><span class="mcq-choice-text">정서</span></button>'
            '</div>'
        )
    }]

    try:
        tc1.test_f1_05_choice_text_spans_clean_without_leading_indices()
        log_test("Tier 1 test_f1_05 catches '❶' prefix", False,
                 "ESCAPE: test_f1_05 PASSED despite '❶ 태도' in choice text!")
        failures.append("Tier 1 test_f1_05 blind to '❶'")
    except AssertionError as e:
        log_test("Tier 1 test_f1_05 catches '❶' prefix", True)

    # Case 4: Injected '㉠ ' in choice text against Tier 4 scenario 3 inner assertion logic
    choice_text_hangul = "㉠ 태도"
    t4_caught_hangul = False
    try:
        assert not re.search(r'^[①②③④⑤❶❷❸❹❺\u2460-\u2473]', choice_text_hangul)
        assert not re.search(r'^[1-5]\s*번\s*[:\.]', choice_text_hangul)
        assert not re.search(r'^[1-5]\s*[\.\)]', choice_text_hangul)
    except AssertionError:
        t4_caught_hangul = True

    if not t4_caught_hangul:
        log_test("Tier 4 scenario_3 regex catches '㉠' prefix", False,
                 "ESCAPE: Tier 4 scenario 3 regexes do NOT catch '㉠' circled Hangul prefix!")
        failures.append("Tier 4 scenario_3 regex blind to '㉠'")
    else:
        log_test("Tier 4 scenario_3 regex catches '㉠' prefix", True)

    return failures


if __name__ == "__main__":
    p_fails = test_parser_adversarial_inputs()
    inline_fails = test_inline_markup_in_choice_text()
    c_fails = test_circled_number_and_prefix_detection()
    e_fails = test_emoji_detection()
    m_fails = test_mutation_fault_injection()
    v_fails = test_verify_restored_cards_validation_gap()
    s_fails = test_tier_test_suites_mutation_sensitivity()

    print("\n" + "="*70)
    print("CHALLENGER 1 ADVERSARIAL STRESS TEST SUMMARY")
    print("="*70)
    print(f"1. Parser adversarial inputs failures: {len(p_fails)}")
    print(f"1.1 Inline markup truncation issues: {len(inline_fails)}")
    print(f"2. Circled & prefix detection failures: {len(c_fails)}")
    print(f"3. Emoji detection failures:           {len(e_fails)}")
    print(f"4. Mutation injection missed:          {len(m_fails)}")
    print(f"5. verify_restored_cards gap:          {len(v_fails)}")
    print(f"6. Tier test module blindspots:        {len(s_fails)}")
    total_issues = len(p_fails) + len(inline_fails) + len(c_fails) + len(e_fails) + len(m_fails) + len(v_fails) + len(s_fails)
    print(f"TOTAL ADVERSARIAL DEFECTS/FINDINGS:    {total_issues}")
    print("="*70)
    sys.exit(0 if total_issues == 0 else 1)
