import { FormEvent, useEffect, useRef, useState } from "react";
import { checkHealth, sendChat } from "../api";
import type { ChatMessage, Recommendation } from "../types";

interface MessageBubble {
  role: "user" | "assistant";
  content: string;
  recommendations?: Recommendation[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<MessageBubble[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [online, setOnline] = useState<boolean | null>(null);
  const [ended, setEnded] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkHealth()
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading || ended) return;

    const nextMessages: MessageBubble[] = [...messages, { role: "user", content: trimmed }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const payload: ChatMessage[] = nextMessages.map(({ role, content }) => ({ role, content }));
      const response = await sendChat(payload);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.reply,
          recommendations: response.recommendations,
        },
      ]);
      if (response.end_of_conversation) setEnded(true);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, the assistant is unavailable right now." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function resetChat() {
    setMessages([]);
    setEnded(false);
    setInput("");
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">SHL Assessment Recommender</h1>
          <p className="text-sm text-slate-400">
            Describe a hiring need and get a catalog-grounded SHL shortlist.
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            online ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
          }`}
        >
          {online === null ? "Checking..." : online ? "API Online" : "API Offline"}
        </span>
      </header>

      <main className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-700 p-6 text-sm text-slate-400">
              Try: "Hiring a mid-level Java developer with Spring and SQL experience."
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={index}
              className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                message.role === "user"
                  ? "ml-auto bg-indigo-600 text-white"
                  : "bg-slate-800 text-slate-100"
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.recommendations && message.recommendations.length > 0 && (
                <ul className="mt-3 space-y-2 border-t border-slate-700 pt-3">
                  {message.recommendations.map((rec) => (
                    <li key={rec.url} className="rounded-lg bg-slate-900/70 p-2">
                      <a
                        href={rec.url}
                        target="_blank"
                        rel="noreferrer"
                        className="font-medium text-indigo-300 hover:underline"
                      >
                        {rec.name}
                      </a>
                      <div className="text-xs text-slate-400">Type: {rec.test_type}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
          {loading && <div className="text-sm text-slate-400">Assistant is thinking...</div>}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-800 p-4">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading || ended}
              placeholder={ended ? "Conversation ended" : "Describe the role or refine the shortlist..."}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none ring-indigo-500 focus:ring-2 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || ended || !input.trim()}
              className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              Send
            </button>
            <button
              type="button"
              onClick={resetChat}
              className="rounded-xl border border-slate-700 px-4 py-3 text-sm text-slate-300 hover:bg-slate-800"
            >
              Reset
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
