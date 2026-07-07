# TODO: Implement
import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

async def execute_tool(executable_path: Path, payload: dict, timeout: int) -> dict:
    process = await asyncio.create_subprocess_exec(
        str(executable_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    payload_str = json.dumps(payload)
    
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=payload_str.encode()), 
            timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError(f"Tool execution timed out after {timeout} seconds.")
        
    if stderr:
        logger.debug(f"Tool {executable_path.name} stderr: {stderr.decode().strip()}")
        
    try:
        return json.loads(stdout.decode())
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON output from {executable_path.name}")