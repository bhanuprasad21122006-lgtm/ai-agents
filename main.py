import os
import sys
import asyncio

# Fix Windows console emoji printing issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Display Splash Screen immediately before heavy imports block the main thread
print(r"""
========================================================================
   ___    ___    ___    _____                       _____
  / _ \  / _ \  / _ \  |  __ \                     / __  \
 / /_\ \/ /_\ \/ /_\ \ | |  \/ __ _ _ __ ___   ___ | |  \ | _____   __
 |  _  ||  _  ||  _  | | | __ / _` | '_ ` _ \ / _ \| |  / |/ _ \ \ / /
 | | | || | | || | | | | |_\ \ (_| | | | | | |  __/| |_/ /  __/\ V /
 \_| |_/\_| |_/\_| |_/  \____/\__,_|_| |_| |_|\___|\____/ \___| \_/

                  AI-POWERED GAME ORCHESTRATOR
========================================================================
""")
print("✨ Booting up Neural Engine and loading AI models... Please wait! ✨\n")

from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

# Import utilities
from utils.artifacts import ProjectWorkspace
from utils.mcp_client import MCPToolBridge

# Import 14 Agents
from agents.phase1_design import get_game_designer, get_system_architect
from agents.phase2_core import get_gameplay_programmer, get_ai_engineer, get_level_designer, set_project_workspace
from agents.phase3_arts import get_graphics_engineer, get_ui_ux_designer, get_sound_engineer
from agents.phase4_6_technical import get_network_engineer, get_asset_manager, get_test_engineer
from agents.phase7_9_ops import get_debugging_specialist, get_performance_optimizer, get_live_ops_engineer

# ---------------------------------------------------------
# RATE LIMIT HANDLING PATCH
# ---------------------------------------------------------
import re
import google.adk.models.google_llm

original_generate_content_async = google.adk.models.google_llm.Gemini.generate_content_async

async def patched_generate_content_async(self, llm_request, stream=False):
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            async for response in original_generate_content_async(self, llm_request, stream):
                yield response
            return # Success
        except google.adk.models.google_llm._ResourceExhaustedError as e:
            if attempt < max_attempts - 1:
                match = re.search(r"retry in (\d+(?:\.\d+)?)s", str(e))
                wait_time = float(match.group(1)) + 5.0 if match else 60.0
                print(f"\n⚠️ [API Rate Limit Hit] Google API requested a pause. Waiting {wait_time:.1f}s before resuming... (Attempt {attempt+1}/{max_attempts})")
                await asyncio.sleep(wait_time)
            else:
                raise e

google.adk.models.google_llm.Gemini.generate_content_async = patched_generate_content_async

# ---------------------------------------------------------
# AAA GAME STUDIO ORCHESTRATOR
# ---------------------------------------------------------

