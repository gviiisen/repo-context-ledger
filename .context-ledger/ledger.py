#!/usr/bin/env python3
"""Deterministic runtime for the repo-context-ledger Agent Skill."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path


VERSION = 7
TOOL_VERSION = "0.5.4"
MANIFEST_VERSION = 1
QUALITY_PROFILE = "evidence-v1"
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
EVIDENCE_START = "<!-- repo-context-ledger:evidence:start -->"
EVIDENCE_END = "<!-- repo-context-ledger:evidence:end -->"
CHECKS_START = "<!-- repo-context-ledger:checks:start -->"
CHECKS_END = "<!-- repo-context-ledger:checks:end -->"
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".context-ledger",
    "node_modules", "vendor", "dist", "build", "target", "bin", "obj",
    ".venv", "venv", "__pycache__", ".next", ".cache",
}
MODULE_MANIFESTS = {
    "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml",
    "build.gradle", "build.gradle.kts", "composer.json", "Gemfile",
}
YEAR_PATTERN = re.compile(r"^\d{4}$")
MONTH_PATTERN = re.compile(r"^(0[1-9]|1[0-2])$")
LEGACY_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
REQUIRED_HANDOFF_HEADINGS = (
    "## Intent", "## Changed behavior", "## Code paths",
    "## Boundaries and risks", "## Verification", "## Documentation updates",
)
ADAPTER_NAMES = ("agents", "claude", "cursor", "copilot")
COVERAGE_GLOB_DEFAULTS = {
    "implementation_globs": ["**"],
    "test_globs": [
        "tests/**", "test/**", "**/tests/**", "**/test/**",
        "**/test_*.py", "**/*_test.*", "**/*.test.*", "**/*.spec.*",
    ],
    "ci_globs": [
        ".github/**", ".gitlab/**", ".gitlab-ci.yml", ".circleci/**",
        "azure-pipelines*.yml", "Jenkinsfile",
    ],
    "config_globs": [
        "pyproject.toml", "setup.cfg", "tox.ini", "package.json",
        "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock",
        "go.mod", "go.sum", "*.config.*", ".env*",
    ],
    "generated_globs": [
        "dist/**", "build/**", "target/**", "coverage/**", "htmlcov/**",
        "node_modules/**", "vendor/**", "**/__pycache__/**",
    ],
    "ignore_globs": [],
}
COVERAGE_GLOB_KEYS = tuple(COVERAGE_GLOB_DEFAULTS)


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


def managed_text(text: str, start: str, end: str) -> str:
    match = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)
    return match.group(1).strip() if match else ""


def replace_managed_text(text: str, start: str, end: str, body: str) -> str:
    block = f"{start}\n{body.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(lambda _: block, text, count=1)
    return text.rstrip() + "\n\n" + block + "\n"


def section_body(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^##\s|\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def is_evidence_quality(text: str) -> bool:
    return field_value(text, "Quality profile").casefold() == QUALITY_PROFILE


def concrete_code_spans(text: str) -> list[str]:
    spans = re.findall(r"`([^`\r\n]+)`", text)
    return [
        item.replace("\\", "/")
        for item in spans
        if "/" in item or "\\" in item or re.search(r"\.[A-Za-z0-9]{1,8}(?::|$)", item)
    ]


def slugify(value: str) -> str:
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return ascii_slug[:48] or "change"


def git_output(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def is_git_repo(repo: Path) -> bool:
    return git_output(repo, "rev-parse", "--is-inside-work-tree") == "true"


def git_revision(repo: Path, ref: str = "HEAD") -> str:
    return git_output(repo, "rev-parse", ref) or "none"


def git_branch(repo: Path) -> str:
    return git_output(repo, "branch", "--show-current") or "detached"


def git_actor(repo: Path) -> str:
    return (
        git_output(repo, "config", "user.name")
        or os.environ.get("GITHUB_ACTOR")
        or os.environ.get("USERNAME")
        or os.environ.get("USER")
        or "unknown"
    )


def detect_default_branch(repo: Path) -> str:
    remote = git_output(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if remote.startswith("origin/"):
        return remote.split("/", 1)[1]
    for candidate in ("main", "master"):
        if git_output(repo, "show-ref", "--verify", f"refs/heads/{candidate}"):
            return candidate
    branch = git_branch(repo)
    return branch if branch != "detached" else "main"


def configured_base_ref(repo: Path, config: dict) -> str:
    branch = config.get("team", {}).get("default_branch", "main")
    remote = f"origin/{branch}"
    return remote if git_revision(repo, remote) != "none" else branch


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


def legacy_context_state_path(repo: Path) -> Path:
    return safe_repo_path(repo, ".context-ledger/context-state.json", "legacy context state")


def context_state_path(repo: Path) -> Path:
    if is_git_repo(repo):
        branch = git_branch(repo)
        state_key = f"{slugify(branch)[:32]}-{hashlib.sha1(branch.encode('utf-8')).hexdigest()[:8]}"
        raw = git_output(
            repo,
            "rev-parse",
            "--git-path",
            f"repo-context-ledger/states/{state_key}/context-state.json",
        )
        if raw:
            path = Path(raw)
            return path.resolve() if path.is_absolute() else (repo / path).resolve()
    return legacy_context_state_path(repo)


def default_context_state() -> dict:
    return {
        "schema_version": VERSION,
        "task_sessions": {},
        "recent_features": [],
    }


def legacy_session_id(raw_handoff: str) -> str:
    return "legacy-" + hashlib.sha1(raw_handoff.encode("utf-8")).hexdigest()[:12]


def normalized_session_record(session_id: str, raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        raise LedgerError(f"context-state task session {session_id} must be an object.")
    draft = raw.get("draft") or raw.get("handoff")
    publish_path = raw.get("publish_path") or raw.get("handoff")
    feature = raw.get("feature", "")
    status = raw.get("status")
    updated = raw.get("updated_at", "")
    if not isinstance(draft, str) or not draft:
        raise LedgerError(f"context-state task session {session_id} requires a draft path.")
    if not isinstance(publish_path, str) or not publish_path:
        raise LedgerError(f"context-state task session {session_id} requires a publish path.")
    if not isinstance(feature, str):
        raise LedgerError(f"context-state task session {session_id} feature must be a string.")
    if status not in {"active", "paused"}:
        raise LedgerError(f"context-state task session {session_id} status must be active or paused.")
    if not isinstance(updated, str):
        raise LedgerError(f"context-state task session {session_id} updated_at must be a string.")
    return {
        "draft": draft,
        "publish_path": publish_path,
        "feature": feature_slug(feature) if feature else "",
        "status": status,
        "updated_at": updated,
    }


def normalize_context_state(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise LedgerError("Context state must be a JSON object.")
    recent = raw.get("recent_features", [])
    if not isinstance(recent, list) or not all(isinstance(item, str) for item in recent):
        raise LedgerError("context-state recent_features must be a list of feature slugs.")
    raw_sessions = raw.get("task_sessions", {})
    if not isinstance(raw_sessions, dict):
        raise LedgerError("context-state task_sessions must be an object.")
    sessions = {
        str(session_id): normalized_session_record(str(session_id), record)
        for session_id, record in raw_sessions.items()
    }
    if not sessions:
        active_handoff_value = raw.get("active_handoff")
        active_feature = raw.get("active_feature") or ""
        paused = raw.get("paused_handoffs", [])
        if active_handoff_value is not None and not isinstance(active_handoff_value, str):
            raise LedgerError("context-state active_handoff must be a path or null.")
        if not isinstance(paused, list) or not all(isinstance(item, str) for item in paused):
            raise LedgerError("context-state paused_handoffs must be a list of paths.")
        if active_handoff_value:
            sessions[legacy_session_id(active_handoff_value)] = {
                "draft": active_handoff_value,
                "publish_path": active_handoff_value,
                "feature": feature_slug(active_feature) if active_feature else "",
                "status": "active",
                "updated_at": "",
            }
        for handoff in paused:
            session_id = legacy_session_id(handoff)
            sessions.setdefault(session_id, {
                "draft": handoff,
                "publish_path": handoff,
                "feature": "",
                "status": "paused",
                "updated_at": "",
            })
    return {
        "schema_version": VERSION,
        "task_sessions": sessions,
        "recent_features": list(dict.fromkeys(recent))[:10],
    }


def load_context_state(repo: Path) -> dict:
    path = context_state_path(repo)
    if not path.exists():
        return default_context_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise LedgerError(f"Invalid context state: {exc}") from exc
    return normalize_context_state(raw)


def save_context_state(repo: Path, state: dict) -> None:
    normalized = normalize_context_state(state)
    atomic_write(context_state_path(repo), json.dumps(normalized, indent=2, ensure_ascii=False) + "\n")


def legacy_active_pointer(repo: Path, config: dict) -> Path:
    return safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes") / ".active-handoff"


def migrate_workspace_state(repo: Path, config: dict) -> bool:
    target = context_state_path(repo)
    state = load_context_state(repo)
    migrated = False
    remove_legacy_state = False
    legacy_state = legacy_context_state_path(repo)
    if target != legacy_state and legacy_state.exists():
        try:
            previous = normalize_context_state(json.loads(legacy_state.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError) as exc:
            raise LedgerError(f"Invalid legacy context state: {exc}") from exc
        state["task_sessions"] = {
            **previous.get("task_sessions", {}),
            **state.get("task_sessions", {}),
        }
        state["recent_features"] = list(dict.fromkeys(
            state.get("recent_features", []) + previous.get("recent_features", [])
        ))[:10]
        remove_legacy_state = True
        migrated = True
    pointer = legacy_active_pointer(repo, config)
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        if raw:
            session_id = legacy_session_id(raw)
            state.setdefault("task_sessions", {}).setdefault(session_id, {
                "draft": raw,
                "publish_path": raw,
                "feature": "",
                "status": "active",
                "updated_at": "",
            })
        migrated = True
    canonical_sessions: dict[str, dict] = {}
    for session_id, record in state.get("task_sessions", {}).items():
        canonical_id = session_id
        if session_id.startswith("legacy-"):
            try:
                handoff = resolve_session_draft(repo, config, session_id, record)
                if handoff.is_file():
                    stored_id = field_value(handoff.read_text(encoding="utf-8"), "Handoff ID")
                    if stored_id:
                        canonical_id = stored_id
            except LedgerError:
                pass
        if canonical_id in canonical_sessions and canonical_sessions[canonical_id]["draft"] != record["draft"]:
            canonical_id = session_id
        draft = resolve_session_draft(repo, config, session_id, record)
        publish_path = validate_handoff_path(
            repo, config, record["publish_path"], "task session publish path"
        )
        private_draft = task_session_draft_path(repo, canonical_id)
        if draft != private_draft:
            if not draft.is_file():
                raise LedgerError(f"Legacy task session draft does not exist: {draft}")
            content = draft.read_text(encoding="utf-8")
            if private_draft.exists() and private_draft.read_text(encoding="utf-8") != content:
                raise LedgerError(f"Private task draft already exists with different content: {private_draft}")
            atomic_write(private_draft, content)
            if draft == publish_path:
                draft.unlink()
            migrated = True
        canonical_sessions[canonical_id] = {
            **record,
            "draft": session_draft_ref(repo, private_draft),
            "publish_path": rel_posix(publish_path, repo),
        }
        migrated = migrated or canonical_id != session_id
    state["task_sessions"] = canonical_sessions
    save_context_state(repo, state)
    if remove_legacy_state:
        legacy_state.unlink()
    if pointer.exists():
        pointer.unlink()
    return migrated


def remember_feature(state: dict, feature: str) -> None:
    state["recent_features"] = [feature] + [
        item for item in state.get("recent_features", []) if item != feature
    ][:9]


def feature_slug(value: str) -> str:
    slug = slugify(value)
    if slug == "change" and value.strip().casefold() != "change":
        digest = hashlib.sha1(value.strip().encode("utf-8")).hexdigest()[:10]
        return f"feature-{digest}"
    return slug


def actor_slug(repo: Path) -> str:
    return slugify(git_actor(repo))[:24] or "unknown"


def unique_handoff_id(repo: Path, stamp: dt.datetime) -> str:
    return f"{stamp.strftime('%Y%m%d%H%M%S')}-{actor_slug(repo)}-{uuid.uuid4().hex[:10]}"


def record_language(config: dict, requested: str = "") -> str:
    language = requested.strip() or config.get("quality", {}).get("language", "auto")
    if language not in {"auto", "en", "zh-CN"}:
        raise LedgerError("Record language must be auto, en, or zh-CN.")
    return language


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


def normalize_coverage_globs(raw_coverage: object) -> dict[str, list[str]]:
    if raw_coverage is None:
        raw_coverage = {}
    if not isinstance(raw_coverage, dict):
        raise LedgerError("config.coverage must be an object.")
    unknown = set(raw_coverage).difference(COVERAGE_GLOB_KEYS)
    if unknown:
        raise LedgerError(f"Unknown coverage setting: {sorted(unknown)[0]}")
    normalized: dict[str, list[str]] = {}
    for key, defaults in COVERAGE_GLOB_DEFAULTS.items():
        values = raw_coverage.get(key, defaults)
        if not isinstance(values, list):
            raise LedgerError(f"config.coverage.{key} must be a list of repository-relative globs.")
        patterns: list[str] = []
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value.strip():
                raise LedgerError(f"config.coverage.{key}[{index}] must be a non-empty glob.")
            pattern = value.strip().replace("\\", "/")
            if pattern.startswith("/") or re.match(r"^[A-Za-z]:", pattern):
                raise LedgerError(f"config.coverage.{key}[{index}] must be repository-relative.")
            if ".." in pattern.split("/"):
                raise LedgerError(f"config.coverage.{key}[{index}] cannot escape the repository.")
            patterns.append(pattern)
        if key == "implementation_globs" and not patterns:
            raise LedgerError("config.coverage.implementation_globs must contain at least one glob.")
        normalized[key] = list(dict.fromkeys(patterns))
    return normalized


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
    raw_team = config.get("team", {})
    if not isinstance(raw_team, dict):
        raise LedgerError("config.team must be an object.")
    team_enabled = bool(raw_team.get("enabled", is_git_repo(repo)))
    default_branch = raw_team.get("default_branch") or detect_default_branch(repo)
    if not isinstance(default_branch, str) or not re.fullmatch(r"[A-Za-z0-9._/-]+", default_branch):
        raise LedgerError("config.team.default_branch must be a valid branch name.")
    derived_updates = raw_team.get("derived_updates", "default-branch")
    if derived_updates not in {"default-branch", "always"}:
        raise LedgerError("config.team.derived_updates must be default-branch or always.")
    raw_quality = config.get("quality", {})
    if not isinstance(raw_quality, dict):
        raise LedgerError("config.quality must be an object.")
    quality_language = raw_quality.get("language", "auto")
    if quality_language not in {"auto", "en", "zh-CN"}:
        raise LedgerError("config.quality.language must be auto, en, or zh-CN.")
    quality_detail = raw_quality.get("detail", "standard")
    if quality_detail not in {"concise", "standard", "detailed"}:
        raise LedgerError("config.quality.detail must be concise, standard, or detailed.")
    default_pack_lines = {"concise": 120, "standard": 180, "detailed": 300}[quality_detail]
    max_pack_lines = raw_quality.get("max_context_pack_lines", default_pack_lines)
    if not isinstance(max_pack_lines, int) or isinstance(max_pack_lines, bool) or not 60 <= max_pack_lines <= 500:
        raise LedgerError("config.quality.max_context_pack_lines must be an integer from 60 to 500.")
    raw_adapters = config.get("adapters", {})
    if not isinstance(raw_adapters, dict):
        raise LedgerError("config.adapters must be an object.")
    unknown_adapters = set(raw_adapters).difference(ADAPTER_NAMES)
    if unknown_adapters:
        raise LedgerError(f"Unknown context adapter: {sorted(unknown_adapters)[0]}")
    adapters = {}
    for name in ADAPTER_NAMES:
        enabled = raw_adapters.get(name, True)
        if not isinstance(enabled, bool):
            raise LedgerError(f"config.adapters.{name} must be true or false.")
        adapters[name] = enabled
    coverage = normalize_coverage_globs(config.get("coverage"))
    return {
        "schema_version": VERSION,
        "docs": normalized_docs,
        "modules": normalized_modules,
        "readme_managed_blocks": bool(config.get("readme_managed_blocks", True)),
        "adapters": adapters,
        "coverage": coverage,
        "team": {
            "enabled": team_enabled,
            "default_branch": default_branch,
            "derived_updates": derived_updates,
        },
        "quality": {
            "profile": QUALITY_PROFILE,
            "language": quality_language,
            "detail": quality_detail,
            "max_context_pack_lines": max_pack_lines,
        },
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
        if relative.parts and (current_path / ".git").exists():
            dirs[:] = []
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

1. Before editing code, run `status`, then start or reuse only this task's private draft session. Keep the returned session ID and pass `--session <id>` whenever multiple sessions exist.
2. Resolve `quality.language`; when it is `auto`, follow nearby docs or the user's language. Keep paths, symbols, commands, and error text untranslated.
3. Use `context --query "<task>"` and focus the feature Context Pack before broad code exploration. If none exists, create and fill one.
4. Run `checkpoint --session <id> --summary "..." --next "..."` before handing active work to another Agent. Pause only this task's session; never pause, resume, or finish another task's session.
5. Run every claimed check through `python .context-ledger/ledger.py verify -- <command>`. Use `verify --not-run --reason \"...\"` only when verification is genuinely unavailable.
6. Run `evidence`, read `.context-ledger/writing-quality.md`, and fill the private draft from actual changed paths. When another session exists, pass repeated `--path <path>` values for only this task; never capture foreign dirty paths. Refresh affected Context Packs with `pack --file ...`.
7. Update `{specs}/` when current behavior, contracts, boundaries, or code navigation changes.
8. Finish with `finish --spec <affected-spec>`, or use `--no-spec --reason \"...\"` only when no stable behavior exists.
9. Let `finish` enforce this session's evidence, specs, and relevant Context Pack fingerprints. Run repository-wide `check --strict --coverage` only at integration or PR time, when foreign sessions are not actively changing the shared worktree.
10. Before opening or updating a pull request, update the base ref and run `team-check --base origin/{config.get('team', {}).get('default_branch', 'main')}`.

Active and paused drafts are stored in Git worktree metadata and must not be committed. Only `finish` may publish a validated draft into `{changes}/`. On feature branches, do not regenerate shared README or monthly index blocks. After merging on `{config.get('team', {}).get('default_branch', 'main')}`, run `python .context-ledger/ledger.py sync --derived` once.

Never send a message, delegation, follow-up prompt, or steering instruction to another user-owned task or thread unless the user explicitly requested cross-task coordination. A foreign dirty path, stale Pack, failed global check, or shared worktree is not permission. Do not repair another session's docs to unblock this task. The ledger does not copy, lock, merge, or coordinate source-code edits; leave code conflicts to the host Agent and Git without interrupting another task.

Do not ask the user to run bookkeeping commands. Do not create a handoff for read-only analysis or formatting-only work. Preserve prose outside `repo-context-ledger` managed markers."""


