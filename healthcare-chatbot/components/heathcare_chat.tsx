"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Calendar, Clock, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar } from "@/components/ui/avatar";

export function HealthcareChat() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [messages, setMessages] = useState<{ id: string; role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState(""); // State for textarea input
  const [isLoading, setIsLoading] = useState(false); // Loading state for API call

  // Scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle form submission
  const handleSend = async () => {
    if (!input.trim()) return; // Ignore empty input

    const userMessage = { id: Date.now().toString(), role: "user" as const, content: input };
    setMessages((prev) => [...prev, userMessage]); // Add user message to chat
    setInput(""); // Clear textarea
    setShowWelcome(false); // Hide welcome message
    setIsLoading(true); // Show loading state

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to get response");
      }

      // Add assistant response to messages
      const assistantMessage = { id: (Date.now() + 1).toString(), role: "assistant" as const, content: data.answer || data };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 2).toString(),
        role: "assistant" as const,
        content: `Error: ${error instanceof Error ? error.message : "Something went wrong"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false); // Reset loading state
    }
  };

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent newline
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <h2 className="font-semibold">MediChat - Healthcare Assistant</h2>
        <p className="text-sm text-muted-foreground">
          Schedule appointments, get health info, or find clinic details
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {showWelcome && messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-4">
            <Avatar className="h-16 w-16 bg-primary/10">
              <Calendar className="h-8 w-8 text-primary" />
            </Avatar>
            <h3 className="text-xl font-semibold">Welcome to MediChat</h3>
            <p className="text-muted-foreground max-w-md">
              I’m here to help you schedule appointments, answer health prompts, and provide clinic information.
              What can I assist you with today?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 w-full max-w-lg mt-4">
              <Button variant="outline" className="flex items-center justify-start gap-2" disabled>
                <Calendar className="h-4 w-4" />
                <span>Appointment</span>
              </Button>
              <Button variant="outline" className="flex items-center justify-start gap-2" disabled>
                <Clock className="h-4 w-4" />
                <span>Check availability</span>
              </Button>
              <Button variant="outline" className="flex items-center justify-start gap-2" disabled>
                <MapPin className="h-4 w-4" />
                <span>Find location</span>
              </Button>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg p-4">
              <Loader2 className="h-5 w-5 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-slate-200">
        <div className="flex gap-2">
          <Textarea
            placeholder="Ask about appointments, health info, or clinic details..."
            className="flex-1 min-h-[60px] max-h-[120px]"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <Button size="icon" onClick={handleSend} disabled={isLoading || !input.trim()}>
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </Button>
        </div>
      </div>
    </div>
  );
}