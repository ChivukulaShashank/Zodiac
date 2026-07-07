# TODO: Implement
class SharedMemory:
    def __init__(self):
        self.store = {}

    def set(self, key: str, value: any) -> None:
        self.store[key] = value

    def get(self, key: str, default=None) -> any:
        return self.store.get(key, default)