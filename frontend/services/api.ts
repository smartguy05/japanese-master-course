/**
 * API Client for Nihongo Sensei Backend
 *
 * This module provides typed API client functions for interacting with the FastAPI backend.
 * Uses fetch API with TypeScript for type safety and includes authentication token handling.
 */

import type {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  User,
  FlashCard,
  ReviewRating,
  NextReview,
  Lesson,
  LessonProgress,
  Conversation,
  ConversationRequest,
  ConversationResponse,
  UserProgress,
  UserSettings,
  DailyStats,
  PaginatedResponse,
} from '@/lib/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string, public details?: unknown) {
    super(message);
    this.name = 'APIError';
  }
}

// ==================== Token Management ====================

const TOKEN_KEY = 'auth_token';

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

// ==================== Base API Request ====================

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  requiresAuth = true
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Add auth token if required
  if (requiresAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `API request failed: ${response.statusText}`;
    let errorDetails;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
      errorDetails = errorData;
    } catch {
      // If parsing JSON fails, use default error message
    }

    throw new APIError(response.status, errorMessage, errorDetails);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// ==================== Authentication API ====================

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiRequest<AuthResponse>(
      '/api/auth/login',
      {
        method: 'POST',
        body: JSON.stringify(credentials),
      },
      false
    );

    // Store token
    setAuthToken(response.access_token);

    return response;
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiRequest<AuthResponse>(
      '/api/auth/register',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      false
    );

    // Store token
    setAuthToken(response.access_token);

    return response;
  },

  async getCurrentUser(): Promise<User> {
    return apiRequest<User>('/api/auth/me');
  },

  logout(): void {
    removeAuthToken();
  },
};

// ==================== Flashcards API ====================

export const flashcardsAPI = {
  async getDueCards(): Promise<FlashCard[]> {
    return apiRequest<FlashCard[]>('/api/flashcards/due');
  },

  async getAllCards(jlptLevel?: string): Promise<FlashCard[]> {
    const params = jlptLevel ? `?jlpt_level=${jlptLevel}` : '';
    return apiRequest<FlashCard[]>(`/api/flashcards${params}`);
  },

  async getCard(cardId: string): Promise<FlashCard> {
    return apiRequest<FlashCard>(`/api/flashcards/${cardId}`);
  },

  async submitReview(rating: ReviewRating): Promise<NextReview> {
    return apiRequest<NextReview>('/api/flashcards/review', {
      method: 'POST',
      body: JSON.stringify(rating),
    });
  },

  async resetCard(cardId: string): Promise<FlashCard> {
    return apiRequest<FlashCard>(`/api/flashcards/${cardId}/reset`, {
      method: 'POST',
    });
  },
};

// ==================== Lessons API ====================

export const lessonsAPI = {
  async getAll(params?: {
    level?: string;
    type?: string;
    page?: number;
    perPage?: number;
  }): Promise<PaginatedResponse<Lesson>> {
    const queryParams = new URLSearchParams();
    if (params?.level) queryParams.append('level', params.level);
    if (params?.type) queryParams.append('type', params.type);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.perPage) queryParams.append('per_page', params.perPage.toString());

    const query = queryParams.toString();
    return apiRequest<PaginatedResponse<Lesson>>(
      `/api/lessons${query ? `?${query}` : ''}`
    );
  },

  async getById(id: string): Promise<Lesson> {
    return apiRequest<Lesson>(`/api/lessons/${id}`);
  },

  async getProgress(lessonId: string): Promise<LessonProgress> {
    return apiRequest<LessonProgress>(`/api/lessons/${lessonId}/progress`);
  },

  async submitExercise(
    lessonId: string,
    exerciseId: string,
    answer: string | string[]
  ): Promise<{ correct: boolean; explanation: string; points: number }> {
    return apiRequest(`/api/lessons/${lessonId}/exercises/${exerciseId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    });
  },

  async completeLesson(lessonId: string): Promise<LessonProgress> {
    return apiRequest<LessonProgress>(`/api/lessons/${lessonId}/complete`, {
      method: 'POST',
    });
  },
};

// ==================== Conversation API ====================

export const conversationAPI = {
  async getAll(): Promise<Conversation[]> {
    return apiRequest<Conversation[]>('/api/conversations');
  },

  async getById(id: string): Promise<Conversation> {
    return apiRequest<Conversation>(`/api/conversations/${id}`);
  },

  async sendMessage(request: ConversationRequest): Promise<ConversationResponse> {
    return apiRequest<ConversationResponse>('/api/conversations/message', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async endConversation(conversationId: string): Promise<Conversation> {
    return apiRequest<Conversation>(`/api/conversations/${conversationId}/end`, {
      method: 'POST',
    });
  },
};

// ==================== Progress API ====================

export const progressAPI = {
  async get(): Promise<UserProgress> {
    return apiRequest<UserProgress>('/api/progress');
  },

  async getDailyStats(startDate: string, endDate: string): Promise<DailyStats[]> {
    return apiRequest<DailyStats[]>(
      `/api/progress/daily?start_date=${startDate}&end_date=${endDate}`
    );
  },

  async getStreakData(): Promise<{
    current_streak: number;
    longest_streak: number;
    streak_dates: string[];
  }> {
    return apiRequest('/api/progress/streak');
  },
};

// ==================== Settings API ====================

export const settingsAPI = {
  async get(): Promise<UserSettings> {
    return apiRequest<UserSettings>('/api/settings');
  },

  async update(settings: Partial<UserSettings>): Promise<UserSettings> {
    return apiRequest<UserSettings>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  },

  async updatePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    return apiRequest('/api/settings/password', {
      method: 'PUT',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  },

  async deleteAccount(): Promise<{ message: string }> {
    return apiRequest('/api/settings/account', {
      method: 'DELETE',
    });
  },
};

// ==================== Speech API (Future Enhancement) ====================

export const speechAPI = {
  async transcribe(audioBlob: Blob): Promise<{ text: string; confidence: number }> {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    return apiRequest('/api/speech/transcribe', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove Content-Type to let browser set it for FormData
    });
  },

  async synthesize(text: string, voice?: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/speech/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify({ text, voice }),
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Speech synthesis failed');
    }

    return response.blob();
  },
};
