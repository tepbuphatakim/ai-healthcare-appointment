import { NextResponse } from "next/server";

// Define the expected request body structure
interface AppointmentRequest {
  appointmentType: string; // e.g., "General Checkup", "Specialist Visit"
  preferredDate: string;   // e.g., "2025-03-15"
  preferredTime: string;   // e.g., "10:30"
  patientName?: string;    // Optional, could be collected from user
  additionalNotes?: string; // Optional notes
}

// Define the response structure from the external API (adjust based on actual API)
interface AppointmentResponse {
  id: string;
  appointmentType: string;
  date: string;
  time: string;
  status: string;
  message?: string;
}

export async function POST(req: Request) {
  try {
    // Parse the incoming request body
    const body: AppointmentRequest = await req.json();

    // Validate required fields
    if (!body.appointmentType || !body.preferredDate || !body.preferredTime) {
      return NextResponse.json(
        { error: "Missing required fields: appointmentType, preferredDate, or preferredTime" },
        { status: 400 }
      );
    }

    // Construct the payload for the external API
    const appointmentPayload = {
      type: body.appointmentType,
      date: body.preferredDate,
      time: body.preferredTime,
      patient_name: body.patientName || "Unknown", // Default if not provided
      notes: body.additionalNotes || "",
    };

    // Make the request to the external API
    const response = await fetch("http://127.0.0.1:8000/appointments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(appointmentPayload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`External API error: ${response.status} - ${errorData.message || "Unknown error"}`);
    }

    // Parse the external API response
    const result: AppointmentResponse = await response.json();

    // Return a success response to the client
    return NextResponse.json({
      message: "Appointment created successfully",
      appointment: {
        id: result.id,
        type: result.appointmentType,
        date: result.date,
        time: result.time,
        status: result.status,
      },
    }, { status: 201 });

  } catch (error) {
    // Safely handle the error to avoid runtime issues
    console.error("Error creating appointment:", error);
    const errorMessage = error instanceof Error ? error.message : String(error) || "An unknown error occurred";
    return NextResponse.json(
      { error: "Failed to create appointment", details: errorMessage },
      { status: 500 }
    );
  }
}

// Optional: Add a GET method to check API status (for debugging)
export async function GET() {
  return NextResponse.json({ message: "Appointment API is active" }, { status: 200 });
}