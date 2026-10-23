# Flow 文件同步的生成時點與驗證邊界

建議把主要生成時點設在交付邊界：要求每個 commit 一致時，於「提交意圖確定、staged candidate 定稿」後生成；只要求 merge 候選一致且常有 WIP commit 時，於 PR ready-for-review 生成，後續候選變動須重新判定。最後由 required PR CI 驗證將要合併的版本。編輯前仍須讀相關 flow，暫時試驗與每次存檔不必重畫。

這個選擇把昂貴生成放在有明確版本的邊界，但 commit 本身不代表功能已定案或可發布。允許 WIP commit 的專案可把主要生成延到 ready-for-review，代價是提交歷史中會存在文件尚未同步的版本，且本地 gate 必須另訂政策。

目前套件提供 checker 與驗證 hook，尚未提供能從一般 `git commit` 自動喚起 AI 的 runner。最小採用方式是先讓既有 agent 的 commit preparation 執行同步；要涵蓋人工 shell commit，還需獨立的 runner 整合，不能用「hook 會擋」宣稱「hook 會生成」。

## 證據範圍與事實

研究日期為 2026-10-23。本文「事實」來自一手文件或指定本地檔案；「推論」是版本與成本分析；「建議」均未實作。網頁使用全域 Firecrawl 唯讀讀取，未執行外部程式或寫入 GitHub。

本地依據是研究時工作樹的 [SKILL.md][skill]、[enforcement contract][contract] 與 [pre-commit][hook]。本文核對這些檔案的明載行為與 hook 命令，沒有逐行審查或執行 Python checker，也沒有查核專案遠端 branch protection。

- 事實：hook 僅執行 `check --base HEAD --staged`，沒有模型呼叫、文件生成或 staging。contract 說明 `--staged` 讀 index；`snapshot` 更新工作樹，且拒絕 `snapshot --staged`。[本地 hook][hook]、[CLI 契約][cli]
- 事實：normalized AST 可忽略一般註解與格式；docstring、literal 內容及受支援 directives 仍可能改變語意 hash。file mode 對 bytes 敏感；語法差異會保守觸發 review，不等同必須改圖。[過濾契約][filter]
- 事實：review fingerprint 綁 exact base、相關 source、flow、mapping、policy 及依賴；review records 排除在自己的 fingerprint 之外。JSON record 是結構化聲明，沒有 reviewer 身分認證。[fingerprint 契約][fingerprints]、[review 契約][reviews]
- 事實：Git `pre-commit` 在建立 commit 前執行，可用非零退出碼中止，也可被 `--no-verify` 略過。`post-commit` 在 commit 後執行，不能改變該次 commit 結果。[Git hooks][git-hooks]
- 事實：Git index 是被選入下次提交的內容；`git add -p` 可只選部分 hunks。之後繼續改工作樹，不會自動更新 index。[Git add][git-add]

## 推論：四種觸發時點

生成是 agent 讀 source、判斷影響、修改必要文件及取得 review；驗證是 checker 判斷既有產物是否符合契約。兩者可以有不同觸發頻率，生成次數也不等於流程圖改寫次數。

| 時點 | 可用版本與優點 | 成本與失敗模式 | 評估 |
| --- | --- | --- | --- |
| 每次 edit／存檔 | 立即看到工作樹狀態 | 包含暫時試驗、半成品及語法錯誤；同一功能反覆閱讀與寫回 | 保留先讀與 dirty 標記，集中生成於下一個明確邊界 |
| 提交意圖確定、stage 定稿至 pre-commit | index 提供將要提交的候選；可讓 code/docs 同 commit | 部分 stage 會與工作樹不同；模型延遲、憑證或失敗會阻擋 commit | 推薦 agent prepare 時生成，hook 最後驗證 |
| post-commit | immutable commit 可識別，互動提交已結束 | 文件無法加入剛才的 commit；自動 amend 或補 commit 改變使用者預期，可能觸發遞迴 | 可排程或通知，較不適合作為保證同步的主要邊界 |
| PR CI，每 push／ready-for-review／merge 前 | 可集中執行，PR diff 可審查生成結果 | 每 push 生成昂貴；ready 之後仍會改；merge 後才補文件已錯過 gate | 每個候選驗證；生成可在 ready 或受影響新版本時排程 |

