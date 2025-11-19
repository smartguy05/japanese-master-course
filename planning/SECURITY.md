# Security Architecture - Nihongo Master

## Security Philosophy

**"Security is not an afterthought - it's a fundamental requirement."**

This document outlines the security architecture, threat model, and security best practices for Nihongo Master.

---

## Threat Model

### Assets to Protect

1. **User Data**
   - Authentication credentials (email, password)
   - Personal information (name, preferences)
   - Learning progress and statistics
   - Conversation history
   - Payment information (future)

2. **System Resources**
   - API access (prevent abuse)
   - AI service credits (prevent unauthorized usage)
   - Database integrity
   - Server compute resources

3. **Intellectual Property**
   - Lesson content
   - Prompts for AI content generation
   - Proprietary algorithms (SRS implementation)

### Threat Actors

1. **Malicious Users**
   - Attempting unauthorized access
   - Scraping content
   - Abusing AI services
   - Data exfiltration

2. **Automated Attacks**
   - Brute force password attempts
   - DDoS attacks
   - SQL injection attempts
   - XSS attacks
   - CSRF attacks

3. **Insider Threats**
   - Database administrators
   - Developers with production access
   - Third-party service providers

---

## Authentication & Authorization

### User Authentication Flow

```
User Login Request
    │
    ├─→ Validate Email Format
    ├─→ Rate Limit Check (10 attempts / 15 min)
    │
    ├─→ Retrieve User from Database
    │       │
    │       └─→ Not Found: Return 401 (Don't reveal if user exists)
    │
    ├─→ Verify Password with bcrypt
    │       │
    │       └─→ Invalid: Increment Failed Attempts, Return 401
    │
    ├─→ Generate JWT Tokens
    │       ├─→ Access Token (15 min expiry)
    │       └─→ Refresh Token (7 days expiry)
    │
    ├─→ Store Refresh Token (Database, HTTP-only cookie)
    │
    └─→ Return Access Token (Response body)
```

### Password Security

**Hashing Algorithm:**
```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- No common passwords (check against dictionary)
- Cannot be same as email or username

**Implementation:**
```python
import re
from typing import Optional

def validate_password(password: str, email: str, username: str) -> Optional[str]:
    """Validate password meets security requirements
    
    Returns None if valid, error message if invalid
    """
    if len(password) < 8:
        return "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    
    # Check if password contains email or username
    if email.split('@')[0].lower() in password.lower():
        return "Password cannot contain your email"
    
    if username.lower() in password.lower():
        return "Password cannot contain your username"
    
    # Check against common passwords
    if is_common_password(password):
        return "Password is too common, please choose a stronger password"
    
    return None
```

### JWT Token Management

**Token Structure:**
```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expires,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token"""
    expires = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")
```

**Token Refresh Flow:**
```python
@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    # Check if token is revoked
    user_id = int(payload["sub"])
    is_valid = await check_refresh_token_valid(db, user_id, refresh_token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Token revoked")
    
    # Generate new access token
    user = await get_user_by_id(db, user_id)
    new_access_token = create_access_token(user.id, user.email)
    
    return {"access_token": new_access_token, "token_type": "bearer"}
```

### Authorization Middleware

**Protect Routes:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    user_id = int(payload["sub"])
    
    # Get user from database
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Use in routes
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile - requires authentication"""
    return current_user
```

**Resource Authorization:**
```python
async def check_card_ownership(
    card_id: int,
    current_user: User,
    db: AsyncSession
) -> Card:
    """Verify user owns the card they're trying to access"""
    card = await db.get(Card, card_id)
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    if card.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this card"
        )
    
    return card

# Use in routes
@router.delete("/cards/{card_id}")
async def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a flashcard - must be owner"""
    card = await check_card_ownership(card_id, current_user, db)
    await db.delete(card)
    await db.commit()
    return {"success": True}
```

---

## Input Validation & Sanitization

### Backend Validation (Pydantic)

```python
from pydantic import BaseModel, EmailStr, field_validator
import re

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', v):
            raise ValueError(
                'Username must be 3-20 characters, '
                'alphanumeric, hyphens, or underscores only'
            )
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Additional checks...
        return v

class CardCreate(BaseModel):
    japanese: str
    romanji: str
    english: str
    
    @field_validator('japanese', 'romanji', 'english')
    @classmethod
    def validate_not_empty(cls, v):
        """Ensure fields are not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('japanese')
    @classmethod
    def validate_japanese_characters(cls, v):
        """Ensure text contains Japanese characters"""
        if not re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', v):
            raise ValueError('Must contain Japanese characters')
        return v
