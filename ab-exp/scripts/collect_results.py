#!/usr/bin/env python3
"""
结果收集与分析脚本
用法: python collect_results.py [results_dir]

输出：
  1. 控制台打印的量化对比表格
  2. CSV 格式的详细数据
  3. 汇总 Markdown 报告
"""
import os
import sys
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "results"
HARNESS_ROOT = Path(__file__).parent.parent.parent  # ab-exp 的父目录是 workspace

def find_result_file(base_dir: Path, pattern: str) -> Path | None:
    for p in base_dir.rglob(pattern):
        if p.is_file():
            return p
    return None

def run_auditor(proj_dir: Path) -> dict:
    try:
        r = subprocess.run(
            [sys.executable, str(HARNESS_ROOT / "scripts" / "harness_auditor.py"),
             "--pipeline", "l1", str(proj_dir), str(HARNESS_ROOT)],
            capture_output=True, text=True, timeout=30
        )
        return {"pass": r.returncode == 0, "output": r.stdout[:200]}
    except Exception as e:
        return {"pass": False, "output": str(e)}

def analyze_code(code_path: Path) -> dict:
    if not code_path or not code_path.is_file():
        return {"loc": 0, "issues": [], "issue_count": 0}
    text = code_path.read_text(encoding="utf-8", errors="ignore")
    lines = [l for l in text.split("\n") if l.strip() and not l.strip().startswith("#")]
    issues = []
    for kw in ["time.time()", "# TODO", "# FIXME", "# XXX", "pass  #", "NotImplementedError"]:
        if kw in text:
            issues.append(kw)
    return {"loc": len(lines), "issues": issues, "issue_count": len(issues)}

def collect():
    tasks = [
        ("l1", "l1-1-string-utils"),
        ("l1", "l1-2-list-utils"),
        ("l2", "l2-1-cache"),
        ("l2", "l2-2-csv-processor"),
        ("l3", "l3-1-task-queue"),
        ("l3", "l3-2-session-manager"),
    ]
    rows = []
    for level, task_id in tasks:
        task_dir = RESULTS_DIR / task_id
        noharness_dir = task_dir / "noharness"
        harness_dir = task_dir / "harness"

        noharness_result = find_result_file(noharness_dir, "*result.json")
        harness_result = find_result_file(harness_dir, "*result.json")

        noharness_data = json.loads(noharness_result.read_text()) if noharness_result else {}
        harness_data = json.loads(harness_result.read_text()) if harness_result else {}

        code_file_nh = find_result_file(noharness_dir, "*code.py")
        code_file_h = find_result_file(harness_dir, "*code.py")

        nh_code = analyze_code(code_file_nh)
        h_code = analyze_code(code_file_h)

        auditor_nh = run_auditor(noharness_dir)
        auditor_h = run_auditor(harness_dir)

        row = {
            "task": task_id,
            "level": level,
            "nh_auditor": "PASS" if auditor_nh["pass"] else "FAIL",
            "h_auditor": "PASS" if auditor_h["pass"] else "FAIL",
            "nh_loc": nh_code["loc"],
            "h_loc": h_code["loc"],
            "nh_defects": nh_code["issue_count"],
            "h_defects": h_code["issue_count"],
            "h_debate_attacks": harness_data.get("debate_attack_count", 0),
            "h_debate_high_score": harness_data.get("debate_high_score_count", 0),
            "h_must_fix": harness_data.get("must_fix_count", 0),
            "h_duration_sec": harness_data.get("duration_sec", 0),
            "nh_duration_sec": noharness_data.get("duration_sec", 0),
        }
        rows.append(row)

    return rows

