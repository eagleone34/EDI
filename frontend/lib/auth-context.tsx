"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface User {
    email: string;
    token: string;
    userId: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (email: string, token: string, userId: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    // Check for existing session on mount
    useEffect(() => {
        const email = localStorage.getItem("user_email");
        const token = localStorage.getItem("user_token");
        const userId = localStorage.getItem("user_id");

        if (email && token && userId) {
            setUser({ email, token, userId });
        }
        setIsLoading(false);
    }, []);

    const login = (email: string, token: string, userId: string) => {
        localStorage.setItem("user_email", email);
        localStorage.setItem("user_token", token);
        localStorage.setItem("user_id", userId);
        setUser({ email, token, userId });
    };

    const logout = () => {
        localStorage.removeItem("user_email");
        localStorage.removeItem("user_token");
        localStorage.removeItem("user_id");
        setUser(null);
        router.push("/");
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                login,
                logout,
                isAuthenticated: !!user,
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
