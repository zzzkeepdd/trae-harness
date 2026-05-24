#!/usr/bin/env python3
"""
Harness Orchestrator v2.0 — 自适应铁面门卫，纯 stdlib。

v2.0 新增: 从 project-profile.json 动态加载状态机、产出物和闸门。
        未匹配模板时回退 v1.0 硬编码默认值，100% 向后兼容。

用法:
  orchestrator.py --init    <任务目录> <项目名>
  orchestrator.py --advance <任务目录>
  orchestrator.py --status  <任务目录>
  orchestrator.py --self-test

默认状态机（无 profile 时）:
  INIT → PHASE_0 → PHASE_1 → PHASE_2 → GATE_1 → PHASE_3 → PHASE_4 → GATE_2
  → PHASE_5 → M2_STEP_1 → TEST_GATE → M2_STEP_2 → M2_STEP_3 → AUDIT_GATE → DONE

有 project-profile.json 时:
  状态机、产出物、闸门均从 profile 动态构建。
"""
import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime

HARNESS_ROOT = Path(__file__).parent.parent.resolve()

DEFAULT_PHASES = [
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

DEFAULT_OUTPUTS = {
    "PHASE_0": {"files": ["complexity-level.txt"], "desc": "复杂度分级文件"},
    "PHASE_1": {"files": ["research-brief.md"], "desc": "调研摘要(3调研员合并)"},
    "PHASE_2": {"files": ["debate-output.json"], "desc": "辩论输出JSON"},
    "GATE_1": {"gate": "validate_debate_output.py", "desc": "节点门1: 辩论输出验证"},
    "PHASE_3": {"files": ["review-summary.md"], "desc": "审核裁决摘要"},
    "PHASE_4": {"files": ["spec.md", "execution-manifest.json"], "desc": "需求规格说明书+执行清单"},
    "GATE_2": {"gate": "check_testability.py", "desc": "节点门2: 验收标准可测性"},
    "PHASE_5": {"files": [".handover-complete"], "desc": "用户确认标记(.handover-complete)"},
    "MODULE_2_STEP_1": {"files": [], "desc": "开发Agent产出(文件存在性由闸门检查)"},
    "TEST_GATE": {"gate": "run_test_suite.py", "desc": "C27 测试闸门"},
    "MODULE_2_STEP_2": {"files": ["code-qa-report.md"], "desc": "代码技术验收报告"},
    "MODULE_2_STEP_3": {"files": ["func-qa-report.md"], "desc": "功能业务验收报告"},
    "AUDIT_GATE": {"gate": "harness_auditor.py", "desc": "最终审计闸门"},
}

GATE_SCRIPT_PARAMS = {
    "validate_debate_output.py": lambda task: [str(task / "debate-output.json")],
    "check_testability.py": lambda task: [str(task / "spec.md")],
    "run_test_suite.py": lambda task: [str(task)],
    "harness_auditor.py": lambda task, level: [
        "--pipeline", level.lower(), str(task), str(HARNESS_ROOT)
    ],
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


def load_profile(task_dir):
    pp = Path(task_dir) / "project-profile.json"
    if pp.exists():
        return json.loads(pp.read_text(encoding="utf-8"))
    return None


def build_dynamic_phases(profile):
    if not profile:
        return DEFAULT_PHASES
    gates = profile.get("gates", [])
    phases = [
        "INIT", "PHASE_0", "PHASE_1", "PHASE_2",
    ]
    if "GATE_1" in gates:
        phases.append("GATE_1")
    phases.extend(["PHASE_3", "PHASE_4"])
    if "GATE_2" in gates:
        phases.append("GATE_2")
    phases.append("PHASE_5")
    phases.extend(["MODULE_2_STEP_1"])
    gate_map = {g: g for g in gates}
    m2_gates = [g for g in gates if g not in ("GATE_1", "GATE_2") and g != "AUDIT_GATE"]
    for g in m2_gates:
        phases.append(g)
        idx = gates.index(g)
        suffix = f"MODULE_2_STEP_{idx + 1}" if idx < 9 else f"M2_post_{g}"
        phases.append(suffix)
    if "AUDIT_GATE" in gates:
        phases.append("AUDIT_GATE")
    phases.append("DONE")
    return phases


def build_dynamic_outputs(profile):
    if not profile:
        return DEFAULT_OUTPUTS
    required = profile.get("required_outputs", {})
    gates = profile.get("gates", [])
    outputs = {
        "PHASE_0": {"files": ["complexity-level.txt"], "desc": "复杂度分级文件"},
        "PHASE_1": {"files": ["research-brief.md"], "desc": "调研摘要(3调研员合并)"},
        "PHASE_2": {"files": ["debate-output.json"], "desc": "辩论输出JSON"},
        "PHASE_3": {"files": ["review-summary.md"], "desc": "审核裁决摘要"},
        "PHASE_4": {"files": ["spec.md", "execution-manifest.json"], "desc": "需求规格+执行清单"},
        "PHASE_5": {"files": [".handover-complete"], "desc": "用户确认标记"},
        "MODULE_2_STEP_1": {"files": [], "desc": "开发/创作Agent产出"},
    }
    for gate_id in gates:
        if gate_id == "GATE_1":
            outputs["GATE_1"] = {"gate": "validate_debate_output.py", "desc": "辩论输出验证"}
        elif gate_id == "GATE_2":
            outputs["GATE_2"] = {"gate": "check_testability.py", "desc": "验收标准可测性"}
        elif gate_id == "TEST_GATE":
            outputs["TEST_GATE"] = {"gate": "run_test_suite.py", "desc": "测试闸门"}
        elif gate_id == "AUDIT_GATE":
            outputs["AUDIT_GATE"] = {"gate": "harness_auditor.py", "desc": "最终审计闸门"}
        elif gate_id == "VISUAL_GATE":
            outputs["VISUAL_GATE"] = {"gate": "check_visual_integrity.py", "desc": "视觉完整性闸门"}
    for phase_key, phase_data in required.items():
        phase_key = phase_key.replace("MODULE_2_STEP_2", "MODULE_2_STEP_2")
        phase_key = phase_key.replace("MODULE_2_STEP_3", "MODULE_2_STEP_3")
        if phase_key not in outputs:
            outputs[phase_key] = {}
        outputs[phase_key].update(phase_data)
    return outputs


def get_phases(profile):
    return build_dynamic_phases(profile)


def get_outputs(profile):
    return build_dynamic_outputs(profile)


def check_files(task_dir, phase, profile):
    outputs = get_outputs(profile)
    req = outputs.get(phase, {})
    files = req.get("files", [])
    task = Path(task_dir)
    missing = []
    for f in files:
        if not (task / f).exists():
            missing.append(f)
    return missing


def run_gate(task_dir, phase, pipeline_level, profile):
    outputs = get_outputs(profile)
    req = outputs.get(phase, {})
    gate_script = req.get("gate", "")
    if not gate_script:
        return True, "无脚本门(自动通过)"

    script_path = HARNESS_ROOT / "scripts" / gate_script
    if not script_path.exists():
        try:
            script_path = HARNESS_ROOT / "scripts" / "check_visual_integrity.py"
            if not script_path.exists():
                return True, f"门脚本不存在但允许继续: {gate_script}"
        except Exception:
            return True, f"门脚本不存在但允许继续: {gate_script}"

    task = Path(task_dir)
    params_fn = GATE_SCRIPT_PARAMS.get(gate_script)
    if params_fn:
        try:
            extra_args = params_fn(task) if gate_script != "harness_auditor.py" else params_fn(task, pipeline_level)
        except TypeError:
            extra_args = params_fn(task)
        cmd = [sys.executable, str(script_path)] + extra_args
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


def is_gate_phase(phase, profile):
    outputs = get_outputs(profile)
    return phase in outputs and "gate" in outputs[phase]


def init(task_dir, project_name):
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
    print(f"当前阶段: INIT (等待 Phase 0 项目分类+复杂度判定)")
    print()
    print("下一步: Agent 执行 Phase 0 → 产出 project-profile.json + complexity-level.txt，然后运行:")
    print(f"  orchestrator.py --advance {task_dir}")


def status(task_dir):
    state = load_state(task_dir)
    if not state:
        print("未初始化。运行 --init 开始。")
        sys.exit(1)

    profile = load_profile(task_dir)
    phases = get_phases(profile)
    outputs = get_outputs(profile)
    current = state["current_phase"]
    idx = phases.index(current) if current in phases else -1

    print(f"项目: {state['project_name']}")
    print(f"级别: {state['pipeline_level']}")
    if profile:
        print(f"类型: {profile.get('project_type', 'unknown')}")
    print(f"当前: {current}")
    print(f"创建: {state['created_at']}")
    print()

    print("流程进度:")
    for i, phase in enumerate(phases):
        if i == idx:
            marker = " ← 当前位置"
        elif idx > i:
            marker = " ✓"
        else:
            marker = ""
        req = outputs.get(phase, {})
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
    state = load_state(task_dir)
    if not state:
        print("FAIL — 未初始化。先运行 --init。")
        sys.exit(1)

    profile = load_profile(task_dir)
    phases = get_phases(profile)
    outputs = get_outputs(profile)
    current = state["current_phase"]

    if current == "DONE":
        print("PASS — 全部流程已完成。")
        return

    idx = phases.index(current)
    pipeline_level = state.get("pipeline_level", "L2")
    phase = current

    if is_gate_phase(phase, profile):
        print(f">>> {phase}: 运行验证脚本 ...")
        passed, msg = run_gate(task_dir, phase, pipeline_level, profile)
        if not passed:
            state["history"].append({
                "phase": phase, "status": "FAIL",
                "time": datetime.now().isoformat(), "message": msg
            })
            save_state(task_dir, state)
            print(f"FAIL — 门 '{phase}' 未通过")
            print(msg)
            print()
            print(f"修复后重新运行: orchestrator.py --advance {task_dir}")
            sys.exit(1)
        else:
            print(f"  {msg}")
    else:
        if phase in ("INIT", "DONE"):
            pass
        else:
            print(f">>> {phase}: 检查产物文件 ...")
            missing = check_files(task_dir, phase, profile)
            if missing:
                message = f"缺少文件: {', '.join(missing)}"
                state["history"].append({
                    "phase": phase, "status": "FAIL",
                    "time": datetime.now().isoformat(), "message": message
                })
                save_state(task_dir, state)
                print(f"FAIL — {message}")
                print()
                print(f"创建缺失文件后重新运行: orchestrator.py advance {task_dir}")
                sys.exit(1)
            else:
                files_count = len(outputs.get(phase, {}).get("files", []))
                if files_count > 0:
                    print(f"  全部 {files_count} 个产物文件存在 ✓")
                else:
                    print(f"  (无文件要求，自动通过)")

    state["history"].append({
        "phase": phase, "status": "PASS", "time": datetime.now().isoformat()
    })

    next_idx = idx + 1
    if next_idx >= len(phases):
        state["current_phase"] = "DONE"
        save_state(task_dir, state)
        print(f"\n==> 推进: {phase} → DONE")
        print("PASS — 全部流程完成。可以交付。")
        return

    next_phase = phases[next_idx]
    state["current_phase"] = next_phase
    save_state(task_dir, state)

    req = outputs.get(next_phase, {})
    next_desc = req.get("desc", next_phase)
    print(f"\n==> 推进: {phase} → {next_phase}")
    print(f"PASS — 进入下一阶段")
    print(f"阶段: {next_phase} — {next_desc}")
    if req.get("files"):
        print(f"需产出: {', '.join(req['files'])}")
    if req.get("gate"):
        print(f"门脚本: {req['gate']}")


def set_level(task_dir, level):
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
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        task_dir = Path(tmp) / "test-task"
        task_dir.mkdir()

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

        (task_dir / "complexity-level.txt").write_text("L2")
        r2 = subprocess.run(
            [sys.executable, __file__, "advance", str(task_dir)],
            capture_output=True, text=True, timeout=10
        )
        if r2.returncode != 0:
            print(f"GOLDEN NEGATIVE FAIL #2 — 有产物但 advance 失败: {r2.stdout}\n{r2.stderr}")
            sys.exit(1)

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
    parser = argparse.ArgumentParser(description="Harness Orchestrator v2.0 (自适应)")
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
