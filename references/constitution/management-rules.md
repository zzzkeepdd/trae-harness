# 宪法管理规则

> 管理规则定义了多Agent协作的边界、约束与强制要求。

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| M01 | 任何流程指令必须附带产出物和验证机制，否则视为软建议。 | 全体 | immutable |
| C08 | 同时只讨论一个维度，当前维度完成后再进入下一个。 | 辩论Agent | debate-integrity |
| C09 | 红队至少攻击3个边界条件，蓝队必须逐条回应。 | 辩论Agent | debate-integrity |
| C10 | 分级门槛：L1≥1个≥3分且≥3个攻击点；L2≥2个≥3分且≥4个；L3≥3个≥3分且≥5个。 | 裁判Agent | debate-integrity |
| C13 | 审核员必须给出代码可行性建议，为模块二提效。 | 审核员 | module-one-integrity |
| C17 | 信息瓶颈：执行清单≤200 token，下游提示词≤150词。 | 规范生成Agent | - |
| C20 | 上下文清理时机：用户确认需求规格后、模块二确认无歧义后才清除。 | Trae统筹 | context-management |
| C22 | 步骤隔离：子Agent只做当前步骤，不知道下一步。 | Trae统筹 | step-isolation |
| C27 | 测试即门：开发Agent产出后如无test_*.py，Trae统筹拒绝进入Step 2。 | Trae统筹 | test-gating |
| C28 | 验证脚本必须有golden negative测试用例，否则视为未完成。 | 全体 | verification-integrity |
| C29 | 无用户模式：确认被跳过时自动进入降级模式，仍完成模块二全部Step。 | Trae统筹 | autonomy-degradation |
| C30 | code-qa必须实际执行测试并附执行结果摘要。 | code-qa | qa-effectiveness |
