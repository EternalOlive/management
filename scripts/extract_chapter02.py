# -*- coding: utf-8 -*-
"""
Chapter 02 Extraction & Text Generation Pipeline
Extracts all 231 Chapter 02 questions (mgmt_0277 through mgmt_0507)
Output: chapter02_extracted.json
"""

import os
import re
import json
import fitz
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
CARDS_DATA_PATH = os.path.join(BASE_DIR, "cards-data.json")
PDF_PAGE_MAP_PATH = os.path.join(BASE_DIR, "pdf-page-map.json")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "chapter02_extracted.json")
OCR_CACHE_PATH = os.path.join(BASE_DIR, ".agents", "teamwork", "m1_explorer_1", "all_ch2_ocr_raw.json")

# Canonical Source Tag Normalization Rules
SOURCE_FIXES = [
    (r'공기업.*출제경향.*반영|수기업.*|장기입.*', '공기업 출제경향 반영'),
    (r'.*코레일.*수송직.*', '2020 코레일 수송직렬 복원'),
    (r'.*(?:2이3|2013).*노무사.*|.*장년기노`nt.*', '2013 공인노무사'),
    (r'.*(?:2이4|2014).*노무사.*', '2014 공인노무사'),
    (r'.*(?:2이5|2015).*노무사.*|.*2015 공언노무사.*', '2015 공인노무사'),
    (r'.*(?:2이6|2016).*노무사.*|.*\.刈16 飜`뜨`,나.*', '2016 공인노무사'),
    (r'.*(?:2이7|2017).*노무사.*', '2017 공인노무사'),
    (r'.*(?:2이8|2018).*노무사.*', '2018 공인노무사'),
    (r'.*(?:2이9|2019).*노무사.*|.*시인!r부사.*', '2019 공인노무사'),
    (r'.*(?:20기|2021).*노무사.*|.*하한\.|노부사.*', '2021 공인노무사'),
    (r'.*(?:2022).*노무사.*', '2022 공인노무사'),
    (r'.*(?:2023).*노무사.*', '2023 공인노무사'),
    (r'.*(?:2024).*노무사.*', '2024 공인노무사'),
    (r'.*(?:2006|℃06).*가[영행뱅명]거래.*', '2006 가맹거래사'),
    (r'.*(?:2008).*가[영행뱅명]거래.*', '2008 가맹거래사'),
    (r'.*(?:2010).*가[영행뱅명]거래.*', '2010 가맹거래사'),
    (r'.*(?:2011).*가[영행뱅명]거래.*', '2011 가맹거래사'),
    (r'.*(?:2012).*가[영행뱅명]거래.*', '2012 가맹거래사'),
    (r'.*(?:2013).*가[영행뱅명]거래.*', '2013 가맹거래사'),
    (r'.*(?:2016).*가[영행뱅명]거래.*', '2016 가맹거래사'),
    (r'.*(?:2017|2이7).*가[영행뱅명]거.*', '2017 가맹거래사'),
    (r'.*(?:2020).*가[영행뱅명]거래.*', '2020 가맹거래사'),
    (r'.*(?:2021|20기).*가[영행뱅명]거래.*', '2021 가맹거래사'),
    (r'.*(?:2022).*가[영행뱅명]거래.*', '2022 가맹거래사'),
    (r'.*(?:2024).*가[영행뱅명]거래.*', '2024 가맹거래사'),
    (r'.*(?:2013|2이3).*지도사.*|.*\(최영`!€사.*', '2013 경영지도사'),
    (r'.*(?:2016|2이6).*지도사.*', '2016 경영지도사'),
    (r'.*(?:2017).*지도사.*|.*2017 71\(2川도사.*', '2017 경영지도사'),
    (r'.*(?:2018|2이8|20tS).*지도사.*|.*원영재도사.*|.*2이8 경영.*', '2018 경영지도사'),
    (r'.*(?:2019).*지도사.*', '2019 경영지도사'),
    (r'.*(?:2020).*지도사.*', '2020 경영지도사'),
    (r'.*(?:2022).*지도사.*|.*경일지도사.*|.*원원`\|도사.*', '2022 경영지도사'),
    (r'.*(?:2023|꼬23).*지도사.*', '2023 경영지도사'),
    (r'.*(?:2024).*군무원.*|.*기급 군무원.*', '2024 7급 군무원'),
    (r'.*(?:2021|20기).*7급.*군무원.*', '2021 7급 군무원'),
    (r'.*(?:2021|20기).*9급.*군무원.*', '2021 9급 군무원'),
    (r'.*(?:2022).*5급.*군무원.*', '2022 5급 군무원'),
    (r'.*(?:2023).*9급.*군무원.*', '2023 9급 군무원'),
    (r'.*(?:2024).*9급.*군무원.*', '2024 9급 군무원'),
    (r'.*(?:2002|℃02).*CPA.*', '2002 CPA'),
    (r'.*(?:2005).*CPA.*', '2005 CPA'),
    (r'.*(?:2006|\.℃06).*C[PN]A?.*', '2006 CPA'),
    (r'.*(?:2007).*CPA.*', '2007 CPA'),
    (r'.*(?:2008).*CPA.*', '2008 CPA'),
    (r'.*(?:2009).*CPA.*', '2009 CPA'),
    (r'.*(?:2010).*CPA.*', '2010 CPA'),
    (r'.*(?:2011).*CPA.*', '2011 CPA'),
    (r'.*(?:2013).*CPA.*', '2013 CPA'),
    (r'.*(?:2014).*CPA.*', '2014 CPA'),
    (r'.*(?:2015|2이5|NOS).*CPA.*', '2015 CPA'),
    (r'.*(?:2016|2이6).*CPA.*', '2016 CPA'),
    (r'.*(?:2018|2이8).*CPA.*', '2018 CPA'),
    (r'.*(?:2019).*CPA.*', '2019 CPA'),
    (r'.*(?:2020).*CPA.*', '2020 CPA'),
    (r'.*(?:2021|202\)).*C[PC,]A.*', '2021 CPA'),
    (r'.*(?:2022).*CPA.*', '2022 CPA'),
    (r'.*(?:2023).*CPA.*', '2023 CPA'),
    (r'.*(?:2024).*CPA.*', '2024 CPA'),
    (r'.*(?:2007).*7급.*국가.*', '2007 7급 국가직'),
    (r'.*(?:2008).*7급.*국가.*', '2008 7급 국가직'),
    (r'.*(?:2009).*7급.*국가.*', '2009 7급 국가직'),
    (r'.*(?:2010).*7급.*국가.*', '2010 7급 국가직'),
    (r'.*(?:2011|℃11).*7.*국가.*', '2011 7급 국가직'),
    (r'.*(?:2012|2이2).*7급.*국가.*', '2012 7급 국가직'),
    (r'.*(?:2013|4刈13).*7급.*국가.*', '2013 7급 국가직'),
    (r'.*(?:2016).*7급.*국가.*', '2016 7급 국가직'),
    (r'.*(?:2017).*7급.*국가.*', '2017 7급 국가직'),
    (r'.*(?:2020).*7.*국가.*', '2020 7급 국가직'),
    (r'.*(?:2021).*7.*국가.*', '2021 7급 국가직'),
    (r'.*(?:2022).*7.*국가.*', '2022 7급 국가직'),
    (r'.*(?:2023).*7.*국가.*', '2023 7급 국가직'),
    (r'.*(?:2024).*7.*국가.*', '2024 7급 국가직'),
    (r'.*(?:2017).*7급.*서울시.*', '2017 7급 서울시'),
    (r'.*(?:2020).*7급.*서[을울]시.*', '2020 7급 서울시'),
    (r'.*(?:2023).*7급.*서울시.*', '2023 7급 서울시'),
    (r'.*(?:2019|2이9).*산업안전.*', '2019 산업안전지도사'),
    (r'^7급\s*국가[직책]$', '7급 국가직'),
    (r'^7급\s*서울시$', '7급 서울시'),
    (r'^가[영행명]거래사$', '가맹거래사'),
    (r'^공기업$', '공기업 출제경향 반영'),
]