def claude_adapter_body() -> str:
    return """@AGENTS.md

Treat Git-tracked Context Packs, stable specs, and handoffs as the cross-Agent source of truth. Follow the repository context ledger workflow without asking the user to run lifecycle commands. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination."""


def cursor_adapter_content() -> str:
    return """---
description: Route Cursor through the repository's verified, cross-Agent context ledger.
alwaysApply: true
---

Read and follow the repository root `AGENTS.md`. Use `python .context-ledger/ledger.py context --query "<task>"` to load the smallest relevant Context Pack and stable spec. Treat Cursor Memory as a private cache, never as the repository source of truth. Run ledger lifecycle commands autonomously; never delegate them to the user. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination.
"""


def copilot_adapter_body() -> str:
    return """## Repository Context Ledger

Read and follow the repository root `AGENTS.md`. Before broad code exploration, run `python .context-ledger/ledger.py context --query "<task>"` and load the matching Context Pack and stable spec. Treat Copilot Memory as a private cache; Git-tracked ledger documents are the shared cross-Agent source of truth. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination."""


def adapter_states(repo: Path, config: dict) -> dict[str, tuple[Path, str, bool]]:
    states: dict[str, tuple[Path, str, bool]] = {}
    agents = repo / "AGENTS.md"
    agents_text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    states["agents"] = (
        agents,
        managed_rules(config),
        managed_text(agents_text, RULE_START, RULE_END) == managed_rules(config),
    )
    claude = repo / "CLAUDE.md"
    claude_text = claude.read_text(encoding="utf-8") if claude.is_file() else ""
    states["claude"] = (
        claude,
        claude_adapter_body(),
        managed_text(claude_text, RULE_START, RULE_END) == claude_adapter_body(),
    )
    cursor = repo / ".cursor/rules/repo-context-ledger.mdc"
    cursor_text = cursor.read_text(encoding="utf-8") if cursor.is_file() else ""
    states["cursor"] = (
        cursor,
        cursor_adapter_content(),
        cursor_text.replace("\r\n", "\n") == cursor_adapter_content(),
    )
    copilot = repo / ".github/copilot-instructions.md"
    copilot_text = copilot.read_text(encoding="utf-8") if copilot.is_file() else ""
    states["copilot"] = (
        copilot,
        copilot_adapter_body(),
        managed_text(copilot_text, RULE_START, RULE_END) == copilot_adapter_body(),
    )
    return states


