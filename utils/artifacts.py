"""Persistent project artifacts and safe validation helpers for the studio pipeline."""

from __future__ import annotations

import ast
import json
import re
import time
from pathlib import Path
from typing import Any

from utils.validator import PhaseValidator


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
            {"concept": concept, "created_at": timestamp, "artifacts": []},
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

    def save_artifact(self, agent_name: str, artifact_name: str, content: str) -> str:
        """Save a validated agent deliverable. Returns revision guidance when validation fails."""
        if not content or not content.strip():
            return "VALIDATION_FAILED: artifact content is empty. Revise it and call save_artifact again."
        passed = PhaseValidator.validate_metrics(agent_name, content)
        validation_file = self.validation_path / f"{self._safe_name(agent_name)}-{self._safe_name(artifact_name)}.json"
        self._write_json(
            validation_file,
            {"agent": agent_name, "artifact": artifact_name, "passed": passed, "checked_at": time.time()},
        )
        if not passed:
            return "VALIDATION_FAILED: remove unresolved errors or conflicts, revise the deliverable, then call save_artifact again."

        filename = f"{self._safe_name(agent_name)}-{self._safe_name(artifact_name)}.md"
        path = self.artifacts_path / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        self._record_manifest({"agent": agent_name, "artifact": artifact_name, "path": str(path.relative_to(self.path))})
        return f"VALIDATION_PASSED: saved {path}"

    def read_artifacts(self) -> str:
        """Return upstream deliverables for an agent handoff, newest files last."""
        files = sorted(self.artifacts_path.glob("*.md"))
        if not files:
            return "No upstream artifacts are available yet. Work from the user brief."
        sections = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            sections.append(f"## {path.name}\n{text[:12000]}")
        return "\n\n".join(sections)

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
