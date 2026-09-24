# CloudWorkTools Skills

[English](README.md) · 繁體中文

可重複使用的 agent 技能，涵蓋預覽、技術教學、專案文件與客戶報價。

| 技能 | 用途 |
| --- | --- |
| [pr-preview](skills/pr-preview/SKILL.md) | 透過專案正式建置路徑，建立或操作按需啟動的 PR／worktree 預覽。 |
| [teaching-with-diagrams](skills/teaching-with-diagrams/SKILL.md) | 以有根據的說明、練習與 Mermaid 圖解教授技術概念；整合三個上游技能，並追蹤其更新。 |
| [readme-value](skills/readme-value/SKILL.md) | 讓第一次來訪的人看懂專案用途、成果證據與下一步；價值尚未驗證時，提出具體的未來工作建議。 |
| [client-quotation](skills/client-quotation/SKILL.md) | 製作服務報價單與對應的白話功能規劃附件，附可編輯的空白 ODT 範本。 |

## 客戶報價

使用 `npx --yes skills@1.5.24 add CloudWorkTools/skills --skill client-quotation --agent codex --yes` 安裝。用 `$client-quotation` 製作共用編號的報價單與功能規劃附件，清楚列出付款階段，以及開發期間的 UI 示範、溝通與約定調整。附帶的 ODT 範本只有欄位提示，交付客戶前需填入已授權的專案資料。

## README 價值表達

在本機 checkout 執行 `npx --yes skills@1.5.24 add . --skill readme-value --agent codex --yes` 安裝，再提出要求：

> 用 $readme-value 改善這個 repo 的 README，讓第一次來、沒有專業背景的人看懂用途、目前成果與如何開始。把深入技術內容放到延伸文件；價值還未驗證的部分，提出具體且標示為建議的未來工作。

此技能採用 `crafting-effective-readmes` 的讀者判斷、`value-proposition` 的受益分析，以及 `documentation-writer` 的文件分工。它與教學技能可分別安裝，並附有自己的上游檢查器。詳見[來源、適配與維護](skills/readme-value/references/composition.md)。

在 repository 執行 `npm run skills:check-readme-updates`，或在安裝後執行 `node <skill-directory>/scripts/check-upstreams.mjs`。每週排程分別檢查兩個技能；README 技能使用獨立的 Draft PR 與 `.github/upstream-reviews/readme-value.md`。上游內容經審查採用後，才更新基準。

## 圖解式教學

將複合技能安裝到你的專案：

```bash
npx --yes skills@1.5.24 add CloudWorkTools/skills --skill teaching-with-diagrams --agent codex --yes
```

接著可以這樣要求 agent：

> 用 $teaching-with-diagrams，把這個模型的 README 整理成繁體中文初學者教材，加入 Mermaid 流程圖、數值例子與有解答的小練習，保留操作指南的入口。

此技能把 **teach**（學習目標與練習）、**documentation-writer**（Diátaxis 文件結構）和 **mermaid-diagrams**（視覺化說明）整合為可獨立使用的版本。它可處理一次性的 Markdown 文件；只有在明確要求時，才會建立持續性的課程。無須另外安裝三個原始技能。來源、維護決策與上游連結請看[組合說明](skills/teaching-with-diagrams/references/composition.md)。

### 追蹤上游更新

在本 repository 中執行：

```bash
npm run skills:check-updates
```

技能安裝後，也可以要求 agent 檢查上游更新，或執行：

```bash
node .agents/skills/teaching-with-diagrams/scripts/check-upstreams.mjs
```

需要 Node.js 22+ 與可連上 GitHub 的網路。檢查程式會比較每個完整技能目錄和根目錄授權檔與已審查基準的差異，輸出變更與比較連結，但不修改檔案。結束碼：`0` 表示沒有變更、`2` 表示有更新、`1` 表示檢查失敗。可選擇設定 `GH_TOKEN` 或 `GITHUB_TOKEN`，以取得較高的已驗證 API 額度。

