# -*- coding: utf-8 -*-
"""
전수환 경영학 카드앱: 카드 에디터 UI에 '보기 진술문(boxStatements ㄱ,ㄴ,ㄷ,ㄹ)' 편집 기능 추가
- 스피킹 매트릭스 디자인 시스템 (tokens.css, DESIGN.md) 100% 준수
"""
import re

html_path = r'c:\Users\yoon\Downloads\management-cards\cards.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS 추가
css_editor_stmt = """
/* ── 카드 에디터 모달 내 보기 진술문(ㄱ, ㄴ, ㄷ, ㄹ) 편집 스타일 ── */
.edit-stmt-zone {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--c-fill);
  padding: 12px 14px;
  border-radius: var(--r-cell, 12px);
  border: 0.5px solid var(--c-sep);
}
.edit-stmt-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.edit-stmt-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: var(--c-card);
  padding: 10px 12px;
  border-radius: var(--r-cell, 12px);
  border: 0.5px solid var(--c-sep);
  box-shadow: var(--sh-card);
}
.edit-stmt-row1 {
  display: flex;
  align-items: center;
  gap: 8px;
}
.edit-stmt-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: var(--r-pill, 999px);
  background: var(--c-fill);
  font-weight: 700;
  font-size: 13px;
  color: var(--c-label);
  flex-shrink: 0;
}
.edit-stmt-input {
  flex: 1;
  padding: 8px 10px;
  border-radius: 8px;
  border: 0.5px solid var(--c-sep);
  background: var(--c-fill);
  color: var(--c-label);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  box-sizing: border-box;
}
.edit-stmt-input:focus {
  border-color: var(--c-acc);
}
.edit-stmt-seg {
  display: inline-flex;
  border-radius: var(--r-pill, 999px);
  background: var(--c-fill);
  padding: 2px;
  gap: 2px;
  flex-shrink: 0;
}
.edit-stmt-seg-btn {
  border: none;
  background: transparent;
  padding: 3px 10px;
  border-radius: var(--r-pill, 999px);
  font-size: 12px;
  font-weight: 700;
  color: var(--c-sec);
  cursor: pointer;
  transition: all 0.15s ease;
}
.edit-stmt-seg-btn.active.is-o {
  background: var(--c-good) !important;
  color: #fff !important;
}
.edit-stmt-seg-btn.active.is-x {
  background: var(--c-again) !important;
  color: #fff !important;
}
.edit-stmt-del {
  border: none;
  background: transparent;
  color: var(--c-sec);
  font-size: 20px;
  line-height: 1;
  padding: 0 4px;
  cursor: pointer;
}
.edit-stmt-del:hover {
  color: var(--c-again);
}
.edit-stmt-row2 {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 34px;
}
.edit-stmt-reason-input {
  flex: 1;
  padding: 5px 8px;
  border-radius: 6px;
  border: 0.5px solid var(--c-sep);
  background: var(--c-fill);
  color: var(--c-label);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  box-sizing: border-box;
}
.btn-add-stmt {
  align-self: flex-start;
  background: var(--c-card);
  border: 0.5px solid var(--c-sep);
  color: var(--c-acc);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: var(--r-pill, 999px);
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-add-stmt:hover {
  background: var(--c-fill);
}
"""

if '.edit-stmt-zone' not in content:
    content = content.replace('.card-edit-body {', css_editor_stmt + '\n.card-edit-body {', 1)
    print("Added editor statement CSS.")

# 2. 모달 HTML 내 진술문 편집 영역 삽입
html_stmt_zone = """
      <!-- 보기 진술문 (ㄱ, ㄴ, ㄷ, ㄹ) 편집 영역 -->
      <div class="edit-field" id="editBoxStatementsZone" style="display:none;">
        <div class="edit-field-header">
          <label>보기 진술문 (ㄱ, ㄴ, ㄷ, ㄹ 박스형 선지)</label>
          <button type="button" class="btn-subtle" id="btnToggleBoxStatements" onclick="toggleBoxStatementsZone()">진술문 박스 제거</button>
        </div>
        <div class="edit-stmt-zone">
          <div id="editStmtList" class="edit-stmt-list"></div>
          <button type="button" class="btn-add-stmt" onclick="addStmtItem()">＋ 진술문 추가</button>
        </div>
      </div>
      <div id="addBoxStatementsZone" style="display:none; margin-top:-6px;">
        <button type="button" class="btn-subtle" onclick="enableBoxStatementsZone()">＋ 보기 박스(진술문 ㄱ, ㄴ, ㄷ, ㄹ) 추가</button>
      </div>
"""

