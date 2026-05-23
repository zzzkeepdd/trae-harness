"""Harness Auditor v4.0 — 看门大爷，合规闸门。纯 stdlib。
v4.0 变更 (ab-exp 复盘):
  - 新增 C27 测试闸门集成
  - 新增 C30 code-qa/func-qa 执行证据检查
  - 新增 golden negative 自测 (C28)
  - 保留原有文件结构检查
"""
import sys
import argparse
import subprocess
from pathlib import Path


def find_file_named(proj_dir, keyword):
    for f in proj_dir.rglob("*"):
        if f.is_file() and keyword.lower() in f.name.lower():
            return f
    return None


def file_contains(path, keywords):
    if not path or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    return any(kw.lower() in text for kw in keywords)


def check_code_qa_report(code_qa_path):
    """C30: code-qa 报告须包含实际执行证据"""
    if not code_qa_path:
        return False, ["code-qa 报告不存在"]
    text = code_qa_path.read_text(encoding="utf-8", errors="ignore").lower()
    issues = []
    if "测试结果" not in text and "test result" not in text and "passed" not in text:
        issues.append("code-qa 报告缺少测试执行结果 (C30)")
    if "lint" not in text and "pylint" not in text and "flake8" not in text and "ruff" not in text:
        issues.append("code-qa 报告缺少 lint/静态检查结果 (C30)")
    return len(issues) == 0, issues


def check_func_qa_report(func_qa_path, is_ui):
    """C30: func-qa 报告须包含执行证据"""
    if not func_qa_path:
        return False, ["func-qa 报告不存在"]
    text = func_qa_path.read_text(encoding="utf-8", errors="ignore").lower()
    issues = []
    if not any(kw in text for kw in ["验收通过", "通过数", "pass count", "e2e"]):
        issues.append("func-qa 报告缺少验收执行结果 (C30)")
    if is_ui:
        browser_kw = ["浏览器实操", "screenshot", "截图", "375px"]
        if not any(kw in text for kw in browser_kw):
            issues.append("func-qa 报告缺浏览器实操痕迹")
    return len(issues) == 0, issues


def check_test_gate(proj):
    """C27: 检查源文件是否有对应测试文件"""
    py_files = list(proj.rglob("*.py"))
    source_files = [f for f in py_files
                    if not f.name.startswith("test_") and not f.name.endswith("_test.py")
                    and f.name != "__init__.py"]
    if not source_files:
        return True, []
    test_files = set(f.name for f in py_files
                     if f.name.startswith("test_") or f.name.endswith("_test.py"))
    issues = []
    for src in source_files:
        name = src.stem
        candidates = {f"test_{name}.py", f"{name}_test.py"}
        if not candidates & test_files:
            issues.append(f"{src.relative_to(proj)} 缺少测试文件 (C27)")
    return len(issues) == 0, issues


def golden_negative():
    """C28: golden negative 自测"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        src = proj / "src.py"
        src.write_text("def foo(): pass")
        ok, _ = check_test_gate(proj)
        if ok:
            print("GOLDEN NEGATIVE FAIL — 无测试文件但通过了测试闸门")
            sys.exit(1)
    return True


def main():
    parser = argparse.ArgumentParser(description="Harness Auditor v4.0")
    parser.add_argument("--pipeline", choices=["l1", "l2", "l3"], default="l2")
    parser.add_argument("proj_root", nargs="?", default=".")
    parser.add_argument("harness_root", nargs="?", default=".")
    parser.add_argument("--self-test", action="store_true", help="C28 golden negative 自测")
    args = parser.parse_args()

    if args.self_test:
        golden_negative()
        print("PASS — 所有 golden negative 测试通过，验证脚本自身合规")
        return

    proj = Path(args.proj_root).resolve()
    harness = Path(args.harness_root).resolve()
    pipeline = args.pipeline
    failures = []

    cq = find_file_named(proj, "code-qa")
    fq = find_file_named(proj, "func-qa")

    # C27: 测试闸门
    test_ok, test_issues = check_test_gate(proj)
    if not test_ok:
        failures.extend(test_issues)

    # C30: code-qa 执行证据
    cq_ok, cq_issues = check_code_qa_report(cq)
    if not cq_ok:
        failures.extend(cq_issues)
    elif not cq:
        failures.append("缺 code-qa 报告")

    # C30: func-qa 执行证据
    ui_kw = ["用户可见产品", "网页", "前端", "gui", "移动端"]
    comp = find_file_named(proj, "complexity")
    comp_text = (comp.read_text(encoding="utf-8", errors="ignore").lower()) if comp else ""
    is_ui = any(kw.lower() in comp_text for kw in ui_kw)
    fq_ok, fq_issues = check_func_qa_report(fq, is_ui)
    if not fq_ok:
        failures.extend(fq_issues)
    elif not fq:
        failures.append("缺 func-qa 报告")

    # L1/L2/L3 QA 独立性
    if cq and fq and cq.resolve() == fq.resolve():
        failures.append(f"{pipeline.upper()} 要求 code-qa 和 func-qa 为独立文件")

    # 宪法文件检查
    const = harness / "references/constitution/management-rules.md"
    if not const.is_file():
        failures.append("宪法文件不存在 (management-rules.md)")
    else:
        ct = const.read_text(encoding="utf-8", errors="ignore").lower()
        for kw in ["m01", "c27", "c28", "c29", "c30", "c31", "c32", "c33"]:
            if kw not in ct:
                failures.append(f"宪法缺 {kw.upper()} (v1.4 必需)")

    # 复杂度分级
    if not comp:
        failures.append("缺复杂度分级文件")

    if failures:
        print(f"不通过 — {len(failures)} 项不合规：")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"PASS [{pipeline.upper()}] — 全部合规，可以交付")


if __name__ == "__main__":
    main()
