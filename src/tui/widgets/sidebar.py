import logging
from textual.widgets import RichLog

class TextualLogHandler(logging.Handler):
    def __init__(self, widget: RichLog):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.app.call_from_thread(self.widget.write, msg)

class Sidebar(RichLog):
    def attach_logger(self):
        handler = TextualLogHandler(self)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
        root_logger.addHandler(handler)