```

### Frontend Validation (Zod)

```typescript
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required')
});

export const signupSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be at most 20 characters')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, hyphens, and underscores'
    ),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(
      /[!@#$%^&*]/,
      'Password must contain at least one special character'
    ),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});
```

### SQL Injection Prevention

**✅ ALWAYS use ORM (SQLAlchemy):**
```python
# GOOD - Parameterized query via ORM
result = await db.execute(
    select(Card).where(Card.user_id == user_id)
)

# GOOD - Parameters bound safely
result = await db.execute(
    text("SELECT * FROM cards WHERE user_id = :user_id"),
    {"user_id": user_id}
)
```

**❌ NEVER use string concatenation:**
```python
# BAD - SQL injection vulnerability!
query = f"SELECT * FROM cards WHERE user_id = {user_id}"
result = await db.execute(text(query))
```

### XSS Prevention

**React Auto-Escaping:**
React automatically escapes content, but be cautious with:

```typescript
// ✅ SAFE - React escapes content
function Component({ userInput }) {
  return <div>{userInput}</div>;
}

// ❌ DANGEROUS - Bypasses escaping
function Component({ userInput }) {
  return <div dangerouslySetInnerHTML={{ __html: userInput }} />;
}

// ✅ SAFE - Sanitize first if absolutely necessary
import DOMPurify from 'dompurify';

function Component({ userInput }) {
  const sanitized = DOMPurify.sanitize(userInput);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

**Content Security Policy:**
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https://api.anthropic.com https://api.openai.com",
    ].join('; ')
  }
];
```

---

## CSRF Protection

### Backend CSRF Tokens

```python
import secrets
from fastapi import Depends, HTTPException, Header

async def generate_csrf_token(user_id: int, redis: Redis) -> str:
    """Generate CSRF token for user"""
    token = secrets.token_urlsafe(32)
    await redis.setex(f"csrf:{user_id}", 3600, token)  # 1 hour expiry
    return token

async def verify_csrf_token(
    user: User = Depends(get_current_user),
    csrf_token: str = Header(..., alias="X-CSRF-Token"),
    redis: Redis = Depends(get_redis)
):
    """Verify CSRF token"""
    stored_token = await redis.get(f"csrf:{user.id}")
    
    if not stored_token or stored_token != csrf_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid CSRF token"
        )
    
    return user

# Protect state-changing endpoints
@router.post("/cards", dependencies=[Depends(verify_csrf_token)])
async def create_card(...):
    pass
```

### Frontend CSRF Handling

```typescript
// Fetch CSRF token on app load
export async function getCsrfToken(): Promise<string> {
  const response = await fetch('/api/v1/csrf-token', {
    credentials: 'include'
  });
  const data = await response.json();
  return data.csrf_token;
}

// Include in all state-changing requests
export async function createCard(cardData: CardCreate): Promise<Card> {
  const csrfToken = await getCsrfToken();
  
  const response = await fetch('/api/v1/cards', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify(cardData)
  });
  
  return response.json();
}
```

**SameSite Cookies:**
```python
from fastapi.responses import JSONResponse

response = JSONResponse(content={"access_token": token})
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,       # Not accessible via JavaScript
    secure=True,         # HTTPS only
    samesite="strict",   # CSRF protection
    max_age=604800       # 7 days
)
```

---

## Rate Limiting

### API Rate Limiting

**Implementation:**
```python
from fastapi import Request
from redis import Redis
from datetime import datetime

class RateLimiter:
    def __init__(self, redis: Redis, max_requests: int, window_seconds: int):
        self.redis = redis
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        current = int(datetime.utcnow().timestamp())
        window_start = current - self.window_seconds
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        request_count = await self.redis.zcard(key)
        
        if request_count >= self.max_requests:
            return False
        
        # Add current request
        await self.redis.zadd(key, {str(current): current})
        await self.redis.expire(key, self.window_seconds)
        
        return True

