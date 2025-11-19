/**
 * Dashboard Page
 *
 * Main dashboard with overview of user progress and quick actions
 */

'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { useProgress } from '@/hooks/useProgress';
import { useFlashcards } from '@/hooks/useFlashcards';
import { ProgressRing } from '@/components/progress/ProgressRing';
import {
  Flame,
  BookOpen,
  MessageSquare,
  CreditCard,
  TrendingUp,
  Award,
  ArrowRight,
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const {
    progress,
    currentStreak,
    xp,
    level,
    lessonsCompleted,
    flashcardsReviewed,
    conversationsCompleted,
  } = useProgress();
  const { dueCardsCount } = useFlashcards();

  const stats = [
    {
      title: 'Current Streak',
      value: currentStreak,
      suffix: 'days',
      icon: Flame,
      color: 'text-orange-500',
    },
    {
      title: 'Lessons Completed',
      value: lessonsCompleted,
      icon: BookOpen,
      color: 'text-blue-500',
    },
    {
      title: 'Cards Reviewed',
      value: flashcardsReviewed,
      icon: CreditCard,
      color: 'text-green-500',
    },
    {
      title: 'Conversations',
      value: conversationsCompleted,
      icon: MessageSquare,
      color: 'text-purple-500',
    },
  ];

  const quickActions = [
    {
      title: 'Review Flashcards',
      description: `${dueCardsCount} cards due for review`,
      href: '/dashboard/flashcards',
      icon: CreditCard,
      color: 'bg-green-500',
      disabled: dueCardsCount === 0,
    },
    {
      title: 'Continue Learning',
      description: 'Pick up where you left off',
      href: '/dashboard/lessons',
      icon: BookOpen,
      color: 'bg-blue-500',
    },
    {
      title: 'Practice Conversation',
      description: 'Chat with AI sensei',
      href: '/dashboard/conversation',
      icon: MessageSquare,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}!
        </h1>
        <p className="text-muted-foreground mt-2">
          Ready to continue your Japanese learning journey?
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stat.value} {stat.suffix}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Level & XP */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Your Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            <div>
              <ProgressRing progress={(xp % 1000) / 10} size={100} strokeWidth={8} />
            </div>
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Level {level}</span>
                <span className="text-sm text-muted-foreground">
                  {xp % 1000} / 1000 XP
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${((xp % 1000) / 1000) * 100}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                {1000 - (xp % 1000)} XP until next level
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Card
                key={action.title}
                className={action.disabled ? 'opacity-50' : 'hover:shadow-lg transition-shadow'}
              >
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle>{action.title}</CardTitle>
                  <CardDescription>{action.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    asChild
                    variant="outline"
                    className="w-full"
                    disabled={action.disabled}
                  >
                    <Link href={action.href}>
                      Start
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* JLPT Progress */}
      {progress?.jlpt_progress && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              JLPT {progress.jlpt_progress.current_level} Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <div className="text-sm font-medium mb-2">Kanji</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-muted rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{
                        width: `${(progress.jlpt_progress.kanji_known / progress.jlpt_progress.kanji_total) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {progress.jlpt_progress.kanji_known}/{progress.jlpt_progress.kanji_total}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm font-medium mb-2">Vocabulary</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-muted rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{
                        width: `${(progress.jlpt_progress.vocabulary_known / progress.jlpt_progress.vocabulary_total) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {progress.jlpt_progress.vocabulary_known}/{progress.jlpt_progress.vocabulary_total}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm font-medium mb-2">Grammar</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-muted rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full"
                      style={{
                        width: `${(progress.jlpt_progress.grammar_points_known / progress.jlpt_progress.grammar_points_total) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {progress.jlpt_progress.grammar_points_known}/
                    {progress.jlpt_progress.grammar_points_total}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
