import re

HTML_PATH = r"c:\Users\yoon\Downloads\management-cards\cards.html"

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CSS 수정: .mcq-option에 3열 그리드 적용 및 .mcq-ox-btn 스타일 추가
OLD_MCQ_OPT_CSS = """.mcq-option {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  border: 0.5px solid var(--c-sep);
  border-radius: var(--r-cell, 12px);
  background: var(--c-card);
  color: var(--c-label);
  cursor: pointer;
  text-align: left;
  font-size: var(--t-body, 16px);
  box-shadow: var(--sh-card);
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease, opacity 0.15s ease;
  box-sizing: border-box;
  user-select: none;
}"""

NEW_MCQ_OPT_CSS = """.mcq-option {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) auto;
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  border: 0.5px solid var(--c-sep);
  border-radius: var(--r-cell, 12px);
  background: var(--c-card);
  color: var(--c-label);
  cursor: pointer;
  text-align: left;
  font-size: var(--t-body, 16px);
  box-shadow: var(--sh-card);
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease, opacity 0.15s ease;
  box-sizing: border-box;
  user-select: none;
  gap: 8px;
}

/* OX 카드 저장 버튼 (디자인 시스템 보조 캡슐 규격) */
.mcq-ox-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-sec);
  background: var(--c-fill);
  border: 0.5px solid var(--c-sep);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;
  user-select: none;
}
.mcq-ox-btn:hover {
  background: var(--c-acc-tint);
  color: var(--c-acc);
  border-color: var(--c-acc);
}
.mcq-ox-btn.saved {
  background: var(--c-acc-tint);
  color: var(--c-acc);
  border-color: var(--c-acc);
  font-weight: 700;
}"""

if OLD_MCQ_OPT_CSS in text:
    text = text.replace(OLD_MCQ_OPT_CSS, NEW_MCQ_OPT_CSS, 1)
    print("[1] CSS replacement succeeded!")
else:
    print("[!] Warning: OLD_MCQ_OPT_CSS not found directly, trying regex...")
    text = re.sub(
        r'\.mcq-option\s*\{\s*display:\s*grid;\s*grid-template-columns:\s*38px\s*minmax\(0,\s*1fr\);',
        '.mcq-option {\n  display: grid;\n  grid-template-columns: 38px minmax(0, 1fr) auto;\n  gap: 8px;',
        text
    )
    if '.mcq-ox-btn' not in text:
        text = text.replace('.mcq-option:hover {', """/* OX 카드 저장 버튼 (디자인 시스템 보조 캡슐 규격) */
.mcq-ox-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-sec);
  background: var(--c-fill);
  border: 0.5px solid var(--c-sep);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;
  user-select: none;
}
.mcq-ox-btn:hover {
  background: var(--c-acc-tint);
  color: var(--c-acc);
  border-color: var(--c-acc);
}
.mcq-ox-btn.saved {
  background: var(--c-acc-tint);
  color: var(--c-acc);
  border-color: var(--c-acc);
  font-weight: 700;
}

.mcq-option:hover {""", 1)
        print("[1] CSS regex replacement succeeded!")

# 2. 이모지 제거: 📄, 📝 제거
text = text.replace('📄 문제 PDF', '문제 PDF')
text = text.replace('📝 답지 PDF', '답지 PDF')
print("[2] Emoji removal completed!")