if 'id="editBoxStatementsZone"' not in content:
    target_html = '<!-- [NEW] 이미지 미리보기 및 삭제 영역 -->'
    content = content.replace(target_html, html_stmt_zone + '\n      ' + target_html, 1)
    print("Added editBoxStatementsZone HTML into modal.")

# 3. JS 함수 추가: 진술문 편집기 제어
js_editor_stmt_funcs = """
// ─── 카드 에디터 모달 내 보기 진술문(boxStatements) 관리 ───
let _editingStatements = [];
const KOR_JAMOS = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];

function toggleBoxStatementsZone() {
  const zone = document.getElementById('editBoxStatementsZone');
  const addZone = document.getElementById('addBoxStatementsZone');
  if (zone.style.display !== 'none') {
    if (_editingStatements.length > 0 && !confirm('보기 진술문 박스를 제거하시겠습니까?')) return;
    _editingStatements = [];
    zone.style.display = 'none';
    if (addZone) addZone.style.display = 'block';
  } else {
    enableBoxStatementsZone();
  }
}

function enableBoxStatementsZone() {
  const zone = document.getElementById('editBoxStatementsZone');
  const addZone = document.getElementById('addBoxStatementsZone');
  if (zone) zone.style.display = 'flex';
  if (addZone) addZone.style.display = 'none';
  if (_editingStatements.length === 0) {
    _editingStatements = [
      { id: 'ㄱ', label: 'ㄱ', text: '', isCorrect: true, reason: '' },
      { id: 'ㄴ', label: 'ㄴ', text: '', isCorrect: false, reason: '' },
      { id: 'ㄷ', label: 'ㄷ', text: '', isCorrect: false, reason: '' },
      { id: 'ㄹ', label: 'ㄹ', text: '', isCorrect: true, reason: '' }
    ];
  }
  renderStmtEditorList();
}

function renderStmtEditorList() {
  const listEl = document.getElementById('editStmtList');
  if (!listEl) return;
  listEl.innerHTML = '';

  _editingStatements.forEach((stmt, idx) => {
    const itemEl = document.createElement('div');
    itemEl.className = 'edit-stmt-item';

    const isTrue = stmt.isCorrect !== false;

    itemEl.innerHTML = `
      <div class="edit-stmt-row1">
        <span class="edit-stmt-badge">${escapeHtml(stmt.label || KOR_JAMOS[idx] || String(idx+1))}</span>
        <input type="text" class="edit-stmt-input" placeholder="진술문 내용을 입력하세요" value="${escapeHtml(stmt.text || '')}">
        <div class="edit-stmt-seg">
          <button type="button" class="edit-stmt-seg-btn is-o ${isTrue ? 'active' : ''}" title="옳은 문장 (O)">O (참)</button>
          <button type="button" class="edit-stmt-seg-btn is-x ${!isTrue ? 'active' : ''}" title="틀린 문장 (X)">X (거짓)</button>
        </div>
        <button type="button" class="edit-stmt-del" title="이 진술문 삭제">&times;</button>
      </div>
      <div class="edit-stmt-row2">
        <input type="text" class="edit-stmt-reason-input" placeholder="↳ 오답 사유 또는 해설 요약 (선택 사항)" value="${escapeHtml(stmt.reason || stmt.desc || '')}">
      </div>
    `;

    // 텍스트 바인딩
    const textInput = itemEl.querySelector('.edit-stmt-input');
    textInput.oninput = (e) => { stmt.text = e.target.value; };

    // 사유 바인딩
    const reasonInput = itemEl.querySelector('.edit-stmt-reason-input');
    reasonInput.oninput = (e) => { stmt.reason = e.target.value; };

    // O / X 토글
    const btnO = itemEl.querySelector('.edit-stmt-seg-btn.is-o');
    const btnX = itemEl.querySelector('.edit-stmt-seg-btn.is-x');
    btnO.onclick = () => {
      stmt.isCorrect = true;
      btnO.classList.add('active');
      btnX.classList.remove('active');
    };
    btnX.onclick = () => {
      stmt.isCorrect = false;
      btnX.classList.add('active');
      btnO.classList.remove('active');
    };

    // 삭제 버튼
    const delBtn = itemEl.querySelector('.edit-stmt-del');
    delBtn.onclick = () => {
      _editingStatements.splice(idx, 1);
      // 번호 재정렬
      _editingStatements.forEach((s, i) => {
        s.label = KOR_JAMOS[i] || String(i+1);
        s.id = s.label;
      });
      renderStmtEditorList();
    };

    listEl.appendChild(itemEl);
  });
}

function addStmtItem() {
  const nextIdx = _editingStatements.length;
  const nextLabel = KOR_JAMOS[nextIdx] || String(nextIdx + 1);
  _editingStatements.push({
    id: nextLabel,
    label: nextLabel,
    text: '',
    isCorrect: false,
    reason: ''
  });
  renderStmtEditorList();
  // 마지막 추가된 인풋에 포커스
  setTimeout(() => {
    const inputs = document.querySelectorAll('.edit-stmt-input');
    if (inputs.length > 0) inputs[inputs.length - 1].focus();
  }, 50);
}
"""

