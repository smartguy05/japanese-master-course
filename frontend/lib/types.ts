/**
 * TypeScript Types and Interfaces for Nihongo Sensei
 */

// ==================== User & Authentication ====================

export interface User {
  id: string;
  email: string;
  full_name: string;
  native_language: string;
  target_jlpt_level: JLPTLevel;
  daily_goal_minutes: number;
  created_at: string;
  last_login: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  native_language: string;
}

// ==================== JLPT & Learning Levels ====================

export type JLPTLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1';

export type LessonType =
  | 'hiragana'
  | 'katakana'
  | 'kanji'
  | 'vocabulary'
  | 'grammar'
  | 'reading'
  | 'listening';

export type ExerciseType =
  | 'multiple_choice'
  | 'fill_in_blank'
  | 'matching'
  | 'true_false'
  | 'writing'
  | 'listening';

// ==================== Flashcards & SRS ====================

export interface FlashCard {
  id: string;
  user_id: string;
  front: string;
  back: string;
  reading?: string;
  meaning: string;
  type: 'kanji' | 'vocabulary' | 'grammar';
  jlpt_level: JLPTLevel;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review: string;
  last_reviewed?: string;
  created_at: string;
}

export interface ReviewSession {
  cards: FlashCard[];
  total_cards: number;
  reviewed_count: number;
  correct_count: number;
  start_time: string;
  end_time?: string;
}

export interface ReviewRating {
  card_id: string;
  quality: 1 | 2 | 3 | 4 | 5;
  time_spent_seconds: number;
}

export interface NextReview {
  card_id: string;
  next_review_date: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

// ==================== Lessons ====================

export interface Lesson {
  id: string;
  title: string;
  description: string;
  level: JLPTLevel;
  type: LessonType;
  order: number;
  estimated_minutes: number;
  content: LessonContent;
  exercises: Exercise[];
  is_locked: boolean;
  completion_percentage?: number;
  created_at: string;
}

export interface LessonContent {
  introduction: string;
  sections: LessonSection[];
  summary: string;
  key_points: string[];
}

export interface LessonSection {
  id: string;
  title: string;
  content: string;
  examples?: Example[];
  tips?: string[];
}

export interface Example {
  japanese: string;
  reading?: string;
  english: string;
  notes?: string;
}

export interface Exercise {
  id: string;
  type: ExerciseType;
  question: string;
  options?: string[];
  correct_answer: string | string[];
  explanation: string;
  points: number;
}

export interface LessonProgress {
  lesson_id: string;
  user_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  exercises_completed: string[];
  score: number;
  time_spent_seconds: number;
  started_at?: string;
  completed_at?: string;
}

// ==================== Conversation ====================

export interface Conversation {
  id: string;
  user_id: string;
  scenario: ConversationScenario;
  messages: Message[];
  started_at: string;
  ended_at?: string;
  total_messages: number;
  corrections_count: number;
}

export type ConversationScenario =
  | 'casual_greeting'
  | 'restaurant'
  | 'shopping'
  | 'work_meeting'
  | 'job_interview'
  | 'making_friends'
  | 'asking_directions'
  | 'phone_call'
  | 'business_email'
  | 'free_conversation';

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  correction?: Correction;
  encouragement?: string;
}

export interface Correction {
  original: string;
  corrected: string;
  explanation: string;
  severity: 'minor' | 'moderate' | 'major';
  type: 'grammar' | 'vocabulary' | 'particle' | 'pronunciation' | 'usage';
}

export interface ConversationRequest {
  scenario: ConversationScenario;
  user_message: string;
  conversation_id?: string;
}

export interface ConversationResponse {
  conversation_id: string;
  message: Message;
}

// ==================== Progress & Statistics ====================

export interface UserProgress {
  user_id: string;
  total_xp: number;
  level: number;
  current_streak_days: number;
  longest_streak_days: number;
  total_study_time_minutes: number;
  lessons_completed: number;
  flashcards_reviewed: number;
  conversations_completed: number;
  achievements: Achievement[];
  jlpt_progress: JLPTProgress;
}

export interface JLPTProgress {
  current_level: JLPTLevel;
  kanji_known: number;
  kanji_total: number;
  vocabulary_known: number;
  vocabulary_total: number;
  grammar_points_known: number;
  grammar_points_total: number;
  estimated_proficiency_percentage: number;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earned_at?: string;
  progress: number;
  target: number;
}

export interface StudySession {
  id: string;
  user_id: string;
  date: string;
  duration_minutes: number;
  activities: {
    flashcards?: number;
    lessons?: number;
    conversations?: number;
  };
  xp_earned: number;
}

export interface DailyStats {
  date: string;
  study_time_minutes: number;
  flashcards_reviewed: number;
  lessons_completed: number;
  conversations: number;
  xp_earned: number;
  streak_maintained: boolean;
}

// ==================== Settings ====================

export interface UserSettings {
  user_id: string;
  notifications_enabled: boolean;
  daily_reminder_time?: string;
  audio_enabled: boolean;
  auto_play_pronunciation: boolean;
  theme: 'light' | 'dark' | 'system';
  interface_language: string;
  study_reminders: boolean;
  email_updates: boolean;
}

// ==================== API Response Wrappers ====================

export interface APIResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface APIError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
}
