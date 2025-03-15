"use client";

import { useChat } from "@ai-sdk/react";
import { useState, useRef, useEffect, ChangeEvent, FormEvent } from "react";
import { Send, Loader2, Calendar, Clock, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function HealthcareChat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: "/api/chat",
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [appointmentLoading, setAppointmentLoading] = useState(false);

  const [isBookingAppointment, setIsBookingAppointment] = useState(false);
  const [appointmentStep, setAppointmentStep] = useState<number>(0);
  const [appointmentData, setAppointmentData] = useState({
    patientName: "",
    patientPhone: "",
    doctorName: "",
    doctorPhone: "",
    appointmentType: "General Checkup",
    preferredDate: "2025-03-15",
    preferredTime: "10:30",
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (messages.some((m) => m.role === "user")) {
      setShowWelcome(false);
    }
  }, [messages]);

  useEffect(() => {
    if (isBookingAppointment && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "user" && lastMessage.content.trim()) {
        handleAppointmentInput(lastMessage.content);
      }
    }
  }, [messages]);

  const startAppointmentBooking = () => {
    setIsBookingAppointment(true);
    setAppointmentStep(1);
    handleInputChange({ target: { value: "Please provide your name." } } as ChangeEvent<HTMLTextAreaElement>);
    handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "Please provide your name." });
  };

  const handleAppointmentInput = (userInput: string) => {
    switch (appointmentStep) {
      case 1:
        setAppointmentData((prev) => ({ ...prev, patientName: userInput }));
        setAppointmentStep(2);
        handleInputChange({ target: { value: "Please provide your phone number." } } as ChangeEvent<HTMLTextAreaElement>);
        handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "Please provide your phone number." });
        break;
      case 2:
        setAppointmentData((prev) => ({ ...prev, patientPhone: userInput }));
        setAppointmentStep(3);
        handleInputChange({ target: { value: "Please provide the doctor's name." } } as ChangeEvent<HTMLTextAreaElement>);
        handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "Please provide the doctor's name." });
        break;
      case 3:
        setAppointmentData((prev) => ({ ...prev, doctorName: userInput }));
        setAppointmentStep(4);
        handleInputChange({ target: { value: "Please provide the doctor's phone number." } } as ChangeEvent<HTMLTextAreaElement>);
        handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "Please provide the doctor's phone number." });
        break;
      case 4:
        setAppointmentData((prev) => ({ ...prev, doctorPhone: userInput }));
        setAppointmentStep(0);
        setIsBookingAppointment(false);
        submitAppointment();
        break;
      default:
        break;
    }
  };

  const submitAppointment = async () => {
    setAppointmentLoading(true);
    try {
      const payload = {
        appointmentType: appointmentData.appointmentType,
        preferredDate: appointmentData.preferredDate,
        preferredTime: appointmentData.preferredTime,
        patientName: appointmentData.patientName,
        additionalNotes: `Patient Phone: ${appointmentData.patientPhone}, Doctor: ${appointmentData.doctorName}, Doctor Phone: ${appointmentData.doctorPhone}`,
      };

      const response = await fetch("/api/appointment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.details || result.error || "Failed to create appointment");
      }

      const successMessage = `Appointment scheduled: ${result.appointment.type} on ${result.appointment.date} at ${result.appointment.time}`;
      handleInputChange({ target: { value: successMessage } } as ChangeEvent<HTMLTextAreaElement>);
      handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: successMessage });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred";
      handleInputChange({ target: { value: `Error: ${errorMessage}` } } as ChangeEvent<HTMLTextAreaElement>);
      handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: `Error: ${errorMessage}` });
    } finally {
      setAppointmentLoading(false);
    }
  };

  const onFormSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("Submitting input:", input); // Debug log
    handleSubmit(e, { prompt: input }); // Explicitly pass prompt
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
        {showWelcome && (
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
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={startAppointmentBooking}
                disabled={isLoading || appointmentLoading}
              >
                <Calendar className="h-4 w-4" />
                {isLoading || appointmentLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <span>Appointment</span>
                )}
              </Button>
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={() => {
                  handleInputChange({
                    target: { value: "What are your available time slots?" },
                  } as ChangeEvent<HTMLTextAreaElement>);
                  handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "What are your available time slots?" });
                }}
              >
                <Clock className="h-4 w-4" />
                <span>Check availability</span>
              </Button>
              <Button
                variant="outline"
                className="flex items-center justify-start gap-2"
                onClick={() => {
                  handleInputChange({
                    target: { value: "Where is your clinic located?" },
                  } as ChangeEvent<HTMLTextAreaElement>);
                  handleSubmit({ preventDefault: () => {} } as FormEvent<HTMLFormElement>, { prompt: "Where is your clinic located?" });
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
              {/* Appointment cards omitted for brevity */}
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
        <form onSubmit={onFormSubmit} className="flex gap-2">
          <Textarea
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about appointments, health info, or clinic details..."
            className="flex-1 min-h-[60px] max-h-[120px]"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}