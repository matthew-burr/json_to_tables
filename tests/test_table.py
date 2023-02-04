import pytest

import src.table as tbl


DEFAULT_NAME = "simple"
DEFAULT_COLUMNS = {
    "col1": "int",
    "col2": "str",
    "col3": "bool",
}


def _dict_to_columns(col_dict: dict[str, str]) -> list[tbl.Column]:
    return [tbl.Column(name, tbl.DataType(dtype)) for name, dtype in col_dict.items()]


@pytest.fixture
def simple_table():
    return tbl.Table(name=DEFAULT_NAME, columns=_dict_to_columns(DEFAULT_COLUMNS))


@pytest.fixture
def other_table_name():
    return "simple"


@pytest.fixture
def other_columns():
    return DEFAULT_COLUMNS


@pytest.fixture
def other_table(other_table_name, other_columns):
    return tbl.Table(name=other_table_name, columns=_dict_to_columns(other_columns))


class TestColumn:
    @pytest.mark.parametrize(
        "col1,col2,want",
        [
            (tbl.Column("a", ""), tbl.Column("a", ""), True),
            (tbl.Column("a", ""), tbl.Column("b", ""), False),
            (tbl.Column("a", "int"), tbl.Column("a", "str"), False),
        ],
    )
    def test_eq(self, col1, col2, want):
        got = col1 == col2
        assert want is got

    @pytest.mark.parametrize(
        "col1,col2,want",
        [
            (tbl.Column("a", ""), tbl.Column("a", ""), True),
            (tbl.Column("a", ""), tbl.Column("b", ""), False),
            (tbl.Column("a", "int"), tbl.Column("a", "str"), True),
        ],
    )
    def test_hash(self, col1, col2, want):
        got = hash(col1) == hash(col2)
        assert got == want


class TestTable:
    @pytest.mark.parametrize(
        "other_columns,want_table",
        [
            (
                {"col4": "int"},
                tbl.Table(
                    DEFAULT_NAME,
                    _dict_to_columns(dict(**DEFAULT_COLUMNS, col4=tbl.DataType("int"))),
                ),
            ),
            (
                {"col3": "bool"},
                tbl.Table(DEFAULT_NAME, _dict_to_columns(dict(**DEFAULT_COLUMNS))),
            ),
            (
                {"col3": "str"},
                tbl.Table(
                    DEFAULT_NAME,
                    _dict_to_columns(
                        {"col1": "int", "col2": "str", "col3": "bool|str"}
                    ),
                ),
            ),
        ],
        ids=[
            "add a column",
            "don't add existing column",
            "combines column data types when same name",
        ],
    )
    def test_merge(self, simple_table, other_table, want_table):
        got_table = simple_table.merge(other_table)
        assert want_table == got_table

    @pytest.mark.parametrize(
        "other_table_name,other_columns,want",
        [
            ("other", DEFAULT_COLUMNS, False),
            (DEFAULT_NAME, {"col1": "int"}, False),
            (DEFAULT_NAME, {"col1": "int", "col2": "str", "col4": "bool"}, False),
            (DEFAULT_NAME, {"col1": "int", "col2": "str", "col3": "foo"}, False),
            (DEFAULT_NAME, {"col3": "bool", "col2": "str", "col1": "int"}, True),
        ],
        ids=[
            "different name",
            "different number of columns",
            "different col names",
            "different col dtypes",
            "diffferent col order",
        ],
    )
    def test_hash(self, simple_table, other_table, want):
        got = hash(simple_table) == hash(other_table)
        assert want is got

    @pytest.mark.parametrize(
        "other_columns,want",
        [
            (DEFAULT_COLUMNS, True),
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
    def test_table_eq__columns(self, simple_table, other_table, want):
        got = other_table == simple_table
        assert got is want

    @pytest.mark.parametrize(
        "other_table_name, want",
        [
            ("simple", True),
            ("other", False),
        ],
        ids=["same name", "different name"],
    )
    def test_table_eq__name(self, simple_table, other_table, want):
        got = other_table == simple_table
        assert got is want