[檢查技能上游更新](https://github.com/CloudWorkTools/skills/actions/workflows/skill-upstreams.yml) 每週一 UTC 03:17（台灣時間 11:17）執行，也可在 Actions 手動觸發。發現更新時，會建立或更新一個指派給 `jhihweijhan` 的 **Draft PR**，其中有報告、比較連結與審查清單。可在 [Pull requests](https://github.com/CloudWorkTools/skills/pulls) 或 [GitHub 通知](https://github.com/notifications)查看；email 是否寄送取決於你的 GitHub 通知設定。不需 AI 金鑰：工作流程使用 GitHub 內建的 `GITHUB_TOKEN`。

這個 PR 是通知，**不是已完成的適配**。請讓 agent 在該 PR 分支審查及適配上游改動、完成測試並更新已審查基準，之後才把它改成 Ready for review。自動化只會寫入 `.github/upstream-reviews/teaching-with-diagrams.md`，不會改動其他檔案或 PR 說明。相同批次不會建立新的報告 commit；已關閉的批次不會自動重開；不再是 Draft 的 PR 不會被自動修改。若想重新考慮已關閉的更新，請手動 reopen PR；若更新後來消失，請手動關閉過期 PR。檢查失敗會停止 PR 寫入，並在 Actions 中保留結果。

組織與 repository 設定必須允許 Actions 建立 PR。此工作流程只對通知工作授予 `contents: write` 與 `pull-requests: write`，只在預設分支執行，不會自動合併或推進 lock 基準。更新基準前請遵循[審查與採用程序](skills/teaching-with-diagrams/references/composition.md#review-and-adopt-an-update)。GitHub Actions 的排程可能延遲。

## 透過 npm 安裝

在要使用技能的專案中執行：

```bash
npm exec --yes --package=skills@1.5.24 -- skills add CloudWorkTools/skills --skill pr-preview --agent codex --yes
```

等效的 `npx` 指令：

```bash
npx --yes skills@1.5.24 add CloudWorkTools/skills --skill pr-preview --agent codex --yes
```

Claude Code 請將 `--agent codex` 換成 `--agent claude-code`。加入 `--global` 可安裝到使用者層級。這些選項使用標準的 [skills npm CLI](https://github.com/vercel-labs/skills)，會將技能與其參考資料複製到 agent 的技能目錄。

你也可以先從 GitHub 將此 repository 作為 npm 相依套件安裝，再註冊技能：

```bash
npm install --save-dev github:CloudWorkTools/skills
npm exec --yes --package=skills@1.5.24 -- skills add ./node_modules/@cloudworktools/skills --skill pr-preview --agent codex --yes
```

此套件透過 GitHub 發布，並未以 `@cloudworktools/skills` 名稱發佈到 npm registry。安裝只複製 agent 指引；不會啟動 container，也不會變更部署設定。

## 使用 pr-preview

可以這樣要求 agent：

> Use $pr-preview to preview PR #42 for manual review, using this project's production build path. Verify the source revision, login and assets, and give me the cleanup command.

或：

> 用 $pr-preview 預覽目前 worktree（含未 commit 修改），確認與生產建置路徑一致。檢視完後清理這一站，保留其他環境。

Agent 會檢查並重用目標專案已有的預覽腳本，或依附帶的實作契約建立／調整腳本。它涵蓋精確的 PR revision、不同的 worktree 身分、就緒失敗、私有狀態、離線日誌／清理，以及清理驗證。

執行預覽需要 Git、Docker Compose 與專用的預覽 host／daemon。僅使用受信任的程式碼與預覽用憑證／資料。與正式環境的一致性取決於專案實際的部署 overlay、資料與外部服務；container 名稱本身不是安全邊界。

## 內容與驗證

- [pr-preview 技能](skills/pr-preview/SKILL.md)
- [實作契約](skills/pr-preview/references/implementation.md)
- [圖解式教學技能](skills/teaching-with-diagrams/SKILL.md)
- [教學技能組合與上游追蹤](skills/teaching-with-diagrams/references/composition.md)

```bash
npm test
```

安裝測試需要 Node.js 22+ 與 npm。它們會打包 repository、安裝 tarball 到暫存專案，使用真實 npm CLI 安裝每個技能，並驗證每份資源都被完整複製且可被發現。上游檢查測試涵蓋參考資料的改動、檔案新增／刪除、授權變更、無關 commit 與 API 呼叫失敗。測試不會留下使用者層級技能或 Docker 工作負載。若尚未快取固定版本 CLI，則需要網路下載。

這份可攜式指引源自 [MUAMS PR #71](https://github.com/ROCMCSpace/MUAMS/pull/71) 的 PR 預覽工作；不包含 MUAMS 專屬的服務名稱、憑證與部署設定。