# 3. OX 저장 로직 주입
OX_JS_LOGIC = """
// ─── OX 카드 저장 및 관리 ───
const MCQ_OX_KEY = 'mgmt_ox_cards_v1';

function getOxCardsMap() {
  try {
    return JSON.parse(localStorage.getItem(MCQ_OX_KEY) || '{}');
  } catch (_) {
    return {};
  }
}

function isOxSaved(qid, origNum) {
  const map = getOxCardsMap();
  const oxId = 'mgmt_ox_' + qid + '_' + origNum;
  return !!map[oxId];
}

function toggleSaveOxCard(c, origNum, choiceText, btn) {
  if (!c || !origNum) return;
  const qid = c.qid || (c.id && c.id.replace('mgmt_', '')) || '0000';
  const oxId = 'mgmt_ox_' + qid + '_' + origNum;
  const map = getOxCardsMap();

  if (map[oxId]) {
    delete map[oxId];
    try { localStorage.setItem(MCQ_OX_KEY, JSON.stringify(map)); } catch (_) {}
    if (typeof DATA !== 'undefined' && Array.isArray(DATA)) {
      const idx = DATA.findIndex(x => x.id === oxId);
      if (idx !== -1) DATA.splice(idx, 1);
    }
    if (btn) {
      btn.classList.remove('saved');
      btn.textContent = 'OX';
    }
    toast('OX 저장을 해제했어요');
  } else {
    const correct = c.correct || Number(document.querySelector('.mcq-result')?.dataset?.correct);
    const stem = (c.stemText || c.front || '');
    const isNegative = /(옳지\\s*않|틀린|틀리게|아닌|적절하지\\s*않|부적절|거리.*먼|잘못)/.test(stem);

    let isO = true;
    if (correct) {
      if (isNegative) {
        isO = (Number(origNum) !== Number(correct));
      } else {
        isO = (Number(origNum) === Number(correct));
      }
    }
    const oxAnswer = isO ? 'O' : 'X';
    let exp = c.explanationText || '';
    if (!exp && c.note) exp = c.note;

    const oxCard = {
      id: oxId,
      qid: qid + '_' + origNum,
      subj: (c.subj || '경영학') + ' [OX]',
      typ: 'OX',
      front: '〔문 ' + qid + ' · 보기 ' + origNum + '〕\\n' + choiceText,
      back: '정답: ' + oxAnswer + (exp ? '\\n\\n해설: ' + exp : ''),
      note: exp,
      tags: [(c.subj || '경영학') + ' [OX]', 'OX선지', '문 ' + qid],
      probPage: c.probPage,
      ansPage: c.ansPage,
      sourceTag: c.sourceTag || ''
    };

    map[oxId] = oxCard;
    try { localStorage.setItem(MCQ_OX_KEY, JSON.stringify(map)); } catch (_) {}

    if (typeof DATA !== 'undefined' && Array.isArray(DATA)) {
      if (!DATA.some(x => x.id === oxId)) {
        DATA.push(oxCard);
      }
    }

    if (btn) {
      btn.classList.add('saved');
      btn.textContent = '저장됨';
    }
    toast('OX 카드로 저장했어요 (' + oxAnswer + ')');
  }
}

function restoreSavedOxCards() {
  try {
    const map = getOxCardsMap();
    if (typeof DATA !== 'undefined' && Array.isArray(DATA)) {
      for (const id in map) {
        if (!DATA.some(x => x.id === id)) {
          DATA.push(map[id]);
        }
      }
    }
  } catch (_) {}
}
"""

if 'const MCQ_OX_KEY' not in text:
    text = text.replace("const MCQ_ELIM_KEY = 'mgmt_eliminated_v1';", OX_JS_LOGIC + "\nconst MCQ_ELIM_KEY = 'mgmt_eliminated_v1';")
    print("[3] OX JS logic injected!")

# 4. runCardScripts 안에서 각 보기 버튼에 oxBtn 주입
OLD_RUN_BTNS = """    // 좌클릭 -> 정답 선택 (소거되어 있었으면 소거 해제 + 선택)
    btn.onclick = (e) => {"""

NEW_RUN_BTNS = """    // 4. OX 저장 캡슐 버튼
    const qid = c.qid || (c.id && c.id.replace('mgmt_', '')) || '0000';
    let oxBtn = btn.querySelector('.mcq-ox-btn');
    if (!oxBtn) {
      oxBtn = document.createElement('span');
      oxBtn.className = 'mcq-ox-btn';
      btn.appendChild(oxBtn);
    }
    const alreadySaved = isOxSaved(qid, orig);
    oxBtn.className = 'mcq-ox-btn' + (alreadySaved ? ' saved' : '');
    oxBtn.textContent = alreadySaved ? '저장됨' : 'OX';
    oxBtn.title = '이 선지를 OX 카드로 저장';
    oxBtn.onclick = (e) => {
      e.stopPropagation();
      e.preventDefault();
      const choiceTextEl = btn.querySelector('.mcq-choice-text');
      const choiceText = choiceTextEl ? choiceTextEl.textContent.trim() : '';
      toggleSaveOxCard(c, orig, choiceText, oxBtn);
    };

    // 좌클릭 -> 정답 선택 (소거되어 있었으면 소거 해제 + 선택)
    btn.onclick = (e) => {"""

if OLD_RUN_BTNS in text and 'let oxBtn' not in text:
    text = text.replace(OLD_RUN_BTNS, NEW_RUN_BTNS, 1)
    print("[4] oxBtn injection succeeded!")

# 5. DATA 로드 후 restoreSavedOxCards() 호출 연결
if 'restoreSavedOxCards()' not in text:
    text = text.replace("initData();", "initData(); restoreSavedOxCards();", 1)
    print("[5] restoreSavedOxCards hook connected!")

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("[OK] All patches applied successfully!")
