import { openai } from "@ai-sdk/openai"
import { streamText } from "ai"

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

export async function POST(req: Request) {
  const { messages } = await req.json()

  const result = streamText({
    model: openai("gpt-4o"),
    system: `You are a helpful healthcare assistant chatbot named MediChat. 
    Your primary functions are:
    1. Help users schedule medical appointments
    2. Provide general health information
    3. Answer questions about clinic services and locations
    
    When scheduling appointments:
    - Ask for the type of appointment they need
    - Ask for preferred date and time
    - Confirm appointment details
    
    Always be professional, empathetic, and concise. 
    Do not provide specific medical diagnoses or treatment recommendations.
    Always clarify that you are an AI assistant and not a medical professional.
    
    For this demo, simulate appointment scheduling but make it clear this is a demonstration.`,
    messages,
  })

  return result.toDataStreamResponse()
}

