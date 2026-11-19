# 心靈契合｜Monorepo

前端是 React/Vite 靜態網站，發布至 GitHub Pages；後端是 Python/FastAPI 容器，發布至 Google Cloud Run。瀏覽器只呼叫後端 API，不直接連 Firestore。Cloud Run 以 Firebase Admin SDK 存取 Firestore，並驗證 CRM 管理員的 Firebase Auth ID token。

## 專案結構

```text
.
├── .github/workflows/
│   ├── deploy-frontend.yml       # React build → GitHub Pages
│   └── deploy-backend.yml        # Docker/FastAPI → Cloud Run
├── backend/
│   ├── app/api/v1/               # FastAPI endpoints
│   ├── app/core/                 # 設定、錯誤、Firebase Admin
│   ├── app/db/                   # Firestore adapter / local stub
│   ├── app/services/             # 業務邏輯
│   ├── app/scripts/              # 維運腳本
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                     # React + TypeScript + Vite
├── examples/minimal-members-api/ # 舊單檔 demo，與主服務分開
├── firebase.json                # Auth／Firestore Emulator 設定
├── firestore.rules              # 前端直接讀寫預設拒絕
├── spec.md
└── todo.md
```

## 本機開發

先在專案根目錄建立 `.env`：

```powershell
Copy-Item .env.example .env
```

### 啟動 API

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

預設 `DATA_STORE_BACKEND=memory`，資料是合成測試用且重啟會清空。健康檢查：`http://127.0.0.1:8000/api/v1/health`。

### 啟動 React

```powershell
cd frontend
npm ci
npm run dev
```

Vite 使用 HashRouter，開發網址為 `http://127.0.0.1:5173/`。本機 CRM 預設用 `.env` 的 `ADMIN_API_TOKEN`；正式 Pages build 使用 Firebase Auth Email/Password 登入。

### Firebase Emulator

安裝 Firebase CLI 後在根目錄執行：

```powershell
firebase emulators:start --only auth,firestore
```

在 `.env` 將 `DATA_STORE_BACKEND=firestore`、`FIRESTORE_EMULATOR_HOST=127.0.0.1:8080`、`FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099`，並設 `ADMIN_AUTH_MODE=firebase`。Admin SDK 會使用同一 Firebase project ID。Firestore rules 預設 deny all；後端 Admin SDK 使用服務身分，不會由瀏覽器直接存取資料庫。

## GitHub Pages 與 Cloud Run 部署

部署工作流程觸發分支為 `master`。前端 workflow 將 `frontend/dist` 發布到 GitHub Pages；Vite 的 production base path 為 `/2611-heart-alignment/`，路由使用 HashRouter，支援 Pages 靜態託管。後端 workflow 使用 `backend/Dockerfile` 建置容器並部署至 Cloud Run。

### GitHub 設定

建立以下 repository secrets：

- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_DEPLOY_SERVICE_ACCOUNT`
- `CLOUD_RUN_RUNTIME_SERVICE_ACCOUNT`

建立以下 repository variables：

- `GCP_REGION`，例如 `asia-east1`
- `CLOUD_RUN_SERVICE`，例如 `heart-alignment-api`
- `PAGES_ORIGIN`，例如 `https://dok8899.github.io`
- `VITE_API_BASE_URL`，Cloud Run URL 加 `/api/v1`
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_APP_ID`

`VITE_FIREBASE_*` 是 Firebase Web App 公開設定，不可放服務帳戶金鑰。請在 Google Cloud 啟用 Cloud Run、Cloud Build、Artifact Registry、Firestore、Firebase Authentication 與 Secret Manager；部署身分使用 Workload Identity Federation，Cloud Run runtime service account 至少具備 Firestore 存取權。後端 workflow 預設不注入 OpenAI 機密；如要啟用聊天 API，需先在 Secret Manager 建立 `OPENAI_API_KEY` secret version，並為 runtime service account 授予該 secret 的 Secret Accessor 權限，再於 workflow 加入 secret mapping。

Firebase Console 需啟用 Email/Password provider、建立營運帳號。先取得該使用者 UID，再以具備 Firebase Auth 管理權的可信任環境執行：

```powershell
cd backend
python -m app.scripts.set_admin_claim FIREBASE_AUTH_UID
```

後端只接受帶有 `admin: true` custom claim 的 Firebase ID token 存取 CRM。管理員需重新登入或刷新 token 才會取得新 claim。應用申請 API 仍公開接受表單；CRM 由後端驗證身分與權限。申請者原規劃的 LINE Login 與營運人員 Firebase Auth 是兩種不同身分流程。

Cloud Run 部署完成後，將服務 URL 加上 `/api/v1` 設成 `VITE_API_BASE_URL` repository variable，再執行前端 workflow。Cloud Run `CORS_ORIGINS` 由 `PAGES_ORIGIN` 設定。GitHub Actions 僅在相應目錄或 workflow 改動時部署。

Firebase Admin SDK 是具備管理權限的 server SDK；Firestore Security Rules 不會限制 Admin SDK 請求，因此 Cloud Run runtime service account 的 IAM 權限必須嚴格控管。詳見 [Firebase server client libraries 安全說明](https://firebase.google.com/docs/firestore/client/libraries) 與 [Firebase Admin SDK 設定](https://firebase.google.com/docs/admin/setup)。

## API

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/v1/health` | API／Firestore 健康檢查 |
| POST | `/api/v1/applications` | 提交申請並寫入 Firestore adapter |
| GET | `/api/v1/admin/applications` | CRM 列表；正式部署需 Firebase ID token 與 `admin` claim |
| POST | `/api/v1/chat` | AI 對話；OpenAI secret 未設定時不可用 |

## 檢查

```powershell
# backend
cd backend
.\.venv\Scripts\python.exe -m pytest

# frontend
cd frontend
npm test
npm run build
```
