import { HealthcareChat } from "@/components/heathcare_chat"
import { Header } from "@/components/header"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Header />
      <main className="flex-1 container mx-auto p-4 md:p-6 lg:p-8 flex flex-col">
        <div className="flex-1 flex flex-col items-center justify-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-center text-primary mb-4">AI Healthcare Assistant</h1>
          <p className="text-center text-muted-foreground max-w-2xl mb-8">
            Schedule appointments, get health information, and more with our AI-powered healthcare assistant.
          </p>
          <div className="w-full max-w-4xl bg-white rounded-xl shadow-lg overflow-hidden border border-slate-200">
            <HealthcareChat />
          </div>
        </div>
      </main>
      <footer className="py-6 border-t border-slate-200 bg-white">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} Healthcare AI Assistant. Demo purposes only.</p>
        </div>
      </footer>
    </div>
  )
}

