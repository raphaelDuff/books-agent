import pytest

from app.infra.persistence.sql_guard import UnsafeSqlError, guard_select

MAX_LIMIT = 50


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO books VALUES (1)",
        "UPDATE books SET title = 'x'",
        "DELETE FROM books",
        "DROP TABLE books",
        "ALTER TABLE books ADD COLUMN x int",
        "TRUNCATE books",
        "GRANT ALL ON books TO public",
        "SELECT * FROM books; DROP TABLE books",  # multi-statement
        "SELECT * FROM books -- comment",  # comment
        "SELECT * FROM books /* block */",  # block comment
        "SELECT * INTO other FROM books",  # SELECT INTO
        "",  # empty
        "   ",  # whitespace
        "WITH x AS (DELETE FROM books RETURNING *) SELECT * FROM x",  # CTE w/ write
    ],
)
def test_guard_rejects_unsafe_sql(sql):
    with pytest.raises(UnsafeSqlError):
        guard_select(sql, MAX_LIMIT)


def test_guard_allows_plain_select_and_injects_limit():
    out = guard_select("SELECT * FROM books WHERE published_year = 1999", MAX_LIMIT)
    assert out == "SELECT * FROM books WHERE published_year = 1999 LIMIT 50"


def test_guard_allows_cte_select():
    sql = "WITH top AS (SELECT * FROM books) SELECT * FROM top"
    out = guard_select(sql, MAX_LIMIT)
    assert out.lower().startswith("with")
    assert out.lower().endswith("limit 50")


def test_guard_keeps_existing_limit():
    sql = "SELECT * FROM books LIMIT 5"
    assert guard_select(sql, MAX_LIMIT) == sql


def test_guard_strips_trailing_semicolon():
    out = guard_select("SELECT * FROM books;", MAX_LIMIT)
    assert ";" not in out
    assert out.endswith("LIMIT 50")
