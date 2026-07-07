from textual.app import ComposeResult
from textual.containers import VerticalScroll, Vertical
from textual.widgets import Input, Static, Markdown
from textual.message import Message

class ChatInputSubmitted(Message):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()

# User messages stay as standard Static text
class UserMessage(Static):
    pass

# AI messages use Textual's Markdown engine for beautiful code blocks
class AIMessage(Markdown):
    pass

class WelcomeMessage(Static):
    pass

class ChatView(Vertical):
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="message-container"):
            yield WelcomeMessage(
                "[#569cd6]"
                "   _____ ____  ____  ____  ___    ______ \n"
                "  /__  // __ \\/ __ \\/  _/ /   |  / ____/ \n"
                "    / / / / / / / / // / / /| | / /      \n"
                "   / /_/ /_/ / /_/ // / / ___ |/ /___    \n"
                "  /____\\____/_____/___//_/  |_|\\____/    \n"
                "[/#569cd6]\n\n"
                "Welcome back, Architect.\n\n"
                "[#808080]Type a message to start, or press [b]Ctrl+L[/b] to open the Llama Shop.[/#808080]"
            )
        yield Input(placeholder="How can I help you today?", id="chat-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            # Remove the welcome screen on first message
            welcome_screen = self.query(WelcomeMessage)
            if welcome_screen:
                welcome_screen.remove()
                
            self.post_message(ChatInputSubmitted(event.value))
            event.input.value = ""