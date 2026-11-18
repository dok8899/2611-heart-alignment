# 《心靈契合：30天，走向彼此》產品流程與資料關係

> 需求依據：`docs/prd.md` v1.16（2026-11-18）。本文件僅轉譯已確認 PRD；未定的營運、法務或技術細節列於第 4 節，不視為已核准承諾。

## 1. 訪客產品路徑與申請旅程（Flowchart）

本圖呈現免費前置體驗、付費體驗階梯、30 天四幕與首版各申請入口。三款封閉營可分開購買；第四幕是活動後自主相處，不是第四款營隊。年度會籍是可選延伸。

```mermaid
flowchart TD
    A[訪客進入雙語網站] --> B{選擇探索路徑}
    B -->|免費線上語音樹洞| C[查看每週免費入口與開放狀態]
    C --> C1{正式場次已開放？}
    C1 -->|是| C2[依核准報名流程參與]
    C1 -->|否或流程未定| C3[查看通知／意向入口；不虛構可用場次]
    B -->|城市樹洞夜| D[查看台北／新竹、約3.5小時與NT$8,800建議價]
    D --> D1{場次及申請方式已核准？}
    D1 -->|是| D2[依公布場次與核准方式提出申請]
    D1 -->|否| D3[查看開放狀態與待公告資訊]
    B -->|三款封閉營| E[比較封閉營與已公布月份／地區]
    E --> E1{選擇營隊}
    E1 -->|一：心靈樹洞 NT$88,000| F[封閉營一《心靈樹洞》；3天2夜]
    E1 -->|二：共好之間 NT$188,000| G[封閉營二《共好之間》；核心5日]
    E1 -->|三：風起之時 NT$238,000| H[封閉營三《風起之時》；核心5日]
    H --> H1{場次類型}
    H1 -->|一般場| H2[不拍攝]
    H1 -->|自願拍攝特別場| H3[閱讀獨立拍攝告知與授權；未核准前不開放]
    F --> J{選擇正式申請或意向登記}
    G --> J
    H2 --> J
    H3 --> J
    J -->|正式申請| K{申請入口來源}
    K -->|產品／月份詳情| L[沿用已選產品與月份]
    K -->|首頁| M[先選產品階段與月份]
    L --> N[單一快速申請入口]
    M --> N
    N --> O{填寫方式}
    O -->|AI助填| P[逐題整理稱呼／年齡、聯絡方式、參與期待]
    P --> P1[申請者確認／編輯欄位與短標籤；可刪除標籤]
    O -->|自行填寫| Q[逐欄輸入基本資料並可返回修改]
    P1 --> R[兩種模式共用確認步驟]
    Q --> R
    R --> S[選必填性別並上傳2至6張照片]
    S --> T{補充資料或履歷解析？}
    T -->|略過| W[選擇月份並確認聲明]
    T -->|手動補充| U[選填標籤；區塊底部自由文字亦選填]
    T -->|同意後履歷解析| V[OpenAI產生可編輯欄位草稿；申請者確認後帶入]
    U --> W
    V --> W
    W --> W1{所選月份收件狀態}
    W1 -->|可申請| X[確認成年單身聲明、安全公約、個資告知及錄音告知]
    W1 -->|額滿或截止且仍收件| X1[標示候補；主辦方人工挑選] --> X
    W1 -->|營運已關閉收件| W2[提示該月份不可送出；保留其他已填資料] --> W
    X --> Y[送出前LINE登入／註冊]
    Y --> Y1{登入與欄位驗證成功？}
    Y1 -->|否| Y2[指出錯誤並保留資料，可重試／返回]
    Y2 --> Y
    Y1 -->|是| Z[建立正式申請、月份關聯與同意紀錄]
    Z --> Z1{資料寫入成功？}
    Z1 -->|否| Z2[顯示送出失敗；保留表單供重試]
    Z2 --> Y
    Z1 -->|是| AA[畫面顯示已收到／候補並寄Email確認信]
    AA --> AB[CRM由授權營運人員檢視、更新狀態、記錄聯絡]
    AB --> AC[主辦方人工聯絡後續付款；網站不收款]
    J -->|低門檻意向| AD[填稱呼、年齡、性別、2至6張照片、聯絡及產品／月份]
    AD --> AE[完成成年單身聲明與必要告知後提交]
    AE --> AF[CRM收件；通知方式依核准規則]
    B -->|免費社群| AG[查看社群介紹與候補通知登記]
    AG --> AH[社群開放後依核准方式通知；未開放不顯示加入連結]
    B -->|節目海選| AI[獨立海選意向表單]
    AI --> AJ[CRM收件並由主辦方初審]
    AJ --> AK{初審通過？}
    AK -->|否| AL[依核准方式通知／結案]
    AK -->|是| AM[提供詳細資格與獨立自願授權流程]
    AM --> AN[海選意向不等於拍攝授權]
    B -->|年度會籍| AO[瀏覽樹洞 NT$138,000／契合 NT$248,000／真實契合黑卡 NT$520,000每年]
    AO --> AP[了解聯絡或申請方式；權益與資格待核定]
    subgraph STORY[30天節目敘事主線（不代表四項必購）]
        ACT1[第一幕「聽見」Day 1–3] --> ACT2[第二幕「看見」Day 4–10]
        ACT2 --> ACT3[第三幕「並肩」Day 11–17]
        ACT3 --> AQ[第四幕「選擇」Day 18–30；自主相處]
    end
    F -.產品對應.-> ACT1
    G -.產品對應.-> ACT2
    H -.產品對應.-> ACT3
    AQ --> AR[自主決定是否繼續；共識卡交付方式待核定]
    AR --> AS{是否自願了解年度會籍？}
    AS -->|是| AO
    AS -->|否| AT[體驗路徑結束；不承諾配對結果]
    F -.報名前明確同意錄音.-> AU[四幕錄音：僅供AI個人報告與品質檢視]
    G -.報名前明確同意錄音.-> AU
    H -.報名前明確同意錄音.-> AU
    AU --> AV[指定授權人員存取；不作節目素材]
    AV --> AW[自該場活動結束日起保存3年後刪除]
```

