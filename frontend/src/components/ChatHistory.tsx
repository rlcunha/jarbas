import React from "react";
import { ChatResponse } from "../models/chatModels";

interface ChatHistoryProps {
  history: ChatResponse[];
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ history }) => {
  return (
    <div className="space-y-4 mt-4">
      {history.filter(chat => chat.question).map((chat, index) => (
        <div key={index} className="p-4 border border-gray-300 rounded">
          <div className="mb-2">
            <p className="font-bold">Pergunta:</p>
            <p>{chat.question}</p>
          </div>
          <div>
            <p className="font-bold mt-2">Resposta:</p>
            {chat.text_response ? (
              <>
                {chat.avatar_response && (
                  <div className="mb-2">
                    <img 
                      src={chat.avatar_response} 
                      alt="Avatar da resposta"
                      className="w-12 h-12 rounded-full"
                    />
                  </div>
                )}
                <p>{chat.text_response.text}</p>
                <div className="mt-2 text-sm text-gray-500">
                  <p>Confiança: {(chat.text_response.confidence * 100).toFixed(1)}%</p>
                  {chat.text_response.metadata && (
                    <p>Modelo: {chat.text_response.metadata.model}</p>
                  )}
                </div>
              </>
            ) : (
              <p className="text-gray-500">Aguardando resposta...</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatHistory;