# TODO: Implement
import logging
from pathlib import Path
from src.personas.runtime import LuaRuntime
from src.personas.loader import PersonaLoader

logger = logging.getLogger(__name__)

class PersonaManager:
    def __init__(self):
        self.runtime = LuaRuntime()
        self.loader = PersonaLoader(self.runtime)
        self.personas = {}

    def load_personas(self, persona_resources: list[dict], workspace_path: Path) -> None:
        personas_dir = workspace_path / "personas"
        if not personas_dir.exists() or not personas_dir.is_dir():
            return

        for file_path in personas_dir.glob("*.lua"):
            try:
                persona_name = file_path.stem
                persona_data = self.loader.load(file_path)
                self.personas[persona_name] = persona_data
                logger.info(f"Successfully loaded persona: {persona_name}")
            except Exception as e:
                logger.warning(f"Failed to load persona from {file_path.name}: {e}")

    def get_persona(self, persona_name: str) -> dict:
        return self.personas.get(persona_name)