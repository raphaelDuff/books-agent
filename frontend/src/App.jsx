import { useState } from "react";
import { recommend } from "./api.js";

const EXAMPLES = [
  "90s books about car chases",
  "something melancholic about memory and loss",
  "sci-fi with a strong female lead",
  "highly rated fantasy from the 2000s",
];

// Plain-language framing for each routing decision — the transparency principle,
// said in a human voice instead of a bare badge.
const INTENT_COPY = {
  STRUCTURED: {
    said: "Read as a structured search — narrowing the shelves by concrete facts.",
    tab: "Structured",
    cls: "tab-structured",
  },
  SEMANTIC: {
    said: "Read as a semantic search — matching by meaning and mood, not keywords.",
    tab: "Semantic",
    cls: "tab-semantic",
  },
  HYBRID: {
    said: "Read as a hybrid — a mood, then narrowed by the hard filters underneath it.",
    tab: "Hybrid",
    cls: "tab-hybrid",
  },
};

// Request a larger, sharper image from Google Books thumbnails (the dataset's
// URLs default to a low-res image and an HTTP page-curl overlay). Bumping the
// zoom level is unreliable — Google returns a blank placeholder for many books
// at zoom=2 — so we keep the known-good zoom=1 render and ask for a wider image
// via the w= parameter, which reliably yields a higher-resolution cover.
function hiResCover(url) {
  if (!url) return url;
  let out = url.replace(/^http:\/\//, "https://").replace(/&edge=curl/, "");
  if (/[?&]zoom=/.test(out)) out = out.replace(/([?&]zoom=)\d+/, "$11");
  if (!/[?&]w=/.test(out)) out += "&w=400";
  return out;
}

function Cover({ book }) {
  if (!book.thumbnail) {
    return (
      <div className="cover-art cover-empty" aria-hidden="true">
        No cover
      </div>
    );
  }
  return (
    <img
      className="cover-art"
      src={hiResCover(book.thumbnail)}
      alt={`Cover of ${book.title}`}
      width={140}
      loading="lazy"
      onError={(e) => {
        if (e.currentTarget.src !== book.thumbnail) {
          e.currentTarget.src = book.thumbnail;
        }
      }}
    />
  );
}

function Entry({ book, rank }) {
  const meta = [
    book.authors,
    book.published_year ? String(book.published_year) : null,
  ].filter(Boolean);

  return (
    <li
      className="entry enter"
      style={{ "--stagger": `${(rank - 1) * 70}ms` }}
    >
      <span className="rank" aria-hidden="true">
        {rank}
      </span>
      <a
        className="cover-link"
        href={`https://books.google.com/books?vid=ISBN${book.isbn13}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <Cover book={book} />
      </a>
      <div className="entry-body">
        <h3 className="title">{book.title}</h3>
        <p className="byline">
          {meta.map((part, i) => (
            <span key={i}>
              {i > 0 && <span className="sep" aria-hidden="true">·&nbsp;</span>}
              {part}
            </span>
          ))}
          {book.average_rating ? (
            <span className="rating" title="Average rating">
              <span aria-hidden="true">★</span>
              {Number(book.average_rating).toFixed(2)}
            </span>
          ) : null}
        </p>
        <p className="why">{book.justification}</p>
        {book.description && (
          <details className="desc">
            <summary>Full description</summary>
            <p>{book.description}</p>
          </details>
        )}
      </div>
    </li>
  );
}

function SkeletonEntry() {
  return (
    <div className="skeleton" aria-hidden="true">
      <div className="sk-rank" />
      <div className="sk-cover" />
      <div className="sk-body">
        <div className="sk-line w-title" />
        <div className="sk-line w-meta" />
        <div className="sk-line w-1" />
        <div className="sk-line w-2" />
      </div>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function submit(q) {
    const query = (q ?? question).trim();
    if (!query || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await recommend(query, threadId);
      setResult(data);
      setThreadId(data.thread_id);
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    submit();
  }

  const intent = result && (INTENT_COPY[result.intent] || INTENT_COPY.HYBRID);
  const hasPicks = result && result.picks.length > 0;

  return (
    <>
      <header className="cover">
        <div className="cover-inner">
          <h1 className="wordmark">
            The&nbsp;<em>well-read</em>&nbsp;agent
          </h1>
          <p className="tagline">
            Tell it what you’re in the mood for, in plain language. It reads your
            request, searches the shelves by fact and by feeling, and hands back a
            short, ranked list — each pick with a reason.
          </p>

          <form className="ask" onSubmit={onSubmit}>
            <div className="ask-field">
              <label className="sr-only" htmlFor="q">
                Describe the book you want
              </label>
              <input
                id="q"
                type="text"
                value={question}
                placeholder="e.g. something melancholic about memory and loss"
                onChange={(e) => setQuestion(e.target.value)}
                autoFocus
              />
            </div>
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? "Reading…" : "Recommend"}
            </button>
          </form>

          <div className="prompts">
            <span className="prompts-lead">Try —</span>
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                className="prompt"
                type="button"
                onClick={() => {
                  setQuestion(ex);
                  submit(ex);
                }}
                disabled={loading}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="reading">
        {error && (
          <div className="error" role="alert">
            <span aria-hidden="true">⚠</span>
            <span>
              <strong>That request didn’t go through.</strong> {error} Try
              rephrasing, or pick one of the prompts above.
            </span>
          </div>
        )}

        {loading && !result && (
          <div aria-live="polite" aria-busy="true">
            <SkeletonEntry />
            <SkeletonEntry />
            <SkeletonEntry />
          </div>
        )}

        {!loading && !result && !error && (
          <div className="firstrun">
            <p>
              Ask for a vibe, an era, a feeling, or a hard constraint — the more
              specific the request, the sharper the shelf.
            </p>
          </div>
        )}

        {result && (
          <>
            <section className="read-strip" aria-label="How the request was read">
              <p className="read-line">
                <span className="read-said">{intent.said}</span>
                <span className={`tab ${intent.cls}`}>{intent.tab}</span>
                {hasPicks && (
                  <span className="count">
                    {result.picks.length} pick{result.picks.length === 1 ? "" : "s"}
                  </span>
                )}
              </p>

              {result.generated_sql && (
                <details className="sql" open>
                  <summary>Generated SQL</summary>
                  <pre>{result.generated_sql}</pre>
                </details>
              )}
            </section>

            {hasPicks ? (
              <ol className="shelf">
                {result.picks.map((book, i) => (
                  <Entry key={book.isbn13 || i} book={book} rank={i + 1} />
                ))}
              </ol>
            ) : (
              <p className="no-matches">
                Nothing on the shelf matched that one. Try loosening a constraint
                or describing the feeling differently.
              </p>
            )}
          </>
        )}
      </main>

      <footer className="colophon">
        Searches ~6,800 books by structured filters and semantic similarity, then{" "}
        <b>ranks and justifies</b> the picks. The generated SQL above is shown for
        transparency.
      </footer>
    </>
  );
}
