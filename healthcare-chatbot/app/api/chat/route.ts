export const maxDuration = 30; // Vercel timeout limit in seconds

export async function POST(req: Request) {
  try {
    // Parse the request body
    const body = await req.json();
    const prompt = body.prompt;

    // Validate prompt
    if (!prompt || typeof prompt !== "string" || !prompt.trim()) {
      return new Response(
        JSON.stringify({ error: "A valid prompt is required" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Make request to RAG API
    const apiUrl = "http://127.0.0.1:5000/api/query"; // Hardcoded for simplicity
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: prompt }),
    });

    if (!response.ok) {
      throw new Error(`RAG API error: ${response.status} - ${response.statusText}`);
    }

    // Get the response body as JSON or text
    const data = await response.json(); // Assuming the API returns JSON; use .text() if it’s plain text

    // Return the API response to the client
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("POST error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}