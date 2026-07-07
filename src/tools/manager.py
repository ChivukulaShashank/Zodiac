# TODO: Implement
import json
import logging
from pathlib import Path
import jsonschema

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self.tools = {}

    def load_tools(self, tools_resources: list[dict], workspace_path: Path) -> None:
        schema_path = Path("schemas/tool.json")
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            logger.error(f"Could not load tool schema: {e}")
            return

        tools_dir = workspace_path / "tools"
        if not tools_dir.exists() or not tools_dir.is_dir():
            return

        for tool_folder in tools_dir.iterdir():
            if not tool_folder.is_dir():
                continue

            manifest_path = tool_folder / "manifest.json"
            if not manifest_path.exists():
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                jsonschema.validate(instance=manifest, schema=schema)
                
                manifest["_tool_dir"] = str(tool_folder.absolute())
                
                self.tools[manifest["name"]] = manifest
                logger.info(f"Successfully loaded tool: {manifest['name']}")
            except jsonschema.exceptions.ValidationError as e:
                logger.warning(f"Validation failed for tool in {tool_folder.name}: {e.message}")
            except Exception as e:
                logger.warning(f"Failed to load tool in {tool_folder.name}: {e}")

    def get_tool(self, tool_name: str) -> dict:
        return self.tools.get(tool_name)