### 流程解讀

- 免費語音與城市樹洞夜是前置入口；封閉營一、二、三分別對應「聽見／看見／並肩」，可分開購買。四幕日程不是四個依序必購的產品。
- 第四幕「選擇」為 Day 18–30 活動後自主相處；年度會籍可選，不構成關係結果承諾。
- 首版正式申請只有一個快速申請入口，提供 AI 助填與自行填寫兩種模式。兩者共用性別、照片、月份及聲明確認。
- 申請者能複選月份；額滿或截止仍可提交候補，由主辦方人工挑選。營運關閉收件時不得提交該月申請。
- 活動錄音須在報名前明確同意，僅供 AI 個人報告及品質檢視，指定授權人員可存取，不作節目素材，活動結束日起保存三年。

## 2. 申請、AI／履歷、CRM 與活動錄音互動（Sequence Diagram）

本圖將首版網站互動和活動履約後的錄音處理分開呈現。活動語音轉錄服務商尚未選定，因此不假設由 OpenAI 處理錄音；OpenAI API 僅為申請 AI 助填與選用履歷解析的已選方向。

```mermaid
sequenceDiagram
    autonumber
    actor Visitor as 訪客／申請者
    participant Web as React網站
    participant API as Python服務
    participant OpenAI as OpenAI API（申請助填／履歷解析）
    participant LINE as LINE Login
    participant DB as SQLite資料庫
    participant Mail as Email服務（待定）
    actor Operator as 授權營運人員
    participant CRM as CRM後台
    participant Audit as 稽核紀錄
    participant EventTeam as 活動團隊
    participant Recorder as 錄音／轉錄服務（待選）
    participant ReportAI as 報告AI服務（待選）

    Visitor->>Web: 瀏覽免費語音、城市夜、封閉營與年度會籍
    Web-->>Visitor: 顯示產品路徑、價格提案、四幕對應與開放狀態
    Note over Web,Visitor: 免費語音／城市夜正式場次、會籍權益等未核定資訊需標示待公告
    alt 正式活動申請
        Visitor->>Web: 從詳情頁快速申請，或首頁選階段／月份
        Web-->>Visitor: 顯示AI助填／自行填寫選擇
        alt AI助填
            loop 三組逐題輸入
                Visitor->>Web: 輸入基本資料、聯絡方式或參與期待
                Web->>API: 傳送當次回答供欄位整理
                API->>OpenAI: 請求辨識欄位／產生期待短標籤
                OpenAI-->>API: 回傳欄位草稿或未辨識欄位
                API-->>Web: 回傳可編輯草稿
                Web-->>Visitor: 顯示草稿；可補填、編輯或刪除短標籤
            end
        else 自行填寫
            loop 一次一欄
                Web-->>Visitor: 顯示目前欄位與返回／繼續操作
                Visitor->>Web: 輸入欄位值
            end
        end
        Web-->>Visitor: 共用確認：性別、2至6張照片、選填補充資料
        opt 申請者選擇履歷解析並同意
            Visitor->>Web: 上傳履歷檔案
            Web->>API: 傳送檔案與解析同意
            API->>OpenAI: 請求擷取履歷欄位草稿
            OpenAI-->>API: 回傳欄位草稿或解析錯誤
            API-->>Web: 回傳可編輯結果／錯誤提示
            Web-->>Visitor: 申請者檢查並確認；可改手動或略過
        end
        Visitor->>Web: 選擇月份、勾必要聲明及錄音告知同意
        Web->>API: 查詢月份狀態
        API->>DB: 讀取月份、狀態及收件開關
        DB-->>API: 可申請／候補／收件關閉
        API-->>Web: 回傳可申請狀態；不揭露精確名額
        Web-->>Visitor: 確認月份與候補提示
        Visitor->>LINE: 送出前登入／註冊
        LINE-->>Web: 回傳登入識別或登入失敗
        alt 登入成功且欄位有效
            Visitor->>Web: 確認送出
            Web->>API: 提交申請、月份、確認欄位與同意紀錄
            API->>API: 驗證必填欄位、照片規格、聲明及月份收件狀態
            API->>DB: 寫入申請、照片參照、月份關聯與同意
            DB-->>API: 申請編號／寫入失敗
            alt 寫入成功
                API-->>Web: 回傳已收到／候補狀態
                Web-->>Visitor: 顯示成功結果；網站不收款
                API->>Mail: 寄送申請確認信
                Mail-->>Visitor: Email確認通知（寄送服務待選）
            else 寫入失敗
                API-->>Web: 回傳提交失敗
                Web-->>Visitor: 保留表單並提供重試
            end
        else 登入取消、驗證失敗或收件已關閉
            Web-->>Visitor: 說明原因並保留可修正欄位
        end
    else 低門檻意向登記
        Visitor->>Web: 填寫基本資料、性別、照片與產品／月份
        Web->>API: 提交意向資料及必要告知
        API->>DB: 建立獨立意向登記
        DB-->>API: 登記結果
        API-->>Web: 回傳送出狀態
        Note over Web,API: Email／電話規則與確認通知方式尚待定義
    else 社群候補或節目海選意向
        Visitor->>Web: 提交獨立通知／海選意向表單
        Web->>API: 提交表單與用途同意
        API->>DB: 建立對應類型的獨立紀錄
        DB-->>API: 登記結果
        API-->>Web: 回傳送出結果
        Note over Visitor,Web: 海選送出不等於拍攝授權；初審後才提供詳細資格
    end

    Operator->>CRM: 檢視申請／意向、更新狀態、記錄聯絡
    CRM->>API: 查詢或更新指定紀錄
    API->>DB: 讀取／寫入紀錄
    API->>Audit: 記錄檢視、修改、匯出、刪除事件
    Audit-->>API: 稽核事件已記錄
    API-->>CRM: 回傳紀錄與操作結果
    Note over Operator,CRM: 所有授權營運人員可查看全部CRM資料；不得稱為人員隔離
    Operator-->>Visitor: 人工聯絡；確認後另行通知付款安排

    opt 四幕活動之錄音與報告（活動服務流程；供應商待定）
        Visitor->>EventTeam: 報名前明確同意錄音
        EventTeam->>Recorder: 活動錄音／必要轉錄
        Note over EventTeam,Recorder: 用途限AI個人報告與品質檢視；不作節目素材
        Recorder-->>ReportAI: 傳送核准處理所需音訊／暫存逐字稿
        ReportAI-->>EventTeam: 產生個人報告草稿
        EventTeam->>EventTeam: 指定授權人員進行品質檢視
        EventTeam->>DB: 保存音檔及可識別報告的活動結束日／刪除日期
        Note over Recorder,DB: 服務商、逐字稿暫存及刪除、本人交付方式待核定；核定前不得傳送真實錄音
        EventTeam->>DB: 活動結束日起滿3年刪除音檔及可識別報告
    end
```

