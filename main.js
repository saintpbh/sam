const textDisplay = document.getElementById('text-display');
const statDate = document.getElementById('stat-date');
const statPhase = document.getElementById('stat-phase');
const statGold = document.getElementById('stat-gold');
const statRice = document.getElementById('stat-rice');
const statMilitary = document.getElementById('stat-military');
const statGenerals = document.getElementById('stat-generals');
const statFame = document.getElementById('stat-fame');
const statCharm = document.getElementById('stat-charm');
const openOfficers = document.getElementById('open-officers');
const openItems = document.getElementById('open-items');
const officersModal = document.getElementById('officers-modal');
const itemsModal = document.getElementById('items-modal');
const officerListContent = document.getElementById('officer-list-content');
const itemListContent = document.getElementById('item-list-content');
const territoryGrid = document.getElementById('territory-grid');
const currentCityName = document.getElementById('current-city-name');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const choiceContainer = document.getElementById('choice-container');

// Settings Elements
const openSettings = document.getElementById('open-settings');
const settingsModal = document.getElementById('settings-modal');
const engineSelect = document.getElementById('engine-select');
const geminiModelContainer = document.getElementById('gemini-model-container');
const geminiModelSelect = document.getElementById('gemini-model-select');
const geminiKeyContainer = document.getElementById('gemini-key-container');
const geminiApiKey = document.getElementById('gemini-api-key');
const groqModelContainer = document.getElementById('groq-model-container');
const groqModelSelect = document.getElementById('groq-model-select');
const groqKeyContainer = document.getElementById('groq-key-container');
const groqApiKey = document.getElementById('groq-api-key');
const saveSettings = document.getElementById('save-settings');

const systemInstruction = `
[엔진: 천하도지 v8.8 - 삼국지 사극 모드]
1. 당신은 **중국 삼국시대(Samgukji)**를 배경으로 하는 '3인칭 관찰자/해설자'입니다. 절대로 조선시대나 다른 시대를 배경으로 하지 마십시오.
2. 모든 서사는 한나라 말기 풍운이 일던 **삼국지(Three Kingdoms of China)**의 인물과 사건을 바탕으로 합니다.
3. 말투는 단순히 "~하오"를 반복하는 사극풍이 아니라, **나관중의 '삼국지연의'나 이문열 평역 삼국지**와 같은 고전 소설의 서사적이고 중후한 문체를 사용하십시오.
   - 문장 끝을 "~다", "~도다", "~였으니", "~지 않겠는가" 등 다양하게 변주하여 지루함을 없애십시오.
   - 웅장한 비유와 인물의 내면 묘사를 곁들여 한 편의 대하소설을 읽는 듯한 느낌을 주십시오.
4. **절대로 영어를 사용하지 마십시오.** 모든 용어, 장수 이름, 지명은 한국어로 기술하십시오.
5. 매 응답 최상단에는 반드시 지시된 포맷의 JSON 블록을 포함해야 합니다.
   - JSON에는 반드시 다음 필드를 포함하십시오:
     "Date": { "Year", "Month", "Week" }, 
     "Time_Flow": "내정" 또는 "전투",
     "Resources": { "Gold", "Rice" },
     "Status": { "Military": 군사수, "Generals": 장수수, "Fame": 유명세(0-100), "Charm": 매력도(0-100) },
     "Officers": [ { "Name": "장수명", "War": 0-100, "Int": 0-100, "Pol": 0-100, "Loyalty": 0-100 } ],
     "Items": [ "소지보물명" ],
     "Territory": { "City": "현재도시명", "ControlledBlocks": [ [R, C, "FactionColor"] ] },
     "Location_Coords": { "x": 0~100, "y": 0~100 }
6. 응답 본문은 반드시 다음 세 구역으로 명확히 구분하여 작성하십시오:
   - **[해설]**: 현재의 정세와 배경에 대한 소설적 묘사
   - **[대사: 인물명]**: 주요 인물(군주 혹은 장수)의 성명을 병기하고, 그들의 고뇌나 결기가 담긴 직접 화법을 기술하십시오. (예: [대사: 조조])
   - **[선택지]**: 플레이어가 선택할 수 있는 4가지 핵심 선택지 (번호 1~4)
7. 각 구역 사이에는 반드시 빈 줄을 두어 전령이 이를 명확히 구분할 수 있게 하십시오.`;

