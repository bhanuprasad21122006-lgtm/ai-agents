import os
import sys
import asyncio

# Fix Windows console emoji printing issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

# Import utilities
from utils.mcp_client import MCPToolBridge
from utils.validator import PhaseValidator

# Import 14 Agents
from agents.phase1_design import get_game_designer, get_system_architect
from agents.phase2_core import get_gameplay_programmer, get_ai_engineer, get_level_designer
from agents.phase3_arts import get_graphics_engineer, get_ui_ux_designer, get_sound_engineer
from agents.phase4_6_technical import get_network_engineer, get_asset_manager, get_test_engineer
from agents.phase7_9_ops import get_debugging_specialist, get_performance_optimizer, get_live_ops_engineer

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
    # Initialize MCP Server connection for local tools
    mcp_bridge = MCPToolBridge()
    # mcp_client = await mcp_bridge.initialize() # Uncomment when MCP server is ready
    
    # Instantiate Agents
    designer = get_game_designer()
    architect = get_system_architect()
    gameplay = get_gameplay_programmer()
    ai = get_ai_engineer()
    level = get_level_designer()
    graphics = get_graphics_engineer()
    ui_ux = get_ui_ux_designer()
    sound = get_sound_engineer()
    network = get_network_engineer()
    asset = get_asset_manager()
    test = get_test_engineer()
    debug = get_debugging_specialist()
    perf = get_performance_optimizer()
    live_ops = get_live_ops_engineer()

    # Define the Studio Pipeline using ADK constructs
    # Dynamic Rate Limit Fix for Free Tier
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest

    async def rate_limit_sleep(callback_context: CallbackContext, llm_request: LlmRequest):
        print("\n⏳ [Agent Sync] Pacing API requests to respect Free Tier Limits (Waiting 12s)...")
        await asyncio.sleep(12)
        return None

    all_agents = [
        designer, architect, gameplay, ai, level, graphics, sound, 
        ui_ux, network, asset, test, debug, perf, live_ops
    ]
    for agent in all_agents:
        agent.before_model_callback = rate_limit_sleep

    print("🏗️ Building Agent Execution Graph...")
    
    # Phase 1: Sequential Design
    phase_1 = SequentialAgent(sub_agents=[designer, architect], name="phase_1")
    
    # Phase 2: Sequential Core Development (Originally Parallel, changed for Free Tier Rate Limits)
    phase_2 = SequentialAgent(sub_agents=[gameplay, ai, level], name="phase_2")
    
    # Phase 3: Sequential Arts & UX (Originally Parallel, changed for Free Tier Rate Limits)
    phase_3 = SequentialAgent(sub_agents=[graphics, sound, ui_ux], name="phase_3")
    
    # Phase 4-6: Network, Asset Management, Testing
    phase_4_to_6 = SequentialAgent(sub_agents=[network, asset, test], name="phase_4_to_6")
    
    # Phase 7-9: Operations
    phase_7_to_9 = SequentialAgent(sub_agents=[debug, perf, live_ops], name="phase_7_to_9")
    
    # Main Studio Loop
    studio_orchestrator = SequentialAgent(
        sub_agents=[phase_1, phase_2, phase_3, phase_4_to_6, phase_7_to_9],
        name="master_orchestrator"
    )

    print("✅ Pipeline Ready.")
    print("========================================================")
    

    # Interactive Prompt
    print("Welcome to the AAA Game Builder AI!")
    user_prompt = input("🎮 Provide a prompt to create your game (e.g., 'Make a 2D Platformer'):\n> ")
    
    if not user_prompt.strip():
        user_prompt = "Create a scalable, modular multiplayer mobile FPS like Arena Breakout."
        
    print("\n[Studio Orchestrator] Starting Work on your Game...")
    
    # Trigger the pipeline
    try:
        from google.adk.runners import Runner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.genai import types
        from google.adk.utils._debug_output import print_event

        session_svc = InMemorySessionService()
        runner = Runner(
            app_name="aaa_game_studio",
            agent=studio_orchestrator,
            session_service=session_svc,
            auto_create_session=True
        )

        message = types.Content(role='user', parts=[types.Part.from_text(text=user_prompt)])
        
        async for event in runner.run_async(
            user_id="user_demo",
            session_id="session_demo",
            new_message=message
        ):
            print_event(event)
                
        print("\n✅ Game Generation Complete! All requested code has been outputted above.")
        
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
                    
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")
        import traceback
        traceback.print_exc()

    # Prevent the terminal window from closing immediately if double-clicked
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())
