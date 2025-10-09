# 🎨 Frontend Implementation Guide

**Status:** Setting up Next.js 15 project...
**Tech Stack:** Next.js 15, TypeScript, TailwindCSS, shadcn/ui, Recharts

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── (auth)/            # Authentication routes
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/         # Main dashboard
│   │   ├── models/            # Model pages
│   │   │   ├── [id]/         # Individual model
│   │   │   └── compare/      # Compare models
│   │   ├── explanations/      # XAI explanations
│   │   ├── study/             # Human study interface
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── charts/           # Chart components
│   │   ├── models/           # Model-specific components
│   │   └── layout/           # Layout components
│   ├── lib/                   # Utilities
│   │   ├── api.ts            # API client
│   │   ├── auth.ts           # Auth utilities
│   │   └── utils.ts          # Helper functions
│   └── store/                 # Zustand state management
│       ├── auth.ts
│       └── models.ts
├── public/                    # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 🎯 Features to Implement

### 1. Authentication System
- Login page
- Register page
- JWT token management
- Protected routes

### 2. Dashboard
- Model overview cards
- Quick stats
- Recent activity
- Leaderboard preview

### 3. Model Management
- List all models
- View model details
- Compare models side-by-side
- Download model files

### 4. Visualizations
- Performance metrics charts
- Confusion matrix heatmap
- ROC curves
- Feature importance plots

### 5. XAI Explanations (Future)
- SHAP visualizations
- LIME explanations
- Feature contribution charts

### 6. Human Study Interface (Future)
- Study session management
- Transaction presentation
- Response collection

---

## 🔧 Core Files to Create

### 1. API Client (`src/lib/api.ts`)
Handles all backend communication with:
- Axios instance with interceptors
- Token management
- Error handling
- Type-safe API calls

### 2. Auth Store (`src/store/auth.ts`)
Zustand store for:
- User state
- Login/logout functions
- Token persistence

### 3. Models Store (`src/store/models.ts`)
Zustand store for:
- Model list
- Selected models
- Leaderboard data

### 4. UI Components (`src/components/ui/`)
shadcn/ui components:
- Button
- Card
- Table
- Dialog
- Tabs
- Toast

### 5. Chart Components (`src/components/charts/`)
Recharts-based visualizations:
- MetricsChart
- ConfusionMatrix
- ROCCurve
- LeaderboardChart

---

## 🎨 Design System

### Colors
- Primary: Blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Background: White/Gray

### Typography
- Font: Inter (system font)
- Headings: Bold, larger sizes
- Body: Regular, readable

### Components
- Cards with shadows
- Rounded corners (8px)
- Hover effects
- Loading states
- Empty states

---

## 📊 Pages Overview

### Home Page (`/`)
- Hero section
- Platform features
- Quick start guide
- Link to dashboard

### Login Page (`/login`)
- Email/password form
- Remember me checkbox
- Link to register
- Error handling

### Dashboard (`/dashboard`)
- Welcome message
- Model overview (6 cards)
- Leaderboard table
- Quick actions

### Models List (`/models`)
- Table of all models
- Sort by metrics
- Filter by type
- Quick actions (view, compare)

### Model Detail (`/models/[id]`)
- Model information
- Performance metrics
- Confusion matrix
- Download button

### Model Comparison (`/models/compare`)
- Select models to compare
- Side-by-side metrics
- Charts comparison
- Export results

---

## 🚀 Implementation Steps

### Phase 1: Setup & Core (Now)
1. ✅ Create Next.js project
2. ⏳ Install dependencies
3. ⏳ Configure Tailwind
4. ⏳ Set up API client
5. ⏳ Create auth store

### Phase 2: Authentication
1. Build login page
2. Build register page
3. Implement token management
4. Add protected routes

### Phase 3: Dashboard
1. Create layout
2. Add navigation
3. Build dashboard page
4. Add model cards

### Phase 4: Models
1. Models list page
2. Model detail page
3. Model comparison page
4. Add charts

### Phase 5: Polish
1. Add loading states
2. Error handling
3. Responsive design
4. Animations

---

## 🔗 API Integration

### Backend Endpoints Used

**Authentication:**
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/refresh`

**Models:**
- `GET /api/v1/models/`
- `GET /api/v1/models/{id}`
- `GET /api/v1/models/{id}/metrics`
- `GET /api/v1/models/leaderboard/performance`
- `POST /api/v1/models/train`

**Datasets:**
- `GET /api/v1/datasets/`
- `GET /api/v1/datasets/{id}`

**Explanations (Future):**
- `POST /api/v1/explanations/generate`
- `GET /api/v1/explanations/{id}`

---

## 📝 Next Steps

Once the setup completes, I'll create:

1. **API Client** - Connect to backend
2. **Auth Pages** - Login/register
3. **Dashboard** - Main interface
4. **Model Pages** - View and compare
5. **Components** - Reusable UI

---

**Setup is running... This will take 2-3 minutes.**

I'll notify you when it's complete and start creating the code files!
