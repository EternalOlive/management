# -*- coding: utf-8 -*-
"""
1. unreveal() 시 진술문 및 보기의 정답/오답 하이라이트와 사유 완전 초기화 (답 숨김 복원)
2. 박스형 진술문 문제에서 하단 번호 버튼(.mcq-options) 완전 숨김 (100% 순수 RemNote 모드)
3. 10번, 14번 및 cards.html 패치
"""
import re

html_paths = [
    r'c:\Users\yoon\Downloads\management-cards\cards.html',
    r'c:\Users\yoon\Downloads\memory-cards-main\memory-cards-main\cards.html'
]

# CSS: 박스형 진술문 모드일 때 하단 보기 번호 조합 완전 숨김
css_hide_options = """
/* 박스형 진술문 모드일 때 하단 객관식 번호 조합 버튼 완전 숨김 (100% 순수 RemNote 모드) */
.mcq-card:has(.mcq-statement-box) .mcq-options,
.mcq-card[data-mode="statement-multi"] .mcq-options {
  display: none !important;
}
"""

js_reset_func = """
function resetMcqAnswerHighlight(c) {
  const frontEl = $('cFront');
  if (frontEl) {
    // 1. 객관식 보기 버튼 리셋
    frontEl.querySelectorAll('.mcq-option').forEach(btn => {
      btn.classList.remove('correct', 'incorrect');
      const orig = Number(btn.dataset.original);
      if (userSelectedChoice === orig) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    });

    // 2. RemNote 진술문 아이템 하이라이트 & 오답사유 완전 리셋 (원래 선택 상태 복원)
    frontEl.querySelectorAll('.mcq-statement-item').forEach(item => {
      const stmtKey = item.dataset.stmt;
      item.classList.remove('result-hit', 'result-miss', 'result-missed', 'result-passed');
      
      // 주입된 오답 사유 제거
      const rEl = item.querySelector('.mcq-stmt-reason');
      if (rEl) rEl.remove();

      // 원래 선택 상태로 복원
      const isSelected = userSelectedStatements.includes(stmtKey);
      item.classList.toggle('selected', isSelected);
      const stBadge = item.querySelector('.mcq-stmt-status');
      if (stBadge) {
        stBadge.textContent = isSelected ? '선택됨' : '선택';
      }
    });
  }

  // 3. 뒷면 요약 배너 리셋
  const summaryEl = document.querySelector('.mcq-stmt-summary');
  if (summaryEl) summaryEl.innerHTML = '';
}
"""

for p in html_paths:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. CSS 추가
    if 'display: none !important;\n}' not in content or '.mcq-statement-box) .mcq-options' not in content:
        content = content.replace('.mcq-statement-box {', css_hide_options + '\n.mcq-statement-box {', 1)
        print(f"Added css_hide_options to {p}")

    # 2. resetMcqAnswerHighlight 함수 추가
    if 'function resetMcqAnswerHighlight' not in content:
        content = content.replace('function unreveal(){', js_reset_func + '\nfunction unreveal(){', 1)
        print(f"Added resetMcqAnswerHighlight function to {p}")

    # 3. unreveal() 내부에 resetMcqAnswerHighlight 호출 주입
    if 'resetMcqAnswerHighlight(c);' not in content:
        target_unrev = "$('cardScroll').scrollTop=0;"
        content = content.replace(target_unrev, 'resetMcqAnswerHighlight(c);\n  ' + target_unrev, 1)
        print(f"Added reset call into unreveal() in {p}")

    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML patching completed!")
