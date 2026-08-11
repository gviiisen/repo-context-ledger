#!/usr/bin/env python3
"""Deterministic runtime for the repo-context-ledger Agent Skill."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


VERSION = 2
TOOL_VERSION = "0.2.0"
BLOCK_START = "<!-- repo-context-ledger:start -->"
BLOCK_END = "<!-- repo-context-ledger:end -->"
RULE_START = "<!-- repo-context-ledger:rules:start -->"
RULE_END = "<!-- repo-context-ledger:rules:end -->"
CHANGES_START = "<!-- repo-context-ledger:changes:start -->"
CHANGES_END = "<!-- repo-context-ledger:changes:end -->"
PACK_FILES_START = "<!-- repo-context-ledger:pack-files:start -->"
PACK_FILES_END = "<!-- repo-context-ledger:pack-files:end -->"
PACK_SPECS_START = "<!-- repo-context-ledger:pack-specs:start -->"
PACK_SPECS_END = "<!-- repo-context-ledger:pack-specs:end -->"
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".context-ledger",
    "node_modules", "vendor", "dist", "build", "target", "bin", "obj",
    ".venv", "venv", "__pycache__", ".next", ".cache",
}
MODULE_MANIFESTS = {
    "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml",
    "build.gradle", "build.gradle.kts", "composer.json", "Gemfile",
}
REQUIRED_HANDOFF_HEADINGS = (
    "## Intent", "## Changed behavior", "## Code paths",
    "## Boundaries and risks", "## Verification", "## Documentation updates",
)


class LedgerError(Exception):
    """Expected user-facing configuration or workflow error."""


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def resolve_repo(raw: str) -> Path:
    repo = Path(raw).expanduser().resolve()
    if not repo.is_dir():
        raise LedgerError(f"Repository directory does not exist: {repo}")
    return repo


def write_if_missing(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(content.rstrip() + "\n")
        return True
    except FileExistsError:
        return False


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


@contextmanager
def repo_lock(repo: Path):
    lock_dir = safe_repo_path(repo, ".context-ledger", "ledger runtime directory")
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / ".write.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise LedgerError(
            "Another Repo Context Ledger write is active. Wait for it to finish; "
            "remove .context-ledger/.write.lock only if the prior process crashed."
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()} started={now().isoformat(timespec='seconds')}\n")
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def replace_block(path: Path, start: str, end: str, body: str, heading: str | None = None) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = (heading or f"# {path.stem}") + "\n"
    block = f"{start}\n{body.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        updated = pattern.sub(block, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, updated.rstrip() + "\n")


def first_heading(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except (OSError, UnicodeError):
        pass
    return path.stem.replace("-", " ").title()


def field_value(text: str, field: str) -> str:
    match = re.search(rf"(?mi)^{re.escape(field)}:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def set_field(text: str, field: str, value: str, after: str | None = None) -> str:
    line = f"{field}: {value}".rstrip()
    if re.search(rf"(?mi)^{re.escape(field)}:", text):
        return re.sub(rf"(?mi)^{re.escape(field)}:.*$", line, text, count=1)
    if after and re.search(rf"(?mi)^{re.escape(after)}:.*$", text):
        return re.sub(
            rf"(?mi)^({re.escape(after)}:.*)$",
            lambda match: match.group(1) + "\n" + line,
            text,
            count=1,
        )
    heading = re.search(r"(?m)^## ", text)
    position = heading.start() if heading else len(text)
    return text[:position].rstrip() + "\n" + line + "\n\n" + text[position:].lstrip()


def slugify(value: str) -> str:
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return ascii_slug[:48] or "change"


def git_revision(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "none"
    return result.stdout.strip() if result.returncode == 0 else "none"


def git_dirty_paths(repo: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    paths = []
    for line in result.stdout.splitlines():
        raw = line[3:].strip()
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        if raw.replace("\\", "/") == ".context-ledger/.write.lock":
            continue
        if raw:
            paths.append(raw.replace("\\", "/"))
    return sorted(dict.fromkeys(paths))


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def context_state_path(repo: Path) -> Path:
    return safe_repo_path(repo, ".context-ledger/context-state.json", "context state")


def default_context_state() -> dict:
    return {
        "schema_version": VERSION,
        "active_feature": None,
        "paused_handoffs": [],
        "recent_features": [],
    }


def load_context_state(repo: Path) -> dict:
    path = context_state_path(repo)
    if not path.exists():
        return default_context_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise LedgerError(f"Invalid context state: {exc}") from exc
    if not isinstance(raw, dict):
        raise LedgerError("Context state must be a JSON object.")
    paused = raw.get("paused_handoffs", [])
    recent = raw.get("recent_features", [])
    active = raw.get("active_feature")
    if not isinstance(paused, list) or not all(isinstance(item, str) for item in paused):
        raise LedgerError("context-state paused_handoffs must be a list of paths.")
    if not isinstance(recent, list) or not all(isinstance(item, str) for item in recent):
        raise LedgerError("context-state recent_features must be a list of feature slugs.")
    if active is not None and not isinstance(active, str):
        raise LedgerError("context-state active_feature must be a string or null.")
    return {
        "schema_version": VERSION,
        "active_feature": active,
        "paused_handoffs": list(dict.fromkeys(paused)),
        "recent_features": list(dict.fromkeys(recent))[:10],
    }


def save_context_state(repo: Path, state: dict) -> None:
    normalized = default_context_state()
    normalized.update(state)
    normalized["schema_version"] = VERSION
    atomic_write(context_state_path(repo), json.dumps(normalized, indent=2, ensure_ascii=False) + "\n")


def remember_feature(state: dict, feature: str) -> None:
    state["active_feature"] = feature
    state["recent_features"] = [feature] + [
        item for item in state.get("recent_features", []) if item != feature
    ][:9]


def feature_slug(value: str) -> str:
    slug = slugify(value)
    if slug == "change" and value.strip().casefold() != "change":
        digest = hashlib.sha1(value.strip().encode("utf-8")).hexdigest()[:10]
        return f"feature-{digest}"
    return slug


def template_source(name: str, repo: Path | None = None) -> Path:
    skill_asset = Path(__file__).resolve().parent.parent / "assets" / name
    if skill_asset.exists():
        return skill_asset
    if repo:
        local = repo / ".context-ledger" / "templates" / name
        if local.exists():
            return local
    raise LedgerError(f"Missing template: {name}")


def render_template(path: Path, values: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def config_path(repo: Path) -> Path:
    return safe_repo_path(repo, ".context-ledger", "ledger runtime directory") / "config.json"


def safe_repo_path(repo: Path, raw: str, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise LedgerError(f"{label} must be a non-empty relative path.")
    supplied = Path(raw)
    if supplied.is_absolute():
        raise LedgerError(f"{label} points outside the repository: {raw}")
    target = (repo / supplied).resolve()
    try:
        relative = target.relative_to(repo.resolve())
    except ValueError as exc:
        raise LedgerError(f"{label} points outside the repository: {raw}") from exc
    if not relative.parts:
        raise LedgerError(f"{label} cannot be the repository root.")
    return target


def validate_config(repo: Path, config: dict) -> dict:
    if not isinstance(config, dict):
        raise LedgerError("Ledger configuration must be a JSON object.")
    docs = config.get("docs")
    if not isinstance(docs, dict) or set(docs) != {"ai", "specs", "changes"}:
        raise LedgerError("config.docs must contain exactly ai, specs, and changes paths.")
    normalized_docs: dict[str, str] = {}
    resolved_docs: list[Path] = []
    runtime_root = safe_repo_path(repo, ".context-ledger", "ledger runtime directory")
    for key in ("ai", "specs", "changes"):
        target = safe_repo_path(repo, docs[key], f"config.docs.{key}")
        if target == runtime_root or runtime_root in target.parents:
            raise LedgerError(f"config.docs.{key} cannot be inside .context-ledger.")
        normalized_docs[key] = rel_posix(target, repo)
        resolved_docs.append(target)
    if len(set(resolved_docs)) != len(resolved_docs):
        raise LedgerError("AI, specs, and changes documentation paths must be distinct.")
    for index, left in enumerate(resolved_docs):
        for right in resolved_docs[index + 1:]:
            if left in right.parents or right in left.parents:
                raise LedgerError("AI, specs, and changes documentation paths cannot contain one another.")

    raw_modules = config.get("modules", [])
    if not isinstance(raw_modules, list):
        raise LedgerError("config.modules must be a list.")
    normalized_modules = []
    seen_modules = set()
    for index, module in enumerate(raw_modules):
        if not isinstance(module, dict):
            raise LedgerError(f"config.modules[{index}] must be an object.")
        module_root = safe_repo_path(repo, module.get("path"), f"config.modules[{index}].path")
        readme = safe_repo_path(repo, module.get("readme"), f"config.modules[{index}].readme")
        if module_root == runtime_root or runtime_root in module_root.parents:
            raise LedgerError(f"config.modules[{index}].path cannot be inside .context-ledger.")
        try:
            readme.relative_to(module_root)
        except ValueError as exc:
            raise LedgerError(
                f"config.modules[{index}].readme must be inside its module and not outside the repository."
            ) from exc
        module_name = rel_posix(module_root, repo)
        if module_name in seen_modules:
            raise LedgerError(f"Duplicate module path: {module_name}")
        seen_modules.add(module_name)
        source = module.get("source", "auto")
        if source not in {"auto", "manual"}:
            raise LedgerError(f"config.modules[{index}].source must be auto or manual.")
        normalized_modules.append({
            "path": module_name,
            "readme": rel_posix(readme, repo),
            "source": source,
        })
    return {
        "schema_version": config.get("schema_version", VERSION),
        "docs": normalized_docs,
        "modules": normalized_modules,
        "readme_managed_blocks": bool(config.get("readme_managed_blocks", True)),
    }


def load_config(repo: Path) -> dict:
    path = config_path(repo)
    if not path.exists():
        raise LedgerError("Repo Context Ledger is not initialized. Initialize it first.")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise LedgerError(f"Invalid ledger configuration: {exc}") from exc
    return validate_config(repo, raw)


def save_config(repo: Path, config: dict) -> None:
    config = validate_config(repo, config)
    path = config_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, json.dumps(config, indent=2, ensure_ascii=False) + "\n")


def discover_modules(repo: Path) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for current, dirs, files in os.walk(repo):
        current_path = Path(current)
        try:
            relative = current_path.relative_to(repo)
        except ValueError:
            continue
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        if len(relative.parts) >= 3:
            dirs[:] = []
        if not relative.parts:
            continue
        has_manifest = bool(MODULE_MANIFESTS.intersection(files)) or any(
            name.endswith((".csproj", ".fsproj", ".vbproj")) for name in files
        )
        if has_manifest:
            key = relative.as_posix()
            found[key] = {"path": key, "readme": f"{key}/README.md", "source": "auto"}
            dirs[:] = []
    return [found[key] for key in sorted(found)]


def managed_rules(config: dict) -> str:
    changes = config["docs"]["changes"]
    specs = config["docs"]["specs"]
    return f"""## Repository context ledger