## 3. 核心資料實體與關係（ER Diagram）

ER 圖呈現 PRD 支持的主要資料。檔案實體以安全儲存參照而非直接把二進位內容放入 SQLite；實際儲存位置、備份及刪除策略待部署設計。欄位為流程推導模型，屬待實作驗證的資料設計假設。

```mermaid
erDiagram
    PRODUCT ||--o{ MONTHLY_SESSION : offers
    PRODUCT ||--o{ APPLICATION : receives
    MONTHLY_SESSION ||--o{ APPLICATION_MONTH : selected_for
    APPLICATION ||--|{ APPLICATION_MONTH : selects
    APPLICATION ||--|{ APPLICATION_PHOTO : includes
    APPLICATION ||--o| APPLICATION_PROFILE : optionally_has
    APPLICATION ||--o{ RESUME_FILE : may_attach
    APPLICATION ||--|{ CONSENT_RECORD : records
    APPLICATION ||--o{ CONTACT_LOG : has
    INTENT_REGISTRATION ||--o{ INTENT_MONTH : selects
    MONTHLY_SESSION ||--o{ INTENT_MONTH : interested_in
    INTENT_REGISTRATION ||--|{ INTENT_PHOTO : includes
    INTENT_REGISTRATION ||--o{ CONTACT_LOG : has
    COMMUNITY_NOTICE ||--o{ CONTACT_LOG : has
    CASTING_INTEREST ||--o{ CONTACT_LOG : has
    EVENT_SESSION ||--o{ EVENT_RECORDING : generates
    EVENT_SESSION ||--o{ EVENT_REPORT : produces
    EVENT_RECORDING ||--o{ EVENT_REPORT : source_for
    APPLICATION ||--o{ EVENT_RECORDING : participant_audio
    CONSENT_RECORD ||--o{ EVENT_RECORDING : authorizes
    CRM_OPERATOR ||--o{ CONTACT_LOG : writes
    CRM_OPERATOR ||--o{ AUDIT_EVENT : performs

    PRODUCT {
        string id PK
        string product_type
        string name_zh
        string name_en
        decimal suggested_price
        string price_unit
        string public_status
    }
    MONTHLY_SESSION {
        string id PK
        string product_id FK
        string month_key
        int capacity_internal
        string public_status
        bool intake_open
        string area_label
        datetime date_confirmed_at
    }
    APPLICATION {
        string id PK
        string product_id FK
        string line_subject_id
        string entry_mode
        string display_name
        string email
        string phone_optional
        int exact_age
        string gender
        bool adult_single_declaration
        string status
        datetime submitted_at
    }
    APPLICATION_MONTH {
        string id PK
        string application_id FK
        string session_id FK
        string status
        datetime selected_at
    }
    APPLICATION_PHOTO {
        string id PK
        string application_id FK
        string storage_key
        string mime_type
        int size_bytes
        int display_order
        datetime uploaded_at
        datetime event_ends_at
        datetime scheduled_deletion_at
    }
    APPLICATION_PROFILE {
        string application_id PK, FK
        string occupation_category
        string education_tags_json
        string education_free_text
        string values_tags_json
        string values_free_text
        string self_introduction
        string relationship_expectations
        datetime confirmed_at
    }
    RESUME_FILE {
        string id PK
        string application_id FK
        string storage_key
        string mime_type
        int size_bytes
        datetime uploaded_at
        string parse_status
        datetime event_ends_at
        datetime scheduled_deletion_at
    }
    CONSENT_RECORD {
        string id PK
        string application_id FK
        string consent_type
        string document_version
        bool accepted
        datetime accepted_at
    }
    INTENT_REGISTRATION {
        string id PK
        string display_name
        string email_optional
        string phone_optional
        int exact_age
        string gender
        bool adult_single_declaration
        string status
        datetime submitted_at
        datetime related_event_ends_at
        datetime scheduled_deletion_at
    }
    INTENT_MONTH {
        string id PK
        string intent_id FK
        string session_id FK
        datetime selected_at
    }
    INTENT_PHOTO {
        string id PK
        string intent_id FK
        string storage_key
        string mime_type
        int size_bytes
        int display_order
        datetime uploaded_at
        datetime related_event_ends_at
        datetime scheduled_deletion_at
    }
    COMMUNITY_NOTICE {
        string id PK
        string display_name
        string contact_value
        string status
        datetime submitted_at
        datetime related_event_ends_at
        datetime scheduled_deletion_at
    }
    CASTING_INTEREST {
        string id PK
        string display_name
        string contact_value
        string review_status
        datetime submitted_at
        datetime detail_shared_at
        datetime related_event_ends_at
        datetime scheduled_deletion_at
    }
    EVENT_SESSION {
        string id PK
        string product_id FK
        string month_key
        string act_name
        datetime starts_at
        datetime ends_at
        bool recording_consent_required
    }
    EVENT_RECORDING {
        string id PK
        string event_session_id FK
        string participant_application_id FK
        string storage_key
        string consent_record_id FK
        string permitted_purpose
        datetime captured_at
        datetime event_ends_at
        datetime scheduled_deletion_at
    }
    EVENT_REPORT {
        string id PK
        string event_session_id FK
        string recording_id FK
        string participant_application_id FK
        string storage_key
        string report_status
        datetime created_at
        datetime event_ends_at
        datetime scheduled_deletion_at
    }
    CONTACT_LOG {
        string id PK
        string application_id FK
        string intent_id FK
        string community_notice_id FK
        string casting_interest_id FK
        string operator_id FK
        string channel
        string note
        datetime contacted_at
    }
    CRM_OPERATOR {
        string id PK
        string email
        string status
        datetime created_at
    }
    AUDIT_EVENT {
        string id PK
        string operator_id FK
        string action
        string record_type
        string record_id
        datetime occurred_at
        string reason
    }
```

