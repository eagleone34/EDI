"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";
import TransactionsTable from "@/components/dashboard/TransactionsTable";
import { FileUploader } from "@/components/FileUploader";
import { SupportedTypes } from "@/components/SupportedTypes";
import { Info, FileText, Clock, CreditCard, Mail, Copy, Check } from "lucide-react";

// Time saved calculation: ~15 min manual entry per document
const MINUTES_SAVED_PER_DOC = 15;

export default function DashboardPage() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [showTimeSavedInfo, setShowTimeSavedInfo] = useState(false);
    const [copied, setCopied] = useState(false);

    // Use firstName if available, otherwise fallback to email prefix
    const displayName = user?.firstName || user?.email?.split("@")[0] || "User";

    // Fetch user's documents for stats
    useEffect(() => {
        const fetchDocs = async () => {
            if (!user?.id) return;

            const { data } = await supabase
                .from("documents")
                .select("*")
                .eq("user_id", user.id);

            if (data) setDocuments(data);
        };
        fetchDocs();
    }, [user?.id]);

    // Calculate stats
    const totalConversions = documents.length;
    const totalMinutesSaved = totalConversions * MINUTES_SAVED_PER_DOC;
    const hoursSaved = Math.floor(totalMinutesSaved / 60);
    const minutesSaved = totalMinutesSaved % 60;
    const timeSavedDisplay = hoursSaved > 0
        ? `${hoursSaved}h ${minutesSaved}m`
        : `${minutesSaved}m`;

    const handleCopyEmail = () => {
        if (user?.inboundEmail) {
            navigator.clipboard.writeText(user.inboundEmail);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
                <p className="text-slate-500 mt-1">Welcome back, {displayName}.</p>
            </div>

            {/* Inbound Email Card */}
            {user?.inboundEmail && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-5">
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                            <Mail className="w-5 h-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-semibold text-slate-800 mb-1">Your Inbound Email Address</h3>
                            <p className="text-sm text-slate-600 mb-3">
                                Forward EDI files to this address for automatic conversion. Documents will appear in your dashboard and routing rules will apply.
                            </p>
                            <div className="flex items-center gap-2">
                                <div className="flex-1 bg-white border border-blue-200 rounded-lg px-4 py-2.5 font-mono text-sm text-slate-700 select-all">
                                    {user.inboundEmail}
                                </div>
                                <button
                                    onClick={handleCopyEmail}
                                    className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
                                >
                                    {copied ? (
                                        <>
                                            <Check className="w-4 h-4" />
                                            Copied!
                                        </>
                                    ) : (
                                        <>
                                            <Copy className="w-4 h-4" />
                                            Copy
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Total Conversions */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-blue-500" />
                            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Total Conversions</p>
                        </div>
                        <p className="text-3xl font-bold text-slate-800 mt-2">{totalConversions}</p>
                        <p className="text-xs text-slate-400 mt-2 font-medium">
                            {totalConversions === 0 ? "Convert your first file to get started" : "Files converted this month"}
                        </p>
                    </div>
                </div>

                {/* Time Saved */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-purple-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-purple-500" />
                            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Time Saved</p>
                            <div className="relative">
                                <button
                                    onClick={() => setShowTimeSavedInfo(!showTimeSavedInfo)}
                                    className="p-1 hover:bg-purple-100 rounded-full transition-colors"
                                    title="How we calculate time saved"
                                >
                                    <Info className="w-3.5 h-3.5 text-purple-400" />
                                </button>

                                {/* Info Tooltip */}
                                {showTimeSavedInfo && (
                                    <div className="fixed inset-0 z-40" onClick={() => setShowTimeSavedInfo(false)} />
                                )}
                                {showTimeSavedInfo && (
                                    <div className="absolute left-1/2 -translate-x-1/2 top-10 z-50 w-80 bg-slate-800 text-white text-xs rounded-lg p-4 shadow-xl">
                                        <div className="font-semibold mb-2 text-sm">How we calculate time saved:</div>
                                        <ul className="space-y-2 text-slate-300">
                                            <li>• Industry average: <span className="text-white font-medium">15 min</span> to manually read and extract data from 1 EDI file</li>
                                            <li>• ReadableEDI conversion: <span className="text-white font-medium">&lt;5 seconds</span></li>
                                            <li>• You've converted <span className="text-purple-300 font-medium">{totalConversions} files</span></li>
                                            <li>• Total time saved: <span className="text-green-400 font-medium">{totalMinutesSaved} minutes</span></li>
                                        </ul>
                                        <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-b-8 border-b-slate-800"></div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <p className="text-3xl font-bold text-slate-800 mt-2">{totalConversions === 0 ? "0m" : timeSavedDisplay}</p>
                        <p className="text-xs text-purple-600 mt-2 font-medium">
                            Based on 15 min manual entry time
                        </p>
                    </div>
                </div>

                {/* Plan */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-50 rounded-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                    <div className="relative">
                        <div className="flex items-center gap-2">
                            <CreditCard className="w-4 h-4 text-emerald-500" />
                            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Plan</p>
                        </div>
                        <p className="text-3xl font-bold text-slate-800 mt-2">Free</p>
                        <p className="text-xs text-emerald-600 mt-2 font-medium">
                            5 conversions/month
                        </p>
                    </div>
                </div>
            </div>

            {/* File Uploader Section */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4">Convert EDI File</h2>
                <FileUploader />

                {/* Supported Types - shared component */}
                <SupportedTypes className="mt-6 pt-4 border-t border-slate-100" />
            </div>

            {/* Recent Conversions */}
            <TransactionsTable />
        </div>
    );
}
