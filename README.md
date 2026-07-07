# Zodiac: "Linux for AI Workspaces"

Zodiac is a terminal-first, highly modular AI framework. It is not an AI assistant—it is the engine to build one. Instead of hardcoded behaviors, Zodiac dynamically loads isolated environments called Workspaces, containing custom LLM models, Lua-defined personas, Rust/Bash tools, and CSS-styled terminal UIs.

## ✨ Key Features

* **100% Local & Private:** Runs entirely inside a Docker container. No data leaves your machine.
* **Dynamic TUI:** A modern, responsive terminal interface built with Textual. Layouts and themes are loaded via JSON/CSS, not hardcoded.
* **Constellation DAGs:** Chain multiple SLM agents together using Directed Acyclic Graphs (DAGs) for complex, multi-step workflows.
* **Sandboxed Lua Personas:** Define AI personalities, stats, and rules using safe Lua scripts. The core framework has zero hardcoded prompts.
* **Rust/Bash Tool Integration:** Extend capabilities by dropping executable files into a folder. Tools communicate via strict stdin/stdout JSON protocols.
* **The Llama Shop:** Press `Ctrl+L` in the UI to browse HuggingFace, view live RAM requirements calculated against your actual hardware, and download models directly.

## 🏗️ Architecture

Zodiac strictly separates the orchestrator from the logic:

* **Python:** The orchestrator. Handles async execution, UI rendering, memory management, and routing.
* **Lua:** Defines behavior (Personas). Completely sandboxed. No file or network access.
* **Rust/Bash:** Defines capabilities (Tools). Isolated subprocesses.

---

## 🚀 Getting Started

### Prerequisites

* Docker
* Docker Compose
* *(Windows Users)* WSL2 enabled.

### 1. Clone the Repository

```bash
git clone https://github.com/ChivukulaShashank/Zodiac.git
cd Zodiac
```

### 2. Build the Docker Container

This installs Python 3.11, Rust, Lua 5.4, and compiles the CPU-optimized `llama-cpp-python` backend.

```bash
docker compose build

```

### 3. Run the Container

Start the container in the background. Volume mounts ensure your code and workspaces sync seamlessly between your host machine and the container.

```bash
docker compose up -d

```

### 4. Enter the Container

```bash
docker exec -it zodiac-dev bash

```

---

## 💻 Usage

### Option A: The Terminal UI (Recommended)

Launch the dynamic Textual interface.

```bash
python -m src.main

```

* **Chat:** Type in the input box at the bottom to chat with the default agent.
* **Shop:** Press `Ctrl+L` to open the Llama Shop to browse and download GGUF models.
* **Logs:** View the sidebar on the right to see real-time framework logs (model loading, persona initialization, etc.).

### Option B: Command Line Interface

Execute a specific Constellation directly from the terminal without opening the TUI.

```bash
python -m src.main --run single_agent_chat --message "Explain quantum computing in one sentence."

```

---

## 📁 Project Structure

Everything inside a Workspace is completely portable and exportable.

```text
zodiac/
├── src/                  # The framework core (DO NOT EDIT unless developing)
│   ├── core/             # Event bus, config, workspace loader
│   ├── models/           # LLM manager, RAM budgeting, streaming
│   ├── agents/           # Agent execution, DAG parser
│   ├── tools/            # Subprocess launcher, JSON protocol
│   ├── personas/         # Lua sandbox runtime
│   └── tui/              # Textual app, layout loader, widgets
├── workspaces/
│   └── default/          # Your active environment
│       ├── manifest.json # Workspace config & RAM budget
│       ├── constellations/# Multi-agent DAG definitions
│       ├── personas/     # Lua character sheets
│       ├── tools/        # Executable capabilities
│       ├── layouts/      # UI tree JSON structures
│       └── themes/       # Textual CSS styles
└── models/               # Downloaded GGUF model weights

```

## 🛠️ Development

This project is built in strict phases. The core knows nothing about specific tools, models, or themes—it only reads schemas.

To add a new tool, simply create a folder in `workspaces/default/tools/`, add a `manifest.json` matching the schema, and drop in your executable. Restart the app, and the framework will discover and register it automatically.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