## 4. 未解需求、假設與資料邊界

### PRD 已確認並落入圖表

- PDF 新版產品路徑與價格建議：免費每週線上語音 → 城市樹洞夜 NT$8,800 → 三款封閉營 NT$88,000／188,000／238,000；年度會籍 NT$138,000／248,000／520,000 為可選延伸。價格與對外資訊仍待核准。
- 封閉營一《心靈樹洞》＝第一幕「聽見」Day 1–3；封閉營二《共好之間》＝第二幕「看見」Day 4–10；封閉營三《風起之時》＝第三幕「並肩」Day 11–17。第四幕「選擇」Day 18–30 為自主相處，沒有第四款封閉營。
- 正式申請與意向登記均需精確年齡、必選性別、2–6 張照片及成年單身聲明。照片 JPG／PNG／WebP，每張≤10MB；只供申請審閱，不公開、不供節目拍攝或 AI 使用。
- 正式申請使用 LINE 登入／註冊、Email 必填；電話選填。申請者可選 AI 助填或自行逐欄填寫；履歷解析為選用，解析欄位須由申請者確認。
- 月份可複選；額滿或截止仍收候補，由主辦方人工挑選；營運可關閉收件。CRM 提供收件檢視、狀態更新與聯絡紀錄；所有授權營運人員均可檢視全部 CRM 資料，存取、異動、匯出、刪除須稽核。
- 四幕活動錄音須報名前明確同意，僅供 AI 個人報告與品質檢視，指定授權人員存取，不作節目素材，自該場活動結束日起保存 3 年。
- AI 對話不保存逐字稿，正式送出後只保存申請者確認的欄位。AI 助填／履歷解析方向已選 OpenAI API；活動錄音／轉錄服務不等於 OpenAI API，仍未選定。

