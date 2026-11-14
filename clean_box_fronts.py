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
        if c.get('boxStatements') and len(c['boxStatements']) > 0:
            qid = c.get('qid')
            q_num = qid or (c.get('id', '').replace('mgmt_', ''))
            source = c.get('sourceTag', '')
            src_html = f'<span class="source-badge">{source}</span>' if source else ''
            
            items_html = ''
            for s in c['boxStatements']:
                lbl = s.get('label') or s.get('id')
                items_html += f"""      <div class="mcq-statement-item" data-stmt="{lbl}">
        <span class="mcq-stmt-badge">{lbl}</span>
        <div class="mcq-stmt-content">
          <div class="mcq-stmt-text">{s.get('text', '')}</div>
        </div>
        <span class="mcq-stmt-status">선택</span>
      </div>\n"""
            
            # choices HTML
            choices_html = ''
            for idx, ch in enumerate(c.get('choices', [])):
                num = idx + 1
                circles = ['①', '②', '③', '④', '⑤']
                lbl = circles[idx] if idx < 5 else f'{num}.'
                txt = ch.replace(f'{num}번:', '').strip()
                choices_html += f'<button type="button" class="mcq-option text-option" data-original="{num}"><span class="mcq-label">{lbl}</span><span class="mcq-choice-text">{txt}</span></button>'
                
            c['front'] = f"""<div class="mcq-card has-statements" data-mode="statement-multi" data-qid="{q_num}" data-shuffle="false">
  <div class="question-header-row">
    <span class="question-number">문제 {q_num}</span>
    {src_html}
  </div>
  <div class="mcq-stem">
    <div class="stem-ocr-text">{c.get('stemText', '')}</div>
    <div class="mcq-statement-box">
{items_html}    </div>
  </div>
  <div class="mcq-options">{choices_html}</div>
  <div class="mcq-help">각 진술문을 탭하여 중복 선택하세요 · Space: 정답 확인</div>
</div>"""
            
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print('Cleaned all box statements cards front!')
