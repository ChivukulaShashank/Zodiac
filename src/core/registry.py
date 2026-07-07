import json
import logging
from .workspace import Workspace
from .event_bus import EventBus

logger = logging.getLogger(__name__)

async def discover_resources(workspace: Workspace, event_bus: EventBus) -> None:
    """Scan workspace directories, load JSON resources, and emit a discovery event."""
    # Added "models" to the directories list
    directories = ["chats", "constellations", "personas", "themes", "layouts", "tools", "models"]
    total_discovered = 0

    for directory in directories:
        dir_path = workspace.path / directory
        
        # Initialize the list for this resource type
        workspace.resources[directory] = []

        if not dir_path.exists() or not dir_path.is_dir():
            continue

        for file_path in dir_path.iterdir():
            # Skip the .gitkeep files we created in Phase 0
            if file_path.name == ".gitkeep" or not file_path.is_file():
                continue
            
            # --- NEW: Special handling for GGUF models ---
            if directory == "models" and file_path.suffix == ".gguf":
                workspace.resources[directory].append({
                    "file": file_path.name,
                    "type": "gguf",
                    "path": str(file_path.absolute())
                })
                total_discovered += 1
                continue
            # ---------------------------------------------

            try:
                # Standard synchronous read is acceptable for the startup sequence
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Append the parsed data in the required format
                workspace.resources[directory].append({
                    "file": file_path.name,
                    "data": data
                })
                total_discovered += 1
                
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in resource file {file_path}: {e}")
            except Exception as e:
                logger.warning(f"Failed to read resource file {file_path}: {e}")

    logger.info(f"Discovered a total of {total_discovered} resources.")
    await event_bus.emit("resources.discovered", workspace.resources)