def sync_adapters(repo: Path, config: dict, quiet: bool = False) -> int:
    enabled = config.get("adapters", {})
    if enabled.get("agents", True):
        replace_block(repo / "AGENTS.md", RULE_START, RULE_END, managed_rules(config), "# Agent instructions")
    if enabled.get("claude", True):
        replace_block(
            repo / "CLAUDE.md",
            RULE_START,
            RULE_END,
            claude_adapter_body(),
            "# Claude Code instructions",
        )
    if enabled.get("cursor", True):
        atomic_write(repo / ".cursor/rules/repo-context-ledger.mdc", cursor_adapter_content())
    if enabled.get("copilot", True):
        replace_block(
            repo / ".github/copilot-instructions.md",
            RULE_START,
            RULE_END,
            copilot_adapter_body(),
            "# GitHub Copilot instructions",
        )
    if not quiet:
        print("Synchronized enabled context adapters.")
    return 0


def inspect_adapters(repo: Path, config: dict, fail_on_drift: bool) -> int:
    errors = []
    states = adapter_states(repo, config)
    for name in ADAPTER_NAMES:
        path, _, current = states[name]
        if not config.get("adapters", {}).get(name, True):
            print(f"{name}: disabled")
            continue
        status = "current" if current else "missing-or-drifted"
        print(f"{name}: {status} ({rel_posix(path, repo)})")
        if not current:
            errors.append(f"Context adapter is missing or drifted: {rel_posix(path, repo)}")
    if errors and fail_on_drift:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


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
    quality_source = Path(__file__).resolve().parent.parent / "references" / "writing-quality.md"
    quality_target = runtime_dir / "writing-quality.md"
    if quality_source.exists() and quality_source.resolve() != quality_target.resolve():
        shutil.copy2(quality_source, quality_target)

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
        "adapters": previous.get("adapters") or {name: True for name in ADAPTER_NAMES},
        "coverage": previous.get("coverage") or COVERAGE_GLOB_DEFAULTS,
        "team": previous.get("team") or {
            "enabled": is_git_repo(repo),
            "default_branch": detect_default_branch(repo),
            "derived_updates": "default-branch",
        },
        "quality": previous.get("quality") or {
            "profile": QUALITY_PROFILE,
            "language": "auto",
            "detail": "standard",
            "max_context_pack_lines": 180,
        },
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
            "LANGUAGE": record_language(config),
            "DETAIL": config.get("quality", {}).get("detail", "standard"),
        }),
    )
    migrated_state = migrate_workspace_state(repo, config)
    write_if_missing(specs_root / "README.md", "# Stable feature context\n")
    write_if_missing(changes_root / "README.md", "# Change history\n")

    sync_adapters(repo, config, quiet=True)

    sync_repo(repo, derived=True)
    print(f"Initialized Repo Context Ledger in {repo}")
    print(f"Detected modules: {len(modules)}")
    print(f"Team mode: {'enabled' if config['team']['enabled'] else 'disabled'}")
    if migrated_state:
        print("Migrated shared pre-v0.3 state to workspace-local state.")
    return 0


def active_pointer(repo: Path, config: dict) -> Path:
    return legacy_active_pointer(repo, config)


def task_session_root(repo: Path) -> Path:
    return context_state_path(repo).parent / "sessions"


def task_session_draft_path(repo: Path, session_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", session_id):
        raise LedgerError(f"Invalid task session ID: {session_id}")
    root = task_session_root(repo).resolve()
    target = (root / session_id / "handoff.md").resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise LedgerError("Task session draft points outside private workspace state.") from exc
    return target


def session_draft_ref(repo: Path, draft: Path) -> str:
    return os.path.relpath(draft.resolve(), context_state_path(repo).parent.resolve()).replace(os.sep, "/")


def validate_private_draft_path(repo: Path, raw: str, label: str = "task session draft") -> Path:
    root = task_session_root(repo).resolve()
    target = (context_state_path(repo).parent / raw).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise LedgerError(f"{label.capitalize()} points outside private workspace state.") from exc
    return target


def validate_handoff_path(repo: Path, config: dict, raw: str, label: str = "handoff") -> Path:
    target = safe_repo_path(repo, raw, "active handoff")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    try:
        target.relative_to(changes_root)
    except ValueError as exc:
        raise LedgerError(f"{label.capitalize()} points outside the configured change history.") from exc
    return target


def resolve_session_draft(repo: Path, config: dict, session_id: str, record: dict) -> Path:
    raw = record["draft"]
    try:
        return validate_private_draft_path(repo, raw)
    except LedgerError:
        legacy = validate_handoff_path(repo, config, raw, f"legacy task session {session_id}")
        return legacy


def session_candidates(state: dict, status: str) -> list[tuple[str, dict]]:
    return [
        (session_id, record)
        for session_id, record in state.get("task_sessions", {}).items()
        if record.get("status") == status
    ]


def resolve_task_session(
    repo: Path,
    config: dict,
    session: str = "",
    status: str = "active",
    handoff: str = "",
) -> tuple[str, dict, Path]:
    state = load_context_state(repo)
    candidates = session_candidates(state, status)
    requested = session.strip()
    if handoff.strip():
        normalized = handoff.strip().replace("\\", "/")
        candidates = [
            item for item in candidates
            if normalized in {item[1].get("draft"), item[1].get("publish_path")}
        ]
    elif requested:
        exact = [item for item in candidates if item[0] == requested]
        prefix = [item for item in candidates if item[0].startswith(requested)]
        candidates = exact or prefix
    if not candidates:
        detail = f" '{requested}'" if requested else ""
        raise LedgerError(f"No {status} task session{detail}.")
    if len(candidates) > 1:
        choices = ", ".join(session_id for session_id, _ in candidates)
        raise LedgerError(
            f"Multiple {status} task sessions exist ({choices}); rerun with --session <id>."
        )
    session_id, record = candidates[0]
    target = resolve_session_draft(repo, config, session_id, record)
    if not target.is_file():
        raise LedgerError(f"Task session draft does not exist: {record['draft']}")
    return session_id, record, target


def active_handoff(repo: Path, config: dict, session: str = "") -> Path | None:
    candidates = session_candidates(load_context_state(repo), "active")
    if not candidates:
        return None
    _, _, target = resolve_task_session(repo, config, session=session, status="active")
    return target


def start_change(repo: Path, title: str, feature: str = "", language: str = "") -> int:
    title = title.strip()
    if not title or len(title) > 160 or "\n" in title or "\r" in title:
        print("Task title must be one line containing 1 to 160 characters.", file=sys.stderr)
        return 2
    config = load_config(repo)
    feature = feature_slug(feature or title)
    stamp = now()
    handoff_id = unique_handoff_id(repo, stamp)
    publish_folder = safe_repo_path(
        repo,
        f"{config['docs']['changes']}/{stamp.strftime('%Y')}/{stamp.strftime('%m')}",
        "handoff month directory",
    )
    content = render_template(
        template_source("handoff-template.md", repo),
        {
            "TITLE": title,
            "FEATURE": feature,
            "ACTOR": git_actor(repo),
            "BRANCH": git_branch(repo),
            "HANDOFF_ID": handoff_id,
            "SESSION_ID": handoff_id,
            "LANGUAGE": record_language(config, language),
            "DETAIL": config.get("quality", {}).get("detail", "standard"),
            "STARTED": stamp.isoformat(timespec="seconds"),
            "BASE_COMMIT": git_revision(repo),
        },
    )
    stem = f"{handoff_id}-{slugify(title)}"
    publish_path = publish_folder / f"{stem}.md"
    counter = 1
    reserved = {
        record.get("publish_path")
        for record in load_context_state(repo).get("task_sessions", {}).values()
    }
    while publish_path.exists() or rel_posix(publish_path, repo) in reserved:
        counter += 1
        publish_path = publish_folder / f"{stem}-{counter}.md"
    draft = task_session_draft_path(repo, handoff_id)
    draft.parent.mkdir(parents=True, exist_ok=True)
    with draft.open("x", encoding="utf-8") as handle:
        handle.write(content.rstrip() + "\n")
    state = load_context_state(repo)
    state.setdefault("task_sessions", {})[handoff_id] = {
        "draft": session_draft_ref(repo, draft),
        "publish_path": rel_posix(publish_path, repo),
        "feature": feature,
        "status": "active",
        "updated_at": stamp.isoformat(timespec="seconds"),
    }
    remember_feature(state, feature)
    save_context_state(repo, state)
    print(f"Session: {handoff_id}")
    print(f"Publish target: {rel_posix(publish_path, repo)}")
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
    language: str = "",
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
                "BASE_BRANCH": config.get("team", {}).get("default_branch", "main"),
                "BASE_COMMIT": git_revision(repo, configured_base_ref(repo, config)),
                "REFRESHED": now().isoformat(timespec="seconds"),
                "LANGUAGE": record_language(config, language),
                "DETAIL": config.get("quality", {}).get("detail", "standard"),
            },
        )
    text = set_field(text, "Status", "current")
    text = set_field(text, "Feature", feature, after="Status")
    text = set_field(text, "Source commit", git_revision(repo), after="Feature")
    text = set_field(
        text,
        "Base branch",
        config.get("team", {}).get("default_branch", "main"),
        after="Source commit",
    )
    text = set_field(
        text,
        "Base commit",
        git_revision(repo, configured_base_ref(repo, config)),
        after="Base branch",
    )
    text = set_field(text, "Last refreshed", now().isoformat(timespec="seconds"), after="Base commit")
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
    if should_update_derived(repo, config):
        write_context_manifest(repo, config)
    print(rel_posix(path, repo))
    if not existing:
        print("Fill every TODO in the new context pack before focusing it.")
    return 0


PACK_REQUIRED_HEADINGS = (
    "## Purpose", "## Load order", "## Entry points and code map",
    "## Contracts and boundaries", "## Verification",
)


