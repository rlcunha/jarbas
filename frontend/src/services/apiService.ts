import axios from "axios";
import { QuestionRequest, ChatResponse } from "../models/chatModels";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1/chat";

export const getResponse = async (
  question: string,
  user_id: string = "default_user",
  context: object = {}
): Promise<ChatResponse> => {
  const url = `${API_BASE_URL}/ask`;
  console.log("Sending request to:", url);
  console.log("Request payload:", { question, user_id, context });

  try {
    const response = await axios.post<ChatResponse>(
    url,
    {
      question,
      user_id,
      context
    },
    {
      headers: {
        "Content-Type": "application/json",
        "accept": "application/json"
      },
      timeout: 60000,
      withCredentials: true,
      validateStatus: function (status) {
        return status >= 200 && status < 500;
      }
    }
    );

    console.log("Response status:", response.status);
    console.log("Full response data:", response.data);
    return response.data;
  } catch (error: any) {
    console.error("API Error Details:");
    if (error.response) {
      console.error("Status:", error.response.status);
      console.error("Data:", error.response.data);
      console.error("Headers:", error.response.headers);
    } else if (error.request) {
      console.error("Request:", error.request);
    } else {
      console.error("Message:", error.message);
    }
    console.error("Config:", error.config);
    throw new Error("Falha ao obter resposta do servidor. Por favor, verifique sua conexão e tente novamente.");
  }
};