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

// External API URL (move to environment variable in production)
const API_URL = process.env.APPOINTMENT_API_URL || "http://127.0.0.1:8000/appointments";

export async function POST(req: Request) {
  try {
    // Parse the incoming request body
    const body: AppointmentRequest = await req.json();

    // Validate required fields with stricter checks
    const { appointmentType, preferredDate, preferredTime } = body;
    if (!appointmentType?.trim() || !preferredDate?.trim() || !preferredTime?.trim()) {
      return NextResponse.json(
        { error: "Missing or empty required fields: appointmentType, preferredDate, or preferredTime" },
        { status: 400 }
      );
    }

    // Optional: Validate date and time formats
    if (!/^\d{4}-\d{2}-\d{2}$/.test(preferredDate)) {
      return NextResponse.json(
        { error: "Invalid date format. Use YYYY-MM-DD" },
        { status: 400 }
      );
    }
    if (!/^\d{2}:\d{2}$/.test(preferredTime)) {