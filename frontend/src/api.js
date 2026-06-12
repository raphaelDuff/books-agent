// Thin client for the recommendation endpoint. Uses a relative URL so the Vite
// dev proxy forwards to the FastAPI backend.
export async function recommend(question, threadId) {
  const response = await fetch("/books/recommendations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, thread_id: threadId ?? null }),
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body?.detail?.message || message;
    } catch {
      // keep default message
    }
    throw new Error(message);
  }

  return response.json();
}
