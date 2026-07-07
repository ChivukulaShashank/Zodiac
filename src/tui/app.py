import json
import logging
from pathlib import Path
from textual.app import App, ComposeResult
from textual import work

from src.tui.widgets.registry import WidgetRegistry
from src.tui.layout_loader import LayoutLoader
from src.tui.widgets.sidebar import Sidebar

# UPDATED: Swapped ChatMessage for UserMessage and AIMessage
from src.tui.widgets.chat import ChatView, ChatInputSubmitted, UserMessage, AIMessage

from src.models.manager import ModelManager
from src.tools.manager import ToolManager
from src.tools.launcher import ToolLauncher
from src.personas.manager import PersonaManager
from src.agents.executor import ConstellationExecutor

class ZodiacApp(App):
    BINDINGS = [
        ("ctrl+l", "open_shop", "Llama Shop")
    ]

    def __init__(self):
        super().__init__()
        self.registry = WidgetRegistry()
        self.registry.register_defaults()
        
        manifest_path = Path("workspaces/default/manifest.json")
        with open(manifest_path, "r") as f:
            self.manifest = json.load(f)
            
        active_theme = self.manifest.get("active_theme", "dark")
        self.CSS_PATH = f"../../workspaces/default/themes/{active_theme}.tcss"
        
        active_layout = self.manifest.get("active_layout", "default")
        layout_path = Path(f"workspaces/default/layouts/{active_layout}.json")
        with open(layout_path, "r") as f:
            self.layout_data = json.load(f)

    def compose(self) -> ComposeResult:
        loader = LayoutLoader(self.registry)
        yield loader.build(self.layout_data)

    def on_mount(self) -> None:
        try:
            sidebar = self.query_one(Sidebar)
            sidebar.attach_logger()
        except Exception as e:
            print(f"Sidebar not found: {e}")

    def action_open_shop(self):
        catalog_config = self.manifest.get("catalog", {})
        from src.models.catalog import ModelCatalog
        from src.core.system import SystemInfo
        from src.tui.widgets.shop import LlamaShopScreen
        
        catalog = ModelCatalog(catalog_config)
        system_info = SystemInfo()
        self.push_screen(LlamaShopScreen(catalog, system_info))

    @work(thread=True)
    # UPDATED: Changed ai_msg type hint to AIMessage
    async def run_constellation(self, message: str, ai_msg: AIMessage):
        try:
            workspace_path = Path("workspaces/default")
            
            ram_budget = self.manifest.get("ram_budget_mb", 2048)
            model_manager = ModelManager(ram_budget_mb=ram_budget)
            
            tool_manager = ToolManager()
            tool_launcher = ToolLauncher(tool_manager, workspace_path)
            persona_manager = PersonaManager()

            executor = ConstellationExecutor(model_manager, tool_manager, tool_launcher, persona_manager)
            
            current_text = ""
            async for chunk in executor.execute_stream("single_agent_chat", message):
                current_text += chunk
                self.call_from_thread(ai_msg.update, current_text)
                
        except Exception as e:
            logging.error(f"Execution error: {e}")

    async def on_chat_input_submitted(self, event: ChatInputSubmitted) -> None:
        msg_container = self.query_one("#message-container")
        
        # UPDATED: Use the new UserMessage class
        user_msg = UserMessage(f"**User:** {event.text}", classes="user-message")
        await msg_container.mount(user_msg)
        
        # UPDATED: Use the new AIMessage class (Markdown)
        ai_msg = AIMessage("", classes="ai-message")
        await msg_container.mount(ai_msg)
        
        msg_container.scroll_end(animate=False)
        
        self.run_constellation(event.text, ai_msg)