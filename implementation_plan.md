# AAA Game Studio Multi-Agent Orchestrator

This document outlines the implementation plan for building a 14-agent system simulating an AAA game studio pipeline using Python, Google ADK (`google-adk`), and Model Context Protocol (MCP).

## User Review Required

- Please review the planned file structure and dependencies to ensure they align with your desktop setup constraints.
- You'll need an active Gemini API key configured in the `.env` file since ADK runs on Gemini 3.1 Flash (or the available Gemini model).
- You'll need to install standard MCP servers (e.g., `mcp-server-filesystem` or `mcp-server-brave-search`) separately if you want agents to interact with real files/web natively, though we will scaffold the MCP client connections.

## Proposed Changes

### Configuration
#### [NEW] `requirements.txt`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/requirements.txt)
Will contain required packages: `google-adk`, `python-dotenv`, `mcp`.

#### [NEW] `.env`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/.env)
Template for API keys (e.g., `GEMINI_API_KEY`, MCP configuration paths).

---

### Core Automation & Utilities
#### [NEW] `main.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/main.py)
The central orchestrator script. This sets up the Google ADK environment, initializes the 14 agents, links them in a Phase 1-9 sequential/parallel pipeline, and triggers the generation loop.

#### [NEW] `utils/mcp_client.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/utils/mcp_client.py)
Provides a bridge for ADK agents to utilize local MCP servers for extended capabilities (like writing artifacts to disk).

#### [NEW] `utils/validator.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/utils/validator.py)
Contains validation logic ensuring output memory constraints, multiplayer sync integrity, and performance thresholds are theoretically met before passing to the next agent.

---

### Agent Modules
The 14 special agents will be defined using ADK (`LlmAgent`) with specific instructions and output formatting. We will group them or create individual files for modularity:

#### [NEW] `agents/phase1_design.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/agents/phase1_design.py)
Agent 1 (Game Designer), Agent 2 (System Architect).

#### [NEW] `agents/phase2_core.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/agents/phase2_core.py)
Agent 3 (Gameplay Programmer), Agent 5 (AI Engineer), Agent 8 (Level Designer).

#### [NEW] `agents/phase3_arts.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/agents/phase3_arts.py)
Agent 6 (Graphics Engineer), Agent 9 (Sound Engineer), Agent 7 (UI/UX Designer).

#### [NEW] `agents/phase4_6_technical.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/agents/phase4_6_technical.py)
Agent 4 (Network Engineer), Agent 10 (Asset Manager), Agent 11 (Test Engineer).

#### [NEW] `agents/phase7_9_ops.py`(file:///c:/Users/bhanu/OneDrive/Desktop/ai_agent/agents/phase7_9_ops.py)
Agent 12 (Debugging Specialist), Agent 13 (Performance Optimizer), Agent 14 (Live Ops Engineer).

---

## Verification Plan

### Automated Tests
- Run `python main.py --dry-run` to ensure the DAG (Directed Acyclic Graph) of agent execution is properly initialized without crashing.
- Execute a test run where the 14 agents generate a small text-based artifact pipeline.

### Manual Verification
- We will verify that artifacts are accurately saved to disk for each phase.
- We will ensure that the orchestrator properly handles a dummy "game concept" from end-to-end.
- Instructions will be provided for you (the student) to quickly run the whole pipeline on your machine using `run.bat`.