ready-for-review 適合代表作者要交付審查的意圖，仍不是最終版本。只跑一次 `ready_for_review` 會漏掉之後的 `synchronize`；反過來，每次 push 都呼叫 AI，會把尚未穩定的工作再次生成。

CI 的低成本檢查應先辨識候選是否已有可用同步證據，再決定是否需要生成。base 改變、rebase 或依賴/policy 改變都可能使證據 stale，即使 source 看起來相同，也不能只按 PR 編號跳過。

## 建議：以 index 為準的提交準備

agent 應先保留 pre-edit 讀取責任，再於使用者要求提交或 agent 準備授權 commit 時完成同步。若工作尚未進入提交或審查交付邊界，可保留 dirty 狀態，避免把每個中間 edit 轉成文件工作。

1. agent 固定 comparison base 與 intended index tree，讀取該候選的 source、flows、manifest 及 policy。工作樹只作其他未提交工作的提示，不能混入候選語意。
2. agent 對該候選計算影響，僅同步受影響文件；行為描述未變時保留圖，依契約取得 review 或更新必要 byte hashes。
3. agent 產出可檢視的 docs/evidence patch；只 stage 本次授權產物，保留原有部分 staging，不得暗中 `git add -A`。
4. checker 重新驗證實際 index；成功後才 commit。失敗時回到明確缺項修復；相同輸入重試應讀既有結果，避免重跑完整生成。

隔離目錄要呈現 index bytes；一般從 `HEAD` 建的 worktree 並不包含 staged candidate。Git 提供 `checkout-index --prefix` 匯出 index、`write-tree` 取得 index tree 身分，但前者需處理 sparse/skip-worktree，後者要求 fully merged index。[Git checkout-index][git-checkout]、[Git write-tree][git-tree] 這些只是 Git 原語，尚不是本套件的 snapshot runner。

部分 stage 尤其影響 manifest：現有 `snapshot` 讀工作樹，直接執行可能把未選入的試驗 code hash 寫進即將提交的 manifest。建議在隔離的 index snapshot 生成，回傳限定產物 patch；若原工作樹同一路徑已有其他修改，需保留並處理衝突，不能整檔覆蓋或把 code 一併 stage。[CLI 契約][cli]

生成期間使用者仍可能改 index。runner 應在套用結果與 commit 前重核 tree 身分，發現變動就令該次結果過期；timeout、離線、缺少模型憑證或必要 review 時回報未完成，不能落入成功路徑。

## 建議：最後驗證與 WIP 政策

若採「同 commit 同步」，推薦 agent prepare 生成、pre-commit 檢查 index、PR CI 檢查每個新候選。這保留早期錯誤回饋，也讓本地 hook 被略過時仍有遠端 gate；實際不可繞過程度由 required checks、protected reviews 及 bypass 設定決定。[Git hooks][git-hooks]、[protected branches][protection]

允許 WIP 的替代方案是「PR 交付前同步」：專案明確放寬 WIP commit 的本地同步要求，在 ready-for-review 生成，之後每次新候選驗證；stale 時須再次 prepare 或生成。這是政策選項，現有 strict hook 不會自行理解 WIP commit message，也不能把略過 hook 當作既有功能。

CI 必須明定比較的是 PR head、GitHub test merge 或 merge-group candidate，以及可信 base；不能對 checkout 後的候選直接 `--base HEAD` 自比。GitHub `pull_request` 預設使用 PR merge ref，`merge_group` 有獨立事件；使用 merge queue 的 required workflow 需涵蓋它。[GitHub events][events] 本地 `HEAD` 與 PR comparison base 不同時，exact-base evidence 不能直接搬用，需重建相應證據或另行設計、驗證可重用契約。

required gate 應驗證最後要審查與合併的版本；機器補出的 docs commit 也是新候選。對新 commit 的 checks 與 human review 仍須完成；可依專案需要啟用 dismiss stale approvals 或 most recent reviewable push approval。[protected branches][protection] 不應把 merge 後補文件設定成同步完成的判準。

## 推論與建議：真正全自動仍缺少的模組

要讓人工 `git commit` 自動生成，最小新增介面可採 provider-neutral runner callback contract，但契約本身不會啟動模型。先使用現有 agent workflow 可驗證內容同步流程；只有需要 shell commit 與無人值守 CI 都自行生成時，才值得補 runner 與 provider adapter。

