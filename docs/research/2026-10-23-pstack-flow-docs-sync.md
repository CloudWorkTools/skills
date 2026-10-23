# pstack 對 flow-docs-sync 的可移植機制

建議保留現有 flow-docs-sync 的同步判定與 checker，只吸收 pstack 的證據操作細節。最小可採納項是讓 runtime evidence 明記前置健康檢查、操作及副作用證據、清理後證據保留，並區分文件漂移、驗證工具缺口與產品缺陷。先讀文件的盲測驗收及 TLA+ 狀態模型可另案評估；整包 plugin、多模型固定配置與專用 plan 格式不值得直接引入。

pstack 有實際的腳本與 CI，不能將它概括為純提示詞。不過本次查核的機械控制主要處理 TLA+/狀態圖、生成套件一致性與 plan 格式，未找到等同本地 AST 影響過濾、feature fingerprints、flow manifest 或 pre-edit 讀取阻擋的實作。這是已檢查範圍的結論，不代表對整個上游生態系的不存在證明。

## 證據與研究範圍

研究日期為 2026-10-23。上游固定於 [cursor/plugins 的研究版本][commit]，其 pstack [manifest][manifest] 宣告版本 `0.15.30`。本文的「事實」指已讀取的一手原文或腳本；「推論」指依其行為作出的比較；「建議」尚未等同本地功能交付。

