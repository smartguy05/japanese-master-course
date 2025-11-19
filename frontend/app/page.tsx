import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Header } from "@/components/layout/Header";

export default function Home() {
  return (
    <>
      <Header />
      <div className="flex flex-col">
      {/* Hero Section */}
      <section className="container flex flex-col items-center justify-center gap-6 py-24 md:py-32">
        <div className="flex flex-col items-center gap-4 text-center">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
            Master Japanese with AI
          </h1>
          <p className="max-w-[700px] text-lg text-muted-foreground sm:text-xl">
            From complete beginner to business proficiency. Learn Japanese through AI-powered conversation,
            spaced repetition, and personalized lessons.
          </p>
          <div className="flex gap-4 mt-4">
            <Button size="lg" asChild>
              <Link href="/signup">Start Learning Free</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/lessons">Explore Lessons</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-16 bg-secondary/50">
        <div className="grid gap-8 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>AI Conversation Practice</CardTitle>
              <CardDescription>
                Practice speaking with Claude, get instant corrections, and improve naturally
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Real-time conversation with intelligent feedback on grammar, pronunciation, and usage
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Smart Spaced Repetition</CardTitle>
              <CardDescription>
                Learn 2,000+ kanji and 10,000+ vocabulary with proven SRS algorithms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Scientifically optimized review scheduling ensures you remember what you learn
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>JLPT N5 to N2</CardTitle>
              <CardDescription>
                Structured curriculum from beginner to business proficiency
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Comprehensive lessons covering grammar, reading, listening, and speaking
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-24 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to start your Japanese journey?</h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-[600px] mx-auto">
          Join thousands of learners mastering Japanese with AI-powered personalized learning
        </p>
        <Button size="lg" asChild>
          <Link href="/signup">Get Started Now</Link>
        </Button>
      </section>
      </div>
    </>
  );
}
