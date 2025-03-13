import { Calendar, Clock, Menu, User } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-bold text-primary text-xl">MediChat</span>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Appointments</span>
          </Link>
          <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>History</span>
          </Link>
          <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2">
            <User className="h-4 w-4" />
            <span>Profile</span>
          </Link>
        </nav>

        <div className="flex items-center gap-2">
          <Button variant="outline" className="hidden md:flex">
            Sign In
          </Button>
          <Button className="hidden md:flex">Register</Button>

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <nav className="flex flex-col gap-4 mt-8">
                <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2 py-2">
                  <Calendar className="h-4 w-4" />
                  <span>Appointments</span>
                </Link>
                <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2 py-2">
                  <Clock className="h-4 w-4" />
                  <span>History</span>
                </Link>
                <Link href="#" className="text-muted-foreground hover:text-primary flex items-center gap-2 py-2">
                  <User className="h-4 w-4" />
                  <span>Profile</span>
                </Link>
                <Button variant="outline" className="mt-4">
                  Sign In
                </Button>
                <Button>Register</Button>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}

