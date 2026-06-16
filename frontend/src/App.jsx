import { useState } from "react";
import { recommend } from "./api.js";

const EXAMPLES = [
  "90s books about car chases",
  "something melancholic about memory and loss",
  "sci-fi with a strong female lead",
  "highly rated fantasy from the 2000s",
];

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

  return (
    <div className="page">
      <header className="header">
        <h1>Talk to your books</h1>
        <p className="subtitle">
          Ask in plain language — a hybrid SQL + semantic agent finds and justifies the picks.
        </p>
      </header>

      <form className="search" onSubmit={onSubmit}>
        <input
          type="text"
          value={question}
          placeholder="e.g. something melancholic about memory and loss"
          onChange={(e) => setQuestion(e.target.value)}
          autoFocus
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Thinking…" : "Recommend"}
        </button>
      </form>

      <div className="examples">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            className="chip"
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

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="results">
          <div className="meta">
            <span className={`badge badge-${result.intent.toLowerCase()}`}>
              {result.intent}
            </span>
            <span className="count">{result.picks.length} picks</span>
          </div>

          {result.generated_sql && (
            <details className="sql" open>
              <summary>Generated SQL</summary>
              <pre>{result.generated_sql}</pre>
            </details>
          )}

          {result.picks.length === 0 && (
            <p className="empty">No matches found. Try rephrasing.</p>
          )}

          <ul className="cards">
            {result.picks.map((book) => (
              <li className="card" key={book.isbn13}>
                {book.thumbnail ? (
                  <img
                    className="cover"
                    src={hiResCover(book.thumbnail)}
                    alt={book.title}
                    loading="lazy"
                    onError={(e) => {
                      if (e.currentTarget.src !== book.thumbnail) {
                        e.currentTarget.src = book.thumbnail;
                      }
                    }}
                  />
                ) : (
                  <div className="cover cover-empty">No cover</div>
                )}
                <div className="card-body">
                  <h3>{book.title}</h3>
                  <p className="author">
                    {book.authors}
                    {book.published_year ? ` · ${book.published_year}` : ""}
                    {book.average_rating ? ` · ★ ${book.average_rating}` : ""}
                  </p>
                  <p className="why-label">Why this pick</p>
                  <p className="why">{book.justification}</p>
                  {book.description && (
                    <details className="desc">
                      <summary>Description</summary>
                      <p>{book.description}</p>
                    </details>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
