# Social Scraper

給社群用戶使用的公開帳號分析平台。

使用者在首頁輸入 `Instagram`、`Threads` 帳號或個人頁連結後，系統會先抓取公開個人資料與貼文文字，再交給 `Groq openai/gpt-oss-120b` 做 AI 分析，最後在前端顯示簡潔的結果頁。

## 功能

- 支援分析 `Threads`、`Instagram`，或兩者一起分析
- 自動抓取公開帳號的基本資料、頭貼與貼文文字
- AI 分析必出項目：
  - 個性
  - 興趣
  - 發生過的重要事件或活動
  - MBTI
  - 建議聊天話題
- 有線索時才顯示推測資訊：
  - 年齡
  - 生日
  - 身高
  - 居住區域
  - 學校 / 公司
  - 星座
- 會根據明顯線索做推測，例如：
  - `jerry921102` 這類帳號數字可能代表生日
  - `mcu`、`nttu` 這類常見學校縮寫
- 不使用資料庫
- 分析結果只保存在使用者瀏覽器的 `localStorage`

## 架構

- `backend/`
  - FastAPI API
  - Instagram / Threads scraper
  - Groq AI 分析整合
- `frontend/`
  - Vue 3 + Vite + Pinia
  - 首頁搜尋流程
  - AI 分析結果頁
  - localStorage 歷史紀錄

## 環境需求

- Python 3.10+
- Node.js 18+
- npm
- Playwright Chromium
- Groq API Key

## 環境變數

前後端已拆開，不共用 `.env`。

### Backend env

先建立：

```bash
cp backend/.env.example backend/.env
```

目前支援的 backend 環境變數：

- `GROQ_API_KEY`
  - 必填，Groq API Key
- `GROQ_MODEL`
  - 選填，預設為 `openai/gpt-oss-120b`
- `GROQ_BASE_URL`
  - 選填，預設為 `https://api.groq.com/openai/v1`

Backend 會自動讀取 `backend/.env`。

### Frontend env

先建立：

```bash
cp frontend/.env.example frontend/.env
```

目前支援的 frontend 環境變數：

- `VITE_API_BASE_URL`
  - 選填
  - 本機開發若使用 Vite proxy，可留空
  - 若前後端部署在不同網域，請填入 backend 位址，例如 `https://api.example.com`

## 啟動方式

### 1. 安裝 backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
cp backend/.env.example backend/.env
```

### 2. 啟動 backend

```bash
uvicorn app.main:app --reload --app-dir backend
```

預設 API 位址：

```text
http://127.0.0.1:8000
```

### 3. 安裝 frontend

```bash
cd frontend
npm install
cp .env.example .env
```

### 4. 啟動 frontend

```bash
npm run dev
```

預設前端位址：

```text
http://127.0.0.1:5173
```

## 使用流程

1. 開啟首頁
2. 輸入 `@username`、Instagram 個人頁連結，或 Threads 個人頁連結
3. 選擇要分析：
   - `Threads`
   - `Instagram`
   - `一起分析`
4. 送出後，系統會：
   - 爬取公開資料
   - 整理貼文與線索
   - 呼叫 Groq 模型產生分析結果
5. 分析結果頁會顯示：
   - 頭貼
   - 個性摘要
   - MBTI 與信心
   - 興趣
   - 建議聊天切入點
   - 重要事件 / 活動
   - 可推測資訊
   - 各平台資料來源摘要

## API

### `POST /api/analyze`

Request:

```json
{
  "username": "jerry921102",
  "platforms": ["threads", "instagram"]
}
```

也可以只傳一個平台：

```json
{
  "username": "jerry921102",
  "platforms": ["threads"]
}
```

Response 會包含：

- `results`
  - 各平台爬取結果
- `analysis`
  - AI 結構化分析內容
- `completed_platforms`
  - 成功取得資料的平台
- `failed_platforms`
  - 失敗的平台

## 資料儲存說明

- 後端不使用 SQLite 或其他資料庫
- 分析結果不會寫入 server 端資料庫
- 前端會把分析結果存進瀏覽器 `localStorage`
- 若清除瀏覽器資料，歷史分析紀錄也會一起消失
- 前後端環境變數分開管理，不共用同一個 `.env`

## 注意事項

- 只支援公開帳號
- 抓取速度與成功率會受平台限制影響
- AI 推測資訊不是官方資料，應視為根據公開線索的合理推論
- 若平台其中一邊抓取失敗，系統仍會使用另一邊可取得的資料完成分析

## 驗證

目前已驗證：

```bash
cd frontend && npm run build
PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall backend/app backend/services
```

## 主要檔案

- `backend/app/routers/scraper.py`
  - 分析 API 入口
- `backend/services/ai_analysis.py`
  - Groq prompt、schema 與後處理邏輯
- `frontend/src/views/HomeView.vue`
  - 首頁搜尋流程
- `frontend/src/views/AnalysisView.vue`
  - 分析結果頁
- `frontend/src/stores/scraper.js`
  - API 呼叫與 localStorage 管理
