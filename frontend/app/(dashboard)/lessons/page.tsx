/**
 * Lessons Page
 *
 * Browse and filter available lessons
 */

'use client';

import { useState } from 'react';
import { LessonCard } from '@/components/lessons/LessonCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useLessons } from '@/hooks/useLessons';
import { Search, Filter } from 'lucide-react';
import type { JLPTLevel, LessonType } from '@/lib/types';

const jlptLevels: JLPTLevel[] = ['N5', 'N4', 'N3', 'N2', 'N1'];
const lessonTypes: LessonType[] = [
  'hiragana',
  'katakana',
  'kanji',
  'vocabulary',
  'grammar',
  'reading',
  'listening',
];

export default function LessonsPage() {
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const { lessons, isLessonsLoading } = useLessons({
    level: selectedLevel,
    type: selectedType,
  });

  const filteredLessons = lessons.filter((lesson) =>
    lesson.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lesson.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Lessons</h1>
        <p className="text-muted-foreground mt-2">
          Structured curriculum from beginner to advanced
        </p>
      </div>

      {/* Filters */}
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search lessons..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Level Filter */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={selectedLevel === '' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedLevel('')}
          >
            All Levels
          </Button>
          {jlptLevels.map((level) => (
            <Button
              key={level}
              variant={selectedLevel === level ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedLevel(level)}
            >
              {level}
            </Button>
          ))}
        </div>

        {/* Type Filter */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={selectedType === '' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedType('')}
          >
            All Types
          </Button>
          {lessonTypes.map((type) => (
            <Button
              key={type}
              variant={selectedType === type ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedType(type)}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Lessons Grid */}
      {isLessonsLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-48 bg-muted animate-pulse rounded-lg"
            />
          ))}
        </div>
      ) : filteredLessons.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredLessons.map((lesson) => (
            <LessonCard key={lesson.id} lesson={lesson} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            No lessons found matching your criteria
          </p>
        </div>
      )}
    </div>
  );
}
