# 完整宪法

> 各阶段加载对应 rules-by-phase/*.md。本文件为索引和修订记录。

## 元规则

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| M01 | 任何流程指令，凡不附带不可绕过之产出物及验证机制者，视为软建议。 | 全体 | immutable |

## 基础规则

| ID | 条款 | 适用角色 | 原子组 | 加载 |
|:---:|------|----------|--------|------|
| C01 | 用户可见产品=是 → 至少L2 | Trae统筹 | — | Phase 0 |
| C02 | L1判据：≤3文件、单一技术栈、无UI、无外部依赖 | Trae统筹 | — | Phase 0 |
| C03 | L3判据：文件>15、API≥3、并发/权限、3+技术栈 | Trae统筹 | — | Phase 0 |
| C04 | 其他=L2 | Trae统筹 | — | Phase 0 |
| C05 | 调研员只读不写 | 调研员 | — | Phase 1 |
| C06 | 调研输出≤200词 | 调研员 | — | Phase 1 |
| C07 | 三调研员并行，独立产出 | 调研员 | — | Phase 1 |
| C08 | 维度串行讨论 | 辩论Agent | debate-integrity | Phase 2 |
| C09 | 红队≥3边界条件，蓝队逐条回应 | 辩论Agent | debate-integrity | Phase 2 |
| C10 | 分级门槛 L1≥1个≥3分≥3条；L2≥2个≥3分≥4条；L3≥3个≥3分≥5条 | 裁判Agent | debate-integrity | Phase 2 |
| C11 | 轮次: L1/L2=1轮, L3=2轮 | 辩论Agent | debate-philosophy | Phase 2 |
| C12 | 审核员检查维度覆盖 | 审核员 | module-one-integrity | Phase 3 |
| C13 | 审核员给代码可行性建议 | 审核员 | module-one-integrity | Phase 3 |
| C14 | 交叉验证维度冲突 | 审核员 | module-one-integrity | Phase 3 |
| C15 | 产出 debate-output.json 符合 schema | 审核员 | module-one-integrity | Phase 3 |
| C16 | 规范只基于 debate-output.json | 规范生成Agent | — | Phase 4 |
| C17 | 信息瓶颈 ≤200 token | 规范生成Agent | — | Phase 4 |
| C18 | 每个需求有可测验收标准 | 规范生成Agent | — | Phase 4 |
| C19 | 用户确认门不可跳过 | Trae统筹 | — | Phase 5 |
| C20 | 上下文清理时机 | Trae统筹 | context-management | Phase 5 |
| C21 | 清理后保留清单 | Trae统筹 | context-management | Phase 5 |
| C22 | 步骤隔离：Module 2 Agent 之间物理隔离，A 不知 B 存在 | 全体子Agent | step-isolation | Module 2 |
| C23 | Module 2 Agent A 不知 Agent B 存在 — 具体角色由 project-profile.json 定义 | Module 2 Agent A | step-isolation | Module 2 |
| C24 | Module 2 Agent B 不知 Agent C 存在 — 具体角色由 project-profile.json 定义 | Module 2 Agent B | step-isolation | Module 2 |
| C25 | Module 2 Agent C 不知前序细节 — 只看验收标准和上游产出 | Module 2 Agent C | step-isolation | Module 2 |

### 管理规则（跨阶段）

| ID | 条款 | 适用角色 | 原子组 |
|:---:|------|----------|--------|
| C26 | 仓库创建同步 schema+脚本 | Trae统筹 | repository-integrity |
| C27 | 测试即门：代码无测试文件→拒绝 | Trae统筹 | test-gating |
| C28 | 验证脚本必有 golden negative | 全体 | verification-integrity |
| C29 | 无用户模式降级 | Trae统筹 | autonomy-degradation |
| C30 | code-qa 必须实际执行测试 | code-qa | qa-effectiveness |
| C31 | 编排器完整闭环含 Module 3 | Trae统筹 | orchestrator-integrity |
| C32 | 测试闸门质量下限 ≥2 有效断言 | Trae统筹 | test-gating |
| C33 | 产出真实性标注 @generated-by | 全体 | verification-integrity |

| C34 | C32 强化: 有效断言下限从 ≥2 提高到 ≥3 (模型单独产出)，或针对 L3 任务要求 ≥5。实验证据: A组=28条 B组=124条 (×4.4) | Trae统筹 | test-gating |
| C35 | C27 强化: 测试闸门不仅检查文件存在，还要求测试文件引用源文件所有 public 函数 (覆盖率 ≥70%)。实验: A 组 62% 覆盖 | Trae统筹 | test-gating |
| C36 | 新增规则: 测试质量复盘必须包含 mutmut 变异测试 (≥100 个变异点)，变异分 < 30% 时拒绝通过测试闸门。当前手动变异精度不足。 | 全体 | verification-integrity |

| C37 | 实验有效性: SWE-bench 风格实验中，buggy code 运行测试的 `buggy_errors` 必须 ≥1，否则实验结论无效。当前实验: buggy_errors=0。 | 全体 | experiment-validity |
| C38 | Adversarial 测试区分度: 安全/防御实验中，对照组 (A组) 的 pass rate 应 <100%，否则测试套件无法区分防御质量差异。当前实验: A=B=100%。 | Trae统筹 | test-design |
| C39 | 对照实验差异性保证: 对照实验 (B组) 必须与 A 组在可测维度上存在差异。若 Δ=0，实验重新设计。当前实验: v11 LiveCodeBench Δ=0。 | Trae统筹 | experiment-validity |

## 修订记录

- v1.0: 初始规则 — 2026-05-22
- v1.1: 新增 C26 仓库基础结构完整性规则 — 2026-05-22 (todo-api)
- v1.2: 修订 C10；新增 C27-C30 — 2026-05-22 (ab-exp)
- v1.3: 新增 C31-C33 — 2026-05-22 (ab-exp)
- v1.4.0: 新增 C34-C36 — 2026-05-23 (experiment-loop)
- v1.5.0: 修复 C37-C39 占位规则污染；新增 C37 Bug注入有效性、C38 Adversarial区分度、C39 对照差异性 — 2026-05-23 (v5-v11批次复盘)
- v2.0: C22-C25 泛化为领域无关；新增 project-profile.json 自适应机制；编排器 v2.0 动态状态机 — 2026-05-24