EXAM_KEYWORDS = [
    '공기업', '출제경향', '공인회계사', 'CPA', '공인노무사', '노무사',
    '군무원', '경영지도사', '지도사', '가맹거래사', '가맹', '서울시',
    '국가직', '지방직', '7급', '9급', '5급', '코레일', '수송직', '산업안전'
]
YEAR_PAT = re.compile(r'^(?:20\d\d|19\d\d|[2근][이01][0-9]|℃\d{2}|\.℃\d{2}|含\d{3}|NOS)\b')

CHOICE_MARKER_PAT = re.compile(r'^\s*(?:[①-⑤]|[\(（]?[1-5][\)）\.]?|[0㉨㉣㉦@㉭]|(?:년|기|향)[\)）])\s*')
STEM_END_PAT = re.compile(
    r'(?:것은\?|무엇인가\?|않은 것은\?|옳은 것은\?|설명이다\.|고르면\?|짝지어진 것은\?|'
    r'나열한 것은\?|모은 것은\?|선택한 것은\?|묶인 것은\?|적절한 것은\?|않는가\?|'
    r'오류는\?|현상은\?|기법은\?|방법은\?|\?$)'
)

def normalize_source_tag(raw_tag):
    if not raw_tag:
        return ""
    tag = raw_tag.strip()
    for pat, canonical in SOURCE_FIXES:
        if re.search(pat, tag, re.IGNORECASE):
            return canonical
    m = re.search(r'\b(20\d\d)\s*([가-힣A-Za-z0-9 ]+)', tag)
    if m:
        return f"{m.group(1)} {m.group(2).strip()}"
    return tag

def clean_choice_body(text):
    cleaned = CHOICE_MARKER_PAT.sub('', text).strip()
    cleaned = re.sub(r'^[\.\-:,]\s*', '', cleaned).strip()
    return cleaned

def sort_lines_reading_order(lines, y_threshold=45):
    if not lines:
        return []
    raw_sorted = sorted([l for l in lines if l.get('rect')], key=lambda l: l['rect']['y'])
    rows = []
    for l in raw_sorted:
        ly = l['rect']['y']
        placed = False
        for row in rows:
            avg_y = sum(item['rect']['y'] for item in row) / len(row)
            if abs(ly - avg_y) <= y_threshold:
                row.append(l)
                placed = True
                break
        if not placed:
            rows.append([l])
    result = []
    rows.sort(key=lambda row: sum(item['rect']['y'] for item in row) / len(row))
    for row in rows:
        row.sort(key=lambda item: item['rect']['x'])
        result.extend(row)
    return result

