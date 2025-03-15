import { streamText } from "ai";

export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const { question } = await req.json();

    if (!question || typeof question !== "string") {
      return new Response(JSON.stringify({ error: "No valid question provided" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const response = await fetch("http://localhost:5000/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`RAG system error: ${response.status} - ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    const result = streamText({
      async *generator() {
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              if (buffer) yield buffer;
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            const parts = buffer.split(/(?<=[.!?])\s+|\n/);
            buffer = parts.pop() || "";

            for (const part of parts) {
              if (part.trim()) yield part.trim();
            }
          }
        } catch (err) {
          yield `Error: Unable to stream response - ${err instanceof Error ? err.message : "Unknown error"}`;
        } finally {
          reader.releaseLock();
        }
      },
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error("POST error:", error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
