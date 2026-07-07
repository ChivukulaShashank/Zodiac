import json
from pathlib import Path
from src.models.manager import ModelManager
from src.memory.manager import SharedMemory
from src.agents.agent import Agent
from src.tools.manager import ToolManager
from src.tools.launcher import ToolLauncher
from src.personas.manager import PersonaManager

class ConstellationExecutor:
    def __init__(self, model_manager: ModelManager, tool_manager: ToolManager, tool_launcher: ToolLauncher, persona_manager: PersonaManager):
        self.model_manager = model_manager
        self.tool_manager = tool_manager
        self.tool_launcher = tool_launcher
        self.persona_manager = persona_manager

    def load_dag(self, dag_data: dict) -> list[str]:
        agents = {a["id"]: a for a in dag_data.get("agents", [])}
        connections = dag_data.get("connections", [])
        
        adj = {a: [] for a in agents}
        in_degree = {a: 0 for a in agents}
        
        for conn in connections:
            u = conn["from"]
            v = conn["to"]
            if u in adj and v in adj:
                adj[u].append(v)
                in_degree[v] += 1
                
        queue = [n for n in agents if in_degree[n] == 0]
        exec_order = []
        
        while queue:
            curr = queue.pop(0)
            exec_order.append(curr)
            
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(exec_order) != len(agents):
            raise ValueError("Cycle detected in Constellation DAG. Only Acyclic Graphs are permitted.")
            
        return exec_order

    async def execute_stream(self, constellation_name: str, user_message: str):
        const_path = Path(f"workspaces/default/constellations/{constellation_name}.json")
        with open(const_path, "r") as f:
            dag_data = json.load(f)
            
        exec_order = self.load_dag(dag_data)
        shared_memory = SharedMemory()
        
        current_message = user_message
        
        agents_dict = {a["id"]: a for a in dag_data.get("agents", [])}
        
        for agent_id in exec_order:
            config = agents_dict[agent_id]
            agent = Agent(
                agent_id, 
                config, 
                self.model_manager, 
                self.tool_manager, 
                self.tool_launcher,
                self.persona_manager
            )
            
            buffer = ""
            async for chunk in agent.execute_stream(current_message, shared_memory, config):
                buffer += chunk
                yield chunk
            current_message = buffer