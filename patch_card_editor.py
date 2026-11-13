#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cards.html에 학습 화면 카드 내용 수정(인라인 에디터 모달) 기능 주입 스크립트:
1. 헤더 도구모음에 [✏️ 수정] 버튼 추가 (단축키: e)
2. 문제 지문, 출처, 1~5번 보기, 정답 지정 라디오, 해설 수정 모달 추가
3. 저장 시 즉시 화면 반영 및 rebuildCardHtml 수행
4. localStorage(mgmt_card_edits_v1) 영속화 및 loadData 시 자동 오버라이드 병합
5. GitHub 연결 시 cards-data.json 원격 커밋 동기화 연동
"""

import os
import shutil
import re

TARGET_HTML = r"c:\Users\yoon\Downloads\management-cards\cards.html"
BACKUP_HTML = r"c:\Users\yoon\Downloads\management-cards\cards.html.pre_editor_bak"

if not os.path.exists(BACKUP_HTML):
    shutil.copyfile(TARGET_HTML, BACKUP_HTML)
    print(f"[*] 원본 백업 완료: {BACKUP_HTML}")

with open(TARGET_HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────
# 1. CSS 스타일 추가
# ─────────────────────────────────────────────────────────────
EDITOR_CSS = """
/* ══════════ 경영학 카드 수정 모달 스타일 ══════════ */
.card-edit-overlay {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
}
.card-edit-dialog {
  background: var(--c-bg, #ffffff);
  color: var(--c-text, #111827);
  border-radius: 16px;
  max-width: 680px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  border: 1px solid var(--c-border, #e5e7eb);
  animation: editModalPop 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes editModalPop {
  from { opacity: 0; transform: scale(0.96) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.card-edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--c-border, #e5e7eb);
  background: var(--c-card-bg, #f9fafb);
}
.card-edit-title {
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-edit-close {
  background: transparent;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 6px;
}
.card-edit-close:hover { color: #111; background: rgba(0,0,0,0.06); }
.card-edit-body {
  padding: 16px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  -webkit-overflow-scrolling: touch;
}
.edit-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.edit-field label {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-label, #374151);
}
.edit-tip {
  font-size: 11px;
  font-weight: normal;
  color: #6b7280;
}
.edit-input, .edit-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1.5px solid var(--c-border, #d1d5db);
  background: var(--c-card-bg, #fff);
  color: var(--c-text, #111);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.15s;
}
.edit-input:focus, .edit-textarea:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}
.edit-choices {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.choice-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.choice-radio-label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding-top: 8px;
  user-select: none;
}
.choice-badge {
  font-size: 18px;
  font-weight: 700;
  color: #6b7280;
  width: 24px;
  text-align: center;
  transition: all 0.15s ease;
}
.choice-radio-label input[type="radio"]:checked + .choice-badge {
  color: #16a34a;
  transform: scale(1.2);
  font-weight: 900;
}
.choice-input {
  flex: 1;
  resize: vertical;
}
.edit-sync-row {
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.06);
  border: 1px dashed rgba(37, 99, 235, 0.3);
}
.sync-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #1d4ed8;
  cursor: pointer;
  user-select: none;
}
.card-edit-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--c-border, #e5e7eb);
  background: var(--c-card-bg, #f9fafb);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.edit-footer-right {
  display: flex;
  gap: 10px;
}
.btn-primary {
  background: #2563eb;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary {
  background: var(--c-fill, #e5e7eb);
  color: var(--c-text, #374151);
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
}
.btn-subtle {
  background: transparent;
  color: #ef4444;
  border: 1px solid #fca5a5;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}
.btn-subtle:hover { background: #fef2f2; }

/* 다크모드 대응 */
[data-theme="dark"] .card-edit-dialog {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}
[data-theme="dark"] .card-edit-header, [data-theme="dark"] .card-edit-footer {
  background: #0f172a;
  border-color: #334155;
}
[data-theme="dark"] .edit-input, [data-theme="dark"] .edit-textarea {
  background: #0f172a;
  border-color: #334155;
  color: #f8fafc;
}
[data-theme="dark"] .btn-secondary {
  background: #334155;
  color: #e2e8f0;
}
[data-theme="dark"] .choice-badge {
  color: #94a3b8;
}
[data-theme="dark"] .edit-sync-row {
  background: rgba(30, 58, 138, 0.25);
  border-color: #3b82f6;
}
[data-theme="dark"] .sync-checkbox-label {
  color: #93c5fd;
}
"""

if "/* ══════════ 경영학 카드 수정 모달 스타일 ══════════ */" not in content:
    content = content.replace("</style>", EDITOR_CSS + "\n</style>", 1)
    print("[+] 에디터 CSS 주입 완료")

# ─────────────────────────────────────────────────────────────
# 2. 상단 버튼 주입 (btnCopyFront 옆에 btnEditCard)
# ─────────────────────────────────────────────────────────────
EDIT_BTN_HTML = """<button type="button" class="c-copy-btn" id="btnEditCard" title="카드 내용 수정 (e)" aria-label="카드 내용 수정" onclick="openCardEditor()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="width:16px;height:16px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>"""

if 'id="btnEditCard"' not in content:
    target_needle = 'id="btnCopyFront" title="카드 내용 복사" aria-label="카드 내용 복사">'
    if target_needle in content:
        # find the closing </button> of btnCopyFront
        idx = content.find(target_needle)
        end_btn = content.find('</button>', idx)
        if end_btn != -1:
            content = content[:end_btn+9] + EDIT_BTN_HTML + content[end_btn+9:]
            print("[+] 헤더 [✏️ 카드 수정] 버튼 주입 완료")

# ─────────────────────────────────────────────────────────────
# 3. 수정 모달 DOM 마크업 추가 (body 닫히기 직전)
# ─────────────────────────────────────────────────────────────
MODAL_HTML = """
<!-- ══════════ 카드 내용 수정 모달 ══════════ -->
<div id="ovlCardEdit" class="card-edit-overlay" style="display:none;" onclick="if(event.target===this)closeCardEditor();">
  <div class="card-edit-dialog" onclick="event.stopPropagation();">
    <div class="card-edit-header">
      <div class="card-edit-title">
        <span class="edit-icon">✏️</span>
        <span id="editModalTitle">문제 내용 수정</span>
      </div>
      <button type="button" class="card-edit-close" id="btnEditClose" onclick="closeCardEditor()" title="닫기">&times;</button>
    </div>
    
    <div class="card-edit-body">
      <!-- 출처 태그 -->
      <div class="edit-field">
        <label for="editSourceTag">출처 구분</label>
        <input type="text" id="editSourceTag" class="edit-input" placeholder="예: 경영지도사, 7급 서울시, 가맹거래사 등">
      </div>

      <!-- 문제 지문 -->
      <div class="edit-field">
        <label for="editStem">문제 지문 (Stem)</label>
        <textarea id="editStem" class="edit-textarea" rows="4" placeholder="문제 지문을 입력하세요"></textarea>
      </div>

      <!-- 1~5번 보기 및 정답 라디오 -->
      <div class="edit-field">
        <label>보기 및 정답 선택 <span class="edit-tip">(원하는 번호 앞의 동그라미를 눌러 정답 지정)</span></label>
        <div class="edit-choices">
          <div class="choice-row">
            <label class="choice-radio-label" title="1번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="1" id="radioChoice1">
              <span class="choice-badge">①</span>
            </label>
            <textarea id="editChoice1" class="edit-textarea choice-input" rows="2" placeholder="1번 보기 내용"></textarea>
          </div>
          <div class="choice-row">
            <label class="choice-radio-label" title="2번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="2" id="radioChoice2">
              <span class="choice-badge">②</span>
            </label>
            <textarea id="editChoice2" class="edit-textarea choice-input" rows="2" placeholder="2번 보기 내용"></textarea>
          </div>
          <div class="choice-row">
            <label class="choice-radio-label" title="3번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="3" id="radioChoice3">
              <span class="choice-badge">③</span>
            </label>
            <textarea id="editChoice3" class="edit-textarea choice-input" rows="2" placeholder="3번 보기 내용"></textarea>
          </div>
          <div class="choice-row">
            <label class="choice-radio-label" title="4번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="4" id="radioChoice4">
              <span class="choice-badge">④</span>
            </label>
            <textarea id="editChoice4" class="edit-textarea choice-input" rows="2" placeholder="4번 보기 내용"></textarea>
          </div>
          <div class="choice-row">
            <label class="choice-radio-label" title="5번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="5" id="radioChoice5">
              <span class="choice-badge">⑤</span>
            </label>
            <textarea id="editChoice5" class="edit-textarea choice-input" rows="2" placeholder="5번 보기 내용"></textarea>
          </div>
        </div>
      </div>

      <!-- 해설 텍스트 -->
      <div class="edit-field">
        <label for="editExplanation">해설 / 오답 정리</label>
        <textarea id="editExplanation" class="edit-textarea" rows="4" placeholder="해설 내용을 입력하세요"></textarea>
      </div>
      
      <!-- GitHub 동기화 옵션 -->
      <div class="edit-sync-row" id="editSyncRow" style="display:none;">
        <label class="sync-checkbox-label">
          <input type="checkbox" id="chkEditGhSync" checked>
          <span>☁️ GitHub 레포에 즉시 반영 (cards-data.json 커밋)</span>
        </label>
      </div>
    </div>

    <div class="card-edit-footer">
      <button type="button" class="btn-subtle" id="btnEditReset" onclick="resetCurrentCardEdit()" title="수정 전 원본 데이터로 복원합니다">원본 초기화</button>
      <div class="edit-footer-right">
        <button type="button" class="btn-secondary" id="btnEditCancel" onclick="closeCardEditor()">취소</button>
        <button type="button" class="btn-primary" id="btnEditSave" onclick="saveCurrentCardEdit()">저장 (Ctrl+Enter)</button>
      </div>
    </div>
  </div>
</div>
"""

if 'id="ovlCardEdit"' not in content:
    content = content.replace("</body>", MODAL_HTML + "\n</body>", 1)
    print("[+] 모달 DOM 마크업 주입 완료")

# ─────────────────────────────────────────────────────────────
# 4. JS 에디터 컨트롤러 및 동기화 함수 주입
# ─────────────────────────────────────────────────────────────
EDITOR_JS = """
// ══════════ 경영학 카드 수정(에디터) 및 영속화 시스템 ══════════
const K_CARD_EDITS = 'mgmt_card_edits_v1';
let _currentEditingCard = null;

function getCardEditsMap() {
  try {
    return JSON.parse(localStorage.getItem(K_CARD_EDITS)) || {};
  } catch(e) {
    return {};
  }
}

function saveCardEditsMap(map) {
  try {
    localStorage.setItem(K_CARD_EDITS, JSON.stringify(map));
  } catch(e) {
    console.warn('[CardEdit] localStorage save error', e);
  }
}

function applyCustomEditsToData() {
  const edits = getCardEditsMap();
  if (!DATA || !Array.isArray(DATA)) return;
  let count = 0;
  for (const c of DATA) {
    if (c && c.id && edits[c.id]) {
      const ed = edits[c.id];
      if (ed.stemText !== undefined) c.stemText = ed.stemText;
      if (ed.sourceTag !== undefined) c.sourceTag = ed.sourceTag;
      if (ed.choices !== undefined) c.choices = ed.choices;
      if (ed.correct !== undefined) c.correct = ed.correct;
      if (ed.explanationText !== undefined) c.explanationText = ed.explanationText;
      rebuildCardHtml(c);
      count++;
    }
  }
  if (count > 0) {
    console.log(`[CardEdit] ${count}장의 사용자 수정 카드가 복원되었습니다.`);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function rebuildCardHtml(c) {
  const circles = ['①', '②', '③', '④', '⑤'];
  
  // 기존 front에서 image-frame이 있으면 추출 보존
  let imgHtml = '';
  if (c.front) {
    const m = c.front.match(/<div class="image-frame"[\\s\\S]*?<\\/div>/);
    if (m) imgHtml = '\\n    ' + m[0];
  }

  const qNum = c.qid || (c.id ? c.id.replace('mgmt_', '') : '');
  const sourceBadge = c.sourceTag ? `<span class="source-badge">${escapeHtml(c.sourceTag)}</span>\\n    ` : '';
  
  const choicesHtml = (c.choices || []).map((ch, idx) => {
    const num = idx + 1;
    const label = circles[idx] || (num + '.');
    let text = ch.replace(/^[1-5]번:\\s*/, '');
    return `<button type="button" class="mcq-option text-option" data-original="${num}"><span class="mcq-label">${label}</span><span class="mcq-choice-text">${escapeHtml(text)}</span></button>`;
  }).join('');

  c.front = `<div class="mcq-card" data-qid="${qNum}" data-shuffle="false">
  <div class="question-number">문제 ${qNum}</div>
  <div class="mcq-stem">
    ${sourceBadge}<div class="stem-ocr-text">${escapeHtml(c.stemText || '')}</div>${imgHtml}
  </div>
  <div class="mcq-options ">${choicesHtml}</div>
  <div class="mcq-help">1~5번 키 또는 보기를 눌러 답을 선택하세요.</div>
</div>`;

  const corrIdx = (Number(c.correct) || 1) - 1;
  const corrLabel = circles[corrIdx] || c.correct;
  
  // 해설에서 줄바꿈은 <br> 태그로 변환
  const expHtml = escapeHtml(c.explanationText || '').replace(/\\n/g, '<br>');
  
  c.back = `<div class="mcq-result" data-qid="${qNum}" data-correct="${c.correct}">
  <div class="mcq-answer-badge">정답: <span class="mcq-current-answer">${corrLabel}</span></div>
  <div class="mcq-explanation">
    <div class="mcq-exp-title">해설</div>
    <div class="mcq-exp-text">${expHtml}</div>
  </div>
</div>`;
}

function openCardEditor() {
  const c = cur();
  if (!c) {
    toast('수정할 카드가 없습니다.');
    return;
  }
  _currentEditingCard = c;

  const qNum = c.qid || (c.id ? c.id.replace('mgmt_', '') : '');
  const titleEl = document.getElementById('editModalTitle');
  if (titleEl) titleEl.textContent = `문제 ${qNum} 내용 수정`;

  const srcEl = document.getElementById('editSourceTag');
  if (srcEl) srcEl.value = c.sourceTag || '';

  const stemEl = document.getElementById('editStem');
  if (stemEl) stemEl.value = c.stemText || '';

  const choices = c.choices || [];
  for (let i = 1; i <= 5; i++) {
    const inputEl = document.getElementById(`editChoice${i}`);
    if (inputEl) {
      let rawText = choices[i - 1] || '';
      inputEl.value = rawText.replace(/^[1-5]번:\\s*/, '');
    }
  }

  const corr = Number(c.correct) || 1;
  const radio = document.getElementById(`radioChoice${corr}`);
  if (radio) radio.checked = true;

  const expEl = document.getElementById('editExplanation');
  if (expEl) {
    let exp = c.explanationText || '';
    expEl.value = exp.replace(/<br\\s*\\/?>/gi, '\\n');
  }

  // GitHub 토큰이 설정되어 있으면 동기화 옵션 표시
  const syncRow = document.getElementById('editSyncRow');
  const token = typeof ghToken === 'function' ? ghToken() : (lsGet('cfg_token') || '');
  if (syncRow) {
    syncRow.style.display = token ? 'block' : 'none';
  }

  // 원본 초기화 버튼 상태 (수정된 적이 있으면 빨간색 강조)
  const edits = getCardEditsMap();
  const resetBtn = document.getElementById('btnEditReset');
  if (resetBtn) {
    resetBtn.style.display = edits[c.id] ? 'inline-block' : 'none';
  }

  const ovl = document.getElementById('ovlCardEdit');
  if (ovl) ovl.style.display = 'flex';
  
  if (stemEl) stemEl.focus();
}

function closeCardEditor() {
  const ovl = document.getElementById('ovlCardEdit');
  if (ovl) ovl.style.display = 'none';
  _currentEditingCard = null;
}

async function saveCurrentCardEdit() {
  const c = _currentEditingCard;
  if (!c) return;

  const srcEl = document.getElementById('editSourceTag');
  const stemEl = document.getElementById('editStem');
  const expEl = document.getElementById('editExplanation');

  const newSourceTag = srcEl ? srcEl.value.trim() : '';
  const newStem = stemEl ? stemEl.value.trim() : '';
  const newExp = expEl ? expEl.value.trim() : '';

  const newChoices = [];
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`editChoice${i}`);
    const text = el ? el.value.trim() : '';
    newChoices.push(`${i}번: ${text}`);
  }

  let selectedCorrect = 1;
  const checkedRadio = document.querySelector('input[name="editCorrectChoice"]:checked');
  if (checkedRadio) {
    selectedCorrect = Number(checkedRadio.value);
  }

  // 카드 객체 업데이트
  c.sourceTag = newSourceTag;
  c.stemText = newStem;
  c.choices = newChoices;
  c.correct = selectedCorrect;
  c.explanationText = newExp;

  // HTML 템플릿 재빌드
  rebuildCardHtml(c);

  // 로컬 스토리지에 영속화
  const edits = getCardEditsMap();
  edits[c.id] = {
    sourceTag: newSourceTag,
    stemText: newStem,
    choices: newChoices,
    correct: selectedCorrect,
    explanationText: newExp,
    updatedAt: new Date().toISOString()
  };
  saveCardEditsMap(edits);

  // 현재 화면 즉시 갱신
  const cFront = document.getElementById('cFront');
  const cBack = document.getElementById('cBack');
  if (cFront) {
    cFront.innerHTML = c.front;
    if (typeof runCardScripts === 'function') runCardScripts(cFront);
  }
  if (cBack) {
    cBack.innerHTML = c.back;
    if (typeof runCardScripts === 'function') runCardScripts(cBack);
  }
  if (typeof checkMcqAnswerAndHighlight === 'function') {
    checkMcqAnswerAndHighlight(c);
  }

  closeCardEditor();
  toast('💾 카드 내용이 저장되었습니다.');

  // GitHub 동기화 요청 여부 확인
  const chkSync = document.getElementById('chkEditGhSync');
  if (chkSync && chkSync.checked && typeof ghPut === 'function') {
    const token = typeof ghToken === 'function' ? ghToken() : (lsGet('cfg_token') || '');
    if (token) {
      toast('☁️ GitHub에 동기화 중...');
      try {
        await ghPut(DATA_PATH, () => ({ v: 1, cards: DATA }));
        toast('☁️ GitHub 저장소(cards-data.json)에 반영 완료!');
      } catch(err) {
        console.error('[GitHub Sync Error]', err);
        toast('⚠️ GitHub 동기화 실패 (로컬 저장은 완료됨)');
      }
    }
  }
}

function resetCurrentCardEdit() {
  const c = _currentEditingCard;
  if (!c) return;
  if (!confirm('수정하기 전 원본 카드로 복원하시겠습니까?')) return;

  const edits = getCardEditsMap();
  delete edits[c.id];
  saveCardEditsMap(edits);

  closeCardEditor();
  toast('🔄 원본 카드로 복원되었습니다. 화면을 새로고침합니다.');
  setTimeout(() => location.reload(), 300);
}

// 수정된 전체 cards-data.json을 파일로 다운로드하는 유틸
function exportEditedCardsDataJson() {
  if (!DATA || !DATA.length) {
    toast('내보낼 카드 데이터가 없습니다.');
    return;
  }
  const blob = new Blob([JSON.stringify({ v: 1, cards: DATA }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cards-data.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  toast('📥 cards-data.json 다운로드 완료');
}
"""

if "function openCardEditor()" not in content:
    content = content.replace("function showCard(){", EDITOR_JS + "\nfunction showCard(){", 1)
    print("[+] 에디터 JS 컨트롤러 함수 주입 완료")

# ─────────────────────────────────────────────────────────────
# 5. loadData 완료 후 applyCustomEditsToData() 호출 주입
# ─────────────────────────────────────────────────────────────
MERGE_HOOK = """applyCustomEditsToData();\n  BYID={};"""
if "applyCustomEditsToData();" not in content:
    if "BYID={}; const tags=new Set()" in content:
        content = content.replace("BYID={}; const tags=new Set()", "applyCustomEditsToData();\n  BYID={}; const tags=new Set()", 1)
        print("[+] loadData() 내 수정본 병합(applyCustomEditsToData) 주입 완료")

# ─────────────────────────────────────────────────────────────
# 6. 키보드 단축키 'e' 바인딩 주입
# ─────────────────────────────────────────────────────────────
EDIT_KEYBOARD_HOOK = """
  // 'e' 또는 'E' 키: 현재 카드 수정 모달 열기
  if((e.key==='e'||e.key==='E') && $('scrSolve').classList.contains('on') && !['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)){
    const ovl = $('ovlCardEdit');
    if(!ovl || ovl.style.display==='none'){
      openCardEditor();
      e.preventDefault();
      return;
    }
  }
  // 에디터 모달 열려있을 때 단축키: Ctrl+Enter (저장), Esc (닫기)
  const editOvl = $('ovlCardEdit');
  if(editOvl && editOvl.style.display!=='none'){
    if(e.key==='Escape'){
      closeCardEditor();
      e.preventDefault();
      return;
    }
    if(e.key==='Enter' && (e.ctrlKey || e.metaKey)){
      saveCurrentCardEdit();
      e.preventDefault();
      return;
    }
  }
"""

if "// 'e' 또는 'E' 키: 현재 카드 수정 모달 열기" not in content:
    content = content.replace("document.addEventListener('keydown',e=>{", "document.addEventListener('keydown',e=>{" + EDIT_KEYBOARD_HOOK, 1)
    print("[+] 키보드 단축키 (e / Ctrl+Enter / Esc) 주입 완료")

with open(TARGET_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] cards.html 카드 수정 에디터 시스템 패치 성공!")
