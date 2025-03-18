export const maxDuration = 30;

interface AppointmentRequest {
  session_id?: string;
  name?: string;
  doctor?: string;
  date?: string;
  time?: string;
}

export async function POST(req: Request) {
  try {
    const body: AppointmentRequest = await req.json();
    const flaskBody: Record<string, string> = {};
    if (body.session_id) flaskBody.session_id = body.session_id;
    if (body.name) flaskBody.name = body.name;
    if (body.doctor) flaskBody.doctor = body.doctor;
    if (body.date) flaskBody.date = body.date;
    if (body.time) flaskBody.time = body.time;

    const apiUrl = process.env.FLASK_API_URL || "http://127.0.0.1:5000/api/book-appointment";
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(flaskBody),
      signal: AbortSignal.timeout(25000),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Flask API error: ${response.status}`);
    }

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Booking error:", error);
    const status = error instanceof Error && error.message.includes("timeout") ? 504 : 500;
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
        message: "Failed to process booking request",
      }),
      { status, headers: { "Content-Type": "application/json" } }
    );
  }
}