# Rate limit middleware
async def rate_limit_middleware(
    request: Request,
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """Rate limit API requests per user"""
    limiter = RateLimiter(redis, max_requests=100, window_seconds=60)
    
    key = f"rate_limit:{user.id}:{request.url.path}"
    
    if not await limiter.is_allowed(key):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
```

**Per-Endpoint Limits:**
```python
# Stricter limits for expensive operations
RATE_LIMITS = {
    "/api/v1/conversation/message": (10, 60),  # 10 requests / minute
    "/api/v1/speech/recognize": (20, 60),      # 20 requests / minute
    "/api/v1/flashcards": (100, 60),           # 100 requests / minute
    "default": (100, 60)                        # Default: 100 / minute
}
```

### Nginx Rate Limiting

```nginx
# nginx.conf
http {
    # Define rate limit zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=conversation_limit:10m rate=2r/s;
    
    server {
        # General API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            # ...
        }
        
        # Expensive AI conversation endpoint
        location /api/v1/conversation/ {
            limit_req zone=conversation_limit burst=5 nodelay;
            # ...
        }
    }
}
```

---

## Data Encryption

### Data at Rest

**Database Encryption:**
```python
from cryptography.fernet import Fernet
from app.core.config import settings

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Use for sensitive fields
class User(Base):
    __tablename__ = "users"
    
    email = Column(String, nullable=False)  # Encrypted
    
    @property
    def decrypted_email(self):
        encryption = EncryptionService()
        return encryption.decrypt(self.email)
```

**File Encryption:**
```python
async def save_encrypted_audio(
    user_id: int,
    audio_data: bytes
) -> str:
    """Save audio file with encryption"""
    encryption = EncryptionService()
    encrypted_data = encryption.encrypt(audio_data.decode('latin1'))
    
    filename = f"audio_{user_id}_{int(time.time())}.enc"
    filepath = f"/app/storage/encrypted/{filename}"
    
    async with aiofiles.open(filepath, 'w') as f:
        await f.write(encrypted_data)
    
    return filename
