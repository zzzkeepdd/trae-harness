#!/usr/bin/env python3
"""
模型调用封装 —— 支持 OpenAI 兼容 API。
在本地实验前，请设置环境变量：
  export MODEL_BASE_URL="https://api.openai.com/v1"   # 或你自己的代理地址
  export MODEL_API_KEY="sk-xxx"
  export MODEL_NAME="gpt-4o"                          # 或 qwen、deepseek 等
"""
import os
import json
import httpx
from typing import Literal

BASE_URL = os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("MODEL_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

SYSTEM_PROMPTS = {
    "trae-coordinator": "你是 Trae 统筹，负责全流程总指挥调度。\n\n核心理念：确定每个Agent边界，不给产生幻觉的模糊空间。\n\n当前任务：{{TASK_DESC}}\n\n你只需输出下一步要执行的指令，不要执行具体任务。",
    "researcher": "你是预调研Agent，只读不写，探查项目环境、行业标准、技术风险。\n\n任务：{{TASK_DESC}}\n\n规则：\n1. 只读不写，不修改任何文件\n2. 输出≤200词结构化报告\n3. 聚焦关键信息\n\n输出格式：\n## 项目环境\n（当前代码结构、依赖、配置）\n\n## 行业标准\n（该领域的常见做法和标准）\n\n## 技术风险\n（主要技术风险点，每个≤1句）",
    "debater-red": "你是红队攻击者，负责发现边界条件和漏洞。\n\n当前维度：{{DIMENSION}}\n当前方案描述：{{PROPOSAL}}\n\n规则：\n1. 至少攻击3个边界条件\n2. 每个攻击点说明：攻击描述 + 为什么危险\n\n输出格式（JSON）：\n{\n  \"attacks\": [\n    {\"描述\": \"...\", \"target_dimension\": \"{{DIMENSION}}\", \"score\": 1-5, \"scoring_rationale\": \"...\"},\n    ...\n  ]\n}\n\n评分标准：\n1=擦边球 2=边缘问题 3=直击核心 4=致命 5=颠覆",
    "debater-blue": "你是蓝队防守者，负责回应攻击并构建方案。\n\n当前维度：{{DIMENSION}}\n红队攻击点：{{ATTACKS}}\n\n规则：\n1. 逐条回应每个攻击点\n2. 说明如何解决或为什么不需解决\n\n输出格式：\n## 回应1：[攻击描述]\n（回应内容）\n\n## 回应2：...\n...",
    "reviewer": "你是审核员，检查维度覆盖完整性并给出代码建议。\n\n辩论输出JSON：{{DEBATE_OUTPUT}}\n需求规格：{{SPEC}}\n\n规则：\n1. 检查每个维度是否已覆盖\n2. 给出代码可行性建议\n3. 交叉验证维度冲突\n\n输出格式：\n## 维度覆盖检查\n（每个维度状态：covered/partial/uncovered）\n\n## 代码可行性建议\n（技术选型、架构设计建议）\n\n## 冲突检查\n（维度间冲突及解决方案）",
    "developer": "你是开发Agent，基于以下规范实现代码。\n\n任务描述：{{TASK_DESC}}\n验收标准：{{AC_LIST}}\n\n规则：\n1. 先写测试，后写代码\n2. 测试即验收标准\n3. 只实现当前任务，不引入额外功能\n\n不要写多余代码，不要过度设计。",
    "code-qa": "你是代码技术验收Agent，执行代码技术验收。\n\n代码路径：{{CODE_PATH}}\n验收标准：{{AC_LIST}}\n\n规则：\n1. 执行集成测试\n2. 执行静态检查\n3. 执行安全扫描\n\n输出格式：\n## 集成测试结果\n（通过/失败列表）\n\n## 静态检查结果\n（问题列表）\n\n## 安全扫描结果\n（问题列表）\n\n## 通过/失败状态",
    "func-qa": "你是功能业务验收Agent，执行功能业务验收。\n\n代码路径：{{CODE_PATH}}\n验收标准：{{AC_LIST}}\n\n规则：\n1. 逐条核对验收标准\n2. 对每条标准给出 PASS/FAIL\n3. 给出警告（如有隐患）\n\n输出格式：\n## 验收标准核对\nAC-X  [标准描述] ................ [PASS/FAIL]\n...",
    "direct": "你是一个专业Python开发工程师，实现以下功能。\n\n任务描述：{{TASK_DESC}}\n验收标准：{{AC_LIST}}\n约束：{{CONSTRAINTS}}\n\n规则：\n1. 写完后运行测试验证\n2. 处理所有边界条件\n3. 不要过度设计\n\n输出你的完整实现代码（用 ```python 包裹），不要解释。",
}


def call_model(
    role: Literal[
        "researcher","debater-red","debater-blue","reviewer",
        "developer","code-qa","func-qa","trae-coordinator","direct"
    ],
    task: str,
    task_desc: str = "",
    dimension: str = "",
    proposal: str = "",
    attacks: str = "",
    debate_output: str = "",
    spec: str = "",
    ac_list: str = "",
    code_path: str = "",
    constraints: str = "",
    model: str = MODEL_NAME,
    **kwargs,
) -> str:
    template = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["direct"])
    user_msg = template
    for k, v in [
        ("{{TASK_DESC}}", task_desc),
        ("{{DIMENSION}}", dimension),
        ("{{PROPOSAL}}", proposal),
        ("{{ATTACKS}}", attacks),
        ("{{DEBATE_OUTPUT}}", debate_output),
        ("{{SPEC}}", spec),
        ("{{AC_LIST}}", ac_list),
        ("{{CODE_PATH}}", code_path),
        ("{{CONSTRAINTS}}", constraints),
    ]:
        user_msg = user_msg.replace(k, v if v else "")

    messages = [{"role": "user", "content": user_msg}]

    if not API_KEY:
        print("警告: 未设置 MODEL_API_KEY，回退为 echo 模式")
        return f"[ECHO mode, role={role}] {task}"

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.3),
                    **kwargs,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"[HTTP ERROR {e.response.status_code}]: {e.response.text[:200]}"
    except Exception as e:
        return f"[ERROR]: {e}"


def extract_code(response: str) -> str:
    import re
    match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1)
    return response
