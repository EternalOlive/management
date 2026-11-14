# -*- coding: utf-8 -*-
"""
전수환 경영학 카드앱 UI/UX 전면 개편:
1. 'ㄱ다음에 엔터' 줄바꿈 완전 제거 -> 가로 한 줄 flex row 인셋 카드 스타일 적용
2. '문제 번호 뒤 여백' 완전 제거 + 문제 번호와 출처 뱃지를 한 줄(question-header-row)에 나란히 인라인 배치
3. 박스형 문제에서 우측/하단의 객관식 번호 조합 버튼(1 ㄱ,ㄴ 등) 완전 제거 (100% 순수 RemNote 모드)
4. 스플릿 모드에서도 박스형 카드가 단일 컬럼으로 깔끔하게 집중되도록 레이아웃 정돈
5. 9개 박스형 문제 및 cards-data.json, cards.html 전수 적용
"""
import json
import re

MANAGEMENT_DIR = r'c:\Users\yoon\Downloads\management-cards'
MEMORY_DIR = r'c:\Users\yoon\Downloads\memory-cards-main\memory-cards-main'

# 1. cards.html에 완전무결한 CSS 삽입
perfect_css = """
/* ══════════ [UI/UX 전면 개선] 문제 헤더 한 줄 통합 & RemNote 진술문 카드 ══════════ */
.question-header-row {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  margin-bottom: 12px !important;
  width: fit-content !important;
}
.question-number {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  height: 26px !important;
  line-height: 26px !important;
  padding: 0 10px !important;
  margin: 0 !important;
  border-radius: var(--r-pill, 999px) !important;
  background: var(--c-fill) !important;
  color: var(--c-sec) !important;
  font-size: 12.5px !important;
  font-weight: 700 !important;
  border: 0.5px solid var(--c-sep) !important;
  width: fit-content !important;
  flex: none !important;
  user-select: none !important;
}
.source-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  height: 26px !important;
  line-height: 26px !important;
  padding: 0 10px !important;
  margin: 0 !important;
  border-radius: var(--r-pill, 999px) !important;
  background: var(--c-acc-tint) !important;
  color: var(--c-acc) !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  border: 0.5px solid transparent !important;
  width: fit-content !important;
  flex: none !important;
  user-select: none !important;
}
.mcq-card.split-layout .question-header-row {
  grid-area: head !important;
  margin-bottom: 10px !important;
}

/* ── RemNote 진술문(ㄱ, ㄴ, ㄷ, ㄹ) 인셋 카드 (가로 한 줄 flex row) ── */
.mcq-statement-box {
  margin: 16px 0 20px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
}
.mcq-statement-item {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 12px 16px !important;
  background: var(--c-card) !important;
  border: 0.5px solid var(--c-sep) !important;
  border-radius: var(--r-cell, 12px) !important;
  box-shadow: var(--sh-card) !important;
  cursor: pointer !important;
  user-select: none !important;
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease !important;
  box-sizing: border-box !important;
  text-align: left !important;
}
.mcq-statement-item:hover {
  background: var(--c-fill) !important;
}
.mcq-statement-item:active {
  transform: scale(0.995) !important;
}
.mcq-stmt-badge {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 26px !important;
  height: 26px !important;
  border-radius: var(--r-pill, 999px) !important;
  background: var(--c-fill) !important;
  color: var(--c-label) !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}
.mcq-stmt-content {
  flex: 1 !important;
  min-width: 0 !important;
}
.mcq-stmt-text {
  font-size: 16px !important;
  line-height: 1.55 !important;
  color: var(--c-label) !important;
  word-break: keep-all !important;
  margin: 0 !important;
}
.mcq-stmt-reason {
  margin-top: 4px !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: var(--c-again) !important;
}
.mcq-stmt-status {
  flex-shrink: 0 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  padding: 4px 10px !important;
  border-radius: var(--r-pill, 999px) !important;
  background: var(--c-fill) !important;
  color: var(--c-sec) !important;
  transition: all 0.15s ease !important;
}

/* 선택 상태 */
.mcq-statement-item.selected {
  background: var(--c-acc-tint) !important;
  border-color: var(--c-acc) !important;
  box-shadow: 0 0 0 1px var(--c-acc) !important;
}
.mcq-statement-item.selected .mcq-stmt-badge {
  background: var(--c-acc) !important;
  color: #fff !important;
}
.mcq-statement-item.selected .mcq-stmt-text {
  color: var(--c-acc) !important;
  font-weight: 600 !important;
}
.mcq-statement-item.selected .mcq-stmt-status {
  background: var(--c-acc) !important;
  color: #fff !important;
}

/* 정답/오답 결과 상태 */
.mcq-statement-item.result-hit {
  background: var(--c-good-bg) !important;
  border-color: var(--c-good) !important;
  box-shadow: 0 0 0 1px var(--c-good) !important;
}
.mcq-statement-item.result-hit .mcq-stmt-badge,
.mcq-statement-item.result-hit .mcq-stmt-status {
  background: var(--c-good) !important;
  color: #fff !important;
}

.mcq-statement-item.result-miss {
  background: var(--c-again-bg) !important;
  border-color: var(--c-again) !important;
  box-shadow: 0 0 0 1px var(--c-again) !important;
}
.mcq-statement-item.result-miss .mcq-stmt-badge,
.mcq-statement-item.result-miss .mcq-stmt-status {
  background: var(--c-again) !important;
  color: #fff !important;
}

.mcq-statement-item.result-missed {
  background: var(--c-card) !important;
  border: 1.5px dashed var(--c-good) !important;
}
.mcq-statement-item.result-missed .mcq-stmt-badge {
  border: 1px solid var(--c-good) !important;
  color: var(--c-good) !important;
}
.mcq-statement-item.result-missed .mcq-stmt-status {
  background: var(--c-good-bg) !important;
  color: var(--c-good) !important;
}

.mcq-statement-item.result-passed {
  opacity: 0.45 !important;
  background: var(--c-fill) !important;
  border-color: var(--c-sep) !important;
}
.mcq-statement-item.result-passed:hover {
  opacity: 0.85 !important;
}

/* 박스형 진술문 문항일 때 하단/우측의 번호 조합 버튼(1 ㄱ,ㄴ 등) 완전 숨김 */
.mcq-card:has(.mcq-statement-box) .mcq-options,
.mcq-card.has-statements .mcq-options,
.mcq-card[data-mode="statement-multi"] .mcq-options {
  display: none !important;
}

/* 스플릿 레이아웃일 때도 진술문 카드가 있으면 단일 집중 컬럼으로 렌더링 */
.mcq-card.split-layout:has(.mcq-statement-box),
.mcq-card.split-layout.has-statements {
  display: block !important;
  max-width: 900px !important;
}
.mcq-card.split-layout:has(.mcq-statement-box) .mcq-stem,
.mcq-card.split-layout.has-statements .mcq-stem {
  border-right: none !important;
  padding-right: 0 !important;
}
"""

