import React, { useState } from "react";

interface ChatFormProps {
  onSubmit: (question: string) => Promise<void>;
}

const ChatForm: React.FC<ChatFormProps> = ({ onSubmit }) => {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);
    
    try {
      await onSubmit(question);
      setQuestion("");
    } catch (err) {
      setError("Erro ao enviar pergunta. Tente novamente.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Digite sua pergunta..."
          className="flex-1 p-2 border border-gray-300 rounded"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
          disabled={isLoading || !question.trim()}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Enviando...</span>
            </div>
          ) : (
            "Enviar"
          )}
        </button>
      </div>
      
      {error && (
        <div className="text-red-500 text-sm mt-1">
          {error}
        </div>
      )}
    </form>
  );
};

export default ChatForm;