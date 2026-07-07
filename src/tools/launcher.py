# TODO: Implement
import logging
from pathlib import Path
from src.tools.manager import ToolManager
from src.tools.protocol import execute_tool

logger = logging.getLogger(__name__)

class ToolLauncher:
    def __init__(self, tool_manager: ToolManager, workspace_path: Path):
        self.tool_manager = tool_manager
        self.workspace_path = workspace_path

    async def run(self, tool_name: str, args: dict) -> dict:
        manifest = self.tool_manager.get_tool(tool_name)
        if not manifest:
            raise ValueError(f"Tool {tool_name} not found.")

        tool_dir = Path(manifest["_tool_dir"])
        executable_path = (tool_dir / manifest["executable"]).resolve()
        
        timeout = manifest.get("timeout_seconds", 5)
        payload = {"args": args}

        return await execute_tool(executable_path, payload, timeout)