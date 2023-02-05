from dataclasses import dataclass, field
from typing import Dict, List, Self


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

    def __add__(self, __o: Self) -> Self:
        if not isinstance(__o, self.__class__):
            return NotImplemented

        if __o.name != self.name:
            return NotImplemented

        return Column(
            self.name,
            self.data_type + __o.data_type,
        )


@dataclass
class Table:
    name: str
    columns: List[Column]
    children: Dict[str, Self] = field(default_factory=dict)

    @staticmethod
    def _merge_columns(left: List[Column], right: List[Column]) -> List[Column]:
        col_dict = {left_col.name: left_col.data_type for left_col in left}

        for right_col in right:
            col_dict[right_col.name] = (
                col_dict.get(right_col.name, "") + right_col.data_type
            )

        return [Column(name, dtypes) for name, dtypes in col_dict.items()]

    def __eq__(self, other):
        if other.name != self.name:
            return False

        if len(other.columns) != len(self.columns):
            return False

        if not all(col in self.columns for col in other.columns):
            return False

        if len(self.children) != len(other.children):
            return False

        for child_name in self.children:
            if child_name not in other.children:
                return False

            if self.children[child_name] != other.children[child_name]:
                return False

        return True

    def __hash__(self):
        return hash((self.name, *sorted((c.name, c.data_type) for c in self.columns)))

    def __add__(self, other: Self) -> Self:
        merged_cols = self._merge_columns(self.columns, other.columns)
        return self.__class__(
            name=self.name,
            columns=merged_cols,
        )
