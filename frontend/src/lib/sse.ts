import type { SSEEvent } from "./types";

export async function* streamJob(jobId: string): AsyncGenerator<SSEEvent> {
  const res = await fetch(`/api/jobs/${jobId}/stream`, {
    headers: { Accept: "text/event-stream" },
  });

  if (!res.ok || !res.body) {
    throw new Error(`SSE connection failed: HTTP ${res.status}`);
  }

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += value;
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        const raw = line.slice(6).trim();
        if (!raw) continue; // ping or empty keep-alive

        try {
          const event: SSEEvent = JSON.parse(raw);
          yield event;
          if (event.status === "done" || event.status === "error") return;
        } catch {
          // ignore malformed JSON
        }
      }
    }
  } finally {
    reader.cancel();
  }
}
