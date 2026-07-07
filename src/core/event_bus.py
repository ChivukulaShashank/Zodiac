# TODO: Implement
import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[..., Awaitable[Any]]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., Awaitable[Any]]) -> None:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    async def _execute_safely(self, callback: Callable[..., Awaitable[Any]], event_name: str, data: Any) -> None:
        try:
            # Pass data only if it was provided
            if data is None:
                await callback()
            else:
                await callback(data)
        except Exception as e:
            # Catch and log so one failing callback doesn't crash the whole bus
            logger.error(f"Exception in callback for event '{event_name}': {e}")

    async def emit(self, event_name: str, data: Any = None) -> None:
        if event_name not in self._subscribers:
            return
        
        # Gather all subscriber callbacks for concurrent execution
        tasks = [
            self._execute_safely(cb, event_name, data) 
            for cb in self._subscribers[event_name]
        ]
        
        if tasks:
            await asyncio.gather(*tasks)