# ── Ground Truth for All 21 Confirmed Boxed Questions ──
BOXED_GROUND_TRUTH = {
    "0313": {
        "sourceTag": "2024 공인노무사",
        "stemText": "핵심 자기평가(core self-evaluation)가 높은 사람들은 자신을 가능성 있고, 능력 있고, 가치 있는 사람으로 평가한다. 핵심 자기평가의 구성요소를 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "자존감", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "통제 위치", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "정서적 안정성", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "관계성", "isCorrect": False},
            {"id": "ㅁ", "label": "ㅁ", "text": "일반화된 자기효능감", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ, ㄹ",
            "2번: ㄱ, ㄷ, ㄹ",
            "3번: ㄴ, ㄷ, ㄹ",
            "4번: ㄱ, ㄴ, ㄷ, ㅁ",
            "5번: ㄴ, ㄷ, ㄹ, ㅁ"
        ],
        "answer": "4",
        "choiceCount": 5
    },
    "0323": {
        "sourceTag": "2024 7급 군무원",
        "stemText": "다음 중 호프스테드(G. Hofstede)가 제시한 국가적 문화 유형의 차이를 구분하는 기준에 해당하는 것으로 가장 알맞게 짝지어진 것은?",
        "boxStatements": [
            {"id": "㉠", "label": "㉠", "text": "권력 격차(power distance)", "isCorrect": True},
            {"id": "㉡", "label": "㉡", "text": "개인주의 / 집단주의(individualism / collectivism)", "isCorrect": True},
            {"id": "㉢", "label": "㉢", "text": "개방성 / 배타성(openness / exclusiveness)", "isCorrect": False},
            {"id": "㉣", "label": "㉣", "text": "단기 지향성 / 장기 지향성(short-term / long-term)", "isCorrect": True},
            {"id": "㉤", "label": "㉤", "text": "불확실성 회피(uncertainty avoidance)", "isCorrect": True},
            {"id": "㉥", "label": "㉥", "text": "수직적 계층성 / 수평적 계층성(vertical hierarchy / horizontal hierarchy)", "isCorrect": False}
        ],
        "choices": [
            "1번: ㉠, ㉡, ㉢, ㉣",
            "2번: ㉠, ㉡, ㉣, ㉤",
            "3번: ㉠, ㉡, ㉤, ㉥",
            "4번: ㉢, ㉣, ㉤, ㉥"
        ],
        "answer": "2",
        "choiceCount": 4
    },
    "0325": {
        "sourceTag": "공기업 출제경향 반영",
        "stemText": "지각에 영향을 미치는 요소 중 지각주체 관련 요소에 해당하는 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "크기", "isCorrect": False},
            {"id": "ㄴ", "label": "ㄴ", "text": "배경", "isCorrect": False},
            {"id": "ㄷ", "label": "ㄷ", "text": "태도", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "시간", "isCorrect": False},
            {"id": "ㅁ", "label": "ㅁ", "text": "동기", "isCorrect": True},
            {"id": "ㅂ", "label": "ㅂ", "text": "직무여건", "isCorrect": False},
            {"id": "ㅅ", "label": "ㅅ", "text": "근접성", "isCorrect": False},
            {"id": "ㅇ", "label": "ㅇ", "text": "흥미", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ, ㄷ",
            "2번: ㄱ, ㅁ, ㅅ",
            "3번: ㄷ, ㅁ, ㅇ",
            "4번: ㄹ, ㅁ, ㅂ",
            "5번: ㅁ, ㅅ, ㅇ"
        ],
        "answer": "3",
        "choiceCount": 5
    },
    "0331": {
        "sourceTag": "2021 공인노무사",
        "stemText": "켈리(H. Kelley)의 귀인이론에서 행동의 원인을 내적 또는 외적으로 판단하는 데 활용하는 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "특이성(distinctiveness)", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "공정성(equity)", "isCorrect": False},
            {"id": "ㄷ", "label": "ㄷ", "text": "일관성(consistency)", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "합의성(consensus)", "isCorrect": True},
            {"id": "ㅁ", "label": "ㅁ", "text": "관계성(relationship)", "isCorrect": False}
        ],
        "choices": [
            "1번: ㄱ, ㄴ",
            "2번: ㄱ, ㄷ, ㄹ",
            "3번: ㄱ, ㄷ, ㅁ",
            "4번: ㄴ, ㄷ, ㄹ",
            "5번: ㄷ, ㄹ, ㅁ"
        ],
        "answer": "2",
        "choiceCount": 5
    },
    "0342": {
        "sourceTag": "2007 7급 국가직",
        "stemText": "공정한 평가를 저해하는 요소에 대한 다음 설명 중 옳은 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "논리적 오류 : 외부적 상황이 모호할수록 자신의 경험, 욕구, 동기를 근거로 눈에 먼저 들어오는 정보에 의존하고 다른 정보는 무시하려는 경향", "isCorrect": False},
            {"id": "b", "label": "b", "text": "현혹효과의 문제 : 피평가자의 어느 한 면을 기준으로 다른 것까지 함께 평가하려는 경향", "isCorrect": True},
            {"id": "c", "label": "c", "text": "관대화 경향 : 피평가자의 실제 능력이나 실적보다도 더 높게 평가하려는 경향", "isCorrect": True},
            {"id": "d", "label": "d", "text": "상동적 태도 : 피평가자가 속한 사회적 집단 또는 계층을 기초로 피평가자를 평가하려는 경향", "isCorrect": True}
        ],
        "choices": [
            "1번: a, b, c",
            "2번: a, b, d",
            "3번: a, c, d",
            "4번: b, c, d"
        ],
        "answer": "4",
        "choiceCount": 4
    },
    "0367": {
        "sourceTag": "2017 가맹거래사",
        "stemText": "동기부여의 내용이론에 해당하는 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "가", "label": "가", "text": "A. Maslow의 욕구단계이론", "isCorrect": True},
            {"id": "나", "label": "나", "text": "C. Alderfer의 ERG이론", "isCorrect": True},
            {"id": "다", "label": "다", "text": "V. Vroom의 기대이론", "isCorrect": False},
            {"id": "라", "label": "라", "text": "J. Adams의 공정성이론", "isCorrect": False},
            {"id": "마", "label": "마", "text": "F. Herzberg의 2요인 이론", "isCorrect": True}
        ],
        "choices": [
            "1번: 가, 나",
            "2번: 가, 다, 라",
            "3번: 가, 나, 마",
            "4번: 나, 라, 마",
            "5번: 다, 라, 마"
        ],
        "answer": "3",
        "choiceCount": 5
    },
    "0372": {
        "sourceTag": "2014 공인노무사",
        "stemText": "매슬로우(Maslow)의 욕구단계를 순서대로 나열한 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "생리욕구", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "안전욕구", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "사회적욕구", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "존경욕구", "isCorrect": True},
            {"id": "ㅁ", "label": "ㅁ", "text": "자아실현욕구", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ - ㄴ - ㄷ - ㄹ - ㅁ",
            "2번: ㄱ - ㄷ - ㄴ - ㄹ - ㅁ",
            "3번: ㄴ - ㄱ - ㄷ - ㄹ - ㅁ",
            "4번: ㄴ - ㄱ - ㄷ - ㅁ - ㄹ",
            "5번: ㄷ - ㄱ - ㄴ - ㄹ - ㅁ"
        ],
        "answer": "1",
        "choiceCount": 5
    },
    "0374": {
        "sourceTag": "2016 공인노무사",
        "stemText": "허츠버그(F. Herzberg)의 2요인이론에서 동기요인을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "상사와의 관계", "isCorrect": False},
            {"id": "ㄴ", "label": "ㄴ", "text": "성취", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "회사 정책 및 관리방침", "isCorrect": False},
            {"id": "ㄹ", "label": "ㄹ", "text": "작업조건", "isCorrect": False},
            {"id": "ㅁ", "label": "ㅁ", "text": "인정", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ",
            "2번: ㄱ, ㄷ",
            "3번: ㄴ, ㄷ",
            "4번: ㄴ, ㅁ",
            "5번: ㄹ, ㅁ"
        ],
        "answer": "4",
        "choiceCount": 5
    },
    "0378": {
        "sourceTag": "2022 공인노무사",
        "stemText": "맥그리거(D. McGregor)의 XY이론 중 Y이론에 관한 설명으로 옳은 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "동기부여는 생리적 욕구나 안전욕구 단계에서만 가능하다.", "isCorrect": False},
            {"id": "ㄴ", "label": "ㄴ", "text": "작업조건이 잘 갖추어지면 일은 놀이와 같이 자연스러운 것이다.", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "대부분의 사람들은 엄격하게 통제되어야 하고 조직 목표를 달성하기 위해서는 강제되어야 한다.", "isCorrect": False},
            {"id": "ㄹ", "label": "ㄹ", "text": "사람은 적절하게 동기부여가 되면 자율적이고 창의적으로 업무를 수행한다.", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ",
            "2번: ㄱ, ㄷ",
            "3번: ㄱ, ㄹ",
            "4번: ㄴ, ㄹ",
            "5번: ㄷ, ㄹ"
        ],
        "answer": "4",
        "choiceCount": 5
    },
    "0380": {
        "sourceTag": "2015 경영지도사",
        "stemText": "허즈버그(F. Herzberg)는 직무만족-생산성의 관련성을 연구한 결과, 2요인 이론을 주장하였다. 허즈버그가 제시한 동기요인으로 옳은 것을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "책임감", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "인정", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "급여", "isCorrect": False},
            {"id": "ㄹ", "label": "ㄹ", "text": "성장", "isCorrect": True},
            {"id": "ㅁ", "label": "ㅁ", "text": "일자체", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ, ㄷ",
            "2번: ㄱ, ㄷ, ㄹ",
            "3번: ㄱ, ㄴ, ㄹ, ㅁ",
            "4번: ㄴ, ㄷ, ㄹ, ㅁ",
            "5번: ㄱ, ㄴ, ㄷ, ㄹ, ㅁ"
        ],
        "answer": "3",
        "choiceCount": 5
    },
    "0390": {
        "sourceTag": "2011 7급 국가직",
        "stemText": "욕구단계 이론에서 매슬로우(Maslow)가 주장하는 인간의 욕구를 하위부터 상위단계 순으로 바르게 나열한 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "일상의 안전, 보호, 안정 등에 대한 욕구", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "물과 음식, 물질적 풍요 등에 대한 욕구", "isCorrect": True},
            {"id": "ㄷ", "label": "ㄷ", "text": "다른 사람과의 관계 속에서 사랑, 관심, 소속감 등에 대한 욕구", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "창조적인 능력을 향상시키고 활용하여 자아를 실현하고자 하는 욕구", "isCorrect": True},
            {"id": "ㅁ", "label": "ㅁ", "text": "타인으로부터 존경, 권위, 위엄 등에 대한 욕구", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ - ㄴ - ㄷ - ㄹ - ㅁ",
            "2번: ㄴ - ㄱ - ㄷ - ㅁ - ㄹ",
            "3번: ㄴ - ㄱ - ㄷ - ㄹ - ㅁ",
            "4번: ㄷ - ㄴ - ㄱ - ㅁ - ㄹ"
        ],
        "answer": "2",
        "choiceCount": 4
    },
    "0405": {
        "sourceTag": "2019 가맹거래사",
        "stemText": "동기부여 이론 중 공정성이론(equity theory)에서 불공정성으로 인한 긴장을 해소할 수 있는 방법을 모두 고른 것은?",
        "boxStatements": [
            {"id": "가", "label": "가", "text": "투입의 변경", "isCorrect": True},
            {"id": "나", "label": "나", "text": "산출의 변경", "isCorrect": True},
            {"id": "다", "label": "다", "text": "준거대상의 변경", "isCorrect": True},
            {"id": "라", "label": "라", "text": "현상 또는 조직으로부터 이탈", "isCorrect": True}
        ],
        "choices": [
            "1번: 가, 나",
            "2번: 가, 다, 라",
            "3번: 나, 다, 라",
            "4번: 가, 나, 다",
            "5번: 가, 나, 다, 라"
        ],
        "answer": "5",
        "choiceCount": 5
    },
    "0428": {
        "sourceTag": "2017 7급 국가직",
        "stemText": "핵크맨(Hackman)과 올드햄(Oldham)이 제시한 직무특성모형에서 핵심직무차원에 해당하는 것만을 모두 고른 것은?",
        "boxStatements": [
            {"id": "ㄱ", "label": "ㄱ", "text": "기술 다양성", "isCorrect": True},
            {"id": "ㄴ", "label": "ㄴ", "text": "과업 표준성", "isCorrect": False},
            {"id": "ㄷ", "label": "ㄷ", "text": "과업 정체성", "isCorrect": True},
            {"id": "ㄹ", "label": "ㄹ", "text": "과업 중요성", "isCorrect": True},
            {"id": "ㅁ", "label": "ㅁ", "text": "과업 교차성", "isCorrect": False},
            {"id": "ㅂ", "label": "ㅂ", "text": "자율성", "isCorrect": True},
            {"id": "ㅅ", "label": "ㅅ", "text": "피드백", "isCorrect": True}
        ],
        "choices": [
            "1번: ㄱ, ㄴ, ㄷ, ㄹ",
            "2번: ㄱ, ㄷ, ㄹ, ㅂ, ㅅ",
            "3번: ㄱ, ㄷ, ㅁ, ㅂ, ㅅ",
            "4번: ㄴ, ㄷ, ㄹ, ㅁ"
        ],
        "answer": "2",
        "choiceCount": 4
    },
    "0429": {
        "sourceTag": "2023 공인노무사",
        "stemText": "직무특성모형에서 중요 심리상태의 하나인 의미 충만(meaningfulness)에 영향을 미치는 핵심 직무 차원을 모두 고른 것은?",
        "boxStatements": [
            {"id": "가", "label": "가", "text": "기술다양성", "isCorrect": True},
            {"id": "나", "label": "나", "text": "과업정체성", "isCorrect": True},
            {"id": "다", "label": "다", "text": "과업중요성", "isCorrect": True},
            {"id": "라", "label": "라", "text": "자율성", "isCorrect": False},
            {"id": "마", "label": "마", "text": "피드백", "isCorrect": False}
        ],
        "choices": [
            "1번: 가, 나, 다",
            "2번: 가, 나, 라",
            "3번: 가, 다, 마",
            "4번: 나, 다, 라",
            "5번: 나, 다, 마"
        ],
        "answer": "1",
        "choiceCount": 5
    },
    "0444": {
        "sourceTag": "2010 CPA",
        "stemText": "태도, 통제의 위치, 조직몰입, 귀인이론, 강화에 관한 다음 서술 중에서 옳은 항목만을 모두 모은 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "태도의 구성요소는 인지적(cognitive) 요소, 정서적(affective) 요소, 행동의도적(behavioral intentional) 요소로 나눌 수 있다.", "isCorrect": True},
            {"id": "b", "label": "b", "text": "통제의 위치(locus of control)에 따르면 외재론자에 비해 내재론자는 성과를 결정짓는 것이 자신의 노력이라고 생각한다.", "isCorrect": True},
            {"id": "c", "label": "c", "text": "마이어(Meyer)와 알렌(Allen)은 조직몰입을 정서적(affective) 몰입, 지속적(continuance) 몰입, 규범적(normative) 몰입으로 나누어 설명한다.", "isCorrect": True},
            {"id": "d", "label": "d", "text": "켈리(Kelley)의 귀인이론(attribution theory)에서는 행동의 원인을 합의성(consensus), 특이성(distinctiveness), 일관성(consistency)의 세 가지 차원으로 구분하여 해석한다.", "isCorrect": True},
            {"id": "e", "label": "e", "text": "부정적 강화(negative reinforcement)와 긍정적 강화(positive reinforcement) 모두 바람직한 행동의 빈도를 증가시킨다.", "isCorrect": True}
        ],
        "choices": [
            "1번: a, b, d",
            "2번: a, b, c, d",
            "3번: a, b, d, e",
            "4번: b, c, d, e",
            "5번: a, b, c, d, e"
        ],
        "answer": "5",
        "choiceCount": 5
    },
    "0450": {
        "sourceTag": "2021 CPA",
        "stemText": "다음 설명 중 적절한 항목만을 모두 선택한 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "성격(personality)은 개인의 독특한 개성을 나타내는 전체적인 개념으로 선천적 유전에 의한 생리적인 것을 바탕으로 하여 개인이 사회문화환경과 작용하는 과정에서 형성된다.", "isCorrect": True},
            {"id": "b", "label": "b", "text": "욕구(needs)는 어떤 목적을 위해 개인의 행동을 일정한 방향으로 작동시키는 내적 심리상태를 의미한다.", "isCorrect": False},
            {"id": "c", "label": "c", "text": "사회적 학습이론(social learning theory)에 의하면, 학습자는 다른 사람의 어떤 행동을 관찰하여 그것이 바람직한 결과를 가져올 때에는 그 행동을 모방하고, 좋지 않은 결과를 가져올 때에는 그 같은 행동을 하지 않게 된다.", "isCorrect": True},
            {"id": "d", "label": "d", "text": "역할갈등(role conflict)은 직무에 대한 개인의 의무·권한·책임이 명료하지 않은 지각상태를 의미한다.", "isCorrect": False}
        ],
        "choices": [
            "1번: a, b",
            "2번: a, c",
            "3번: b, c",
            "4번: a, d",
            "5번: b, d"
        ],
        "answer": "2",
        "choiceCount": 5
    },
    "0460": {
        "sourceTag": "2023 CPA",
        "stemText": "다음 설명 중 적절한 항목만을 모두 선택한 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "태도(attitude)는 정서적(affective), 인지적(cognitive), 행동적(behavioral) 요소로 구성된다.", "isCorrect": True},
            {"id": "b", "label": "b", "text": "직무만족은 직무를 활용한 전문가로서의 체계적인 경력개발을 의미한다.", "isCorrect": False},
            {"id": "c", "label": "c", "text": "마키아벨리즘 성격 특성은 대인관계에 있어 속임수와 조작을 사용하는 성향을 의미한다.", "isCorrect": True},
            {"id": "d", "label": "d", "text": "켈리(Kelley)가 제시한 귀인의 결정요인은 합의성(consensus), 특이성(distinctiveness), 책무성(accountability)이다.", "isCorrect": False},
            {"id": "e", "label": "e", "text": "피그말리온 효과(Pygmalion effect)는 특정인에 대한 기대가 실제 행동 결과로 나타나게 되는 현상을 의미한다.", "isCorrect": True}
        ],
        "choices": [
            "1번: a, d",
            "2번: b, e",
            "3번: c, d",
            "4번: a, c, e",
            "5번: b, c, e"
        ],
        "answer": "4",
        "choiceCount": 5
    },
    "0461": {
        "sourceTag": "2006 CPA",
        "stemText": "동기부여(motivation) 이론 중 매슬로우의 욕구이론(need theory)에 관한 서술 중에 가장 적절한 것으로 묶인 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "하나의 욕구가 충족되면 그 다음 상위단계의 욕구를 충족시키려 한다.", "isCorrect": True},
            {"id": "b", "label": "b", "text": "상위욕구의 충족이 좌절되면 그보다 하위단계의 욕구를 충족시키려 한다.", "isCorrect": False},
            {"id": "c", "label": "c", "text": "생리적 욕구 - 안전욕구 - 존경욕구 - 사회적 욕구 - 자아실현욕구의 순서로 단계가 나누어진다.", "isCorrect": False},
            {"id": "d", "label": "d", "text": "사회적 욕구는 위생요인으로, 생리적 욕구와 안전욕구는 동기요인으로 분류하였다.", "isCorrect": False},
            {"id": "e", "label": "e", "text": "매슬로우의 5가지 욕구 중 존경(esteem), 관계(relatedness), 성장(growth) 욕구 3가지만을 고려하여 ERG이론을 만들었다.", "isCorrect": False}
        ],
        "choices": [
            "1번: a",
            "2번: a, b, c",
            "3번: b, c, d",
            "4번: d, e",
            "5번: c, d, e"
        ],
        "answer": "1",
        "choiceCount": 5
    },
    "0480": {
        "sourceTag": "2024 CPA",
        "stemText": "다음 설명 중 적절한 항목만을 모두 선택한 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "맥그리거(McGregor)의 X-Y 이론에 의하면, X이론은 인간이 기본적으로 책임을 기꺼이 수용하며 자율적으로 직무를 수행한다고 가정한다.", "isCorrect": False},
            {"id": "b", "label": "b", "text": "불공정성을 느끼는 경우, 개인은 준거인물을 변경함으로써 불균형 상태를 줄일 수 있다.", "isCorrect": True},
            {"id": "c", "label": "c", "text": "명목집단법(nominal group technique)은 의사결정 과정 동안 토론이나 대인 커뮤니케이션을 제한한다.", "isCorrect": True},
            {"id": "d", "label": "d", "text": "분배적 공정성(distributive justice)은 결과를 결정하는 데 사용되는 과정의 공정성에 대한 지각을 말한다.", "isCorrect": False}
        ],
        "choices": [
            "1번: a, b",
            "2번: a, c",
            "3번: b, c",
            "4번: a, d",
            "5번: b, c, d"
        ],
        "answer": "3",
        "choiceCount": 5
    },
    "0490": {
        "sourceTag": "CPA 기출",
        "stemText": "동기부여(motivation) 이론에 관한 다음 설명 중 옳은 것을 모두 고르면?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "매슬로(Maslow)의 욕구단계이론에서 사회적 욕구(social needs)는 존경욕구(esteem needs)보다 더 상위의 욕구이다.", "isCorrect": False},
            {"id": "b", "label": "b", "text": "허즈버그(Herzberg)의 2요인이론은 급여나 작업조건을 개선할수록 종업원들의 '만족' 수준은 높아진다고 주장한다.", "isCorrect": False},
            {"id": "c", "label": "c", "text": "알더퍼(Alderfer)의 ERG이론은 관계욕구(relatedness needs)가 제대로 충족되지 않은 경우, 존재욕구(existence needs)가 더 커질 수 있다고 주장한다.", "isCorrect": True},
            {"id": "d", "label": "d", "text": "핵크만(Hackman)과 올드햄(Oldham)의 직무특성이론(job characteristics theory)에서 개인의 성장욕구수준은 직무특성과 심리상태, 심리상태와 성과관계를 조절해주는 역할을 하고 있다.", "isCorrect": True},
            {"id": "e", "label": "e", "text": "기대이론(expectancy theory)은 개인이 기대감(expectancy), 수단성(instrumentality), 유의성(valence)을 모두 높게 지각했을 때 노력의 양을 가장 많이 투입한다고 주장한다.", "isCorrect": True}
        ],
        "choices": [
            "1번: a, b, c",
            "2번: b, c, d",
            "3번: c, d, e",
            "4번: b, d, e",
            "5번: a, c, e"
        ],
        "answer": "3",
        "choiceCount": 5
    },
    "0507": {
        "sourceTag": "CPA 기출",
        "stemText": "귀인(attribution)과 귀인오류(attribution error)에 대한 설명 중 적절한 것을 모두 선택한 것은?",
        "boxStatements": [
            {"id": "a", "label": "a", "text": "켈리(Kelley)의 귀인이론에서 특이성(distinctiveness)은 사람이 상황에 따라 얼마나 다른 방식으로 행동하는 성향이 있는가의 문제로 특이성이 높을 때 내부적으로 귀인하게 된다.", "isCorrect": False},
            {"id": "b", "label": "b", "text": "자존적 편견(self-serving bias)이란 자신의 성공은 내부에 귀인하고 자신의 실패는 외부에 귀인하는 오류를 말한다.", "isCorrect": True},
            {"id": "c", "label": "c", "text": "근원적 귀인오류(fundamental attribution error)란 다른 사람의 행동을 판단할 때 내부적 요인의 영향을 과소평가하고 외부적인 요인의 영향을 과대평가하는 경향이다.", "isCorrect": False},
            {"id": "d", "label": "d", "text": "행위자-관찰자 효과(actor-observer bias)란 다른 사람들의 행동은 상황적인 요소에 의한 것으로 판단하는 반면, 자신 즉 행위자의 행동은 기질적 요소 때문에 발생한 것으로 생각하는 것이다.", "isCorrect": False}
        ],
        "choices": [
            "1번: b",
            "2번: b, c",
            "3번: a, d",
            "4번: b, c, d",
            "5번: a, b, c"
        ],
        "answer": "1",
        "choiceCount": 5
    }
}

