from src.tui.widgets.chat import ChatView
from src.tui.widgets.sidebar import Sidebar

class WidgetRegistry:
    def __init__(self):
        self.widgets = {}
        
    def register(self, widget_id: str, widget_class):
        self.widgets[widget_id] = widget_class
        
    def get(self, widget_id: str):
        return self.widgets.get(widget_id)
        
    def register_defaults(self):
        self.register("chat_view", ChatView)
        self.register("log_sidebar", Sidebar)