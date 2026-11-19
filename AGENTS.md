# 心靈契合（Heart Alignment）專案 — Codex 開發指引

## 專案概述

「心靈契合：30天，走向彼此」是一個針對重視隱私與深度連結的成年單身者的封閉式活動網站。

## 技術棧

| 層 | 技術 |
|---|---|
| 後端 | Python 3.12 / FastAPI / Uvicorn |
| 前端 | React / TypeScript / Vite |
| 資料庫 | Google Cloud Firestore（本機用記憶體 stub） |
| AI | OpenAI API（`gpt-4o-mini` 預設） |
| 套件管理 | pip + pyproject.toml（後端）、npm（前端） |

## 專案結構（Monorepo）

```
2611-心靈契合-走向彼此/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI 路由（health、applications、chat）
│   │   ├── core/            # 設定、錯誤碼、port 介面
│   │   ├── db/              # Firestore / 記憶體 adapter
│   │   └── services/        # 業務邏輯（chat_service.py）
│   │   ├── scripts/         # 管理員 claim 等維運工具
│   ├── tests/
│   ├── Dockerfile            # Cloud Run 容器
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── api/             # API 呼叫層
│       ├── components/      # React 元件
│       └── router/          # 路由
├── .env                     # 本機密鑰（不提交 git）
├── .github/workflows/       # GitHub Pages／Cloud Run 自動部署
├── firebase.json            # Firebase Emulator 設定
├── firestore.rules          # 瀏覽器端預設禁止直接讀寫
├── .env.example             # 設定範本
└── spec.md                  # 完整功能規格
```

前端由 GitHub Actions 部署至 GitHub Pages；後端容器由 GitHub Actions 部署至 Google Cloud Run。Cloud Run 使用 Firebase Admin SDK 存取 Firestore，前端不得直接存取申請資料。CRM 正式環境以 Firebase Auth ID token 與 `admin` custom claim 驗證。

## 開發環境啟動

### 後端

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 前端

```powershell
cd frontend
npm run dev
```

## 核心規範

### API 設計
- Base path: `/api/v1`
- 統一錯誤格式: `{ "error": { "code": "ERROR_CODE", "message": "..." } }`
- 所有錯誤碼集中在 `app/core/error_codes.py`
- 路由檔案放 `app/api/v1/`，業務邏輯放 `app/services/`

### 資料與隱私（重要限制）
- **OpenAI API 核准前不得傳送真實申請者資料**，只可用合成資料
- 照片不可公開、不用於節目、不送入 AI
- 履歷解析需明確使用者同意

### 環境變數（`.env`）

```env
DATA_STORE_BACKEND=memory          # memory 或 firestore
OPENAI_API_KEY=sk-...             # OpenAI 金鑰
OPENAI_MODEL=gpt-4o-mini          # 預設模型
ADMIN_API_TOKEN=change-me-local-only # 僅供本機 CRM token 模式
ADMIN_AUTH_MODE=token              # 本機 token；正式環境 firebase
ADMIN_FIREBASE_CLAIM=admin
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ADMIN_AUTH_MODE=token
```

### 測試

```powershell
# 後端
cd backend
.\.venv\Scripts\python.exe -m pytest

# 前端
cd frontend
npm test
```

## 目前 API 端點

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/v1/health` | 健康檢查 |
| POST | `/api/v1/applications` | 提交申請 |
| GET | `/api/v1/admin/applications` | CRM 列表（本機 Bearer token；正式環境 Firebase ID token 且需 `admin` claim） |
| POST | `/api/v1/chat` | AI 心靈諮詢對話 |

## 待完成項目（見 todo.md）

詳見 `spec.md` 與 `todo.md` 了解完整功能需求。

正式管理員帳號使用 Firebase Authentication Email/Password。從 `backend/` 執行 `python -m app.scripts.set_admin_claim FIREBASE_AUTH_UID` 授予 CRM 權限。部署前需設定 GitHub Actions 所需的 GCP Workload Identity、Cloud Run、Pages 與 Firebase Web App 變數；細節見 `README.md`。
