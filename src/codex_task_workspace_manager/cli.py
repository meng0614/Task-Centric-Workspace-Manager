from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

TASK_SUBFOLDERS = ("input", "output", "logs", "assets", "temp", "archive")
SKILL_CATEGORIES = ("common", "media", "research", "experimental", "archive")
FORBIDDEN_STEMS = {"final", "output", "result", "test", "demo", "temp", "new_final", "ultimate_final"}


def today() -> str:
    return datetime.now().strftime("%Y%m%d")


def sanitize_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    value = value.strip("_.-")
    return value or "Task"


def safe_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    index = 2
    while True:
        candidate = path.with_name(f"{stem}_v{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def ensure_task(path: Path) -> None:
    for folder in TASK_SUBFOLDERS:
        (path / folder).mkdir(parents=True, exist_ok=True)


def workspace_root(value: str | None) -> Path:
    return Path(value or os.environ.get("CODEX_WORKSPACE_ROOT", r"E:\codex"))


def bootstrap(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    for folder in ("skills", "media", "research", "projects", "downloads", "logs", "temp", "archive"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for category in SKILL_CATEGORIES:
        (root / "skills" / category).mkdir(parents=True, exist_ok=True)
    print(json.dumps({"workspace_root": str(root), "status": "bootstrapped"}, indent=2))
    return 0


def create_task(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    date = args.date or today()
    task_name = f"{date}_{sanitize_name(args.name)}"
    task_path = root / args.domain / args.type / task_name
    ensure_task(task_path)
    update_task_registry(root, task_name, f"{args.domain}/{args.type}", task_path, status="created", notes="created by create-task")
    print(json.dumps({"task": task_name, "path": str(task_path)}, indent=2))
    return 0


def find_task(root: Path, task: str) -> Path | None:
    matches = [p for p in root.rglob(task) if p.is_dir()]
    if not matches:
        return None
    matches.sort(key=lambda p: len(str(p)))
    return matches[0]


def enforce_filename(task: str, kind: str, source: Path, date: str | None = None) -> str:
    date = date or task[:8] if re.match(r"^\d{8}_", task) else today()
    task_part = sanitize_name(task[9:] if re.match(r"^\d{8}_", task) else task)
    purpose = sanitize_name(kind)
    stem = source.stem.lower()
    if stem in FORBIDDEN_STEMS or not source.name.startswith(date):
        return f"{date}_{task_part}_{purpose}{source.suffix}"
    return source.name


def route_file(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    source = Path(args.file)
    if not source.exists():
        raise SystemExit(f"file not found: {source}")
    task_path = find_task(root, args.task)
    if task_path is None:
        raise SystemExit(f"task not found under {root}: {args.task}")
    if args.kind not in TASK_SUBFOLDERS:
        raise SystemExit(f"kind must be one of {', '.join(TASK_SUBFOLDERS)}")
    target_dir = task_path / args.kind
    target_dir.mkdir(parents=True, exist_ok=True)
    target = safe_destination(target_dir / enforce_filename(args.task, args.kind, source))
    if args.copy:
        shutil.copy2(source, target)
        action = "copied"
    else:
        shutil.move(str(source), str(target))
        action = "moved"
    print(json.dumps({"action": action, "source": str(source), "target": str(target)}, indent=2))
    return 0


def task_dirs(root: Path) -> Iterable[Path]:
    pattern = re.compile(r"^\d{8}_[A-Za-z0-9_.-]+")
    for path in root.rglob("*"):
        if path.is_dir() and pattern.match(path.name):
            yield path


def audit_workspace(root: Path) -> dict:
    tasks = list(task_dirs(root))
    complete_tasks = [p for p in tasks if all((p / sub).is_dir() for sub in TASK_SUBFOLDERS)]
    legacy_dirs = [p for p in root.rglob("*") if p.is_dir() and p.name in {"input", "output", "logs"} and not re.search(r"\\\d{8}_", str(p))]
    skill_dirs = list((root / "skills").rglob("SKILL.md")) if (root / "skills").exists() else []
    unnamed_skills = [p.parent for p in skill_dirs if "__" not in p.parent.name]
    return {
        "root": str(root),
        "task_like_dirs": len(tasks),
        "complete_task_dirs": len(complete_tasks),
        "legacy_input_output_logs_dirs": len(legacy_dirs),
        "skill_dirs": len(skill_dirs),
        "skills_missing_short_description_name": len(unnamed_skills),
    }


def audit(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    result = audit_workspace(root)
    report = root / "projects" / "codex-task-workspace-manager" / f"{today()}_WorkspaceAudit.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Workspace Audit", "", f"Generated: {datetime.now().isoformat()}", ""]
    for key, value in result.items():
        lines.append(f"- {key}: {value}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result["report"] = str(report)
    print(json.dumps(result, indent=2))
    return 0


def migrate(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    result = audit_workspace(root)
    plan_dir = root / "projects" / "codex-task-workspace-manager"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan = plan_dir / f"{today()}_MigrationPlan.md"
    lines = ["# Migration Plan", "", "This command is conservative. It reports drift and only applies safe directory creation.", ""]
    for key, value in result.items():
        lines.append(f"- {key}: {value}")
    if args.apply:
        bootstrap(argparse.Namespace(root=str(root)))
        lines.append("- apply: bootstrap directories ensured")
        mode = "apply"
    else:
        lines.append("- apply: false; no files moved")
        mode = "dry-run"
    plan.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"mode": mode, "plan": str(plan)}, indent=2))
    return 0


def read_skill_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip().strip('"') if match else ""


def classify_skill(name: str, description: str) -> str:
    haystack = f"{name} {description}".lower()
    if re.search(r"danger|reverse|security|experimental|electron", haystack):
        return "experimental"
    if re.search(r"wechat|weibo|twitter|xhs|social|image|video|article|cover|comic", haystack):
        return "media"
    if re.search(r"paper|research|academic|arxiv|citation|experiment|literature|presentation|diagram", haystack):
        return "research"
    return "common"


def skill_short_description(name: str, description: str) -> str:
    haystack = f"{name} {description}".lower()
    if "find" in haystack and "skill" in haystack:
        return "Search_OpenSourceSkills"
    if "browser" in haystack:
        return "Automate_Browser_Tasks"
    if "paper" in haystack or "academic" in haystack:
        return "Analyze_AcademicPapers"
    if "presentation" in haystack or "ppt" in haystack:
        return "Generate_AcademicPresentation"
    if "image" in haystack or "illustration" in haystack:
        return "Generate_VisualContent"
    if "workspace" in haystack:
        return "Manage_TaskWorkspace"
    words = [w.title() for w in re.split(r"[-_\s]+", name) if w][:4]
    return "_".join(words) or "GeneralSkill"


def skill_audit(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    skills_root = root / "skills"
    items = []
    for skill_md in skills_root.rglob("SKILL.md") if skills_root.exists() else []:
        path = skill_md.parent
        base = path.name.split("__", 1)[0]
        desc = read_skill_description(skill_md)
        items.append({
            "name": base,
            "path": str(path),
            "category": path.parent.name if path.parent.name in SKILL_CATEGORIES else classify_skill(base, desc),
            "has_short_description_name": "__" in path.name,
        })
    print(json.dumps({"skills": items, "count": len(items)}, indent=2))
    return 0


def skill_register(args: argparse.Namespace) -> int:
    root = workspace_root(args.root)
    skills_root = root / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for skill_md in skills_root.rglob("SKILL.md"):
        path = skill_md.parent
        name = path.name.split("__", 1)[0]
        desc = read_skill_description(skill_md)
        category = path.parent.name if path.parent.name in SKILL_CATEGORIES else classify_skill(name, desc)
        rows.append((name, category, path, desc))
    registry = skills_root / "skill_registry.md"
    lines = ["# Skill Registry", "", f"Updated: {datetime.now().isoformat()}", "", "| Skill | Category | Path | Summary | When to use | When not to use | Source | Enabled |", "|---|---|---|---|---|---|---|---|"]
    for name, category, path, desc in sorted(rows):
        summary = (desc or "No description")[:140].replace("|", "/")
        use = "When the task clearly matches this Skill"
        not_use = "When the task does not match or ownership is unclear"
        lines.append(f"| {name} | {category} | {path} | {summary} | {use} | {not_use} | local/installed | yes |")
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"registry": str(registry), "skills": len(rows)}, indent=2))
    return 0


def update_task_registry(root: Path, task: str, domain: str, path: Path, status: str, notes: str) -> None:
    registry = root / "task_registry.md"
    if not registry.exists():
        registry.write_text("# Task Registry\n\n| Task | Domain | Path | Input | Output | Skills | Status | Notes |\n|---|---|---|---|---|---|---|---|\n", encoding="utf-8")
    line = f"| {task} | {domain} | {path} |  |  |  | {status} | {notes} |\n"
    with registry.open("a", encoding="utf-8") as handle:
        handle.write(line)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workspace-manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("bootstrap")
    p.add_argument("--root")
    p.set_defaults(func=bootstrap)

    p = sub.add_parser("create-task")
    p.add_argument("--root")
    p.add_argument("--domain", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--date")
    p.set_defaults(func=create_task)

    p = sub.add_parser("route-file")
    p.add_argument("--root")
    p.add_argument("--file", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--kind", required=True, choices=TASK_SUBFOLDERS)
    p.add_argument("--copy", action="store_true")
    p.set_defaults(func=route_file)

    p = sub.add_parser("audit")
    p.add_argument("--root")
    p.set_defaults(func=audit)

    p = sub.add_parser("migrate")
    p.add_argument("--root")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    p.set_defaults(func=migrate)

    p = sub.add_parser("skill-audit")
    p.add_argument("--root")
    p.set_defaults(func=skill_audit)

    p = sub.add_parser("skill-register")
    p.add_argument("--root")
    p.set_defaults(func=skill_register)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
