#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cards.html에 학습 화면 카드 내용 수정(인라인 에디터 모달) 기능 업그레이드 스크립트:
1. 헤더 도구모음에 [✏️ 수정] 버튼 추가 (단축키: e)
2. 문제 지문, 출처, 보기, 정답 지정 라디오, 해설 수정 모달
3. [NEW] 이미지 삭제/복원 기능 (이미지 미리보기 및 🗑️ 이미지 삭제 버튼)
4. [NEW] 4지선다 / 5지선다 유연한 지원 (5번 보기 삭제/추가 및 자동 감지, 4지선다 단축키 연동)
5. 저장 시 즉시 화면 반영 및 rebuildCardHtml 수행
6. localStorage(mgmt_card_edits_v1) 영속화 및 loadData 시 자동 오버라이드 병합
7. GitHub 연결 시 cards-data.json 원격 커밋 동기화 연동
"""

import os
import shutil
import re

TARGET_HTML = r"c:\Users\yoon\Downloads\management-cards\cards.html"
BACKUP_HTML = r"c:\Users\yoon\Downloads\management-cards\cards.html.pre_editor_bak"

# pre_editor_bak이 있으면 거기서부터 깔끔하게 재적용
if os.path.exists(BACKUP_HTML):
    with open(BACKUP_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    print("[*] pre_editor_bak 원본에서 깔끔하게 시작합니다.")
else:
    with open(TARGET_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    shutil.copyfile(TARGET_HTML, BACKUP_HTML)
    print(f"[*] 원본 백업 완료: {BACKUP_HTML}")

# ─────────────────────────────────────────────────────────────
# 1. CSS 스타일 추가
# ─────────────────────────────────────────────────────────────
EDITOR_CSS = """
/* ══════════ 경영학 카드 수정 모달 스타일 (v2: 이미지 삭제 및 4지선다 지원) ══════════ */
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
.edit-field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

