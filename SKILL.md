---
name: trae-harness
description: "一人公司" Trae版 — 注意力友好的多Agent协作框架。全程保持3子Agent并行，步骤隔离防幻觉，信息瓶颈防注意力漂移。编排器铁面门卫，闸门不可跳过。
version: 1.5.0
phase: stable
---

# Trae Harness v1.5.0

## 核心铁律 — 不可跳过

**以下行为绝对禁止，违者实验无效：**

1. ❌ 不跑 `init` 就直接写代码
2. ❌ 不跑 `advance` 就进入下一 Phase
3. ❌ 闸门失败后不修复、直接跳过
4. ❌ 在 Phase 0 之前就创建文件或写代码
5. ❌ 跳过辩论、跳过审核、跳过审计

**编排器是唯一路径。** 每完成一个 Phase 必须跑 `python <harness>/scripts/harness_orchestrator.py advance <项目目录>`。编排器检查通过才放行，不通过则阻塞并打印缺失项。

## 完整状态机

```
INIT ──→ PHASE_0 ──→ PHASE_1 ──→ PHASE_2 ──→ GATE_1 ──→ PHASE_3 ──→ PHASE_4 ──→ GATE_2
──→ PHASE_5 ──→ M2_STEP_1 ──→ TEST_GATE ──→ M2_STEP_2 ──→ M2_STEP_3 ──→ AUDIT_GATE ──→ DONE
```

每个 `──→` 都必须跑 `advance`。没有捷径。

## 启动流程（必须严格按顺序）

### Step 0: 找到 harness 路径

```bash
HARNESS="~/.trae/skills/trae-harness"
# 或项目内路径
```

### Step 1: 初始化

```bash
python $HARNESS/scripts/harness_orchestrator.py init <项目目录> --name <项目名>
```

此步骤创建 `.harness_state.json`。没有这个文件，后续 advance 全部失败。

### Step 2: 按 Phase 执行

每个 Phase 的详细流程见下方「各 Phase 执行清单」。**每个 Phase 结束后必须跑 advance。**

```bash
python $HARNESS/scripts/harness_orchestrator.py advance <项目目录>
```

### Step 3: 查看状态

```bash
python $HARNESS/scripts/harness_orchestrator.py status <项目目录>
```

## 各 Phase 执行清单

### INIT (init 后自动完成)

产出: `.harness_state.json`

### PHASE_0 — 复杂度判定

1. 分析用户需求
2. 产出 `complexity-level.txt`，内容只能是 `L1`、`L2` 或 `L3`
   - L1: ≤3文件、单一技术栈、无UI、无外部依赖
   - L3: 文件>15、API≥3、并发/权限、3+技术栈
   - 其他 = L2
3. **跑 advance**

### PHASE_1 — 预调研（3调研员并行）

1. 创建3个调研员子Agent，并行产出:
   - 项目环境调研 (≤200词)
   - 行业标准调研 (≤200词)
   - 技术风险调研 (≤200词)
2. 汇总为 `research-brief.md`
3. **跑 advance**

### PHASE_2 — 维度辩论

1. 根据 L 级别确定维度数量: L1=3, L2=5, L3=7
2. 每个维度单独辩论: 红队(攻击) / 蓝队(防御) / 裁判(评分)
3. 合并所有维度产出 `debate-output.json`
4. **跑 advance**（此时触发 GATE_1）

### GATE_1 — 辩论验证

编排器自动运行 `validate_debate_output.py`:
- 检查 JSON schema
- L1≥1个维度≥3分≥3攻击点；L2≥2个≥3分≥4个；L3≥3个≥3分≥5个
- 不通过 → 阻塞，回 Phase 2 修复

### PHASE_3 — 审核裁决（3审核员并行）

1. 创建3个审核员子Agent:
   - 需求完整性对照
   - 代码可行性建议
   - 交叉验证 + 合并结果
2. 产出 `review-summary.md`
3. **跑 advance**

### PHASE_4 — 规范生成

1. 基于 debate-output.json 生成规范
2. 产出:
   - `spec.md`（需求规格说明书）
   - `execution-manifest.json`（执行清单，≤200 token）
