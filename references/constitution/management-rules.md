# 宪法管理规则

> 跨阶段规则，所有 Agent 在工作时按需加载。

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| M01 | 任何流程指令必须附带产出物和验证机制，否则视为软建议。 | 全体 | immutable |
| C26 | 仓库基础结构完整性：创建新仓库时，必须同步复制所有 schema 文件和必要验证脚本。 | Trae统筹 | repository-integrity |
| C27 | 测试即门：模块二 Step 1 产出后如无 test_*.py，Trae 统筹拒绝进入 Step 2。开发 Agent 不知道此规则存在。 | Trae统筹 | test-gating |
| C28 | 门必须挡住：每个验证脚本必须包含至少一个 golden negative 用例并验证其被检出。 | 全体 | verification-integrity |
| C29 | 无用户模式降级：用户跳过确认 → 跳过 Phase 5 用户门，但须完成 Module 2 全部 Step + 审计闸门。Module 3 仍触发。 | Trae统筹 | autonomy-degradation |
| C30 | code-qa 实效性：code-qa 必须实际执行测试文件并附结果摘要（通过数/失败数/lint 错误数），不能仅代码审查。 | code-qa | qa-effectiveness |
| C31 | 编排器完整闭环：AUDIT_GATE 后插入 MODULE_3_REVIEW 再进入 DONE。L3 强制完整 Module 3，L2 至少 Phase 1-2。 | Trae统筹 | orchestrator-integrity |
| C32 | 测试闸门质量下限：C27 测试闸门不仅检查文件存在，还验证 ≥2 个有效断言（非 assert True）。 | Trae统筹 | test-gating |
| C33 | 产出真实性：脚本/自动化代理产出的交付物首行必须标注 `# @generated-by: script` vs `# @generated-by: model`。 | 全体 | verification-integrity |
