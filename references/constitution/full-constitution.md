# 完整宪法

> 本文件为索引和修订记录。运行时规则按阶段分散加载，见 `rules-by-phase/` 各文件。

## 宪法版本清单

| 版本 | 日期 | 变更 | 触发实验 |
|------|------|------|----------|
| v1.0 | 2026-05-22 | 初始规则 C01-C25 | — |
| v1.1 | 2026-05-22 | 新增 C26 | todo-api |
| v1.2 | 2026-05-22 | 修订 C10；新增 C27-C30 | ab-exp |
| v1.3 | 2026-05-22 | 新增 C31-C33 | ab-exp |
| v1.4.0 | 2026-05-23 | 新增 C34-C36 | experiment-loop |
| v1.5.0 | 2026-05-23 | 新增 C37-C39（修复占位规则污染） | v5-v11 批次复盘 |
| v2.0 | 2026-05-24 | C22-C25 泛化；project-profile.json 自适应 | — |
| **v2.1** | **2026-05-26** | **新增 C40-C41；规则按阶段拆分加载；审计器多文件检查** | **v12-v16 批次复盘** |

## 按阶段加载索引

### Phase 0 — 复杂度分级 + 攻击配置

| ID | 规则 | 文件 |
|:--:|------|------|
| C01 | 用户可见产品=是 → 至少L2 | [phase-0-complexity.md](rules-by-phase/phase-0-complexity.md) |
| C02 | L1判据全满足 | ↑ |
| C03 | L3判据任一满足 | ↑ |
| C04 | 其他=L2 | ↑ |
| C26 | 攻击数量门槛 per 等级 | ↑ |
| C34 | 攻击维度池（10个维度） | ↑ |

### Phase 1 — 调研

| ID | 规则 | 文件 |
|:--:|------|------|
| C05 | 调研员只读不写 | [phase-1-research.md](rules-by-phase/phase-1-research.md) |
| C06 | 输出≤200词 | ↑ |
| C07 | 三调研员并行独立 | ↑ |

### Phase 2 — 辩论

| ID | 规则 | 文件 |
|:--:|------|------|
| C08 | 维度串行 | [phase-2-debate.md](rules-by-phase/phase-2-debate.md) |
| C09 | 红≥3边界，蓝逐条回 | ↑ |
| C10 | 分级门槛 | ↑ |
| C11 | 轮次控制 | ↑ |
| C30 | debate-output.json schema | ↑ |

### Phase 3 — 审核

| ID | 规则 | 文件 |
|:--:|------|------|
| C12 | 检查维度覆盖 | [phase-3-review.md](rules-by-phase/phase-3-review.md) |
| C13 | 代码可行性建议 | ↑ |
| C14 | 交叉验证冲突 | ↑ |
| C15 | debate-output.json schema | ↑ |

### Phase 4 — 规范生成

| ID | 规则 | 文件 |
|:--:|------|------|
| C16 | 只基于辩论输出 | [phase-4-spec.md](rules-by-phase/phase-4-spec.md) |
| C17 | 信息瓶颈 200 token | ↑ |
| C18 | 可测验收标准 | ↑ |

### Phase 5 — 交付

| ID | 规则 | 文件 |
|:--:|------|------|
| C19 | 用户确认门 | [phase-5-handover.md](rules-by-phase/phase-5-handover.md) |
| C20 | 上下文清理时机 | ↑ |
| C21 | 保留清单 | ↑ |

### Module 2 — 步骤隔离

| ID | 规则 | 文件 |
|:--:|------|------|
| C22 | 步骤隔离 | [module-2-steps.md](rules-by-phase/module-2-steps.md) |
| C23 | 开发Agent隔离 | ↑ |
| C24 | QA Agent隔离 | ↑ |
| C25 | func-qa隔离 | ↑ |

### Module 2 — 测试与质量门

| ID | 规则 | 文件 |
|:--:|------|------|
| C27 | 测试文件存在闸门 | [module-2-test-gates.md](rules-by-phase/module-2-test-gates.md) |
| C28 | 质量门双激活 | ↑ |
| C29 | 覆盖率闸门 | ↑ |
| C32 | 有效断言检查 | ↑ |
| C33 | 审计闸门 | ↑ |
| C40 | 多维度质量门（5新维度）| ↑ |

### 跨阶段 — 管理规则

| ID | 规则 | 文件 |
|:--:|------|------|
| C31 | 编排器闭环含 Module 3 | [management-rules.md](management-rules.md) |
| C35 | Module 3 复盘触发 | ↑ |
| C36 | 宪法生命周期 | ↑ |
| C37 | Token ROI 追踪 | ↑ |
| C38 | 原子组防撞 | ↑ |
| C39 | 实验方法论 | ↑ |

### 复盘专用

| ID | 规则 | 文件 |
|:--:|------|------|
| C41 | 攻击维度注入机制（must_fix↔attacks绑定） | [management-rules.md](management-rules.md) |

## 文件结构

```
constitution/
├── full-constitution.md        # 本文件（索引+修订记录）
├── meta-rules.md               # M01 元规则
├── management-rules.md         # C31,C35-C39,C41 跨阶段管理规则
├── proposals.md                # 待确认草案
└── rules-by-phase/
    ├── phase-0-complexity.md   # C01-C04,C26,C34 共6条
    ├── phase-1-research.md     # C05-C07 共3条
    ├── phase-2-debate.md       # C08-C11,C30 共5条
    ├── phase-3-review.md       # C12-C15 共4条
    ├── phase-4-spec.md         # C16-C18 共3条
    ├── phase-5-handover.md     # C19-C21 共3条
    ├── module-2-steps.md       # C22-C25 共4条
    └── module-2-test-gates.md  # C27-C29,C32-C33,C40 共6条
```

## 元规则

| ID | 条款 | 适用角色 |
|:--:|------|----------|
| M01 | 任何流程指令，凡不附带不可绕过之产出物及验证机制者，视为软建议。 | 全体 |
