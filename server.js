import express from 'express';
import fetch from 'node-fetch';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 8000;
const OLLAMA_URL = 'http://127.0.0.1:11434/api/generate';

app.use(express.json());
app.use(express.static(__dirname));

app.post('/api/chat', async (req, res) => {
    const { prompt, history, engine, model, apiKey } = req.body;

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
     \`"Date"\`: { "Year", "Month", "Week" }, 
     \`"Time_Flow"\`: "내정" 또는 "전투",
     \`"Resources"\`: { "Gold", "Rice" },
     \`"Status"\`: { "Military": 군사수, "Generals": 장수수, "Fame": 유명세(0-100), "Charm": 매력도(0-100) },
     \`"Officers"\`: [ { "Name": "장수명", "War": 0-100, "Int": 0-100, "Pol": 0-100, "Loyalty": 0-100 } ],
     \`"Items"\`: [ "소지보물명" ],
     \`"Territory"\`: { "City": "현재도시명", "ControlledBlocks": [ [R, C, "FactionColor"] ] },
     \`"Location_Coords"\`: { "x": 0~100, "y": 0~100 }
6. 응답 본문은 반드시 다음 세 구역으로 명확히 구분하여 작성하십시오:
   - **[해설]**: 현재의 정세와 배경에 대한 소설적 묘사
   - **[대사: 인물명]**: 주요 인물(군주 혹은 장수)의 성명을 병기하고, 그들의 고뇌나 결기가 담긴 직접 화법을 기술하십시오. (예: [대사: 조조])
   - **[선택지]**: 플레이어가 선택할 수 있는 4가지 핵심 선택지 (번호 1~4)
7. 각 구역 사이에는 반드시 빈 줄을 두어 전령이 이를 명확히 구분할 수 있게 하십시오.`;

    // Format history for context (keep only last 10 turns to save tokens)
    const historyLimit = 10 * 2; // 10 pairs of user/model messages
    const limitedHistory = (history || []).slice(-historyLimit);

    const formattedHistory = limitedHistory.map(msg => ({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
    }));

    try {
        if (engine === 'gemini') {
            if (!apiKey) throw new Error('Gemini API 키가 필요합니다.');
            // Use the model passed from frontend
            const geminiModel = model || 'gemini-2.0-flash';
            const geminiUrl = `https://generativelanguage.googleapis.com/v1/models/${geminiModel}:generateContent?key=${apiKey}`;

            // Build contents with system instruction at the start
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

            if (data.error) throw new Error(`제미나이 API 오류: ${data.error.message}`);
            if (!data.candidates || data.candidates.length === 0) {
                if (data.promptFeedback && data.promptFeedback.blockReason) {
                    throw new Error(`안전 정책에 의해 차단되었습니다. 사유: ${data.promptFeedback.blockReason}`);
                }
                throw new Error('대답을 생성할 수 없습니다. (결과값 없음)');
            }

            const text = data.candidates[0].content.parts[0].text;
            res.json({ response: text });
        } else {
            // Ollama: Combine history into a single prompt for consistency
            let ollamaPrompt = `시스템 지침: ${systemInstruction}\n\n`;
            history.forEach(msg => {
                ollamaPrompt += `${msg.role === 'user' ? '사용자' : '엔진'}: ${msg.content}\n`;
            });
            ollamaPrompt += `사용자: ${prompt}\n엔진: `;

            const response = await fetch(OLLAMA_URL, {
                method: 'POST',
                body: JSON.stringify({
                    model: 'llama3:latest',
                    prompt: ollamaPrompt,
                    stream: false,
                    options: { temperature: 0.7, num_ctx: 4096 }
                })
            });
            const data = await response.json();
            res.json({ response: data.response });
        }
    } catch (error) {
        console.error('Engine Error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`천하도지 v8.8 서버가 실행되었습니다.`);
    console.log(`로컬 접속: http://localhost:${port}`);
    console.log(`Tailscale 접속: http://[당신의-Tailscale-IP]:${port}`);
});