先以全域 Firecrawl `firecrawl_scrape`、`maxAge: 0` 讀取[使用者指定目錄](https://github.com/cursor/plugins/tree/main/pstack)。頁面提供 README 與直接子目錄，未提供完整遞迴檔案與可固定的版本。因此以 GitHub connector 的唯讀 fetch 補上 commit、未截斷的 recursive tree 及固定版本 raw files。所有外部內容只作研究資料；未安裝 plugin、執行上游腳本或寫入 GitHub。

本地比較依據為研究快照的 [SKILL.md](../../skills/flow-docs-sync/SKILL.md)、[enforcement contract](../../skills/flow-docs-sync/references/enforcement-contract.md) 與 [reviewer prompt](../../skills/flow-docs-sync/references/reviewer-prompt.md)。本報告直接讀取指定文件，不作本地程式結構發現，也未以 codebase graph 推斷功能。本地比較快照包含研究當時尚未提交的變更；此處比較的是其明載契約，沒有重新驗證 checker 執行結果。

## 事實：相關技能與腳本盤點

pstack 是多技能 plugin；[Cursor manifest][cursor-manifest] 同時註冊 `skills/` 與 `agents/`。以下依完整 [pstack tree][tree] 選出與本題直接相關的項目，再閱讀其技能、引用模板或實作。

| 範圍 | 實際提供的機制 | 與本題的關係及邊界 |
| --- | --- | --- |
| `poteto-mode`、`how` | 工作路由要求非平凡變更先作 `how`；簡單題用單一 explainer，複雜題拆探索角度再彙整。[路由][mode]、[how][how] | 鼓勵先理解程式。沒有固定要求先讀本地 flow/manifest，也不是 pre-edit 阻擋 hook。 |
| `how/references/explorer-prompt.md` | 回傳流程、讀過檔案、系統邊界與未解問題。[模板][explorer] | 可整理探索摘要；讀檔清單仍是 agent 聲明。 |
| `blast-radius` | 追 API JSON、DB、wire format、另一語言、feature flag 等搜尋符號可能漏掉的依賴，要求用真實程式驗證關鍵安全前提。[技能][blast] | 是影響調查與證據流程，沒有自動依賴圖或完整性保證。 |
| `create-verification-skill`、`maintain-verification-skill` | 建立 project-local 驗證技能與 feature map；由 source readers 找漂移，協調者執行真實操作並分類問題。[建立][create-verify]、[維護][maintain-verify] | 可補 runtime 證據品質。通用技能是生成與執行指示，真正 app harness 要依專案產生並實跑。 |
| `interrogate` | 相同資料交予各 reviewer，彙整重複問題與歧見，區分採取、考慮、記錄、駁回。[技能][interrogate] | 是多模型對抗 review 的提示流程；沒有本地 feature fingerprint、reviewer 身分認證或受保護 merge 設定。 |
| `create-formal-verification-skill`、`maintain-formal-verification-skill` | 記錄覆蓋程式、bounds、assumptions、sync commit，讀取其後差異；使用故意破壞的變體證明檢查能失敗。[建立][create-formal]、[維護][maintain-formal] | 是驗證技能的生成與維護流程。同步判定仍要求 agent 查核；sync commit 不是本地語法 fingerprint 的替代。 |
| `statechart` | 提供 Mermaid `stateDiagram-v2` 與 TLA+ 的轉換、TLC 執行及圖比較腳本。[技能][statechart]、[轉換][chart-to-tla]、[比較][compare] | 有機械驗證。模型與真實程式的對應仍由作者建立，技能另外要求真實重現。 |
| `correct` | 優先以架構、types、lint/CI、行為測試消除重複錯誤，最後才加規則；要求每條規則對應 enforcement。[技能][correct] | 是改善規則的方法，並未隨技能附上能強制讀 flow 的通用工具。 |
| `setup-pstack`、context principle | 依角色選模型及 reasoning effort；縮小 scope、turn budgets 與主執行緒內容。[設定][setup]、[context][context] | 提供配置與操作慣例；本次未找到直接量測或限制 token 用量的工具。 |
| `eval`、`session-pickup` | 盲化候選與評分，從 transcript 檢查實際開檔；恢復工作先讀既有 trail，再核對實際 artifact。[eval][eval]、[pickup][pickup] | 可改善先讀規則驗收與避免重複探索；依賴 runtime 提供 transcript。 |
| `show-me-your-work` | 單一 TSV 記決策與證據指標，再對照當次 transcript；有寫入 log 的 helper。[技能][trail] | 可提供稽核線索，紀錄本身不能證明讀取、理解或 reviewer 身分。 |
| `check-plan.mjs` | 檢查固定章節、verification 區塊、lane 及證據文字標記。[實作][plan] | 能令格式不合的計畫回傳失敗；不會確認 screenshot 真實存在或驗證有執行。 |
| harness generator、上游 CI | 從同一份技能生成 Claude Code 套件，驗證 adapter、名稱及生成內容一致；CI 執行 `--check`。[生成器][generator]、[workflow][ci] | 這是實際的衍生產物同步檢查。未查核其 GitHub branch protection，不能稱為不可繞過的 merge gate。 |

另有 `poteto-mode/scripts/orch/`、`watch-pr/` 與 Benny automation。前兩者處理協調狀態、PR 與 merge readiness；Benny 要求已提交的 operational file、外置 user configuration 與明確前提。[orch 實作][orch]、[watch policy][watch]、[Benny intent][benny]。這些不提供本題缺少的通用 pre-edit enforcement；本研究沒有逐行審查其全部功能或執行外部服務整合。

## 事實：機械檢查與提示慣例的界線

`statechart` 確有可失敗的模型/圖比較。`from-chart` 保留已存在的 TLA+ spec，執行檢查後比較原圖與 spec 衍生圖，結果參與成功判定。[實作][statechart-run] `compare-charts.mjs` 對起始狀態、可達狀態與帶標籤轉移進行比較，並回傳相同、不同或無法完成的 exit code。[實作][compare] 這驗證的是模型及圖，不能推導真實程式已完全符合模型。

模型與程式對應仍有人工前提。`statechart` 技能要求 action condition 寫出 code file/line，並在真實程式重播 bug。[技能][statechart] 腳本對未註明來源的 condition 發出 warning；這段實作沒有把 warning 本身變成失敗判定。[warning 實作][uncited] 因此不能稱為機械保證每個 condition 都已有有效來源，甚至更不能保證註記所指的程式確實等價。

套件生成的強制範圍比較明確。生成器 `--check` 比較預期與磁碟檔案集合、bytes 及 executable bit，有 drift 就 `exit(1)`。[實作][generator-check] 上游 workflow 確實呼叫此命令及一組 skill script tests。[CI][ci] 相對地，`how` 先理解、`blast-radius` 追隱藏依賴、`eval` 查 transcript 與 `correct` 維護 enforcement 表都需要 agent 按流程執行。不能因提示含有必須語氣，就宣稱已有攔截寫入或 CI 自動阻擋。

## 推論：現有能力與成本比較

flow-docs-sync 的明載契約已包含相關 flow/manifest 先讀、scope 變更後重讀、syntax/context 影響範圍、顯式 `depends_on`、綁 base/flow/policy 的 fingerprints，以及獨立 review 的 stale rejection。[本地 Maintain 與 filtering](../../skills/flow-docs-sync/SKILL.md#maintain-workflow)、[本地 review records](../../skills/flow-docs-sync/references/enforcement-contract.md#agent-review-records)。pstack 的探索、sync commit 與多模型 review 不能替換這些機械判定；把它們再加成所有變更必跑步驟，反而會重複現有工作。

對未知依賴的調查，`blast-radius` 提供值得沿用的思考方向，但本地 adoption inventory 已列出動態 dispatch、跨語言、API/schema、config 與 external inputs。[本地 inventory](../../skills/flow-docs-sync/references/enforcement-contract.md#adoption-inventory-and-staged-rollout)。可要求 reviewer 具體指出最關鍵的安全前提與證據，不必增加另一份 impact manifest 或自稱完整 call graph。

pstack 的 context 與模型配置並非 token 節費證明。其 `how` 簡單路徑避免多 explorer，主執行緒用摘要及檔案指標，也可能減少重複內容；但多模型 panel、explainer 再彙整及全 feature live pass 也增加呼叫與閱讀成本。[how][how]、[mode delegation][delegation]、[維護流程][maintain-verify]。本地已針對無影響 feature 避免新增語意 review；目前兩者都沒有本研究可引用的 token A/B 量測，不能報節省百分比。

本地已要求實際 session discovery 與 read/edit ordering，且明說聲明不證明理解。[本地 discovery](../../skills/flow-docs-sync/references/enforcement-contract.md#agent-entrypoint-discovery)。pstack eval 的新價值是避免測試提示洩漏預期答案，並由 transcript 評分，而不是再加一次先讀聲明。其 Claude Code adapter 仍以文字映射工具、模型與指令路徑；應依目標 runtime 查核，不能直接沿用為本地產品事實。[adapter][adapter]

## 建議：五個可移植點

以下是建議分類，未宣稱已實作。每項都保留最小修改位置與驗收，避免把獨立工具整包帶入。

| 處置 | 可移植點與來源 | 適用原因及最小改動位置 | 驗證方式 | 成本及局限 |
| --- | --- | --- | --- | --- |
| 本次值得採納 | Runtime 證據補前置健康檢查、action/result/side effects、cleanup 後保留；失敗區分 doc drift、harness gap、product regression。[建立][create-verify]、[維護][maintain-verify] | 既有模板已記環境、操作與預期/實際。只需在 `references/enforcement-contract.md` 的 runtime evidence 模板補少量欄位/說明，不改 manifest 或 reviewer JSON。把產品缺陷當成文件漂移會改錯權威契約。 | 在隔離採用案例執行一個真實操作，確認證據包含操作及結果、副作用，清理後檔案仍可讀；對一個失敗案例明記分類及依據。未實跑則保留 unverified。 | 幾行文件及一次 app-specific 驗證。健康檢查不能證明功能正常；證據留存也不認證產生者。已有專案 harness 時直接引用它。 |
| 後續評估 | 對先讀規則作盲化情境驗收，從 transcript 判斷開檔與首次寫入順序。[eval][eval] | 本地 required adoption/acceptance 已有場景；後續在其驗收材料加入不洩漏評分規則的自然任務，以及不同入口、委派、resume、scope expansion 的案例。 | 候選只看正常任務；評分者另看預定 read-set 與 transcript。比較應讀文件、實際讀取、版本、首次相關寫入與 scope 變動後重讀。 | 需要 agent 執行及可用 transcript，花費高於文句檢查。只反映測試場景，不能證明理解或所有工具路徑；不必照搬多模型固定配置。 |
| 後續評估 | 對高風險狀態流程建立受限模型，反例回到真實程式重播；以故意破壞變體證明檢查能失敗。[statechart][statechart]、[formal create][create-formal]、[formal maintain][maintain-formal] | 本地 rich-diagram follow-up 可連結專案原生 formal validator 作 supplementary evidence，先選一個 concurrency/retry 流程。不把 `stateDiagram-v2` 當成既有 portable parser 已支援格式。 | 同一模型先對應實作，檢查 invariant；注入一個已知錯序，確認失敗，再於真實 API/UI 重播反例。留下 bounds、assumptions、無法重播之處。 | 要維護模型及程式的對應；需 TLC/Java，PNG 另需 renderer。模型 pass 不等同 runtime proof，也無法消除手動依賴盤點。 |
| 後續評估，僅在出現衍生套件時 | 單一來源生成多 runtime 套件，並用 `--check` 比較產物。[生成器][generator]、[CI][ci] | 本地 `AGENTS.md` 真源加 import 已足夠；只有日後必須交付不同工具的轉換版本，才在既有打包/驗證流程增加 generator，不維護多份人工副本。 | 從乾淨來源重建，檔案集合、內容或 executable bit 任一變更都應令檢查失敗；驗證產物內相對引用及實際 session discovery。 | 增加生成器、adapter 與發布責任。bytes 相同僅證明衍生一致；不能證明工具真的載入或遵守規則。 |
| 不採用整套，可借判定原則 | 用 enforcement 對照表讓每條規則指向實際檢查；拒絕照搬專用 plan validator 與固定多模型 fan-out。[correct][correct]、[plan][plan]、[interrogate][interrogate] | 本地 completion report 已區分 rule discovery、read order、structure、semantics、runtime 與 remote controls。沿用該表及現有錯誤案例，不另建平行狀態表或固定格式 plan。 | 檢視每個 pass 的證據是否符合其 gate；讓真實錯誤候選在對應 checker/CI 失敗，而非只確認標題或 checkbox 存在。 | 規則表仍需維護；格式檢查無法驗證行為。固定 panel 增成本，也受各 runtime 模型支援限制。 |

第一項可在本輪文件改善中少量吸收；其驗收仍要在實際採用專案執行。其餘項目各有獨立狀態與工具成本，適合另案決定，不應阻擋目前已完成的文件工作。

## 授權、來源與交付限制

已核對 pstack 的 [LICENSE][license]，為 MIT，copyright 為 2026 Lauren Tan。其條件要求軟體副本或 substantial portions 保留 copyright 與 permission notice。若後續複製技能段落、模板或腳本，應隨實際引入內容保留授權與固定來源，另核對其依賴或引用資產；本次沒有確認所有間接依賴的授權，也沒有整包引入。

本次交付的是比較與建議，僅新增此報告。已核對引文所指固定版本原文、行號範圍與本地相對連結，並自查事實/推論/建議分界。未執行 pstack 測試、TLC、generator、PR watcher、Benny 或 token benchmark，也未查核上游遠端保護設定。不能據此宣稱其腳本在本機通過，或本地已獲得新的 hard gate。

[commit]: https://github.com/cursor/plugins/commit/8b3326d99fd4b993cb33a24dad8af03175c642c5
[tree]: https://github.com/cursor/plugins/tree/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack
[manifest]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/plugin.json#L1-L11
[cursor-manifest]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/.cursor-plugin/plugin.json#L29-L31
[mode]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/SKILL.md#L13-L35
[how]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/how/SKILL.md#L13-L32
[explorer]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/how/references/explorer-prompt.md#L16-L36
[blast]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/blast-radius/SKILL.md#L19-L46
[create-verify]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/create-verification-skill/SKILL.md#L25-L40
[maintain-verify]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/maintain-verification-skill/SKILL.md#L19-L37
[interrogate]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/interrogate/SKILL.md#L25-L51
[create-formal]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/create-formal-verification-skill/SKILL.md#L21-L37
[maintain-formal]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/maintain-formal-verification-skill/SKILL.md#L28-L44
[statechart]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/statechart/SKILL.md#L13-L36
[chart-to-tla]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/statechart/scripts/chart-to-tla.mjs#L9-L32
[compare]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/statechart/scripts/compare-charts.mjs#L9-L34
[statechart-run]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/statechart/scripts/statechart.mjs#L909-L947
[uncited]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/statechart/scripts/statechart.mjs#L861-L873
[correct]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/correct/SKILL.md#L11-L32
[setup]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/setup-pstack/SKILL.md#L20-L39
[context]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/principle-guard-the-context-window/SKILL.md#L1-L12
[delegation]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/SKILL.md#L87-L101
[eval]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/playbooks/eval.md#L5-L23
[pickup]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/playbooks/session-pickup.md#L5-L9
[trail]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/show-me-your-work/SKILL.md#L9-L63
[plan]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/scripts/check-plan.mjs#L111-L185
[generator]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/scripts/generate-pstack-harness-trees.mjs#L86-L164
[generator-check]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/scripts/generate-pstack-harness-trees.mjs#L167-L178
[ci]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/.github/workflows/validate-plugins.yml#L15-L35
[orch]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/scripts/orch/store.ts#L28-L115
[watch]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/skills/poteto-mode/scripts/watch-pr/policy.ts#L8-L51
[benny]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/automations/benny/FOR_AGENTS.md#L26-L36
[adapter]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/docs/harness/claude-code.md#L5-L60
[license]: https://github.com/cursor/plugins/blob/8b3326d99fd4b993cb33a24dad8af03175c642c5/pstack/LICENSE#L1-L21