# ── Ground Truth for Special Cases ──
SPECIAL_CASES = {
    "0278": {
        "sourceTag": "공기업 출제경향 반영",
        "stemText": "다음 중 긍정심리자본(positive psychological capital)에 해당하지 않는 것은?",
        "typ": "객관식",
        "boxStatements": [],
        "choices": [
            "1번: 창의력(creativity)",
            "2번: 자기효능감(self-efficacy)",
            "3번: 낙관주의(optimism)",
            "4번: 희망(hope)",
            "5번: 회복 탄력성(resilience)"
        ],
        "answer": "1",
        "choiceCount": 5
    },
    "0454": {
        "sourceTag": "2005 CPA",
        "stemText": "켈리(Kelley)의 귀인이론(attribution theory)에서는 행동의 원인을 합의성(consensus), 특이성(distinctiveness), 일관성(consistency)의 세 가지 차원으로 구분하여 해석하고 있다. 다음 중 행동의 원인을 행위자의 내적(internal) 요인으로 판단하기에 가장 적절한 경우는?",
        "typ": "객관식",
        "boxStatements": [],
        "choices": [
            "1번: 합의성: 높음 / 특이성: 높음 / 일관성: 높음",
            "2번: 합의성: 높음 / 특이성: 높음 / 일관성: 낮음",
            "3번: 합의성: 낮음 / 특이성: 낮음 / 일관성: 높음",
            "4번: 합의성: 낮음 / 특이성: 높음 / 일관성: 낮음",
            "5번: 합의성: 낮음 / 특이성: 낮음 / 일관성: 낮음"
        ],
        "answer": "3",
        "choiceCount": 5
    }
}

