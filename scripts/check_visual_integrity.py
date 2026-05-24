#!/usr/bin/env python3
"""VISUAL_GATE — 视频/设计项目视觉完整性闸门。

检查:
1. 画面文件是否存在>=3个
2. 分镜文件是否完整（storyboard.json/design-brief.json）
3. (预留) 色彩一致性与跳帧检测
"""
import sys
import json
from pathlib import Path


def check(task_dir):
    task = Path(task_dir)

    issues = []
    ok = []

    storyboard = task / "storyboard.json"
    design_brief = task / "design-brief.json"

    if storyboard.exists():
        try:
            sb = json.loads(storyboard.read_text(encoding="utf-8"))
            scenes = sb.get("scenes", [])
            if len(scenes) >= 3:
                ok.append(f"分镜场景数={len(scenes)}")
            else:
                issues.append(f"分镜场景数={len(scenes)} < 3 个")
        except json.JSONDecodeError:
            issues.append("storyboard.json JSON 格式错误")
    elif design_brief.exists():
        try:
            db = json.loads(design_brief.read_text(encoding="utf-8"))
            elements = db.get("elements", [])
            if len(elements) >= 1:
                ok.append(f"设计元素数={len(elements)}")
            else:
                issues.append("design-brief.json 无设计元素")
        except json.JSONDecodeError:
            issues.append("design-brief.json JSON 格式错误")
    else:
        issues.append("缺少 storyboard.json 或 design-brief.json（视觉项目必需）")

    if issues:
        print("FAIL — 视觉完整性未通过")
        for i in issues:
            print(f"  → {i}")
        return False

    print("PASS — 视觉完整性通过")
    for o in ok:
        print(f"  ✓ {o}")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: check_visual_integrity.py <任务目录>")
        sys.exit(1)
    task_dir = sys.argv[1]
    passed = check(task_dir)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
