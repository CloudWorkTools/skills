# Docs sync 實際執行與 Token 用量

受控的兩功能同步流程已執行通過：程式從回傳 1 改成 3，模型更新了 flow，獨立模型審查通過，現有 checker 驗證候選內容。Draft、重複交付及 AST 不變的註解修改，都沒有新增生成或語意審查呼叫。這項證據與先前的[決策測試](2026-10-29-flow-token-measurement.md)分開。

**Docs sync token usage：已記錄模型小計 24,707 Token；整項開發任務總量未知。** 小計包含這次三個試跑的全部五次模型呼叫及回報的輔助模型，包括前兩個未完成試跑。主 Codex 的共用開發上下文無法可靠歸屬，沒有列入小計，也沒有當成零。

## 實際執行結果

測試在暫存 Git repo 建立 `first()` 和 `second()` 兩個 feature，使用原有 Python AST checker。只有 `first()` 從 1 改為 3；`second()` 保持 2。測試輸出、設定原文、base/candidate manifest、原始 diff 及候選 tree 身分都提供給 reviewer。

| 事件 | 新增模型呼叫 | 實際結果 |
| --- | ---: | --- |
| Draft | 0 | 保留 pending，不生成或審查。 |
| Ready 恢復 | 1 | 比對程式、測試設定與 mapping 後沿用前次生成的 flow；重新取得獨立審查，checker 通過。 |
| 相同內容再次交付 | 0 | 指紋與有效證據相符，checker 通過。 |
| 一般註解修改 | 0 | 刷新 byte fingerprint，AST 與語意證據不變，checker 通過。 |

這裡的零指額外生成／reviewer 呼叫，不代表本地 checker 或主 agent 沒有執行。實際檢查比較的 Git base 仍顯示 feature one 有變更；已通過的 matching fingerprint 避免它再次觸發模型。

最終證據是[執行結果](data/2026-10-29-flow-sync-execution-recovered.json)與[呼叫用量 ledger](data/2026-10-29-flow-sync-execution-recovered.usage.jsonl)。生成結果的重用有來源檔雜湊，並核對程式、測試設定與 feature mappings；沒有重用未通過的審查。用量摘要由 ledger 重新計算，沒有重跑或改寫模型回覆。

## 包含未完成試跑的用量

| 階段 | 模型呼叫 | Input，含 cache | Output | 合計 |
| --- | ---: | ---: | ---: | ---: |
| 同步生成 | 2 | 4,644 | 261 | 4,905 |
| 獨立語意審查 | 3 | 15,915 | 3,887 | 19,802 |
| 全部已記錄呼叫 | 5 | 20,559 | 4,148 | 24,707 |

輸入包含 uncached 10,931、cache creation 9,628、cache read 0。Thinking 與 cache TTL 子計數沒有再加一次。所有數字來自[request 用量摘要](data/2026-10-29-flow-sync-request-usage.json)及其列出的三份 ledger，不是用字數估算。

- 第一試跑 6,820 Token：模型雖回 `pass`，卻在 `findings` 填入正向觀察，正式驗收拒收，沒有偽造 passing record。
- 第二試跑 8,086 Token：完整 reviewer 模板辨認出缺少候選快照、原始 diff、base manifest 與設定原文，回 `incomplete`。這些缺口被補齊；資料與用量均保留。
- 恢復試跑 9,801 Token：沿用輸入相符的生成結果，只派一次新 reviewer。完整 pass 及最終 checker 結果都已保存。

前兩份 ledger 的 CLI 呼叫及 JSON 解碼成功，因此其 call status 是 `success`；這不代表同步或語意審查通過。每份 execution report 的 `complete` 和原始 reviewer 回覆另行記錄流程結果。

沒有從這三次試跑推算一般專案的節省比例。額外 Token 也暴露出準備材料與 schema 不完整的成本；不能只報最後恢復的 9,801 而省略先前耗用。

實作的獨立程式審查另以 `implementation_validation` 記錄，見 request 摘要的 `supporting_work`。它屬於本輪開發驗證，不計入這個 fixture 的同步用量。`known_task_subtotal_tokens` 另外合計已記錄的 fixture 與支援工作；`whole_task_total_tokens` 仍為未知，避免漏算主 Codex 的共用上下文。

## 已落實的環境改善

- 用真實檔案、Git 差異、模型 flow 與 checker 驗證流程事件；離線測試另驗證無效 flow 不會進入模型 review。
- 每次 CLI 嘗試先寫入 append-only 用量 ledger，再回傳或拋錯。非零退出、格式錯誤、timeout 與未知用量均有離線案例；相同 attempt 去重，衝突身分報錯。
- `review_context()` 自動帶入設定的測試命令、設定原文、GitHub workflow 及實際執行紀錄，reviewer 不必猜 unittest 的預設 pattern。
- 用 `phase` 分開同步、review、材料補件、驗證或實驗；摘要區分已知小計與未知總量。沒有用量時仍可完成同步，不能把未知寫成零。
- Skill 的交付報告必須包含「Docs sync token usage」，並聲明來源、模型、cache 分類、失敗／重試、觀測範圍及未知部分。用量證據留在既有 task evidence，排除於 flow fingerprints。

## 重跑

這個命令會實際呼叫模型，產生新的 fixture 執行結果與相鄰 `.usage.jsonl`；使用尚不存在的輸出檔：

```bash
python3 -B scripts/exercise-flow-sync.py --output /tmp/flow-sync-run.json
```

如果一次未完成的執行已保存 `failure_artifacts`，可使用 `--reuse-generated-from <report.json>`。輸入不符就拒絕重用，不會把舊的 approval 換成新 fingerprint。

一般 `npm test` 僅執行假模型與真 checker 的離線案例，不產生付費模型呼叫。這不是在各專案安裝的無人值守 runner，也未驗證 GitHub 自動生成、渲染、部署或真實大型程式的依賴完整性。

生成資料的重用僅用於這個固定 fixture。程式未把 base 身分、原 flow 或需求文字當成通用 cache key，不能外推成任意專案的生成快取；新候選的獨立審查與 checker 仍必須通過。
