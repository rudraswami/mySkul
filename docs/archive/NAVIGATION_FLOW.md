# Updated Navigation Flow & User Journey

## 🗺️ Complete User Journey Map

### **Scenario 1: New User First Visit**
```
Landing Page (/)
    ↓
[Click ANY button: "Sign In", "Start Free", "Upgrade Plan", "Start Journey"]
    ↓
New Login Screen (/login)
    ↓
[Click "Continue with Google"]
    ↓
Emergent OAuth (Gmail Login)
    ↓
Redirected back with session_id
    ↓
Profile Setup (/profile-setup)
    - Select: JEE / NEET / UPSC / Others
    - Enter: Study Goal, Target Year
    - Select: Preferred Mode
    ↓
[Click "Continue to Dashboard"]
    ↓
Dashboard (/dashboard)
```

### **Scenario 2: Returning User**
```
Landing Page (/)
    ↓
[User has valid session cookie]
    ↓
Auto-redirect to Dashboard (/dashboard)
```

### **Scenario 3: Click Sign In (Already Logged In)**
```
Landing Page (/)
    ↓
[Click "Sign In"]
    ↓
Detect existing session
    ↓
Auto-redirect to Dashboard (/dashboard)
```

### **Scenario 4: Session Expired**
```
Any Protected Page (/dashboard, /tutor, etc.)
    ↓
[No valid session]
    ↓
Auto-redirect to Login (/login)
    ↓
[Continue with Google]
    ↓
Dashboard (Profile already complete)
```

### **Scenario 5: Old Links/Bookmarks**
```
Old URLs: /register, /signin, /signup
    ↓
Auto-redirect to /login
    ↓
New Login Screen (Gmail OAuth)
```

---

## 🔄 Route Configuration

### **Public Routes (No Authentication Required)**
| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | LandingPage | Marketing homepage |
| `/login` | LoginScreen | Gmail OAuth login |

### **Semi-Protected Routes (Auth Required)**
| Route | Component | Condition |
|-------|-----------|-----------|
| `/profile-setup` | ProfileSetup | Only if `!profile_completed` |

### **Protected Routes (Auth + Profile Required)**
| Route | Component | Purpose |
|-------|-----------|---------|
| `/dashboard` | StudentDashboard | Main dashboard |
| `/tutor` | AITutor | AI Tutor chat |
| `/tests` | MockTests | Mock exams |
| `/auto-notes` | AutoNoteMentor | Note generation |
| `/subscription` | Subscription | Pricing plans |
| `/profile` | ProfileSettings | User settings |

### **Legacy Redirects (Automatic)**
| Old Route | Redirects To |
|-----------|--------------|
| `/register` | `/login` |
| `/signin` | `/login` |
| `/signup` | `/login` |

---

## 🎯 Landing Page Button Mappings

### **Updated Button Actions:**

1. **"Sign In" Button (Top Navigation)**
   - Route: `/login` → LoginScreen
   - Action: Gmail OAuth

2. **"Start Free - No Credit Card" Button (Hero Section)**
   - Route: `/login` → LoginScreen
   - Action: Gmail OAuth

3. **"Upgrade" Buttons (Pricing Plans)**
   - Route: `/login` → LoginScreen
   - Then: Auto-redirect to `/subscription` after login

4. **"Start Your Journey" Button (CTA Section)**
   - Route: `/login` → LoginScreen
   - Action: Gmail OAuth

5. **"Get Started" Buttons (Feature Cards)**
   - Route: `/login` → LoginScreen
   - Action: Gmail OAuth

---

## 🔐 Authentication Logic Flow

### **Session Check (Happens on Every Page Load)**
```javascript
useEffect(() => {
  1. Check for session_id in URL (OAuth callback)
     → If found: Process OAuth, login user
  
  2. Check for existing session cookie
     → Call /api/auth/session
     → If valid: Load user data
     → If invalid: Clear session, redirect to /login
  
  3. Check route protection
     → Public routes: Allow access
     → Protected routes: Require auth
     → Profile setup: Require !profile_completed
}, [])
```

### **OAuth Callback Processing**
```javascript
URL: /#session_id=abc123
    ↓
1. Detect session_id in URL fragment
2. Call Emergent: /auth/v1/env/oauth/session-data
3. Get: { id, email, name, picture, session_token }
4. Call Backend: /api/auth/google/callback
5. Backend returns: { user, profile_completed }
6. Redirect:
   - If !profile_completed → /profile-setup
   - If profile_completed → /dashboard
7. Clean URL fragment (remove #session_id)
```

---

## 🛡️ Route Guards

### **Before Rendering Any Route:**
```
1. Loading State
   → Show "Authenticating..." spinner
   
2. OAuth Processing State
   → Show "Completing sign in..." spinner
   
3. Check User State
   → If user exists:
      - Check profile_completed
      - If false → Redirect /profile-setup
      - If true → Allow access to protected routes
   → If no user:
      - Public routes → Allow
      - Protected routes → Redirect /login
```

---

## 📱 Mobile Navigation Flow

### **Same as Desktop, with additional considerations:**
- Hamburger menu for navigation
- Touch-optimized buttons
- Responsive layout for Profile Setup
- Mobile-friendly OAuth redirect

---

## ⚡ Quick Reference

### **All Paths Lead to One Login:**
```
ANY button on landing page
    ↓
/login (LoginScreen)
    ↓
Gmail OAuth Only
```

### **No More:**
- ❌ Email/password fields
- ❌ Separate register page
- ❌ Password reset flow
- ❌ Email verification

### **Now Just:**
- ✅ One-click Gmail login
- ✅ One-time profile setup
- ✅ 7-day session persistence
- ✅ Auto-redirect to dashboard

---

## 🎨 Visual Journey Map

```
┌─────────────────┐
│  Landing Page   │  ← All entry points
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LoginScreen    │  ← Single login page
│  (Gmail OAuth)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ProfileSetup    │  ← First-time only
│ (Select Exam)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │  ← Protected app
└─────────────────┘
```

---

## ✅ Testing Checklist for Each Button

### **From Landing Page:**
- [ ] Click "Sign In" (nav) → Goes to /login ✓
- [ ] Click "Start Free" (hero) → Goes to /login ✓
- [ ] Click pricing plan "Upgrade" → Goes to /login ✓
- [ ] Click "Start Your Journey" → Goes to /login ✓
- [ ] Click any "Get Started" → Goes to /login ✓

### **From Login Screen:**
- [ ] Click "Continue with Google" → Emergent OAuth
- [ ] Complete Gmail auth → Redirects back with session_id
- [ ] New user → Goes to /profile-setup
- [ ] Returning user → Goes to /dashboard

### **From Profile Setup:**
- [ ] Select exam type → Required field
- [ ] Click "Continue" → Saves profile, goes to /dashboard
- [ ] Click "Skip" → Sets defaults, goes to /dashboard

---

## 🎯 Success Criteria

**Every button on landing page MUST:**
1. Navigate to `/login` route
2. Show new LoginScreen component
3. Display "Continue with Google" button
4. NOT show email/password fields

**After Gmail login MUST:**
1. Create/update user in database
2. Set httpOnly session cookie
3. Redirect to profile-setup (first time)
4. Redirect to dashboard (returning user)

---

## 📊 Route Analytics (For Future)

Track these conversions:
- Landing → Login (click-through rate)
- Login → OAuth (conversion rate)
- OAuth → Profile Setup (completion rate)
- Profile Setup → Dashboard (onboarding rate)

---

This document provides the complete navigation flow and user journey for the new Gmail-only authentication system.
