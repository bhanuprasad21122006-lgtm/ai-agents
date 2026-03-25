# Walkthrough: AAA Game Studio AI Agent

We have successfully developed a fully structured, locally-runnable multi-agent orchestrator simulating a professional AAA game development studio.

## What was built

We orchestrated **14 specialized AI agents**, structured according to the prompt's requirements, into a robust architectural pipeline:

1.  **Project Foundation** 
    -   `requirements.txt` with dependencies mapping `google-adk`, `mcp`, and `python-dotenv`.
    -   `.env` template created for the `GEMINI_API_KEY`.
2.  **Phase 1-9 Agent Development (`agents/`)**
    -   **Phase 1 (Design & Architecture):** Game Designer, System Architect.
    -   **Phase 2 (Core Logic):** Gameplay Programmer, AI Engineer, Level Designer.
    -   **Phase 3 (Arts & UX):** Graphics Engineer, UI/UX Designer, Sound Engineer.
    -   **Phase 4-6 (Technical Base):** Network Engineer, Asset Manager, Test Engineer.
    -   **Phase 7-9 (Review & Publish):** Debugging Specialist, Performance Optimizer, Live Ops Engineer.
3.  **Communication Protocol (`utils/`)**
    -   Defined an `MCPToolBridge` to allow the agents access to MCP server capabilities natively in Python.
    -   Built a `PhaseValidator` that applies the constraints (Memory, performance thresholds, etc.) natively mimicking validation loops natively inside ADK.
4.  **Sequential Studio Loop (`main.py`)** 
    -   Linked all 14 agents utilizing the `google.adk.agent` primitives `SequentialAgent` and `ParallelAgent`.

---

## Desktop Setup Instructions
Since you requested this to run right from your desktop, an automatic runner script was included for environments like yours.

1.  **Supply your API key:** Open `c:\Users\bhanu\OneDrive\Desktop\ai_agent\.env` and paste your Google Gemini Key (`GEMINI_API_KEY`).
2.  **Run the script:** Double-click on `c:\Users\bhanu\OneDrive\Desktop\ai_agent\run_builder.bat` from your File Explorer.
    > The script will automatically create a secure Python virtual environment, download the required libraries via `pip`, and spin up the Master Agent loop.

*(Note: The system acts exactly like a command-line script. Ensure you have the ADK SDK properly hooked to your preferred Gemini model access through the installed `.env` configuration first!)*
