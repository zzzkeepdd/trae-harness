# 完整宪法

> 复盘时参考，平时按需加载拆分版

## 元规则

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| M01 | 任何流程指令，凡不附带不可绕过之产出物及验证机制者，视为软建议，不视为规则。所有流程规则必须明确其必须产出的交付物和验证方式。无法被验证是否执行的规则，在设计和复盘时视为软建议，不具备强制力。 | 全体 | immutable |

## 基础规则

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| C01 | 用户可见产品=是 → 至少L2。任何网页/App/GUI都不可走L1。 | Trae统筹 | - |
| C02 | L1判据必须全部满足：≤3文件、单一技术栈、无用户可见产品、无外部依赖。 | Trae统筹 | - |
| C03 | L3判据任一满足即L3：文件数>15、外部API≥3个、复杂并发/多角色权限、3种+技术栈。 | Trae统筹 | - |
| C04 | 其他情况=L2。 | Trae统筹 | - |
| C05 | 调研员只读不写，严禁修改任何文件。 | 调研员 | - |
| C06 | 调研输出≤200词，聚焦关键信息，禁止冗长。 | 调研员 | - |
| C07 | 三个调研员并行工作，互不共享上下文，各自独立产出。 | 调研员 | - |
| C08 | 同时只讨论一个维度，当前维度完成后再进入下一个。 | 辩论Agent | debate-integrity |
| C09 | 红队至少攻击3个边界条件，蓝队必须逐条回应。 | 辩论Agent | debate-integrity |
| C10 | 裁判评分1-5分。分级门槛：L1≥1个攻击点≥3分且总数≥3；L2≥2个攻击点≥3分且总数≥4；L3≥3个攻击点≥3分且总数≥5。不满足则打回重辩。 | 裁判Agent | debate-integrity |
| C11 | 轮次控制：L1/L2=1轮（收敛边界），L3=2轮（先发散功能后收敛边界）。 | 辩论Agent | debate-philosophy |
| C12 | 审核员必须检查维度覆盖完整性，标记遗漏风险。 | 审核员 | module-one-integrity |
| C13 | 审核员必须给出代码可行性建议，为模块二提效。 | 审核员 | module-one-integrity |
| C14 | 交叉验证维度间冲突，统一评分标准。 | 审核员 | module-one-integrity |
| C15 | 产出debate-output.json必须符合schema，通过节点门1验证。 | 审核员 | module-one-integrity |
| C16 | 规范生成只基于debate-output.json，禁止引入新需求。 | 规范生成Agent | - |
| C17 | 信息瓶颈：执行清单≤200 token，下游提示词≤150词。 | 规范生成Agent | - |
| C18 | 每个需求必须有可测验收标准，禁止模糊词。 | 规范生成Agent | - |
| C19 | 用户确认门不可跳过，用户说"go"才进入模块二。 | Trae统筹 | - |
| C20 | 上下文清理时机：用户确认需求规格后、模块二确认无歧义后才清除。 | Trae统筹 | context-management |
| C21 | 清理后保留：debate-output.json、需求规格说明书、执行清单JSON、复杂度分级。 | Trae统筹 | context-management |
| C22 | 步骤隔离：每个子Agent只做当前步骤，不知道下一步。整改后的任务作为新任务派发。 | Trae统筹, 全体子Agent | step-isolation |
| C23 | 开发Agent只知本任务，不知道code-qa和func-qa存在。 | 开发Agent | step-isolation |
| C24 | code-qa Agent只知验收当前代码，不知道func-qa存在。 | code-qa | step-isolation |
| C25 | func-qa Agent（GLM-5V）只知验收，不知道前面步骤细节。 | func-qa | step-isolation |
| C26 | 仓库基础结构完整性：创建新仓库时，必须同步复制所有schema文件（debate-output.schema.json、execution-manifest.schema.json）和必要脚本（validate_debate_output.py等）。不得遗漏。 | Trae统筹 | repository-integrity |
| C27 | 测试即门：模块二Step 1产出的代码文件如无对应测试文件（test_*.py或*_test.py），Trae统筹必须拒绝进入Step 2。开发Agent不知道此规则存在。 | Trae统筹 | test-gating |
| C28 | 门必须挡住不该通过的东西：每个验证脚本必须包含至少一个golden negative测试用例（必定失败的输入），并在repo CI中验证该失败被正确检出。无此用例的验证脚本视为未完成。 | 全体 | verification-integrity |
| C29 | 无用户模式降级：当用户显式跳过确认（"只要结果"/"不用问我"/"go ahead"等），系统自动进入无用户模式：跳过Phase 5用户确认门，但须完成模块二全部4个Step和审计闸门。模块三复盘仍正常触发。 | Trae统筹 | autonomy-degradation |
| C30 | code-qa实效性：code-qa必须实际执行测试文件并附执行结果摘要，不能仅通过代码审查产出报告。产出报告中须包含：测试通过数/失败数、lint错误数。 | code-qa | qa-effectiveness |
| C31 | 编排器完整闭环：编排器状态机必须在AUDIT_GATE后插入MODULE_3_REVIEW步骤，再进入DONE。L3项目强制执行完整的Module 3（Phase 1-5），L2项目至少执行Phase 1-2记录（Phase 3-5提醒后可选）。 | Trae统筹 | orchestrator-integrity |
| C32 | 测试闸门质量下限：C27测试闸门不仅检查测试文件存在，还必须验证测试文件中包含至少2个有效断言（assert/self.assert*且非`assert True`）。包含`assert True`且无其他断言的测试文件视为未通过闸门。 | Trae统筹 | test-gating |
| C33 | 产出真实性：任何由脚本/编排器/自动化工具代理产出的交付物（代码、报告、测试等），必须在文件首行标注生成方式（`# @generated-by: model` vs `# @generated-by: script`）。审计闸门检查此标注，mock产出在标注`@generated-by: script`时不视为真实通过的产出。 | 全体 | verification-integrity |

| C34 | 增强 代码质量 检查: A组有 11 个测试失败，B组全部通过 (+246%) | 全体 | verification-integrity |

## 修订记录

- v1.0:  - v1.4.0: 新增 C34 (experiment-loop)
初始规则 — 2026-05-22
- v1.1: 新增C26仓库基础结构完整性规则 — 2026-05-22 (todo-api项目复盘)
- v1.2: 修订C10分级别评分门槛；新增C27测试即门、C28验证脚本golden negative、C29无用户模式降级、C30 code-qa实效性 — 2026-05-22 (ab-exp项目复盘)
- v1.3: 新增C31编排器完整闭环、C32测试闸门质量下限、C33产出真实性 — 2026-05-22 (ab-exp项目复盘)
