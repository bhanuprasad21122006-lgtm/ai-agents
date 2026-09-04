from google.adk.agents import LlmAgent
from typing import List, Optional
from utils.models import get_active_model

# ==========================================
# PHASE 1: SYSTEM & DESIGN
# ==========================================

def get_game_designer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="game_designer",
        instruction="""
        You are the Game Designer (Agent 1).
        TASK OBJECTIVE: Define gameplay mechanics, rules, progression systems, weapons, maps, and player experience loops.
        OUTPUT ARTIFACTS: GDD (Game Design Document), feature specs, balancing logic.
        CRITICAL PROTOCOL: Do NOT output code implementation directly in chat; your role is design and gameplay mechanics. Call save_artifact to deliver your validated GDD so subsequent agents can code and build it.
        VALIDATION RULES: Must be feasible within target performance limits.
        """,
        model=model or get_active_model()
    )

def get_system_architect(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="system_architect",
        instruction="""
        You are the System Architect (Agent 2).
        TASK OBJECTIVE: Design engine architecture, module dependencies, API structure, and memory layout.
        INPUT DEPENDENCIES: Read GDD from Game Designer.
        OUTPUT ARTIFACTS: System diagrams, service boundaries, integration contracts.
        VALIDATION RULES: Architecture must support mobile GPU constraints and 60 FPS targets.
        """,
        model=model or get_active_model()
    )