# Canonical stems for OCR-noisy items
CANONICAL_STEM_PATCHES = {
    "0289": "인지주의(cognitivism) 학습이론에 대한 설명으로 옳지 않은 것은?",
    "0320": "조직행동에서 가치관(value)에 관한 설명으로 옳지 않은 것은?",
    "0328": "사회적 정보처리 모형에 따른 지각과정을 순서대로 연결한 것은?",
    "0330": "켈리(Kelley)의 귀인이론에 따르면 사람들은 타인의 행동의 원인을 관찰하고 이에 대처하는 경향이 있다. 만일 다른 사람의 행동이 외적 요인이라고 생각하면 그 타인에 대해 너그러운 반응을 보인다. 사람들은 어떤 경우에 이러한 반응을 하게 되는가에 대한 설명으로 가장 옳은 것은?",
    "0334": "자신이 속한 집단의 지각에 기초하여 타인을 평가하는 지각적 오류는?",
    "0337": "개인의 일부 특성을 기반으로 그 개인 전체를 평가하는 지각경향은?",
    "0344": "인사고과를 위한 평가에서 일반적으로 많이 범하게 되는 오류 중, 평가자 자신의 감정이나 경향을 피평가자의 능력을 평가하는 데 귀속시키거나 전가하는 오류는?",
    "0347": "앞의 내용들 보다는 나중에 제시된 내용을 보다 많이 기억하는 경향을 무엇이라고 하는가?",
    "0365": "맥그리거(D. McGregor)의 X, Y이론에 관한 설명으로 옳은 것은?",
    "0411": "브룸(V. Vroom)이 제시한 기대이론의 작동순서로 올바른 것은?",
    "0419": "브룸(V. Vroom)이 제시한 기대이론의 요소에 해당하지 않는 것은?",
    "0433": "동기부여의 연구자와 그 이론의 연결이 옳지 않은 것은?",
    "0445": "조직에서 개인의 태도와 행동에 관한 설명으로 가장 적절한 것은?",
    "0447": "조직에서 개인의 행동에 관한 설명으로 가장 적절하지 않은 것은?",
    "0453": "감정, 지각 및 가치관에 관한 설명으로 가장 적절하지 않은 것은?",
    "0464": "핵크맨(Hackman)과 올드햄(Oldham)이 주장한 직무특성이론(job characteristics theory)에 관한 설명으로 가장 적절하지 않은 것은?",
    "0468": "동기부여(motivation) 이론에 관한 설명으로 가장 적절한 것은?",
    "0478": "동기부여 이론과 성격에 관한 설명으로 가장 적절하지 않은 것은?",
    "0483": "학습(learning)에 대한 다음 설명 중 가장 적절하지 않은 것은?",
    "0485": "성격과 지각(perception)에 대한 설명 중 가장 적절하지 않은 것은?",
    "0496": "조직행동의 개인차원 변수에 관한 다음 설명 중 가장 적절하지 않은 것은?",
    "0497": "동기부여(motivation) 이론에 대한 다음 설명 중 가장 적절하지 않은 것은?",
    "0499": "조직에서 개인의 행동과 관련한 다음 설명 중 적절하지 않은 것은?",
    "0504": "동기부여(motivation)에 대한 다음 설명 가운데 가장 적절한 것은?",
    "0506": "학습, 태도, 가치관에 대한 다음 설명 중 가장 적절하지 않은 것은?",
}

