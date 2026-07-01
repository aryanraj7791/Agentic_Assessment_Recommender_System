export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Recommendation {
  name: string;
  url: string;
  test_type: string;
}

export interface ChatResponse {
  reply: string;
  recommendations: Recommendation[];
  end_of_conversation: boolean;
}

export interface HealthResponse {
  status: string;
}
