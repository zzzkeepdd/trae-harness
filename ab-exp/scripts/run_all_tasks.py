#!/usr/bin/env python3
"""
批量运行所有 6 个任务的 A/B 对照实验
用法: python run_all_tasks.py [results_dir]

会依次运行：
  L1-1 (string-utils)
  L1-2 (list-utils)
  L2-1 (cache)
  L2-2 (csv-processor)
  L3-1 (task-queue)
  L3-2 (session-manager)

每个任务跑两轮：
  1. --no-harness（对照组A）
  2. 默认（实验组B，Harness）

需要在环境中设置：
  export MODEL_BASE_URL="https://your-api/v1"
  export MODEL_API_KEY="sk-xxx"
  export MODEL_NAME="your-model-name"
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
TASKS_DIR = SCRIPT_DIR.parent / "tasks"
OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR.parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TASKS = [
    ("l1", "l1-1-string-utils.md"),
    ("l1", "l1-2-list-utils.md"),
    ("l2", "l2-1-cache.md"),
    ("l2", "l2-2-csv-processor.md"),
    ("l3", "l3-1-task-queue.md"),
    ("l3", "l3-2-session-manager.md"),
]

LOG_FILE = OUT_DIR / f"run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.write_text(LOG_FILE.read_text() + line + "\n", encoding="utf-8")

def run_single(task_rel, mode):
    task_file = TASKS_DIR / task_rel
    task_out = OUT_DIR / task_file.stem / mode
    task_out.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(SCRIPT_DIR / "run_single_task.py"),
        str(task_file),
        str(task_out),
    ]
    if mode == "noharness":
        cmd.append("--no-harness")
    log(f"开始: {task_file.stem} [{mode}]")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        log(f"完成: {task_file.stem} [{mode}] exit={r.returncode}")
        if r.stdout:
            log(f"STDOUT: {r.stdout[:500]}")
        if r.returncode != 0 and r.stderr:
            log(f"STDERR: {r.stderr[:300]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log(f"超时: {task_file.stem} [{mode}]")
        return False
    except Exception as e:
        log(f"错误: {e}")
        return False

def main():
    LOG_FILE.write_text("", encoding="utf-8")
    summary = []
    for level, task in TASKS:
        log(f"========== {task} ==========")
        a_ok = run_single(f"{level}/{task}", "noharness")
        b_ok = run_single(f"{level}/{task}", "harness")
        summary.append({
            "task": task,
            "level": level,
            "noharness_ok": a_ok,
            "harness_ok": b_ok,
        })
        log(f"结果: noharness={'OK' if a_ok else 'FAIL'}, harness={'OK' if b_ok else 'FAIL'}")

    summary_file = OUT_DIR / "experiment_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    log(f"\n全部完成！汇总: {summary_file}")
    print(f"\n实验完成，结果保存在: {OUT_DIR}")
    print("下一步: python collect_results.py")

if __name__ == "__main__":
    main()