let gameState = {
    history: [],
    engine: localStorage.getItem('chunhadoji_engine') || 'gemini',
    geminiModel: localStorage.getItem('chunhadoji_gemini_model') || 'gemini-2.0-flash',
    groqModel: localStorage.getItem('chunhadoji_groq_model') || 'llama-3.3-70b-versatile',
    apiKey: localStorage.getItem('chunhadoji_gemini_key') || '',
    groqApiKey: localStorage.getItem('chunhadoji_groq_key') || ''
};

// Initialize Settings UI
engineSelect.value = gameState.engine;
geminiModelSelect.value = gameState.geminiModel;
geminiApiKey.value = gameState.apiKey;
groqModelSelect.value = gameState.groqModel;
groqApiKey.value = gameState.groqApiKey;

function updateSettingsVisibility() {
    const isGemini = engineSelect.value === 'gemini';
    const isGroq = engineSelect.value === 'groq';
    geminiModelContainer.style.display = isGemini ? 'block' : 'none';
    geminiKeyContainer.style.display = isGemini ? 'block' : 'none';
    groqModelContainer.style.display = isGroq ? 'block' : 'none';
    groqKeyContainer.style.display = isGroq ? 'block' : 'none';
}
updateSettingsVisibility();

openSettings.onclick = () => settingsModal.style.display = 'flex';
engineSelect.onchange = updateSettingsVisibility;
saveSettings.onclick = () => {
    gameState.engine = engineSelect.value;
    gameState.geminiModel = geminiModelSelect.value;
    gameState.groqModel = groqModelSelect.value;
    gameState.apiKey = geminiApiKey.value;
    gameState.groqApiKey = groqApiKey.value;
    localStorage.setItem('chunhadoji_engine', gameState.engine);
    localStorage.setItem('chunhadoji_gemini_model', gameState.geminiModel);
    localStorage.setItem('chunhadoji_groq_model', gameState.groqModel);
    localStorage.setItem('chunhadoji_gemini_key', gameState.apiKey);
    localStorage.setItem('chunhadoji_groq_key', gameState.groqApiKey);
    settingsModal.style.display = 'none';
};

// Record (Save/Load) UI Hooks
const openRecord = document.getElementById('open-record');
const recordModal = document.getElementById('record-modal');
const saveBtnLocal = document.getElementById('save-btn-local');
const loadBtnLocal = document.getElementById('load-btn-local');
const closeRecord = document.getElementById('close-record');
const saveStatusMsg = document.getElementById('save-status-msg');

openRecord.onclick = () => {
    saveStatusMsg.textContent = "";
    recordModal.style.display = 'flex';
};
closeRecord.onclick = () => recordModal.style.display = 'none';

saveBtnLocal.onclick = () => {
    try {
        const saveData = {
            history: gameState.history,
            timestamp: new Date().getTime()
        };
        localStorage.setItem('chunhadoji_save_data', JSON.stringify(saveData));
        saveStatusMsg.textContent = "기록이 성공적으로 저장되었습니다.";
        saveStatusMsg.style.color = "var(--gold)";
    } catch (e) {
        saveStatusMsg.textContent = "저장 중 오류가 발생했습니다.";
        saveStatusMsg.style.color = "red";
    }
};

