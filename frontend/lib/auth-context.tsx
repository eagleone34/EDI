"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { User, Session } from "@supabase/supabase-js";

// Lazy import supabase to avoid SSR issues
let supabaseClient: ReturnType<typeof import("@supabase/supabase-js").createClient> | null = null;

function getSupabase() {
    if (typeof window === "undefined") return null;
    if (supabaseClient) return supabaseClient;

    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        console.warn("Supabase env vars not set");
        return null;
    }

    const { createClient } = require("@supabase/supabase-js");
    supabaseClient = createClient(url, key);
    return supabaseClient;
}

interface AuthUser {
    id: string;
    email: string;
    firstName?: string;
    lastName?: string;
}

interface AuthContextType {
    user: AuthUser | null;
    session: Session | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    signInWithOtp: (email: string) => Promise<{ error: Error | null }>;
    verifyOtp: (email: string, token: string) => Promise<{ error: Error | null; user: User | null }>;
    logout: () => Promise<void>;
    updateProfile: (firstName: string, lastName: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Check for existing session on mount
    useEffect(() => {
        const supabase = getSupabase();
        if (!supabase) {
            setIsLoading(false);
            return;
        }

        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }: { data: { session: Session | null } }) => {
            if (session?.user) {
                setSession(session);
                setUser({
                    id: session.user.id,
                    email: session.user.email || "",
                    firstName: session.user.user_metadata?.first_name,
                    lastName: session.user.user_metadata?.last_name,
                });
            }
            setIsLoading(false);
        });

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (_event: string, session: Session | null) => {
                if (session?.user) {
                    setSession(session);
                    setUser({
                        id: session.user.id,
                        email: session.user.email || "",
                        firstName: session.user.user_metadata?.first_name,
                        lastName: session.user.user_metadata?.last_name,
                    });
                } else {
                    setSession(null);
                    setUser(null);
                }
            }
        );

        return () => subscription.unsubscribe();
    }, []);

    const signInWithOtp = async (email: string): Promise<{ error: Error | null }> => {
        const supabase = getSupabase();
        if (!supabase) return { error: new Error("Supabase not initialized") };

        const { error } = await supabase.auth.signInWithOtp({
            email,
            options: {
                shouldCreateUser: true,
            },
        });

        return { error };
    };

    const verifyOtp = async (email: string, token: string): Promise<{ error: Error | null; user: User | null }> => {
        const supabase = getSupabase();
        if (!supabase) return { error: new Error("Supabase not initialized"), user: null };

        const { data, error } = await supabase.auth.verifyOtp({
            email,
            token,
            type: "email",
        });

        if (data?.user) {
            setUser({
                id: data.user.id,
                email: data.user.email || "",
                firstName: data.user.user_metadata?.first_name,
                lastName: data.user.user_metadata?.last_name,
            });
            setSession(data.session);
        }

        return { error, user: data?.user || null };
    };

    const updateProfile = (firstName: string, lastName: string) => {
        const supabase = getSupabase();
        if (!supabase || !user) return;

        supabase.auth.updateUser({
            data: { first_name: firstName, last_name: lastName }
        });

        setUser(prev => prev ? { ...prev, firstName, lastName } : null);
    };

    const logout = async () => {
        const supabase = getSupabase();
        if (supabase) {
            await supabase.auth.signOut();
        }
        setUser(null);
        setSession(null);
        router.push("/");
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                session,
                isLoading,
                isAuthenticated: !!user,
                signInWithOtp,
                verifyOtp,
                logout,
                updateProfile,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
