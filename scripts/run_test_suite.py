#!/usr/bin/env python3
"""C27 测试即门：检查开发Agent产出是否包含测试文件。纯 stdlib。v1.0"""
import sys
import os
from pathlib import Path


def check_test_files(project_dir):
    """遍历项目目录，检查每个 .py 文件是否有对应的 test_*.py 或 *_test.py"""
    project = Path(project_dir)
    if not project.is_dir():
        print(f"FAIL: 目录不存在: {project_dir}")
        return False

    py_files = list(project.rglob("*.py"))
    if not py_files:
        print("WARN: 无 Python 文件，跳过测试门")
        return True

    source_files = [f for f in py_files
                    if not f.name.startswith("test_") and not f.name.endswith("_test.py")]
    test_files = [f for f in py_files
                  if f.name.startswith("test_") or f.name.endswith("_test.py")]

    failures = []
    for src in source_files:
        name = src.stem
        candidates = [
            src.parent / f"test_{name}.py",
            src.parent / f"{name}_test.py",
        ]
        if not any(c in test_files for c in candidates):
            failures.append(f"{src.relative_to(project)} 缺少测试文件 (期望 test_{name}.py 或 {name}_test.py)")

    if failures:
        print(f"FAIL — C27 测试即门: {len(failures)} 个文件缺少测试")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print(f"PASS — C27 测试即门: {len(source_files)} 个源文件均已覆盖测试 ({len(test_files)} 个测试文件)")
        return True


def golden_negative():
    """C28: golden negative 自测"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src.py"
        src.write_text("def foo(): pass")
        result = check_test_files(tmp)
        if result:
            print("GOLDEN NEGATIVE FAIL — 无测试文件但通过了闸门")
            sys.exit(1)
        return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        golden_negative()
        print("PASS — 所有 golden negative 测试通过，验证脚本自身合规")
    elif len(sys.argv) > 1:
        ok = check_test_files(sys.argv[1])
        sys.exit(0 if ok else 1)
    else:
        print("用法: run_test_suite.py <项目目录>")
        print("      run_test_suite.py --self-test  (C28 golden negative 自测)")
        sys.exit(1)
