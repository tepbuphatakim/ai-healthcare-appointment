export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { doctor, patient_name, appointment_time } = body;

    if (!doctor || !patient_name || !appointment_time) {
      return new Response(JSON.stringify({ error: "Missing required fields" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const apiUrl = process.env.RAG_API_URL || "http://127.0.0.1:5000/api/book-appointment";
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doctor, patient_name, appointment_time }),
      signal: AbortSignal.timeout(25000),
    });

    if (!response.ok) {
      throw new Error(`Booking API error: ${response.status} - ${response.statusText}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Booking error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}