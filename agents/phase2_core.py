import os
from pathlib import Path
from typing import Optional
from google.adk.agents import LlmAgent
from utils.models import get_active_model

_workspace = None


def set_project_workspace(workspace) -> None:
    """Configure the durable output location for the current orchestration run."""
    global _workspace
    _workspace = workspace

def write_game_code(filename: str, code: str) -> str:
    """Saves final playable game code into the current project's persistent game folder.
    Args:
        filename: name of the file (e.g. game.py, index.html, style.css, script.js)
        code: the full, runnable source code for the game
    """
    if _workspace is None:
        return "VALIDATION_FAILED: project workspace is not configured."
    result = _workspace.save_game_code(filename, code)
    if result.startswith("VALIDATION_PASSED"):
        suffix = Path(filename).suffix.lower()
        if suffix in {".html", ".htm", ".js", ".css"}:
            path = _workspace.games_path / (Path(filename).stem + suffix)
        else:
            path = _workspace.games_path / (Path(filename).stem + ".py")
        os.environ["GENERATED_GAME_PATH"] = str(path)
    return result

# ==========================================
# PHASE 2: CORE SYSTEMS
# ==========================================

def get_gameplay_programmer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="gameplay_programmer",
        instruction="""
        You are the Gameplay Programmer (Agent 3).
        TASK OBJECTIVE: Implement the complete game code (logic, graphics, controls) in Python (e.g. pygame/turtle) or Web (HTML/CSS/JS) matching the user's brief.
        INPUT DEPENDENCIES: Read the target game requested by the user and upstream design specs.
        CRITICAL RULE: You MUST call the `write_game_code` tool to output your fully playable code files (e.g. index.html, style.css, script.js, or game.py) so the user can play it immediately! Do not just write code in chat, you must call the tool.
        """,
        tools=[write_game_code],
        model=model or get_active_model()
    )

def get_ai_engineer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="ai_engineer",
        instruction="""
        You are the AI Engineer (Agent 5).
        TASK OBJECTIVE: Create NPC logic, bot behavior trees, pathfinding systems, adaptive difficulty modules.
        OUTPUT ARTIFACTS: Behavior trees, state machines, navigation meshes.
        """,
        model=model or get_active_model()
    )

def get_level_designer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="level_designer",
        instruction="""
        You are the Level Designer (Agent 8).
        TASK OBJECTIVE: Design terrain, cover systems, spawn points, map flow, choke points.
        OUTPUT ARTIFACTS: Map layouts and environment logic.
        """,
        model=model or get_active_model()
    )
