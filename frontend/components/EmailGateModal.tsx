"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Mail, ArrowLeft, Loader2, X, CheckCircle, User } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

interface EmailGateModalProps {
    isOpen: boolean;
    onClose: () => void;
    onVerified: (userData: { email: string; userId: string; firstName: string; lastName: string }) => void;
    pendingDownload?: () => void;
}

export function EmailGateModal({ isOpen, onClose, onVerified, pendingDownload }: EmailGateModalProps) {
    const router = useRouter();
    const { signInWithOtp, verifyOtp, updateProfile } = useAuth();
    const [step, setStep] = useState<"info" | "code">("info");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSendCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const { error: authError } = await signInWithOtp(email);

            if (authError) {
                throw authError;
            }

            setStep("code");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to send verification code");
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const { error: authError, user } = await verifyOtp(email, code);

            if (authError) {
                throw authError;
            }

            if (!user) {
                throw new Error("Verification failed - no user returned");
            }

            // Update profile with name
            updateProfile(firstName, lastName);

            // Trigger pending download if any
            if (pendingDownload) {
                pendingDownload();
            }

            // Call parent callback with user data
            onVerified({
                email,
                userId: user.id,
                firstName,
                lastName,
            });

            // Redirect to dashboard
            router.push("/dashboard");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Invalid verification code");
        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        setStep("info");
        setCode("");
        setError("");
    };

    const handleClose = () => {
        setStep("info");
        setFirstName("");
        setLastName("");
        setEmail("");
        setCode("");
        setError("");
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

                {step === "info" ? (
                    <>
                        {/* Info Step - Name + Email */}
                        <div className="text-center mb-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <User className="w-8 h-8 text-white" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 mb-2">
                                Create your account
                            </h2>
                            <p className="text-slate-600">
                                Enter your details to download your converted files
                            </p>
                        </div>

                        <form onSubmit={handleSendCode} className="space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label htmlFor="firstName" className="block text-sm font-medium text-slate-700 mb-1.5">
                                        First name
                                    </label>
                                    <input
                                        type="text"
                                        id="firstName"
                                        value={firstName}
                                        onChange={(e) => setFirstName(e.target.value)}
                                        placeholder="John"
                                        required
                                        className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="lastName" className="block text-sm font-medium text-slate-700 mb-1.5">
                                        Last name
                                    </label>
                                    <input
                                        type="text"
                                        id="lastName"
                                        value={lastName}
                                        onChange={(e) => setLastName(e.target.value)}
                                        placeholder="Doe"
                                        required
                                        className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                                    />
                                </div>
                            </div>

                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">
                                    Work email
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
                                disabled={loading || !email || !firstName || !lastName}
                                className="w-full py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Sending...
                                    </>
                                ) : (
                                    <>
                                        <Mail className="w-5 h-5" />
                                        Send Verification Code
                                    </>
                                )}
                            </button>
                        </form>

                        <p className="text-center text-xs text-slate-500 mt-4">
                            Your converted files will be saved to your account
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
