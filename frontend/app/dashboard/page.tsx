"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { supabase, Document } from "@/lib/supabase";
import TransactionsTable from "@/components/dashboard/TransactionsTable";
import { FileUploader } from "@/components/FileUploader";
import { Info, FileText, Clock, CreditCard } from "lucide-react";

// Time saved calculation: ~15 min manual entry per document
const MINUTES_SAVED_PER_DOC = 15;

export default function DashboardPage() {
    const { user } = useAuth();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [showTimeSavedInfo, setShowTimeSavedInfo] = useState(false);

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

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
                <p className="text-slate-500 mt-1">Welcome back, {displayName}.</p>
            </div>

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
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
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
                                    <div className="absolute left-0 top-8 z-50 w-72 bg-slate-800 text-white text-xs rounded-lg p-4 shadow-xl">
                                        <div className="font-semibold mb-2">How we calculate time saved:</div>
                                        <ul className="space-y-1.5 text-slate-300">
                                            <li>• Industry average: <span className="text-white font-medium">15 min</span> to manually read and extract data from 1 EDI file</li>
                                            <li>• ReadableEDI conversion: <span className="text-white font-medium">&lt;5 seconds</span></li>
                                            <li>• <span className="text-purple-300 font-medium">You've converted {totalConversions} files</span></li>
                                            <li>• Total time saved: <span className="text-green-400 font-medium">{totalMinutesSaved} minutes</span></li>
                                        </ul>
                                        <div className="absolute -top-2 left-4 w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-b-8 border-b-slate-800"></div>
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

                {/* Supported Types */}
                <div className="mt-6 pt-4 border-t border-slate-100">
                    <p className="text-xs text-slate-500 mb-2 font-medium">Supported Transaction Types:</p>
                    <div className="flex flex-wrap gap-2">
                        {/* Current */}
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">850 Purchase Order</span>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">810 Invoice</span>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">812 Credit/Debit</span>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">856 ASN</span>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">855 PO Ack</span>
                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium">997 Func Ack</span>
                        {/* Phase 2 - Coming Soon */}
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">820 Payment</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">860 PO Change</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">861 Receiving</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">870 Status</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">830 Planning</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">852 POS Data</span>
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-500 rounded-md text-xs font-medium">875/880 Grocery</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-2">
                        <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-1"></span> Available now
                        <span className="inline-block w-2 h-2 bg-slate-300 rounded-full ml-3 mr-1"></span> Coming soon
                    </p>
                </div>
            </div>

            {/* Recent Conversions */}
            <TransactionsTable />
        </div>
    );
}
