# Flow 同步決策的 Token 實測與工作環境回顧

這批 12 次決策測試沒有顯示新版較省 Token。全部模型的輸入加輸出由 103,247 增至 108,884，增加 5.46%。兩版對 Draft、未變更輸入都沒有要求同步或重審；新版把材料補救的剩餘額度明定為一次，但增加了指令讀取成本。

這是決策測試，不是完整流程圖同步的成本測試。沒有執行流程生成、checker、語意 reviewer、部署或真實截斷恢復，因此不能據此宣稱整個工作流程節省或增加相同比例的 Token。

## 測量方法

- 舊版：`b17df8308b674704f9c0aab13cd4db434609e2c4`；新版：`d1cfa7cec2af1799455887cd30c0be1052ad4323`。
- Claude Code `2.1.312`，指定 `claude-opus-5-5`、`low` effort。每個案例各跑兩組配對，順序為舊新版、再新舊版。
- 使用獨立暫存目錄、safe mode、空工具集合、空 MCP 配置及固定 system prompt。關閉 session persistence；不讀取工作區的動態上下文。
- Draft、未變更案例只提供 `SKILL.md`；材料補救再提供 `references/reviewer-prompt.md`。兩版使用同一案例文字、檔案選擇和輸出格式。
- 用 CLI 的 `modelUsage` 計數，包含回報的 Opus 與 Haiku 用量。Haiku 的用途未由此測試確認，不能把它的用量漏算。
- 輸入等於 uncached input、cache creation 和 cache read 的總和。輸出使用回報的 `outputTokens`，不再加上 thinking 或 cache TTL 的子計數。

來源是[逐次實測資料](data/2026-10-29-flow-token-measurement.json)及[測量程式](../../scripts/measure-flow-tokens.py)。以下數字均由該資料計算；不是依字數估算。

## 結果

下表為每次 CLI 呼叫的平均 Token，包含回報的所有模型。`review_dispatches` 是模型提出的決策，不是實際執行的 reviewer 呼叫。

| 案例 | 舊版輸入 | 新版輸入 | 舊版輸出 | 新版輸出 | 決策差異 |
| --- | ---: | ---: | ---: | ---: | --- |
| Draft/WIP | 16,269 | 16,551 | 60 | 61 | 兩版都不重寫 flow、不派 reviewer、不宣稱交付完成。 |
| 證據與輸入未變 | 16,313 | 16,595 | 61.5 | 60 | 兩版都沿用有效證據，不重寫或重審。案例已提供通過的候選檢查。 |
| 截斷後補件 | 18,287 | 20,665 | 633 | 510 | 兩版都提出一次審查；舊版未定義剩餘補件額度，新版回報剩一次。 |

| 12 次呼叫的彙總項目 | 舊版六次 | 新版六次 |
| --- | ---: | ---: |
| Uncached input | 52,312 | 55,254 |
| Cache creation | 24,713 | 26,184 |
| Cache read | 24,713 | 26,184 |
| 輸入總和 | 101,738 | 107,622 |
| 輸出 | 1,509 | 1,262 |
| 輸入加輸出 | 103,247 | 108,884 |

Opus 本身的輸入總和為舊版 49,438、新版 52,380；其餘輸入來自 CLI 回報的輔助模型。不能只讀頂層 `usage` 而把輔助模型排除。快取類別不同，不能把這些 Token 直接換算成帳單金額。

## 本輪工作環境的改善候選

按可觀察的影響排序，以下是改善候選，尚未修改全域設定。

1. **審查上下文過大。** [六份 worker 主對話的用量摘錄](data/2026-10-29-flow-session-usage.json)共有 62 個不重複 assistant message ID。首次可見 assistant 請求已包含 56,020-57,039 個輸入 Token。應先測試精簡的唯讀 reviewer profile，只提供必要工具、指令和檔案；尚未分解這些 Token 分別來自哪些系統指令、skills 或 MCP 描述。
2. **整份審查重複啟動。** 本輪先做完整九情境 review，修改後又做完整九情境 review，最後才縮成四項邊界複核。第一次完整檢查有必要；後續應綁定修改身分，只重驗受修正影響的情境與跨檔一致性。保留要求真正獨立 reviewer 的關卡，不能以作者自審取代。
3. **Orca 的 structured worker 重用介面與實際行為不一致。** 本輪用已結案的 `structworker_*` handle 呼叫 `worker-start --terminal`，收到 `terminal_unsupported_for_agent_session`，因此最後啟動新的窄範圍 reviewer。應在 Orca 層加入 structured/terminal 兩種 surface 的相容性測試，並回傳可直接使用的後續動作。這不是本 repository 的程式修正。
4. **工具輸出過量。** 本輪數次一次讀取多份完整 skill 或 CLI help，回傳截斷後再補讀。專案 [AGENTS.md](../../AGENTS.md)已要求先找路徑與標題、按需讀取。應改善 skill/tool loader 的分段與輸出預算；不需要再新增同義的全域禁止條文。
5. **用量觀測不足。** 審查結果原先只有完成狀態，必須另外讀取本機 transcript 才能取得用量。建議協調工具的 completion receipt 提供分模型的 uncached/cache/output 計數，讓昂貴的角色和重派容易被辨認；本輪的測量程式先覆蓋 headless CLI 的計數。

六份主對話的可見計數為 uncached input 124、cache creation 501,671、cache read 4,476,855、output 98,012。原始 log 保留於本機，公開摘錄只含角色、來源雜湊與用量。這些數字不包含主 Codex、未記錄的輔助呼叫、巢狀 transcript 或新的 A/B 實測，不能當作整個 session 的完整帳單。

既有 `npm test`、安裝包連結檢查及 GitHub required CI 已在運作。[貢獻指南](../contributing.md)也已規定獨立情境評估，不需要再加一份重複的 hook 或 coding standard。專案與全域 AGENTS.md 都很短，沒有證據支持繼續擴充它們。

## 重跑與限制

重跑會實際呼叫模型，需要既有 Claude Code 認證；每次 CLI 呼叫設有一美元預算上限。選擇尚不存在的輸出檔，避免覆寫原始結果：

```bash
python3 -B scripts/measure-flow-tokens.py --output /tmp/flow-token-rerun.json
```

一般 `npm test` 只跑離線的計數與輸出驗證測試，不會呼叫模型。Cache 子計數與 helper 用量分開測試，避免重複計算或默默把缺失欄位當成零。

每個版本每案例只有兩次樣本，輸出推理量會波動。測試未重現舊版提早停止，也未實跑大檔案恢復，所以沒有證據量化「避免失敗重派」的節省。新版的可靠性條款與後續環境精簡應分開評估，不能把本輪量測描述成已證實的節費成果。
