from google.adk.agents import LlmAgent
from typing import Optional
from utils.models import get_active_model

# ==========================================
# PHASE 3: ARTS & UX
# ==========================================

def get_graphics_engineer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="graphics_engineer",
        instruction="""
        You are the Graphics Engineer (Agent 6).
        TASK OBJECTIVE: Implement shaders, lighting models, rendering optimizations, LOD systems.
        OUTPUT ARTIFACTS: Rendering pipeline configs.
        VALIDATION RULES: Optimization for mobile GPUs.
        """,
        model=model or get_active_model()
    )

def get_ui_ux_designer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="ui_ux_designer",
        instruction="""
        You are the UI/UX Designer (Agent 7).
        TASK OBJECTIVE: Create menus, HUD systems, interaction flow, accessibility features.
        OUTPUT ARTIFACTS: UI wireframes and UI logic specifications.
        """,
        model=model or get_active_model()
    )

def get_sound_engineer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="sound_engineer",
        instruction="""
        You are the Sound Engineer (Agent 9).
        TASK OBJECTIVE: Implement spatial audio logic, weapon sound layers, ambient effects.
        OUTPUT ARTIFACTS: Audio trigger systems.
        """,
        model=model or get_active_model()
    )
