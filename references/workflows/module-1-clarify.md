# 模块一：需求澄清流程

## 触发
用户提需求后，主Agent判定项目类型+L2+ → 启动此流程。L1跳过。

## 流程

### Phase 0: 项目分类 + 复杂度判定

**步骤 0.1：项目分类**

分析用户需求关键词，匹配项目类型模板（`references/project-templates/*.yaml`）：

1. 遍历所有模板的 `trigger_keywords`
2. 首个匹配>2 个关键词的模板即命中
3. 无匹配 → 使用 `default.yaml`
4. 若匹配到多个 → 显示候选让用户选择（显示模板 `label`）

匹配后产出 `project-profile.json`：
```json
{
  "project_type": "video-production",
  "complexity": "L2",
  "agent_roster": { "module_1": [...], "module_2": [...] },
  "debate_dimensions": [...],
  "gates": [...],
  "acceptance_criteria": [...],
  "tools": [...]
}
```

**步骤 0.2：复杂度分级**

从模板读取 `complexity_rules`，根据用户需求的实际规模匹配 L1/L2/L3：
- 若用户需求规模明显超过模板默认值 → 升一级
- 若用户需求规模明显低于模板默认值 → 降一级

产出 `complexity-level.txt`（内容为 `L1`/`L2`/`L3`）。

**步骤 0.3：确认**

向用户展示：
- 项目类型: {{ label }}
- 复杂度: {{ L1/L2/L3 }}
- Agent 阵容: Module 1 (3 个), Module 2 (3 个)
- 辩论维度: {{ dimension_count }} 个
- 质量门: {{ gate_count }} 道

用户确认 → 继续。用户修改 → 根据修改重新生成 profile。

### Phase 0.5: 维度确认（可选）
若项目模板的维度与用户需求不完全匹配：
1. 展示模板维度（标注 [模板默认]）
2. 用户说"全部默认" → 全部接受
3. 用户改任意维度 → 按修改后值辩论

### Phase 1: 预调研（3调研员并行）
创建3个调研员Agent并行：
- 调研员A：项目环境
- 调研员B：行业标准
- 调研员C：技术/实现风险

每个调研员加载 [phase-1-research.md](../phase-guides/phase-1-research.md)，产出≤200词报告。

### Phase 2: 维度辩论（自适应维度）

**从 `project-profile.json` 读取 `debate_dimensions`**，而非使用固定维度：

对于每个维度（批次轮换）：
1. 创建辩论Agent，注入维度特定的 attack_prompts 作为红队引导
2. 辩论Agent内部创建红/蓝/裁判3个Sub-Agent
3. 执行辩论：
   - L1/L2：1轮（收敛边界）
   - L3：2轮（第1轮发散功能，第2轮收敛边界）
4. 产出 debate-output.json（合并所有维度）

加载 [phase-2-debate.md](../phase-guides/phase-2-debate.md)

### Phase 2.6: 节点门1
运行 `python scripts/validate_debate_output.py <任务目录> --profile project-profile.json`
- C10分级门槛：L1≥1个≥3分且≥3攻击点；L2≥2个≥3分且≥4个；L3≥3个≥3分且≥5个
- 攻击点内容质量检查：description≥10字符，scoring_rationale≥5字符
- must_fix非空
- 不通过 → 回辩论Agent修复

### Phase 3: 审核裁决（3审核员并行）
创建3个审核员Agent并行：
- 审核员A：需求完整性对照
- 审核员B：实现可行性建议 + 开发优先级
- 审核员C：交叉验证 + 合并debate-output.json

加载 [phase-3-review.md](../phase-guides/phase-3-review.md)

### Phase 4: 规范生成
创建规范生成Agent → 产出：
- 《需求规格说明书》或《创意规格》(spec.md)
- 执行清单JSON（~200 token）
- 下游提示词（≤150词）
- 项目类型特需文件（如 storyboard.json / design-brief.json）

加载 [phase-4-spec.md](../phase-guides/phase-4-spec.md)

### Phase 4.5: 节点门2
运行 `python scripts/check_testability.py <spec.md路径>`
- 通过 → 继续
- 失败 → 回规范生成Agent修复

### Phase 5: 用户确认门 + 上下文清理
1. 主Agent呈用户确认
2. 用户说"go" → 进入模块二
3. 模块二启动且确认无歧义后 → 清除模块一对话上下文
4. 保留：debate-output.json、spec.md、execution-manifest.json、project-profile.json、complexity-level.txt

### Phase 5.1: 无用户模式降级（C29）
当用户显式跳过（"只要结果"/"不用问我"/"go ahead"等），自动进入无用户模式：
- 跳过用户等待
- **但不跳过模块二全部 Step**
- 所有闸门仍正常执行
- 模块三复盘仍正常触发

加载 [phase-5-handover.md](../phase-guides/phase-5-handover.md)

## 子Agent并发控制
- 全程保持3个子Agent并行
- 辩论阶段：同时只讨论1个维度，红/蓝/裁判3角色在辩论Agent内部并行
- 维度>3时采用批次轮换

## 项目类型自适应
Phase 0 产出的 `project-profile.json` 决定了后续所有流程：
- **Agent 阵容** → 哪个角色进入 Module 2
- **辩论维度** → 攻击什么
- **质量门** → 检查什么
- **验收标准** → 通过的判定条件
- **工具** → Agent 可以调用哪些 skill
