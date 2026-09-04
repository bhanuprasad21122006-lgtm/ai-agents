"""Persistent project artifacts and safe validation helpers for the studio pipeline."""

from __future__ import annotations

import ast
import json
import re
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from utils.validator import PhaseValidator


class ArtifactPayload(BaseModel):
    """Minimum contract required for every role deliverable."""

    title: str = Field(min_length=3, max_length=160)
    summary: str = Field(min_length=20)
    decisions: list[str] = Field(min_length=1)
    dependencies: list[str]
    risks: list[str]
    next_steps: list[str] = Field(min_length=1)


REQUIRED_AGENTS = (
    "game_designer", "system_architect", "gameplay_programmer", "ai_engineer",
    "level_designer", "graphics_engineer", "sound_engineer", "ui_ux_designer",
    "network_engineer", "asset_manager", "test_engineer", "debugging_specialist",
    "performance_optimizer", "live_ops_engineer",
)

PREREQUISITES = {
    "system_architect": ("game_designer",),
    "gameplay_programmer": ("system_architect",),
    "ai_engineer": ("gameplay_programmer",),
    "level_designer": ("gameplay_programmer",),
    "graphics_engineer": ("system_architect",),
    "sound_engineer": ("gameplay_programmer",),
    "ui_ux_designer": ("gameplay_programmer",),
    "network_engineer": ("system_architect",),
    "asset_manager": ("graphics_engineer",),
    "test_engineer": ("gameplay_programmer", "network_engineer"),
    "debugging_specialist": ("test_engineer",),
    "performance_optimizer": ("debugging_specialist",),
    "live_ops_engineer": ("performance_optimizer",),
}


