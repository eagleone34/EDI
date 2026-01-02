"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, ArrowRight, Loader2, CheckCircle, ArrowLeft } from "lucide-react";

export default function LoginPage() {
    const router = useRouter();
    const [step, setStep] = useState<"email" | "code">("email");
    const [email, setEmail] = useState("");
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [devCode, setDevCode] = useState<string | null>(null);

    const handleSendCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app';
            const response = await fetch(`${apiUrl}/api/v1/auth/send-code`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Failed to send code");
            }

            // In dev mode, show the code
            if (data.dev_code) {
                setDevCode(data.dev_code);
            }

            setStep("code");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app';
            const response = await fetch(`${apiUrl}/api/v1/auth/verify-code`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, code }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Invalid code");
            }

            // Store auth info in localStorage
            localStorage.setItem("user_email", email);
            localStorage.setItem("user_token", data.token);
            localStorage.setItem("user_id", data.user_id);

            // Redirect to dashboard
            router.push("/dashboard");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Invalid code");
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        setStep("email");
        setCode("");
        setError("");
        setDevCode(null);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
            {/* Background effects */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl"></div>
            </div>

            <div className="relative w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex items-center gap-2">
                        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                            R
                        </div>
                        <span className="text-2xl font-bold text-white">
                            ReadableEDI
                        </span>
                    </Link>
                </div>

                {/* Card */}
                <div className="bg-white rounded-2xl shadow-2xl p-8">
                    {step === "email" ? (
                        <>
                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <Mail className="w-8 h-8 text-white" />
                                </div>
                                <h1 className="text-2xl font-bold text-slate-900 mb-2">
                                    Welcome back
                                </h1>
                                <p className="text-slate-600">
                                    Enter your email to sign in to your account
                                </p>
                            </div>

                            <form onSubmit={handleSendCode} className="space-y-4">
                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
                                        Email address
                                    </label>
                                    <input
                                        type="email"
                                        id="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="you@company.com"
                                        required
                                        className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                                    />
                                </div>

                                {error && (
                                    <p className="text-red-500 text-sm">{error}</p>
                                )}

                                <button
                                    type="submit"
                                    disabled={loading || !email}
                                    className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Sending...
                                        </>
                                    ) : (
                                        <>
                                            Continue with Email
                                            <ArrowRight className="w-5 h-5" />
                                        </>
                                    )}
                                </button>
                            </form>

                            <div className="mt-6 text-center">
                                <p className="text-sm text-slate-500">
                                    Don't have an account?{" "}
                                    <Link href="/#convert" className="text-blue-600 hover:underline font-medium">
                                        Try it free
                                    </Link>
                                </p>
                            </div>
                        </>
                    ) : (
                        <>
                            <button
                                onClick={handleBack}
                                className="flex items-center gap-1 text-slate-600 hover:text-slate-900 mb-4 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back
                            </button>

                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <CheckCircle className="w-8 h-8 text-white" />
                                </div>
                                <h1 className="text-2xl font-bold text-slate-900 mb-2">
                                    Check your email
                                </h1>
                                <p className="text-slate-600">
                                    We sent a 6-digit code to<br />
                                    <span className="font-medium text-slate-900">{email}</span>
                                </p>
                            </div>

                            {devCode && (
                                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
                                    <p className="text-xs text-yellow-600 mb-1">Development mode</p>
                                    <p className="text-lg font-mono font-bold text-yellow-700">{devCode}</p>
                                </div>
                            )}

                            <form onSubmit={handleVerifyCode} className="space-y-4">
                                <div>
                                    <label htmlFor="code" className="block text-sm font-medium text-slate-700 mb-2">
                                        Verification code
                                    </label>
                                    <input
                                        type="text"
                                        id="code"
                                        value={code}
                                        onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                        placeholder="000000"
                                        required
                                        maxLength={6}
                                        className="w-full px-4 py-4 border border-slate-300 rounded-xl text-center text-2xl font-mono tracking-widest focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                                    />
                                </div>

                                {error && (
                                    <p className="text-red-500 text-sm text-center">{error}</p>
                                )}

                                <button
                                    type="submit"
                                    disabled={loading || code.length !== 6}
                                    className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Verifying...
                                        </>
                                    ) : (
                                        "Sign In"
                                    )}
                                </button>
                            </form>

                            <p className="text-center text-xs text-slate-500 mt-4">
                                Didn't receive the code?{" "}
                                <button
                                    onClick={handleBack}
                                    className="text-blue-600 hover:underline"
                                >
                                    Try again
                                </button>
                            </p>
                        </>
                    )}
                </div>

                {/* Footer */}
                <p className="text-center text-sm text-slate-400 mt-6">
                    By signing in, you agree to our{" "}
                    <Link href="/terms" className="hover:underline">Terms</Link>
                    {" "}and{" "}
                    <Link href="/privacy" className="hover:underline">Privacy Policy</Link>
                </p>
            </div>
        </div>
    );
}
