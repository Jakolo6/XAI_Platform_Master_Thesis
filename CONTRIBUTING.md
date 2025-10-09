# 🤝 Contributing to XAI Platform

Thank you for your interest in contributing to the XAI Platform! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or experience level.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what is best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Publishing others' private information
- Any conduct that could be considered inappropriate in a professional setting

---

## 🚀 Getting Started

### Prerequisites

1. **Read the documentation:**
   - [README.md](README.md) - Project overview
   - [INSTALLATION.md](INSTALLATION.md) - Setup instructions
   - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design

2. **Set up your development environment:**
   ```bash
   # Fork the repository on GitHub
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/XAI_Platform_Master_Thesis.git
   cd XAI_Platform_Master_Thesis
   
   # Add upstream remote
   git remote add upstream https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git
   
   # Install dependencies
   docker-compose up -d
   ```

3. **Create a branch for your work:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🔄 Development Workflow

### 1. Find or Create an Issue

- Check [existing issues](https://github.com/Jakolo6/XAI_Platform_Master_Thesis/issues)
- Create a new issue if needed
- Comment on the issue to let others know you're working on it

### 2. Development Process

```bash
# Keep your fork up to date
git fetch upstream
git rebase upstream/main

# Make your changes
# ... edit files ...

# Test your changes
docker-compose exec backend pytest
cd frontend && npm test

# Commit your changes
git add .
git commit -m "feat: add new feature"
```

### 3. Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(backend): add LIME explainer integration
fix(frontend): resolve authentication persistence issue
docs(readme): update installation instructions
test(api): add tests for explanation endpoints
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Fill out the PR template with details
```

---

## 💻 Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```python
# Use type hints
def train_model(model_type: str, hyperparameters: Dict[str, Any]) -> Model:
    """
    Train a machine learning model.
    
    Args:
        model_type: Type of model to train (e.g., 'xgboost')
        hyperparameters: Model hyperparameters
        
    Returns:
        Trained model instance
    """
    pass

# Use docstrings for all functions/classes
# Use meaningful variable names
# Keep functions small and focused
# Use list comprehensions when appropriate
```

**Tools:**
```bash
# Format code
black backend/app/

# Check style
flake8 backend/app/

# Type checking
mypy backend/app/
```

### TypeScript (Frontend)

**Style Guide:** Airbnb TypeScript Style Guide

```typescript
// Use TypeScript interfaces
interface ExplanationResult {
  method: string;
  featureImportance: FeatureImportance[];
  numSamples: number;
}

// Use functional components with hooks
export default function ModelDetail({ modelId }: { modelId: string }) {
  const [model, setModel] = useState<Model | null>(null);
  
  useEffect(() => {
    fetchModel(modelId);
  }, [modelId]);
  
  return <div>...</div>;
}

// Use async/await for promises
// Destructure props
// Use meaningful component names
```

**Tools:**
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

### General Guidelines

- **DRY (Don't Repeat Yourself):** Avoid code duplication
- **KISS (Keep It Simple, Stupid):** Prefer simple solutions
- **YAGNI (You Aren't Gonna Need It):** Don't add unnecessary features
- **Single Responsibility:** Each function/class should do one thing well
- **Meaningful Names:** Use descriptive variable and function names

---

## 🧪 Testing Guidelines

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_explanations.py

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

**Test Structure:**
```python
# tests/test_explanations.py
import pytest
from app.utils.explainers.shap_explainer import ShapExplainer

def test_shap_explainer_initialization():
    """Test SHAP explainer initializes correctly."""
    explainer = ShapExplainer(model_path="path/to/model", model_type="xgboost")
    assert explainer is not None

@pytest.mark.asyncio
async def test_generate_explanation():
    """Test explanation generation."""
    # ... test code ...
```

### Frontend Tests

```bash
# Run all tests
cd frontend && npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- ModelDetail.test.tsx
```

**Test Structure:**
```typescript
// __tests__/ModelDetail.test.tsx
import { render, screen } from '@testing-library/react';
import ModelDetail from '@/app/models/[id]/page';

describe('ModelDetail', () => {
  it('renders model information', () => {
    render(<ModelDetail modelId="123" />);
    expect(screen.getByText('Model Details')).toBeInTheDocument();
  });
});
```

### Test Coverage

- Aim for **80%+ code coverage**
- All new features must include tests
- Bug fixes should include regression tests
- Critical paths require integration tests

---

## 📤 Submitting Changes

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (if applicable)
5. **Fill out PR template** completely
6. **Request review** from maintainers

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **At least one approval** from maintainer
3. **Address review comments**
4. **Squash commits** if requested
5. **Merge** when approved

---

## 📁 Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API routes
│   │   ├── auth.py           # Authentication
│   │   ├── models.py         # Model management
│   │   └── explanations.py   # XAI explanations
│   ├── core/                 # Core configuration
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   └── security.py       # Auth utilities
│   ├── models/               # SQLAlchemy models
│   │   ├── model.py          # Model entity
│   │   └── explanation.py    # Explanation entity
│   ├── tasks/                # Celery tasks
│   │   ├── training_tasks.py
│   │   └── explanation_tasks.py
│   └── utils/                # Utilities
│       ├── explainers/       # XAI implementations
│       ├── preprocessing.py  # Data pipeline
│       └── training.py       # Model training
├── tests/                    # Test files
└── requirements.txt          # Dependencies
```

### Frontend Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js pages
│   │   ├── dashboard/
│   │   ├── models/
│   │   └── login/
│   ├── components/           # React components
│   │   ├── charts/           # Visualization
│   │   └── explanations/     # XAI displays
│   ├── lib/                  # Utilities
│   │   └── api.ts            # API client
│   └── store/                # State management
│       ├── auth.ts           # Auth store
│       └── models.ts         # Models store
└── package.json              # Dependencies
```

---

## 🎯 Areas for Contribution

### High Priority

- [ ] DiCE counterfactual explanations
- [ ] Quantus metrics integration
- [ ] Human study module
- [ ] Report generation (PDF)
- [ ] Performance optimization

### Medium Priority

- [ ] Additional ML models (Neural Networks, SVM)
- [ ] More visualization types
- [ ] Export functionality
- [ ] API rate limiting
- [ ] Caching improvements

### Good First Issues

- [ ] Documentation improvements
- [ ] UI/UX enhancements
- [ ] Bug fixes
- [ ] Test coverage
- [ ] Code refactoring

---

## 💡 Development Tips

### Backend Development

```bash
# Hot reload backend
docker-compose exec backend uvicorn app.main:app --reload

# Access backend shell
docker-compose exec backend bash

# View logs
docker-compose logs -f backend

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Frontend Development

```bash
# Hot reload frontend
cd frontend && npm run dev

# Access frontend shell
docker-compose exec frontend sh

# View logs
docker-compose logs -f frontend

# Build for production
npm run build
```

### Debugging

```bash
# Backend debugging with pdb
import pdb; pdb.set_trace()

# Frontend debugging
console.log('Debug:', variable);
debugger;

# Check API responses
curl -X GET http://localhost:8000/api/v1/models \
  -H "Authorization: Bearer TOKEN"
```

---

## 📚 Resources

### Learning Materials

- **FastAPI:** https://fastapi.tiangolo.com/tutorial/
- **Next.js:** https://nextjs.org/learn
- **SHAP:** https://shap.readthedocs.io/
- **LIME:** https://github.com/marcotcr/lime
- **Docker:** https://docs.docker.com/get-started/

### Related Projects

- **Quantus:** https://github.com/understandable-machine-intelligence-lab/Quantus
- **DiCE:** https://github.com/interpretml/DiCE
- **Alibi:** https://github.com/SeldonIO/alibi

---

## 🙏 Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Acknowledged in thesis (if significant contribution)

---

## 📧 Questions?

- **GitHub Discussions:** [Ask a question](https://github.com/Jakolo6/XAI_Platform_Master_Thesis/discussions)
- **Email:** [your.email@novasbe.pt]
- **Issues:** [Report a bug](https://github.com/Jakolo6/XAI_Platform_Master_Thesis/issues)

---

**Thank you for contributing to explainable AI research!** 🎉
