import platform
import psutil

class SystemInfo:
    def get_ram_available_mb(self) -> int:
        return int(psutil.virtual_memory().available / (1024 * 1024))
    
    def get_ram_total_mb(self) -> int:
        return int(psutil.virtual_memory().total / (1024 * 1024))
        
    def get_cpu_info(self) -> str:
        return platform.processor() or "Unknown CPU"