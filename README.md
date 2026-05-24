# Trae Harness

> "一人公司" Trae版 — 注意力友好的多Agent协作框架 + 铁面双引擎编排器

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](./SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

## v2.0 新特性：项目类型自适应

Phase 0 不再是简单的复杂度判定——**自动识别项目类型，匹配合适的 Agent 阵容和维度**。

| 项目类型 | 触发词示例 | Module 2 Agent | 特色闸门 |
|------|------|------|:--:|
| web-app | web/api/react/vue/fastapi | developer + code-qa + func-qa | TEST_GATE |
| quant-trading | 量化/交易/策略/风控 | developer + code-qa + func-qa | TEST_GATE |
| cli-tool | cli/命令行/argparse | developer + code-qa + func-qa | TEST_GATE |
| data-pipeline | etl/数据管道/pandas | developer + code-qa + func-qa | TEST_GATE |
| **video-production** | **视频/动画/分镜/字幕** | **storyboard-planner + creative-director + visual-qa** | **VISUAL_GATE** |
| **design-document** | **设计/logo/品牌/海报** | **creative-director + visual-qa + format-qa** | **VISUAL_GATE** |
| mobile-app | 移动端/app/ios/android | developer + code-qa + func-qa | TEST_GATE |
| default | (无匹配) | developer + code-qa + func-qa | TEST_GATE |

8 个项目模板在 `references/project-templates/*.yaml`，Phase 0 自动匹配。

## 核心理念

**确定每个Agent边界，不给产生幻觉的模糊空间。**

通过以下设计实现：
- **步骤隔离**：每个子Agent只做当前步，不知道下一步
- **注意力控制**：每个子Agent规则≤4条，上下文≤400 token
- **信息瓶颈**：模块间只传递执行清单JSON (~200 token)
- **全程3子Agent**：符合Trae并发限制，保持效率
- **编排器铁门**：15步状态机，每步必须通过闸门才推进

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     Harness Orchestrator                     │
│              15步状态机，铁面门卫，100%流程保证               │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
    ┌──────▼──────┐           ┌──────▼──────┐
    │  CLI 控制   │           │  闸门脚本    │
    │ init/advance│           │ validate +   │
    │ status/set  │           │ check + run  │
    └─────────────┘           │ + audit      │
                              └──────────────┘
           │
┌──────────┴──────────────────────────────────────────────────┐
│                     SOLO Agent（主Agent，常驻）                │
│                    不负责执行，只负责调度和聚合                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │子Agent A│          │子Agent B│          │子Agent C│
   │(并行)   │          │(并行)   │          │(并行)   │
   └─────────┘          └─────────┘          └─────────┘

模块一：需求澄清
├── Phase 0: 复杂度判定（主Agent）
├── Phase 1: 3调研员并行（项目环境/行业标准/技术风险）
├── Phase 2: 维度辩论（同时1维度，红/蓝/裁判3角色并行）
├── Phase 3: 3审核员并行（完整性/代码建议/交叉验证）
├── Phase 4: 规范生成
└── Phase 5: 用户确认 → 清除上下文 → 进入模块二

模块二：TDD开发
├── Step 0: 节点门3验证
├── Step 1: 开发Agent（只知本任务）
├── Step 2: code-qa Agent（只知验收）
├── Step 3: func-qa Agent（GLM-5V，只知验收）
└── Step 4: 审计闸门 → 交付/整改

模块三：复盘宪法（主Agent内化）
```

## 版本演进

| 维度 | v1.0 | v1.5 | v2.0 |
|------|------|------|------|
| **编排器** | 无 | 15 步状态机 | **动态状态机**（从 project-profile.json 生成） |
| **闸门数量** | 2 个 | 4 个 | **5 个**（+ VISUAL_GATE） |
| **宪法规则** | 25 条 | 39 条 | 39 条（C22-C25 泛化为领域无关） |
| **Agent 阵容** | 固定 8 个 | 固定 8 个 | **按项目类型自适应**（11 个 + 按需加载） |
| **项目模板** | 无 | 无 | **8 个 YAML 模板**（自动匹配） |
| **非代码支持** | 纯代码 | 纯代码 | **视频/设计/动画** |
| **验收引擎** | 无 | 无 | **[trae-acceptance](https://github.com/zzzkeepdd/trae-acceptance)** 独立验收 skill |
| **流程保证** | ~12% | 100% | 100% |

## 编排器 — 动态状态机

状态机由 `project-profile.json` 动态生成，不同项目类型走不同的闸门路径：

```
代码项目: INIT → PHASE_0 → ... → GATE_1 → ... → GATE_2 → ... → TEST_GATE → ... → AUDIT_GATE → DONE
视频/设计: INIT → PHASE_0 → ... → GATE_1 → ... → GATE_2 → ... → VISUAL_GATE → ... → AUDIT_GATE → DONE
```

不再硬编码 15 步——自适应。

```bash
python scripts/harness_orchestrator.py --init    <任务目录> <项目名>
python scripts/harness_orchestrator.py --advance <任务目录>
python scripts/harness_orchestrator.py --status  <任务目录>
python scripts/harness_orchestrator.py --set-level <任务目录> <l1|l2|l3>
```

编排器不做创造性工作——只做门卫。每个 Phase 要求产出物必须存在，每个 Gate 要求验证脚本 exit 0 才放行。

## 快速开始

### 1. 安装Trae
下载并安装 [Trae IDE](https://www.trae.ai/)

### 2. 配置Trae Harness
将本仓库复制到Trae的skills目录：

```bash
cp -r trae-harness ~/.trae/skills/
```

### 3. 启动开发
在Trae SOLO模式下输入：

```
"启动一人公司，我要开发一个 [你的项目描述]"
```

Trae Harness会自动：
1. 判定复杂度（L1/L2/L3）
2. 拆分维度并并行调研
3. 红蓝辩论（同时1维度，3角色并行）
4. 审核裁决（3审核员并行，含代码建议）
5. 生成规范并用户确认
6. TDD开发（步骤隔离，GLM-5V视觉验收）
7. 复盘宪法（可选）

## 宪法体系 — 39 条规则

### 元规则（1 条）

| ID | 条款 |
|:---:|------|
| M01 | 任何流程指令，凡不附带不可绕过之产出物及验证机制者，视为软建议。 |

### 核心规则 C01-C25
按 Phase 拆分加载，覆盖复杂度判定、维度辩论、审核裁决、规范生成、步骤隔离等全流程。每个 Agent 只加载 ≤4 条，控制上下文 ≤400 token。

### 管理规则 C26-C39（跨阶段强制执行）

| ID | 作用 |
|:---:|------|
| C26 | 仓库创建同步 schema+脚本 |
| C27 | 测试即门：代码无测试文件→拒绝 |
| C28 | 验证脚本必有 golden negative |
| C29 | 无用户模式降级 |
| C30 | code-qa 必须实际执行测试 |
| C31 | 编排器完整闭环含 Module 3 |
| C32 | 测试闸门质量下限 ≥2 有效断言 |
| C33 | 产出真实性标注 @generated-by |
| C34 | C32 强化：有效断言 ≥3（实验证据：A=28条 B=124条 ×4.4） |
| C35 | C27 强化：测试覆盖率 ≥70% public 函数 |
| C36 | 变异测试：mutmut ≥100 变异点，变异分 <30% 拒绝 |
| C37 | 实验有效性：buggy code 测试 errors ≥1 |
| C38 | Adversarial 区分度：A 组 pass rate <100% |
| C39 | 对照差异性：B 组必须与 A 组存在可测差异 |

完整规则参见 [references/constitution/full-constitution.md](references/constitution/full-constitution.md)

## 验证脚本（7 个）

| 脚本 | 对应闸门 | 作用 |
|------|:---:|------|
| `validate_debate_output.py` | GATE_1 | 辩论 JSON 格式 + 维度完整性验证 |
| `check_testability.py` | GATE_2 | 验收标准可测性检查 |
| `validate_execution_manifest.py` | GATE_2 | 执行清单 schema 验证 |
| `run_test_suite.py` | TEST_GATE | 运行测试套件，失败则拒绝交付 |
| `check_visual_integrity.py` | VISUAL_GATE | 视觉完整性（视频/设计项目专用） |
| `harness_auditor.py` | AUDIT_GATE | 最终审计：宪法规则覆盖 + 产出物完整性 |
| `harness_orchestrator.py` | 编排器 | **动态状态机**，从 project-profile.json 构建 |

```bash
# 闸门验证
python scripts/validate_debate_output.py <辩论JSON路径>
python scripts/check_testability.py <需求规格说明书路径>
python scripts/validate_execution_manifest.py <执行清单JSON路径>
python scripts/run_test_suite.py <任务目录>
python scripts/harness_auditor.py --pipeline <l1|l2|l3> <项目目录> <harness根目录>

# 编排器
python scripts/harness_orchestrator.py --init <任务目录> <项目名>
python scripts/harness_orchestrator.py --advance <任务目录>
python scripts/harness_orchestrator.py --status <任务目录>
```

## 🔥 实验室量化验证

> 模型: **DeepSeek V4 Pro** | 实验: **v1-v11 共 11 轮 A/B 对照** | 详见 [trae-harness-experiments](https://github.com/zzzkeepdd/trae-harness-experiments)

### 代码质量提升（8 个维度，全部 WIN）

| 维度 | A 组（无 Harness） | B 组（+ Harness） | 提升 |
|------|------|------|:--:|
| 代码正确性 | 90% (36/40 tests) | **100% (40/40)** | **+10%** |
| 测试断言密度 | 28 条 | **124 条** | **×4.4** |
| 测试覆盖率 | 62% | **85%** | **+23%** |
| 代码规范 | flake8=13.0 | flake8=5.3 | **↓59%** |
| 安全防御 | CWE=0.5 | CWE=2.2 | **↑340%** |
| 长期学习 | 复发 20 | 复发 **2** | **↓91.7%** |
| 性能优化 | 1.0x | **4.61x** | **×4.61** |
| SWE-bench 回归 | 2 regressions | **0** | **↓100%** |

### 💰 Token ROI（返工 + 上下文拆分）

| 指标 | 数值 |
|------|------:|
| 单次 Harness 投入 | ~20,000 tokens |
| 单次净节省 (中位数) | **~105,900 tokens** |
| **ROI (中位数)** | **+529.5%** |
| 上下文拆分固定净赚 | **+7,500 tokens/次** |
| L3 复杂任务 ROI | **可超 +1000%** |

> **Harness 不仅提升代码质量，还在 Token 消耗上做到净盈利。** 核心逻辑：用 2 万 tokens 的前期辩论 + 质量门，节省后期 10 倍以上的返工成本。

## 目录结构
```
trae-harness/
├── SKILL.md
├── README.md
├── phase-guides/                # 6 份阶段指南（极简）
│   ├── phase-0-complexity.md
│   ├── phase-1-research.md
│   ├── phase-2-debate.md
│   ├── phase-3-review.md
│   ├── phase-4-spec.md
│   └── phase-5-handover.md
├── step-guides/                 # 5 份步骤指南（模块二）
│   ├── step-2-0-manifest.md
│   ├── step-2-1-develop.md
│   ├── step-2-2-code-qa.md
│   ├── step-2-3-func-qa.md
│   └── step-2-4-audit.md
├── references/
│   ├── agent-roster/            # Agent 角色卡（11个，按项目类型加载）
│   │   ├── trae-coordinator.md
│   │   ├── researcher.md
│   │   ├── debater.md
│   │   ├── reviewer.md
│   │   ├── spec-generator.md
│   │   ├── developer.md
│   │   ├── code-qa.md
│   │   ├── func-qa.md
│   │   ├── storyboard-planner.md  # 视频项目：分镜规划
│   │   ├── creative-director.md   # 视频/设计：创意审核
│   │   └── visual-qa.md           # 视频/设计：视觉验收
│   ├── project-templates/       # 8 个项目类型模板（v2.0 新增）
│   │   ├── web-app.yaml
│   │   ├── cli-tool.yaml
│   │   ├── quant-trading.yaml
│   │   ├── data-pipeline.yaml
│   │   ├── mobile-app.yaml
│   │   ├── video-production.yaml
│   │   ├── design-document.yaml
│   │   └── default.yaml
│   ├── constitution/
│   │   ├── meta-rules.md
│   │   ├── management-rules.md
│   │   ├── rules-by-phase/
│   │   ├── full-constitution.md
│   │   ├── proposals.md
│   │   ├── vague-words.txt
│   │   ├── debate-output.schema.json
│   │   └── execution-manifest.schema.json
│   └── workflows/
│       ├── module-1-clarify.md
│       ├── module-2-tdd.md
│       └── module-3-review.md
└── scripts/
    ├── harness_orchestrator.py      # 动态状态机编排器（v2.0）
    ├── validate_debate_output.py
    ├── check_testability.py
    ├── validate_execution_manifest.py
    ├── run_test_suite.py
    ├── check_visual_integrity.py    # 视觉闸门（v2.0 新增）
    └── harness_auditor.py
```
## 相关仓库
| 仓库 | 说明 |
|------|------|
| [trae-acceptance](https://github.com/zzzkeepdd/trae-acceptance) | 独立验收 skill（Playwright + 视觉 + 双轨复盘） |
| [trae-harness-experiments](https://github.com/zzzkeepdd/trae-harness-experiments) | v1-v11 完整 A/B 实验数据 |

## 适用场景

| 场景 | 推荐管道 | 说明 |
|------|---------|------|
| 简单脚本/工具 | L1 | ≤3文件，单一技术栈 |
| Web应用/API | L2 | 中等复杂度，完整流程 |
| 复杂系统/多模块 | L3 | 完整流程+强制复盘 |

## 注意事项

1. **不要一次性加载全部规则**：按需加载当前阶段规则
2. **不要提前清理上下文**：模块二确认无歧义后才清理模块一
3. **不要跳过闸门**：编排器强制执行，每个 Gate 必须通过
4. **不要让子Agent知道下一步**：保持步骤隔离

## 贡献

欢迎提交Issue和PR，共同完善Trae Harness。

## 许可

MIT License

---

**核心理念**：用确定性对抗模糊，用边界约束自由，用规则防幻觉。