| 缺少的責任 | 最小契約內容 | 未完成時的界線 |
| --- | --- | --- |
| 事件與政策 | commit preparation／ready 等事件、WIP 例外、允許寫入及 stage 的路徑 | 只能驗證或由 agent 執行，不能宣稱全面自動 |
| Snapshot 與隔離 | 固定 base/tree、完整必要 index inputs、輸出 patch、並行變動檢查 | 部分 stage 與工作樹可能混用 |
| AI runner | 非互動命令、provider adapter、憑證供給、timeout/cancel、失敗狀態與必要 reviewer | hook 只會執行已有命令，無內建 AI 生命週期 |
| 結果與重試 | 輸入 fingerprint、產物 diff、狀態、輸出 allowlist、重入鎖及有限重試 | commit retry 或自產 commit 可能重複生成與形成回圈 |
| 最後整合 | 明確 stage 授權、commit retry、CI 最終驗證及 protected review | 生成文件不等同已驗證或已合併 |

快取建議先以 exact base 加 index tree、runner/policy 版本識別請求，再以 feature fingerprint 重用未變內容。index tree 含生成文件與 evidence，不能把「輸入 tree 變了」一律當成全新生成；runner 須記錄輸入到輸出關係，限定自產路徑並重新驗證。review records 自身排除 fingerprint 的既有規則，不能推論任意 runtime evidence 或其他 outputs 都可排除。[fingerprint 契約][fingerprints]

生成 flow 本身會改變 review fingerprint，因此應先生成最終文件，再 review 與寫證據。若 review 要求改 flow，就重新取得受影響 review；base 或相關依賴更新也使快取失效。未量測模型耗時與 token，用 debounce 或快取能否省多少仍需實際工作負載驗證。

CI generation 另需最小權限與輸出回送策略。fork PR 通常沒有模型 secrets，且 `GITHUB_TOKEN` 為唯讀；不能為取得寫入能力而用 `pull_request_target` 執行不可信 PR code，官方明列 secrets、write privileges 與 cache poisoning 風險。[GitHub events][events] 可先回傳 patch artifact，由可信流程或作者納入 PR；若要 bot push，須另處理 fork、branch protection、後續 review 及重試。

截至研究日，官方文件說明 `GITHUB_TOKEN` 的 push 不會觸發新的 push workflow；PR `opened`、`synchronize`、`reopened` 則有 approval-required run 的例外。不能假設 bot 補 commit 後 CI 一定自動重跑，也不能把所有 token events 都描述為不觸發。[GitHub token][token] 改用 App token 仍需設計回圈、權限與 candidate validation，不會免除這些責任。

## 交付與驗證限制

本次交付僅為架構評估。已讀取引用的一手來源、檢查本地相對連結與報告的事實/推論/建議分界；沒有新增 hook、runner、CI workflow，沒有修改既有技能。agent commit preparation、任意人工 commit 啟動 AI、CI 生成的採用範圍仍待選定，本報告不構成實作授權。全自動 runner 的可用 provider、憑證、安全隔離及耗時沒有現成本地驗證，需在選定平台後另作整合驗收。

[skill]: ../../skills/flow-docs-sync/SKILL.md
[contract]: ../../skills/flow-docs-sync/references/enforcement-contract.md
[hook]: ../../skills/flow-docs-sync/assets/pre-commit
[cli]: ../../skills/flow-docs-sync/references/enforcement-contract.md#cli-and-staged-hook
[filter]: ../../skills/flow-docs-sync/references/enforcement-contract.md#change-filtering-and-review-cost
[fingerprints]: ../../skills/flow-docs-sync/references/enforcement-contract.md#ast-impact-and-fingerprints
[reviews]: ../../skills/flow-docs-sync/references/enforcement-contract.md#agent-review-records
[git-hooks]: https://git-scm.com/docs/githooks
[git-add]: https://git-scm.com/docs/git-add
[git-checkout]: https://git-scm.com/docs/git-checkout-index
[git-tree]: https://git-scm.com/docs/git-write-tree
[events]: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
[token]: https://docs.github.com/en/actions/concepts/security/github_token
[protection]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
