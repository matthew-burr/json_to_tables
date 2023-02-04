import pytest

import src.table as tbl


@pytest.fixture
def simple_table():
    return tbl.Table(
        name="simple",
        columns=[
            tbl.Column("col1", tbl.DataType("int")),
            tbl.Column("col2", tbl.DataType("str")),
            tbl.Column("col3", tbl.DataType("bool")),
        ],
    )


@pytest.fixture
def other_table_name():
    return "simple"


DEFAULT_OTHER_COLUMNS = {
    "col1": "int",
    "col2": "str",
    "col3": "bool",
}


@pytest.fixture
def other_columns():
    return DEFAULT_OTHER_COLUMNS


@pytest.fixture
def other_table(other_table_name, other_columns):
    return tbl.Table(
        name=other_table_name,
        columns=[
            tbl.Column(name, tbl.DataType(dtype))
            for name, dtype in other_columns.items()
        ],
    )


@pytest.mark.parametrize(
    "other_table_name, want",
    [
        ("simple", True),
        ("other", False),
    ],
    ids=["same name", "different name"],
)
def test_table_eq__name(simple_table, other_table, want):
    got = other_table == simple_table
    assert got is want


@pytest.mark.parametrize(
    "other_columns,want",
    [
        (DEFAULT_OTHER_COLUMNS, True),
        ({"col1": "int"}, False),
        (
            {
                "col1": "int",
                "col2": "int",
                "col3": "int",
            },
            False,
        ),
        (
            {
                "col1": "int",
                "col3": "bool",
                "col2": "str",
            },
            True,
        ),
    ],
    ids=[
        "identical",
        "different column count",
        "different column types",
        "different column order",
    ],
)
def test_table_eq__columns(simple_table, other_table, want):
    got = other_table == simple_table
    assert got is want


@pytest.mark.parametrize(
    "col1,col2,want",
    [
        (tbl.Column("a", ""), tbl.Column("a", ""), True),
        (tbl.Column("a", ""), tbl.Column("b", ""), False),
        (tbl.Column("a", "int"), tbl.Column("a", "str"), False),
    ],
)
def test_col_eq(col1, col2, want):
    got = col1 == col2
    assert want is got