For every feature, bug fix, refactor, interface change, or other behavior-changing code task:

1. Before editing code, inspect `{changes}/.active-handoff`. If empty, run `python .context-ledger/ledger.py start --title \"<task>\" --feature \"<feature>\"` yourself.
2. Prefer `python .context-ledger/ledger.py focus --feature \"<feature>\"` and read its Context Pack before broad code exploration. If no pack exists, create it with `pack`, fill it, then focus it. Fall back to `context --query` for discovery.
3. When the user pauses or switches work, run `pause` with an accurate summary and next step before starting another handoff. When the user resumes, run `resume` and revalidate any stale state.
4. Keep the active handoff current while working. Refresh affected Context Packs with `pack --file ...` when tracked code changes.
5. Update `{specs}/` when current behavior, contracts, boundaries, or code navigation changes.
6. After code and tests are complete, fill every handoff section and run `python .context-ledger/ledger.py finish --spec <affected-spec>`. Use `--no-spec --reason \"...\"` only when no stable behavior exists to document.
7. Run `python .context-ledger/ledger.py check --strict` and resolve failures before reporting completion.

Do not ask the user to run bookkeeping commands. Do not create a handoff for read-only analysis or formatting-only work. Preserve prose outside `repo-context-ledger` managed markers."""


def init_repo(repo: Path) -> int:
    previous = load_config(repo) if config_path(repo).exists() else {}
    runtime_dir = safe_repo_path(repo, ".context-ledger", "ledger runtime directory")
    template_dir = runtime_dir / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    runtime_target = runtime_dir / "ledger.py"
    if Path(__file__).resolve() != runtime_target.resolve():
        shutil.copy2(Path(__file__).resolve(), runtime_target)
    for name in (
        "handoff-template.md", "spec-template.md", "project-context-template.md",
        "context-pack-template.md",
    ):
        source = template_source(name, repo)
        target = template_dir / name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)

    known_modules = {
        item["path"]: item
        for item in previous.get("modules", [])
        if item.get("source") == "manual"
    }
    for item in discover_modules(repo):
        known_modules[item["path"]] = item
    modules = [known_modules[key] for key in sorted(known_modules)]
    config = {
        "schema_version": VERSION,
        "docs": previous.get("docs") or {"ai": "docs/ai", "specs": "docs/specs", "changes": "docs/changes"},
        "modules": modules,
        "readme_managed_blocks": True,
    }
    save_config(repo, config)

    docs = config["docs"]
    ai_root = safe_repo_path(repo, docs["ai"], "config.docs.ai")
    specs_root = safe_repo_path(repo, docs["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, docs["changes"], "config.docs.changes")
    ai_root.mkdir(parents=True, exist_ok=True)
    (ai_root / "context-packs").mkdir(parents=True, exist_ok=True)
    specs_root.mkdir(parents=True, exist_ok=True)
    changes_root.mkdir(parents=True, exist_ok=True)
    project_context = ai_root / "project-context.md"
    write_if_missing(
        project_context,
        render_template(template_dir / "project-context-template.md", {
            "SPECS_INDEX": os.path.relpath(specs_root / "README.md", ai_root).replace(os.sep, "/"),
            "CHANGES_INDEX": os.path.relpath(changes_root / "README.md", ai_root).replace(os.sep, "/"),
        }),
    )
    write_if_missing(changes_root / ".active-handoff", "")
    if not context_state_path(repo).exists():
        save_context_state(repo, default_context_state())
    else:
        save_context_state(repo, load_context_state(repo))
    write_if_missing(specs_root / "README.md", "# Stable feature context\n")
    write_if_missing(changes_root / "README.md", "# Change history\n")

    replace_block(repo / "AGENTS.md", RULE_START, RULE_END, managed_rules(config), "# Agent instructions")
    claude_body = "@AGENTS.md\n\nFollow the repository context ledger workflow without asking the user to run its lifecycle commands."
    replace_block(repo / "CLAUDE.md", RULE_START, RULE_END, claude_body, "# Claude Code instructions")
    cursor_rule = repo / ".cursor/rules/repo-context-ledger.mdc"
    cursor_content = """---
