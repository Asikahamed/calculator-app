from typing import Optional
from app.schemas import CalculationResponse


class CalculationStore:
    """Simple in-memory store for calculation history."""

    def __init__(self):
        self._store: dict[str, CalculationResponse] = {}

    def save(self, record: CalculationResponse) -> CalculationResponse:
        self._store[record.id] = record
        return record

    def get(self, record_id: str) -> Optional[CalculationResponse]:
        return self._store.get(record_id)

    def get_all(self) -> list[CalculationResponse]:
        # Return most recent first
        return sorted(
            self._store.values(),
            key=lambda r: r.timestamp,
            reverse=True,
        )

    def count(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        """Used in tests to reset state between test cases."""
        self._store.clear()


# Single shared instance (acts as an in-memory DB for the app lifetime)
store = CalculationStore()
