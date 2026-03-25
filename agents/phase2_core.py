import os
from google.adk.agents import LlmAgent

def write_game_code(filename: str, python_code: str) -> str:
    """Saves the final playable game code into the 'generated_game' folder. Use this tool heavily to output code!
    Args:
        filename: name of the python file (e.g. game.py)
        python_code: the full, runnable python source code for the generated game
    """
    os.makedirs("generated_game", exist_ok=True)
    filepath = os.path.join("generated_game", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(python_code)
    return f"Successfully saved runnable code to {filepath}"

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
        model="gemini-flash-latest"
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
