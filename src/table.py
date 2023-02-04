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
        merged = self.__class__(
            name=self.name,
            columns=[
                *self.columns,
            ],
        )

        for other_col in other.columns:
            my_col = next((s for s in merged.columns if s.name == other_col.name), None)
            if my_col:
                if my_col.data_type == other_col.data_type:
                    continue

                my_col.data_type = "|".join(
                    sorted(
                        {*my_col.data_type.split("|"), *other_col.data_type.split("|")}
                    )
                )
            else:
                merged.columns.append(other_col)

        return merged

    def __eq__(self, other):
        if other.name != self.name:
            return False

        if len(other.columns) != len(self.columns):
            return False

        return all(col in self.columns for col in other.columns)

    def __hash__(self):
        return hash((self.name, *sorted((c.name, c.data_type) for c in self.columns)))
