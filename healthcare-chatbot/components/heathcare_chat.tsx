"use client";

import { useChat } from "@ai-sdk/react";
import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Calendar, Clock, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function HealthcareChat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: "/api/chat", // Points to the refined POST function
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Hide welcome message after first user message
  useEffect(() => {
    if (messages.some((m) => m.role === "user")) {
      setShowWelcome(false);
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-[600px]">
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <h2 className="font-semibold">MediChat - Healthcare Assistant</h2>
        <p className="text-sm text-muted-foreground">
          Schedule appointments, get health info, or find clinic details
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {showWelcome && (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-4">
            <Avatar className="h-16 w-16 bg-primary/10">
              <Calendar className="h-8 w-8 text-primary" />
            </Avatar>
            <h3 className="text-xl font-semibold">Welcome to MediChat</h3>
            <p className="text-muted-foreground max-w-md">
              I’m here to help you schedule appointments, answer health questions, and provide clinic information.
              What can I assist you with today?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 w-full max-w-lg mt-4">
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={() => {
                  handleInputChange({ target: { value: "I need to schedule an appointment" } } as any);
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
              >
                <Calendar className="h-4 w-4" />
                <span>Appointment</span>
              </Button>
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={() => {
                  handleInputChange({ target: { value: "What are your available time slots?" } } as any);
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
              >
                <Clock className="h-4 w-4" />
                <span>Check availability</span>
              </Button>
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={() => {
                  handleInputChange({ target: { value: "Where is your clinic located?" } } as any);
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
              >
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

              {/* Conditionally render appointment card based on assistant response */}
              {message.role === "assistant" && message.content.toLowerCase().includes("appointment") && (
                <Card className="mt-4 p-4 bg-background">
                  <div className="flex flex-col space-y-2">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">Appointment Demo (Simulated)</h4>
                      <Badge>Pending</Badge>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>March 15, 2025</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>10:30 AM</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span>Main Clinic, Floor 3</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      This is a demo. Contact the clinic to confirm real appointments.
                    </p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted max-w-[80%] rounded-lg p-4">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center">
            <div className="bg-destructive/10 text-destructive max-w-[80%] rounded-lg p-4">
              An error occurred: {error.message}. Please try again.
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-slate-200">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Textarea
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about appointments, health info, or clinic details..."
            className="flex-1 min-h-[60px] max-h-[120px]"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as any);
              }
            }}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-5 w-5" />
          </Button>
        </form>
      </div>
    </div>
  );
}