# Supabase Migrations

## 📁 Files

1. **`1_supabase_reset.sql`** - Deletes everything (⚠️ WARNING: Deletes all data!)
2. **`2_supabase_complete_schema.sql`** - Creates complete schema from scratch

---

## 🚀 How to Use

### Option 1: Fresh Start (Recommended)

**Run both files in order:**

1. **Reset (Delete Everything):**
   - Open Supabase Dashboard → SQL Editor
   - Copy `1_supabase_reset.sql`
   - Paste and Run
   - ⚠️ This deletes ALL tables and data!

2. **Create Schema:**
   - Copy `2_supabase_complete_schema.sql`
   - Paste and Run
   - ✅ Complete schema created!

### Option 2: Keep Existing Data

**Run only file 2:**
- If you want to keep existing data
- File 2 will fail if tables already exist
- Not recommended if you had errors before

---

## ✅ What You Get

### 8 Tables:
1. `users` - Authentication
2. `datasets` - Dataset metadata
3. `models` - Trained models
4. `model_metrics` - Performance metrics
5. `explanations` - SHAP/LIME results
6. `study_sessions` - Human evaluation sessions
7. `study_questions` - Evaluation instances
8. `human_evaluations` - Participant ratings

### 3 Views:
1. `model_leaderboard` - Ranked models
2. `human_evaluation_summary` - Aggregated ratings
3. `dataset_statistics` - Overview

### ~25 Indexes:
- All performance-optimized
- Foreign keys
- Constraints

---

## 🎯 Recommended Steps

1. **Backup your data** (if you have any important data)
2. **Run `1_supabase_reset.sql`** to clean everything
3. **Run `2_supabase_complete_schema.sql`** to create fresh schema
4. **Done!** ✅

---

**Status: Ready to use! 🚀**
