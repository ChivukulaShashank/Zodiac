# TODO: Implement
import logging
from pathlib import Path
import lupa

logger = logging.getLogger(__name__)

class LuaRuntime:
    def __init__(self):
        self._lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        
        self._lua.globals()['os'] = None
        self._lua.globals()['io'] = None
        self._lua.globals()['debug'] = None
        self._lua.globals()['load'] = None
        self._lua.globals()['dofile'] = None

    def execute_file(self, file_path: Path) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lua_code = f.read()
            
            return self._lua.execute(lua_code)
        except Exception as e:
            logger.error(f"Failed to execute Lua file {file_path}: {e}")
            raise