if 'function toggleBoxStatementsZone' not in content:
    content = content.replace('function openCardEditor() {', js_editor_stmt_funcs + '\nfunction openCardEditor() {', 1)
    print("Added js_editor_stmt_funcs.")

# 4. openCardEditor() 내 진술문 데이터 로드 로직 삽입
load_stmt_logic = """
  // 보기 진술문(boxStatements) 초기화 및 바인딩
  const stmtZone = document.getElementById('editBoxStatementsZone');
  const addStmtZone = document.getElementById('addBoxStatementsZone');
  const boxStmts = c.boxStatements || [];
  
  if (boxStmts.length > 0) {
    _editingStatements = JSON.parse(JSON.stringify(boxStmts));
    if (stmtZone) stmtZone.style.display = 'flex';
    if (addStmtZone) addStmtZone.style.display = 'none';
    renderStmtEditorList();
  } else {
    _editingStatements = [];
    if (stmtZone) stmtZone.style.display = 'none';
    if (addStmtZone) addStmtZone.style.display = 'block';
  }
"""

if '보기 진술문(boxStatements) 초기화 및 바인딩' not in content:
    target_open = "const stemEl = document.getElementById('editStem');"
    content = content.replace(target_open, target_open + '\n' + load_stmt_logic, 1)
    print("Added load_stmt_logic into openCardEditor.")

# 5. saveCurrentCardEdit() 내 진술문 저장 로직 삽입
save_stmt_logic = """
  // 보기 진술문(boxStatements) 수집
  const stmtZone = document.getElementById('editBoxStatementsZone');
  if (stmtZone && stmtZone.style.display !== 'none' && _editingStatements.length > 0) {
    c.boxStatements = JSON.parse(JSON.stringify(_editingStatements));
    c.correctChoices = c.boxStatements.filter(s => s.isCorrect !== false).map(s => s.label || s.id);
    c.typ = '박스선택형';
  } else {
    delete c.boxStatements;
    delete c.correctChoices;
    if (c.typ === '박스선택형') c.typ = '객관식';
  }
"""

if '보기 진술문(boxStatements) 수집' not in content:
    target_save = "c.removeImage = _cardImageRemoved;"
    content = content.replace(target_save, target_save + '\n' + save_stmt_logic, 1)
    print("Added save_stmt_logic into saveCurrentCardEdit.")

# 6. rebuildCardHtml() 내 boxStatements HTML 렌더링 지원
rebuild_stmt_code = """
  // 보기 진술문(boxStatements) 박스 빌드
  let stmtBoxHtml = '';
  if (c.boxStatements && c.boxStatements.length > 0) {
    const itemsHtml = c.boxStatements.map((stmt, idx) => {
      const lbl = stmt.label || ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ'][idx] || String(idx+1);
      return `<div class="mcq-statement-item" data-stmt="${escapeHtml(lbl)}">
        <span class="mcq-stmt-badge">${escapeHtml(lbl)}</span>
        <div class="mcq-stmt-content">
          <div class="mcq-stmt-text">${escapeHtml(stmt.text || '')}</div>
        </div>
        <span class="mcq-stmt-status">선택</span>
      </div>`;
    }).join('\\n      ');

    stmtBoxHtml = `\\n    <div class="mcq-statement-box">
      <div class="mcq-statement-header">
        <span>진술문 보기 (탭하여 옳은 선지 중복 선택)</span>
        <span class="mcq-stmt-hint">단축키: ㄱ/ㄴ/ㄷ/ㄹ 또는 1~4</span>
      </div>
      ${itemsHtml}
    </div>`;
  }
"""

if '보기 진술문(boxStatements) 박스 빌드' not in content:
    target_rebuild = "const sourceBadge = c.sourceTag ? `<span class=\"source-badge\">${escapeHtml(c.sourceTag)}</span>\\n    ` : '';"
    content = content.replace(target_rebuild, target_rebuild + '\n' + rebuild_stmt_code, 1)
    print("Added rebuild_stmt_code into rebuildCardHtml.")

# front 템플릿에 stmtBoxHtml 삽입
if '${stmtBoxHtml}' not in content:
    content = content.replace('${imgHtml}', '${stmtBoxHtml}${imgHtml}', 1)
    print("Inserted ${stmtBoxHtml} into front template.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# memory-cards-main에도 동기화
with open(r'c:\Users\yoon\Downloads\memory-cards-main\memory-cards-main\cards.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied Box Statement Editor to cards.html!")
