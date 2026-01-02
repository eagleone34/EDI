"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Mail, Menu, X, User, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const { user, isLoading, logout, isAuthenticated } = useAuth();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <nav
            className={`
        fixed top-0 w-full z-50 transition-all duration-300
        ${isScrolled
                    ? "bg-white/95 backdrop-blur-lg shadow-sm border-b border-slate-200"
                    : "bg-white border-b border-slate-100"
                }
      `}
        >
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex justify-between items-center">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform">
                            <Mail className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                            ReadableEDI
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-8">
                        <Link
                            href="#features"
                            className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                        >
                            Features
                        </Link>
                        <Link
                            href="#pricing"
                            className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                        >
                            Pricing
                        </Link>
                        <Link
                            href="#how-it-works"
                            className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                        >
                            How it Works
                        </Link>
                    </div>

                    {/* CTA Buttons - Auth Aware */}
                    <div className="hidden md:flex items-center gap-4">
                        {isLoading ? (
                            <div className="w-20 h-8 bg-slate-100 animate-pulse rounded-lg"></div>
                        ) : isAuthenticated ? (
                            <>
                                <Link
                                    href="/dashboard"
                                    className="flex items-center gap-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                >
                                    <User className="w-4 h-4" />
                                    Dashboard
                                </Link>
                                <button
                                    onClick={logout}
                                    className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-red-600 transition-colors font-medium"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                >
                                    Login
                                </Link>
                                <Link
                                    href="/login"
                                    className="px-5 py-2.5 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg"
                                >
                                    Get Started Free
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        {isMobileMenuOpen ? (
                            <X className="w-6 h-6 text-slate-600" />
                        ) : (
                            <Menu className="w-6 h-6 text-slate-600" />
                        )}
                    </button>
                </div>

                {/* Mobile Menu */}
                {isMobileMenuOpen && (
                    <div className="md:hidden mt-4 pb-4 border-t border-slate-100 pt-4">
                        <div className="flex flex-col gap-4">
                            <Link
                                href="#features"
                                className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Features
                            </Link>
                            <Link
                                href="#pricing"
                                className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                Pricing
                            </Link>
                            <Link
                                href="#how-it-works"
                                className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                onClick={() => setIsMobileMenuOpen(false)}
                            >
                                How it Works
                            </Link>
                            <div className="pt-4 border-t border-slate-100 flex flex-col gap-3">
                                {isAuthenticated ? (
                                    <>
                                        <Link
                                            href="/dashboard"
                                            className="text-center py-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                            onClick={() => setIsMobileMenuOpen(false)}
                                        >
                                            Dashboard
                                        </Link>
                                        <button
                                            onClick={() => {
                                                logout();
                                                setIsMobileMenuOpen(false);
                                            }}
                                            className="text-center py-3 bg-red-50 text-red-600 rounded-lg font-semibold hover:bg-red-100 transition-colors"
                                        >
                                            Logout
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <Link
                                            href="/login"
                                            className="text-center py-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                            onClick={() => setIsMobileMenuOpen(false)}
                                        >
                                            Login
                                        </Link>
                                        <Link
                                            href="/login"
                                            className="text-center py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                                            onClick={() => setIsMobileMenuOpen(false)}
                                        >
                                            Get Started Free
                                        </Link>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
