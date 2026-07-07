# TODO: Implement
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

async def load_workspace_config(workspace_path: Path) -> dict:
    """Load and parse the manifest.json file for a given workspace."""
    manifest_file = workspace_path / "manifest.json"
    
    if not manifest_file.exists():
        logger.error(f"Manifest file not found at: {manifest_file}")
        raise FileNotFoundError(f"Missing manifest.json in {workspace_path}")
        
    try:
        # Standard sync file reading is acceptable here per instructions
        with open(manifest_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in manifest file {manifest_file}: {e}")
        raise ValueError(f"Failed to parse manifest.json: {e}")