loadBtnLocal.onclick = () => {
    try {
        const rawData = localStorage.getItem('chunhadoji_save_data');
        if (!rawData) {
            saveStatusMsg.textContent = "저장된 기록이 없사옵니다.";
            saveStatusMsg.style.color = "red";
            return;
        }
        const savedData = JSON.parse(rawData);

        // Restore State
        gameState.history = savedData.history;

        // Re-render UI from the last state in history
        textDisplay.innerHTML = "";
        appLog("기록을 성공적으로 불러왔사옵니다.", "system");

        let lastNarrative = "";
        let lastJson = null;

        gameState.history.forEach(msg => {
            if (msg.role === 'assistant') {
                const jsonMatch = msg.content.match(/```json\n([\s\S]*?)\n```/);
                if (jsonMatch) {
                    try {
                        lastJson = JSON.parse(jsonMatch[1]);
                        lastNarrative = msg.content.replace(jsonMatch[0], '').trim();
                    } catch (e) { }
                }
            }
        });

        if (lastJson) updateStats(lastJson);
        if (lastNarrative) {
            // Re-process narrative chunks for the last state
            const mapMatch = lastNarrative.match(/🚩 \[전국 현황\]([\s\S]*?)🚩 \[현재 챕터명 및 서사\]/);
            if (mapMatch) lastNarrative = lastNarrative.replace(mapMatch[0], '🚩 [현재 챕터명 및 서사]');

            const chunkTags = ['[해설]', '[대사', '[선택지]'];
            for (let tag of chunkTags) {
                const start = lastNarrative.indexOf(tag);
                if (start !== -1) {
                    // Find end (next tag)
                    let nextStart = -1;
                    for (let otherTag of chunkTags) {
                        if (otherTag === tag) continue;
                        const pos = lastNarrative.indexOf(otherTag);
                        if (pos !== -1 && (nextStart === -1 || pos < nextStart)) nextStart = pos;
                    }
                    const content = nextStart !== -1 ? lastNarrative.slice(start, nextStart) : lastNarrative.slice(start);
                    appLog(content.trim());
                }
            }
        }

        renderChoiceButtons();
        recordModal.style.display = 'none';
    } catch (e) {
        console.error(rawData);
        saveStatusMsg.textContent = "불러오기 중 오류가 발생했습니다.";
        saveStatusMsg.style.color = "red";
    }
};

openOfficers.onclick = () => officersModal.style.display = 'flex';
openItems.onclick = () => itemsModal.style.display = 'flex';

async function appLog(text, type = 'narrative') {
    const p = document.createElement('div');
    p.className = 'fade-in section-block';

    // Assign specific classes based on content headers or type
    if (text.startsWith('[해설]')) p.classList.add('section-explanation');
    else if (text.startsWith('[대사')) p.classList.add('section-dialogue');
    else if (text.startsWith('[선택지]')) p.classList.add('section-selection');

    if (type === 'system') p.style.color = '#888';
    if (type === 'choice') p.style.color = 'var(--gold)';

    // Parse Markdown basic (bold, line breaks)
    let formattedText = text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    p.innerHTML = formattedText;
    textDisplay.appendChild(p);
    textDisplay.scrollTop = textDisplay.scrollHeight;
}

const playerMarker = document.getElementById('player-marker');

function animateValue(obj, start, end, duration) {
    if (start === end) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        obj.textContent = value.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.textContent = end.toLocaleString();
            obj.classList.add('stat-changed');
            setTimeout(() => obj.classList.remove('stat-changed'), 500);
        }
    };
    window.requestAnimationFrame(step);
}

