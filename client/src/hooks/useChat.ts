import { useState, useEffect, useCallback, useRef } from "react";
import type { Message } from "../App";
import { sendMessage, ApiClientError } from "../api/client";

export interface UseChatReturn {
  messages: Message[];
  loading: boolean;
  error: string | null;
  sendUserMessage: (text: string) => Promise<void>;
  clearError: () => void;
  clearChat: () => void;
  retryLastMessage: () => Promise<void>;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastUserMessageRef = useRef<string>("");

  // Load messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem("climateLens_messages");
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        if (Array.isArray(parsed)) {
          setMessages(parsed);
        }
      } catch (error) {
        console.error("Failed to parse saved messages:", error);
      }
    }
  }, []);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("climateLens_messages", JSON.stringify(messages));
    }
  }, [messages]);

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const updateLastMessage = useCallback((updates: Partial<Message>) => {
    setMessages((prev) => {
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      if (lastIndex >= 0) {
        newMessages[lastIndex] = { ...newMessages[lastIndex], ...updates };
      }
      return newMessages;
    });
  }, []);

  const sendUserMessage = useCallback(
    async (text: string) => {
      setError(null);
      lastUserMessageRef.current = text;

      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        text,
        timestamp: Date.now(),
      };
      addMessage(userMessage);

      // Add placeholder assistant message with loading state
      const assistantMessageId = (Date.now() + 1).toString();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: "assistant",
        text: "",
        timestamp: Date.now(),
        loading: true,
      };
      addMessage(assistantMessage);

      setLoading(true);

      try {
        const response = await sendMessage(text);

        // Update the assistant message with the real response
        updateLastMessage({
          text: response.answer,
          sources: response.sources,
          loading: false,
        });
      } catch (error) {
        let errorMessage = "An unexpected error occurred.";

        if (error instanceof ApiClientError) {
          errorMessage = error.message;
        }

        // Update the assistant message with error state
        updateLastMessage({
          text: `⚠️ ${errorMessage}`,
          loading: false,
          error: true,
        });

        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [addMessage, updateLastMessage],
  );

  const retryLastMessage = useCallback(async () => {
    if (lastUserMessageRef.current) {
      // Remove the last assistant message if it was an error
      setMessages((prev) => {
        const newMessages = [...prev];
        if (
          newMessages.length > 0 &&
          newMessages[newMessages.length - 1].role === "assistant" &&
          newMessages[newMessages.length - 1].error
        ) {
          newMessages.pop();
        }
        return newMessages;
      });

      await sendUserMessage(lastUserMessageRef.current);
    }
  }, [sendUserMessage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    localStorage.removeItem("climateLens_messages");
    setError(null);
    lastUserMessageRef.current = "";
  }, []);

  return {
    messages,
    loading,
    error,
    sendUserMessage,
    clearError,
    clearChat,
    retryLastMessage,
  };
}
