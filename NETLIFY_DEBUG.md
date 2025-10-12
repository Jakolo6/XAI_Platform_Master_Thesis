# 🔍 Netlify Deployment Debug Guide

## **Issue: Changes Not Showing on Netlify**

Your local code is correct and pushed to GitHub, but Netlify is showing the old version.

---

## **✅ STEP 1: Check Netlify Build Status**

1. Go to your Netlify dashboard: https://app.netlify.com
2. Find your site: `xai-platform` or similar
3. Click on it
4. Go to **"Deploys"** tab
5. Check the latest deploy:
   - ✅ **Published** (green) = deployed successfully
   - ⚠️ **Building** (yellow) = still building
   - ❌ **Failed** (red) = build error

---

## **✅ STEP 2: Check Latest Commit**

In Netlify Deploys tab, check if the latest deploy shows commit:
- `f5bf30b` - "feat: complete Human Study with session page"

If it shows an older commit (like `0b7a6ae` or earlier), Netlify hasn't picked up your latest changes.

---

## **✅ STEP 3: Force New Deploy**

### **Method A: Trigger Deploy (Recommended)**
1. In Netlify dashboard → **"Deploys"** tab
2. Click **"Trigger deploy"** button (top right)
3. Select **"Clear cache and deploy site"**
4. Wait 3-5 minutes for build to complete

### **Method B: Push Empty Commit**
```bash
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis
git commit --allow-empty -m "trigger netlify rebuild"
git push origin main
```

---

## **✅ STEP 4: Check Build Logs**

If deploy fails:
1. Click on the failed deploy
2. Scroll to **"Deploy log"**
3. Look for errors (usually in red)
4. Common issues:
   - `npm install` fails → dependency issue
   - `npm run build` fails → TypeScript/build error
   - Environment variables missing

---

## **✅ STEP 5: Verify Environment Variables**

In Netlify dashboard:
1. Go to **"Site settings"** → **"Environment variables"**
2. Check if `NEXT_PUBLIC_API_URL` is set
3. Should be: `https://your-backend-url.com/api/v1`
4. If missing, add it and redeploy

---

## **✅ STEP 6: Check Browser Cache**

After successful deploy:
1. Hard refresh: **Cmd + Shift + R** (Mac) or **Ctrl + Shift + R** (Windows)
2. Or open in incognito/private window
3. Or clear browser cache

---

## **🎯 Expected Result After Fix:**

### **Navigation should show 7 items:**
- Dashboard
- Datasets
- Train Model
- Research ← NEW
- Human Study ← NEW
- Reports ← NEW
- Benchmarks

### **Dashboard should show:**
- Real model counts (not hardcoded 3, 6, 2)
- 6 Quick Action cards (including Research, Human Study, Reports)

---

## **🔴 If Still Not Working:**

### **Check Netlify Configuration:**

1. Verify `netlify.toml` settings:
   ```toml
   [build]
     base = "frontend"
     command = "npm run build"
     publish = ".next"
   ```

2. Check if Netlify is watching the correct branch:
   - Go to **"Site settings"** → **"Build & deploy"** → **"Continuous deployment"**
   - Should be watching: `main` branch
   - Should be: **"Auto publishing"** enabled

3. Check build command:
   - Should be: `npm run build`
   - NOT: `npm run dev`

---

## **🚨 Common Errors & Fixes:**

### **Error: "Module not found"**
```bash
cd frontend
npm install
npm run build  # Test locally
```

### **Error: "Type errors"**
Check TypeScript errors:
```bash
cd frontend
npm run type-check
```

### **Error: "Out of memory"**
In Netlify, go to **"Site settings"** → **"Environment variables"**
Add: `NODE_OPTIONS=--max-old-space-size=4096`

---

## **✅ Quick Test:**

After deploy completes, test these URLs:
- `https://your-site.netlify.app/` → Landing page
- `https://your-site.netlify.app/dashboard` → Should show new dashboard
- `https://your-site.netlify.app/research` → Should work (not 404)
- `https://your-site.netlify.app/study` → Should work (not 404)
- `https://your-site.netlify.app/reports` → Should work (not 404)

---

## **📊 Current Git Status:**

Latest commits pushed to GitHub:
- ✅ `f5bf30b` - Human Study complete
- ✅ `17da211` - User flow connections
- ✅ `4f6b3f6` - Dataset to training flow
- ✅ `6eb10b7` - Reports page

All code is ready, just needs Netlify to rebuild!
