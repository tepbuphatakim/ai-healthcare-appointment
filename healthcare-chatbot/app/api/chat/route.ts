import { streamText } from "ai";

export const maxDuration = 30; // Vercel timeout limit in seconds

export async function POST(req: Request) {
  try {
    // Parse and validate request body
    const body = await req.json();
    let prompt: string;

    // Extract prompt from either direct prompt or messages array
    if (body.prompt && typeof body.prompt === "string") {
      prompt = body.prompt;
    } else if (body.messages && Array.isArray(body.messages)) {
      const lastUserMessage = body.messages
        .filter((msg: any) => msg.role === "user")
        .pop();
      prompt = lastUserMessage?.content || "";
    } else {
      if (process.env.NODE_ENV === "development") {
        console.log("Validation failed: body is", body);
      }
      return new Response(JSON.stringify({ error: "No valid prompt or messages provided" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (process.env.NODE_ENV === "development") {
      console.log("Extracted prompt:", prompt);
    }

    if (!prompt.trim()) {
      return new Response(JSON.stringify({ error: "Prompt is empty" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Make request to external API
    const apiUrl = process.env.RAG_API_URL || "http://127.0.0.1:5000/api/query"; // Use env var with fallback
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: prompt }),
    });

    if (!response.ok) {
      throw new Error(`RAG system error: ${response.status} - ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    // Stream the response
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    const result = await streamText({
      async *generator() {
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              if (buffer.trim()) yield buffer.trim(); // Yield remaining buffer
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            // Split on sentence boundaries or newlines
            const parts = buffer.split(/(?<=[.!?])\s+|\n/);
            buffer = parts.pop() || ""; // Keep incomplete part in buffer

            for (const part of parts) {
              if (part.trim()) yield part.trim(); // Yield complete sentences
            }
          }
        } catch (err) {
          yield `Error: Unable to stream response - ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
          reader.releaseLock(); // Ensure reader is always released
        }
      },
    });

    return result.toDataStreamResponse();
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