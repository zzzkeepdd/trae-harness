# Harness A/B 对照实验

## 实验目标

验证 Trae Harness 能否提升国内弱模型的工程产出质量。用单一模型分别以"无Harness直接实现"和" Harness流程"两种方式完成 6 个任务，对比量化结果。

---

## 实验设计

### 任务池（6 个任务）

| 任务 | 难度 | 文件 | 核心挑战 |
|------|:----:|------|---------|
| L1-1 字符串工具库 | L1 | `tasks/l1/l1-1-string-utils.md` | 边界条件处理（空字符串、None）|
| L1-2 列表处理工具 | L1 | `tasks/l1/l1-2-list-utils.md` | 嵌套结构、key函数设计 |
| L2-1 TTL+LRU缓存库 | L2 | `tasks/l2/l2-1-cache.md` | 线程安全、LRU正确性、TTL竞态 |
| L2-2 CSV数据处理器 | L2 | `tasks/l2/l2-2-csv-processor.md` | 文件IO、聚合、往返一致性 |
| L3-1 并发任务队列 | L3 | `tasks/l3/l3-1-task-queue.md` | 优先级队列、重试、超时、优雅关闭 |
| L3-2 会话管理服务 | L3 | `tasks/l3/l3-2-session-manager.md` | JWT手写实现、RBAC、Token黑名单 |

### 对照设计

```
同一模型 × 同一任务 × 两种方式

对照组 A（no-harness）：
  直接 prompt → 模型直接输出代码 → 测试验证

实验组 B（harness）：
  Phase 1 预调研（3调研员并行）
  Phase 2 维度辩论（红/蓝/裁判）
  Phase 3 审核裁决
  Phase 4 规范生成
  Phase 5 用户确认
  模块二 TDD 开发
  Step 4 审计闸门
```

---

## 量化指标

| 指标 | 说明 | 测量方式 |
|------|------|---------|
| **Harness Auditor** | 最终合规审计是否通过 | PASS/FAIL |
| **辩论攻击点数量** | 红队发现的风险点总数 | 统计 attacks 数组长度 |
| **高分攻击点（≥3分）** | 直击核心的攻击数 | 统计 score≥3 的攻击 |
| **must_fix 项数** | 必须修复的严重问题数 | 统计 must_fix 数组长度 |
| **代码缺陷数** | TODO/FIXME/time.time()/NotImplementedError 等 | 静态扫描 |
| **代码行数（LOC）** | 有效代码行数 | 去注释后行数 |
| **节点门通过数** | 节点门1/2/3 通过率 | 脚本验证结果 |
| **审计合规** | harness_auditor.py 最终审计 | PASS/FAIL |

---

## 环境准备

### 1. 配置模型 API

在本地终端设置环境变量：

```bash
# OpenAI 兼容 API（如自己部署的模型代理）
export MODEL_BASE_URL="https://your-model-proxy.example.com/v1"
export MODEL_API_KEY="sk-your-key-here"
export MODEL_NAME="qwen-plus"   # 或 deepseek-chat / gpt-4o / glm-4 等

# 验证配置
python -c "from scripts.model_call import call_model; print(call_model('direct', 'say hello'))"
```

### 2. 复制 Harness 到可访问位置

```bash
# 脚本里用相对路径引用 harness 的 scripts/ 目录
# 确保 ab-exp/ 的父目录有 trae-harness/
ls <ab-exp父目录>/scripts/harness_auditor.py
```

---

## 运行实验

### 方式一：一键运行全部（推荐）

```bash
cd ab-exp
python scripts/run_all_tasks.py

# 或者指定结果目录
python scripts/run_all_tasks.py ./my_results
```

这会自动：
1. 依次运行 6 个任务
2. 每个任务跑两轮（no-harness → harness）
3. 保存原始输出到 `results/`
4. 输出日志到 `results/run_log_*.txt`

**预计耗时**：取决于模型响应速度，每个任务 2-5 分钟，全部跑完约 20-40 分钟。

### 方式二：单任务调试

```bash
# 只跑一个任务
python scripts/run_single_task.py tasks/l2/l2-1-cache.md results/l2-1-cache

# 对照组 A（无Harness）
python scripts/run_single_task.py tasks/l2/l2-1-cache.md results/l2-1-cache --no-harness

# 实验组 B（Harness）
python scripts/run_single_task.py tasks/l2/l2-1-cache.md results/l2-1-cache
```

### 方式三：手动调用（更精细控制）

```bash
# 在 Python 里直接用
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from model_call import call_model, extract_code

# 测试模型连通性
r = call_model('direct', '实现一个加法函数', task_desc='a+b', ac_list='AC-1: 1+1=2')
print(r[:500])
"
```

---

## 收集与分析结果

```bash
# 全部跑完后，运行结果分析
python scripts/collect_results.py

# 输出：
# - 控制台量化对比表格
# - results/results.csv（详细数据）
# - results/report.md（Markdown报告）
```

---

## 目录结构

```
ab-exp/
├── README.md                      # 本文件
├── tasks/
│   ├── l1/
│   │   ├── l1-1-string-utils.md  # 任务定义
│   │   └── l1-2-list-utils.md
│   ├── l2/
│   │   ├── l2-1-cache.md
│   │   └── l2-2-csv-processor.md
│   └── l3/
│       ├── l3-1-task-queue.md
│       └── l3-2-session-manager.md
├── scripts/
│   ├── model_call.py             # 模型调用封装
│   ├── run_single_task.py        # 单任务运行器
│   ├── run_all_tasks.py          # 批量运行器
│   └── collect_results.py        # 结果收集与分析
└── results/                      # 运行后自动生成
    ├── run_log_*.txt
    ├── l1-1-string-utils/
    │   ├── noharness/            # 对照组 A 输出
    │   └── harness/               # 实验组 B 输出
    ├── l2-1-cache/
    │   ├── noharness/
    │   └── harness/
    ├── ...
    ├── results.csv               # CSV 对比数据
    └── report.md                  # Markdown 报告
```

---

## 预期结果解读

### 如果 Harness 有效，期望看到：

1. **实验组 B 审计通过率 > 对照组 A**（尤其是 L2/L3 任务）
2. **实验组 B 辩论发现额外的边界条件**（攻击点数量 > 0）
3. **实验组 B 代码缺陷数 < 对照组 A**（防御式编程更好）
4. **must_fix 项不为零**（说明辩论真正发现了问题）
5. **L1 任务两组差异小**（L1 本身简单，Harness 提升有限）
6. **L3 任务两组差异大**（复杂度越高，Harness 补偿效果越明显）

### 如果 Harness 无效，期望看到：

1. 两组审计通过率相近
2. 辩论攻击点全为低分（1-2 分），must_fix 为空
3. 代码缺陷数无显著差异
4. LOC 差异仅来自代码风格而非质量

---

## 注意事项

1. **模型选择影响实验有效性**：建议用国内二三级模型（Qwen-Turbo、DeepSeek-V2 等）对比国际顶尖模型（GPT-4o、Claude-3.5），而不是同一模型跑两次
2. **Prompt 差异**：实验组 B 的 Harness 流程本质上是结构化 prompt 约束，如果模型本身很强差异会缩小
3. **成本**：6 个任务 × 2 轮 = 12 次模型调用，按 token 消耗估算
4. **Harness 流程简化**：当前脚本里只实现了核心辩论+开发，未包含完整的 Phase 3 审核和 Phase 4 规范生成（因为这些需要多次模型调用），如需完整流程可扩展