def context_pack_errors(
    repo: Path,
    path: Path,
    tracked_paths: set[str] | None = None,
) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if field_value(text, "Status").casefold() != "current":
        errors.append("Context pack status must be current.")
    if not field_value(text, "Feature"):
        errors.append("Context pack is missing Feature metadata.")
    if not field_value(text, "Source commit"):
        errors.append("Context pack is missing Source commit metadata.")
    if not field_value(text, "Base branch"):
        errors.append("Context pack is missing Base branch metadata.")
    if not field_value(text, "Base commit"):
        errors.append("Context pack is missing Base commit metadata.")
    if not field_value(text, "Last refreshed"):
        errors.append("Context pack is missing Last refreshed metadata.")
    if re.search(r"(?i)TODO:\s*|\{\{[A-Z_]+\}\}", text):
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
        if tracked_paths is not None and normalize_git_path(raw) not in tracked_paths:
            continue
        try:
            target = normalize_tracked_file(repo, raw)
        except LedgerError as exc:
            errors.append(str(exc))
            continue
        if file_digest(target) != expected:
            errors.append(f"Context pack is stale; tracked file changed: {raw}")
    if is_evidence_quality(text):
        config = load_config(repo)
        errors.extend(quality_metadata_errors(text, "Context pack"))
        max_lines = config.get("quality", {}).get("max_context_pack_lines", 180)
        if len(text.splitlines()) > max_lines:
            errors.append(f"Context pack has {len(text.splitlines())} lines; configured maximum is {max_lines}.")
        load_order = section_body(text, "## Load order")
        for label in ("Read first", "Read if needed", "Do not load by default"):
            if len(labeled_value(load_order, label)) < 8:
                errors.append(f"Context pack Load order requires a substantive {label}: value.")
        if not concrete_code_spans(section_body(text, "## Entry points and code map")):
            errors.append("Context pack code map must cite a concrete path or symbol in backticks.")
        contracts = section_body(text, "## Contracts and boundaries")
        for label in ("Invariants and contracts", "Failure / recovery", "Non-goals"):
            if len(labeled_value(contracts, label)) < 12:
                errors.append(f"Context pack boundaries require a substantive {label}: value.")
        if not re.search(r"`[^`\r\n]+`", section_body(text, "## Verification")):
            errors.append("Context pack Verification must cite a reliable command in backticks.")
        semantic = "\n".join(section_body(text, heading) for heading in PACK_REQUIRED_HEADINGS)
        if has_vague_standalone_text(semantic):
            errors.append("Context pack contains a vague standalone claim; replace it with concrete navigation or evidence.")
    return errors


def focus_context(repo: Path, feature: str, session: str = "") -> int:
    config = load_config(repo)
    feature = feature_slug(feature)
    pack = context_pack_path(repo, config, feature)
    if not pack.is_file():
        print(
            f"No context pack for {feature}. Create one with the pack command before focusing it.",
            file=sys.stderr,
        )
        return 2
    current = active_handoff(repo, config, session)
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


def pause_change(repo: Path, summary: str, next_step: str, session: str = "") -> int:
    if len(summary.strip()) < 10 or len(next_step.strip()) < 5:
        print("Pause requires a substantive --summary and --next step.", file=sys.stderr)
        return 2
    config = load_config(repo)
    session_id, record, handoff = resolve_task_session(repo, config, session=session)
    text = handoff.read_text(encoding="utf-8")
    if field_value(text, "Status").casefold() != "active":
        print("Only an active handoff can be paused.", file=sys.stderr)
        return 2
    feature = feature_slug(field_value(text, "Feature") or first_heading(handoff))
    text = set_field(text, "Feature", feature, after="Status")
    text = set_field(text, "Status", "paused")
    text = set_field(text, "Paused", now().isoformat(timespec="seconds"), after="Completed")
    text = set_field(text, "Base commit", field_value(text, "Base commit") or git_revision(repo), after="Resumed")
    text = set_field(text, "Checkpointed", now().isoformat(timespec="seconds"), after="Resumed")
    text = set_field(text, "Checkpoint actor", git_actor(repo), after="Checkpointed")
    text = set_field(text, "Resume summary", summary.strip(), after="Dirty paths")
    text = set_field(text, "Next step", next_step.strip(), after="Resume summary")
    dirty = git_dirty_paths(repo)
    text = set_field(text, "Dirty paths", ", ".join(dirty) if dirty else "none", after="Base commit")
    atomic_write(handoff, text.rstrip() + "\n")
    state = load_context_state(repo)
    state["task_sessions"][session_id] = {
        **record,
        "status": "paused",
        "updated_at": now().isoformat(timespec="seconds"),
    }
    save_context_state(repo, state)
    print(f"Paused session {session_id}")
    return 0


def checkpoint_change(repo: Path, summary: str, next_step: str, session: str = "") -> int:
    if len(summary.strip()) < 10 or len(next_step.strip()) < 5:
        print("Checkpoint requires a substantive --summary and --next step.", file=sys.stderr)
        return 2
    config = load_config(repo)
    session_id, record, handoff = resolve_task_session(repo, config, session=session)
    text = handoff.read_text(encoding="utf-8")
    if field_value(text, "Status").casefold() != "active":
        print("Only an active handoff can be checkpointed.", file=sys.stderr)
        return 2
    text = set_field(text, "Checkpointed", now().isoformat(timespec="seconds"), after="Resumed")
    text = set_field(text, "Checkpoint actor", git_actor(repo), after="Checkpointed")
    text = set_field(text, "Resume summary", summary.strip(), after="Dirty paths")
    text = set_field(text, "Next step", next_step.strip(), after="Resume summary")
    dirty = git_dirty_paths(repo)
    text = set_field(text, "Dirty paths", ", ".join(dirty) if dirty else "none", after="Base commit")
    atomic_write(handoff, text.rstrip() + "\n")
    refresh_handoff_evidence(repo, handoff)
    state = load_context_state(repo)
    state["task_sessions"][session_id] = {
        **record,
        "updated_at": now().isoformat(timespec="seconds"),
    }
    save_context_state(repo, state)
    print(f"Checkpointed session {session_id}")
    return 0


def resume_change(repo: Path, raw_handoff: str, session: str = "") -> int:
    config = load_config(repo)
    state = load_context_state(repo)
    session_id, record, handoff = resolve_task_session(
        repo, config, session=session, status="paused", handoff=raw_handoff
    )
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
    state["task_sessions"][session_id] = {
        **record,
        "feature": feature,
        "status": "active",
        "updated_at": now().isoformat(timespec="seconds"),
    }
    remember_feature(state, feature)
    save_context_state(repo, state)
    print(f"Resumed session {session_id}")
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
    paths = []
    for path in base.rglob("*.md"):
        if is_change_index(path, base):
            continue
        text = path.read_text(encoding="utf-8")
        if is_evidence_quality(text) and field_value(text, "Status").casefold() in {"active", "paused"}:
            continue
        paths.append(path)
    return sorted(paths, key=lambda p: p.as_posix(), reverse=True)


def context_manifest_path(repo: Path, config: dict) -> Path:
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    return ai_root / "context-manifest.json"


def context_manifest_data(repo: Path, config: dict) -> dict:
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    packs_root = ai_root / "context-packs"
    recent_by_feature: dict[str, list[dict[str, str]]] = {}
    for change in all_changes(repo, config):
        text = change.read_text(encoding="utf-8")
        feature = feature_slug(field_value(text, "Feature") or first_heading(change))
        recent_by_feature.setdefault(feature, []).append({
            "path": rel_posix(change, repo),
            "title": first_heading(change),
            "status": field_value(text, "Status") or "unknown",
        })
    features = []
    if packs_root.exists():
        for pack in sorted(packs_root.glob("*.md")):
            text = pack.read_text(encoding="utf-8")
            feature = feature_slug(field_value(text, "Feature") or pack.stem)
            specs = []
            for raw in pack_spec_paths(text):
                target = (pack.parent / raw).resolve()
                try:
                    specs.append(rel_posix(target, repo))
                except ValueError:
                    specs.append(raw.replace("\\", "/"))
            features.append({
                "feature": feature,
                "title": first_heading(pack).removesuffix(" context pack"),
                "context_pack": rel_posix(pack, repo),
                "status": field_value(text, "Status") or "unknown",
                "source_commit": field_value(text, "Source commit") or "none",
                "last_refreshed": field_value(text, "Last refreshed"),
                "stable_specs": specs,
                "tracked_files": [raw for raw, _ in pack_file_entries(text)],
                "recent_changes": recent_by_feature.get(feature, [])[:5],
            })
    project_context = ai_root / "project-context.md"
    return {
        "manifest_version": MANIFEST_VERSION,
        "tool_version": TOOL_VERSION,
        "default_branch": config.get("team", {}).get("default_branch", "main"),
        "project_context": rel_posix(project_context, repo) if project_context.is_file() else None,
        "docs": dict(config["docs"]),
        "features": features,
    }


def write_context_manifest(repo: Path, config: dict) -> Path:
    path = context_manifest_path(repo, config)
    atomic_write(path, json.dumps(context_manifest_data(repo, config), indent=2, ensure_ascii=False) + "\n")
    return path


def context_manifest_errors(repo: Path, config: dict) -> list[str]:
    path = context_manifest_path(repo, config)
    if not path.is_file():
        return [f"Missing context manifest: {rel_posix(path, repo)}"]
    try:
        actual = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Invalid context manifest: {exc}"]
    if actual != context_manifest_data(repo, config):
        return ["Context manifest is stale; run manifest sync on the default branch."]
    return []


