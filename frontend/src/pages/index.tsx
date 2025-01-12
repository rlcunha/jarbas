import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState, AppDispatch } from "../store/store";
import { startLoading, addChatResponse, setError } from "../store/chatSlice";
import { getResponse } from "../services/apiService";
import ChatForm from "../components/ChatForm";
import ChatHistory from "../components/ChatHistory";

const Home: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { history, loading, error } = useSelector((state: RootState) => state.chat);
  
  React.useEffect(() => {
    console.log('Component mounted');
    return () => console.log('Component unmounted');
  }, []);

  React.useEffect(() => {
    console.log('History updated:', history);
  }, [history]);

  const handleQuestionSubmit = async (question: string) => {
    dispatch(startLoading());
    try {
      const response = await getResponse(question);
      dispatch(addChatResponse(response));
    } catch (err: any) {
      dispatch(setError(err.message));
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chat com IA</h1>
      <ChatForm onSubmit={handleQuestionSubmit} />
      {error && <p className="text-red-500 mt-2">{error}</p>}
      <ChatHistory history={history} />
    </div>
  );
};

export default Home;