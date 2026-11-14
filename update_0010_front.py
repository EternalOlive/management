# -*- coding: utf-8 -*-
import json

paths = [
    r'c:\Users\yoon\Downloads\management-cards\cards-data.json',
    r'c:\Users\yoon\Downloads\memory-cards-main\memory-cards-main\cards-data.json'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for c in data['cards']:
        if c['id'] == 'mgmt_0010':
            c['typ'] = '박스선택형'
            items_html = ''
            for s in c['boxStatements']:
                items_html += f"""      <div class="mcq-statement-item" data-stmt="{s['label']}">
        <span class="mcq-stmt-badge">{s['label']}</span>
        <div class="mcq-stmt-content">
          <div class="mcq-stmt-text">{s['text']}</div>
        </div>
        <span class="mcq-stmt-status">선택</span>
      </div>\n"""
            
            c['front'] = f"""<div class="mcq-card" data-qid="0010" data-shuffle="false" data-mode="statement-multi">
  <div class="question-number">문제 0010 · RemNote 다중선택</div>
  <div class="mcq-stem">
    <span class="source-badge">2021 7급 서울시</span>
    <div class="stem-ocr-text"><보기>에서 전문경영자의 장점을 모두 고른 것은?</div>
    <div class="mcq-statement-box">
      <div class="mcq-statement-header">
        <span>진술문 보기 (탭하여 옳은 선지 중복 선택)</span>
        <span class="mcq-stmt-hint">단축키: ㄱ/ㄴ/ㄷ/ㄹ 또는 1~4</span>
      </div>
{items_html}    </div>
  </div>
  <div class="mcq-options">
    <button type="button" class="mcq-option text-option" data-original="1"><span class="mcq-label">①</span><span class="mcq-choice-text">ㄱ, ㄷ</span></button><button type="button" class="mcq-option text-option" data-original="2"><span class="mcq-label">②</span><span class="mcq-choice-text">ㄱ, ㄹ</span></button><button type="button" class="mcq-option text-option" data-original="3"><span class="mcq-label">③</span><span class="mcq-choice-text">ㄴ, ㄷ</span></button><button type="button" class="mcq-option text-option" data-original="4"><span class="mcq-label">④</span><span class="mcq-choice-text">ㄴ, ㄹ</span></button>
  </div>
  <div class="mcq-help">각 진술문을 탭하여 중복 선택하세요 · Space: 정답 확인</div>
</div>"""

            c['back'] = """<div class="mcq-result" data-qid="0010" data-correct="4">
  <div class="mcq-answer-badge">정답: <span class="mcq-current-answer">④ ㄴ, ㄹ</span></div>
  <div class="mcq-stmt-summary"></div>
  <div class="mcq-explanation">
    <div class="mcq-exp-title">상세 해설</div>
    <div class="mcq-exp-text">
      • <b>ㄱ (X):</b> 과감한 경영혁신과 신속한 결단은 소유경영자의 특징입니다.<br>
      • <b>ㄴ (O):</b> 경영의 전문화와 합리적 의사결정은 전문경영자의 대표적인 장점입니다.<br>
      • <b>ㄷ (X):</b> 환경변화에 대한 빠른 적응은 단독 의사결정이 가능한 소유경영자의 장점입니다.<br>
      • <b>ㄹ (O):</b> 전문경영인은 무리한 모험보다는 체계적인 관리를 통해 회사의 안정적 성장을 도모합니다.
    </div>
  </div>
</div>"""
            print(f'Updated mgmt_0010 front and back in {p}')
            break
            
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print('Done!')
