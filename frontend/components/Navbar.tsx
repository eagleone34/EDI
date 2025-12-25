"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Mail, Menu, X } from "lucide-react";

export function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
                    ? "bg-white/90 backdrop-blur-lg shadow-sm border-b border-slate-200"
                    : "bg-transparent"
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
                            EDI.email
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

                    {/* CTA Buttons */}
                    <div className="hidden md:flex items-center gap-4">
                        <Link
                            href="/auth/login"
                            className="text-slate-600 hover:text-primary-600 transition-colors font-medium"
                        >
                            Login
                        </Link>
                        <Link
                            href="/auth/signup"
                            className="px-5 py-2.5 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg"
                        >
                            Get Started Free
                        </Link>
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
                                <Link
                                    href="/auth/login"
                                    className="text-center py-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
                                >
                                    Login
                                </Link>
                                <Link
                                    href="/auth/signup"
                                    className="text-center py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                                >
                                    Get Started Free
                                </Link>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}
