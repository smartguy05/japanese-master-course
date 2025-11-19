"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold">日本語先生</span>
            <span className="text-sm text-muted-foreground">Nihongo Sensei</span>
          </Link>
          
          <nav className="hidden md:flex items-center gap-6">
            <Link 
              href="/lessons" 
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Lessons
            </Link>
            <Link 
              href="/conversation" 
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Conversation
            </Link>
            <Link 
              href="/progress" 
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Progress
            </Link>
          </nav>
        </div>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" asChild>
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link href="/signup">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
