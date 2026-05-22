#!/usr/bin/env python3
"""
Harness Orchestrator — 铁面门卫，100% 流程执行保证。纯 stdlib。v1.0

用法:
  orchestrator.py --init    <任务目录> <项目名>          初始化新任务
  orchestrator.py --advance <任务目录>                   检查当前 Phase 产物 + 门，通过则推进
  orchestrator.py --status  <任务目录>                   查看当前状态
  orchestrator.py --self-test                             golden negative 自测

状态机:
  INIT → PHASE_0 → PHASE_1 → PHASE_2 → GATE_1 → PHASE_3 → PHASE_4 → GATE_2
  → PHASE_5 → M2_STEP_1 → TEST_GATE → M2_STEP_2 → M2_STEP_3 → AUDIT_GATE → DONE

每个 Phase 要求产出物 (必须存在)，Gate 要求验证脚本通过 (exit 0)。
编排器不做创造性工作，不替代 Agent。只当门卫。
"""
import sys
import os
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime

HARNESS_ROOT = Path(__file__).parent.parent.resolve()

PHASES = [
    "INIT",
    "PHASE_0",
    "PHASE_1",
    "PHASE_2",
    "GATE_1",
    "PHASE_3",
    "PHASE_4",
    "GATE_2",
    "PHASE_5",
    "MODULE_2_STEP_1",
    "TEST_GATE",
    "MODULE_2_STEP_2",
    "MODULE_2_STEP_3",
    "AUDIT_GATE",
    "DONE",
]

REQUIRED_OUTPUTS = {
    "PHASE_0": {"files": ["complexity-level.txt"], "desc": "复杂度分级文件"},
    "PHASE_1": {"files": ["research-brief.md"], "desc": "调研摘要(3调研员合并)"},
    "PHASE_2": {"files": ["debate-output.json"], "desc": "辩论输出JSON"},
    "GATE_1": {"gate": "validate_debate_output.py", "desc": "节点门1: 辩论输出验证"},
    "PHASE_3": {"files": ["review-summary.md"], "desc": "审核裁决摘要"},
    "PHASE_4": {"files": ["spec.md", "execution-manifest.json"], "desc": "需求规格说明书+执行清单"},
    "GATE_2": {"gate": "check_testability.py", "desc": "节点门2: 验收标准可测性"},
    "PHASE_5": {"files": [".handover-complete"], "desc": "用户确认标记(.handover-complete)"},
    "MODULE_2_STEP_1": {"files": [], "desc": "开发Agent产出(文件存在性由TEST_GATE检查)"},
    "TEST_GATE": {"gate": "run_test_suite.py", "desc": "C27 测试闸门"},
    "MODULE_2_STEP_2": {"files": ["code-qa-report.md"], "desc": "代码技术验收报告"},
    "MODULE_2_STEP_3": {"files": ["func-qa-report.md"], "desc": "功能业务验收报告"},
    "AUDIT_GATE": {"gate": "harness_auditor.py", "desc": "最终审计闸门"},
}


def get_state_path(task_dir):
    return Path(task_dir) / ".harness_state.json"


def load_state(task_dir):
    p = get_state_path(task_dir)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_state(task_dir, state):
    get_state_path(task_dir).write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def check_files(task_dir, phase):
    """检查当前 Phase 的必需文件是否存在"""
    req = REQUIRED_OUTPUTS.get(phase, {})
    files = req.get("files", [])
    task = Path(task_dir)
    missing = []
    for f in files:
        if not (task / f).exists():
            missing.append(f)
    return missing


def run_gate(task_dir, phase, pipeline_level):
    """运行门脚本，返回 (passed, output_message)"""
    req = REQUIRED_OUTPUTS.get(phase, {})
    gate_script = req.get("gate", "")
    if not gate_script:
        return True, "无脚本门(自动通过)"

    script_path = HARNESS_ROOT / "scripts" / gate_script
    if not script_path.exists():
        return False, f"门脚本不存在: {script_path}"

    task = Path(task_dir)

    if gate_script == "validate_debate_output.py":
        debate_json = task / "debate-output.json"
        if not debate_json.exists():
            return False, "debate-output.json 不存在"
        cmd = [sys.executable, str(script_path), str(debate_json)]
    elif gate_script == "check_testability.py":
        spec = task / "spec.md"
        if not spec.exists():
            return False, "spec.md 不存在"
        cmd = [sys.executable, str(script_path), str(spec)]
    elif gate_script == "run_test_suite.py":
        cmd = [sys.executable, str(script_path), str(task)]
    elif gate_script == "harness_auditor.py":
        cmd = [sys.executable, str(script_path),
               "--pipeline", pipeline_level.lower(),
               str(task), str(HARNESS_ROOT)]
    else:
        cmd = [sys.executable, str(script_path), str(task)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                                cwd=str(task))
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stdout.strip() + "\n" + result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "门脚本执行超时(60s)"
    except Exception as e:
        return False, f"门脚本执行异常: {e}"