### 待確認事項與設計假設

1. 免費語音場次、平台、容量、報名欄位、錄音告知，以及城市樹洞夜的正式申請欄位與支付流程尚未定案；圖中只呈現依核准狀態顯示入口。
2. 免費社群候補通知方式、平台、管理者與安全規範待定；節目海選完整欄位、初審規則、授權期限與撤回方式待定。
3. 年度會籍三等級的權益、資格、公開申請／邀請方式及服務交付未定；產品節點不推定自動升級。
4. 封閉營價格、地點、日期、容量、費用包含項目、旅行社分軌契約及取消／退款條款未核准；付款仍由主辦方後續聯絡，網站不收款。
5. 第三階自願拍攝特別場的授權文件與拒絕／退出流程未核准；一般場不拍攝。錄音同意與節目肖像／聲音授權是不同用途、不同同意。
6. AI／履歷解析之 OpenAI 模型、端點、檔案處理方式、`store` 設定、留存、地區、跨境、DPA 及人工存取條件未定；核准前不得處理真實申請者資料。圖中 API 服務互動是目標流程，不代表整合已完成。
7. 錄音服務商、轉錄處理、逐字稿暫存／刪除、拒絕錄音者替代方案、報告內容與本人交付方式未定；核准前不得傳送真實錄音或宣稱報告交付已上線。
8. 所有個資、履歷、照片、活動錄音及可識別報告自相關活動結束日起保存 3 年。意向、社群通知、海選及取消／未成行資料沒有明確活動結束日，須定義對應事件後才能設刪除日期；圖中 `related_event_ends_at` 為待落地欄位。
9. ER 圖的表格／欄位與檔案儲存參照為依 PRD 推導的資料模型假設；需與部署、檔案儲存、交易紀錄及刪除／備份策略一起驗證。CRM 全員可讀不代表資料庫或服務商之間已實體隔離。
10. 前台公開狀態僅限「可申請／候補／截止」；不揭露精確名額。候補人工挑選，不進行自動排序或推薦。

## 5. HTML 檢視頁同步規則

`flow.html` 以此文件三個 Mermaid 程式區塊為唯一圖表來源，並提供瀏覽器分頁、原始碼檢視及 Mermaid 無法載入時的文字備援。兩份文件需一併更新版本標記與圖表內容。
