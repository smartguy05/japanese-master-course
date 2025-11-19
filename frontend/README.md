# Nihongo Sensei - Frontend

Next.js 14 frontend for the Nihongo Sensei AI-powered Japanese learning platform.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS 3+
- **UI Components:** shadcn/ui (Button, Card, Input)
- **State Management:** 
  - TanStack Query v5 (server state)
  - Zustand (client state)
- **Forms:** React Hook Form + Zod
- **Animations:** Framer Motion
- **PWA:** next-pwa
- **Testing:** Jest + React Testing Library

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with Header
│   ├── page.tsx             # Landing page
│   └── globals.css          # Global styles with shadcn theme
├── components/
│   ├── ui/                  # shadcn UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── layout/              # Layout components
│   │   └── Header.tsx
│   ├── flashcards/          # Flashcard components (TBD)
│   ├── conversation/        # Conversation components (TBD)
│   ├── progress/            # Progress components (TBD)
│   └── lessons/             # Lesson components (TBD)
├── hooks/                   # Custom React hooks
│   └── useSRS.ts           # Spaced repetition algorithm
├── lib/                     # Utilities
│   └── utils.ts            # CN utility for Tailwind
├── services/                # API clients
│   └── api.ts              # FastAPI backend client
├── __tests__/              # Test files
│   ├── components/
│   │   └── Button.test.tsx
│   └── hooks/
│       └── useSRS.test.ts
├── public/                  # Static assets
│   └── manifest.json       # PWA manifest
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local
```

### Development

```bash
# Start dev server (http://localhost:3000)
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## Testing

This project follows **Test-Driven Development (TDD)** practices:

1. Write tests FIRST
2. Watch them FAIL
3. Write minimum code to pass
4. Refactor while keeping tests green

### Running Tests

```bash
# Run all tests
npm test

# Watch mode for TDD
npm run test:watch

# Coverage report
npm run test:coverage
```

### Test Coverage Requirements

- **Overall:** 85% minimum
- **New code:** 90% minimum
- **Critical paths:** 100% (SRS algorithm, progress tracking)

### Example Test

```typescript
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  it('should render button with text', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
  });
});
```

## Available Components

### UI Components (shadcn/ui)

- **Button** - Accessible button with variants (default, destructive, outline, ghost, link)
- **Card** - Card container with Header, Title, Description, Content, Footer
- **Input** - Styled input field

### Custom Hooks

- **useSRS** - Spaced Repetition System using SM-2 algorithm

### API Client

The `services/api.ts` file provides typed API clients:

```typescript
import { authAPI, lessonsAPI, progressAPI } from '@/services/api';

// Login
await authAPI.login(email, password);

// Get lessons
const lessons = await lessonsAPI.getAll();

// Get progress
const progress = await progressAPI.get();
```

## PWA Support

Progressive Web App features are enabled via `next-pwa`:

- Service worker auto-generation
- Offline support (disabled in development)
- Install prompt on mobile devices
- Manifest configuration in `public/manifest.json`

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Code Quality

- **ESLint** - Next.js configuration
- **TypeScript** - Strict mode enabled
- **Prettier** - Code formatting (configure as needed)

## Deployment

Build the production bundle:

```bash
npm run build
npm start
```

For Docker deployment, see the root project's Docker documentation.

## Contributing

1. Follow TDD practices - write tests FIRST
2. Maintain 85%+ test coverage
3. Use TypeScript strict mode
4. Follow component naming conventions
5. Keep components small and focused

## Next Steps

- [ ] Implement auth pages (login, signup)
- [ ] Create lessons listing page
- [ ] Build conversation interface
- [ ] Add progress dashboard
- [ ] Implement flashcard system
- [ ] Add speech recognition integration
- [ ] Configure TanStack Query provider
- [ ] Set up Zustand stores

---

**Status:** Infrastructure complete, ready for feature development

Last updated: 2025-11-19
