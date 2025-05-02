export const maxDuration = 60;

export async function POST(req: Request) {
  const apiUrl = process.env.FAST_API_URL! + "/recommend";
  const { messages } = await req.json();
  const user_query = messages?.[messages.length - 1]?.content[0]?.text || "";

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.FAST_API_KEY ?? "",
    },
    body: JSON.stringify({ user_query }),
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/plain",
      "x-vercel-ai-data-stream": "v1",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
