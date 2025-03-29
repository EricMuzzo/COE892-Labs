from typing import List, TypeVar, Generic
from pydantic import BaseModel, computed_field
T = TypeVar("T")

class ListResponse(BaseModel, Generic[T]):
    """Used for GET endpoint responses on a list of resources"""
    records: List[T]

    @computed_field
    @property
    def count(self) -> int:
        return len(self.records)