import axios from "axios";
import type { ChatMessage, ChatResponse, HealthResponse } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
}

export async function sendChat(messages: ChatMessage[]): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", { messages });
  return data;
}
