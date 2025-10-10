/**
 * REGISTER PAGE
 * Route: /register
 * 
 * User registration page with Supabase authentication
 */

import AuthForm from '@/components/AuthForm'

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <AuthForm mode="register" />
    </div>
  )
}
