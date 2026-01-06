import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Lazy-loaded Supabase client (avoids issues during static build)
let supabaseInstance: SupabaseClient | null = null;

function getSupabaseClient(): SupabaseClient {
    if (supabaseInstance) return supabaseInstance;

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        // During static build, return a mock client that throws on use
        console.warn('Supabase environment variables not available');
        // Return a proxy that will throw meaningful errors
        return new Proxy({} as SupabaseClient, {
            get: () => () => {
                throw new Error('Supabase client not initialized - missing env vars');
            }
        });
    }

    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey);
    return supabaseInstance;
}

// Export as getter to ensure lazy initialization
export const supabase = typeof window !== 'undefined'
    ? getSupabaseClient()
    : new Proxy({} as SupabaseClient, {
        get: (target, prop) => {
            // During SSR/build, return functions that do nothing
            if (prop === 'from') {
                return () => ({
                    select: () => ({ eq: () => ({ order: () => Promise.resolve({ data: [], error: null }) }) }),
                    insert: () => Promise.resolve({ data: null, error: null }),
                });
            }
            return () => Promise.resolve({ data: null, error: null });
        }
    });

// Types for our database
export interface Document {
    id: string;
    user_id: string;
    filename: string;
    transaction_type: string;
    transaction_name: string;
    transaction_count: number;
    trading_partner?: string;
    source?: string;
    pdf_url?: string;
    excel_url?: string;
    html_url?: string;
    created_at: string;
}

// Helper to check if user is authenticated
export async function getUser() {
    if (typeof window === 'undefined') return null;
    const client = getSupabaseClient();
    const { data: { user } } = await client.auth.getUser();
    return user;
}

// Helper to save a document
export async function saveDocument(doc: Omit<Document, 'id' | 'created_at'>) {
    if (typeof window === 'undefined') return null;
    const client = getSupabaseClient();
    const { data, error } = await client
        .from('documents')
        .insert(doc)
        .select()
        .single();

    if (error) throw error;
    return data;
}

// Helper to get user's documents
export async function getUserDocuments(userId: string) {
    if (typeof window === 'undefined') return [];
    const client = getSupabaseClient();
    const { data, error } = await client
        .from('documents')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
}