def patch_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # CSS 추가
    if '/* ══════════ [UI/UX 전면 개선] 문제 헤더 한 줄 통합' not in html:
        target = '</style>'
        html = html.replace(target, perfect_css + '\n' + target, 1)
        print(f"Injected perfect_css into {file_path}")

    # rebuildCardHtml 수정: question-header-row 생성
    old_rebuild_head = """c.front = `<div class="mcq-card" data-qid="${qNum}" data-shuffle="false">
  <div class="question-number">문제 ${qNum}</div>
  <div class="mcq-stem">
    ${sourceBadge}<div class="stem-ocr-text">${escapeHtml(c.stemText || '')}</div>${imgHtml}
  </div>"""

    new_rebuild_head = """const hasStmts = c.boxStatements && c.boxStatements.length > 0;
  const cardClasses = ['mcq-card'];
  if (hasStmts) cardClasses.push('has-statements');

  c.front = `<div class="${cardClasses.join(' ')}" data-qid="${qNum}" data-shuffle="false" ${hasStmts ? 'data-mode="statement-multi"' : ''}>
  <div class="question-header-row">
    <span class="question-number">문제 ${qNum}</span>
    ${sourceBadge}
  </div>
  <div class="mcq-stem">
    <div class="stem-ocr-text">${escapeHtml(c.stemText || '')}</div>${stmtBoxHtml}${imgHtml}
  </div>`;"""

    # rebuildCardHtml 내부 템플릿 교체
    if 'class="question-header-row"' not in html:
        # replace in rebuildCardHtml
        pattern = r'c\.front\s*=\s*`<div class="mcq-card"[^>]*>[\s\S]*?<div class="stem-ocr-text">[\s\S]*?<\/div>\s*<\/div>'
        match = re.search(pattern, html)
        if match:
            # We can replace the snippet
            html = html[:match.start()] + new_rebuild_head + html[match.end():]
            print(f"Updated rebuildCardHtml front template in {file_path}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

for p in [f"{MANAGEMENT_DIR}/cards.html", f"{MEMORY_DIR}/cards.html"]:
    patch_html(p)

# 2. cards-data.json의 9개 박스형 문제 및 모든 문제의 front를 question-header-row 구조로 일괄 정돈
def patch_cards_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for c in data['cards']:
        qid = c.get('qid')
        front = c.get('front', '')
        source = c.get('sourceTag', '')
        box_stmts = c.get('boxStatements')

        # 1) question-number와 source-badge를 question-header-row로 한 줄 통합
        # 기존: <div class="question-number">...</div>\n  <div class="mcq-stem">\n    <span class="source-badge">...</span>
        has_src = bool(source)
        src_html = f'<span class="source-badge">{source}</span>' if has_src else ''
        q_num = qid or (c.get('id', '').replace('mgmt_', ''))
        new_header = f'<div class="question-header-row">\n    <span class="question-number">문제 {q_num}</span>\n    {src_html}\n  </div>'

        # Remove old source-badge inside mcq-stem
        front = re.sub(r'<span class="source-badge">.*?</span>\s*', '', front)
        # Replace old question-number with new question-header-row
        front = re.sub(r'<div class="question-number">.*?</div>\s*', new_header + '\n  ', front)
        front = re.sub(r'<div class="question-header-row">[\s\S]*?</div>\s*', new_header + '\n  ', front, count=1)

        # 2) 만약 boxStatements가 있거나 0057, 0010, 0014 등 박스형 문항인 경우
        if qid == '0057':
            c['boxStatements'] = [
                { 'id': 'ㄱ', 'label': 'ㄱ', 'text': '출자에 있어서는 물적 재산, 인적 신용, 노무 등이 모두 가능하다.', 'isCorrect': True, 'desc': '합명회사는 무한책임사원으로만 구성되어 신용·노무출자 가능' },
                { 'id': 'ㄴ', 'label': 'ㄴ', 'text': '합명회사는 합자회사에 비해 자본 조달이 용이하다.', 'isCorrect': False, 'reason': '합자회사가 유한책임사원을 둘 수 있어 자본조달이 더 용이함' },
                { 'id': 'ㄷ', 'label': 'ㄷ', 'text': '합명회사는 무한책임사원과 유한책임사원으로 구성된다.', 'isCorrect': False, 'reason': '무한+유한은 합자회사이며, 합명회사는 전원 무한책임사원' },
                { 'id': 'ㄹ', 'label': 'ㄹ', 'text': '합명회사는 대자본을 필요로 하는 회사에는 부적당하다.', 'isCorrect': True, 'desc': '소규모 인적 회사로 대자본 조달에는 부적당함' }
            ]
            c['typ'] = '박스선택형'
            c['correctChoices'] = ['ㄱ', 'ㄹ']
            box_stmts = c['boxStatements']

        if box_stmts and len(box_stmts) > 0:
            c['typ'] = '박스선택형'
            # 진술문 박스 생성 (엔터 줄바꿈 없는 가로 한 줄 flex row 인셋 카드)
            items_html = ''
            for s in box_stmts:
                lbl = s.get('label') or s.get('id')
                items_html += f"""      <div class="mcq-statement-item" data-stmt="{lbl}">
        <span class="mcq-stmt-badge">{lbl}</span>
        <div class="mcq-stmt-content">
          <div class="mcq-stmt-text">{s.get('text', '')}</div>
        </div>
        <span class="mcq-stmt-status">선택</span>
      </div>\n"""

            stmt_box = f"""    <div class="mcq-statement-box">
{items_html}    </div>"""

            # mcq-card 클래스에 has-statements 부여
            front = re.sub(r'class="mcq-card([^"]*)"', r'class="mcq-card has-statements\1" data-mode="statement-multi"', front)
            
            # Remove any old mcq-statement-box
            front = re.sub(r'<div class="mcq-statement-box">[\s\S]*?</div>\s*</div>', '</div>', front)

            # Insert new clean stmt_box inside mcq-stem right below stem-ocr-text
            stem_ocr_match = re.search(r'<div class="stem-ocr-text">.*?</div>', front, flags=re.DOTALL)
            if stem_ocr_match:
                front = front[:stem_ocr_match.end()] + '\n' + stmt_box + front[stem_ocr_match.end():]

        c['front'] = front
        count += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {count} cards in {file_path}")

for p in [f"{MANAGEMENT_DIR}/cards-data.json", f"{MEMORY_DIR}/cards-data.json"]:
    patch_cards_data(p)

print("All redesigns applied successfully!")