async def main():
    print("🚀 Initializing AAA Game Studio Orchestrator...")
    load_dotenv()

    # Check if user added an API Key before instantiating any models
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("🔑 No Gemini API key found.")
        api_key = input("Please paste your Gemini API Key to continue (or press Enter to exit):\n> ").strip()
        if not api_key:
            print("❌ Exiting. A valid API key is required.")
            return

        # Set it in the environment so the ADK can pick it up
        os.environ["GEMINI_API_KEY"] = api_key
    # Interactive Prompt
    print("Welcome to the AAA Game Builder AI!")
    print("🎮 Provide a prompt to create your game (e.g., 'Make a 2D Platformer').")
    print("   (You can paste multiple lines. Type 'END' on a new line and press Enter to submit.)")
    print("   (Or just press Enter on an empty line to use the default prompt.)")

    lines = []
    while True:
        try:
            line = input("> ")
            if line.strip().upper() == "END":
                break
            if not line.strip() and not lines:
                break # Default prompt
            if line.strip().upper() != "END":
                lines.append(line)
        except EOFError:
            break

    user_prompt = "\n".join(lines).strip()

    if not user_prompt:
        user_prompt = "Create a scalable, modular multiplayer mobile FPS like Arena Breakout."

    workspace = ProjectWorkspace(user_prompt)
    set_project_workspace(workspace)
    mcp_toolset = None
    if os.getenv("ENABLE_MCP", "0").lower() in {"1", "true", "yes"}:
        try:
            mcp_toolset = MCPToolBridge(str(workspace.path.resolve())).create_toolset()
            print("🔌 MCP filesystem tools enabled; each server action will require confirmation.")
        except Exception as exc:
            workspace.record_event("mcp_unavailable", str(exc))
            print(f"⚠️ MCP is unavailable; continuing with built-in artifact tools. ({exc})")

    def build_artifact_tools(agent_name):
        def read_upstream_artifacts() -> str:
            """Read the durable deliverables created by agents that ran earlier."""
            return workspace.read_artifacts()

        def save_artifact(artifact_name: str, content: str) -> str:
            """Save this agent's deliverable. If validation fails, revise and call this tool again."""
            return workspace.save_artifact(agent_name, artifact_name, content)

        return [read_upstream_artifacts, save_artifact]

    # Instantiate Agents only after the project workspace exists, so every agent shares it.
    designer = get_game_designer(); architect = get_system_architect(); gameplay = get_gameplay_programmer()
    ai = get_ai_engineer(); level = get_level_designer(); graphics = get_graphics_engineer()
    ui_ux = get_ui_ux_designer(); sound = get_sound_engineer(); network = get_network_engineer()
    asset = get_asset_manager(); test = get_test_engineer(); debug = get_debugging_specialist()
    perf = get_performance_optimizer(); live_ops = get_live_ops_engineer()
    all_agents = [designer, architect, gameplay, ai, level, graphics, sound, ui_ux, network, asset, test, debug, perf, live_ops]

    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest
    async def rate_limit_sleep(callback_context: CallbackContext, llm_request: LlmRequest):
        await asyncio.sleep(2)
        return None

    for agent in all_agents:
        agent.before_model_callback = rate_limit_sleep
        agent.tools.extend(build_artifact_tools(agent.name))
        if mcp_toolset:
            agent.tools.append(mcp_toolset)
        agent.instruction += """
        EXECUTION PROTOCOL: First call read_upstream_artifacts to inspect earlier work. At the end, call
        save_artifact with a JSON object containing exactly: title, summary, decisions, dependencies, risks,
        and next_steps. If it returns VALIDATION_FAILED, revise the deliverable and save it again. Do not claim
        an artifact exists unless the save tool confirms it. Phase gates prevent work that lacks prerequisites.
        """
        agent.output_key = f"{agent.name}_final_output"

    print("🏗️ Building Agent Execution Graph...")
    phase_1 = SequentialAgent(sub_agents=[designer, architect], name="phase_1")
    phase_2 = SequentialAgent(sub_agents=[gameplay, ai, level], name="phase_2")
    phase_3 = SequentialAgent(sub_agents=[graphics, sound, ui_ux], name="phase_3")
    phase_4_to_6 = SequentialAgent(sub_agents=[network, asset, test], name="phase_4_to_6")
    phase_7_to_9 = SequentialAgent(sub_agents=[debug, perf, live_ops], name="phase_7_to_9")
    studio_orchestrator = SequentialAgent(sub_agents=[phase_1, phase_2, phase_3, phase_4_to_6, phase_7_to_9], name="master_orchestrator")
    print(f"✅ Pipeline Ready. Artifacts will be saved in: {workspace.path}")
    print("========================================================")

    print("\n[Studio Orchestrator] Starting Work on your Game...")

    # Trigger the pipeline
    try:
        from google.adk.runners import Runner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.genai import types
        from google.adk.utils._debug_output import print_event

        session_svc = InMemorySessionService()
        max_attempts = max(1, int(os.getenv("MAX_PIPELINE_ATTEMPTS", "2")))
        timeout_seconds = max(60, int(os.getenv("PIPELINE_TIMEOUT_SECONDS", "900")))
        timed_out = False
        attempts = 0

        async def run_attempt(message):
            runner = Runner(
                app_name="aaa_game_studio",
                agent=studio_orchestrator,
                session_service=session_svc,
                auto_create_session=True,
            )
            async for event in runner.run_async(user_id="user_demo", session_id="session_demo", new_message=message):
                print_event(event)

        message = types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
        for attempts in range(1, max_attempts + 1):
            workspace.record_event("pipeline_attempt", str(attempts))
            try:
                await asyncio.wait_for(run_attempt(message), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                timed_out = True
                workspace.record_event("pipeline_timeout", str(timeout_seconds))
                print(f"\n⚠️ Pipeline attempt timed out after {timeout_seconds}s.")
                break
            missing = workspace.missing_agents()
            if not missing:
                break
            if attempts < max_attempts:
                print(f"\n⚠️ Missing artifacts from: {', '.join(missing)}. Starting automatic recovery attempt...")
                message = types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=(
                        "Recovery pass: create the missing validated artifacts only. "
                        f"Missing agents: {', '.join(missing)}. Follow all phase gates and JSON schema exactly."
                    ))],
                )

        # Preserve final responses for review after all automated recovery attempts, never silently discard them.
        session = await session_svc.get_session(app_name="aaa_game_studio", user_id="user_demo", session_id="session_demo")
        if session:
            for agent_name in workspace.missing_agents():
                workspace.save_captured_output(agent_name, session.state.get(f"{agent_name}_final_output", ""))
        run_report = workspace.write_run_report(attempts, timed_out)
        print(f"[RUN REPORT] {run_report['status']}; attempts={attempts}; missing={len(run_report['missing_agents'])}; fallbacks={len(run_report['fallback_agents'])}")

        print("\n✅ Game Generation Complete! Durable artifacts have been saved to the project folder.")
        smoke_results = workspace.validate_generated_games()
        for result in smoke_results:
            print(f"[GAME SMOKE TEST] {result}")

        # Check if a game was generated
        generated_path = os.environ.get("GENERATED_GAME_PATH")
        if generated_path and os.path.exists(generated_path):
            download = input("\n🎮 Game successfully generated! Would you like to download/save it? (y/n): ")
            if download.lower() == 'y':
                import tkinter as tk
                from tkinter import filedialog
                import shutil

                # Hide the main tkinter window
                root = tk.Tk()
                root.withdraw()
                # Ensure the dialog appears on top
                root.attributes('-topmost', True)

                # Suggest the original filename
                suggested_name = os.path.basename(generated_path)

                save_path = filedialog.asksaveasfilename(
                    title="Save Generated Game",
                    initialfile=suggested_name,
                    defaultextension=".py",
                    filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
                )

                if save_path:
                    shutil.copy2(generated_path, save_path)
                    print(f"✅ Game saved to: {save_path}")
                else:
                    print("❌ Save cancelled.")
        else:
            print("\n⚠️ The AI did not generate a final playable code file this time.")
        print(f"📁 Run output: {workspace.path}")

    except Exception as e:
        workspace.record_event("execution_error", repr(e))
        workspace.write_run_report(0)
        print(f"\n❌ Execution Error: {e}")
        import traceback
        traceback.print_exc()

    # Prevent the terminal window from closing immediately if double-clicked
    if os.name == 'nt':
        os.system("pause")
    else:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())
