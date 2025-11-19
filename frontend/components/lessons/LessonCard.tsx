/**
 * LessonCard Component
 *
 * Displays a lesson preview card
 */

'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ProgressRing } from '@/components/progress/ProgressRing';
import type { Lesson } from '@/lib/types';
import { cn } from '@/lib/utils';
import { Clock, Lock, CheckCircle2 } from 'lucide-react';

interface LessonCardProps {
  lesson: Lesson;
  className?: string;
}

export function LessonCard({ lesson, className }: LessonCardProps) {
  const isCompleted = lesson.completion_percentage === 100;
  const isInProgress = (lesson.completion_percentage || 0) > 0 && !isCompleted;

  return (
    <Card className={cn('relative overflow-hidden', className)}>
      {lesson.is_locked && (
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-10 flex items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <Lock className="w-8 h-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Complete previous lessons to unlock</p>
          </div>
        </div>
      )}

      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className={cn(
                'text-xs px-2 py-1 rounded-full font-medium',
                'bg-primary/10 text-primary'
              )}>
                {lesson.level}
              </span>
              <span className="text-xs text-muted-foreground">{lesson.type}</span>
              {isCompleted && <CheckCircle2 className="w-4 h-4 text-green-500" />}
            </div>
            <CardTitle className="text-lg">{lesson.title}</CardTitle>
            <CardDescription className="mt-1">{lesson.description}</CardDescription>
          </div>
          {(lesson.completion_percentage || 0) > 0 && (
            <ProgressRing progress={lesson.completion_percentage || 0} size={60} strokeWidth={4} />
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span>{lesson.estimated_minutes} min</span>
          </div>
          <Button asChild variant={isInProgress ? 'default' : 'outline'} disabled={lesson.is_locked}>
            <Link href={`/dashboard/lessons/${lesson.id}`}>
              {isCompleted ? 'Review' : isInProgress ? 'Continue' : 'Start'}
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
