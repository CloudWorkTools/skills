# flow-docs-sync 採用方式與保證邊界

| 欄位 | 內容 |
| --- | --- |
| 狀態 | 兩個 agent 已收斂的建議方向，功能尚未實作 |
| 日期 | 2026-10-23 |
| 討論者 | 主 agent `/root`、獨立分析 agent `/root/issue3_direction_review` |
| 對象 | flow-docs-sync 維護者與後續實作者 |
| 範圍 | [Issue #3](https://github.com/CloudWorkTools/skills/issues/3) 的合理性、取捨與驗收條件 |
| 原始碼依據 | 本機 HEAD `9570aaa0337e504d03cb17b8d7c9219d0e49e3a7`，分析前工作目錄乾淨 |

## 決議

優先改善 bootstrap 與採用指南。`AGENTS.md` 作為同步規則的唯一真源，依實際工具保留必要的載入方式。下一次實作以文件修改為主，保持 manifest schema 與 checker/parser 行為不變。

Issue 的使用需求合理，但應區分載入方式不明確、採用指引不足，以及已明載的工具限制。現有技能沒有承諾單靠 checker 證明語意正確，也沒有承諾驗證 reviewer 身分。這些限制需要在完成報告中更容易辨認。

CI 範本列為獨立後續工作。Pre-edit hook 與 sequence parser 保留待評估，先定義狀態、映射與失效條件。本紀錄不代表已導入 UAV-Downloader、已設定遠端保護或已取得人類核准。

## 已核對的事實

以下為原始碼、測試或官方文件支持的觀察；後續章節則是實作建議。

| 觀察 | 證據 |
| --- | --- |
| 現有 bootstrap 已要求寫入 root `AGENTS.md`，其他入口只在適用時連結；缺少明確 import 與載入驗證方式。 | [SKILL.md](../../skills/flow-docs-sync/SKILL.md)，第 21 行 |
| `snapshot` 只更新已登記來源；正確基準下，語意變更仍須目前有效的 review。 | [flow_checker.py](../../skills/flow-docs-sync/scripts/flow_checker.py)，`run` 第 350-401 行 |
| review JSON 僅檢查欄位與 fingerprint 一致性，不能驗證作者是否冒充 reviewer。 | [enforcement-contract.md](../../skills/flow-docs-sync/references/enforcement-contract.md)，Agent review records；[reviewer-prompt.md](../../skills/flow-docs-sync/references/reviewer-prompt.md)，第 40 行 |
| Python 之外可選明確的 file mode；Tree-sitter 只為已實作 adapter 的語言提供符號粒度。 | [flow_parsers.py](../../skills/flow-docs-sync/scripts/flow_parsers.py)，`LANGUAGES`、`tree_sitter_hashes`；[語言支援契約](../../skills/flow-docs-sync/references/enforcement-contract.md#tested-language-adapters) |
| `depends_on` 為人工宣告；file mode 只擴大該檔已映射 features 的影響，不會補回跨檔遺漏的依賴。 | [flow_checker.py](../../skills/flow-docs-sync/scripts/flow_checker.py)，`closure`、`feature_content`、`fingerprints` |
| 圖表 parser 接受節點圖子集，映射要求每個節點都有來源；branch depth 使用強連通分量計算。 | [flow_checker.py](../../skills/flow-docs-sync/scripts/flow_checker.py)，`graph`、`load` |
| 現有文件已區分本機 hook、必要 CI 結果與遠端 merge 保護。 | [SKILL.md](../../skills/flow-docs-sync/SKILL.md)，第 67、75 行 |

2026-10-23 透過 Firecrawl 即時讀取的 [Claude Code 官方 memory 文件](https://code.claude.com/docs/en/memory#agents-md)支持 issue 的主要載入風險，但相容性條件更完整：

- 直接讀取 `AGENTS.md` 自 v2.1.277 起提供；v2.1.281 前的部分 session 仍有例外，例如 Bedrock 或停用 telemetry。
- 預設會檢查工作目錄及祖先的 `CLAUDE.md`、`.claude/CLAUDE.md`、`CLAUDE.local.md`。使用者的 `~/.claude/CLAUDE.md` 不算這個切換條件。
- `instructionFiles` 的 `claude-md-and-agents-md` 值可使兩者同時載入。該選項的設定檔來源為 user、`--settings` 或 managed settings，project/local settings 中的對應設定會被忽略。
- 直接載入 `AGENTS.md` 不觸發 `InstructionsLoaded`；從 `CLAUDE.md` import 則會。v2.1.280 前，直接載入的 `AGENTS.md` 不會列於 `/memory`、`/context`。

以上版本行為屬外部產品資訊。實作者應重查官方文件並驗證目標 session，不能只依版本號宣稱載入成功。

## 逐項處置

「本次」指下一次實作的建議範圍；「後續」不代表已提供能力或承諾交付日期。

| 建議 | 判定 | 處置與理由 |
| --- | --- | --- |
| 主建議：AGENTS.md 唯一入口 | 調整後採納 | 改為規則唯一真源。直接載入已驗證時不新建 `CLAUDE.md`；必要時保留 import 相容入口，避免舊版或既有指令檔遮蔽規則。 |
| 1. 先讀缺少硬性阻擋 | 問題成立，hook 待評估 | 本次標明規則、實際讀取順序與理解是不同證據。Hook 能降低正常工作流漏讀，但需處理 session/worktree、文件版本、scope 擴張、委派及 shell 等寫入途徑。不能宣稱觸發 hook 即證明理解。 |
| 2. 結構通過與語意正確 | 採納呈現改善 | 現有文件已明載限制。本次提供完成狀態範例，分列 structural check、agent semantic review、行為證據、必要 CI 與 merge 設定，不重寫 checker。 |
| 3. 多語言覆蓋 | 採納選擇指南 | Python 用內建 AST；JS/CJS 可明確選 `javascript`，Rust 可選現有 adapter；HTML、CSS、Dockerfile、YAML 等使用明確 file mode。本次不擴語言；缺少選配套件時，使用者須明確改選 file mode，不能自動降級。 |
| 4. 依賴人工宣告 | 採納盤點清單 | 本次檢查 routes、工廠與動態分派、前後端 API/schema、共享服務、設定、建置旗標及 codegen。漏跨檔依賴須補 `depends_on` 或擴 mappings/scope；自動盤點工具另行評估。 |
| 5. sequenceDiagram / subgraph | 採納替代方式，parser 待評估 | 補充圖可連回受控 flowchart，但不能宣稱已受 checker 驗證。直接支援 sequence 前須定義 message-to-source 映射、`alt`/`loop` 等分支及複雜度；不能僅多接受 header。25 節點是可調預設值。 |
| 6. 外部行為證據 | 採納輕量模板 | 本次用 Markdown 記錄 base/candidate、環境與遠端版本或觀測時間、操作、預期/實際、證據位置、未驗證項目。沿用現有 evidence 流程，不新增 manifest schema。 |
| 7. CI 範本 | 採納需求，獨立實作 | 先定義比較基準、PR head/merge candidate 與 evidence 的一致性，再提供範本及整合測試；保護規則仍需另行確認。 |
| 8. 既有文件分工 | 採納 | Adopt 列出既有規格、架構、流程與 contracts 的路徑及責任。原始碼核對實際行為，需求與契約定義預期行為；衝突須記錄處理，避免複製一套競爭的權威文件。 |
| 9. 分階段導入 | 採納 | 先選核心端到端 feature，連同共享依賴與行為輸入一起納入。明列未納入與未知範圍，只聲稱該 scope 的覆蓋；已納入範圍維持原有同步與 review 要求。 |

## Bootstrap 的具體方向

保留使用者既有內容與 local-only 檔案。同步規則維護於 root `AGENTS.md`，入口依下列情況處理：

| 情況 | 建議動作 | 驗收觀察 |
| --- | --- | --- |
| 沒有遮蔽檔案，目標 session 已驗證直接載入 | 不新建 `CLAUDE.md` | session 可見正確 `AGENTS.md` 規則 |
| root 已有 `CLAUDE.md` | 保留原文，缺少時加入真正的 `@AGENTS.md` import | 實際載入共享規則；普通文字連結不當成 import |
| 已有 `.claude/CLAUDE.md` | 依檔案位置使用 `@../AGENTS.md` | import 相對於指令檔位置解析 |
| 有 `CLAUDE.local.md` | 保留並提醒預設載入可能切換 | 確認 import 或有效的同時載入設定；不自動改全域設定 |
| 舊版、停用內建支援或直接載入無法確認 | 提供或使用必要的 import stub，回報未驗證部分 | 沒有實際 session 證據時，不宣稱載入通過 |
| 祖先、nested instruction 或其他 agent 工具 | 查核各自的發現與作用域 | 不盲目改祖先指令、不假設所有工具皆發現 root `AGENTS.md` |

## 討論取捨與成本

主 agent 提出以文件與採用體驗優先；獨立 agent 支持這個範圍，並要求保留相容入口、local 指令與跨檔依賴的邊界。兩者針對 CI 是否併入本次進行討論，決定分離處理。

直接提供 CI 範本的優點是降低導入成本，但目前 fingerprints 綁定精確 `base_oid`。本機 review 基準與 CI 基準不一致會使證據失效；在已提交候選上使用 `--base HEAD` 又會形成空比較。後續 CI 必須定義這個契約，涵蓋 target 更新、fork、首次導入與 workflow/checker 自我修改，並維持無 secrets、最低權限的執行方式。

完整禁止 `CLAUDE.md` 能減少入口種類，但會失去必要的相容載入。保留 import 的代價是仍須驗證實際 session；直接載入驗證失敗時，以可驗證的 import 方式回復共享規則。

立即增加 hook 或 sequence parser 可改善部分工作流，但會引入狀態失效與映射語意。這次先保留現有 checker 的可驗證界線，代價是先讀仍需執行軌跡佐證，sequence 補充圖仍需人工或專案工具驗證。

## 下一次實作的範圍與驗收

修改 [SKILL.md](../../skills/flow-docs-sync/SKILL.md) 的 bootstrap、Adopt 與完成狀態指引；修改 [enforcement-contract.md](../../skills/flow-docs-sync/references/enforcement-contract.md) 的採用指引，容納選擇表、依賴清單及 runtime evidence 模板。只有當摘要承諾變更時，才同步 [README.md](../../README.md) 與 [README.zh-TW.md](../../README.zh-TW.md)。

不修改 checker、parser、manifest schema、現有 hook 或 reviewer JSON 格式。純文件變更不新增逐字比對文件內容的測試。驗收條件如下：

1. Bootstrap 涵蓋上表情境，並將規則真源與載入入口分開說明。
2. 在隔離採用場景觀察必要文件先 read 再 edit；scope 擴張及委派後重新讀取。沒有執行軌跡則標示 read-order 未驗證，讀取聲明不能代替證據。
3. 完成報告逐項標明覆蓋範圍、結構檢查、agent review、行為證據、視覺檢查及 CI/merge 狀態；不得把單一 pass 擴大成整體保證。
4. 混合語言與分階段導入範例可供照做，包含核心流程的共享依賴；未知依賴不能藉由默默縮 scope 消失。
5. 主建議與九項不足都有處置與理由；尚未提供的 hook、CI、sequence parser 必須標明後續或待評估。
6. 現有流程測試持續通過，略過的選配測試明列。後續 CI 實作另加錯誤基準、基準更新、候選變更、fork、首次導入與政策變更案例。

## 驗證證據與限制

本次執行 `python3 -m unittest discover -s tests -p 'flow*_test.py'`，結果為 44 項中 31 項通過、13 項略過。其中 12 項因未安裝選配 Tree-sitter 套件，另 1 項因未設定 `FLOW_TEST_OLD_PYTHON`。未驗證多語言真實 grammar 路徑與跨 Python minor 版本可攜性，也未執行無關的 npm 安裝測試。

另外使用 [CheckerTests](../../tests/flow_checker_test.py) 的暫存 Git fixture 驗證基準選錯的結果：先建立 baseline，修改 `first` 並 snapshot，對原始基準檢查得到 `missing current review: one`。將未審查候選提交後，對自身 `HEAD` 檢查通過且 affected features 為空；改回原始基準則再次失敗。這說明 CI 不能直接照抄本機比較基準。

本機 codebase-memory 索引為 2026-09-18，相關檔案的 coverage freshness 均為 `not_tracked`；因此本分析直接讀取完整 checker/parser 與相關技能、測試原文，不以圖譜空結果推斷功能不存在。

未驗證 UAV-Downloader 的檔案數、實際依賴、Claude session 載入、read/edit 順序或遠端 branch protection。此紀錄不宣稱能強制理解文件、認證 reviewer 或偵測未登記的外部行為變更。