description: Maintain repository feature context and change history for behavior-changing code work.
alwaysApply: true
---

Read and follow the repository root `AGENTS.md`, especially the Repository context ledger section. Run ledger lifecycle commands autonomously; never delegate them to the user.
"""
    cursor_rule.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(cursor_rule, cursor_content)

    sync_repo(repo)
    print(f"Initialized Repo Context Ledger in {repo}")
    print(f"Detected modules: {len(modules)}")
    return 0


def active_pointer(repo: Path, config: dict) -> Path:
    return safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes") / ".active-handoff"


def active_handoff(repo: Path, config: dict) -> Path | None:
    pointer = active_pointer(repo, config)
    if not pointer.exists():
        return None
    raw = pointer.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    target = (repo / raw).resolve()
    try:
        target.relative_to(repo.resolve())
    except ValueError as exc:
        raise LedgerError("Active handoff points outside the repository.") from exc
    return target


def start_change(repo: Path, title: str, feature: str = "") -> int:
    title = title.strip()
    if not title or len(title) > 160 or "\n" in title or "\r" in title:
        print("Task title must be one line containing 1 to 160 characters.", file=sys.stderr)
        return 2
    config = load_config(repo)
    feature = feature_slug(feature or title)
    current = active_handoff(repo, config)
    if current and current.exists():
        if first_heading(current).casefold() == title.casefold():
            print(rel_posix(current, repo))
            return 0
        print(f"Another handoff is active: {rel_posix(current, repo)}", file=sys.stderr)
        return 2

    stamp = now()
    folder = safe_repo_path(
        repo,
        f"{config['docs']['changes']}/{stamp.strftime('%Y')}/{stamp.strftime('%m')}",
        "handoff month directory",
    )
    folder.mkdir(parents=True, exist_ok=True)
    content = render_template(
        template_source("handoff-template.md", repo),
        {
            "TITLE": title,
            "FEATURE": feature,
            "STARTED": stamp.isoformat(timespec="seconds"),
            "BASE_COMMIT": git_revision(repo),
        },
    )
    stem = f"{stamp.strftime('%Y%m%d-%H%M%S')}-{slugify(title)}"
    path = folder / f"{stem}.md"
    counter = 1
    while True:
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content.rstrip() + "\n")
            break
        except FileExistsError:
            counter += 1
            path = folder / f"{stem}-{counter}.md"
    atomic_write(active_pointer(repo, config), rel_posix(path, repo) + "\n")
    state = load_context_state(repo)
    remember_feature(state, feature)
    save_context_state(repo, state)
    sync_repo(repo)
    print(rel_posix(path, repo))
    return 0


def query_tokens(query: str) -> list[str]:
    chunks = re.findall(r"[a-z0-9_.:/-]+|[\u3400-\u9fff]+", query.casefold())
    tokens: list[str] = []
    for chunk in chunks:
        tokens.append(chunk)
        if re.fullmatch(r"[\u3400-\u9fff]+", chunk) and len(chunk) > 2:
            tokens.extend(chunk[i:i + 2] for i in range(len(chunk) - 1))
    return list(dict.fromkeys(token for token in tokens if token))


def context_search(repo: Path, query: str, limit: int) -> int:
    config = load_config(repo)
    tokens = query_tokens(query)
    candidates: list[tuple[int, Path]] = []
    for key in ("ai", "specs"):
        base = repo / config["docs"][key]
        for path in base.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8").casefold()
            except (OSError, UnicodeError):
                continue
            title = first_heading(path).casefold()
            score = sum((text.count(token) + 4 * title.count(token)) * max(1, len(token)) for token in tokens)
            if score or not tokens:
                candidates.append((score, path))
    candidates.sort(key=lambda item: (-item[0], rel_posix(item[1], repo)))
    if not candidates:
        print("No matching context documents. Inspect docs/ai and docs/specs indexes.")
        return 1
    for score, path in candidates[:limit]:
        print(f"{rel_posix(path, repo)}\t{first_heading(path)}\tscore={score}")
    return 0


def context_pack_path(repo: Path, config: dict, feature: str) -> Path:
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    return ai_root / "context-packs" / f"{feature_slug(feature)}.md"


def pack_file_entries(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(re.escape(PACK_FILES_START) + r"(.*?)" + re.escape(PACK_FILES_END), re.DOTALL)
    match = pattern.search(text)
    if not match:
        return []
    return re.findall(r"(?m)^- `([^`]+)` — `sha256:([0-9a-f]{64})`$", match.group(1))


def pack_spec_paths(text: str) -> list[str]:
    pattern = re.compile(re.escape(PACK_SPECS_START) + r"(.*?)" + re.escape(PACK_SPECS_END), re.DOTALL)
    match = pattern.search(text)
    if not match:
        return []
    return re.findall(r"(?m)^- \[[^\]]+\]\(([^)]+)\)$", match.group(1))


def normalize_tracked_file(repo: Path, raw: str) -> Path:
    target = Path(raw).resolve() if Path(raw).is_absolute() else (repo / raw).resolve()
    try:
        target.relative_to(repo.resolve())
    except ValueError as exc:
        raise LedgerError(f"Tracked file points outside the repository: {raw}") from exc
    if not target.is_file():
        raise LedgerError(f"Tracked file does not exist: {raw}")
    return target


def refresh_context_pack(
    repo: Path,
    feature: str,
    title: str,
    raw_files: list[str],
    raw_specs: list[str],
) -> int:
    config = load_config(repo)
    feature = feature_slug(feature)
    path = context_pack_path(repo, config, feature)
    existing = path.exists()
    previous = path.read_text(encoding="utf-8") if existing else ""
    if not raw_files and existing:
        raw_files = [item[0] for item in pack_file_entries(previous)]
    if not raw_specs and existing:
        raw_specs = [
            os.path.normpath(os.path.join(path.parent, item))
            for item in pack_spec_paths(previous)
        ]
    if not raw_files:
        print("A context pack must track at least one repository file.", file=sys.stderr)
        return 2
    tracked = list(dict.fromkeys(normalize_tracked_file(repo, raw) for raw in raw_files))
    specs = list(dict.fromkeys(normalize_spec(repo, config, raw) for raw in raw_specs))
    if existing:
        text = previous
    else:
        display_title = title.strip() or feature.replace("-", " ").title()
        text = render_template(
            template_source("context-pack-template.md", repo),
            {
                "TITLE": display_title,
                "FEATURE": feature,
                "SOURCE_COMMIT": git_revision(repo),
                "REFRESHED": now().isoformat(timespec="seconds"),
            },
        )
    text = set_field(text, "Status", "current")
    text = set_field(text, "Feature", feature, after="Status")
    text = set_field(text, "Source commit", git_revision(repo), after="Feature")
    text = set_field(text, "Last refreshed", now().isoformat(timespec="seconds"), after="Source commit")
    file_lines = [
        f"- `{rel_posix(item, repo)}` — `sha256:{file_digest(item)}`"
        for item in tracked
    ]
    replace_files = (
        "## Tracked file fingerprints\n\n" + "\n".join(file_lines)
    )
    temp_path = path
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(temp_path, text.rstrip() + "\n")
    replace_block(temp_path, PACK_FILES_START, PACK_FILES_END, replace_files)
    spec_lines = [
        f"- [{first_heading(item)}]({os.path.relpath(item, path.parent).replace(os.sep, '/')})"
        for item in specs
    ] or ["- No linked stable specs yet."]
    replace_block(
        temp_path,
        PACK_SPECS_START,
        PACK_SPECS_END,
        "## Stable context\n\n" + "\n".join(spec_lines),
    )
    print(rel_posix(path, repo))
    if not existing:
        print("Fill every TODO in the new context pack before focusing it.")
    return 0


PACK_REQUIRED_HEADINGS = (
    "## Purpose", "## Load order", "## Entry points and code map",
    "## Contracts and boundaries", "## Verification",
)


def context_pack_errors(repo: Path, path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if field_value(text, "Status").casefold() != "current":
        errors.append("Context pack status must be current.")
    if not field_value(text, "Feature"):
        errors.append("Context pack is missing Feature metadata.")
    if not field_value(text, "Source commit"):
        errors.append("Context pack is missing Source commit metadata.")
    if not field_value(text, "Last refreshed"):
        errors.append("Context pack is missing Last refreshed metadata.")
    if re.search(r"(?mi)^\s*TODO:\s*", text):
        errors.append("Context pack still contains TODO placeholders.")
    for index, heading in enumerate(PACK_REQUIRED_HEADINGS):
        if heading not in text:
            errors.append(f"Missing context pack section: {heading}")
            continue
        start = text.index(heading) + len(heading)
        later = [text.find(other, start) for other in PACK_REQUIRED_HEADINGS[index + 1:]]
        managed = [
            text.find(PACK_SPECS_START, start), text.find(PACK_FILES_START, start),
        ]
        ends = [position for position in later + managed if position >= 0]
        end = min(ends) if ends else len(text)
        body = re.sub(r"[`*_#>\-]", "", text[start:end]).strip()
        if len(body) < 10:
            errors.append(f"Context pack section has no substantive content: {heading}")
    entries = pack_file_entries(text)
    if not entries:
        errors.append("Context pack must contain at least one tracked file fingerprint.")
    for raw, expected in entries:
        try:
            target = normalize_tracked_file(repo, raw)
        except LedgerError as exc:
            errors.append(str(exc))
            continue
        if file_digest(target) != expected:
            errors.append(f"Context pack is stale; tracked file changed: {raw}")
    return errors


def focus_context(repo: Path, feature: str) -> int:
    config = load_config(repo)
    feature = feature_slug(feature)
    pack = context_pack_path(repo, config, feature)
    if not pack.is_file():
        print(
            f"No context pack for {feature}. Create one with the pack command before focusing it.",
            file=sys.stderr,
        )
        return 2
    current = active_handoff(repo, config)
    if current and current.exists():
        active_feature = feature_slug(field_value(current.read_text(encoding="utf-8"), "Feature") or first_heading(current))
        if active_feature != feature:
            print(
                f"Active handoff belongs to {active_feature}; pause it before focusing {feature}.",
                file=sys.stderr,
            )
            return 2
    errors = context_pack_errors(repo, pack)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    state = load_context_state(repo)
    remember_feature(state, feature)
    save_context_state(repo, state)
    text = pack.read_text(encoding="utf-8")
    print(f"Context pack: {rel_posix(pack, repo)}")
    for raw in pack_spec_paths(text):
        target = (pack.parent / raw).resolve()
        print(f"Stable spec: {rel_posix(target, repo)}")
    for raw, _ in pack_file_entries(text):
        print(f"Tracked file: {raw}")
    return 0


def pause_change(repo: Path, summary: str, next_step: str) -> int:
    if len(summary.strip()) < 10 or len(next_step.strip()) < 5:
        print("Pause requires a substantive --summary and --next step.", file=sys.stderr)
        return 2
    config = load_config(repo)
    handoff = active_handoff(repo, config)
    if not handoff or not handoff.is_file():
        print("No active handoff to pause.", file=sys.stderr)
        return 2
    text = handoff.read_text(encoding="utf-8")
    if field_value(text, "Status").casefold() != "active":
        print("Only an active handoff can be paused.", file=sys.stderr)
        return 2
    feature = feature_slug(field_value(text, "Feature") or first_heading(handoff))
    text = set_field(text, "Feature", feature, after="Status")
    text = set_field(text, "Status", "paused")
    text = set_field(text, "Paused", now().isoformat(timespec="seconds"), after="Completed")
    text = set_field(text, "Base commit", field_value(text, "Base commit") or git_revision(repo), after="Resumed")
    text = set_field(text, "Resume summary", summary.strip(), after="Dirty paths")
    text = set_field(text, "Next step", next_step.strip(), after="Resume summary")
    dirty = git_dirty_paths(repo)
    text = set_field(text, "Dirty paths", ", ".join(dirty) if dirty else "none", after="Base commit")
    atomic_write(handoff, text.rstrip() + "\n")
    atomic_write(active_pointer(repo, config), "")
    state = load_context_state(repo)
    handoff_rel = rel_posix(handoff, repo)
    state["paused_handoffs"] = [handoff_rel] + [
        item for item in state.get("paused_handoffs", []) if item != handoff_rel
    ]
    state["active_feature"] = None
    save_context_state(repo, state)
    sync_repo(repo)
    print(f"Paused {handoff_rel}")
    return 0


def resolve_paused_handoff(repo: Path, config: dict, raw: str, state: dict) -> Path:
    candidate = raw.strip() if raw else (state.get("paused_handoffs") or [""])[0]
    if not candidate:
        raise LedgerError("No paused handoff is available to resume.")
    target = safe_repo_path(repo, candidate, "paused handoff")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    try:
        target.relative_to(changes_root)
    except ValueError as exc:
        raise LedgerError("Paused handoff must be inside the configured change history.") from exc
    if not target.is_file():
        raise LedgerError(f"Paused handoff does not exist: {candidate}")
    return target


def resume_change(repo: Path, raw_handoff: str) -> int:
    config = load_config(repo)
    current = active_handoff(repo, config)
    if current:
        print(f"Another handoff is active: {rel_posix(current, repo)}", file=sys.stderr)
        return 2
    state = load_context_state(repo)
    handoff = resolve_paused_handoff(repo, config, raw_handoff, state)
    text = handoff.read_text(encoding="utf-8")
    if field_value(text, "Status").casefold() != "paused":
        print("Only a paused handoff can be resumed.", file=sys.stderr)
        return 2
    feature = feature_slug(field_value(text, "Feature") or first_heading(handoff))
    base_commit = field_value(text, "Base commit")
    current_commit = git_revision(repo)
    text = set_field(text, "Feature", feature, after="Status")
    text = set_field(text, "Status", "active")
    text = set_field(text, "Resumed", now().isoformat(timespec="seconds"), after="Paused")
    atomic_write(handoff, text.rstrip() + "\n")
    handoff_rel = rel_posix(handoff, repo)
    atomic_write(active_pointer(repo, config), handoff_rel + "\n")
    state["paused_handoffs"] = [
        item for item in state.get("paused_handoffs", []) if item != handoff_rel
    ]
    remember_feature(state, feature)
    save_context_state(repo, state)
    sync_repo(repo)
    print(f"Resumed {handoff_rel}")
    if base_commit and base_commit != "none" and current_commit != base_commit:
        print(f"WARNING: repository moved from {base_commit} to {current_commit}; revalidate the resume state.")
    pack = context_pack_path(repo, config, feature)
    if pack.exists():
        errors = context_pack_errors(repo, pack)
        if errors:
            print("WARNING: context pack requires refresh:")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"Context pack: {rel_posix(pack, repo)}")
    return 0


def markdown_items(paths: list[Path], base: Path) -> list[str]:
    items = []
    for path in paths:
        link = os.path.relpath(path, base).replace(os.sep, "/")
        text = path.read_text(encoding="utf-8")
        status = field_value(text, "Status")
        suffix = f" — {status}" if status else ""
        items.append(f"- [{first_heading(path)}]({link}){suffix}")
    return items


def all_specs(repo: Path, config: dict) -> list[Path]:
    base = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    return sorted((p for p in base.rglob("*.md") if p.name.casefold() != "readme.md"), key=lambda p: p.as_posix())


def all_changes(repo: Path, config: dict) -> list[Path]:
    base = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    paths = [p for p in base.rglob("*.md") if p.name.casefold() != "readme.md"]
    return sorted(paths, key=lambda p: p.as_posix(), reverse=True)


def readme_body(repo: Path, config: dict, readme: Path, module: str | None) -> str:
    readme_dir = readme.parent
    specs = all_specs(repo, config)
    changes = all_changes(repo, config)
    if module:
        needle = module.casefold()
        relevant_specs = [p for p in specs if needle in p.read_text(encoding="utf-8").casefold()]
        relevant_spec_names = {rel_posix(path, repo).casefold() for path in relevant_specs}
        relevant_changes = []
        for path in changes:
            change_text = path.read_text(encoding="utf-8").casefold()
            if needle in change_text or any(spec_name in change_text for spec_name in relevant_spec_names):
                relevant_changes.append(path)
    else:
        relevant_specs, relevant_changes = specs, changes
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    packs_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai") / "context-packs"
    spec_index = os.path.relpath(specs_root / "README.md", readme_dir).replace(os.sep, "/")
    change_index = os.path.relpath(changes_root / "README.md", readme_dir).replace(os.sep, "/")
    packs_link = os.path.relpath(packs_root, readme_dir).replace(os.sep, "/")
    lines = [
        "## Repository context",
        "",
        f"- [Stable feature context]({spec_index})",
        f"- [Change history]({change_index})",
        f"- [Feature Context Packs]({packs_link})",
    ]
    if relevant_specs:
        lines.append("- Relevant specs: " + ", ".join(
            f"[{first_heading(path)}]({os.path.relpath(path, readme_dir).replace(os.sep, '/')})"
            for path in relevant_specs[:5]
        ))
    if relevant_changes:
        latest = relevant_changes[0]
        latest_link = os.path.relpath(latest, readme_dir).replace(os.sep, "/")
        lines.append(f"- Latest recorded change: [{first_heading(latest)}]({latest_link})")
    return "\n".join(lines)


def sync_repo(repo: Path) -> int:
    config = load_config(repo)
    specs = all_specs(repo, config)
    changes = all_changes(repo, config)
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    spec_index = specs_root / "README.md"
    change_index = changes_root / "README.md"
    spec_lines = markdown_items(specs, spec_index.parent) or ["- No stable feature specs yet."]
    replace_block(spec_index, BLOCK_START, BLOCK_END, "## Index\n\n" + "\n".join(spec_lines), "# Stable feature context")

    months: dict[tuple[str, Path], list[Path]] = {}
    for change in changes:
        relative_parent = change.parent.relative_to(changes_root)
        if relative_parent.parts:
            label = relative_parent.as_posix().replace("/", "-")
            month_dir = change.parent
        else:
            label = "legacy"
            month_dir = changes_root / "legacy"
        months.setdefault((label, month_dir), []).append(change)
    month_lines = []
    for label, month_dir in sorted(months, key=lambda item: item[0], reverse=True):
        month_index = month_dir / "README.md"
        entries = markdown_items(months[(label, month_dir)], month_dir)
        replace_block(
            month_index,
            BLOCK_START,
            BLOCK_END,
            f"## Changes in {label}\n\n" + "\n".join(entries),
            f"# Changes in {label}",
        )
        link = os.path.relpath(month_index, changes_root).replace(os.sep, "/")
        month_lines.append(f"- [{label}]({link}) — {len(entries)} changes")
    replace_block(
        change_index,
        BLOCK_START,
        BLOCK_END,
        "## Months\n\n" + "\n".join(month_lines or ["- No recorded changes yet."]),
        "# Change history",
    )

    root_readme = repo / "README.md"
    replace_block(root_readme, BLOCK_START, BLOCK_END, readme_body(repo, config, root_readme, None), f"# {repo.name}")
    for module in config.get("modules", []):
        module_root = safe_repo_path(repo, module["path"], "config.modules.path")
        if not module_root.is_dir():
            continue
        readme = safe_repo_path(repo, module["readme"], "config.modules.readme")
        replace_block(readme, BLOCK_START, BLOCK_END, readme_body(repo, config, readme, module["path"]), f"# {Path(module['path']).name}")
    return 0


def normalize_spec(repo: Path, config: dict, raw: str) -> Path:
    path = Path(raw)
    target = path.resolve() if path.is_absolute() else (repo / path).resolve()
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    try:
        target.relative_to(specs_root)
    except ValueError as exc:
        raise LedgerError(f"Spec must be under {rel_posix(specs_root, repo)}: {raw}") from exc
    if not target.is_file():
        raise LedgerError(f"Spec does not exist: {raw}")
    return target


def link_change_to_spec(spec: Path, handoff: Path) -> None:
    text = spec.read_text(encoding="utf-8")
    link = os.path.relpath(handoff, spec.parent).replace(os.sep, "/")
    item = f"- [{first_heading(handoff)}]({link})"
    pattern = re.compile(re.escape(CHANGES_START) + r".*?" + re.escape(CHANGES_END), re.DOTALL)
    existing: list[str] = []
    match = pattern.search(text)
    if match:
        existing = re.findall(r"(?m)^- \[[^\n]+$", match.group(0))
        existing = [line for line in existing if "No recorded changes yet" not in line]
    lines = list(dict.fromkeys([item] + existing))
    block = f"{CHANGES_START}\n## Related changes\n\n" + "\n".join(lines) + f"\n{CHANGES_END}"
    if match:
        updated = pattern.sub(block, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"
    reviewed = now().date().isoformat()
    if re.search(r"(?mi)^Last reviewed:", updated):
        updated = re.sub(r"(?mi)^Last reviewed:.*$", f"Last reviewed: {reviewed}", updated, count=1)
    atomic_write(spec, updated.rstrip() + "\n")


def handoff_validation_errors(text: str) -> list[str]:
    errors = []
    if field_value(text, "Status").casefold() != "active":
        errors.append("Handoff status must be active.")
    for field in ("Started", "Specs"):
        if not field_value(text, field):
            errors.append(f"Handoff metadata is missing: {field}.")
    if re.search(r"(?mi)^\s*TODO:\s*", text):
        errors.append("Active handoff still contains TODO placeholders.")
    positions = [text.find(heading) for heading in REQUIRED_HANDOFF_HEADINGS]
    present_positions = [position for position in positions if position >= 0]
    if present_positions != sorted(present_positions):
        errors.append("Handoff sections are out of order.")
    for index, heading in enumerate(REQUIRED_HANDOFF_HEADINGS):
        if heading not in text:
            errors.append(f"Missing handoff section: {heading}")
            continue
        start = text.index(heading) + len(heading)
        later = [text.find(other, start) for other in REQUIRED_HANDOFF_HEADINGS[index + 1:]]
        ends = [position for position in later if position >= 0]
        end = min(ends) if ends else len(text)
        body = re.sub(r"[`*_#>\-]", "", text[start:end]).strip()
        if len(body) < 10:
            errors.append(f"Handoff section has no substantive content: {heading}")
    return errors


def finish_change(
    repo: Path,
    raw_specs: list[str],
    no_spec: bool = False,
    reason: str = "",
) -> int:
    config = load_config(repo)
    handoff = active_handoff(repo, config)
    if not handoff or not handoff.is_file():
        print("No active handoff.", file=sys.stderr)
        return 2
    text = handoff.read_text(encoding="utf-8")
    errors = handoff_validation_errors(text)
    if raw_specs and no_spec:
        errors.append("Use either --spec or --no-spec, not both.")
    if not raw_specs and not no_spec:
        errors.append("At least one --spec is required; otherwise use --no-spec with --reason.")
    if no_spec and len(reason.strip()) < 20:
        errors.append("--no-spec requires a substantive --reason of at least 20 characters.")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    specs = [normalize_spec(repo, config, raw) for raw in raw_specs]
    for spec in specs:
        link_change_to_spec(spec, handoff)
    sync_repo(repo)
    preflight = check_repo(repo, strict=True)
    if preflight != 0:
        print("Finish preflight failed; the handoff remains active.", file=sys.stderr)
        return preflight
    completed = now().isoformat(timespec="seconds")
    text = re.sub(r"(?mi)^Status:\s*active\s*$", "Status: completed", text, count=1)
    text = re.sub(r"(?mi)^Completed:.*$", f"Completed: {completed}", text, count=1)
    spec_names = ", ".join(rel_posix(path, repo) for path in specs) if specs else "none"
    text = re.sub(r"(?mi)^Specs:.*$", f"Specs: {spec_names}", text, count=1)
    exception_line = f"Spec exception: {reason.strip()}" if no_spec else "Spec exception: none"
    if re.search(r"(?mi)^Spec exception:", text):
        text = re.sub(r"(?mi)^Spec exception:.*$", exception_line, text, count=1)
    else:
        text = re.sub(r"(?mi)^(Specs:.*)$", rf"\1\n{exception_line}", text, count=1)
    atomic_write(handoff, text.rstrip() + "\n")
    atomic_write(active_pointer(repo, config), "")
    sync_repo(repo)
    result = check_repo(repo, strict=True)
    if result == 0:
        print(f"Completed {rel_posix(handoff, repo)}")
    return result


def local_links(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text)


def check_repo(repo: Path, strict: bool) -> int:
    errors: list[str] = []
    try:
        config = load_config(repo)
    except LedgerError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    for required in (
        repo / "AGENTS.md", specs_root / "README.md", changes_root / "README.md",
        context_state_path(repo),
    ):
        if not required.exists():
            errors.append(f"Missing required file: {rel_posix(required, repo)}")
    if (repo / "AGENTS.md").exists() and RULE_START not in (repo / "AGENTS.md").read_text(encoding="utf-8"):
        errors.append("AGENTS.md is missing the managed ledger rules.")
    current = active_handoff(repo, config)
    if current and not current.exists():
        errors.append(f"Active handoff does not exist: {current}")
    if strict and current and current.exists():
        errors.extend(handoff_validation_errors(current.read_text(encoding="utf-8")))
    try:
        state = load_context_state(repo)
        paused_seen = set()
        for raw in state.get("paused_handoffs", []):
            if raw in paused_seen:
                errors.append(f"Duplicate paused handoff in context state: {raw}")
                continue
            paused_seen.add(raw)
            try:
                paused = safe_repo_path(repo, raw, "paused handoff")
            except LedgerError as exc:
                errors.append(str(exc))
                continue
            if not paused.is_file():
                errors.append(f"Paused handoff does not exist: {raw}")
            elif field_value(paused.read_text(encoding="utf-8"), "Status").casefold() != "paused":
                errors.append(f"Paused handoff has non-paused status: {raw}")
    except LedgerError as exc:
        errors.append(str(exc))

    if strict:
        packs_root = ai_root / "context-packs"
        if packs_root.exists():
            for pack in sorted(packs_root.glob("*.md")):
                for error in context_pack_errors(repo, pack):
                    errors.append(f"{rel_posix(pack, repo)}: {error}")

    markdown_files = []
    for docs_root in (ai_root, specs_root, changes_root):
        markdown_files.extend(docs_root.rglob("*.md"))
    if (repo / "README.md").exists():
        markdown_files.append(repo / "README.md")
    for module in config.get("modules", []):
        module_readme = repo / module["readme"]
        if module_readme.exists():
            markdown_files.append(module_readme)
    for path in dict.fromkeys(markdown_files):
        text = path.read_text(encoding="utf-8")
        if text.count(BLOCK_START) != text.count(BLOCK_END):
            errors.append(f"Unbalanced managed markers: {rel_posix(path, repo)}")
        if text.count(CHANGES_START) != text.count(CHANGES_END):
            errors.append(f"Unbalanced related-change markers: {rel_posix(path, repo)}")
        for raw_link in local_links(path):
            link = raw_link.split("#", 1)[0].strip()
            if not link or re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
                continue
            target = (path.parent / link).resolve()
            if not target.exists():
                errors.append(f"Broken link in {rel_posix(path, repo)}: {raw_link}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Repo Context Ledger check passed.")
    return 0


def show_status(repo: Path) -> int:
    config = load_config(repo)
    current = active_handoff(repo, config)
    state = load_context_state(repo)
    packs_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai") / "context-packs"
    print(f"Repository: {repo}")
    print(f"Active handoff: {rel_posix(current, repo) if current else 'none'}")
    print(f"Active feature: {state.get('active_feature') or 'none'}")
    print(f"Paused handoffs: {len(state.get('paused_handoffs', []))}")
    for raw in state.get("paused_handoffs", []):
        print(f"- {raw}")
    print(f"Context packs: {len(list(packs_root.glob('*.md'))) if packs_root.exists() else 0}")
    print(f"Stable specs: {len(all_specs(repo, config))}")
    print(f"Recorded changes: {len(all_changes(repo, config))}")
    print(f"Detected modules: {len(config.get('modules', []))}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain AI-friendly repository context documentation.")
    parser.add_argument("--version", action="version", version=f"repo-context-ledger {TOOL_VERSION}")
    parser.add_argument("--repo", default=".", help="Repository root (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize or refresh repository integration")
    start = sub.add_parser("start", help="Start a behavior-changing work handoff")
    start.add_argument("--title", required=True)
    start.add_argument("--feature", default="", help="Stable feature slug or name")
    context = sub.add_parser("context", help="Find likely stable background documents")
    context.add_argument("--query", required=True)
    context.add_argument("--limit", type=int, default=5)
    pack = sub.add_parser("pack", help="Create or refresh a feature Context Pack")
    pack.add_argument("--feature", required=True)
    pack.add_argument("--title", default="")
    pack.add_argument("--file", action="append", default=[])
    pack.add_argument("--spec", action="append", default=[])
    focus = sub.add_parser("focus", help="Load and validate a feature Context Pack")
    focus.add_argument("--feature", required=True)
    pause = sub.add_parser("pause", help="Pause the active handoff and preserve resume state")
    pause.add_argument("--summary", required=True)
    pause.add_argument("--next", required=True, dest="next_step")
    resume = sub.add_parser("resume", help="Resume the latest or selected paused handoff")
    resume.add_argument("--handoff", default="")
    finish = sub.add_parser("finish", help="Complete the active handoff and link specs")
    finish_group = finish.add_mutually_exclusive_group()
    finish_group.add_argument("--spec", action="append", default=[])
    finish_group.add_argument("--no-spec", action="store_true")
    finish.add_argument("--reason", default="", help="Required explanation when --no-spec is used")
    sub.add_parser("sync", help="Regenerate indexes and managed README blocks")
    check = sub.add_parser("check", help="Validate ledger structure and local links")
    check.add_argument("--strict", action="store_true")
    sub.add_parser("status", help="Show ledger state")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        repo = resolve_repo(args.repo)
        if args.command in {"init", "start", "pack", "focus", "pause", "resume", "finish", "sync"}:
            with repo_lock(repo):
                if args.command == "init":
                    return init_repo(repo)
                if args.command == "start":
                    return start_change(repo, args.title, args.feature)
                if args.command == "pack":
                    return refresh_context_pack(repo, args.feature, args.title, args.file, args.spec)
                if args.command == "focus":
                    return focus_context(repo, args.feature)
                if args.command == "pause":
                    return pause_change(repo, args.summary, args.next_step)
                if args.command == "resume":
                    return resume_change(repo, args.handoff)
                if args.command == "finish":
                    return finish_change(repo, args.spec, args.no_spec, args.reason)
                return sync_repo(repo)
        if args.command == "context":
            return context_search(repo, args.query, max(1, args.limit))
        if args.command == "check":
            return check_repo(repo, args.strict)
        if args.command == "status":
            return show_status(repo)
        return 2
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
