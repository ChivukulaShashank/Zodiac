def check_permissions(agent_config: dict, tool_name: str, tool_manifest: dict) -> None:
    allowed_tools = agent_config.get("allowed_tools", [])
    if tool_name not in allowed_tools:
        raise PermissionError(f"Agent is not authorized to use the tool: {tool_name}")