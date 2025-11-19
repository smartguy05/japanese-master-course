/**
 * Lesson Detail Page
 *
 * Individual lesson with content and exercises
 */

'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ProgressRing } from '@/components/progress/ProgressRing';
import { useLesson } from '@/hooks/useLessons';
import { ArrowLeft, CheckCircle2, Clock } from 'lucide-react';
import Link from 'next/link';
import type { Exercise } from '@/lib/types';

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = params.id as string;

  const {
    lesson,
    isLessonLoading,
    progress,
    submitExercise,
    isSubmittingExercise,
    completeLesson,
    isCompletingLesson,
  } = useLesson(lessonId);

  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string | string[]>>({});
  const [exerciseResults, setExerciseResults] = useState<Record<string, boolean>>({});

  if (isLessonLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <h2 className="text-2xl font-bold mb-2">Lesson not found</h2>
        <Button asChild>
          <Link href="/dashboard/lessons">Back to Lessons</Link>
        </Button>
      </div>
    );
  }

  const currentSection = lesson.content.sections[currentSectionIndex];
  const isLastSection = currentSectionIndex === lesson.content.sections.length - 1;

  const handleExerciseSubmit = (exercise: Exercise) => {
    const answer = selectedAnswers[exercise.id];
    if (!answer) return;

    submitExercise(
      { exerciseId: exercise.id, answer },
      {
        onSuccess: (result) => {
          setExerciseResults((prev) => ({
            ...prev,
            [exercise.id]: result.correct,
          }));
        },
      }
    );
  };

  const handleComplete = () => {
    completeLesson(undefined, {
      onSuccess: () => {
        router.push('/dashboard/lessons');
      },
    });
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <Button variant="ghost" size="sm" asChild className="mb-4">
            <Link href="/dashboard/lessons">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Lessons
            </Link>
          </Button>
          <h1 className="text-3xl font-bold">{lesson.title}</h1>
          <p className="text-muted-foreground mt-2">{lesson.description}</p>
          <div className="flex items-center gap-4 mt-4">
            <span className="text-sm bg-primary/10 text-primary px-3 py-1 rounded-full">
              {lesson.level}
            </span>
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {lesson.estimated_minutes} min
            </span>
          </div>
        </div>
        <ProgressRing
          progress={progress?.completion_percentage || 0}
          size={100}
          strokeWidth={6}
        />
      </div>

      {/* Introduction */}
      {currentSectionIndex === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Introduction</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{lesson.content.introduction}</p>
          </CardContent>
        </Card>
      )}

      {/* Current Section */}
      {currentSection && (
        <Card>
          <CardHeader>
            <CardTitle>{currentSection.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="prose dark:prose-invert max-w-none">
              <p>{currentSection.content}</p>
            </div>

            {/* Examples */}
            {currentSection.examples && currentSection.examples.length > 0 && (
              <div className="space-y-3 mt-6">
                <h4 className="font-semibold">Examples:</h4>
                {currentSection.examples.map((example, i) => (
                  <div key={i} className="bg-muted p-4 rounded-lg space-y-1">
                    <div className="text-lg font-medium">{example.japanese}</div>
                    {example.reading && (
                      <div className="text-sm text-muted-foreground">{example.reading}</div>
                    )}
                    <div className="text-sm">{example.english}</div>
                    {example.notes && (
                      <div className="text-xs text-muted-foreground italic">{example.notes}</div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Tips */}
            {currentSection.tips && currentSection.tips.length > 0 && (
              <div className="space-y-2 mt-6">
                <h4 className="font-semibold">Tips:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {currentSection.tips.map((tip, i) => (
                    <li key={i} className="text-sm text-muted-foreground">{tip}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Exercises */}
      {lesson.exercises.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Practice Exercises</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {lesson.exercises.map((exercise, i) => (
              <div key={exercise.id} className="space-y-3">
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-semibold">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="font-medium">{exercise.question}</p>

                    {/* Multiple Choice */}
                    {exercise.type === 'multiple_choice' && exercise.options && (
                      <div className="space-y-2 mt-3">
                        {exercise.options.map((option) => (
                          <label
                            key={option}
                            className="flex items-center gap-2 p-3 rounded-lg border cursor-pointer hover:bg-accent"
                          >
                            <input
                              type="radio"
                              name={exercise.id}
                              value={option}
                              checked={selectedAnswers[exercise.id] === option}
                              onChange={(e) =>
                                setSelectedAnswers((prev) => ({
                                  ...prev,
                                  [exercise.id]: e.target.value,
                                }))
                              }
                              disabled={exerciseResults[exercise.id] !== undefined}
                            />
                            <span>{option}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {/* Submit Button */}
                    {!exerciseResults[exercise.id] && (
                      <Button
                        size="sm"
                        className="mt-3"
                        onClick={() => handleExerciseSubmit(exercise)}
                        disabled={!selectedAnswers[exercise.id] || isSubmittingExercise}
                      >
                        Check Answer
                      </Button>
                    )}

                    {/* Result */}
                    {exerciseResults[exercise.id] !== undefined && (
                      <div
                        className={`mt-3 p-3 rounded-lg ${
                          exerciseResults[exercise.id]
                            ? 'bg-green-50 dark:bg-green-950 text-green-800 dark:text-green-200'
                            : 'bg-red-50 dark:bg-red-950 text-red-800 dark:text-red-200'
                        }`}
                      >
                        <div className="flex items-center gap-2 font-medium">
                          {exerciseResults[exercise.id] ? (
                            <>
                              <CheckCircle2 className="w-4 h-4" />
                              Correct!
                            </>
                          ) : (
                            <>Incorrect</>
                          )}
                        </div>
                        <p className="text-sm mt-1">{exercise.explanation}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentSectionIndex(Math.max(0, currentSectionIndex - 1))}
          disabled={currentSectionIndex === 0}
        >
          Previous
        </Button>

        {isLastSection ? (
          <Button
            onClick={handleComplete}
            disabled={isCompletingLesson}
          >
            Complete Lesson
          </Button>
        ) : (
          <Button
            onClick={() =>
              setCurrentSectionIndex(
                Math.min(lesson.content.sections.length - 1, currentSectionIndex + 1)
              )
            }
          >
            Next
          </Button>
        )}
      </div>
    </div>
  );
}
