import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { ChatResponse } from "../models/chatModels";

interface ChatState {
  history: ChatResponse[];
  loading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  history: [],
  loading: false,
  error: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    startLoading(state) {
      state.loading = true;
      state.error = null;
    },
    addChatResponse(state, action: PayloadAction<ChatResponse>) {
      state.history.push(action.payload);
      state.loading = false;
    },
    setError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const { startLoading, addChatResponse, setError } = chatSlice.actions;
export default chatSlice.reducer;