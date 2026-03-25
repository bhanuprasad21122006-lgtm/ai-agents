from google.adk.agents import LlmAgent

# ==========================================
# PHASE 3: ARTS & UX
# ==========================================

def get_graphics_engineer() -> LlmAgent:
    return LlmAgent(
        name="graphics_engineer",
        instruction="""
        You are the Graphics Engineer (Agent 6).
        TASK OBJECTIVE: Implement shaders, lighting models, rendering optimizations, LOD systems.
        OUTPUT ARTIFACTS: Rendering pipeline configs.
        VALIDATION RULES: Optimization for mobile GPUs.
        """,
        model="gemini-flash-latest"
    )

def get_ui_ux_designer() -> LlmAgent:
    return LlmAgent(
        name="ui_ux_designer",
        instruction="""
        You are the UI/UX Designer (Agent 7).
        TASK OBJECTIVE: Create menus, HUD systems, interaction flow, accessibility features.
        OUTPUT ARTIFACTS: UI wireframes and UI logic specifications.
        """,
        model="gemini-flash-latest"
    )

def get_sound_engineer() -> LlmAgent:
    return LlmAgent(
        name="sound_engineer",
        instruction="""
        You are the Sound Engineer (Agent 9).
        TASK OBJECTIVE: Implement spatial audio logic, weapon sound layers, ambient effects.
        OUTPUT ARTIFACTS: Audio trigger systems.
        """,
        model="gemini-flash-latest"
    )
