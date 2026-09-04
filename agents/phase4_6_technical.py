from google.adk.agents import LlmAgent
from typing import Optional
from utils.models import get_active_model

# ==========================================
# PHASE 4-6: TECHNICAL & ASSETS
# ==========================================

def get_network_engineer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="network_engineer",
        instruction="""
        You are the Network Engineer (Agent 4).
        TASK OBJECTIVE: Implement matchmaking, synchronization models, latency handling, packet compression, rollback logic.
        OUTPUT ARTIFACTS: Multiplayer protocol logic.
        VALIDATION RULES: Multiplayer sync integrity.
        """,
        model=model or get_active_model()
    )

def get_asset_manager(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="asset_manager",
        instruction="""
        You are the Asset Manager (Agent 10).
        TASK OBJECTIVE: Coordinate 3D models, textures, animation pipelines.
        OUTPUT ARTIFACTS: Asset indexing and compression rules.
        """,
        model=model or get_active_model()
    )

def get_test_engineer(model: Optional[str] = None) -> LlmAgent:
    return LlmAgent(
        name="test_engineer",
        instruction="""
        You are the Test Engineer (Agent 11).
        TASK OBJECTIVE: Run automated gameplay testing, regression tests, exploit detection.
        OUTPUT ARTIFACTS: Bug reports and stability metrics.
        """,
        model=model or get_active_model()
    )
