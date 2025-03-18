"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar } from "@/components/ui/avatar";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ApiResponse {
  message?: string; // For /api/appointment and /api/book-appointment
  answer?: string;  // For /api/chat
  session_id?: string;
  confirmation?: string;
  document?: string;
  error?: string;
}

interface BookingData {
  patient_name?: string;
  doctor?: string;
  appointment_time?: string;
}

export function HealthcareChat() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [bookingSessionId, setBookingSessionId] = useState<string | null>(null);
  const [bookingData, setBookingData] = useState<BookingData>({});
  const [bookingStep, setBookingStep] = useState<"name" | "doctor" | "time" | "confirm" | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setShowWelcome(false);
    setIsLoading(true);

    try {
      if (!bookingSessionId) {
        // Regular chat mode
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: input }),
        });

        const data: ApiResponse = await response.json();
        if (!response.ok || data.error) {
          throw new Error(data.error || "Failed to get chat response");
        }

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.answer || "No response from chat API",
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        // Booking mode
        const updatedBookingData = { ...bookingData };
        let nextStep: "doctor" | "time" | "confirm" | null = null;

        switch (bookingStep) {
          case "name":
            updatedBookingData.patient_name = input;
            nextStep = "doctor";
            setMessages((prev) => [
              ...prev,
              { id: (Date.now() + 1).toString(), role: "assistant", content: "Please enter the doctor's name." },
            ]);
            break;
          case "doctor":
            updatedBookingData.doctor = input;
            nextStep = "time";
            setMessages((prev) => [
              ...prev,
              { id: (Date.now() + 1).toString(), role: "assistant", content: "Please enter the appointment time (e.g., 2025-03-20 10:00)." },
            ]);
            break;
          case "time":
            updatedBookingData.appointment_time = input;
            nextStep = "confirm";
            setMessages((prev) => [
              ...prev,
              {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: `Confirm your appointment: Patient: ${updatedBookingData.patient_name}, Doctor: ${updatedBookingData.doctor}, Time: ${input}. Type "yes" to confirm.`,
              },
            ]);
            break;
          case "confirm":
            if (input.toLowerCase() === "yes") {
              const response = await fetch("/api/appointment", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedBookingData),
              });

              const data: ApiResponse = await response.json();
              if (!response.ok || data.error) {
                throw new Error(data.error || "Failed to book appointment");
              }

              // Use the exact message from the backend
              setMessages((prev) => [
                ...prev,
                { id: (Date.now() + 1).toString(), role: "assistant", content: data.message || "Appointment booked." },
              ]);
              setBookingSessionId(null);
              setBookingData({});
              setBookingStep(null);
            } else {
              setMessages((prev) => [
                ...prev,
                { id: (Date.now() + 1).toString(), role: "assistant", content: "Booking canceled. Start over by clicking 'Book Appointment'." },
              ]);
              setBookingSessionId(null);
              setBookingData({});
              setBookingStep(null);
            }
            break;
        }

        if (bookingStep !== "confirm") {
          setBookingData(updatedBookingData);
          setBookingStep(nextStep);
        }
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Something went wrong"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleBookAppointment = async () => {
    setIsLoading(true);
    setShowWelcome(false);

    try {
      setBookingSessionId(Date.now().toString()); // Temporary session ID
      setBookingStep("name");
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: "assistant", content: "Please enter your name." },
      ]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to initiate booking"}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <h2 className="font-semibold">MediChat - Healthcare Assistant</h2>
        <p className="text-sm text-muted-foreground">
          Schedule appointments with ease
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
              I’m here to help you schedule appointments with our doctors. Click below to start!
            </p>
            <Button
              variant="outline"
              className="flex items-center justify-start gap-2"
              onClick={handleBookAppointment}
              disabled={isLoading}
            >
              <Calendar className="h-4 w-4" />
              <span>Book Appointment</span>
            </Button>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
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
            placeholder={
              bookingSessionId
                ? "Enter your response..."
                : "Type to start chatting..."
            }
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