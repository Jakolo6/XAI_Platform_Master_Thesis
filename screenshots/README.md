# 📸 Screenshots for Thesis

This directory contains screenshots for the thesis documentation.

## 📋 Required Screenshots

### 1. Platform Overview
- [ ] `01_login_page.png` - Login screen
- [ ] `02_dashboard.png` - Main dashboard
- [ ] `03_models_list.png` - List of all models

### 2. Model Details
- [ ] `04_model_detail.png` - Model detail page
- [ ] `05_model_metrics.png` - Performance metrics display

### 3. SHAP Explanations
- [ ] `06_shap_generation.png` - SHAP generation in progress
- [ ] `07_shap_results.png` - SHAP feature importance chart
- [ ] `08_shap_top_features.png` - Top features table

### 4. LIME Explanations
- [ ] `09_lime_generation.png` - LIME generation with progress bar
- [ ] `10_lime_progress.png` - Progress tracking (2/5 min)
- [ ] `11_lime_results.png` - LIME feature importance chart
- [ ] `12_lime_top_features.png` - Top features table

### 5. Method Switcher
- [ ] `13_method_switcher.png` - Toggle between SHAP and LIME
- [ ] `14_shap_selected.png` - SHAP button active
- [ ] `15_lime_selected.png` - LIME button active
- [ ] `16_both_available.png` - "Both methods available" badge

### 6. Comparison Dashboard
- [ ] `17_comparison_page.png` - Full comparison view
- [ ] `18_side_by_side.png` - SHAP vs LIME side-by-side
- [ ] `19_agreement_metrics.png` - Agreement statistics
- [ ] `20_correlation_chart.png` - Correlation visualization

### 7. Quality Metrics
- [ ] `21_quality_metrics.png` - Quality metrics display
- [ ] `22_faithfulness.png` - Faithfulness score
- [ ] `23_robustness.png` - Robustness score
- [ ] `24_complexity.png` - Complexity score

### 8. Error Handling
- [ ] `25_error_message.png` - User-friendly error
- [ ] `26_loading_state.png` - Loading indicator

### 9. Architecture
- [ ] `27_system_architecture.png` - System diagram
- [ ] `28_database_schema.png` - Database schema
- [ ] `29_api_flow.png` - API request flow

## 📐 Screenshot Guidelines

### Resolution
- **Minimum:** 1920x1080
- **Recommended:** 2560x1440 or higher
- **Format:** PNG (lossless)

### Quality
- Clear and readable text
- No personal information
- Professional appearance
- Consistent styling

### Naming Convention
```
[number]_[description].png
Example: 01_login_page.png
```

### Content Guidelines
1. **Clean UI** - No debug info visible
2. **Realistic Data** - Use actual model results
3. **Professional** - No test/dummy data labels
4. **Focused** - Highlight the feature being shown
5. **Annotated** - Add arrows/labels if needed

## 🎨 Editing Tools

### Recommended
- **macOS:** Preview, Skitch, or built-in screenshot tools
- **Annotations:** Add arrows, boxes, text as needed
- **Cropping:** Focus on relevant areas
- **Compression:** Optimize file size without quality loss

### macOS Screenshot Shortcuts
```bash
# Full screen
Cmd + Shift + 3

# Selected area
Cmd + Shift + 4

# Window
Cmd + Shift + 4, then Space

# Screenshot tool
Cmd + Shift + 5
```

## 📊 Usage in Thesis

### Figures
- Figure 1: System Architecture
- Figure 2: Model Dashboard
- Figure 3: SHAP Feature Importance
- Figure 4: LIME Feature Importance
- Figure 5: Method Comparison
- Figure 6: Quality Metrics

### Captions Template
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{screenshots/07_shap_results.png}
\caption{SHAP feature importance visualization showing the top 20 features contributing to fraud detection predictions.}
\label{fig:shap_results}
\end{figure}
```

## ✅ Checklist

Before submitting thesis:
- [ ] All required screenshots captured
- [ ] High resolution (>1920x1080)
- [ ] Professional quality
- [ ] No sensitive information
- [ ] Properly named
- [ ] Referenced in thesis text
- [ ] Captions written
- [ ] Labels added where needed

## 📝 Notes

### Important
- Take screenshots in **light mode** for better printing
- Ensure **consistent zoom level** across similar screenshots
- **Crop** unnecessary UI elements (browser chrome, etc.)
- **Highlight** key features with annotations if needed

### For Comparison Screenshots
- Use **same model** for SHAP and LIME
- Show **same features** in both views
- Capture at **same zoom level**
- Include **agreement metrics**

## 🔗 References

Screenshots will be used in:
1. Thesis chapters (Methodology, Results)
2. Presentation slides
3. Demo video
4. README.md
5. User documentation

---

**Status:** Ready for screenshot capture  
**Priority:** HIGH  
**Deadline:** Before thesis submission  
**Quality:** Professional, publication-ready
