# Contributing to Nihongo Sensei

Thank you for your interest in contributing to Nihongo Sensei! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Git Workflow](#git-workflow)
- [Testing Requirements](#testing-requirements)
- [Code Style Guidelines](#code-style-guidelines)
- [Pull Request Process](#pull-request-process)
- [Commit Message Conventions](#commit-message-conventions)
- [What to Contribute](#what-to-contribute)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment, trolling, or insulting comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see below)
4. **Create a branch** for your changes
5. **Make your changes** following our guidelines
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/nihongo-sensei.git
cd nihongo-sensei

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/nihongo-sensei.git

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend setup
cd ../frontend
npm install

# Environment configuration
cp ../.env.example ../.env
# Edit .env with your configuration

# Database setup
docker-compose up -d postgres redis
cd backend
alembic upgrade head
```

### Verify Setup

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

If all tests pass, you're ready to contribute!

## Development Workflow

### Test-Driven Development (TDD) - MANDATORY

**This project strictly follows TDD. This is non-negotiable.**

#### The TDD Cycle

```
1. RED    → Write a failing test
2. GREEN  → Write minimum code to pass
3. REFACTOR → Improve code while keeping tests green
4. REPEAT
```

#### TDD Example

**Step 1: Write the test FIRST**

```python
# tests/unit/test_new_feature.py
def test_calculate_streak():
    """Test that study streak is calculated correctly."""
    user = create_test_user()
    add_study_session(user, days_ago=0)
    add_study_session(user, days_ago=1)
    add_study_session(user, days_ago=2)

    streak = calculate_study_streak(user)

    assert streak == 3
```

**Step 2: Run test - it MUST fail**

```bash
pytest tests/unit/test_new_feature.py
# FAILURE - calculate_study_streak doesn't exist yet
```

**Step 3: Write MINIMUM code to pass**

```python
# app/services/progress_service.py
def calculate_study_streak(user):
    # Minimum implementation
    sessions = get_study_sessions(user)
    streak = count_consecutive_days(sessions)
    return streak
```

**Step 4: Run test - it should pass**

```bash
pytest tests/unit/test_new_feature.py
# SUCCESS
```

**Step 5: Refactor while keeping tests green**

### What NOT to Do

**❌ Writing implementation before tests**

```python
# DON'T DO THIS
def new_feature():
    # Write implementation
    return result

# Then write tests later - NO!
```

**❌ Skipping tests for "simple" features**

```python
# Even simple features need tests
def add_numbers(a, b):
    return a + b  # Still needs a test!
```

**❌ Committing code without running tests**

```bash
# WRONG
git add .
git commit -m "Add feature"  # Without running pytest first
```

## Git Workflow

### Branching Strategy

**Branch naming convention:**

```
feature/description       # New features
fix/description          # Bug fixes
test/description         # Test improvements
docs/description         # Documentation
refactor/description     # Code refactoring
```

**Examples:**

```bash
feature/flashcard-audio
fix/srs-calculation-bug
test/conversation-service
docs/api-endpoints
refactor/auth-service
```

### Working on a Feature

```bash
# 1. Update your fork
git checkout main
git pull upstream main
git push origin main

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes (TDD!)
# - Write test
# - Watch it fail
# - Write code
# - Make test pass
# - Refactor

# 4. Commit changes
git add .
git commit -m "feat: add amazing feature"

# 5. Push to your fork
git push origin feature/amazing-feature

# 6. Create Pull Request on GitHub
```

### Keeping Your Branch Updated

```bash
# Regularly sync with upstream
git fetch upstream
git rebase upstream/main

# Resolve conflicts if any
git push origin feature/amazing-feature --force-with-lease
```

## Testing Requirements

### Coverage Requirements

- **Overall minimum:** 85%
- **New code minimum:** 90%
- **Critical paths:** 100% (SRS, auth, progress tracking)

### Running Tests

**Backend:**

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific tests
pytest tests/unit/test_srs_algorithm.py -v

# Watch mode for TDD
pytest-watch -- --cov=app
```

**Frontend:**

```bash
cd frontend

# Run all tests
npm test

# Watch mode for TDD
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### Writing Good Tests

**Test Structure:**

```python
def test_descriptive_name():
    """Clear docstring explaining what is being tested."""
    # Arrange - Set up test data
    user = create_test_user()
    card = create_test_card()

    # Act - Execute the functionality
    result = review_card(user, card, quality=4)

    # Assert - Verify the outcome
    assert result.next_review_date > datetime.now()
    assert result.ease_factor >= 2.5
```

**Good Test Characteristics:**
- **Fast** - Unit tests should run in milliseconds
- **Independent** - Tests don't depend on each other
- **Repeatable** - Same result every time
- **Self-validating** - Clear pass/fail outcome
- **Timely** - Written before implementation

## Code Style Guidelines

### Python (Backend)

**Formatting:**
- Use **Black** for code formatting
- Use **Ruff** for linting
- Use **mypy** for type checking

```bash
# Format code
black app tests

# Lint code
ruff check app tests

# Type check
mypy app
```

**Style Guidelines:**

```python
# Good: Type hints, docstrings, clear naming
async def get_user_progress(
    user_id: int,
    db: AsyncSession
) -> UserProgress:
    """
    Retrieve user progress statistics.

    Args:
        user_id: User identifier
        db: Database session

    Returns:
        UserProgress object with statistics

    Raises:
        UserNotFoundError: If user doesn't exist
    """
    result = await db.execute(
        select(Progress).where(Progress.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

**Naming Conventions:**
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names over short names

### TypeScript (Frontend)

**Style Guidelines:**

```typescript
// Good: Interface, type safety, clear component structure
interface UserProgressProps {
  userId: number;
  showDetails?: boolean;
}

export const UserProgress: React.FC<UserProgressProps> = ({
  userId,
  showDetails = false
}) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['progress', userId],
    queryFn: () => api.getProgress(userId)
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Progress</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Content */}
      </CardContent>
    </Card>
  );
};
```

**Naming Conventions:**
- `camelCase` for variables, functions
- `PascalCase` for components, types, interfaces
- `UPPER_CASE` for constants

### General Guidelines

- **DRY (Don't Repeat Yourself)** - Avoid code duplication
- **KISS (Keep It Simple, Stupid)** - Simple solutions over complex ones
- **YAGNI (You Aren't Gonna Need It)** - Don't add functionality until needed
- **Single Responsibility** - Each function/class should do one thing well

## Pull Request Process

### Before Submitting

**Checklist:**

- [ ] All tests pass (`pytest && npm test`)
- [ ] Code coverage hasn't decreased
- [ ] Code is formatted (`black` / `prettier`)
- [ ] Linting passes (`ruff` / `eslint`)
- [ ] Type checking passes (`mypy` / `tsc`)
- [ ] No debug statements or commented code
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions

### PR Template

When creating a PR, include:

```markdown
## Description

Brief description of what this PR does.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Testing

Describe the tests you wrote (TDD):

1. Test for scenario X
2. Test for scenario Y
3. Integration test for Z

## Test Coverage

- Before: X%
- After: Y%

## Checklist

- [ ] Tests written first (TDD)
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)

Add screenshots for UI changes.
```

### PR Review Process

1. **Automated checks** run (CI/CD pipeline)
2. **Code review** by maintainer
3. **Feedback** addressed by contributor
4. **Approval** and merge

### Review Criteria

Reviewers will check for:
- TDD followed (tests before implementation)
- Test coverage maintained or improved
- Code quality and style
- Documentation updated
- No breaking changes (or properly documented)

## Commit Message Conventions

We follow the **Conventional Commits** specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `test` - Adding or updating tests
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `style` - Code style changes (formatting, etc.)
- `chore` - Build process, dependencies, etc.

### Examples

```bash
# Feature
git commit -m "feat(flashcards): add audio playback support"

# Bug fix
git commit -m "fix(srs): correct ease factor calculation for quality < 3"

# Tests
git commit -m "test(conversation): add tests for grammar correction parsing"

# Documentation
git commit -m "docs(api): update authentication endpoint examples"

# With body and footer
git commit -m "feat(lessons): add N4 grammar lessons

Add 20 new grammar lessons covering N4 content:
- Conditional forms
- Passive voice
- Causative forms

Closes #123"
```

### Commit Best Practices

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- First line should be 50 characters or less
- Reference issues and PRs in the footer

## What to Contribute

### High Priority

- **Bug Fixes** - Always welcome!
- **Test Coverage** - Help us reach 100%
- **Documentation** - Improve clarity and completeness
- **Performance** - Optimize slow operations
- **Accessibility** - Improve a11y compliance

### Feature Contributions

Before working on a new feature:

1. **Check existing issues** - May already be planned
2. **Open an issue** - Discuss the feature first
3. **Wait for approval** - Ensure it aligns with project goals
4. **Follow TDD** - Write tests first!

### Good First Issues

Look for issues tagged:
- `good first issue` - Good for newcomers
- `help wanted` - Maintainers need help
- `documentation` - Documentation improvements

### Areas Needing Help

- Japanese language content validation
- UI/UX improvements
- Performance optimization
- Mobile PWA features
- Accessibility improvements
- Test coverage for edge cases

## Questions?

- **GitHub Issues** - For bug reports and feature requests
- **GitHub Discussions** - For questions and ideas
- **Documentation** - Check docs/ directory

## Recognition

Contributors will be recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- GitHub contributors page

Thank you for contributing to Nihongo Sensei! 🇯🇵

---

**Last Updated:** 2025-11-19
