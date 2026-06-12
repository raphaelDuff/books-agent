"""SELECT-only guard for LLM-generated SQL.

This is the ONLY write-protection on the text-to-SQL path (we run on the same
engine as the app, with no separate read-only role), so it is deliberately
strict and must be kept under test. It rejects anything that isn't a single,
comment-free read query and forces a row cap.
"""

import re

# Whole-word keywords that have no place in a read-only SELECT.
_FORBIDDEN = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
    "merge",
    "call",
    "copy",
    "attach",
    "vacuum",
    "into",  # blocks SELECT ... INTO
    "set",
    "commit",
    "rollback",
)
_FORBIDDEN_RE = re.compile(r"\b(" + "|".join(_FORBIDDEN) + r")\b", re.IGNORECASE)
_LIMIT_RE = re.compile(r"\blimit\b", re.IGNORECASE)


class UnsafeSqlError(ValueError):
    """Raised when LLM SQL fails the read-only guard."""


def guard_select(sql: str, max_limit: int) -> str:
    """Validate a single read-only SELECT and return it with a row cap applied.

    Raises:
        UnsafeSqlError: if the statement isn't a single comment-free SELECT/CTE.
    """
    if not sql or not sql.strip():
        raise UnsafeSqlError("Empty SQL.")

    text = sql.strip().rstrip(";").strip()

    if "--" in text or "/*" in text or "*/" in text:
        raise UnsafeSqlError("SQL comments are not allowed.")

    if ";" in text:
        raise UnsafeSqlError("Multiple statements are not allowed.")

    lowered = text.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise UnsafeSqlError("Only SELECT (or WITH ... SELECT) queries are allowed.")

    match = _FORBIDDEN_RE.search(text)
    if match:
        raise UnsafeSqlError(f"Forbidden keyword in SQL: {match.group(1)!r}.")

    if not _LIMIT_RE.search(text):
        text = f"{text} LIMIT {max_limit}"

    return text