def manage_context_manifest(repo: Path, action: str) -> int:
    config = load_config(repo)
    if action == "show":
        print(json.dumps(context_manifest_data(repo, config), indent=2, ensure_ascii=False))
        return 0
    if action == "sync":
        path = write_context_manifest(repo, config)
        print(f"Synchronized {rel_posix(path, repo)}")
        return 0
    errors = context_manifest_errors(repo, config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Context manifest is current.")
    return 0


def recognized_month_bucket(parent_parts: tuple[str, ...], changes_root: Path) -> tuple[str, Path] | None:
    if (
        len(parent_parts) >= 2
        and YEAR_PATTERN.fullmatch(parent_parts[0])
        and MONTH_PATTERN.fullmatch(parent_parts[1])
    ):
        label = f"{parent_parts[0]}-{parent_parts[1]}"
        return label, changes_root / parent_parts[0] / parent_parts[1]
    if parent_parts and LEGACY_MONTH_PATTERN.fullmatch(parent_parts[0]):
        return parent_parts[0], changes_root / parent_parts[0]
    return None


def is_change_index(path: Path, changes_root: Path) -> bool:
    name = path.name.casefold()
    if name == "readme.md":
        return True
    if name != "index.md":
        return False
    relative = path.relative_to(changes_root)
    parent_parts = relative.parts[:-1]
    if not parent_parts:
        return True
    bucket = recognized_month_bucket(parent_parts, changes_root)
    return bucket is not None and bucket[1] == path.parent


def change_month_bucket(change: Path, changes_root: Path) -> tuple[str, Path, bool]:
    relative_parent = change.parent.relative_to(changes_root)
    parent_parts = relative_parent.parts
    recognized = recognized_month_bucket(parent_parts, changes_root)
    if recognized:
        return recognized[0], recognized[1], True
    if parent_parts:
        return relative_parent.as_posix().replace("/", "-"), change.parent, False
    return "legacy", changes_root / "legacy", False


def unchanged_generated_change_index(path: Path, changes_root: Path) -> bool:
    """Return true only when the old generated file can be reproduced byte-for-byte."""
    try:
        relative_parent = path.parent.relative_to(changes_root)
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeError):
        return False
    if not relative_parent.parts:
        return False
    label = relative_parent.as_posix().replace("/", "-")
    source_changes = sorted(
        (candidate for candidate in path.parent.glob("*.md") if candidate.name.casefold() != "readme.md"),
        key=lambda candidate: candidate.as_posix(),
        reverse=True,
    )
    if not source_changes:
        return False
    entries = markdown_items(source_changes, path.parent)
    expected = (
        f"# Changes in {label}\n\n"
        f"{BLOCK_START}\n"
        f"## Changes in {label}\n\n"
        + "\n".join(entries)
        + f"\n{BLOCK_END}\n"
    )
    return text == expected


def remove_obsolete_change_indexes(changes_root: Path, expected: set[Path]) -> int:
    removed = 0
    root_index = (changes_root / "README.md").resolve()
    expected_resolved = {path.resolve() for path in expected}
    for candidate in changes_root.rglob("README.md"):
        resolved = candidate.resolve()
        if resolved == root_index or resolved in expected_resolved:
            continue
        if unchanged_generated_change_index(candidate, changes_root):
            candidate.unlink()
            removed += 1
    return removed


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


def should_update_derived(repo: Path, config: dict) -> bool:
    team = config.get("team", {})
    if not team.get("enabled") or team.get("derived_updates") == "always":
        return True
    return git_branch(repo) == team.get("default_branch")


def sync_repo(repo: Path, derived: bool = False) -> int:
    config = load_config(repo)
    if not derived and not should_update_derived(repo, config):
        print(
            "Skipped shared README and index regeneration on a feature branch; "
            "run sync --derived after merging on the default branch."
        )
        return 0
    specs = all_specs(repo, config)
    changes = all_changes(repo, config)
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    spec_index = specs_root / "README.md"
    change_index = changes_root / "README.md"
    spec_lines = markdown_items(specs, spec_index.parent) or ["- No stable feature specs yet."]
    replace_block(spec_index, BLOCK_START, BLOCK_END, "## Index\n\n" + "\n".join(spec_lines), "# Stable feature context")

    months: dict[tuple[str, str], dict[str, object]] = {}
    for change in changes:
        label, month_dir, recognized = change_month_bucket(change, changes_root)
        key = ("month", label) if recognized else ("path", month_dir.as_posix())
        bucket = months.setdefault(key, {"label": label, "directories": set(), "changes": []})
        bucket["directories"].add(month_dir)
        bucket["changes"].append(change)
    month_lines = []
    expected_indexes: set[Path] = set()
    ordered_months = sorted(months.values(), key=lambda item: str(item["label"]), reverse=True)
    for bucket in ordered_months:
        label = str(bucket["label"])
        directories = sorted(bucket["directories"], key=lambda path: path.as_posix())
        month_dir = next((path for path in directories if (path / "index.md").is_file()), None)
        if month_dir is None:
            month_dir = next((path for path in directories if (path / "README.md").is_file()), None)
        if month_dir is None:
            month_dir = next(
                (path for path in directories if LEGACY_MONTH_PATTERN.fullmatch(path.name)),
                directories[0],
            )
        legacy_index = month_dir / "index.md"
        month_index = legacy_index if legacy_index.is_file() else month_dir / "README.md"
        expected_indexes.add(month_index)
        entries = markdown_items(bucket["changes"], month_dir)
        if month_index.name.casefold() == "readme.md":
            replace_block(
                month_index,
                BLOCK_START,
                BLOCK_END,
                f"## Changes in {label}\n\n" + "\n".join(entries),
                f"# Changes in {label}",
            )
        link = os.path.relpath(month_index, changes_root).replace(os.sep, "/")
        month_lines.append(f"- [{label}]({link}) — {len(entries)} changes")
    removed_indexes = remove_obsolete_change_indexes(changes_root, expected_indexes)
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
    write_context_manifest(repo, config)
    if removed_indexes:
        print(f"Removed obsolete generated change indexes: {removed_indexes}")
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


def quality_metadata_errors(text: str, kind: str) -> list[str]:
    errors: list[str] = []
    language = field_value(text, "Language")
    if language not in {"en", "zh-CN"}:
        errors.append(f"{kind} Language must resolve to en or zh-CN; replace auto before completion.")
    if field_value(text, "Detail") not in {"concise", "standard", "detailed"}:
        errors.append(f"{kind} Detail must be concise, standard, or detailed.")
    return errors


def labeled_value(body: str, label: str) -> str:
    match = re.search(rf"(?mi)^\s*(?:[-*]\s*)?{re.escape(label)}:\s*(.+?)\s*$", body)
    return match.group(1).strip() if match else ""


def has_vague_standalone_text(body: str) -> bool:
    vague = {
        "updated relevant files", "fixed the logic", "tests passed", "updated documentation",
        "修改了相关代码", "修复了逻辑", "测试通过", "更新了相关文档", "已完成修改",
    }
    for raw in body.splitlines():
        line = re.sub(r"^[\s|>*-]+|[\s.|]+$", "", raw).casefold()
        if line in vague:
            return True
    return False


def normalize_git_path(raw: str) -> str:
    normalized = raw.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def glob_path_matches(raw: str, pattern: str) -> bool:
    path_parts = normalize_git_path(raw).split("/")
    pattern_parts = pattern.replace("\\", "/").strip("/").split("/")

    def match(path_index: int, pattern_index: int) -> bool:
        while pattern_index < len(pattern_parts):
            part = pattern_parts[pattern_index]
            if part == "**":
                if pattern_index == len(pattern_parts) - 1:
                    return True
                return any(
                    match(candidate, pattern_index + 1)
                    for candidate in range(path_index, len(path_parts) + 1)
                )
            if path_index >= len(path_parts) or not fnmatch.fnmatchcase(path_parts[path_index], part):
                return False
            path_index += 1
            pattern_index += 1
        return path_index == len(path_parts)

    return match(0, 0)


def coverage_path_kind(config: dict, raw: str) -> str:
    normalized = normalize_git_path(raw)
    doc_roots = [config["docs"][key].rstrip("/") + "/" for key in ("ai", "specs", "changes")]
    if any(normalized.startswith(prefix) for prefix in doc_roots):
        return "docs"
    managed_readmes = {
        normalize_git_path(module["readme"])
        for module in config.get("modules", [])
        if isinstance(module, dict) and isinstance(module.get("readme"), str)
    }
    if normalized in managed_readmes or (
        "/" not in normalized and re.fullmatch(r"README(?:\.[^/]+)*\.md", normalized, re.IGNORECASE)
    ):
        return "managed"
    if normalized.startswith((".context-ledger/", ".cursor/", ".agents/", ".claude/", ".grok/")):
        return "managed"
    if normalized == ".github/copilot-instructions.md":
        return "managed"
    if normalized in {"AGENTS.md", "CLAUDE.md"}:
        return "managed"
    coverage = config.get("coverage") or normalize_coverage_globs({})
    ordered = (
        ("ignore_globs", "ignored"),
        ("generated_globs", "generated"),
        ("test_globs", "test"),
        ("ci_globs", "ci"),
        ("config_globs", "config"),
        ("implementation_globs", "implementation"),
    )
    for key, kind in ordered:
        if any(glob_path_matches(normalized, pattern) for pattern in coverage.get(key, [])):
            return kind
    return "other"


def is_implementation_path(config: dict, raw: str) -> bool:
    return coverage_path_kind(config, raw) == "implementation"


def evidence_handoff_errors(repo: Path, config: dict, text: str) -> list[str]:
    errors = quality_metadata_errors(text, "Handoff")
    changed = section_body(text, "## Changed behavior")
    for label in ("Before", "After"):
        value = labeled_value(changed, label)
        if len(value) < 12:
            errors.append(f"Handoff Changed behavior requires a substantive {label}: value.")
    code_body = section_body(text, "## Code paths")
    code_refs = concrete_code_spans(code_body)
    if not code_refs:
        errors.append("Handoff Code paths must cite at least one concrete path or symbol in backticks.")
    boundaries = section_body(text, "## Boundaries and risks")
    for label in ("Invariant", "Failure / recovery", "Not changed"):
        if len(labeled_value(boundaries, label)) < 12:
            errors.append(f"Handoff Boundaries and risks requires a substantive {label}: value.")
    checks = managed_text(text, CHECKS_START, CHECKS_END)
    has_passed = "- Status: passed" in checks
    if "- Status: failed" in checks and not has_passed:
        errors.append("Handoff has a failed verification with no later passed verification.")
    if not has_passed and "- Not run —" not in checks:
        errors.append("Handoff requires a passed ledger verify record or a substantive not-run exception.")
    docs = section_body(text, "## Documentation updates")
    updated = labeled_value(docs, "Updated")
    reason = labeled_value(docs, "Reason")
    if not concrete_code_spans(updated) and not re.match(r"(?i)^none\s*[—-]\s*.{12,}$", updated):
        errors.append("Documentation updates must cite a path or use None — <substantive reason>.")
    if len(reason) < 12:
        errors.append("Documentation updates requires a substantive Reason: value.")
    questions = section_body(text, "## Open questions")
    if len(re.sub(r"[`*_#>\-]", "", questions).strip()) < 4:
        errors.append("Handoff Open questions must record uncertainty or explicitly say None.")
    evidence = managed_text(text, EVIDENCE_START, EVIDENCE_END)
    if not evidence or "Evidence has not been captured yet" in evidence:
        errors.append("Handoff Git change evidence has not been captured.")
    evidence_paths = [path for path in concrete_code_spans(evidence) if is_implementation_path(config, path)]
    if evidence_paths and not any(path in code_refs for path in evidence_paths):
        errors.append("Handoff Code paths must cite at least one implementation path from Git change evidence.")
    semantic = "\n".join(section_body(text, heading) for heading in REQUIRED_HANDOFF_HEADINGS)
    if has_vague_standalone_text(semantic):
        errors.append("Handoff contains a vague standalone claim; replace it with behavior, path, and evidence.")
    return errors


