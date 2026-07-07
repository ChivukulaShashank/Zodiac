import asyncio
import json
import urllib.request
import urllib.parse
from pathlib import Path
from huggingface_hub import hf_hub_download, HfApi
from src.core.system import SystemInfo

class ModelCatalog:
    def __init__(self, config: dict):
        self.config = config

    async def fetch_models(self, system_info: SystemInfo) -> list[dict]:
        # 1. Fetch the main list of models
        def _fetch_list():
            params = {
                "filter": self.config.get("search_filter", "gguf"),
                "sort": self.config.get("sort", "downloads"),
                "direction": self.config.get("direction", -1),
                "limit": 30,
                "full": "true"
            }
            qs = urllib.parse.urlencode(params)
            url = f"{self.config['api_url']}?{qs}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())

        # 2. Fetch specific file size using HfApi
        def _get_size(model_id, file_name):
            try:
                api = HfApi()
                info = api.model_info(model_id, files_metadata=True)
                for sib in info.siblings:
                    if sib.rfilename == file_name:
                        return sib.size or 0
                return 0
            except Exception:
                return 0

        data = await asyncio.to_thread(_fetch_list)
        
        # Prepare the list of models we want to check
        pending_models = []
        for model in data:
            model_id = model.get("modelId")
            siblings = model.get("siblings", [])
            
            gguf_file = None
            for sib in siblings:
                fname = sib.get("rfilename", "")
                if fname.endswith(".gguf"):
                    gguf_file = sib
                    break
            
            if not gguf_file:
                continue
                
            pending_models.append({
                "model_id": model_id,
                "file_name": gguf_file.get("rfilename")
            })

        # 3. Fetch all sizes concurrently so we don't freeze the TUI
        async def fetch_size(m):
            size_bytes = await asyncio.to_thread(_get_size, m["model_id"], m["file_name"])
            return m, size_bytes
            
        tasks = [fetch_size(m) for m in pending_models]
        size_results = await asyncio.gather(*tasks)
        
        results = []
        avail_ram = system_info.get_ram_available_mb()
        overhead = self.config.get("ram_overhead_percent", 10)
        
        for m, size_bytes in size_results:
            size_mb = int(size_bytes / (1024 * 1024)) if size_bytes else 0
            est_ram = int(size_mb * (1 + (overhead / 100)))
            fits = est_ram <= avail_ram
            
            results.append({
                "model_id": m["model_id"],
                "file_name": m["file_name"],
                "size_mb": size_mb,
                "estimated_ram_mb": est_ram,
                "fits": fits
            })
            
        return results

    async def download_model(self, model_id: str, file_name: str, save_path: Path):
        def _download():
            return hf_hub_download(
                repo_id=model_id,
                filename=file_name,
                local_dir=str(save_path)
            )
        return await asyncio.to_thread(_download)