def init(task_dir, project_name):
    """初始化新任务"""
    task = Path(task_dir).resolve()
    if not task.exists():
        task.mkdir(parents=True)

    if load_state(task_dir):
        print(f"任务目录已有状态文件。运行 --status 查看或删除 .harness_state.json 重新初始化。")
        sys.exit(1)

    state = {
        "project_name": project_name,
        "pipeline_level": "L2",
        "current_phase": "INIT",
        "created_at": datetime.now().isoformat(),
        "history": [],
        "notes": "",
    }
    save_state(task_dir, state)
    print(f"PASS — 初始化完成: {project_name} ({task})")
    print(f"当前阶段: INIT (等待 Phase 0 复杂度判定)")
    print()
    print("下一步: Agent 执行 Phase 0 → 产出 complexity-level.txt，然后运行:")
    print(f"  orchestrator.py --advance {task_dir}")


def status(task_dir):
    """查看当前状态"""
    state = load_state(task_dir)
    if not state:
        print("未初始化。运行 --init 开始。")
        sys.exit(1)

    current = state["current_phase"]
    idx = PHASES.index(current) if current in PHASES else -1

    print(f"项目: {state['project_name']}")
    print(f"级别: {state['pipeline_level']}")
    print(f"当前: {current}")
    print(f"创建: {state['created_at']}")
    print()

    print("流程进度:")
    for i, phase in enumerate(PHASES):
        if i == idx:
            marker = " ← 当前位置"
        elif PHASES.index(current) > i:
            marker = " ✓"
        else:
            marker = ""
        req = REQUIRED_OUTPUTS.get(phase, {})
        desc = req.get("desc", phase)
        print(f"  [{phase:<16}] {desc}{marker}")

    if state["history"]:
        print()
        print("执行历史:")
        for h in state["history"][-5:]:
            print(f"  {h['phase']} → {h['status']} ({h['time']})")
            if h.get("message"):
                print(f"    {h['message']}")


def check_and_advance(task_dir):
    """核心门卫逻辑：检查当前 Phase 产物 + 门 → 推进或阻止"""
    state = load_state(task_dir)
    if not state:
        print("FAIL — 未初始化。先运行 --init。")
        sys.exit(1)

    current = state["current_phase"]
    if current == "DONE":
        print("PASS — 全部流程已完成。")
        return

    idx = PHASES.index(current)
    pipeline_level = state.get("pipeline_level", "L2")

    # --- 检查当前 Phase 产物或门 ---
    phase = current

    # 门检查
    if current.startswith("GATE_") or current == "TEST_GATE" or current == "AUDIT_GATE":
        print(f">>> {phase}: 运行验证脚本 ...")
        passed, msg = run_gate(task_dir, phase, pipeline_level)
        if not passed:
            message = f"门 '{phase}' 未通过"
            state["history"].append({
                "phase": phase, "status": "FAIL", "time": datetime.now().isoformat(), "message": msg
            })
            save_state(task_dir, state)
            print(f"FAIL — {message}")
            print(msg)
            print()
            print(f"修复后重新运行: orchestrator.py --advance {task_dir}")
            sys.exit(1)
        else:
            print(f"  {msg}")
    else:
        # 文件检查
        if phase == "INIT":
            # INIT → PHASE_0 直接跳转，无文件要求
            pass
        elif phase == "DONE":
            print("PASS — 全部流程已完成。")
            return
        else:
            print(f">>> {phase}: 检查产物文件 ...")
            missing = check_files(task_dir, phase)
            if missing:
                message = f"缺少文件: {', '.join(missing)}"
                state["history"].append({
                    "phase": phase, "status": "FAIL", "time": datetime.now().isoformat(), "message": message
                })
                save_state(task_dir, state)
                print(f"FAIL — {message}")
                print()
                print(f"创建缺失文件后重新运行: orchestrator.py advance {task_dir}")
                sys.exit(1)
            else:
                files_count = len(REQUIRED_OUTPUTS.get(phase, {}).get("files", []))
                if files_count > 0:
                    print(f"  全部 {files_count} 个产物文件存在 ✓")
                else:
                    print(f"  (无文件要求，自动通过)")

    # --- 记录通过 ---
    state["history"].append({
        "phase": phase, "status": "PASS", "time": datetime.now().isoformat()
    })

    # --- 推进到下一个 Phase ---
    next_idx = idx + 1
    if next_idx >= len(PHASES):
        state["current_phase"] = "DONE"
        save_state(task_dir, state)
        print(f"\n==> 推进: {phase} → DONE")
        print("PASS — 全部流程完成。可以交付。")
        return

    next_phase = PHASES[next_idx]
    state["current_phase"] = next_phase
    save_state(task_dir, state)

    req = REQUIRED_OUTPUTS.get(next_phase, {})
    next_desc = req.get("desc", next_phase)
    print(f"\n==> 推进: {phase} → {next_phase}")
    print(f"PASS — 进入下一阶段")
    print(f"阶段: {next_phase} — {next_desc}")
    if req.get("files"):
        print(f"需产出: {', '.join(req['files'])}")
    if req.get("gate"):
        print(f"门脚本: {req['gate']}")


