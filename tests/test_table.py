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


class TestDataType:
    @pytest.mark.parametrize(
        "initial_value,want",
        [
            ("Int", "int"),
            ("int", "int"),
            ("StR", "str"),
        ],
    )
    def test_casing(self, initial_value, want):
        got = str(tbl.NewDataType(initial_value))
        assert want == got

    def test_when_multi_type__sorted(self):
        want = "int|str"
        got = str(tbl.NewDataType("str|int"))
        assert want == got

    @pytest.mark.parametrize(
        "type_string,want",
        [
            ("int|int", "int"),
            ("Foo|foo", "foo"),
        ],
    )
    def test_when_type_string_has_dupes__no_dupes(self, type_string, want):
        got = str(tbl.NewDataType(type_string))
        assert want == got

    @pytest.mark.parametrize(
        "add_type,want",
        [
            ("bar", "bar|foo"),
            ("foo", "foo"),
            ("str|bar", "bar|foo|str"),
            (tbl.NewDataType("bar"), "bar|foo"),
        ],
    )
    def test_add__adds_only_new_types(self, add_type, want):
        got = str(tbl.NewDataType("foo") + add_type)
        assert want == got

    @pytest.mark.parametrize(
        "other,want_error",
        [
            ("str", False),
            (tbl.NewDataType("int"), False),
            (1, True),
        ],
    )
    def test_add_incorrect_arg_type__raises_error(self, other, want_error):
        if want_error:
            with pytest.raises(TypeError):
                tbl.NewDataType("") + other
        else:
            tbl.NewDataType("") + other

    @pytest.mark.parametrize(
        "test_str,should_equal",
        [
            ("foo", True),
            ("bar", False),
        ],
    )
    def test_eq__works_with_str(self, test_str, should_equal):
        if should_equal:
            assert tbl.NewDataType("foo") == test_str
        else:
            assert tbl.NewDataType("foo") != test_str

    @pytest.mark.parametrize("test_str", ["foo|bar", "bar|foo"])
    def test_eq__order_irrelevant(self, test_str):
        assert tbl.NewDataType("foo|bar") == test_str

    @pytest.mark.parametrize("test_str", ["Foo|Bar", "foo|bar"])
    def test_eq__case_insensitive(self, test_str):
        assert tbl.NewDataType("foo|bar") == test_str


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

    @pytest.mark.parametrize(
        "col,want",
        [
            (tbl.Column("a", tbl.DataType("int")), True),
            (tbl.Column("a", tbl.DataType("str")), False),
        ],
    )
    def test_in(self, col, want):
        cols = {
            tbl.Column("a", tbl.DataType("int")): None,
            tbl.Column("b", tbl.DataType("int")): None,
        }
        got = col in cols
        assert want == got


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