# Canonical choices for 2-column or OCR-noisy items
CANONICAL_CHOICE_PATCHES = {
    "0282": ["1번: 긍정적 강화", "2번: 소거", "3번: 벌", "4번: 부정적 강화", "5번: 소극적 강화"],
    "0283": ["1번: 고정간격법", "2번: 변동간격법", "3번: 고정비율법", "4번: 변동비율법", "5번: 연속강화법"],
    "0284": ["1번: 행동수정기법", "2번: 형태적 접근기법", "3번: 의사거래분석법", "4번: 감수성 훈련기법", "5번: 델파이법"],
    "0286": ["1번: 적극적 강화", "2번: 소극적 강화", "3번: 소거", "4번: 벌", "5번: 연속적 강화계획"],
    "0291": [
        "1번: ㄱ- 감정적 요소 / ㄴ- 인지적 요소 / ㄷ- 행동적 요소",
        "2번: ㄱ- 긍정적 요소 / ㄴ- 행동적 요소 / ㄷ- 인지적 요소",
        "3번: ㄱ- 인지적 요소 / ㄴ- 행동적 요소 / ㄷ- 감정적 요소",
        "4번: ㄱ- 인지적 요소 / ㄴ- 감정적 요소 / ㄷ- 행동적 요소",
        "5번: ㄱ- 행동적 요소 / ㄴ- 감정적 요소 / ㄷ- 인지적 요소"
    ],
    "0295": ["1번: 주장(voice)", "2번: 이탈(exit)", "3번: 일탈(deviance)", "4번: 충성(loyalty)", "5번: 방관(neglect)"],
    "0298": ["1번: 정서적 요소", "2번: 인지적 요소", "3번: 관계적 요소", "4번: 행위적 요소"],
    "0308": ["1번: 조화성", "2번: 신경성", "3번: 성실성", "4번: 외향성", "5번: 개방성"],
    "0322": ["1번: 야망(ambitious)", "2번: 용기(courageous)", "3번: 청결(clean)", "4번: 자유(freedom)", "5번: 복종(obedient)"],
    "0328": [
        "1번: 선택적 주의/이해 - 부호화/단순화 - 인출/반응 - 저장/보유",
        "2번: 선택적 주의/이해 - 부호화/단순화 - 저장/보유 - 인출/반응",
        "3번: 부호화/단순화 - 선택적 주의/이해 - 저장/보유 - 인출/반응",
        "4번: 부호화/단순화 - 저장/보유 - 선택적 주의/이해 - 인출/반응",
        "5번: 부호화/단순화 - 인출/반응 - 선택적 주의/이해 - 저장/보유"
    ],
    "0330": [
        "1번: 타인 행동의 높은 특이성",
        "2번: 타인 행동의 다른 사람들과의 낮은 합의성",
        "3번: 타인 행동의 높은 일관성",
        "4번: 타인 행동의 높은 개인성"
    ],
    "0334": ["1번: 스테레오타입", "2번: 후광효과", "3번: 대조효과", "4번: 최근효과", "5번: 자존적 편견"],
    "0335": ["1번: 감성적 몰입", "2번: 자기실현적 예언", "3번: 후광효과", "4번: 자존적 편견", "5번: 스테레오타이핑"],
    "0337": ["1번: 스테레오타입", "2번: 투사", "3번: 기대효과", "4번: 최근효과", "5번: 후광효과"],
    "0338": ["1번: 고정관념", "2번: 자존적 편견", "3번: 최근효과", "4번: 후광효과", "5번: 투사"],
    "0340": ["1번: 후광효과", "2번: 관대화 경향", "3번: 중심화 경향", "4번: 가혹화 경향", "5번: 스테레오타입"],
    "0345": ["1번: 시간적 오류(recency errors)", "2번: 논리적 오류(logical errors)", "3번: 대비 오류(contrast errors)", "4번: 상동적 오류(stereotyping errors)"],
    "0347": ["1번: 스테레오타이핑", "2번: 대비효과", "3번: 주관의 객관화", "4번: 후광효과", "5번: 최근 효과"],
    "0350": [
        "1번: 매그리거(McGregor)의 X이론",
        "2번: 피그말리온 효과(Pygmalion effect)",
        "3번: 자기충족적 예언(self-fulfilling prophecy)",
        "4번: 갈라테아 효과(Galatea effect)",
        "5번: 긍정적 강화(positive reinforcement)"
    ],
    "0352": ["1번: 초두효과", "2번: 대조효과", "3번: 관대화경향", "4번: 가혹화경향", "5번: 중심화경향"],
    "0364": ["1번: 매슬로우 - ERG이론", "2번: 알더퍼 - 욕구단계이론", "3번: 아담스 - 공정성이론", "4번: 맥클리랜드 - 2요인이론", "5번: 허츠버그 - 성취동기이론"],
    "0371": ["1번: 생리적 욕구", "2번: 안전 욕구", "3번: 사회적 욕구", "4번: 존경 욕구", "5번: 자아실현 욕구"],
    "0377": ["1번: 성취감", "2번: 임금", "3번: 책임감", "4번: 발전가능성", "5번: 일 그 자체"],
    "0387": ["1번: 기대이론", "2번: ERG이론", "3번: 공정성이론", "4번: 직무특성이론", "5번: 목표설정이론"],
    "0395": ["1번: 기대이론", "2번: 강화이론", "3번: 공정성이론", "4번: 목표설정이론", "5번: 성취동기이론"],
    "0409": ["1번: 인지부조화이론", "2번: 목표설정이론", "3번: 귀인이론", "4번: 기대이론", "5번: 공정성이론"],
    "0411": [
        "1번: 기대감 - 수단성 - 유의성",
        "2번: 기대감 - 유의성 - 수단성",
        "3번: 수단성 - 유의성 - 기대감",
        "4번: 수단성 - 기대감 - 유의성",
        "5번: 유의성 - 수단성 - 기대감"
    ],
    "0419": ["1번: 기대감", "2번: 수단성", "3번: 유의성", "4번: 만족도"],
    "0421": ["1번: 목표설정이론", "2번: 강화이론", "3번: 인지평가이론", "4번: 공정성이론", "5번: 기대이론"],
    "0423": ["1번: 합의성", "2번: 특이성", "3번: 일관성", "4번: 독특성", "5번: 보편성"],
    "0433": [
        "1번: 브룸(Vroom) - 기대이론",
        "2번: 아담스(Adams) - 공정성이론",
        "3번: 허즈버그(Herzberg) - 2요인이론",
        "4번: 로크(Locke) - 목표설정이론",
        "5번: 앨더퍼(Alderfer) - 2요인이론"
    ],
    "0469": [
        "1번: 목표의 구체성",
        "2번: 목표의 난이도",
        "3번: 목표에 대한 피드백",
        "4번: 목표설정에 대한 참여",
        "5번: 목표의 보상 연계성"
    ],
}

