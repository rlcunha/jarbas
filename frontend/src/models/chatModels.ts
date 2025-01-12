export interface QuestionRequest {
  question: string;
  user_id: string;
  context: Record<string, any>;
}

export interface UsageDetails {
  completion_tokens: number;
  prompt_tokens: number;
  total_tokens: number;
  prompt_tokens_details: {
    cached_tokens: number;
    audio_tokens: number;
  };
  completion_tokens_details: {
    reasoning_tokens: number;
    audio_tokens: number;
    accepted_prediction_tokens: number;
    rejected_prediction_tokens: number;
  };
}

export interface LLMResponse {
  text: string;
  confidence: number;
  metadata: {
    model: string;
    usage: UsageDetails;
  };
}

export interface ChatResponse {
  question: string;
  text_response: LLMResponse;
  avatar_response: any | null;
  timestamp: string;
  cache_hit: boolean;
}