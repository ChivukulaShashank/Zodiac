from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer, Button, Label
from textual.containers import Vertical, Horizontal
from textual import work
from textual.coordinate import Coordinate
from pathlib import Path

from src.models.catalog import ModelCatalog
from src.core.system import SystemInfo

class LlamaShopScreen(Screen):
    def __init__(self, catalog: ModelCatalog, system_info: SystemInfo):
        super().__init__()
        self.catalog = catalog
        self.system_info = system_info
        self.models_data = []

    def compose(self) -> ComposeResult:
        avail_ram = self.system_info.get_ram_available_mb()
        yield Header()
        with Vertical():
            yield Label(f"System RAM Available: {avail_ram} MB", id="ram-label")
            yield Label("Fetching models...", id="status-label")
            yield DataTable(id="models-table", cursor_type="row")
            with Horizontal():
                yield Button("Download Selected", id="btn-download", variant="success")
                yield Button("Close", id="btn-close", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.fetch_models()

    @work(thread=True)
    async def fetch_models(self):
        try:
            models = await self.catalog.fetch_models(self.system_info)
            self.app.call_from_thread(self.populate_table, models)
        except Exception as e:
            self.app.call_from_thread(self.update_status, f"Error fetching models: {e}")

    def update_status(self, msg: str):
        self.query_one("#status-label", Label).update(msg)

    def populate_table(self, models: list[dict]):
        self.models_data = models
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("Model", "File", "Size (MB)", "Est. RAM (MB)", "Fits?")
        
        for idx, m in enumerate(models):
            fits_str = "[green]Yes[/green]" if m["fits"] else "[red]No[/red]"
            table.add_row(
                m["model_id"], 
                m["file_name"], 
                str(m["size_mb"]), 
                str(m["estimated_ram_mb"]), 
                fits_str,
                key=str(idx)
            )
            
        if models:
            self.update_status("Models loaded. Select one and click Download.")
        else:
            self.update_status("No GGUF models found.")
        table.focus()

    @work(thread=True)
    async def process_download(self, model_idx: int):
        m = self.models_data[model_idx]
        if not m["fits"]:
            self.app.call_from_thread(self.update_status, "Blocked: Model exceeds available RAM.")
            return
        
        self.app.call_from_thread(self.update_status, f"Downloading {m['file_name']}... (This may take a while)")
        save_path = Path("models")
        save_path.mkdir(exist_ok=True)
        try:
            await self.catalog.download_model(m["model_id"], m["file_name"], save_path)
            self.app.call_from_thread(self.update_status, f"Downloaded {m['file_name']} successfully!")
            self.app.call_from_thread(self.app.notify, f"{m['file_name']} downloaded.")
        except Exception as e:
            self.app.call_from_thread(self.update_status, f"Download failed: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.app.pop_screen()
        elif event.button.id == "btn-download":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(Coordinate(table.cursor_row, 0)).row_key
                    idx = int(row_key.value)
                    self.process_download(idx)
                except Exception:
                    self.update_status("Could not select row.")
            else:
                self.update_status("Please select a model to download.")