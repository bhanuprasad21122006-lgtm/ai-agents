import os
from pathlib import Path
from google.adk.agents import LlmAgent

_workspace = None


def set_project_workspace(workspace) -> None:
    """Configure the durable output location for the current orchestration run."""
    global _workspace
    _workspace = workspace

def write_game_code(filename: str, python_code: str) -> str:
    """Saves final playable game code into the current project's persistent game folder.
    Args:
        filename: name of the python file (e.g. game.py)
        python_code: the full, runnable python source code for the generated game
    """
    if _workspace is None:
        return "VALIDATION_FAILED: project workspace is not configured."
    result = _workspace.save_game_code(filename, python_code)
    if result.startswith("VALIDATION_PASSED"):
        path = _workspace.games_path / (Path(filename).stem + ".py")
        os.environ["GENERATED_GAME_PATH"] = str(path)
    return result

# ==========================================
# PHASE 2: CORE SYSTEMS
# ==========================================

def get_gameplay_programmer() -> LlmAgent:
    return LlmAgent(
        name="gameplay_programmer",
        instruction="""
        You are the Gameplay Programmer (Agent 3).
        TASK OBJECTIVE: Implement the entire game code (logic, graphics, controls) in Python.
        INPUT DEPENDENCIES: Read the target game requested by the user.
        CRITICAL RULE: You MUST use the `write_game_code` tool to output your fully playable Python script (like pygame or turtle) so the user can play it locally! Do not just write text, use the tool.
        """,
        tools=[write_game_code],
        model="gemini-2.5-flash"
    )

def get_ai_engineer() -> LlmAgent:
    return LlmAgent(
        name="ai_engineer",
        instruction="""
        You are the AI Engineer (Agent 5).
        TASK OBJECTIVE: Create NPC logic, bot behavior trees, pathfinding systems, adaptive difficulty modules.
        OUTPUT ARTIFACTS: Behavior trees, state machines, navigation meshes.
        """,
        model="gemini-2.5-flash"
    )

def get_level_designer() -> LlmAgent:
    return LlmAgent(
        name="level_designer",
        instruction="""
        You are the Level Designer (Agent 8).
        TASK OBJECTIVE: Design terrain, cover systems, spawn points, map flow, choke points.
        OUTPUT ARTIFACTS: Map layouts and environment logic.
        """,
        model="gemini-2.5-flash"
    )
