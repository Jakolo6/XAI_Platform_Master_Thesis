# 🔴 USER FLOW BREAKS - Critical Issues

## **Current State: Pages exist but are NOT connected**

---

## **❌ BREAK 1: Dataset → Training**

**Problem:**
- Datasets page has "Train Model" button
- Button navigates to `/models/train?dataset=german-credit`
- Training page **IGNORES** the URL parameter
- User has to manually select dataset again

**Fix Needed:**
- Training page must read `searchParams.get('dataset')`
- Pre-select the dataset from URL
- Auto-advance to step 2

---

## **❌ BREAK 2: Training → Model Detail**

**Problem:**
- After training completes, user gets alert with model_id
- User has to manually navigate to `/models/[id]`
- No automatic redirect or "View Model" button

**Fix Needed:**
- Add "View Model" button after training completes
- Automatically navigate to model detail page
- Show training status with link

---

## **❌ BREAK 3: Model List → Model Detail**

**Problem:**
- `/models` page exists but might not show trained models
- Need to verify it lists models and links to detail pages

**Fix Needed:**
- Ensure models list shows all trained models
- Each model should link to `/models/[id]`
- Show training status

---

## **❌ BREAK 4: Model Detail → Explanations**

**Current State:**
- Model detail page has "Generate SHAP" and "Generate LIME" buttons
- These trigger explanation generation
- **BUT:** Page doesn't auto-refresh to show new explanations
- User has to manually refresh page

**Fix Needed:**
- After generating explanation, auto-refresh the page
- Or better: poll for completion and update UI
- Show loading state during generation

---

## **❌ BREAK 5: Explanations → Quality Metrics**

**Current State:**
- "Show Quality Metrics" button exists
- Calls API correctly
- **BUT:** Might not handle loading/error states well

**Fix Needed:**
- Verify quality metrics display properly
- Show loading spinner
- Handle errors gracefully

---

## **❌ BREAK 6: Model Detail → Reports**

**Problem:**
- Export buttons exist on model detail page
- **BUT:** No clear path to Reports page
- Reports page exists but user might not know about it

**Fix Needed:**
- Add "View All Reports" link on model detail
- Or add breadcrumb navigation
- Make Reports page more discoverable

---

## **❌ BREAK 7: Research Page Data**

**Problem:**
- Research page fetches leaderboard data
- **BUT:** If no explanations exist, page is empty
- No guidance on what to do next

**Fix Needed:**
- Show empty state with clear instructions
- "Train a model first" message
- Link to training page

---

## **❌ BREAK 8: Human Study**

**Problem:**
- Study intro page exists
- **BUT:** Study session page doesn't exist
- Clicking "Start Study" → 404 error

**Fix Needed:**
- Create `/study/session` page
- Or remove Human Study from navigation until complete

---

## **❌ BREAK 9: Navigation Context**

**Problem:**
- User can navigate anywhere from navbar
- **BUT:** No indication of where they are in the workflow
- No breadcrumbs or progress indicator

**Fix Needed:**
- Add breadcrumb navigation
- Show workflow progress
- Highlight current step

---

## **❌ BREAK 10: Dashboard → Actual Work**

**Problem:**
- Dashboard shows stats
- **BUT:** Stats might be hardcoded (3 datasets, 6 model types)
- Not showing actual user's models/explanations

**Fix Needed:**
- Fetch real user data
- Show "You have X trained models"
- Show recent activity
- Link to specific models

---

## **🎯 PRIORITY FIXES (Most Critical):**

### **1. Dataset → Training Connection** (5 minutes)
Add URL parameter reading to training page

### **2. Training → Model Detail** (10 minutes)
Add "View Model" button and auto-navigation

### **3. Model Detail Auto-Refresh** (15 minutes)
Poll for explanation completion

### **4. Dashboard Real Data** (20 minutes)
Fetch and display user's actual models

### **5. Empty States** (15 minutes)
Add helpful messages when no data exists

---

## **Total Estimated Time: 65 minutes**

These fixes will transform the platform from "pages that exist" to "a working tool with connected flow".
