# Phase 2 专用规则

> 红蓝辩论 + 输出规范

| ID | 条款 |
|:---:|------|
| C08 | 同时只讨论一个维度，当前维度完成后再进入下一个。 |
| C09 | 红队至少攻击3个边界条件，蓝队必须逐条回应。 |
| C10 | 裁判评分1-5分。分级：L1≥1个≥3分且≥3个；L2≥2个≥3分且≥4个；L3≥3个≥3分且≥5个。不满足打回重辩。 |
| C11 | 轮次控制：L1/L2=1轮（收敛边界），L3=2轮（先发散功能后收敛边界）。 |
| C30 | debate-output.json 必须包含字段：dimension, red_attack, blue_response, judge_score, judge_reasoning, resolution, must_fix（布尔）。裁判（judge）产出时即附带 schema 验证。 |
