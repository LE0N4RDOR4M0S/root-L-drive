class InMemoryObjectStream:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def stream(self, amt: int = 1024 * 64):
        for index in range(0, len(self._payload), amt):
            yield self._payload[index : index + amt]

    def close(self) -> None:
        return

    def release_conn(self) -> None:
        return
