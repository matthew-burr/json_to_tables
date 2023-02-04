from dataclasses import dataclass
from typing import List, NewType, Self


DataType = NewType("DataType", str)


@dataclass
class Column:
    name: str
    data_type: DataType


@dataclass
class Table:
    name: str
    columns: List[Column]

    def merge(self, other: Self) -> Self:
        return self

    def __eq__(self, other):
        if other.name != self.name:
            return False

        if len(other.columns) != len(self.columns):
            return False

        return all(col in self.columns for col in other.columns)