def handoff_validation_errors(
    text: str,
    repo: Path | None = None,
    config: dict | None = None,
    expected_status: str = "active",
) -> list[str]:
    errors = []
    if field_value(text, "Status").casefold() != expected_status.casefold():
        errors.append(f"Handoff status must be {expected_status}.")
    for field in ("Started", "Specs"):
        if not field_value(text, field):
            errors.append(f"Handoff metadata is missing: {field}.")
    if re.search(r"(?i)TODO:\s*", text):
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
    if is_evidence_quality(text):
        if repo is None or config is None:
            errors.append("Evidence-quality handoff validation requires repository context.")
        else:
            errors.extend(evidence_handoff_errors(repo, config, text))
    return errors


SPEC_REQUIRED_HEADINGS = (
    "## Purpose and behavior", "## Entry points and code map",
    "## Data flow and contracts", "## Boundaries and failure modes", "## Verification",
)


def spec_quality_errors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if not is_evidence_quality(text):
        return []
    errors = quality_metadata_errors(text, "Stable spec")
    if re.search(r"(?i)TODO:\s*|\{\{[A-Z_]+\}\}", text):
        errors.append("Stable spec still contains template placeholders.")
    for heading in SPEC_REQUIRED_HEADINGS:
        if len(re.sub(r"[`*_#>\-|]", "", section_body(text, heading)).strip()) < 12:
            errors.append(f"Stable spec section has no substantive content: {heading}")
    if not concrete_code_spans(section_body(text, "## Entry points and code map")):
        errors.append("Stable spec code map must cite a concrete path or symbol in backticks.")
    flow = section_body(text, "## Data flow and contracts")
    for label in ("Input", "Flow", "Persistence / dependencies", "Output"):
        if len(labeled_value(flow, label)) < 12:
            errors.append(f"Stable spec data flow requires a substantive {label}: value.")
    boundaries = section_body(text, "## Boundaries and failure modes")
    for label in ("Invariants", "Permissions / concurrency", "Failure / recovery", "Non-goals"):
        if len(labeled_value(boundaries, label)) < 12:
            errors.append(f"Stable spec boundaries require a substantive {label}: value.")
    if not re.search(r"`[^`\r\n]+`", section_body(text, "## Verification")):
        errors.append("Stable spec Verification must cite at least one reliable command in backticks.")
    return errors


def finish_change(
    repo: Path,
    raw_specs: list[str],
    no_spec: bool = False,
    reason: str = "",
    session: str = "",
) -> int:
    config = load_config(repo)
    session_id, record, draft = resolve_task_session(repo, config, session=session)
    publish_path = validate_handoff_path(
        repo, config, record["publish_path"], "task session publish path"
    )
    ensure_finish_evidence(repo, config, session_id, draft)
    text = draft.read_text(encoding="utf-8")
    errors = handoff_validation_errors(text, repo, config)
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
        errors.extend(f"{rel_posix(spec, repo)}: {error}" for error in spec_quality_errors(spec))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    preflight_errors = task_session_finish_errors(repo, config, text, specs, no_spec)
    if preflight_errors:
        for error in preflight_errors:
            print(error, file=sys.stderr)
        print("Finish preflight failed; the private draft remains active.", file=sys.stderr)
        return 2
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
    completed_text = text.rstrip() + "\n"
    if publish_path.exists():
        existing = publish_path.read_text(encoding="utf-8")
        if (
            field_value(existing, "Handoff ID") != session_id
            or field_value(existing, "Status").casefold() != "completed"
        ):
            print(f"Publish target already exists: {rel_posix(publish_path, repo)}", file=sys.stderr)
            return 2
        completed_text = existing
    else:
        atomic_write(publish_path, completed_text)
    for spec in specs:
        link_change_to_spec(spec, publish_path)
    sync_repo(repo)
    published_errors = handoff_validation_errors(
        completed_text, repo, config, expected_status="completed"
    )
    published_errors.extend(task_session_finish_errors(
        repo, config, completed_text, specs, no_spec
    ))
    if published_errors:
        for error in published_errors:
            print(error, file=sys.stderr)
        print(
            "Published record validation failed; the private draft and session were preserved for recovery.",
            file=sys.stderr,
        )
        return 2
    state = load_context_state(repo)
    state["task_sessions"].pop(session_id, None)
    save_context_state(repo, state)
    try:
        private = validate_private_draft_path(repo, record["draft"])
        private.unlink(missing_ok=True)
        private.parent.rmdir()
    except (LedgerError, OSError):
        print(f"WARNING: completed session draft could not be cleaned automatically: {record['draft']}")
    print(f"Completed {rel_posix(publish_path, repo)}")
    return 0


def local_links(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text)


def git_changed_paths(repo: Path, *args: str) -> set[str]:
    output = git_output(repo, "diff", "--name-only", "--diff-filter=ACMRD", *args)
    return {line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()}


def handoff_evidence_paths(
    repo: Path,
    handoff_text: str,
    raw_paths: list[str] | None = None,
) -> list[str]:
    paths: set[str] = set(git_dirty_paths(repo))
    base = field_value(handoff_text, "Base commit")
    if is_git_repo(repo) and base not in {"", "none"} and git_revision(repo, base) != "none":
        paths.update(git_changed_paths(repo, f"{base}..HEAD"))
    if raw_paths is None:
        return sorted(paths)
    selected: set[str] = set()
    for raw in raw_paths:
        normalized = normalize_git_path(raw.strip())
        safe_repo_path(repo, normalized, "evidence path")
        if normalized not in paths:
            raise LedgerError(f"Evidence path is not changed from this session base: {normalized}")
        selected.add(normalized)
    return sorted(selected)


def refresh_handoff_evidence(
    repo: Path,
    handoff: Path,
    raw_paths: list[str] | None = None,
) -> list[str]:
    text = handoff.read_text(encoding="utf-8")
    paths = handoff_evidence_paths(repo, text, raw_paths)
    lines = [
        "## Git change evidence",
        "",
        f"- Base commit: `{field_value(text, 'Base commit') or 'none'}`",
        f"- Current commit: `{git_revision(repo)}`",
        "- Changed paths:",
    ]
    lines.extend(f"  - `{raw}`" for raw in paths)
    if not paths:
        lines.append("  - None detected.")
    updated = replace_managed_text(text, EVIDENCE_START, EVIDENCE_END, "\n".join(lines))
    atomic_write(handoff, updated.rstrip() + "\n")
    return paths


def recorded_handoff_evidence_paths(text: str) -> set[str]:
    evidence = managed_text(text, EVIDENCE_START, EVIDENCE_END)
    return {
        normalize_git_path(raw)
        for raw in concrete_code_spans(evidence)
        if normalize_git_path(raw)
    }


def ensure_finish_evidence(repo: Path, config: dict, session_id: str, handoff: Path) -> None:
    text = handoff.read_text(encoding="utf-8")
    evidence = managed_text(text, EVIDENCE_START, EVIDENCE_END)
    if evidence and "Evidence has not been captured yet" not in evidence:
        return
    sessions = load_context_state(repo).get("task_sessions", {})
    if is_git_repo(repo) and len(sessions) > 1:
        raise LedgerError(
            f"Session {session_id} has no scoped evidence; run evidence --session {session_id} "
            "with --path for only this task."
        )
    refresh_handoff_evidence(repo, handoff)


def task_session_finish_errors(
    repo: Path,
    config: dict,
    handoff_text: str,
    specs: list[Path],
    no_spec: bool,
) -> list[str]:
    errors: list[str] = []
    documented = recorded_handoff_evidence_paths(handoff_text)
    actual = set(handoff_evidence_paths(repo, handoff_text))
    for raw in sorted(documented - actual):
        errors.append(f"Session evidence path is no longer changed from its base: {raw}")

    implementation = sorted(
        raw for raw in documented if is_implementation_path(config, raw)
    )
    if not implementation:
        return errors

    documented_specs = {
        rel_posix(spec, repo) for spec in specs
    }
    if specs and not documented_specs.issubset(documented):
        for raw in sorted(documented_specs - documented):
            errors.append(f"Session evidence does not include its stable spec: {raw}")
    if not specs and not no_spec:
        errors.append("Session implementation evidence requires a stable spec or explicit exception.")

    packs_by_path = tracked_context_packs(repo, config)
    for raw in implementation:
        related = packs_by_path.get(normalize_git_path(raw), [])
        if not related:
            continue
        refreshed = [pack for pack in related if pack in documented]
        if not refreshed:
            errors.append(f"Session did not refresh a related Context Pack for: {raw}")
            continue
        for pack_raw in refreshed:
            pack = safe_repo_path(repo, pack_raw, "session Context Pack")
            for error in context_pack_errors(repo, pack, {normalize_git_path(raw)}):
                errors.append(f"{pack_raw}: {error}")
    return errors


def capture_evidence(
    repo: Path,
    session: str = "",
    raw_paths: list[str] | None = None,
) -> int:
    config = load_config(repo)
    session_id, record, handoff = resolve_task_session(repo, config, session=session)
    sessions = load_context_state(repo).get("task_sessions", {})
    if is_git_repo(repo) and len(sessions) > 1 and not raw_paths:
        raise LedgerError(
            f"Multiple task sessions exist; pass --path for only this task "
            f"when capturing session {session_id}."
        )
    paths = refresh_handoff_evidence(repo, handoff, raw_paths or None)
    print(f"Updated private Git change evidence for session {session_id} -> {record['publish_path']}")
    for raw in paths:
        print(f"- {raw}")
    return 0


def verification_output_summary(stdout: str, stderr: str) -> str:
    output = stdout + ("\n" if stdout and stderr else "") + stderr
    if not output:
        return "No output."
    digest = hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest()
    return f"sha256:{digest} ({len(output)} characters captured; content not persisted)"


def redacted_command(command: list[str]) -> list[str]:
    sensitive = re.compile(r"(?i)(password|passwd|secret|token|api[-_]?key|authorization)")
    result: list[str] = []
    redact_next = False
    for item in command:
        if redact_next:
            result.append("<redacted>")
            redact_next = False
            continue
        if "=" in item:
            key, _ = item.split("=", 1)
            if sensitive.search(key):
                result.append(f"{key}=<redacted>")
                continue
        result.append(item)
        if item.startswith("-") and sensitive.search(item):
            redact_next = True
    return result


