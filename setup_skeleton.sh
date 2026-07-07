#!/bin/bash

# Define the Python placeholder and JSON schema stub
PY_STUB="# TODO: Implement"
JSON_STUB='{ "$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}, "required": [] }'

echo "Generating Zodiac project skeleton..."

# 1. Create all directories
mkdir -p src/core src/agents src/models src/tools src/personas src/memory src/tui/views
mkdir -p workspaces/default/chats workspaces/default/constellations workspaces/default/personas workspaces/default/themes workspaces/default/layouts workspaces/default/memory
mkdir -p schemas

# 2. Generate Python files with the required stub
py_files=(
    "src/__init__.py" "src/main.py"
    "src/core/__init__.py" "src/core/event_bus.py" "src/core/config.py" "src/core/workspace.py"
    "src/agents/__init__.py" "src/agents/manager.py" "src/agents/agent.py" "src/agents/executor.py"
    "src/models/__init__.py" "src/models/manager.py"
    "src/tools/__init__.py" "src/tools/manager.py" "src/tools/launcher.py" "src/tools/protocol.py"
    "src/personas/__init__.py" "src/personas/manager.py" "src/personas/runtime.py"
    "src/memory/__init__.py" "src/memory/manager.py"
    "src/tui/__init__.py" "src/tui/app.py" "src/tui/views/__init__.py"
)

for file in "${py_files[@]}"; do
    echo "$PY_STUB" > "$file"
done

# 3. Generate Schema JSON files with the required stub
json_files=(
    "schemas/workspace.json" "schemas/constellation.json" "schemas/agent.json" 
    "schemas/tool.json" "schemas/persona.json" "schemas/theme.json" "schemas/layout.json"
)

for file in "${json_files[@]}"; do
    echo "$JSON_STUB" > "$file"
done

# 4. Generate .gitkeep files for empty directories
gitkeep_dirs=(
    "workspaces/default/chats" "workspaces/default/constellations" 
    "workspaces/default/personas" "workspaces/default/themes" 
    "workspaces/default/layouts" "workspaces/default/memory"
    "models"
)

for dir in "${gitkeep_dirs[@]}"; do
    touch "$dir/.gitkeep"
done

echo "Project skeleton successfully generated!"