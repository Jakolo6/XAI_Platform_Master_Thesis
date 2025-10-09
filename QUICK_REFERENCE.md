# ⚡ Quick Reference Card

**XAI Platform - Essential Commands & Info**

---

## 🚀 Quick Start

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

**Login:** researcher@xai.com / research123

---

## 📊 Current Status

- **Phase 1:** ✅ 100%
- **Phase 2:** 🚀 90% (LIME + Comparison)
- **Phase 3:** 🚀 95% (Quantus)
- **Overall:** 80% Thesis-Ready

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| START_HERE.md | Begin here |
| README.md | Overview |
| INSTALLATION.md | Setup |
| SESSION_SUMMARY_OCT9.md | Latest work |

---

## 🎯 Features

✅ 6 ML Models (94.3% AUC-ROC)  
✅ SHAP Explanations  
✅ LIME Explanations  
✅ Comparison Dashboard  
✅ Quantus Quality Metrics  

---

## 🔬 Research Findings

- **Agreement:** 40% top-10
- **Correlation:** 0.617
- **Top Feature:** C13 (both methods)

---

## 📝 Next Tasks

1. [ ] Integration testing
2. [ ] Feature stories
3. [ ] Human study module

---

## 🐛 Common Issues

**Port in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d
```

---

## 📧 Links

- **GitHub:** github.com/Jakolo6/XAI_Platform_Master_Thesis
- **Commit:** 0566f25
- **Docs:** /api/v1/docs

---

**Last Updated:** Oct 9, 2025 | **Status:** Production-Ready ✅
