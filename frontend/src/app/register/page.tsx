/**
 * REGISTER PAGE
 * Route: /register
 * 
 * User registration page with Supabase authentication
 */

'use client'

export const dynamic = 'force-dynamic'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import Link from 'next/link'
import { UserPlus, Mail, Lock, User, ArrowRight } from 'lucide-react'
import AuthForm from '@/components/AuthForm'

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <AuthForm mode="register" />
    </div>
  )
}
