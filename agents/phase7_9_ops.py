from google.adk.agents import LlmAgent

# ==========================================
# PHASE 7-9: OPS & OPTIMIZATION
# ==========================================

def get_debugging_specialist() -> LlmAgent:
    return LlmAgent(
        name="debugging_specialist",
        instruction="""
        You are the Debugging Specialist (Agent 12).
        TASK OBJECTIVE: Locate runtime faults, memory leaks, sync errors, performance bottlenecks.
        INPUT DEPENDENCIES: Read bug reports from Test Engineer.
        OUTPUT ARTIFACTS: Patch suggestions.
        """,
        model="gemini-flash-latest"
    )

def get_performance_optimizer() -> LlmAgent:
    return LlmAgent(
        name="performance_optimizer",
        instruction="""
        You are the Performance Optimizer (Agent 13).
        TASK OBJECTIVE: Maintain FPS targets, GPU budgets, RAM usage limits.
        OUTPUT ARTIFACTS: Optimization reports.
        VALIDATION RULES: 60 FPS performance targets.
        """,
        model="gemini-flash-latest"
    )

def get_live_ops_engineer() -> LlmAgent:
    return LlmAgent(
        name="live_ops_engineer",
        instruction="""
        You are the Live Ops Engineer (Agent 14).
        TASK OBJECTIVE: Handle updates, analytics hooks, telemetry, patch rollout strategy.
        OUTPUT ARTIFACTS: Deployment pipelines.
        """,
        model="gemini-flash-latest"
    )
