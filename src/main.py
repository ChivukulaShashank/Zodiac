import argparse
import asyncio
import logging
from pathlib import Path

from src.core import (
    EventBus,
    Workspace,
    setup_logging,
    load_workspace_config,
    discover_resources
)

from src.models.manager import ModelManager
from src.agents.executor import ConstellationExecutor
from src.tools.manager import ToolManager
from src.tools.launcher import ToolLauncher
from src.personas.manager import PersonaManager

logger = logging.getLogger(__name__)

async def main() -> None:
    parser = argparse.ArgumentParser(description="Zodiac Terminal Workspace")
    parser.add_argument("--workspace", type=str, default="default", help="Name of the workspace to load")
    parser.add_argument("--run", type=str, help="Name of the constellation to execute")
    parser.add_argument("--message", type=str, help="Initial user message for the constellation")
    args = parser.parse_args()

    if not args.run:
        from src.tui.app import ZodiacApp
        app = ZodiacApp()
        await app.run_async()
        return

    setup_logging()
    logger.info("Starting Zodiac CLI...")
    event_bus = EventBus()
    workspace_path = Path(f"workspaces/{args.workspace}")

    try:
        config = await load_workspace_config(workspace_path)
        workspace = Workspace(name=args.workspace, path=workspace_path, config=config)
        logger.info(f"Loaded manifest for workspace: {workspace.name}")
        
        await discover_resources(workspace, event_bus)
        
        persona_manager = PersonaManager()
        persona_manager.load_personas(workspace.resources.get("personas", []), workspace_path)
        
        if args.run and args.message:
            ram_budget = workspace.config.get("ram_budget_mb", 2048)
            model_manager = ModelManager(ram_budget_mb=ram_budget)
            
            tool_manager = ToolManager()
            tool_manager.load_tools(workspace.resources.get("tools", []), workspace_path)
            tool_launcher = ToolLauncher(tool_manager, workspace_path)
            
            executor = ConstellationExecutor(model_manager, tool_manager, tool_launcher, persona_manager)
            logger.info("Executing constellation...")
            
            print("\n--- FINAL OUTPUT ---")
            async for chunk in executor.execute_stream(args.run, args.message):
                print(chunk, end="", flush=True)
            print("\n--------------------\n")
            
            logger.info("Execution complete.")
            
    except Exception as e:
        logger.critical(f"Startup failed: {e}")

    logger.info("Shutting down.")

if __name__ == "__main__":
    asyncio.run(main())