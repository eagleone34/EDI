"use client";

import { useState } from "react";
import { Mail, ArrowLeft, Loader2, X, CheckCircle } from "lucide-react";

interface EmailGateModalProps {
    isOpen: boolean;
    onClose: () => void;
    onVerified: (email: string, token: string) => void;
}

export function EmailGateModal({ isOpen, onClose, onVerified }: EmailGateModalProps) {
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
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app'}/api/v1/auth/send-code`, {
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
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://edi-production.up.railway.app'}/api/v1/auth/verify-code`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, code }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Invalid code");
            }

            // Success! Call callback with email and token
            onVerified(email, data.token);
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

    const handleClose = () => {
        setStep("email");
        setEmail("");
        setCode("");
        setError("");
        setDevCode(null);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={handleClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-in fade-in zoom-in duration-200">
                {/* Close button */}
                <button
                    onClick={handleClose}
                    className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>

                {step === "email" ? (
                    <>
                        {/* Email Step */}
                        <div className="text-center mb-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <Mail className="w-8 h-8 text-white" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 mb-2">
                                Enter your email to download
                            </h2>
                            <p className="text-slate-600">
                                We'll send a verification code to your email
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
                                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                                />
                            </div>

                            {error && (
                                <p className="text-red-500 text-sm">{error}</p>
                            )}

                            <button
                                type="submit"
                                disabled={loading || !email}
                                className="w-full py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Sending...
                                    </>
                                ) : (
                                    "Send Verification Code"
                                )}
                            </button>
                        </form>

                        <p className="text-center text-xs text-slate-500 mt-4">
                            Your files will be saved to your account
                        </p>
                    </>
                ) : (
                    <>
                        {/* Code Step */}
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
                            <h2 className="text-2xl font-bold text-slate-900 mb-2">
                                Check your email
                            </h2>
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
                                    className="w-full px-4 py-4 border border-slate-300 rounded-xl text-center text-2xl font-mono tracking-widest focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                                />
                            </div>

                            {error && (
                                <p className="text-red-500 text-sm text-center">{error}</p>
                            )}

                            <button
                                type="submit"
                                disabled={loading || code.length !== 6}
                                className="w-full py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Verifying...
                                    </>
                                ) : (
                                    "Verify & Download"
                                )}
                            </button>
                        </form>

                        <p className="text-center text-xs text-slate-500 mt-4">
                            Didn't receive the code?{" "}
                            <button
                                onClick={handleBack}
                                className="text-primary-600 hover:underline"
                            >
                                Try again
                            </button>
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
