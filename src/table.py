from dataclasses import dataclass
from typing import List, NewType, Self


DataType = NewType("DataType", str)


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
        col_dict = {
            left_col.name: {*left_col.data_type.split("|")} for left_col in left
        }
        for right_col in right:
            col_dict[right_col.name] = col_dict.get(right_col.name, set()).union(
                {*right_col.data_type.split("|")}
            )

        return [
            Column(name, DataType("|".join(sorted(dtypes))))
            for name, dtypes in col_dict.items()
        ]

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
