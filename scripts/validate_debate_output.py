#!/usr/bin/env python3
"""节点门1：辩论输出 JSON schema + 维度覆盖 + 攻击点硬计数验证。纯 stdlib。v4.0
v4.0 变更 (ab-exp 复盘):
  - 新增 golden negative 自测
  - 新增 C10 分级评分门槛 (L1/L2/L3)
  - 新增攻击点内容质量检查 (description 非空, scoring_rationale 非空)
  - 新增 must_fix 非空检查
"""
import sys
import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "references/constitution/debate-output.schema.json"


def run_golden_negatives():
    """C28: 必须包含 golden negative 测试——传入注定失败的数据，验证脚本能正确检出。"""
    failures = []

    case1 = {"verified_items": [], "rounds_completed": 0, "converged": True}
    if run_validations(case1) == True:
        failures.append("golden-neg1: rounds_completed=0 未检出")

    case2 = {"verified_items": [], "converged": True,
             "attacks": [{"description": "weak", "score": 2}],
             "dimensions_covered": [{"name": "d1", "status": "covered"}],
             "rounds_completed": 1}
    if run_validations(case2) == True:
        failures.append("golden-neg2: 所有攻击点 < 3分 未检出")

    case3 = {"verified_items": [], "rounds_completed": 1, "converged": True,
             "attacks": [{"score": 5}],
             "dimensions_covered": [{"name": "d1", "status": "covered"}]}
    if run_validations(case3) == True:
        failures.append("golden-neg3: 攻击点缺少 description 未检出")

    if failures:
        print(f"GOLDEN NEGATIVE FAIL — 验证脚本自身不合规 ({len(failures)} 项):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    return True


def run_validations(data):
    """返回 True 表示通过，返回 list 表示有 errors"""
    errors = []

    if "rounds_completed" not in data or not (1 <= data["rounds_completed"] <= 3):
        errors.append("rounds_completed 必须在 1-3")
    if not isinstance(data.get("converged"), bool):
        errors.append("converged 必须为 boolean")
    if not isinstance(data.get("must_fix"), list) or len(data.get("must_fix", [])) == 0:
        errors.append("must_fix 非空数组")

    attacks = data.get("attacks", [])
    if not isinstance(attacks, list) or len(attacks) == 0:
        errors.append("attacks 非空数组")
        return errors

    total_attacks = len(attacks)

    content_ok = True
    for i, a in enumerate(attacks):
        if not isinstance(a, dict):
            errors.append(f"attacks[{i}] 不是 object")
            content_ok = False
            continue
        if not a.get("description") or len(str(a.get("description", "")).strip()) < 10:
            errors.append(f"attacks[{i}] description 过短或缺失")
            content_ok = False
        if not a.get("scoring_rationale") or len(str(a.get("scoring_rationale", "")).strip()) < 5:
            errors.append(f"attacks[{i}] scoring_rationale 过短或缺失")
            content_ok = False

    high_score_count = sum(1 for a in attacks if isinstance(a, dict) and a.get("score", 0) >= 3)
    low_score_count = sum(1 for a in attacks if isinstance(a, dict) and a.get("score", 0) <= 0)
    if low_score_count > 0:
        errors.append(f"攻击点评分含 <= 0 分项 ({low_score_count} 条)")

    dims = data.get("dimensions_covered", [])
    if isinstance(dims, list) and len(dims) > 0:
        covered = [d for d in dims if isinstance(d, dict) and d.get("status") == "covered"]
        dim_total = len(dims)
        dim_covered = len(covered)
        if dim_covered < dim_total:
            uncovered = [d.get("name", "?") for d in dims if isinstance(d, dict) and d.get("status") != "covered"]
            errors.append(f"维度覆盖率 {dim_covered}/{dim_total}，未覆盖: {uncovered}")
        min_attacks = dim_total * 2
        if total_attacks < min_attacks:
            errors.append(f"攻击点不足: {total_attacks} < {min_attacks}（维度数{dim_total} x2）")

    level = data.get("complexity_level", "L2")
    if level == "L1":
        if high_score_count < 1 or total_attacks < 3:
            errors.append(f"C10 L1 门槛不满足: 高分{high_score_count}(需>=1) 总数{total_attacks}(需>=3)")
    elif level == "L3":
        if high_score_count < 3 or total_attacks < 5:
            errors.append(f"C10 L3 门槛不满足: 高分{high_score_count}(需>=3) 总数{total_attacks}(需>=5)")
    else:
        if high_score_count < 2 or total_attacks < 4:
            errors.append(f"C10 L2 门槛不满足: 高分{high_score_count}(需>=2) 总数{total_attacks}(需>=4)")

    if errors:
        return errors
    return True


def main(json_path):
    data = None
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"FAIL: 无法解析JSON — {e}")
        sys.exit(1)

    result = run_validations(data)
    if result is True:
        dims = data.get("dimensions_covered", [])
        dim_covered = sum(1 for d in dims if isinstance(d, dict) and d.get("status") == "covered")
        attacks = data.get("attacks", [])
        total_attacks = len(attacks) if isinstance(attacks, list) else 0
        high_score = sum(1 for a in attacks if isinstance(a, dict) and a.get("score", 0) >= 3)
        level = data.get("complexity_level", "L2")
        print(f"PASS ({level}) — 攻击点{total_attacks}，高分{high_score}，维度覆盖{dim_covered}/{len(dims)}")
    else:
        print(f"FAIL — {len(result)} 项不合规：")
        for e in result:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        run_golden_negatives()
        print("PASS — 所有 golden negative 测试通过，验证脚本自身合规")
    elif len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("用法: validate_debate_output.py <json路径>")
        print("      validate_debate_output.py --self-test  (C28 golden negative 自测)")
        sys.exit(1)