def print_table(rows):
    header = ["任务", "级别", "A审计", "B审计", "A行数", "B行数", "A缺陷", "B缺陷", "B攻击点", "B高分", "B修复项"]
    col_widths = [max(len(str(r.get(h, ""))) for r in rows + [dict(zip(header, header))]) for h in header]

    def fmt_row(data):
        return " | ".join(str(data.get(h, "")).ljust(col_widths[i]) for i, h in enumerate(header))

    sep = "-+-".join("-" * w for w in col_widths)
    print(f"\n{'='*len(sep)}")
    print("A/B 对照实验结果汇总")
    print(f"{'='*len(sep)}\n")
    print(fmt_row(dict(zip(header, header))))
    print(sep)
    for row in rows:
        print(fmt_row(row))
    print(sep)

    totals = {
        "nh_auditor_pass": sum(1 for r in rows if r["nh_auditor"] == "PASS"),
        "h_auditor_pass": sum(1 for r in rows if r["h_auditor"] == "PASS"),
        "total_nh_defects": sum(r["nh_defects"] for r in rows),
        "total_h_defects": sum(r["h_defects"] for r in rows),
        "total_debate_attacks": sum(r["h_debate_attacks"] for r in rows),
        "total_must_fix": sum(r["h_must_fix"] for r in rows),
    }
    print()
    print(f"对照组 A 审计通过: {totals['nh_auditor_pass']}/{len(rows)}")
    print(f"实验组 B 审计通过: {totals['h_auditor_pass']}/{len(rows)}")
    print(f"对照组 A 总缺陷数: {totals['total_nh_defects']}")
    print(f"实验组 B 总缺陷数: {totals['total_h_defects']}")
    print(f"实验组 B 总辩论攻击点: {totals['total_debate_attacks']}")
    print(f"实验组 B 总 must_fix 项: {totals['total_must_fix']}")

    l1_rows = [r for r in rows if r["level"] == "l1"]
    l2_rows = [r for r in rows if r["level"] == "l2"]
    l3_rows = [r for r in rows if r["level"] == "l3"]
    print(f"\n--- 按级别汇总 ---")
    for level, grp in [("L1", l1_rows), ("L2", l2_rows), ("L3", l3_rows)]:
        if grp:
            nh_pass = sum(1 for r in grp if r["nh_auditor"] == "PASS")
            h_pass = sum(1 for r in grp if r["h_auditor"] == "PASS")
            nh_def = sum(r["nh_defects"] for r in grp)
            h_def = sum(r["h_defects"] for r in grp)
            attacks = sum(r["h_debate_attacks"] for r in grp)
            mf = sum(r["h_must_fix"] for r in grp)
            print(f"  {level}: A审计{nh_pass}/{len(grp)} | B审计{h_pass}/{len(grp)} | "
                  f"A缺陷{nh_def} | B缺陷{h_def} | 攻击点{attacks} | 修复{mf}")

def write_csv(rows, out_path):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

def write_markdown(rows, out_path):
    lines = [
        "# A/B 对照实验报告",
        f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## 任务清单",
        "| 任务 | 级别 | A审计 | B审计 | A缺陷 | B缺陷 | B攻击点 | B高分攻击 | B修复项 |",
        "|------|------|-------|-------|-------|-------|---------|-----------|---------|",
    ]
    for r in rows:
        lines.append(f"| {r['task']} | {r['level']} | {r['nh_auditor']} | {r['h_auditor']} "
                     f"| {r['nh_defects']} | {r['h_defects']} | {r['h_debate_attacks']} "
                     f"| {r['h_debate_high_score']} | {r['h_must_fix']} |")

    totals = {
        "nh_pass": sum(1 for r in rows if r["nh_auditor"] == "PASS"),
        "h_pass": sum(1 for r in rows if r["h_auditor"] == "PASS"),
        "nh_def": sum(r["nh_defects"] for r in rows),
        "h_def": sum(r["h_defects"] for r in rows),
    }
    lines += [
        "\n## 总体结论",
        f"- 对照组 A（Harness审计通过）: {totals['nh_pass']}/{len(rows)}",
        f"- 实验组 B（Harness审计通过）: {totals['h_pass']}/{len(rows)}",
        f"- 对照组 A 总缺陷数: {totals['nh_def']}",
        f"- 实验组 B 总缺陷数: {totals['h_def']}",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main():
    print("收集实验结果...")
    rows = collect()
    if not rows:
        print(f"未找到结果文件，请先运行 run_all_tasks.py，结果目录: {RESULTS_DIR}")
        sys.exit(1)

    print_table(rows)

    csv_path = RESULTS_DIR / "results.csv"
    md_path = RESULTS_DIR / "report.md"
    write_csv(rows, csv_path)
    write_markdown(rows, md_path)
    print(f"\nCSV 详细数据: {csv_path}")
    print(f"Markdown 报告: {md_path}")

if __name__ == "__main__":
    main()