```

### Data in Transit

**HTTPS Enforcement:**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**TLS Configuration (Nginx):**
```nginx
server {
    listen 443 ssl http2;
    
    # SSL certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Strong ciphers only
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## Secrets Management

### Environment Variables

**DO NOT commit secrets to git:**
```bash
# .gitignore
.env
.env.local
.env.production
secrets/
*.pem
*.key
```

**Use .env for configuration:**
```bash
# .env (never committed)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
CLAUDE_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Database credentials
POSTGRES_PASSWORD=secure_random_password

# Encryption key
ENCRYPTION_KEY=your-fernet-key-here
```

**Secure generation:**
```bash
# Generate secure random secrets
openssl rand -hex 32  # For SECRET_KEY, JWT_SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # For ENCRYPTION_KEY
```

### Secret Rotation

**Implement key rotation:**
```python
class KeyRotationService:
    def __init__(self):
        self.current_key = settings.JWT_SECRET_KEY
        self.previous_key = settings.JWT_SECRET_KEY_OLD
    
    def verify_token(self, token: str) -> dict:
        """Verify token with current or previous key"""
        try:
            return jwt.decode(token, self.current_key, algorithms=["HS256"])
        except jwt.InvalidSignatureError:
            # Try previous key for graceful rotation
            return jwt.decode(token, self.previous_key, algorithms=["HS256"])
```

---

## Logging & Monitoring

### Security Event Logging

```python
import logging
from datetime import datetime

security_logger = logging.getLogger("security")

class SecurityEvent:
    @staticmethod
    def log_login_success(user_id: int, ip_address: str):
        security_logger.info(
            "login_success",
            extra={
                "user_id": user_id,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_login_failure(email: str, ip_address: str, reason: str):
        security_logger.warning(
            "login_failure",
            extra={
                "email": email,
                "ip_address": ip_address,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_suspicious_activity(user_id: int, activity: str, details: dict):
        security_logger.warning(
            "suspicious_activity",
            extra={
                "user_id": user_id,
                "activity": activity,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

**Alert on suspicious patterns:**
```python
async def detect_brute_force(email: str, redis: Redis):
    """Detect brute force login attempts"""
    key = f"failed_login:{email}"
    failed_count = await redis.incr(key)
    await redis.expire(key, 900)  # 15 minutes
    
    if failed_count >= 5:
        # Alert security team
        await send_security_alert(
            f"Brute force detected for {email}",
            f"{failed_count} failed attempts in 15 minutes"
        )
        
        # Temporarily lock account
        await lock_account(email, duration=3600)
```

---

## Vulnerability Management

### Dependency Scanning

**Backend (Python):**
```bash
# Check for known vulnerabilities
pip-audit

# Update vulnerable packages
pip install -U package-name

# Generate updated requirements
pip freeze > requirements.txt
```

**Frontend (Node):**
```bash
# Audit dependencies
npm audit

# Fix vulnerabilities
npm audit fix

# Check for updates
npm outdated
```

### Security Headers

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
```

---

## Privacy & GDPR Compliance

### Data Minimization

**Only collect necessary data:**
```python
class User(Base):
    # Required fields
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Optional fields (user can choose not to provide)
    full_name = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
```

### Right to Deletion

**Implement data deletion:**
```python
@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account and all associated data"""
    # Delete related data (CASCADE handles most)
    await db.execute(
        delete(Card).where(Card.user_id == current_user.id)
    )
    await db.execute(
        delete(Conversation).where(Conversation.user_id == current_user.id)
    )
    
    # Delete user
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "Account deleted successfully"}
```

### Data Export

**GDPR data export:**
```python
@router.get("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user data in JSON format"""
    # Gather all user data
    cards = await get_user_cards(db, current_user.id)
    conversations = await get_user_conversations(db, current_user.id)
    progress = await get_user_progress(db, current_user.id)
    
    export_data = {
        "user": {
            "email": current_user.email,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat()
        },
        "flashcards": [card.to_dict() for card in cards],
        "conversations": [conv.to_dict() for conv in conversations],
        "progress": progress.to_dict()
    }
    
    return JSONResponse(content=export_data)
```

---

## Security Testing

### Penetration Testing Checklist

- [ ] SQL injection attempts on all endpoints
- [ ] XSS attacks on all input fields
- [ ] CSRF attacks on state-changing operations
- [ ] Authentication bypass attempts
- [ ] Authorization bypass attempts
- [ ] Rate limit testing
- [ ] Session hijacking attempts
- [ ] Password reset flow security
- [ ] File upload security (if applicable)
- [ ] API abuse scenarios

### Automated Security Testing

```bash
# OWASP ZAP scan
docker run -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable \
  zap-baseline.py -t http://localhost:3000

# Bandit (Python security linter)
bandit -r backend/app/

# npm audit (Node.js dependencies)
npm audit --audit-level=moderate
```

---

## Incident Response

### Security Incident Procedure

1. **Detect & Assess**
   - Monitor logs for suspicious activity
   - Assess scope and severity

2. **Contain**
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IPs

3. **Eradicate**
   - Remove malware/backdoors
   - Patch vulnerabilities
   - Reset all credentials

4. **Recover**
   - Restore from clean backups
   - Verify system integrity
   - Resume normal operations

5. **Post-Incident**
   - Document incident
   - Conduct post-mortem
   - Update security measures

### Emergency Contacts

```
Security Lead: security@nihongomaster.com
Database Admin: dba@nihongomaster.com
Infrastructure: ops@nihongomaster.com
```

---

## Security Checklist (Pre-Production)

**Authentication & Authorization:**
- [ ] Strong password policy enforced
- [ ] bcrypt with cost factor 12 for password hashing
- [ ] JWT tokens with short expiry (15 min access, 7 days refresh)
- [ ] Refresh token rotation implemented
- [ ] Rate limiting on authentication endpoints
- [ ] Account lockout after failed attempts

**Data Protection:**
- [ ] All sensitive data encrypted at rest
- [ ] HTTPS enforced in production
- [ ] TLS 1.2+ only
- [ ] Strong cipher suites configured
- [ ] Secrets stored in environment variables
- [ ] No secrets in git history

**Input Validation:**
- [ ] Pydantic validation on all API inputs
- [ ] Zod validation on all frontend forms
- [ ] SQL injection prevention (ORM only)
- [ ] XSS prevention (React auto-escaping)
- [ ] CSRF protection enabled

**Security Headers:**
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Strict-Transport-Security in production
- [ ] Content-Security-Policy configured

**Monitoring & Logging:**
- [ ] Security event logging implemented
- [ ] Failed login attempts monitored
- [ ] Suspicious activity alerts configured
- [ ] Log rotation configured
- [ ] Backup procedures tested

**Dependencies:**
- [ ] All dependencies up to date
- [ ] No known critical vulnerabilities
- [ ] Automated vulnerability scanning enabled
- [ ] Dependency updates scheduled monthly

---

**Last Updated:** Initial creation
**Review Cadence:** Quarterly security audits
