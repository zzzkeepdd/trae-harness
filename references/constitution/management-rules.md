# 管理规则

> 跨阶段通用规则，编排器 + 复盘时加载

| ID | 条款 |
|:---:|------|
| C31 | run_harness 统一调用标准：所有子Agent调用时使用标准化参数格式，确保可追踪可复现。 |
| C35 | 每次实验批次完成后，必须触发 Module 3 复盘（Phase 1-5：复盘辩论→裁决→草案→确认→合并宪法）。 |
| C36 | 宪法生命周期：rules/→drafts/→proposals/→full-constitution.md。proposals状态：draft→confirmed→merged。 |
| C37 | Token ROI 追踪：每次实验记录上下文字节数、辩论轮次、总耗时。复盘时统计节省量。 |
| C38 | 原子组防撞：多条规则同属一个原子组时，必须检查是否有冲突。有冲突则标记并裁决。 |
| C39 | 实验方法论：A/B 两组使用同一模型，评估手段独立于被测系统。不可用 Harness 审计器检查无 Harness 代码。 |
| C41 | 攻击维度注入机制：L3 任务每个 must_fix 必须在 attacks 中对应 ≥1 条 ≥3 分攻击。避免规则盲区（如 dry-violation A=B=0%）因未被攻击/审查而漏过。v15实验证据。 |