function updateStats(jsonData) {
    if (!jsonData) return;

    if (jsonData.Date) {
        statDate.textContent = `${jsonData.Date.Year}년 ${jsonData.Date.Month}월 ${jsonData.Date.Week}주`;
    }
    if (jsonData.Time_Flow) {
        // Translation mapping for phases
        const phaseMap = { 'Normal': '내정', 'War': '전투', 'Normal_Phase': '내정', 'War_Phase': '전투' };
        statPhase.textContent = phaseMap[jsonData.Time_Flow] || jsonData.Time_Flow;
    }

    if (jsonData.Resources) {
        const oldGold = parseInt(statGold.textContent.replace(/,/g, '')) || 0;
        const oldRice = parseInt(statRice.textContent.replace(/,/g, '')) || 0;
        animateValue(statGold, oldGold, jsonData.Resources.Gold, 1000);
        animateValue(statRice, oldRice, jsonData.Resources.Rice, 1000);
    }

    if (jsonData.Status) {
        const oldMil = parseInt(statMilitary.textContent.replace(/,/g, '')) || 0;
        const oldGen = parseInt(statGenerals.textContent.replace(/,/g, '')) || 0;
        const oldFame = parseInt(statFame.textContent.replace(/,/g, '')) || 0;
        const oldCharm = parseInt(statCharm.textContent.replace(/,/g, '')) || 0;

        animateValue(statMilitary, oldMil, jsonData.Status.Military || 0, 1000);
        animateValue(statGenerals, oldGen, jsonData.Status.Generals || 0, 1000);
        animateValue(statFame, oldFame, jsonData.Status.Fame || 0, 1000);
        animateValue(statCharm, oldCharm, jsonData.Status.Charm || 0, 1000);
    }

    if (jsonData.Officers) {
        officerListContent.innerHTML = jsonData.Officers.map(o => `
            <div class="officer-pill">
                <div style="color:var(--gold); font-weight:bold;">${o.Name}</div>
                <div style="font-size:0.8rem; color:#aaa;">무:${o.War} 지:${o.Int} 정:${o.Pol} 충:${o.Loyalty}</div>
            </div>
        `).join('');
    }

    if (jsonData.Items) {
        itemListContent.innerHTML = jsonData.Items.map(item => `
            <div class="item-badge">💎 ${item}</div>
        `).join('');
    }

    if (jsonData.Territory) {
        currentCityName.textContent = jsonData.Territory.City || '-';
        if (jsonData.Territory.ControlledBlocks) {
            territoryGrid.innerHTML = '';
            // Create 8x5 grid
            for (let r = 0; r < 5; r++) {
                for (let c = 0; c < 8; c++) {
                    const block = document.createElement('div');
                    block.className = 'territory-block';
                    const controlled = jsonData.Territory.ControlledBlocks.find(b => b[0] === r && b[1] === c);
                    if (controlled) {
                        block.style.background = controlled[2]; // Faction color
                    }
                    territoryGrid.appendChild(block);
                }
            }
        }
    }

    // Update Map Marker
    if (jsonData.Location_Coords) {
        const { x, y } = jsonData.Location_Coords;
        playerMarker.style.left = `${x}%`;
        playerMarker.style.top = `${y}%`;
        playerMarker.style.display = 'block';

        // Update Tactical View (8x5 grid)
        const col = Math.min(Math.floor(x / 12.5), 7);
        const row = Math.min(Math.floor(y / 20), 4);
        const tacticalMap = document.getElementById('tactical-map');
        tacticalMap.src = `./public/tiles/tile_${row}_${col}.png`;

        // Handle image error (tile not generated yet)
        tacticalMap.onerror = () => {
            tacticalMap.src = './map.png'; // Fallback to main map
        };
    }
}

// Fullscreen Toggle
document.getElementById('toggle-fullscreen').onclick = () => {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
};

const continueIndicator = document.getElementById('continue-indicator');
let waitingForNext = false;
let nextResolver = null;

function waitForNext() {
    waitingForNext = true;
    continueIndicator.style.display = 'block';
    textDisplay.scrollTop = textDisplay.scrollHeight;
    return new Promise(resolve => {
        nextResolver = resolve;
    });
}

function handleNext() {
    if (waitingForNext && nextResolver) {
        waitingForNext = false;
        continueIndicator.style.display = 'none';
        const resolve = nextResolver;
        nextResolver = null;
        resolve();
    }
}

// Global click/keypress for paging
document.addEventListener('click', (e) => {
    if (waitingForNext) handleNext();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && waitingForNext) {
        e.preventDefault();
        handleNext();
    }
});

const portraitBox = document.getElementById('portrait-box');
const speakerPortrait = document.getElementById('speaker-portrait');
const speakerName = document.getElementById('speaker-name');

const portraitMap = {
    '유비': 'liu_bei.png', '관우': 'guan_yu.png', '장비': 'zhang_fei.png', '제갈량': 'zhuge_liang.png',
    '조운': 'zhao_yun.png', '마초': 'ma_chao.png', '황충': 'huang_zhong.png', '위연': 'wei_yan.png',
    '방통': 'pang_tong.png', '강유': 'jiang_wei.png', '조조': 'cao_cao.png', '하후돈': 'xiahou_dun.png',
    '하후연': 'xiahou_yuan.png', '장료': 'zhang_liao.png', '서황': 'xu_huang.png', '장합': 'zhang_he.png',
    '조인': 'cao_ren.png', '사마의': 'sima_yi.png', '곽가': 'guo_jia.png', '순욱': 'xun_yu.png',
    '손견': 'sun_jian.png', '손책': 'sun_ce.png', '손권': 'sun_quan.png', '주유': 'zhou_yu.png',
    '노숙': 'lu_su.png', '여몽': 'lu_meng.png', '육손': 'lu_xun.png', '감녕': 'gan_ning.png',
    '태사자': 'taishi_ci.png', '황개': 'huang_gai.png', '여포': 'lu_bu.png', '초선': 'diaochan.png',
    '동탁': 'dong_zhuo.png', '원소': 'yuan_shao.png', '원술': 'yuan_shu.png', '장각': 'zhang_jue.png',
    '공손찬': 'gongsun_zan.png', '맹획': 'meng_huo.png', '축융': 'zhu_rong.png', '가후': 'jia_xu.png'
};

