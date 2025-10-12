/**
 * Supabase Client for Browser
 * Used for client-side authentication and data access
 */

import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  // Provide fallback values during build to prevent errors
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'
  
  return createBrowserClient(
    supabaseUrl,
    supabaseKey
  )
}