def record_verification(
    repo: Path,
    command: list[str],
    timeout_seconds: int,
    not_run: bool = False,
    reason: str = "",
    session: str = "",
) -> int:
    config = load_config(repo)
    if not_run:
        if len(reason.strip()) < 20:
            print("A not-run verification reason must contain at least 20 characters.", file=sys.stderr)
            return 2
        with repo_lock(repo):
            session_id, record, handoff = resolve_task_session(repo, config, session=session)
            text = handoff.read_text(encoding="utf-8")
            checks = managed_text(text, CHECKS_START, CHECKS_END)
            if "No verification recorded yet." in checks:
                checks = ""
            entry = f"- Not run — {reason.strip()}\n  - Recorded: {now().isoformat(timespec='seconds')}"
            checks = "\n".join(item for item in (checks, entry) if item).strip()
            updated = replace_managed_text(text, CHECKS_START, CHECKS_END, checks)
            atomic_write(handoff, updated.rstrip() + "\n")
        print(f"Recorded verification exception for session {session_id} -> {record['publish_path']}")
        return 0
    command = [item for item in command if item != "--"]
    if not command:
        print("verify requires a command after --, or --not-run with --reason.", file=sys.stderr)
        return 2
    if timeout_seconds < 1 or timeout_seconds > 3600:
        print("Verification timeout must be from 1 to 3600 seconds.", file=sys.stderr)
        return 2
    with repo_lock(repo):
        session_id, record, handoff = resolve_task_session(repo, config, session=session)
        draft_identity = str(handoff.resolve())
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=repo,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        exit_code = result.returncode
        stdout, stderr = result.stdout, result.stderr
        status = "passed" if exit_code == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stderr += f"\nTimed out after {timeout_seconds} seconds."
        status = "failed"
    except OSError as exc:
        exit_code = 127
        stdout, stderr = "", str(exc)
        status = "failed"
    duration = time.monotonic() - started
    display_command = subprocess.list2cmdline(redacted_command(command)).replace("`", "'")
    recorded = now().isoformat(timespec="seconds")
    entry = (
        f"- Command: `{display_command}`\n"
        f"  - Status: {status}\n"
        f"  - Exit code: {exit_code}\n"
        f"  - Duration: {duration:.2f}s\n"
        f"  - Recorded: {recorded}\n"
        f"  - Output evidence: {verification_output_summary(stdout, stderr)}"
    )
    try:
        with repo_lock(repo):
            latest_id, _, latest_handoff = resolve_task_session(
                repo, config, session=session_id, status="active"
            )
            if latest_id != session_id or str(latest_handoff.resolve()) != draft_identity:
                raise LedgerError("Task session changed while verification was running; result was not recorded.")
            text = latest_handoff.read_text(encoding="utf-8")
            checks = managed_text(text, CHECKS_START, CHECKS_END)
            if "No verification recorded yet." in checks:
                checks = ""
            checks = "\n".join(item for item in (checks, entry) if item).strip()
            updated = replace_managed_text(text, CHECKS_START, CHECKS_END, checks)
            atomic_write(latest_handoff, updated.rstrip() + "\n")
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Verification command finished, but its result was not written.", file=sys.stderr)
        return 2
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n")
    if stderr:
        print(stderr, file=sys.stderr, end="" if stderr.endswith("\n") else "\n")
    print(f"Recorded {status} verification for session {session_id} -> {record['publish_path']}")
    return 0 if exit_code == 0 else 1


def handoff_features_for_paths(
    repo: Path,
    config: dict,
    paths: set[str],
    ref: str | None = None,
) -> set[str]:
    changes_prefix = config["docs"]["changes"].rstrip("/") + "/"
    features: set[str] = set()
    for raw in paths:
        if not raw.startswith(changes_prefix) or not raw.endswith(".md") or raw.endswith("/README.md"):
            continue
        if ref:
            text = git_output(repo, "show", f"{ref}:{raw}")
        else:
            path = repo / raw
            text = path.read_text(encoding="utf-8") if path.is_file() else git_output(repo, "show", f"HEAD:{raw}")
        feature = field_value(text, "Feature")
        if feature:
            features.add(feature_slug(feature))
    return features


def is_generated_index(config: dict, raw: str) -> bool:
    raw = raw.replace("\\", "/")
    specs_index = config["docs"]["specs"].rstrip("/") + "/README.md"
    changes_root = config["docs"]["changes"].rstrip("/")
    manifest = config["docs"]["ai"].rstrip("/") + "/context-manifest.json"
    return raw in {specs_index, manifest} or (
        raw.startswith(changes_root + "/") and raw.endswith("/README.md")
    ) or raw == changes_root + "/README.md"


def tracked_context_packs(repo: Path, config: dict) -> dict[str, list[str]]:
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    packs_root = ai_root / "context-packs"
    tracked: dict[str, list[str]] = {}
    if not packs_root.exists():
        return tracked
    for pack in sorted(packs_root.glob("*.md")):
        pack_rel = rel_posix(pack, repo)
        text = pack.read_text(encoding="utf-8")
        for raw, _ in pack_file_entries(text):
            tracked.setdefault(normalize_git_path(raw), []).append(pack_rel)
    return tracked


