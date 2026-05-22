---
name: trae-harness
description: "一人公司" Trae版 — 注意力友好的多Agent协作框架。全程保持3子Agent并行，步骤隔离防幻觉，信息瓶颈防注意力漂移。
version: 1.2
phase: stable
---

# Trae Harness v1.2

编排器模式：每个 Phase 产出后必须跑 `harness_orchestrator.py advance`，门不通过则阻塞，确保 100% 流程执行。

## 快速开始

```bash
# 1. 初始化任务
python scripts/harness_orchestrator.py init <项目目录> --name <项目名>

# 2. Agent 执行 Phase 0 → 产出 complexity-level.txt → 推进
python scripts/harness_orchestrator.py advance <项目目录>

# 3. 在每个 Phase 产出文件后重复第 2 步
# 编排器自动检查产物 + 验证门，不通过则阻塞

# 4. 查看进度
python scripts/harness_orchestrator.py status <项目目录>

# 5. 自测（CI/CD）
python scripts/harness_orchestrator.py self-test
```

## 状态机（编排器强制执行）

```
INIT → PHASE_0 → PHASE_1 → PHASE_2 → GATE_1 → PHASE_3 → PHASE_4 → GATE_2
→ PHASE_5 → M2_STEP_1 → TEST_GATE → M2_STEP_2 → M2_STEP_3 → AUDIT_GATE → DONE
```

每个 → 都经过编排器检查：
- **Phase**: 检查产物文件是否存在 (complexity-level.txt / debate-output.json / spec.md ...)
- **Gate**: 运行验证脚本并检查 exit code (validate_debate_output.py / run_test_suite.py / harness_auditor.py ...)
- 不通过 → 阻塞，打印缺失项，Agent 修复后重新 advance

## 三模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 模块一 | [module-1-clarify.md](references/workflows/module-1-clarify.md) | 需求澄清，维度拆分，红蓝辩论 |
| 模块二 | [module-2-tdd.md](references/workflows/module-2-tdd.md) | TDD开发，步骤隔离，验收链（含 C27 测试闸门） |
| 模块三 | [module-3-review.md](references/workflows/module-3-review.md) | 复盘宪法，规则积累 |

## 宪法 v1.2 新增规则

| ID | 条款 | 原因 |
|:---:|------|------|
| C10 | 分级评分门槛: L1≥1≥3分≥3个; L2≥2≥3分≥4个; L3≥3≥3分≥5个 | ab-exp 复盘 |
| C27 | 测试即门: 无 test_*.py 拒绝进入 Step 2 | ab-exp 复盘 |
| C28 | 验证脚本必须有 golden negative 自测 | ab-exp 复盘 |
| C29 | 无用户模式降级: 跳过确认但不跳过闸门 | ab-exp 复盘 |
| C30 | code-qa 必须实际执行测试并附结果 | ab-exp 复盘 |

## 角色索引

参见 [references/agent-roster/](references/agent-roster/)

## 规则索引

- [元规则](references/constitution/meta-rules.md) — 必加载
- [按阶段拆分规则](references/constitution/rules-by-phase/) — 按需加载
- [完整宪法](references/constitution/full-constitution.md) — 复盘参考

## 验证脚本

```bash
# 编排器（总控）
python scripts/harness_orchestrator.py advance <项目目录>

# 节点门1: 辩论输出验证
python scripts/validate_debate_output.py <辩论JSON路径>

# 节点门2: 验收标准可测性检查
python scripts/check_testability.py <需求规格说明书路径>

# 节点门3: 执行清单验证
python scripts/validate_execution_manifest.py <执行清单JSON路径>

# C27 测试闸门
python scripts/run_test_suite.py <项目目录>

# 最终审计
python scripts/harness_auditor.py --pipeline <l1|l2|l3> <项目目录> <harness根目录>
```

## 使用

```
"启动一人公司，我要开发一个 [你的项目]"
```

编排器确保 Trae Harness 自动按复杂度分级，调度子Agent完成全流程，且**每个闸门不可跳过**。
