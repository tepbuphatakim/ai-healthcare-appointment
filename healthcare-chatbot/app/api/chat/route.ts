import { streamText } from "ai";

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Extract the latest user message as the query
  const latestMessage = messages[messages.length - 1]?.content || "";
  if (!latestMessage) {
    return new Response(JSON.stringify({ error: "No message provided" }), { status: 400 });
  }

  try {
    // Make a fetch request to your local RAG endpoint
    const response = await fetch("http://localhost:5000/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: latestMessage,
      }),
    });

    if (!response.ok) {
      throw new Error(`RAG system error: ${response.status} - ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    // Stream the response from the local endpoint
    const result = streamText({
      async *generator() {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              if (buffer) yield buffer; // Yield any remaining content
              break;
            }

            // Decode the chunk and append to buffer
            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            // Split by sentence boundaries or newlines for natural streaming
            const parts = buffer.split(/(?<=[.!?])\s+|\n/);
            buffer = parts.pop() || ""; // Keep incomplete part in buffer

            for (const part of parts) {
              if (part.trim()) yield part.trim(); // Yield non-empty parts
            }
          }
        } catch (err) {
          console.error("Error in generator:", err);
          yield `Error: Unable to stream response - ${err.message}`;
        } finally {
          reader.releaseLock();
        }
      },
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error("POST error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}