import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Types for our database
export interface Document {
    id: string;
    user_id: string;
    filename: string;
    transaction_type: string;
    transaction_name: string;
    transaction_count: number;
    pdf_url?: string;
    excel_url?: string;
    html_url?: string;
    created_at: string;
}

// Helper to check if user is authenticated
export async function getUser() {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
}

// Helper to save a document
export async function saveDocument(doc: Omit<Document, 'id' | 'created_at'>) {
    const { data, error } = await supabase
        .from('documents')
        .insert(doc)
        .select()
        .single();

    if (error) throw error;
    return data;
}

// Helper to get user's documents
export async function getUserDocuments(userId: string) {
    const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
}