def set_level(task_dir, level):
    """设置复杂度级别"""
    state = load_state(task_dir)
    if not state:
        print("FAIL — 未初始化。")
        sys.exit(1)
    if level not in ("L1", "L2", "L3"):
        print(f"FAIL — 无效级别: {level}")
        sys.exit(1)
    state["pipeline_level"] = level
    save_state(task_dir, state)
    print(f"PASS — 级别设置为 {level}")


def golden_negative():
    """C28: 编排器自身 golden negative 测试"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        task_dir = Path(tmp) / "test-task"
        task_dir.mkdir()

        # 测试1: PHASE_0 无产出 → advance 应被阻止
        state = {
            "project_name": "gn-test", "pipeline_level": "L2",
            "current_phase": "PHASE_0", "created_at": datetime.now().isoformat(), "history": []
        }
        save_state(str(task_dir), state)

        r1 = subprocess.run(
            [sys.executable, __file__, "advance", str(task_dir)],
            capture_output=True, text=True, timeout=10
        )
        if r1.returncode == 0:
            print("GOLDEN NEGATIVE FAIL #1 — 无产物但 advance 通过")
            sys.exit(1)

        # 测试2: 创建产物后 advance 应通过
        (task_dir / "complexity-level.txt").write_text("L2")
        r2 = subprocess.run(
            [sys.executable, __file__, "advance", str(task_dir)],
            capture_output=True, text=True, timeout=10
        )
        if r2.returncode != 0:
            print(f"GOLDEN NEGATIVE FAIL #2 — 有产物但 advance 失败: {r2.stdout}\n{r2.stderr}")
            sys.exit(1)

        # 测试3: 所有门脚本都能通过 --self-test (C28 级联)
        for script in ["validate_debate_output.py", "run_test_suite.py", "harness_auditor.py"]:
            sp = HARNESS_ROOT / "scripts" / script
            if sp.exists():
                r = subprocess.run([sys.executable, str(sp), "--self-test"],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode != 0:
                    print(f"GOLDEN NEGATIVE FAIL #3 — {script} --self-test 失败: {r.stdout}\n{r.stderr}")
                    sys.exit(1)
    return True


def main():
    parser = argparse.ArgumentParser(description="Harness Orchestrator v1.0")
    sub = parser.add_subparsers(dest="action")

    p_init = sub.add_parser("init", help="初始化新任务")
    p_init.add_argument("task_dir", help="任务目录")
    p_init.add_argument("--name", default="harness-task", help="项目名")

    p_adv = sub.add_parser("advance", help="检查当前阶段并推进")
    p_adv.add_argument("task_dir", help="任务目录")

    p_st = sub.add_parser("status", help="查看当前状态")
    p_st.add_argument("task_dir", help="任务目录")

    lp = sub.add_parser("set-level", help="设置复杂度级别")
    lp.add_argument("task_dir", help="任务目录")
    lp.add_argument("--level", choices=["L1", "L2", "L3"], required=True)

    sub.add_parser("self-test", help="golden negative 自测")

    args = parser.parse_args()

    if args.action == "self-test":
        golden_negative()
        print("PASS — 所有 golden negative 测试通过，编排器自身合规")
        return

    if args.action == "init":
        init(args.task_dir, getattr(args, "name", "harness-task"))
        return

    task_dir = args.task_dir

    if args.action == "advance":
        check_and_advance(task_dir)
    elif args.action == "status":
        status(task_dir)
    elif args.action == "set-level":
        set_level(task_dir, args.level)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
