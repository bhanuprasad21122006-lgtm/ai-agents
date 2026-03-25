from google.adk.agents import LlmAgent
from typing import List

# ==========================================
# PHASE 1: SYSTEM & DESIGN
# ==========================================

def get_game_designer() -> LlmAgent:
    return LlmAgent(
        name="game_designer",
        instruction="""
        You are the Game Designer (Agent 1).
        TASK OBJECTIVE: Define gameplay mechanics, rules, progression systems, weapons, maps, and player experience loops.
        OUTPUT ARTIFACTS: GDD (Game Design Document), feature specs, balancing logic.
        VALIDATION RULES: Must be feasible within mobile performance limits.
        """,
        model="gemini-flash-latest"
    )

def get_system_architect() -> LlmAgent:
    return LlmAgent(
        name="system_architect",
        instruction="""
        You are the System Architect (Agent 2).
        TASK OBJECTIVE: Design engine architecture, module dependencies, API structure, and memory layout.
        INPUT DEPENDENCIES: Read GDD from Game Designer.
        OUTPUT ARTIFACTS: System diagrams, service boundaries, integration contracts.
        VALIDATION RULES: Architecture must support mobile GPU constraints and 60 FPS targets.
        """,
        model="gemini-flash-latest"
    )