3. **跑 advance**（此时触发 GATE_2）

### GATE_2 — 可测性 + 清单验证

编排器自动运行:
- `check_testability.py <spec.md>` — 验收标准可测性
- `validate_execution_manifest.py <execution-manifest.json>` — schema 验证
- 不通过 → 阻塞，回 Phase 4 修复

### PHASE_5 — 用户确认

1. 展示 spec 和辩论结论给用户
2. 用户确认后产出 `.handover-complete`
3. **跑 advance**
4. 清除模块一上下文（保留 debate-output.json / spec.md / execution-manifest.json）

### M2_STEP_1 — 开发

1. 创建开发Agent（只知本任务，不知后续 code-qa/func-qa）
2. 测试先行: 先写 test_*.py，再写 main.py
3. 产出代码到 `src/` 目录
4. **跑 advance**（此时触发 TEST_GATE）

### TEST_GATE — 测试闸门 (C27/C32/C35)

编排器自动运行 `run_test_suite.py <项目目录>`:
- 每个源文件必须有对应测试文件
- `__init__.py` 除外
- 至少 2 个有效断言 (C32)，非 `assert True`
- 覆盖率 ≥70% public 函数 (C35)
- 不通过 → 阻塞，开发Agent整改（作为新任务，不告知整改原因）

### M2_STEP_2 — 代码技术验收 (code-qa)

1. 创建 code-qa Agent（只知验收，不知 func-qa）
2. 实际执行测试并记录结果 (C30)
3. 运行 lint 检查
4. 安全扫描
5. 产出 `code-qa-report.md`
6. **跑 advance**

### M2_STEP_3 — 功能业务验收 (func-qa)

1. 创建 func-qa Agent（只知 code-qa 已通过）
2. e2e 测试
3. 功能比对验收标准
4. 产出 `func-qa-report.md`
5. **跑 advance**（此时触发 AUDIT_GATE）

### AUDIT_GATE — 最终审计

编排器自动运行 `harness_auditor.py --pipeline <L级别> <项目目录> <harness根目录>`:
- 检查宪法规则覆盖 (C26-C39)
- 检查产出物完整性
- 不通过 → 阻塞，打印缺失项，回相应步骤修复

### DONE

全部通过，交付用户。

## 防跳过机制

| 机制 | 作用 |
|------|------|
| `.harness_state.json` | 编排器只认此文件，没有则全部 advance 失败 |
| `advance` 门禁 | 每个 Phase 结束时必须跑，Gate 自动触发验证脚本 |
| 验证脚本 exit code | 非 0 即阻塞，编排器不关心原因，只关心结果 |
| 整改作为新任务 | 失败后创建新任务，Agent 不知道这是整改 |

## 快速开始

```
"启动一人公司，我要开发一个 [你的项目]"
```

## 三模块参考

| 模块 | 文件 |
|------|------|
| 模块一 | [module-1-clarify.md](references/workflows/module-1-clarify.md) |
| 模块二 | [module-2-tdd.md](references/workflows/module-2-tdd.md) |
| 模块三 | [module-3-review.md](references/workflows/module-3-review.md) |

## 宪法体系 (39条)

- [元规则](references/constitution/meta-rules.md) — M01，必加载
- [按阶段拆分规则](references/constitution/rules-by-phase/) — 按需加载，每Agent≤4条
- [管理规则](references/constitution/management-rules.md) — C26-C39，跨阶段
- [完整宪法](references/constitution/full-constitution.md) — 复盘参考

## 验证脚本

```bash
python $HARNESS/scripts/harness_orchestrator.py init <项目目录> --name <项目名>
python $HARNESS/scripts/harness_orchestrator.py advance <项目目录>
python $HARNESS/scripts/harness_orchestrator.py status <项目目录>
python $HARNESS/scripts/validate_debate_output.py <辩论JSON路径>
python $HARNESS/scripts/check_testability.py <spec.md路径>
python $HARNESS/scripts/validate_execution_manifest.py <清单JSON路径>
python $HARNESS/scripts/run_test_suite.py <项目目录>
python $HARNESS/scripts/harness_auditor.py --pipeline <l1|l2|l3> <项目目录> <harness根目录>
```