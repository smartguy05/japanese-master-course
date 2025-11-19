/**
 * Progress Page
 *
 * Detailed user progress statistics and achievements
 */

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProgressRing } from '@/components/progress/ProgressRing';
import { useProgress, useDailyStats } from '@/hooks/useProgress';
import { Flame, Trophy, Clock, TrendingUp, Award, BookOpen } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

export default function ProgressPage() {
  const {
    currentStreak,
    longestStreak,
    totalStudyTime,
    xp,
    level,
    achievements,
    jlptProgress,
  } = useProgress();

  const { stats } = useDailyStats(30);

  const chartData = stats.map((stat) => ({
    date: format(parseISO(stat.date), 'MMM dd'),
    studyTime: stat.study_time_minutes,
    xp: stat.xp_earned,
  }));

  const studyHours = Math.floor(totalStudyTime / 60);
  const studyMinutes = totalStudyTime % 60;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Your Progress</h1>
        <p className="text-muted-foreground mt-2">
          Track your learning journey and achievements
        </p>
      </div>

      {/* Top Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Level</CardTitle>
            <TrendingUp className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{level}</div>
            <p className="text-xs text-muted-foreground">
              {xp % 1000} / 1000 XP to next level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Streak</CardTitle>
            <Flame className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{currentStreak}</div>
            <p className="text-xs text-muted-foreground">
              Longest: {longestStreak} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Study Time</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {studyHours}h {studyMinutes}m
            </div>
            <p className="text-xs text-muted-foreground">
              Keep up the great work!
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total XP</CardTitle>
            <Trophy className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{xp}</div>
            <p className="text-xs text-muted-foreground">
              Experience points earned
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Study Time Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Study Time (Last 30 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="studyTime"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Study Time (min)"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* XP Earned Chart */}
      <Card>
        <CardHeader>
          <CardTitle>XP Earned (Last 30 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="xp" fill="#10b981" name="XP Earned" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* JLPT Progress */}
      {jlptProgress && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              JLPT {jlptProgress.current_level} Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="text-center">
                <ProgressRing
                  progress={(jlptProgress.kanji_known / jlptProgress.kanji_total) * 100}
                  size={120}
                  strokeWidth={8}
                  label="Kanji"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  {jlptProgress.kanji_known} / {jlptProgress.kanji_total}
                </p>
              </div>
              <div className="text-center">
                <ProgressRing
                  progress={(jlptProgress.vocabulary_known / jlptProgress.vocabulary_total) * 100}
                  size={120}
                  strokeWidth={8}
                  label="Vocabulary"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  {jlptProgress.vocabulary_known} / {jlptProgress.vocabulary_total}
                </p>
              </div>
              <div className="text-center">
                <ProgressRing
                  progress={
                    (jlptProgress.grammar_points_known / jlptProgress.grammar_points_total) * 100
                  }
                  size={120}
                  strokeWidth={8}
                  label="Grammar"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  {jlptProgress.grammar_points_known} / {jlptProgress.grammar_points_total}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Achievements */}
      {achievements && achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`p-4 rounded-lg border ${
                    achievement.earned_at
                      ? 'bg-primary/5 border-primary/20'
                      : 'bg-muted/50 opacity-60'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-3xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <h4 className="font-semibold">{achievement.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">
                        {achievement.description}
                      </p>
                      {!achievement.earned_at && (
                        <div className="mt-2">
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full"
                              style={{
                                width: `${(achievement.progress / achievement.target) * 100}%`,
                              }}
                            />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {achievement.progress} / {achievement.target}
                          </p>
                        </div>
                      )}
                      {achievement.earned_at && (
                        <p className="text-xs text-primary mt-2">
                          Earned {new Date(achievement.earned_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
