from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import os
import subprocess
import sys
import webbrowser

from .project_scaffold import ProjectScaffoldGenerator
from .event_log import FactoryEventLogger


@dataclass
class PreflightResult:
    github_repository: str
    github_exists: bool
    github_url: str | None
    local_directory: str
    local_exists: bool
    local_is_git: bool
    local_origin: str | None
    local_origin_matches: bool
    scaffold_stage_files: int
    project_yaml_exists: bool
    conflicts: list[str]
    allowed_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProjectInitializer:
    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root)
        self.events = FactoryEventLogger()

    @staticmethod
    def _run(args: list[str], cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=check,
            shell=False,
        )

    @staticmethod
    def _github_full_name(proposal: dict[str, Any]) -> str:
        return f"{proposal['github_owner']}/{proposal['github_repository']}"

    @staticmethod
    def _expected_origin(full_name: str) -> tuple[str, str]:
        return (
            f"https://github.com/{full_name}.git",
            f"git@github.com:{full_name}.git",
        )

    def _gh_available(self) -> bool:
        try:
            return self._run(["gh", "--version"]).returncode == 0
        except FileNotFoundError:
            return False

    def github_status(self, full_name: str) -> tuple[bool, str | None]:
        if not self._gh_available():
            return False, None
        result = self._run(["gh", "repo", "view", full_name, "--json", "url", "-q", ".url"])
        if result.returncode == 0:
            url = result.stdout.strip() or f"https://github.com/{full_name}"
            return True, url
        return False, None

    def local_status(self, path: str | Path, full_name: str) -> dict[str, Any]:
        root = Path(path)
        exists = root.exists()
        is_git = (root / ".git").exists() if exists else False
        origin = None
        if is_git:
            result = self._run(["git", "remote", "get-url", "origin"], cwd=root)
            if result.returncode == 0:
                origin = result.stdout.strip() or None
        expected = self._expected_origin(full_name)
        normalized = (origin or "").rstrip("/")
        origin_matches = normalized in {x.rstrip("/") for x in expected}
        stage_files = len(list((root / "stages").glob("*.yaml"))) if (root / "stages").exists() else 0
        return {
            "exists": exists,
            "is_git": is_git,
            "origin": origin,
            "origin_matches": origin_matches,
            "stage_files": stage_files,
            "project_yaml_exists": (root / "project.yaml").exists(),
        }

    def preflight(self, proposal: dict[str, Any], execution_plan: dict[str, Any]) -> PreflightResult:
        session_id = str(proposal.get("session_id") or "runtime")
        self.events.emit(session_id=session_id, stage_id="STAGE-001", source="RUNTIME", event_type="PREFLIGHT_START", action="project_preflight", status="STARTED", project_id=proposal.get("project_id"), details={"repository": self._github_full_name(proposal), "local_directory": proposal.get("local_directory")})
        full_name = self._github_full_name(proposal)
        github_exists, github_url = self.github_status(full_name)
        local = self.local_status(proposal["local_directory"], full_name)
        conflicts: list[str] = []
        allowed: list[str] = []

        github_mode = execution_plan.get("github_mode", "CREATE_NEW")
        local_mode = execution_plan.get("local_mode", "CREATE_NEW")
        git_mode = execution_plan.get("git_mode", "INIT_AND_BIND")

        if github_mode == "CREATE_NEW" and github_exists:
            conflicts.append("GITHUB_REPOSITORY_ALREADY_EXISTS")
            allowed += ["BIND_EXISTING", "RENAME_REPOSITORY"]
        elif github_mode == "BIND_EXISTING" and not github_exists:
            conflicts.append("GITHUB_REPOSITORY_NOT_FOUND")
            allowed += ["CREATE_NEW", "CHANGE_REPOSITORY"]

        if local_mode == "CREATE_NEW" and local["exists"]:
            conflicts.append("LOCAL_DIRECTORY_ALREADY_EXISTS")
            allowed += ["USE_EXISTING", "CHANGE_LOCAL_DIRECTORY"]
        elif local_mode == "USE_EXISTING" and not local["exists"]:
            conflicts.append("LOCAL_DIRECTORY_NOT_FOUND")
            allowed += ["CREATE_NEW", "CHANGE_LOCAL_DIRECTORY"]

        if local["is_git"] and local["origin"] and not local["origin_matches"]:
            conflicts.append("LOCAL_GIT_ORIGIN_MISMATCH")
            allowed += ["CHANGE_LOCAL_DIRECTORY", "REVIEW_EXISTING_ORIGIN"]

        if git_mode == "CLONE" and local["exists"]:
            conflicts.append("CLONE_TARGET_ALREADY_EXISTS")
            allowed += ["USE_EXISTING", "CHANGE_LOCAL_DIRECTORY"]

        if not self._gh_available():
            conflicts.append("GH_CLI_NOT_AVAILABLE_OR_NOT_AUTHENTICATED")
            allowed += ["INSTALL_OR_AUTHENTICATE_GH"]

        result = PreflightResult(
            github_repository=full_name,
            github_exists=github_exists,
            github_url=github_url,
            local_directory=str(proposal["local_directory"]),
            local_exists=local["exists"],
            local_is_git=local["is_git"],
            local_origin=local["origin"],
            local_origin_matches=local["origin_matches"],
            scaffold_stage_files=local["stage_files"],
            project_yaml_exists=local["project_yaml_exists"],
            conflicts=sorted(set(conflicts)),
            allowed_actions=sorted(set(allowed)),
        )
        self.events.emit(session_id=session_id, stage_id="STAGE-001", source="RUNTIME", event_type="PREFLIGHT_RESULT", action="project_preflight", status="PASS" if not result.conflicts else "HOLD", project_id=proposal.get("project_id"), details=result.to_dict())
        return result

    def execute(
        self,
        proposal: dict[str, Any],
        execution_plan: dict[str, Any],
        *,
        approved: bool,
    ) -> dict[str, Any]:
        if not approved:
            raise PermissionError("STAGE-001 execution requires explicit human approval")
        session_id = str(proposal.get("session_id") or "runtime")
        self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GATE", event_type="GATE_DECISION", action="approve_execution", status="APPROVED", project_id=proposal.get("project_id"))
        preflight = self.preflight(proposal, execution_plan)
        if preflight.conflicts:
            self.events.emit(session_id=session_id, stage_id="STAGE-001", source="RUNTIME", event_type="EXECUTION_STEP", action="execution_blocked_by_preflight", status="HOLD", project_id=proposal.get("project_id"), details=preflight.to_dict())
            return {
                "status": "BLOCKED",
                "reason": "PREFLIGHT_CONFLICT",
                "preflight": preflight.to_dict(),
            }

        full_name = self._github_full_name(proposal)
        local_root = Path(proposal["local_directory"])
        github_mode = execution_plan.get("github_mode", "CREATE_NEW")
        local_mode = execution_plan.get("local_mode", "CREATE_NEW")
        git_mode = execution_plan.get("git_mode", "INIT_AND_BIND")
        visibility = proposal.get("visibility", "private")

        steps: list[dict[str, Any]] = []
        self.events.emit(session_id=session_id, stage_id="STAGE-001", source="RUNTIME", event_type="EXECUTION_START", action="project_initialization", status="STARTED", project_id=proposal.get("project_id"), details={"execution_plan": execution_plan})

        if github_mode == "CREATE_NEW":
            cmd = ["gh", "repo", "create", full_name, f"--{visibility}"]
            result = self._run(cmd)
            steps.append({"step": "create_github", "returncode": result.returncode, "stderr": result.stderr.strip()})
            self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GITHUB", event_type="GITHUB_OPERATION", action="create_repository", status="PASS" if result.returncode == 0 else "ERROR", project_id=proposal.get("project_id"), target=full_name, details={"returncode": result.returncode, "stderr": result.stderr.strip()})
            if result.returncode != 0:
                return {"status": "FAIL", "steps": steps, "preflight": preflight.to_dict()}

        if git_mode == "CLONE":
            result = self._run(["gh", "repo", "clone", full_name, str(local_root)])
            steps.append({"step": "clone", "returncode": result.returncode, "stderr": result.stderr.strip()})
            if result.returncode != 0:
                return {"status": "FAIL", "steps": steps, "preflight": preflight.to_dict()}
            generator_root = local_root
            if not (generator_root / "project.yaml").exists():
                self._populate_existing_root(generator_root, proposal)
        else:
            if local_mode == "CREATE_NEW":
                ProjectScaffoldGenerator().create(
                    local_root,
                    project_id=proposal["project_id"],
                    public_name=proposal["public_name"],
                    code_name=proposal["code_name"],
                    approved=True,
                )
                steps.append({"step": "create_scaffold", "returncode": 0})
                self.events.emit(session_id=session_id, stage_id="STAGE-001", source="FILESYSTEM", event_type="DIRECTORY_CREATED", action="create_project_scaffold", status="PASS", project_id=proposal.get("project_id"), target=str(local_root), details={"stage_files":101})
            else:
                self._populate_existing_root(local_root, proposal)
                steps.append({"step": "populate_existing_root", "returncode": 0})

            if not (local_root / ".git").exists():
                result = self._run(["git", "init", "-b", proposal.get("default_branch", "main")], cwd=local_root)
                steps.append({"step": "git_init", "returncode": result.returncode, "stderr": result.stderr.strip()})
                self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GIT", event_type="GIT_COMMAND", action="git_init", status="PASS" if result.returncode == 0 else "ERROR", project_id=proposal.get("project_id"), target=str(local_root), details={"returncode":result.returncode})
                if result.returncode != 0:
                    return {"status": "FAIL", "steps": steps, "preflight": preflight.to_dict()}

            expected_https = self._expected_origin(full_name)[0]
            current = self._run(["git", "remote", "get-url", "origin"], cwd=local_root)
            if current.returncode != 0:
                result = self._run(["git", "remote", "add", "origin", expected_https], cwd=local_root)
            else:
                result = self._run(["git", "remote", "set-url", "origin", expected_https], cwd=local_root)
            steps.append({"step": "bind_origin", "returncode": result.returncode, "stderr": result.stderr.strip()})
            self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GIT", event_type="GIT_COMMAND", action="bind_origin", status="PASS" if result.returncode == 0 else "ERROR", project_id=proposal.get("project_id"), target=expected_https, details={"returncode":result.returncode})
            if result.returncode != 0:
                return {"status": "FAIL", "steps": steps, "preflight": preflight.to_dict()}

        evidence_dir = local_root / "evidence" / "stage_001"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "execution_plan.json").write_text(
            json.dumps({"proposal": proposal, "execution_plan": execution_plan}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if execution_plan.get("initial_commit", True):
            self._run(["git", "add", "."], cwd=local_root)
            commit = self._run(["git", "commit", "-m", "stage-001: initialize canonical project scaffold"], cwd=local_root)
            steps.append({"step": "initial_commit", "returncode": commit.returncode, "stderr": commit.stderr.strip()})
            self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GIT", event_type="GIT_COMMAND", action="initial_commit", status="PASS" if commit.returncode == 0 else "ERROR", project_id=proposal.get("project_id"), details={"returncode":commit.returncode})
            if commit.returncode == 0:
                push = self._run(["git", "push", "-u", "origin", proposal.get("default_branch", "main")], cwd=local_root)
                steps.append({"step": "push", "returncode": push.returncode, "stderr": push.stderr.strip()})
                self.events.emit(session_id=session_id, stage_id="STAGE-001", source="GIT", event_type="GIT_COMMAND", action="git_push", status="PASS" if push.returncode == 0 else "ERROR", project_id=proposal.get("project_id"), details={"returncode":push.returncode})

        verification = self.verify(proposal)
        (evidence_dir / "verification.json").write_text(
            json.dumps(verification, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        verification["evidence_written"] = True
        verification["status"] = "PASS" if all(
            verification[k]
            for k in (
                "github_repository_exists",
                "local_directory_exists",
                "git_repository_initialized",
                "git_remote_matches",
                "stage_files_101",
                "project_yaml_exists",
                "initial_commit_exists",
            )
        ) else "HOLD"
        self.events.emit(session_id=session_id, stage_id="STAGE-001", source="TEST", event_type="TEST_RESULT", action="stage_001_verification", status=verification["status"], project_id=proposal.get("project_id"), details=verification)
        return {"status": verification["status"], "steps": steps, "verification": verification}

    def _populate_existing_root(self, root: Path, proposal: dict[str, Any]) -> None:
        if not root.exists():
            root.mkdir(parents=True, exist_ok=False)
        if any(root.iterdir()) and not (root / "project.yaml").exists():
            raise FileExistsError("Existing local directory is non-empty and is not a recognized NEXUS project")
        if not (root / "project.yaml").exists():
            temp = root.parent / f".{root.name}.nexus_scaffold_tmp"
            if temp.exists():
                raise FileExistsError(str(temp))
            ProjectScaffoldGenerator().create(
                temp,
                project_id=proposal["project_id"],
                public_name=proposal["public_name"],
                code_name=proposal["code_name"],
                approved=True,
            )
            for item in temp.iterdir():
                item.rename(root / item.name)
            temp.rmdir()

    def verify(self, proposal: dict[str, Any]) -> dict[str, Any]:
        full_name = self._github_full_name(proposal)
        github_exists, github_url = self.github_status(full_name)
        local = self.local_status(proposal["local_directory"], full_name)
        root = Path(proposal["local_directory"])
        commit = False
        if local["is_git"]:
            result = self._run(["git", "rev-parse", "HEAD"], cwd=root)
            commit = result.returncode == 0
        return {
            "github_repository_exists": github_exists,
            "github_url": github_url or f"https://github.com/{full_name}",
            "local_directory_exists": local["exists"],
            "local_directory": str(root),
            "git_repository_initialized": local["is_git"],
            "git_remote_matches": local["origin_matches"],
            "git_remote": local["origin"],
            "stage_files_101": local["stage_files"] == 101,
            "stage_file_count": local["stage_files"],
            "project_yaml_exists": local["project_yaml_exists"],
            "initial_commit_exists": commit,
            "evidence_written": (root / "evidence" / "stage_001" / "execution_plan.json").exists(),
        }

    def open_local(self, path: str | Path) -> None:
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(str(target))
        if os.name == "nt":
            os.startfile(str(target))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            self._run(["open", str(target)])
        else:
            self._run(["xdg-open", str(target)])

    @staticmethod
    def open_github(url: str) -> None:
        webbrowser.open(url)