def extract_stem_robust(qid, lines):
    if qid in CANONICAL_STEM_PATCHES:
        return CANONICAL_STEM_PATCHES[qid]
    if qid in BOXED_GROUND_TRUTH:
        return BOXED_GROUND_TRUTH[qid]["stemText"]
    if qid in SPECIAL_CASES:
        return SPECIAL_CASES[qid]["stemText"]
        
    if not lines:
        return ""
        
    t0 = lines[0]['text'].strip()
    is_qnum = False
    if len(t0) <= 8 and (re.search(r'^\s*0?[2-5]', t0) or t0 in ['1', '1 1', '사리', '하스', '자']):
        if not ('?' in t0 or '것은' in t0):
            is_qnum = True
            
    idx = 1 if is_qnum else 0
    
    # Check source tag line
    if idx < len(lines):
        t1 = lines[idx]['text'].strip()
        is_src = False
        if any(kw in t1 for kw in EXAM_KEYWORDS) or YEAR_PAT.search(t1) or '반영' in t1 or '복원' in t1:
            is_src = True
        if '?' in t1 or '것은' in t1 or '설명이다' in t1:
            is_src = False
        if is_src:
            idx += 1
            
    stem_lines = []
    for i in range(idx, len(lines)):
        t = lines[i]['text'].strip()
        if re.match(r'^[<〈\[]?\s*보기\s*[>〉\]]?$', t):
            break
        if re.match(r'^(?:[①-⑤]|0\s|㉨|㉦|@\s|㉭|[1-5]\s*[\.\)])', t):
            break
        stem_lines.append(t)
        if STEM_END_PAT.search(t):
            break
            
    stem = " ".join(stem_lines).strip()
    # Normalize question mark ending
    if stem and not stem.endswith(('?', '.', '!', ':', '것은?')):
        if stem.endswith(('으7', '거으2', '거으7', '은2', '은7', '것은7')):
            stem = re.sub(r'(?:으[72]|거으[72]|은[27]|것은7)$', '것은?', stem)
        elif stem.endswith('것은('):
            stem = re.sub(r'것은\($', '것은?', stem)
        elif stem.endswith('않•'):
            stem = re.sub(r'않•$', '않은 것은?', stem)
        elif not stem.endswith('?'):
            stem = stem + '?'
    return stem

def extract_source_tag(qid, lines):
    if qid in BOXED_GROUND_TRUTH:
        return BOXED_GROUND_TRUTH[qid]["sourceTag"]
    if qid in SPECIAL_CASES:
        return SPECIAL_CASES[qid]["sourceTag"]
    if qid == "0347":
        return "2020 코레일 수송직렬 복원"
    if qid == "0388":
        return "2022 경영지도사"
        
    if not lines:
        return ""
        
    t0 = lines[0]['text'].strip()
    is_qnum = False
    if len(t0) <= 8 and (re.search(r'^\s*0?[2-5]', t0) or t0 in ['1', '1 1', '사리', '하스', '자']):
        if not ('?' in t0 or '것은' in t0):
            is_qnum = True
            
    idx = 1 if is_qnum else 0
    if idx < len(lines):
        t1 = lines[idx]['text'].strip()
        is_src = False
        if any(kw in t1 for kw in EXAM_KEYWORDS) or YEAR_PAT.search(t1) or '반영' in t1 or '복원' in t1:
            is_src = True
        if '?' in t1 or '것은' in t1 or '설명이다' in t1:
            is_src = False
        if is_src:
            return normalize_source_tag(t1)
            
    return ""

