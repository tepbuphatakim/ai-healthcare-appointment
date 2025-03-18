export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const prompt = body.prompt;

    if (!prompt || typeof prompt !== "string" || !prompt.trim()) {
      return new Response(
        JSON.stringify({ error: "A valid prompt is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const apiUrl = process.env.RAG_API_URL || "http://127.0.0.1:5000/api/query";
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: prompt }),
      signal: AbortSignal.timeout(25000),
    });

    if (!response.ok) {
      throw new Error(`RAG API error: ${response.status} - ${response.statusText}`);
    }

    const data = await response.json();
    const answer = data.answer || "No answer returned from RAG API"; // Fallback if answer is missing

    // Return only the answer string
    return new Response(JSON.stringify({ answer }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("POST error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}