def coverage_validation_errors(repo: Path, config: dict, raw_base: str = "") -> list[str]:
    if not is_git_repo(repo):
        return ["Change coverage requires a Git repository."]
    base = raw_base.strip() or configured_base_ref(repo, config)
    if git_revision(repo, base) == "none":
        return [f"Coverage base ref does not exist locally: {base}"]
    merge_base = git_output(repo, "merge-base", "HEAD", base) or git_revision(repo, base)
    changed = git_changed_paths(repo, f"{merge_base}..HEAD")
    changed.update(git_dirty_paths(repo))
    implementation = sorted(path for path in changed if is_implementation_path(config, path))
    if not implementation:
        return []

    changes_prefix = config["docs"]["changes"].rstrip("/") + "/"
    handoff_paths = sorted(
        path for path in changed
        if path.startswith(changes_prefix) and path.endswith(".md")
        and not path.endswith("/README.md") and not path.endswith("/index.md")
    )
    private_handoff_texts: list[str] = []
    for session_id, record in load_context_state(repo).get("task_sessions", {}).items():
        try:
            draft = resolve_session_draft(repo, config, session_id, record)
        except LedgerError:
            continue
        if draft.is_file():
            private_handoff_texts.append(draft.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not handoff_paths and not private_handoff_texts:
        errors.append("Behavior-changing paths have no changed record or active private handoff.")
        documented: set[str] = set()
        no_spec_reason = False
    else:
        documented = set()
        no_spec_reason = False
        for raw in handoff_paths:
            path = repo / raw
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            documented.update(concrete_code_spans(managed_text(text, EVIDENCE_START, EVIDENCE_END)))
            exception = field_value(text, "Spec exception")
            if exception and exception.casefold() != "none" and len(exception) >= 20:
                no_spec_reason = True
        for text in private_handoff_texts:
            documented.update(concrete_code_spans(managed_text(text, EVIDENCE_START, EVIDENCE_END)))
            exception = field_value(text, "Spec exception")
            if exception and exception.casefold() != "none" and len(exception) >= 20:
                no_spec_reason = True
    for raw in implementation:
        if raw not in documented:
            errors.append(f"Behavior-changing path is not covered by handoff evidence: {raw}")

    specs_prefix = config["docs"]["specs"].rstrip("/") + "/"
    changed_specs = [
        path for path in changed
        if path.startswith(specs_prefix) and path.endswith(".md") and not path.endswith("/README.md")
    ]
    if not changed_specs and not no_spec_reason:
        errors.append("Behavior-changing paths require a changed stable spec or a completed spec exception.")

    packs_prefix = config["docs"]["ai"].rstrip("/") + "/context-packs/"
    changed_packs = {
        path for path in changed if path.startswith(packs_prefix) and path.endswith(".md")
    }
    packs_by_path = tracked_context_packs(repo, config)
    for raw in implementation:
        related = packs_by_path.get(normalize_git_path(raw), [])
        if not related:
            errors.append(
                f"Behavior-changing path has no related Context Pack tracked file: {raw}"
            )
            continue
        for pack in related:
            if pack not in changed_packs:
                errors.append(
                    f"Related Context Pack was not changed for behavior-changing path {raw}: {pack}"
                )
    return errors


def team_check(repo: Path, raw_base: str) -> int:
    config = load_config(repo)
    if not is_git_repo(repo):
        print("Team check requires a Git repository.", file=sys.stderr)
        return 2
    base = raw_base.strip() or configured_base_ref(repo, config)
    base_revision = git_revision(repo, base)
    if base_revision == "none":
        print(f"Base ref does not exist locally: {base}", file=sys.stderr)
        return 2
    merge_base = git_output(repo, "merge-base", "HEAD", base)
    if not merge_base:
        print(f"Cannot determine a merge base with {base}.", file=sys.stderr)
        return 2

    local_changed = git_changed_paths(repo, f"{merge_base}..HEAD")
    local_changed.update(git_dirty_paths(repo))
    upstream_changed = git_changed_paths(repo, f"{merge_base}..{base}")
    errors: list[str] = []

    for raw in sorted(local_changed.intersection(upstream_changed)):
        errors.append(f"Both this branch and {base} changed: {raw}")

    local_features = handoff_features_for_paths(repo, config, local_changed)
    upstream_features = handoff_features_for_paths(repo, config, upstream_changed, base)
    for feature in sorted(local_features.intersection(upstream_features)):
        errors.append(f"Concurrent handoffs affect the same feature: {feature}")

    current_branch = git_branch(repo)
    default_branch = config.get("team", {}).get("default_branch", "main")
    if current_branch != default_branch:
        for raw in sorted(path for path in local_changed if is_generated_index(config, path)):
            errors.append(
                f"Feature branch modifies generated index {raw}; restore it and regenerate after merge."
            )

    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    packs_root = ai_root / "context-packs"
    if packs_root.exists():
        for pack in sorted(packs_root.glob("*.md")):
            pack_rel = rel_posix(pack, repo)
            if pack_rel not in local_changed:
                continue
            for error in context_pack_errors(repo, pack):
                errors.append(f"{pack_rel}: {error}")
            recorded_base = field_value(pack.read_text(encoding="utf-8"), "Base commit")
            if recorded_base not in {"", "none", base_revision}:
                errors.append(
                    f"{pack_rel} was refreshed from base {recorded_base}, but {base} is {base_revision}."
                )

    print(f"Team check base: {base} ({base_revision})")
    print(f"Current branch: {current_branch}")
    print(f"Branch changes: {len(local_changed)}; upstream changes: {len(upstream_changed)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("Team collaboration check passed.")
    return 0


def check_repo(
    repo: Path,
    strict: bool,
    coverage: bool = False,
    coverage_base: str = "",
) -> int:
    errors: list[str] = []
    try:
        config = load_config(repo)
    except LedgerError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    specs_root = safe_repo_path(repo, config["docs"]["specs"], "config.docs.specs")
    changes_root = safe_repo_path(repo, config["docs"]["changes"], "config.docs.changes")
    ai_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai")
    for required in (repo / "AGENTS.md", specs_root / "README.md", changes_root / "README.md"):
        if not required.exists():
            errors.append(f"Missing required file: {rel_posix(required, repo)}")
    if (repo / "AGENTS.md").exists() and RULE_START not in (repo / "AGENTS.md").read_text(encoding="utf-8"):
        errors.append("AGENTS.md is missing the managed ledger rules.")
    states = adapter_states(repo, config)
    for name in ADAPTER_NAMES:
        path, _, current_adapter = states[name]
        if config.get("adapters", {}).get(name, True) and not current_adapter:
            errors.append(f"Context adapter is missing or drifted: {rel_posix(path, repo)}")
    if should_update_derived(repo, config):
        errors.extend(context_manifest_errors(repo, config))
    try:
        state = load_context_state(repo)
        draft_seen = set()
        publish_seen = set()
        for session_id, record in state.get("task_sessions", {}).items():
            raw = record["draft"]
            publish_raw = record["publish_path"]
            status = record["status"]
            if raw in draft_seen:
                errors.append(f"Duplicate private draft across task sessions: {raw}")
                continue
            draft_seen.add(raw)
            if publish_raw in publish_seen:
                errors.append(f"Duplicate publish target across task sessions: {publish_raw}")
                continue
            publish_seen.add(publish_raw)
            try:
                handoff = resolve_session_draft(repo, config, session_id, record)
                publish_path = validate_handoff_path(
                    repo, config, publish_raw, f"task session {session_id} publish path"
                )
            except LedgerError as exc:
                errors.append(str(exc))
                continue
            if not handoff.is_file():
                errors.append(f"Task session draft does not exist: {raw}")
                continue
            file_status = field_value(handoff.read_text(encoding="utf-8"), "Status").casefold()
            if file_status != status:
                errors.append(f"Task session {session_id} is {status}, but its draft is {file_status}: {raw}")
            if publish_path.exists():
                published = publish_path.read_text(encoding="utf-8")
                if (
                    field_value(published, "Handoff ID") != session_id
                    or field_value(published, "Status").casefold() != "completed"
                ):
                    errors.append(f"Task session publish target is occupied: {publish_raw}")
    except LedgerError as exc:
        errors.append(str(exc))

    if strict:
        for change in all_changes(repo, config):
            change_text = change.read_text(encoding="utf-8")
            if is_evidence_quality(change_text) and field_value(change_text, "Status").casefold() == "completed":
                for error in handoff_validation_errors(
                    change_text, repo, config, expected_status="completed"
                ):
                    errors.append(f"{rel_posix(change, repo)}: {error}")
        for path in changes_root.rglob("*.md"):
            if is_change_index(path, changes_root):
                continue
            text = path.read_text(encoding="utf-8")
            if is_evidence_quality(text) and field_value(text, "Status").casefold() in {"active", "paused"}:
                errors.append(f"Unfinished handoff is stored in formal change history: {rel_posix(path, repo)}")
        for spec in all_specs(repo, config):
            for error in spec_quality_errors(spec):
                errors.append(f"{rel_posix(spec, repo)}: {error}")
        packs_root = ai_root / "context-packs"
        if packs_root.exists():
            for pack in sorted(packs_root.glob("*.md")):
                for error in context_pack_errors(repo, pack):
                    errors.append(f"{rel_posix(pack, repo)}: {error}")
    if coverage:
        errors.extend(coverage_validation_errors(repo, config, coverage_base))

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
        if text.count(EVIDENCE_START) != text.count(EVIDENCE_END):
            errors.append(f"Unbalanced evidence markers: {rel_posix(path, repo)}")
        if text.count(CHECKS_START) != text.count(CHECKS_END):
            errors.append(f"Unbalanced verification markers: {rel_posix(path, repo)}")
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
    state = load_context_state(repo)
    packs_root = safe_repo_path(repo, config["docs"]["ai"], "config.docs.ai") / "context-packs"
    print(f"Repository: {repo}")
    print(f"Actor: {git_actor(repo)}")
    print(f"Branch: {git_branch(repo)}")
    print(f"Workspace state: {context_state_path(repo)}")
    print(f"Default branch: {config.get('team', {}).get('default_branch', 'main')}")
    active = session_candidates(state, "active")
    paused = session_candidates(state, "paused")
    print(f"Active task sessions: {len(active)}")
    for session_id, record in active:
        print(f"- {session_id} [{record.get('feature') or 'unknown'}] -> {record['publish_path']}")
    print(f"Paused task sessions: {len(paused)}")
    for session_id, record in paused:
        print(f"- {session_id} [{record.get('feature') or 'unknown'}] -> {record['publish_path']}")
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
    start.add_argument("--language", choices=("auto", "en", "zh-CN"), default="")
    context = sub.add_parser("context", help="Find likely stable background documents")
    context.add_argument("--query", required=True)
    context.add_argument("--limit", type=int, default=5)
    pack = sub.add_parser("pack", help="Create or refresh a feature Context Pack")
    pack.add_argument("--feature", required=True)
    pack.add_argument("--title", default="")
    pack.add_argument("--file", action="append", default=[])
    pack.add_argument("--spec", action="append", default=[])
    pack.add_argument("--language", choices=("auto", "en", "zh-CN"), default="")
    focus = sub.add_parser("focus", help="Load and validate a feature Context Pack")
    focus.add_argument("--feature", required=True)
    focus.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    checkpoint = sub.add_parser("checkpoint", help="Save an active cross-Agent resume checkpoint")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--next", required=True, dest="next_step")
    checkpoint.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    pause = sub.add_parser("pause", help="Pause the active handoff and preserve resume state")
    pause.add_argument("--summary", required=True)
    pause.add_argument("--next", required=True, dest="next_step")
    pause.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    resume = sub.add_parser("resume", help="Resume the latest or selected paused handoff")
    resume.add_argument("--handoff", default="")
    resume.add_argument("--session", default="", help="Paused task session ID; required when multiple sessions are paused")
    finish = sub.add_parser("finish", help="Complete the active handoff and link specs")
    finish_group = finish.add_mutually_exclusive_group()
    finish_group.add_argument("--spec", action="append", default=[])
    finish_group.add_argument("--no-spec", action="store_true")
    finish.add_argument("--reason", default="", help="Required explanation when --no-spec is used")
    finish.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    evidence = sub.add_parser("evidence", help="Refresh an active task session from actual Git changed paths")
    evidence.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    evidence.add_argument(
        "--path",
        action="append",
        default=[],
        help="Changed repository path owned by this task; repeat for multiple paths",
    )
    verify = sub.add_parser("verify", help="Run and record an actual verification command")
    verify.add_argument("--timeout", type=int, default=300)
    verify.add_argument("--not-run", action="store_true")
    verify.add_argument("--reason", default="")
    verify.add_argument("--session", default="", help="Task session ID; required when multiple sessions are active")
    verify.add_argument("verification_command", nargs=argparse.REMAINDER)
    sync = sub.add_parser("sync", help="Regenerate indexes and managed README blocks")
    sync.add_argument(
        "--derived",
        action="store_true",
        help="Force shared derived files to regenerate (normally after merging on the default branch)",
    )
    manifest = sub.add_parser("manifest", help="Show, synchronize, or validate the context manifest")
    manifest.add_argument("action", choices=("show", "sync", "check"))
    adapters = sub.add_parser("adapters", help="Synchronize or inspect native Agent entry files")
    adapters.add_argument("action", choices=("sync", "check", "status"))
    check = sub.add_parser("check", help="Validate ledger structure and local links")
    check.add_argument("--strict", action="store_true")
    check.add_argument("--coverage", action="store_true", help="Require Git changes to have handoff, spec, and Context Pack coverage")
    check.add_argument("--base", default="", help="Coverage base ref (default: configured default branch)")
    team = sub.add_parser("team-check", help="Detect branch, feature, and generated-file conflicts")
    team.add_argument("--base", default="", help="Base ref (default: configured origin default branch)")
    sub.add_parser("status", help="Show ledger state")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        repo = resolve_repo(args.repo)
        mutating = args.command in {
            "init", "start", "pack", "focus", "checkpoint", "pause", "resume", "finish",
            "evidence", "sync",
        } or (args.command in {"manifest", "adapters"} and args.action == "sync")
        if mutating:
            with repo_lock(repo):
                if args.command == "init":
                    return init_repo(repo)
                if args.command == "start":
                    return start_change(repo, args.title, args.feature, args.language)
                if args.command == "pack":
                    return refresh_context_pack(
                        repo, args.feature, args.title, args.file, args.spec, args.language
                    )
                if args.command == "focus":
                    return focus_context(repo, args.feature, args.session)
                if args.command == "checkpoint":
                    return checkpoint_change(repo, args.summary, args.next_step, args.session)
                if args.command == "pause":
                    return pause_change(repo, args.summary, args.next_step, args.session)
                if args.command == "resume":
                    return resume_change(repo, args.handoff, args.session)
                if args.command == "finish":
                    return finish_change(repo, args.spec, args.no_spec, args.reason, args.session)
                if args.command == "evidence":
                    return capture_evidence(repo, args.session, args.path)
                if args.command == "manifest":
                    return manage_context_manifest(repo, args.action)
                if args.command == "adapters":
                    return sync_adapters(repo, load_config(repo))
                return sync_repo(repo, args.derived)
        if args.command == "context":
            return context_search(repo, args.query, max(1, args.limit))
        if args.command == "verify":
            if args.not_run and args.verification_command:
                print("Use either a command or --not-run, not both.", file=sys.stderr)
                return 2
            return record_verification(
                repo, args.verification_command, args.timeout, args.not_run, args.reason, args.session
            )
        if args.command == "check":
            return check_repo(repo, args.strict, args.coverage, args.base)
        if args.command == "manifest":
            return manage_context_manifest(repo, args.action)
        if args.command == "adapters":
            return inspect_adapters(repo, load_config(repo), args.action == "check")
        if args.command == "team-check":
            return team_check(repo, args.base)
        if args.command == "status":
            return show_status(repo)
        return 2
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
