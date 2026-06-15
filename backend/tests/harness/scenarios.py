"""Reproducible scenarios — one per distinctive path through the graph.

Each exercises the full compiled graph deterministically: the scripted LLM,
SQL repo, vector repo and embeddings make every run identical, so the metrics
measure graph *mechanics* (routing, the repair loop, hybrid allowlist, dedup),
not model variance.
"""

from __future__ import annotations

from app.application.service_ports.llm_service import IntentClassification
from app.domain.value_objects import Intent
from tests.harness.fakes import make_book
from tests.harness.types import Scenario, SqlStep

# A small, stable book set referenced across scenarios.
B1 = make_book("111", "The Long Drive", "A melancholic road trip across the 90s.")
B2 = make_book("222", "Fast Lanes", "High-octane car chases and heists.")
B3 = make_book("333", "Quiet Memory", "A meditation on loss and remembrance.")


SCENARIOS: list[Scenario] = [
    # 1) STRUCTURED — pure SQL, straight to rank.
    Scenario(
        id="structured_sql_only",
        question="books rated above 4.5 published in the 1990s",
        classify=IntentClassification(
            intent=Intent.STRUCTURED,
            sql="SELECT * FROM books WHERE average_rating > 4.5",
        ),
        sql_steps=(SqlStep(rows=(B1, B2)),),
        expect_intent="STRUCTURED",
        expect_route=("classify_intent", "sql_search", "rank"),
        expect_generated_sql=True,
        expect_sql_attempts=1,
        expect_pick_isbns=("111", "222"),
        expect_recall_isbns=frozenset({"111", "222"}),
    ),
    # 2) SEMANTIC — pure vector search, no SQL, no allowlist.
    Scenario(
        id="semantic_only",
        question="something melancholic about memory and loss",
        classify=IntentClassification(
            intent=Intent.SEMANTIC, semantic_query="melancholy, memory, loss"
        ),
        semantic_books=(B3, B1),
        expect_intent="SEMANTIC",
        expect_route=("classify_intent", "semantic_search", "rank"),
        expect_generated_sql=False,
        expect_pick_isbns=("333", "111"),
        expect_recall_isbns=frozenset({"333"}),
    ),
    # 3) HYBRID — SQL narrows to an allowlist, semantic ranks within it.
    Scenario(
        id="hybrid_sql_then_semantic",
        question="90s books about car chases that feel melancholic",
        classify=IntentClassification(
            intent=Intent.HYBRID,
            sql="SELECT * FROM books WHERE published_year BETWEEN 1990 AND 1999",
            semantic_query="melancholic car chases",
        ),
        sql_steps=(SqlStep(rows=(B1, B2)),),
        semantic_books=(B3, B1),  # B3 not in allowlist, B1 is
        expect_intent="HYBRID",
        expect_route=("classify_intent", "sql_search", "semantic_search", "rank"),
        expect_generated_sql=True,
        expect_sql_attempts=1,
        # candidates = semantic ([333,111]) + sql ([111,222]), deduped in order
        expect_pick_isbns=("333", "111", "222"),
    ),
    # 4) SQL fails once, repair fixes it, then succeeds.
    Scenario(
        id="sql_fail_then_repair",
        question="books by Murakami after 2000",
        classify=IntentClassification(
            intent=Intent.STRUCTURED,
            sql="SELECT * FROM books WHERE authr ILIKE '%murakami%'",  # typo
        ),
        sql_steps=(
            SqlStep(error='column "authr" does not exist'),
            SqlStep(rows=(B1,)),
        ),
        repairs=("SELECT * FROM books WHERE authors ILIKE '%murakami%'",),
        expect_intent="STRUCTURED",
        expect_route=(
            "classify_intent",
            "sql_search",
            "repair_sql",
            "sql_search",
            "rank",
        ),
        expect_generated_sql=True,
        expect_sql_attempts=2,  # initial + one repair
        expect_pick_isbns=("111",),
    ),
    # 5) SQL fails twice — retry budget exhausted, proceeds without results.
    Scenario(
        id="sql_fail_exhausted",
        question="malformed structured query",
        classify=IntentClassification(
            intent=Intent.STRUCTURED, sql="SELECT bogus FROM books"
        ),
        sql_steps=(
            SqlStep(error="syntax error at or near 'bogus'"),
            SqlStep(error="still broken after repair"),
        ),
        repairs=("SELECT also_bogus FROM books",),
        expect_intent="STRUCTURED",
        expect_route=(
            "classify_intent",
            "sql_search",
            "repair_sql",
            "sql_search",
            "rank",
        ),
        expect_generated_sql=True,  # set even on failure
        expect_sql_attempts=2,  # no infinite loop
        expect_pick_isbns=(),  # no candidates -> no picks
    ),
    # 6) Dedup — overlapping semantic and SQL candidate sets collapse by isbn13.
    Scenario(
        id="hybrid_dedup",
        question="overlapping candidate sets",
        classify=IntentClassification(
            intent=Intent.HYBRID,
            sql="SELECT * FROM books",
            semantic_query="anything",
        ),
        sql_steps=(SqlStep(rows=(B2, B3)),),
        semantic_books=(B1, B2),  # B2 appears in both sources
        expect_intent="HYBRID",
        expect_route=("classify_intent", "sql_search", "semantic_search", "rank"),
        # semantic [111,222] + sql [222,333] -> deduped [111,222,333]
        expect_pick_isbns=("111", "222", "333"),
    ),
]