def extract_choices(qid, lines, img_w, expected_count, existing_choices):
    if qid in BOXED_GROUND_TRUTH:
        return BOXED_GROUND_TRUTH[qid]["choices"]
    if qid in SPECIAL_CASES:
        return SPECIAL_CASES[qid]["choices"]
    if qid in CANONICAL_CHOICE_PATCHES:
        return CANONICAL_CHOICE_PATCHES[qid]
        
    # Check if existing choices in cards-data.json are complete and non-dummy
    if existing_choices and len(existing_choices) == expected_count:
        is_dummy = all(len(re.sub(r'^[1-5]번:\s*', '', opt).strip()) == 0 for opt in existing_choices)
        if not is_dummy:
            # Check for truncations in existing choices
            # If not truncated, we can use them directly or enhance them
            cleaned_existing = []
            for idx, ch in enumerate(existing_choices, 1):
                txt = re.sub(r'^[1-5]번:\s*', '', ch).strip()
                txt = clean_choice_body(txt)
                cleaned_existing.append(f"{idx}번: {txt}")
            # Verify no empty choice
            if all(len(c.split(':', 1)[1].strip()) > 0 for c in cleaned_existing):
                return cleaned_existing

    # Fall back to geometric OCR sorting
    choice_lines = []
    # Find start of choices
    choice_start_found = False
    for l in lines:
        t = l['text'].strip()
        if CHOICE_MARKER_PAT.match(t):
            choice_start_found = True
        if choice_start_found:
            choice_lines.append(l)
            
    # Sort geometrically if right-column elements exist
    has_right_col = any(l.get('rect', {}).get('x', 0) > img_w * 0.45 for l in choice_lines)
    if has_right_col:
        choice_lines = sort_lines_reading_order(choice_lines)
        
    options = []
    cur_opt = []
    for l in choice_lines:
        txt = l['text'].strip()
        if txt in ['가치관', '동기부여', '지각', '태도', '성격', '동기부여 • 과정이론']:
            continue
        if CHOICE_MARKER_PAT.match(txt):
            if cur_opt:
                options.append(" ".join(cur_opt))
                cur_opt = []
            cur_opt.append(clean_choice_body(txt))
        else:
            if cur_opt:
                cur_opt.append(txt)
    if cur_opt:
        options.append(" ".join(cur_opt))
        
    formatted = []
    for idx, opt in enumerate(options[:expected_count], 1):
        clean_text = clean_choice_body(opt)
        formatted.append(f"{idx}번: {clean_text}")
        
    # If count matches, return
    if len(formatted) == expected_count:
        return formatted
        
    # Fallback to existing choices
    fallback = []
    for idx in range(1, expected_count + 1):
        if idx <= len(existing_choices) and len(re.sub(r'^[1-5]번:\s*', '', existing_choices[idx-1]).strip()) > 0:
            c_text = clean_choice_body(re.sub(r'^[1-5]번:\s*', '', existing_choices[idx-1]).strip())
            fallback.append(f"{idx}번: {c_text}")
        elif idx <= len(options):
            c_text = clean_choice_body(options[idx-1])
            fallback.append(f"{idx}번: {c_text}")
        else:
            fallback.append(f"{idx}번: 선택지 {idx}")
    return fallback

def run_extraction():
    print("Loading datasets...")
    with open(CARDS_DATA_PATH, "r", encoding="utf-8") as f:
        cards_raw = json.load(f)["cards"]
    cards_dict = {c["qid"]: c for c in cards_raw if "0277" <= c["qid"] <= "0507"}
    
    # Load OCR Cache or execute WinOCR
    raw_ocr = {}
    if os.path.exists(OCR_CACHE_PATH):
        print(f"Loading OCR cache from {OCR_CACHE_PATH}...")
        with open(OCR_CACHE_PATH, "r", encoding="utf-8") as f:
            raw_ocr = json.load(f)
            
    # Always ensure 0374 is OCR'd
    img_0374_path = os.path.join(IMAGES_DIR, "_jh_q_0374.webp")
    if os.path.exists(img_0374_path) and os.path.getsize(img_0374_path) > 0:
        if "0374" not in raw_ocr or raw_ocr["0374"].get("status") != "ok":
            print("Running WinOCR on recovered _jh_q_0374.webp...")
            import winocr
            im_0374 = Image.open(img_0374_path)
            res = winocr.recognize_pil_sync(im_0374, lang="ko")
            lines_0374 = []
            for l in res.get("lines", []):
                words = l.get("words", [])
                if words:
                    min_x = min(w["bounding_rect"]["x"] for w in words)
                    min_y = min(w["bounding_rect"]["y"] for w in words)
                    max_x = max(w["bounding_rect"]["x"] + w["bounding_rect"]["width"] for w in words)
                    max_y = max(w["bounding_rect"]["y"] + w["bounding_rect"]["height"] for w in words)
                    rect = {"x": round(min_x, 1), "y": round(min_y, 1), "w": round(max_x - min_x, 1), "h": round(max_y - min_y, 1)}
                else:
                    rect = None
                lines_0374.append({"text": l.get("text", ""), "rect": rect})
            raw_ocr["0374"] = {
                "status": "ok",
                "img_width": im_0374.width,
                "img_height": im_0374.height,
                "lines": lines_0374
            }

    extracted_output = {}
    total_count = 0
    boxed_count = 0
    std_count = 0

    print("Extracting Chapter 02 items (0277 ~ 0507)...")
    for qnum in range(277, 508):
        qid = f"{qnum:04d}"
        cid = f"mgmt_{qid}"
        card = cards_dict[qid]
        
        # Ground truth answer from back
        back_html = card.get("back", "")
        ans_m = re.search(r'data-correct="(\d+)"', back_html)
        assert ans_m, f"[{cid}] data-correct missing in back HTML!"
        answer = ans_m.group(1)
        
        # Expected choices count
        if qid in ["0331", "0429"]:
            expected_choices_count = 5
        elif qid in BOXED_GROUND_TRUTH:
            expected_choices_count = BOXED_GROUND_TRUTH[qid]["choiceCount"]
        elif qid in SPECIAL_CASES:
            expected_choices_count = SPECIAL_CASES[qid]["choiceCount"]
        elif qid in CANONICAL_CHOICE_PATCHES:
            expected_choices_count = len(CANONICAL_CHOICE_PATCHES[qid])
        else:
            btn_matches = re.findall(r'<button\s+[^>]*class="[^"]*mcq-option', card.get("front", ""))
            expected_choices_count = len(btn_matches) if len(btn_matches) in [4, 5] else 5
            
        ocr_data = raw_ocr.get(qid, {})
        lines = ocr_data.get("lines", [])
        img_w = ocr_data.get("img_width", 1400)
        
        # 1. Stem Text
        stem_text = extract_stem_robust(qid, lines)
        assert len(stem_text.strip()) >= 5, f"[{cid}] Stem text is empty or too short: {stem_text}"
        
        # 2. Source Tag
        source_tag = extract_source_tag(qid, lines)
        
        # 3. Typ & Box Statements
        if qid in BOXED_GROUND_TRUTH:
            typ = "박스선택형"
            box_statements = BOXED_GROUND_TRUTH[qid]["boxStatements"]
            boxed_count += 1
        elif qid in SPECIAL_CASES:
            typ = SPECIAL_CASES[qid]["typ"]
            box_statements = SPECIAL_CASES[qid]["boxStatements"]
            std_count += 1
        else:
            typ = "객관식"
            box_statements = []
            std_count += 1
            
        # 4. Choices
        existing_choices = card.get("choices", [])
        choices = extract_choices(qid, lines, img_w, expected_choices_count, existing_choices)
        
        assert len(choices) == expected_choices_count, f"[{cid}] Choices count mismatch: {len(choices)} != {expected_choices_count}"
        assert int(answer) <= expected_choices_count, f"[{cid}] Answer ({answer}) > choiceCount ({expected_choices_count})"
        
        record = {
            "id": cid,
            "qid": qid,
            "sourceTag": source_tag,
            "stemText": stem_text,
            "typ": typ,
            "boxStatements": box_statements,
            "choices": choices,
            "answer": answer,
            "choiceCount": expected_choices_count
        }
        extracted_output[cid] = record
        total_count += 1

    print(f"\nExtraction completed:")
    print(f"  Total items: {total_count} (expected 231)")
    print(f"  Boxed questions: {boxed_count} (expected 21)")
    print(f"  Standard MCQ: {std_count} (expected 210)")

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(extracted_output, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved artifact to: {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    run_extraction()
