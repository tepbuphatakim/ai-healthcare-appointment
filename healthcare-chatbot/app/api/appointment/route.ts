export const maxDuration = 30; // Vercel timeout limit in seconds

export async function POST(req: Request) {
  try {
    // Parse the request body
    const body = await req.json();
    const { name, doctor, date, time } = body;

    // Validate required fields
    if (!name || !doctor || !date || !time) {
      return new Response(
        JSON.stringify({ error: "Missing required fields: name, doctor, date, time" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Make request to Flask RAG API
    const apiUrl = "http://127.0.0.1:5000/api/book-appointment"; // Update this for production
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, doctor, date, time }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Booking error: ${response.status} - ${errorData.error || response.statusText}`);
    }

    // Get the response body as JSON
    const data = await response.json();

    // Return the API response to the client
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Booking error:", error);
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