# 📁 Next.js Routing Structure

## ⚠️ Important: File Naming Convention

**The `page.tsx` filename CANNOT be changed!**

This is a **Next.js App Router requirement**. Files named `page.tsx` are special - they define the UI for a route.

---

## 🗂️ Current Routing Structure

```
frontend/src/app/
│
├── page.tsx                          → Home/Landing Page
│   Route: /
│   Purpose: Welcome page, redirects authenticated users
│
├── login/
│   └── page.tsx                      → Login Page
│       Route: /login
│       Purpose: User authentication
│
├── dashboard/
│   └── page.tsx                      → Dashboard Page
│       Route: /dashboard
│       Purpose: Main dashboard after login
│
└── models/
    ├── page.tsx                      → Models List Page
    │   Route: /models
    │   Purpose: Display all trained models
    │
    ├── compare/
    │   └── page.tsx                  → Global Comparison Page
    │       Route: /models/compare
    │       Purpose: Compare multiple models
    │
    └── [id]/
        ├── page.tsx                  → Model Detail Page
        │   Route: /models/:id
        │   Purpose: Single model details + explanations
        │
        └── compare/
            └── page.tsx              → Model Comparison Page
                Route: /models/:id/compare
                Purpose: Compare SHAP vs LIME for one model
```

---

## 📄 Page Details

### 1. Home Page (`/`)
**File:** `frontend/src/app/page.tsx`
- Landing page
- Shows platform features
- Login button for guests
- Auto-redirects authenticated users to dashboard

### 2. Login Page (`/login`)
**File:** `frontend/src/app/login/page.tsx`
- User authentication
- Email/password form
- Redirects to dashboard on success
- Demo credentials available

### 3. Dashboard Page (`/dashboard`)
**File:** `frontend/src/app/dashboard/page.tsx`
- Main dashboard after login
- Overview of all models
- Quick stats and metrics
- Navigation to models

### 4. Models List Page (`/models`)
**File:** `frontend/src/app/models/page.tsx`
- Lists all 6 trained models
- Model cards with metrics
- Links to model details
- Compare models button

### 5. Model Detail Page (`/models/[id]`)
**File:** `frontend/src/app/models/[id]/page.tsx`
- Single model details
- Performance metrics
- Confusion matrix
- SHAP generation
- LIME generation
- Method switcher
- Export functionality
- Quality metrics

### 6. Model Comparison Page (`/models/[id]/compare`)
**File:** `frontend/src/app/models/[id]/compare/page.tsx`
- Compare SHAP vs LIME for ONE model
- Agreement metrics
- Rank correlation
- Side-by-side tables
- Comparison charts

### 7. Global Comparison Page (`/models/compare`)
**File:** `frontend/src/app/models/compare/page.tsx`
- Compare MULTIPLE models
- Model selection
- Performance comparison
- Metrics comparison

---

## 🔄 How Next.js Routing Works

### File-Based Routing
Next.js uses the file system for routing:
- `page.tsx` → Defines a route
- `layout.tsx` → Wraps pages with shared UI
- `loading.tsx` → Loading UI
- `error.tsx` → Error UI

### Dynamic Routes
- `[id]` → Dynamic segment (e.g., `/models/123`)
- `[...slug]` → Catch-all segment
- `[[...slug]]` → Optional catch-all

### Example
```
app/
├── page.tsx              → /
├── about/
│   └── page.tsx          → /about
└── blog/
    ├── page.tsx          → /blog
    └── [slug]/
        └── page.tsx      → /blog/:slug
```

---

## ✅ Why We Can't Rename `page.tsx`

### Next.js Convention
- `page.tsx` is a **reserved filename**
- It tells Next.js "this is a route"
- Changing it breaks routing

### What We CAN Do
✅ Add clear header comments (DONE!)
✅ Use descriptive component names
✅ Add JSDoc documentation
✅ Create this guide

### What We CANNOT Do
❌ Rename `page.tsx` to `HomePage.tsx`
❌ Rename `page.tsx` to `models-list.tsx`
❌ Use any other filename

---

## 📝 Header Comments Added

All `page.tsx` files now have clear headers:

```typescript
/**
 * MODEL DETAIL PAGE
 * Route: /models/[id]
 * 
 * Detailed view of a single model.
 * Shows metrics, confusion matrix, and explanation generation.
 * Supports SHAP and LIME explanation methods.
 * Protected route - requires authentication.
 */
```

---

## 🎯 Quick Reference

| Route | File | Purpose |
|-------|------|---------|
| `/` | `app/page.tsx` | Home/Landing |
| `/login` | `app/login/page.tsx` | Authentication |
| `/dashboard` | `app/dashboard/page.tsx` | Main Dashboard |
| `/models` | `app/models/page.tsx` | Models List |
| `/models/compare` | `app/models/compare/page.tsx` | Global Comparison |
| `/models/:id` | `app/models/[id]/page.tsx` | Model Detail |
| `/models/:id/compare` | `app/models/[id]/compare/page.tsx` | SHAP vs LIME |

---

## 🔗 Navigation Flow

```
Home (/)
  ↓
Login (/login)
  ↓
Dashboard (/dashboard)
  ↓
Models List (/models)
  ↓
Model Detail (/models/:id)
  ├→ Generate SHAP
  ├→ Generate LIME
  └→ Compare Methods (/models/:id/compare)
```

---

## 📚 Learn More

- [Next.js Routing](https://nextjs.org/docs/app/building-your-application/routing)
- [File Conventions](https://nextjs.org/docs/app/building-your-application/routing#file-conventions)
- [Dynamic Routes](https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes)

---

**Summary:** The `page.tsx` filename is required by Next.js and cannot be changed. However, all files now have clear header comments explaining their purpose!