function showPortrait(tagName) {
    portraitBox.style.display = 'none';
    const nameMatch = tagName.match(/\[대사:\s*(.*?)\]/);
    if (nameMatch) {
        const name = nameMatch[1].trim();
        const filename = portraitMap[name];
        if (filename) {
            speakerPortrait.src = `./public/portraits/${filename}`;
            speakerName.textContent = name;
            portraitBox.style.display = 'block';
            speakerPortrait.onerror = () => portraitBox.style.display = 'none';
        }
    }
}

async function callEngine(prompt) {
    appLog('명령을 하달하는 중...', 'system');

    try {
        let fullOutput = "";

        // Determine if we should use local server or direct API
        const isLocalServer = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

        // For simplicity and GitHub compatibility, we'll implement direct API calls here
        // If you still want to use the local Node.js server, you can uncomment the local fetch block.

        if (gameState.engine === 'gemini') {
            if (!gameState.apiKey) throw new Error('Gemini API 키가 필요합니다. 설정에서 입력해 주십시오.');

            const geminiUrl = `https://generativelanguage.googleapis.com/v1/models/${gameState.geminiModel}:generateContent?key=${gameState.apiKey}`;

            const formattedHistory = gameState.history.slice(-20).map(msg => ({
                role: msg.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: msg.content }]
            }));

            const contents = [
                { role: 'user', parts: [{ text: `시스템 지침: ${systemInstruction}` }] },
                ...formattedHistory,
                { role: 'user', parts: [{ text: prompt }] }
            ];

            const response = await fetch(geminiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contents })
            });

            const data = await response.json();
            if (data.error) throw new Error(`Gemini API 오류: ${data.error.message}`);
            fullOutput = data.candidates[0].content.parts[0].text;

        } else if (gameState.engine === 'groq') {
            // Groq: OpenAI-compatible API
            if (!gameState.groqApiKey) throw new Error('Groq API 키가 필요합니다. 설정에서 입력해 주십시오.');

            const groqUrl = 'https://api.groq.com/openai/v1/chat/completions';

            const messages = [
                { role: 'system', content: systemInstruction },
                ...gameState.history.slice(-20).map(msg => ({
                    role: msg.role === 'assistant' ? 'assistant' : 'user',
                    content: msg.content
                })),
                { role: 'user', content: prompt }
            ];

            const response = await fetch(groqUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${gameState.groqApiKey}`
                },
                body: JSON.stringify({
                    model: gameState.groqModel,
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 2048
                })
            });

            const data = await response.json();
            if (data.error) throw new Error(`Groq API 오류: ${data.error.message}`);
            fullOutput = data.choices[0].message.content;

        } else {
            // Ollama: Direct call to local Ollama (requires CORS enabled on Ollama)
            // or fallback to local server if available
            const ollamaUrl = 'http://127.0.0.1:11434/api/generate';

            let ollamaPrompt = `시스템 지침: ${systemInstruction}\n\n`;
            gameState.history.slice(-10).forEach(msg => {
                ollamaPrompt += `${msg.role === 'user' ? '사용자' : '엔진'}: ${msg.content}\n`;
            });
            ollamaPrompt += `사용자: ${prompt}\n엔진: `;

            try {
                const response = await fetch(ollamaUrl, {
                    method: 'POST',
                    body: JSON.stringify({
                        model: 'llama3:latest',
                        prompt: ollamaPrompt,
                        stream: false,
                        options: { temperature: 0.7, num_ctx: 4096 }
                    })
                });
                const data = await response.json();
                fullOutput = data.response;
            } catch (e) {
                // If direct Ollama fails (likely CORS), try local server if on localhost
                if (isLocalServer) {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            prompt: prompt,
                            history: gameState.history,
                            engine: gameState.engine,
                            model: gameState.geminiModel,
                            apiKey: gameState.apiKey
                        })
                    });
                    const data = await response.json();
                    if (data.error) throw new Error(data.error);
                    fullOutput = data.response;
                } else {
                    throw new Error('Ollama에 연결할 수 없습니다. 로컬에서 Ollama가 실행 중이고 CORS가 설정되어 있는지 확인하거나, Gemini 엔진을 사용하십시오.');
                }
            }
        }

        // Split JSON and Narrative
        const jsonMatch = fullOutput.match(/```json\n([\s\S]*?)\n```/);
        let narrative = fullOutput;
        let jsonData = null;

        if (jsonMatch) {
            jsonData = JSON.parse(jsonMatch[1]);
            narrative = fullOutput.replace(jsonMatch[0], '').trim();
            updateStats(jsonData);
        }

        // Split Map and Text
        const mapMatch = narrative.match(/🚩 \[전국 현황\]([\s\S]*?)🚩 \[현재 챕터명 및 서사\]/);
        if (mapMatch) {
            narrative = narrative.replace(mapMatch[0], '🚩 [현재 챕터명 및 서사]');
        }

        // PAGING LOGIC: Split by [해설], [대사], [선택지] headers
        const chunkTags = ['[해설]', '[대사', '[선택지]'];
        const chunks = [];
        const foundTags = [];

        for (let i = 0; i < chunkTags.length; i++) {
            const currentTag = chunkTags[i];
            const start = narrative.indexOf(currentTag);
            if (start === -1) continue;

            let nextStart = -1;
            for (let j = i + 1; j < chunkTags.length; j++) {
                nextStart = narrative.indexOf(chunkTags[j]);
                if (nextStart !== -1) break;
            }

            const end = nextStart !== -1 ? nextStart : narrative.length;
            const content = narrative.slice(start, end).trim();
            if (content) {
                chunks.push(content);
                const actualTagMatch = content.match(/\[(.*?)\]/);
                foundTags.push(actualTagMatch ? `[${actualTagMatch[1]}]` : currentTag);
            }
        }

        // Display in steps
        for (let i = 0; i < chunks.length; i++) {
            portraitBox.style.display = 'none';
            if (foundTags[i].startsWith('[대사:')) {
                showPortrait(foundTags[i]);
            }

            await appLog(chunks[i]);
            if (i < chunks.length - 1) {
                await waitForNext();
            }
        }

        renderChoiceButtons();

        // Save to history
        gameState.history.push({ role: 'user', content: prompt });
        gameState.history.push({ role: 'assistant', content: fullOutput });

    } catch (error) {
        console.error(error);
        appLog(`전령 오류: ${error.message}`, 'system');
    }
}

function renderChoiceButtons() {
    choiceContainer.innerHTML = '';
    choiceContainer.style.display = 'flex';

    for (let i = 1; i <= 4; i++) {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = i;
        btn.onclick = () => {
            appLog(`> ${i}번 선택`, 'choice');
            callEngine(i.toString());
        };
        choiceContainer.appendChild(btn);
    }
}

sendBtn.addEventListener('click', () => {
    const cmd = userInput.value.trim();
    if (!cmd) return;
    appLog(`> ${cmd}`, 'choice');
    callEngine(cmd);
    userInput.value = '';
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendBtn.click();
});

// Initial Start Flow
function startNewGame() {
    appLog('천하도지 v8.8 엔진 가동 중...', 'system');
    appLog('어느 성세에 대업을 시작하시겠나이까? (연도를 선택하거나 직접 입력하시옵소서)');

    const years = [184, 190, 200, 208];
    choiceContainer.innerHTML = '';
    choiceContainer.style.display = 'flex';

    years.forEach(year => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.style.width = 'auto';
        btn.style.borderRadius = '4px';
        btn.style.padding = '10px 20px';
        btn.textContent = `${year}년`;
        btn.onclick = () => {
            appLog(`> ${year}년 선택`, 'choice');
            initializeGame(year);
        };
        choiceContainer.appendChild(btn);
    });
}

async function initializeGame(year) {
    const initPrompt = `천하도지 v8.8 엔진 가동. 삼국지 시대를 서기 ${year}년부터 시작합니다. 
    ${year}년 당시의 천하 정세에 맞는 군주 10명과 장수 10명을 번호와 함께 제시하고, 마지막에는 [신장수] 옵션을 주어 게임을 시작하게 하십시오. 
    모든 설명은 한글 사극 말투로 진행하되, 영어는 일절 사용하지 마십시오. 
    반드시 초기 위치 좌표(Location_Coords)를 포함하고, 본문은 [해설], [대사], [선택지]의 3구역으로 나누어 출력하십시오.`;

    callEngine(initPrompt);
}

startNewGame();