/* 이미지 관리 구역 */
.edit-image-zone {
  border: 1.5px dashed var(--c-border, #d1d5db);
  border-radius: 10px;
  padding: 12px 14px;
  background: rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.edit-image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.edit-image-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-label, #374151);
}
.edit-image-preview-wrapper {
  max-height: 180px;
  overflow: hidden;
  border-radius: 6px;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s ease;
}
.edit-image-preview-wrapper img {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}
.edit-image-removed-notice {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #b91c1c;
  font-weight: 600;
}
.btn-restore-img {
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 11px;
  cursor: pointer;
}

/* 보기(Choices) 영역 */
.edit-choices {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.choice-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  position: relative;
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
.btn-remove-choice {
  background: transparent;
  border: 1px solid transparent;
  color: #9ca3af;
  font-size: 18px;
  line-height: 1;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 6px;
}
.btn-remove-choice:hover {
  color: #ef4444;
  background: #fee2e2;
}
.btn-add-choice {
  width: 100%;
  padding: 8px;
  background: rgba(37, 99, 235, 0.06);
  border: 1.5px dashed #93c5fd;
  color: #2563eb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-add-choice:hover {
  background: rgba(37, 99, 235, 0.12);
  border-color: #2563eb;
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
[data-theme="dark"] .edit-image-zone {
  background: rgba(255,255,255,0.03);
  border-color: #334155;
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
[data-theme="dark"] .btn-add-choice {
  background: rgba(30, 58, 138, 0.3);
  border-color: #3b82f6;
  color: #93c5fd;
}
"""

content = content.replace("</style>", EDITOR_CSS + "\n</style>", 1)
print("[+] 에디터 v2 CSS 주입 완료")

# ─────────────────────────────────────────────────────────────
# 2. 상단 버튼 주입 (btnCopyFront 옆에 btnEditCard)
# ─────────────────────────────────────────────────────────────
EDIT_BTN_HTML = """<button type="button" class="c-copy-btn" id="btnEditCard" title="카드 내용 수정 (e)" aria-label="카드 내용 수정" onclick="openCardEditor()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="width:16px;height:16px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>"""

target_needle = 'id="btnCopyFront" title="카드 내용 복사" aria-label="카드 내용 복사">'
if target_needle in content:
    idx = content.find(target_needle)
    end_btn = content.find('</button>', idx)
    if end_btn != -1:
        content = content[:end_btn+9] + EDIT_BTN_HTML + content[end_btn+9:]
        print("[+] 헤더 [카드 수정] 버튼 주입 완료")

# ─────────────────────────────────────────────────────────────
# 3. 수정 모달 DOM 마크업 추가 (body 닫히기 직전)
# ─────────────────────────────────────────────────────────────
MODAL_HTML = """
<!-- ══════════ 카드 내용 수정 모달 (v2) ══════════ -->
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

      <!-- [NEW] 이미지 미리보기 및 삭제 영역 -->
      <div id="editImageZone" class="edit-image-zone" style="display:none;">
        <div class="edit-image-header">
          <span class="edit-image-label">🖼️ 문제 첨부 이미지</span>
          <button type="button" class="btn-subtle" id="btnToggleRemoveImage" onclick="toggleRemoveImage()">🗑️ 이미지 삭제</button>
        </div>
        <div class="edit-image-preview-wrapper" id="editImagePreviewWrapper">
          <img id="editImagePreview" src="" alt="문제 이미지 미리보기">
        </div>
        <div id="editImageRemovedNotice" class="edit-image-removed-notice" style="display:none;">
          <span>⚠️ 이미지가 삭제 예정입니다. (저장 시 완전히 제거됩니다)</span>
          <button type="button" class="btn-restore-img" onclick="toggleRemoveImage()">되돌리기</button>
        </div>
      </div>

      <!-- 1~5번 보기 및 정답 라디오 (4지/5지선다 지원) -->
      <div class="edit-field">
        <div class="edit-field-header">
          <label>보기 및 정답 선택 <span class="edit-tip">(원하는 번호 앞의 동그라미를 눌러 정답 지정)</span></label>
        </div>
        <div class="edit-choices">
          <div class="choice-row" id="choiceRow1">
            <label class="choice-radio-label" title="1번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="1" id="radioChoice1">
              <span class="choice-badge">①</span>
            </label>
            <textarea id="editChoice1" class="edit-textarea choice-input" rows="2" placeholder="1번 보기 내용"></textarea>
          </div>
          <div class="choice-row" id="choiceRow2">
            <label class="choice-radio-label" title="2번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="2" id="radioChoice2">
              <span class="choice-badge">②</span>
            </label>
            <textarea id="editChoice2" class="edit-textarea choice-input" rows="2" placeholder="2번 보기 내용"></textarea>
          </div>
          <div class="choice-row" id="choiceRow3">
            <label class="choice-radio-label" title="3번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="3" id="radioChoice3">
              <span class="choice-badge">③</span>
            </label>
            <textarea id="editChoice3" class="edit-textarea choice-input" rows="2" placeholder="3번 보기 내용"></textarea>
          </div>
          <div class="choice-row" id="choiceRow4">
            <label class="choice-radio-label" title="4번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="4" id="radioChoice4">
              <span class="choice-badge">④</span>
            </label>
            <textarea id="editChoice4" class="edit-textarea choice-input" rows="2" placeholder="4번 보기 내용"></textarea>
          </div>
          <!-- 5번 보기 행 (4지선다인 경우 숨김 가능) -->
          <div class="choice-row" id="choiceRow5">
            <label class="choice-radio-label" title="5번을 정답으로 지정">
              <input type="radio" name="editCorrectChoice" value="5" id="radioChoice5">
              <span class="choice-badge">⑤</span>
            </label>
            <textarea id="editChoice5" class="edit-textarea choice-input" rows="2" placeholder="5번 보기 내용"></textarea>
            <button type="button" class="btn-remove-choice" id="btnRemoveChoice5" onclick="setChoiceCount(4)" title="5번 보기 제거 (4지선다로 변경)">&times;</button>
          </div>
          <div id="addChoice5Zone" style="display:none;">
            <button type="button" class="btn-add-choice" onclick="setChoiceCount(5)">➕ 5번 보기 추가 (5지선다로 변경)</button>
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

content = content.replace("</body>", MODAL_HTML + "\n</body>", 1)
print("[+] 모달 v2 DOM 마크업 주입 완료")

# ─────────────────────────────────────────────────────────────
# 4. JS 에디터 컨트롤러 및 동기화 함수 주입
# ─────────────────────────────────────────────────────────────
EDITOR_JS = """
// ══════════ 경영학 카드 수정(에디터 v2) 시스템 ══════════
const K_CARD_EDITS = 'mgmt_card_edits_v1';
let _currentEditingCard = null;
let _cardImageRemoved = false;
let _choiceCount = 5;

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
      if (ed.removeImage) c.removeImage = true;
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
  
  // 이미지 처리 (removeImage 플래그가 있으면 제거)
  let imgHtml = '';
  if (!c.removeImage && c.front) {
    const m = c.front.match(/<div class="image-frame"[\\s\\S]*?<\\/div>/);
    if (m) imgHtml = '\\n    ' + m[0];
  }

  const qNum = c.qid || (c.id ? c.id.replace('mgmt_', '') : '');
  const sourceBadge = c.sourceTag ? `<span class="source-badge">${escapeHtml(c.sourceTag)}</span>\\n    ` : '';
  
  // choices 빌드: 비어있지 않은 보기만 생성 (4지선다면 4개만)
  let choicesList = c.choices || [];
  if (choicesList.length === 0 && !c.stemText) {
    // 순수 번호 버튼일 때
    const count = (c.correct && c.correct > 4) ? 5 : 4;
    choicesList = Array.from({length: count}, (_, i) => `${i+1}번: `);
  }

  const choicesHtml = choicesList.map((ch, idx) => {
    const num = idx + 1;
    const label = circles[idx] || (num + '.');
    let text = ch.replace(/^[1-5]번:\\s*/, '').trim();
    if (!text) {
      // 본문이 없으면 번호 버튼
      return `<button type="button" class="mcq-option number-option" data-original="${num}"><span class="mcq-label">${label}</span></button>`;
    }
    return `<button type="button" class="mcq-option text-option" data-original="${num}"><span class="mcq-label">${label}</span><span class="mcq-choice-text">${escapeHtml(text)}</span></button>`;
  }).join('');

  const optCompactClass = choicesList.some(ch => ch.replace(/^[1-5]번:\\s*/, '').trim()) ? '' : 'compact';

  c.front = `<div class="mcq-card" data-qid="${qNum}" data-shuffle="false">
  <div class="question-number">문제 ${qNum}</div>
  <div class="mcq-stem">
    ${sourceBadge}<div class="stem-ocr-text">${escapeHtml(c.stemText || '')}</div>${imgHtml}
  </div>
  <div class="mcq-options ${optCompactClass}">${choicesHtml}</div>
  <div class="mcq-help">1~${choicesList.length}번 키 또는 보기를 눌러 답을 선택하세요.</div>
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

function setChoiceCount(count) {
  _choiceCount = count;
  const row5 = document.getElementById('choiceRow5');
  const addZone = document.getElementById('addChoice5Zone');
  if (count === 4) {
    if (row5) row5.style.display = 'none';
    if (addZone) addZone.style.display = 'block';
    // 5번이 정답으로 체크되어 있다면 1번으로 자동 이동
    const radio5 = document.getElementById('radioChoice5');
    if (radio5 && radio5.checked) {
      const radio1 = document.getElementById('radioChoice1');
      if (radio1) radio1.checked = true;
    }
  } else {
    if (row5) row5.style.display = 'flex';
    if (addZone) addZone.style.display = 'none';
  }
}

function toggleRemoveImage() {
  _cardImageRemoved = !_cardImageRemoved;
  updateImageZoneUI();
}

function updateImageZoneUI() {
  const prevWrapper = document.getElementById('editImagePreviewWrapper');
  const notice = document.getElementById('editImageRemovedNotice');
  const btnRemove = document.getElementById('btnToggleRemoveImage');
  if (_cardImageRemoved) {
    if (prevWrapper) prevWrapper.style.opacity = '0.25';
    if (notice) notice.style.display = 'flex';
    if (btnRemove) btnRemove.style.display = 'none';
  } else {
    if (prevWrapper) prevWrapper.style.opacity = '1';
    if (notice) notice.style.display = 'none';
    if (btnRemove) btnRemove.style.display = 'inline-block';
  }
}

function openCardEditor() {
  const c = cur();
  if (!c) {
    toast('수정할 카드가 없습니다.');
    return;
  }
  _currentEditingCard = c;
  _cardImageRemoved = !!c.removeImage;

  const qNum = c.qid || (c.id ? c.id.replace('mgmt_', '') : '');
  const titleEl = document.getElementById('editModalTitle');
  if (titleEl) titleEl.textContent = `문제 ${qNum} 내용 수정`;

  const srcEl = document.getElementById('editSourceTag');
  if (srcEl) srcEl.value = c.sourceTag || '';

  const stemEl = document.getElementById('editStem');
  if (stemEl) stemEl.value = c.stemText || '';

  // 이미지 영역 처리
  const imgZone = document.getElementById('editImageZone');
  const imgPrev = document.getElementById('editImagePreview');
  let imgSrc = '';
  if (c.front) {
    const m = c.front.match(/<img[^>]+src=["']([^"']+)["']/i);
    if (m) imgSrc = m[1];
  }
  if (imgSrc) {
    if (imgPrev) imgPrev.src = imgSrc;
    if (imgZone) imgZone.style.display = 'flex';
    updateImageZoneUI();
  } else {
    if (imgZone) imgZone.style.display = 'none';
  }

  // 보기 처리 (4지/5지선다 여부 감지)
  const choices = c.choices || [];
  const has5th = choices.length >= 5 && (choices[4] || '').replace(/^[1-5]번:\\s*/, '').trim().length > 0;
  setChoiceCount(has5th ? 5 : 4);

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

  // 보기 수집 (4지선다면 4번까지만, 5번이 채워져있으면 5번까지)
  const newChoices = [];
  const limit = (_choiceCount === 4) ? 4 : 5;
  for (let i = 1; i <= limit; i++) {
    const el = document.getElementById(`editChoice${i}`);
    const text = el ? el.value.trim() : '';
    newChoices.push(`${i}번: ${text}`);
  }

  let selectedCorrect = 1;
  const checkedRadio = document.querySelector('input[name="editCorrectChoice"]:checked');
  if (checkedRadio) {
    selectedCorrect = Number(checkedRadio.value);
  }
  if (_choiceCount === 4 && selectedCorrect > 4) {
    selectedCorrect = 1;
  }

  // 카드 객체 업데이트
  c.sourceTag = newSourceTag;
  c.stemText = newStem;
  c.choices = newChoices;
  c.correct = selectedCorrect;
  c.explanationText = newExp;
  c.removeImage = _cardImageRemoved;

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
    removeImage: _cardImageRemoved,
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
"""

content = content.replace("function showCard(){", EDITOR_JS + "\nfunction showCard(){", 1)
print("[+] 에디터 v2 JS 함수 주입 완료")

# ─────────────────────────────────────────────────────────────
# 5. loadData 완료 후 applyCustomEditsToData() 호출 주입
# ─────────────────────────────────────────────────────────────
if "BYID={}; const tags=new Set()" in content:
    content = content.replace("BYID={}; const tags=new Set()", "applyCustomEditsToData();\n  BYID={}; const tags=new Set()", 1)
    print("[+] loadData() 내 수정본 병합(applyCustomEditsToData) 주입 완료")

# ─────────────────────────────────────────────────────────────
# 6. 키보드 단축키 'e' 및 1~5번 키 처리 (보기 개수 가변 대응)
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

content = content.replace("document.addEventListener('keydown',e=>{", "document.addEventListener('keydown',e=>{" + EDIT_KEYBOARD_HOOK, 1)
print("[+] 키보드 단축키 주입 완료")

with open(TARGET_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] cards.html 카드 수정 에디터 시스템 v2 패치 성공!")
