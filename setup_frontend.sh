#!/bin/bash

# Frontend Setup Script for XAI Platform
echo "🚀 Setting up Next.js 15 Frontend..."

cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis

# Create Next.js app
echo "📦 Creating Next.js app..."
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --import-alias "@/*" --no-git --yes

cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install @radix-ui/react-avatar @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-label @radix-ui/react-select @radix-ui/react-slot @radix-ui/react-tabs @radix-ui/react-toast class-variance-authority clsx tailwind-merge tailwindcss-animate lucide-react recharts axios zustand

echo "✅ Frontend setup complete!"
echo "📝 Next: Run 'cd frontend && npm run dev' to start the development server"
