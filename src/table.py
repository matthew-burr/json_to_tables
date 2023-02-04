from dataclasses import dataclass
from typing import List, Self


class DataType:
    def __init__(self, initial_value: str = None) -> None:
        self._values = {*initial_value.lower().split("|")} if initial_value else set()

    def __str__(self) -> str:
        return "|".join(sorted(self._values))

    def __add__(self, other: Self | str) -> Self:
        if not isinstance(other, (self.__class__, str)):
            return NotImplemented

        result = self.__class__(str(other))
        result._values = result._values.union(self._values)
        return result

    def __radd__(self, other: Self | str) -> Self:
        return self + other

    def __eq__(self, __o: object) -> bool:
        other = self.__class__(str(__o))
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


@dataclass
class Column:
    name: str
    data_type: DataType

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Table:
    name: str
    columns: List[Column]

    @staticmethod
    def _merge_columns(left: List[Column], right: List[Column]) -> List[Column]:
        col_dict = {left_col.name: left_col.data_type for left_col in left}

        for right_col in right:
            col_dict[right_col.name] = (
                col_dict.get(right_col.name, "") + right_col.data_type
            )

        return [Column(name, dtypes) for name, dtypes in col_dict.items()]

    def merge(self, other: Self) -> Self:
        merged_cols = self._merge_columns(self.columns, other.columns)
        return self.__class__(
            name=self.name,
            columns=merged_cols,
        )

    def __eq__(self, other):
        if other.name != self.name:
            return False

        if len(other.columns) != len(self.columns):
            return False

        return all(col in self.columns for col in other.columns)

    def __hash__(self):
        return hash((self.name, *sorted((c.name, c.data_type) for c in self.columns)))
