import json
import logging
from pathlib import Path
from src.models.manager import ModelManager
from src.memory.manager import SharedMemory
from src.personas.null_persona import NullPersona
from src.personas.manager import PersonaManager
from src.tools.manager import ToolManager
from src.tools.launcher import ToolLauncher
from src.tools.permissions import check_permissions

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, agent_id: str, config: dict, model_manager: ModelManager, tool_manager: ToolManager, tool_launcher: ToolLauncher, persona_manager: PersonaManager):
        self.agent_id = agent_id
        self.config = config
        self.model_manager = model_manager
        self.tool_manager = tool_manager
        self.tool_launcher = tool_launcher
        self.persona_manager = persona_manager

    async def execute_stream(self, user_message: str, shared_memory: SharedMemory, agent_config: dict):
        persona_name = agent_config.get("persona")
        persona = None
        
        if persona_name:
            persona = self.persona_manager.get_persona(persona_name)
        
        if persona and "build_system_prompt" in persona:
            system_prompt = persona["build_system_prompt"]("User request incoming")
        else:
            fallback_persona = NullPersona()
            system_prompt = fallback_persona.build_system_prompt(config=self.config, context="")

        allowed_tools = agent_config.get("allowed_tools", [])
        
        if allowed_tools:
            system_prompt += "\n\n[AVAILABLE TOOLS]\n"
            for tool_name in allowed_tools:
                manifest = self.tool_manager.get_tool(tool_name)
                if manifest:
                    system_prompt += f"- {manifest['trigger_instruction']}\n"
            system_prompt += "If no tool is needed, reply normally without using any TOOL triggers.\n"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        model_filename = self.config.get("model")
        model_path = Path("models") / model_filename
        
        for _ in range(5):
            buffer = ""
            async for chunk in self.model_manager.generate_stream(model_path, messages):
                buffer += chunk
                yield chunk
                
            tool_triggered = False
            for tool_name in allowed_tools:
                manifest = self.tool_manager.get_tool(tool_name)
                if not manifest:
                    continue
                    
                trigger_prefix = f"TOOL_{tool_name.upper()}:"
                
                if trigger_prefix in buffer:
                    tool_triggered = True
                    parts = buffer.split(trigger_prefix)
                    args = parts[1].split("\n")[0].strip() if len(parts) > 1 else ""
                    
                    check_permissions(agent_config, tool_name, manifest)
                    
                    tool_result = await self.tool_launcher.run(tool_name, args)
                    
                    if manifest["output_mode"] == "console":
                        logger.info(f"TOOL OUTPUT ({tool_name}): {json.dumps(tool_result, indent=2)}")
                        return
                        
                    elif manifest["output_mode"] == "agent":
                        messages.append({"role": "assistant", "content": buffer})
                        messages.append({"role": "user", "content": json.dumps(tool_result)})
                        break 
                        
            if not tool_triggered:
                shared_memory.set(self.agent_id, buffer)
                return