class ProjectWorkspace:
    """Stores all agent deliverables in one durable, self-contained project folder."""

    def __init__(self, concept: str, root: str | Path = "generated_game") -> None:
        slug = re.sub(r"[^a-z0-9]+", "-", concept.lower()).strip("-")[:48] or "game"
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.path = Path(root) / f"{slug}-{timestamp}"
        self.artifacts_path = self.path / "artifacts"
        self.games_path = self.path / "game"
        self.validation_path = self.path / "validation"
        for directory in (self.artifacts_path, self.games_path, self.validation_path):
            directory.mkdir(parents=True, exist_ok=True)
        self._write_json(
            self.path / "manifest.json",
            {"concept": concept, "created_at": timestamp, "artifacts": [], "events": []},
        )

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _safe_name(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")[:80] or "artifact"

    def _record_manifest(self, item: dict[str, str]) -> None:
        manifest_file = self.path / "manifest.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest["artifacts"].append(item)
        self._write_json(manifest_file, manifest)

    def record_event(self, event: str, detail: str = "") -> None:
        manifest_file = self.path / "manifest.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest["events"].append({"at": time.time(), "event": event, "detail": detail})
        self._write_json(manifest_file, manifest)

    def has_agent_artifact(self, agent_name: str) -> bool:
        manifest = json.loads((self.path / "manifest.json").read_text(encoding="utf-8"))
        return any(item["agent"] == agent_name for item in manifest["artifacts"])

    def missing_agents(self) -> list[str]:
        return [agent for agent in REQUIRED_AGENTS if not self.has_agent_artifact(agent)]

    def save_artifact(self, agent_name: str, artifact_name: str, content: str) -> str:
        """Save a JSON deliverable. Failed validation must be revised and submitted again."""
        if not content or not content.strip():
            return "VALIDATION_FAILED: artifact content is empty. Revise it and call save_artifact again."
        missing_prerequisites = [agent for agent in PREREQUISITES.get(agent_name, ()) if not self.has_agent_artifact(agent)]
        if missing_prerequisites:
            return f"VALIDATION_FAILED: phase gate is closed. Required artifacts are missing from: {', '.join(missing_prerequisites)}."
        try:
            payload = ArtifactPayload.model_validate_json(content)
        except ValidationError as exc:
            return f"VALIDATION_FAILED: use valid JSON with title, summary, decisions, dependencies, risks, and next_steps. Details: {exc.errors()[0]['msg']}"
        passed = PhaseValidator.validate_metrics(agent_name, payload.summary)
        validation_file = self.validation_path / f"{self._safe_name(agent_name)}-{self._safe_name(artifact_name)}.json"
        self._write_json(
            validation_file,
            {"agent": agent_name, "artifact": artifact_name, "passed": passed, "checked_at": time.time(), "schema": "ArtifactPayload"},
        )
        if not passed:
            return "VALIDATION_FAILED: remove unresolved errors or conflicts, revise the deliverable, then call save_artifact again."

        filename = f"{self._safe_name(agent_name)}-{self._safe_name(artifact_name)}.json"
        path = self.artifacts_path / filename
        path.write_text(payload.model_dump_json(indent=2) + "\n", encoding="utf-8")
        self._record_manifest({"agent": agent_name, "artifact": artifact_name, "path": str(path.relative_to(self.path))})
        return f"VALIDATION_PASSED: saved {path}"

    def read_artifacts(self) -> str:
        """Return upstream deliverables for an agent handoff, newest files last."""
        files = sorted(self.artifacts_path.glob("*.json"))
        if not files:
            return "No upstream artifacts are available yet. Work from the user brief."
        sections = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            sections.append(f"## {path.name}\n{text[:12000]}")
        return "\n\n".join(sections)

    def save_captured_output(self, agent_name: str, output: str) -> bool:
        """Persist a final model response only after automated attempts are exhausted."""
        if not output or not output.strip():
            return False
        fallback = ArtifactPayload(
            title=f"Fallback output from {agent_name}",
            summary=output.strip()[:12000],
            decisions=["Captured because the agent did not call the artifact tool."],
            dependencies=[],
            risks=["This is an unverified fallback artifact."],
            next_steps=["Review and replace with a role-specific validated artifact."],
        )
        path = self.artifacts_path / f"{self._safe_name(agent_name)}-fallback.json"
        path.write_text(fallback.model_dump_json(indent=2) + "\n", encoding="utf-8")
        self._record_manifest({"agent": agent_name, "artifact": "fallback_output", "path": str(path.relative_to(self.path))})
        self.record_event("fallback_artifact", agent_name)
        return True

    def write_run_report(self, attempts: int, timed_out: bool = False) -> dict[str, Any]:
        missing = self.missing_agents()
        manifest = json.loads((self.path / "manifest.json").read_text(encoding="utf-8"))
        fallback_agents = [item["agent"] for item in manifest["artifacts"] if item["artifact"] == "fallback_output"]
        report = {
            "attempts": attempts,
            "timed_out": timed_out,
            "required_agents": list(REQUIRED_AGENTS),
            "missing_agents": missing,
            "fallback_agents": fallback_agents,
            "status": "passed" if not missing and not fallback_agents and not timed_out else "needs_review",
        }
        self._write_json(self.validation_path / "run-report.json", report)
        return report

    def save_game_code(self, filename: str, python_code: str) -> str:
        """Persist generated Python code and require a syntax check before accepting it."""
        safe_filename = self._safe_name(Path(filename).stem) + ".py"
        try:
            ast.parse(python_code)
        except SyntaxError as exc:
            return f"VALIDATION_FAILED: generated Python has a syntax error at line {exc.lineno}: {exc.msg}. Fix it and call write_game_code again."
        path = self.games_path / safe_filename
        path.write_text(python_code, encoding="utf-8")
        self._record_manifest({"agent": "gameplay_programmer", "artifact": "playable_game", "path": str(path.relative_to(self.path))})
        return f"VALIDATION_PASSED: saved runnable Python game to {path}"

    def validate_generated_games(self) -> list[str]:
        """Perform a non-executing AST smoke test; never run untrusted generated code automatically."""
        results = []
        for path in sorted(self.games_path.glob("*.py")):
            try:
                ast.parse(path.read_text(encoding="utf-8"))
                result = f"PASS: {path.name} parses successfully"
            except SyntaxError as exc:
                result = f"FAIL: {path.name}, line {exc.lineno}: {exc.msg}"
            results.append(result)
        report = self.validation_path / "generated-game-smoke-test.txt"
        report.write_text("\n".join(results) or "No generated Python game was saved.\n", encoding="utf-8")
        return results
