from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from src.tui.widgets.registry import WidgetRegistry

class LayoutLoader:
    def __init__(self, registry: WidgetRegistry):
        self.registry = registry

    def build(self, layout_data: dict) -> Widget:
        l_type = layout_data.get("type")
        children_data = layout_data.get("children", [])
        children_widgets = [self.build(c) for c in children_data]
        
        if l_type == "horizontal":
            container = Horizontal(*children_widgets)
        elif l_type == "vertical":
            container = Vertical(*children_widgets)
        elif l_type == "widget":
            widget_class = self.registry.get(layout_data["id"])
            if not widget_class:
                raise ValueError(f"Widget {layout_data['id']} not found in registry")
            container = widget_class()
        else:
            raise ValueError(f"Unknown layout type: {l_type}")
            
        if "ratio" in layout_data:
            ratio_percent = layout_data["ratio"] * 100
            if l_type in ["horizontal", "widget"]:
                container.styles.width = f"{ratio_percent}%"
            elif l_type == "vertical":
                container.styles.height = f"{ratio_percent}%"
            
        return container