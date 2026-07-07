import logging
from pathlib import Path
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, ram_budget_mb: int):
        self.ram_budget_mb = ram_budget_mb
        self.loaded_models = {}

    def _load_model(self, model_path: Path):
        model_name = model_path.name
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        logger.info(f"Loading model {model_name}...")
        try:
            model = Llama(model_path=str(model_path), verbose=False)
            self.loaded_models[model_name] = model
            return model
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    async def generate_stream(self, model_path: Path, messages: list[dict]):
        model = self._load_model(model_path)
        try:
            response = model.create_chat_completion(
                messages=messages,
                max_tokens=1024,
                stream=True
            )
            for chunk in response:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta and delta['content']:
                    yield delta['content']
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise