import logging
from pathlib import Path
from src.personas.runtime import LuaRuntime

logger = logging.getLogger(__name__)

class PersonaLoader:
    def __init__(self, runtime: LuaRuntime):
        self.runtime = runtime

    def load(self, file_path: Path) -> dict:
        persona_data = self.runtime.execute_file(file_path)
        
        if not persona_data:
            raise ValueError(f"Persona file {file_path} returned empty data.")

        if 'build_system_prompt' not in persona_data or not callable(persona_data['build_system_prompt']):
            raise ValueError(f"Persona file {file_path} missing callable 'build_system_prompt'.")
            
        if 'on_load' not in persona_data or not callable(persona_data['on_load']):
            raise ValueError(f"Persona file {file_path} missing callable 'on_load'.")
            
        if 'metadata' not in persona_data:
            raise ValueError(f"Persona file {file_path} missing 'metadata' table.")

        try:
            persona_data['on_load']()
        except Exception as e:
            logger.error(f"Error executing on_load for {file_path}: {e}")

        return persona_data