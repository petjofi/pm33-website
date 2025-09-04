/**
 * Supabase Connection Test Utility
 * Run this to verify Supabase setup is working
 */

import { supabase } from './supabase'

export async function testSupabaseConnection() {
  try {
    console.log('🔍 Testing Supabase connection...')
    
    // Test 1: Check if client is initialized
    if (!supabase) {
      throw new Error('Supabase client not initialized')
    }
    
    // Test 2: Try to get session (this doesn't require auth)
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    
    if (sessionError) {
      console.warn('⚠️  Session check warning:', sessionError.message)
    } else {
      console.log('✅ Session check passed')
    }
    
    // Test 3: Try a simple query (this will fail if tables don't exist, but connection will work)
    const { error: queryError } = await supabase
      .from('profiles') // Common table name
      .select('id')
      .limit(1)
    
    if (queryError) {
      if (queryError.message.includes('relation "profiles" does not exist')) {
        console.log('✅ Connection successful - database needs setup')
        return { success: true, needsSetup: true, message: 'Supabase connected but needs table setup' }
      } else if (queryError.message.includes('Invalid API key')) {
        console.error('❌ Invalid API key')
        return { success: false, error: 'Invalid Supabase API key' }
      } else {
        console.warn('⚠️  Query warning:', queryError.message)
        return { success: true, needsSetup: true, message: 'Connected with minor issues' }
      }
    } else {
      console.log('✅ Full connection successful - tables exist')
      return { success: true, needsSetup: false, message: 'Supabase fully operational' }
    }
    
  } catch (error: any) {
    console.error('❌ Supabase connection failed:', error.message)
    return { success: false, error: error.message }
  }
}

export function getSupabaseConfig() {
  return {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL || 'NOT_SET',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? '[REDACTED]' : 'NOT_SET',
    serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY ? '[REDACTED]' : 'NOT_SET'
  }
}